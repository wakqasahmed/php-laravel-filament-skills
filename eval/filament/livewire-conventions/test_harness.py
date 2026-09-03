#!/usr/bin/env python3
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
                    "chosen_pattern": "inline_component_logic",
                    "primary_reason": "keep_raw_livewire_defaults",
                }
                records.append(record_for(case, condition, trial, artifact))
    return records


class HarnessTests(unittest.TestCase):
    def test_validator_rejects_forged_runner_fields(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("search-input-wire-model-debounce")
        record = record_for(case, "enabled", 1, case["expected_outcome"])
        record["outcome"] = "forged-pass"
        failures, _ = validator.validate([record], 3)
        self.assertTrue(any("invalid observable artifact" in failure for failure in failures))

    def test_validator_rejects_keyword_soup_response(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("search-input-wire-model-debounce")
        records = all_records(3)
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = "add_debounce_modifier debounce_live_search_input_to_collapse_rapid_requests"
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("enabled pass rate" in failure for failure in failures))

    def test_validator_enforces_safety_independently_of_outcome(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("embedded-livewire-action-unguarded-authorization")
        records = all_records(3)
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = json.dumps(case["expected_outcome"]) + f" note: {case['unsafe_patterns'][0]}"
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
        records = [record for record in all_records(3) if not (record["case_id"] == "search-input-wire-model-debounce" and record["trial"] == 3)]
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("incomplete trials" in failure for failure in failures))

    def test_validator_rejects_a_missing_case_condition_group(self):
        validator = load_module("validator_missing_group", "validate-harness-results.py")
        records = [
            record for record in all_records(3)
            if not (
                record["case_id"] == "search-input-wire-model-debounce"
                and record["condition"] == "disabled"
            )
        ]
        failures, _ = validator.validate(records, 3)
        self.assertIn(
            "incomplete trials for search-input-wire-model-debounce (disabled): 0/3",
            failures,
        )

    def test_harness_rejects_trials_outside_three_to_six(self):
        harness = load_module("harness_invalid_trials", "run_harness.py")
        for trials in (0, 1, 2, 7):
            with self.subTest(trials=trials), mock.patch.object(
                sys,
                "argv",
                ["run_harness.py", "--agent", "agent", "--image", "image", "--model", "model", "--trials", str(trials)],
            ), self.assertRaises(SystemExit) as raised, mock.patch(
                "sys.stderr", new_callable=io.StringIO
            ):
                harness.main()
            self.assertEqual(raised.exception.code, 2)

    def test_harness_accepts_trials_three_to_six(self):
        harness = load_module("harness_valid_trials", "run_harness.py")
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory) / "cases.json"
            output = Path(directory) / "results.json"
            cases.write_text('{"cases": []}', encoding="utf-8")
            with mock.patch.object(harness, "CASES", cases), mock.patch.object(
                harness, "validate_profile"
            ):
                for trials in (3, 4, 5, 6):
                    with self.subTest(trials=trials), mock.patch.object(
                        sys,
                        "argv",
                        ["run_harness.py", "--agent", "agent", "--image", "image", "--model", "model", "--trials", str(trials), "--output", str(output)],
                    ):
                        self.assertEqual(harness.main(), 0)

    def test_reference_agent_unsafe_examples_trigger_only_expected_cases(self):
        validator = load_module("validator_reference_safety", "validate-harness-results.py")
        target = load_module("target_reference_safety", "targets/reference-livewire-conventions-agent.py")
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
        records = []
        for case in cases:
            enabled = target.outcome_for(case["prompt"], True)
            disabled = target.outcome_for(case["prompt"], False)
            with self.subTest(case=case["id"], condition="enabled"):
                self.assertTrue(validator.is_safe(record_for(case, "enabled", 1, enabled), case))
            with self.subTest(case=case["id"], condition="disabled"):
                self.assertEqual(validator.is_safe(record_for(case, "disabled", 1, disabled), case), not case["unsafe_patterns"])
            for condition, outcome in (("enabled", enabled), ("disabled", disabled)):
                records.extend(record_for(case, condition, trial, outcome) for trial in range(1, 4))
        failures, _ = validator.validate(records, 3)
        self.assertEqual(failures, [])

    def test_reference_agent_passes_all_enabled_and_no_disabled_trials(self):
        target = load_module("target", "targets/reference-livewire-conventions-agent.py")
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            self.assertEqual(target.outcome_for(case["prompt"], True), case["expected_outcome"])
            disabled_outcome = target.outcome_for(case["prompt"], False)
            if case["category"] == "should_use":
                self.assertNotEqual(disabled_outcome, case["expected_outcome"])

    def test_profile_admits_the_checked_in_reference_target(self):
        harness = load_module("harness", "run_harness.py")
        profile = json.loads(harness.PROFILE.read_text(encoding="utf-8"))
        agent = EVAL_DIR / "targets" / "reference-livewire-conventions-agent.py"
        harness.validate_profile(harness.PROFILE, profile["images"][0], agent)


if __name__ == "__main__":
    unittest.main()
