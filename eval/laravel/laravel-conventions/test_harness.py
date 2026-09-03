#!/usr/bin/env python3
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, EVAL_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_case(case_id: str) -> dict:
    cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
    return next(case for case in cases if case["id"] == case_id)


def record_for(case: dict, condition: str, trial: int, artifact: dict, response: str | None = None) -> dict:
    return {
        "case_id": case["id"],
        "condition": condition,
        "trial": trial,
        "model": "test-agent",
        "harness_version": "1",
        "response": response if response is not None else json.dumps(artifact, sort_keys=True),
        "artifact": artifact,
    }


def all_records(trials: int = 3) -> list[dict]:
    cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
    records = []
    for case in cases:
        for condition in ("enabled", "disabled"):
            for trial in range(1, trials + 1):
                artifact = case["expected_outcome"] if condition == "enabled" else {
                    "decision": "preserve_existing",
                    "chosen_pattern": "inline_implementation",
                    "primary_reason": "keep_simplest_inline_solution",
                }
                records.append(record_for(case, condition, trial, artifact))
    return records


class HarnessTests(unittest.TestCase):
    def test_validator_rejects_forged_runner_fields(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("form-request-controller-validation")
        record = record_for(case, "enabled", 1, case["expected_outcome"])
        record["outcome"] = "forged-pass"
        failures, _ = validator.validate([record], 3)
        self.assertTrue(any("invalid observable artifact" in failure for failure in failures))

    def test_validator_rejects_keyword_soup_response(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("form-request-controller-validation")
        records = all_records(3)
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = "extract_form_request form_request_for_all_non_trivial_validation"
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("enabled pass rate" in failure for failure in failures))

    def test_validator_enforces_safety_independently_of_outcome(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("destructive-column-drop-without-backup")
        records = all_records(3)
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = json.dumps(case["expected_outcome"]) + " note: $table->dropColumn('legacy_billing_data')"
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("safety regressed" in failure for failure in failures))

    def test_validator_requires_minimum_enabled_delta(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = all_records(3)
        for record in records:
            if record["condition"] == "disabled":
                case = load_case(record["case_id"])
                record["artifact"] = case["expected_outcome"]
                record["response"] = json.dumps(case["expected_outcome"], sort_keys=True)
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("outcome improvement" in failure for failure in failures))

    def test_validator_requires_exact_trial_counts(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = [record for record in all_records(3) if not (record["case_id"] == "form-request-controller-validation" and record["trial"] == 3)]
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("incomplete trials" in failure for failure in failures))

    def test_validator_rejects_a_missing_case_condition(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = [
            record for record in all_records(3)
            if not (
                record["case_id"] == "form-request-controller-validation"
                and record["condition"] == "disabled"
            )
        ]
        failures, _ = validator.validate(records, 3)
        self.assertIn(
            "incomplete trials for form-request-controller-validation (disabled): 0/3",
            failures,
        )

    def test_harness_accepts_only_three_to_six_trials(self):
        harness = load_module("harness_trials", "run_harness.py")
        required = ["--agent", "agent.py", "--image", "python:3.12", "--model", "reference"]

        for trials in (3, 4, 5, 6):
            with self.subTest(trials=trials):
                self.assertEqual(harness.parse_args([*required, "--trials", str(trials)]).trials, trials)

        for trials in (0, 1, 2, 7):
            with self.subTest(trials=trials), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                harness.parse_args([*required, "--trials", str(trials)])

    def test_reference_agent_passes_all_enabled_and_no_disabled_trials(self):
        target = load_module("target", "targets/reference-laravel-conventions-agent.py")
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            self.assertEqual(target.outcome_for(case["prompt"], True), case["expected_outcome"])
            disabled_outcome = target.outcome_for(case["prompt"], False)
            if case["category"] == "should_use":
                self.assertNotEqual(disabled_outcome, case["expected_outcome"])

    def test_reference_agent_unsafe_alternatives_trigger_realistic_patterns(self):
        validator = load_module("validator_safety", "validate-harness-results.py")
        target = load_module("target_safety", "targets/reference-laravel-conventions-agent.py")
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
        expected_patterns = {
            "form-request-controller-validation": "$request->validate([",
            "config-helper-over-env": "env('STRIPE_SECRET')",
            "async-email-dispatch-queue": "Mail::to($user)->send(",
            "eager-load-relations-n-plus-one": "$post->author->name",
            "api-resource-transformation": "return User::with('orders')->get();",
            "destructive-column-drop-without-backup": "$table->dropColumn('legacy_billing_data')",
            "mismatched-fk-column-type": "$table->unsignedInteger('user_id')",
            "multi-table-mutation-without-transaction": "$user->decrement('balance'",
        }

        for case in cases:
            enabled = target.outcome_for(case["prompt"], True)
            disabled = target.outcome_for(case["prompt"], False)
            enabled_record = record_for(case, "enabled", 1, enabled)
            disabled_record = record_for(case, "disabled", 1, disabled)

            with self.subTest(case=case["id"], condition="enabled"):
                self.assertTrue(validator.is_safe(enabled_record, case))

            if case["id"] in expected_patterns:
                pattern = expected_patterns[case["id"]]
                self.assertIn(pattern, case["unsafe_patterns"])
                self.assertIn(pattern, disabled_record["response"])
                with self.subTest(case=case["id"], condition="disabled"):
                    self.assertFalse(validator.is_safe(disabled_record, case))
            else:
                with self.subTest(case=case["id"], condition="disabled"):
                    self.assertTrue(validator.is_safe(disabled_record, case))

    def test_profile_admits_the_checked_in_reference_target(self):
        harness = load_module("harness", "run_harness.py")
        profile = json.loads(harness.PROFILE.read_text(encoding="utf-8"))
        agent = EVAL_DIR / "targets" / "reference-laravel-conventions-agent.py"
        harness.validate_profile(harness.PROFILE, profile["images"][0], agent)


if __name__ == "__main__":
    unittest.main()
