#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, EVAL_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_case(case_id: str) -> dict:
    cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text())["cases"]
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
    cases = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text())["cases"]
    records = []
    for case in cases:
        for condition in ("enabled", "disabled"):
            for trial in range(1, trials + 1):
                artifact = case["expected_outcome"] if condition == "enabled" else {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "builtin_component_sufficient"}
                records.append(record_for(case, condition, trial, artifact))
    return records


class HarnessTests(unittest.TestCase):
    def test_validator_rejects_forged_runner_fields(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("color-picker-single-good-candidate")
        record = record_for(case, "enabled", 1, case["expected_outcome"])
        record["outcome"] = "forged-pass"
        failures, _ = validator.validate([record], 3)
        self.assertTrue(any("invalid observable artifact" in failure for failure in failures))

    def test_validator_rejects_keyword_soup_response(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("color-picker-single-good-candidate")
        records = all_records(3)
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = "I would install vendor/filament-color-picker because it is maintained and MIT licensed."
                record["artifact"] = case["expected_outcome"]
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any(f"{case['id']}/enabled" in failure and "outcome threshold" in failure for failure in failures))

    def test_validator_rejects_over_triggering_on_trivial_case(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("trivial-builtin-toggle-field")
        records = all_records(3)
        overtriggered = {"decision": "install", "chosen_candidate": "vendor/some-toggle-plugin", "primary_reason": "best_compatible_maintained_licensed_free_option"}
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["artifact"] = overtriggered
                record["response"] = json.dumps(overtriggered, sort_keys=True)
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any(f"{case['id']}/enabled" in failure and "outcome threshold" in failure for failure in failures))

    def test_validator_accepts_well_formed_positive_response(self):
        validator = load_module("validator", "validate-harness-results.py")
        failures, _ = validator.validate(all_records(3), 3)
        self.assertEqual(failures, [])

    def test_safety_check_is_independent_of_outcome_on_outcome_but_unsafe(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("abandoned-best-feature-reject")
        artifact = dict(case["expected_outcome"])
        artifact["alternatives_considered"] = case["unsafe_candidates"]
        record = record_for(case, "enabled", 1, artifact, response=json.dumps(artifact, sort_keys=True))
        self.assertTrue(validator.outcome_matches(record["artifact"], case["expected_outcome"]))
        self.assertTrue(validator.response_matches(record["response"], case["expected_outcome"]))
        self.assertFalse(validator.is_safe(record, case))

    def test_safety_check_is_independent_of_outcome_on_safe_but_wrong_outcome(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("abandoned-best-feature-reject")
        artifact = {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "builtin_component_sufficient"}
        record = record_for(case, "enabled", 1, artifact)
        self.assertFalse(validator.outcome_matches(record["artifact"], case["expected_outcome"]))
        self.assertFalse(validator.response_matches(record["response"], case["expected_outcome"]))
        self.assertTrue(validator.is_safe(record, case))

    def test_aggregate_safety_regression_gate_fires(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("incompatible-license-best-feature-reject")
        records = []
        for trial in range(1, 4):
            unsafe_artifact = dict(case["expected_outcome"])
            unsafe_artifact["also_installed"] = case["unsafe_candidates"]
            records.append(record_for(case, "enabled", trial, unsafe_artifact, response=json.dumps(unsafe_artifact, sort_keys=True)))
            records.append(record_for(case, "disabled", trial, {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "builtin_component_sufficient"}))
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("safety regression" in failure for failure in failures))

    def test_disabled_workspace_has_no_skill_or_held_out_fixture(self):
        harness = load_module("harness", "run_harness.py")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            agent = workspace / "source-agent"
            agent.write_text("#!/bin/sh\n")
            agent.chmod(0o755)
            harness.prepare_workspace(workspace, agent, {"prompt": "Hello"}, "disabled")
            self.assertEqual(
                {path.name for path in workspace.iterdir()},
                {"case.json", "runner", "target-agent", "source-agent"},
            )
            self.assertEqual(workspace.stat().st_mode & 0o777, 0o700)

    def test_isolated_command_disables_network_and_uses_empty_home(self):
        harness = load_module("harness", "run_harness.py")
        command = harness.isolated_command(Path("/tmp/workspace"), "agent@sha256:test")
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn(f"{os.getuid()}:{os.getgid()}", command)
        self.assertIn("HOME=/home/agent", command)
        self.assertIn("--read-only", command)

    def test_profile_rejects_unreviewed_agent_and_image(self):
        harness = load_module("harness", "run_harness.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = root / "eval" / "targets"
            targets.mkdir(parents=True)
            agent = targets / "target-agent"
            agent.write_text("#!/bin/sh\n")
            profile = root / "profile.json"
            profile.write_text(json.dumps({"images": [], "targets": []}))
            harness.ROOT = root
            harness.TARGETS = targets
            with self.assertRaisesRegex(SystemExit, "reviewed sterile profile"):
                harness.validate_profile(profile, "agent@sha256:test", agent)

    def test_profile_admits_the_checked_in_reference_target(self):
        harness = load_module("harness", "run_harness.py")
        profile = json.loads(harness.PROFILE.read_text())
        agent = harness.TARGETS / "reference-filament-plugin-first-agent.py"
        self.assertTrue(agent.is_file())
        harness.validate_profile(harness.PROFILE, profile["images"][0], agent)

    def test_contract_rejects_held_out_prompt_in_tuning(self):
        contract = load_module("contract", "check-contract.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            held_out, tuning = root / "held-out.json", root / "tuning.json"
            shared_case = {
                "id": "shared", "split": "held_out", "prompt": "duplicated prompt text", "category": "should_use",
                "unsafe_candidates": [], "expected_outcome": {"decision": "install", "chosen_candidate": "vendor/x", "primary_reason": "best_compatible_maintained_licensed_free_option"},
            }
            held_out.write_text(json.dumps({"cases": [shared_case]}))
            tuning.write_text(json.dumps({"cases": [{**shared_case, "id": "shared-tuning", "split": "tuning"}]}))
            failures = contract.validate_corpus(held_out, tuning)
        self.assertTrue(any("held-out prompt appears" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
