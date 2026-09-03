#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
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
        case = load_case("fc-01-relationship-column-eager-load")
        record = record_for(case, "enabled", 1, case["expected_outcome"])
        record["outcome"] = "forged-pass"
        failures, _ = validator.validate([record], 3)
        self.assertTrue(any("invalid observable artifact" in failure for failure in failures))

    def test_validator_rejects_keyword_soup_response(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = all_records(3)
        for record in records:
            if record["case_id"] == "fc-01-relationship-column-eager-load" and record["condition"] == "enabled":
                record["response"] = "Yes, we should use eager_load_relationships_via_modify_query for Prevent N+1 queries."
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("is below the 80% outcome threshold" in failure for failure in failures))

    def test_independent_safety_check_detects_unsafe_pattern(self):
        validator = load_module("validator", "validate-harness-results.py")
        case = load_case("fc-01-relationship-column-eager-load")
        safe_record = record_for(case, "enabled", 1, case["expected_outcome"])
        self.assertTrue(validator.is_safe(safe_record, case))

        unsafe_record = record_for(case, "enabled", 1, case["expected_outcome"], response=json.dumps(case["expected_outcome"]) + " with query_relation_per_row_without_eager_loading")
        self.assertFalse(validator.is_safe(unsafe_record, case))

    def test_validator_enforces_safety_regression_gate(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = all_records(3)
        case = load_case("fc-01-relationship-column-eager-load")
        for record in records:
            if record["case_id"] == case["id"] and record["condition"] == "enabled":
                record["response"] = json.dumps(case["expected_outcome"]) + " " + case["unsafe_patterns"][0]
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("safety regression" in failure for failure in failures))

    def test_validator_enforces_outcome_threshold(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = all_records(3)
        for record in records:
            if record["case_id"] == "fc-01-relationship-column-eager-load" and record["condition"] == "enabled" and record["trial"] in (1, 2):
                record["artifact"] = {"decision": "preserve_existing", "chosen_pattern": "none", "primary_reason": "none"}
                record["response"] = json.dumps(record["artifact"])
        failures, _ = validator.validate(records, 3)
        self.assertTrue(any("is below the 80% outcome threshold" in failure for failure in failures))

    def test_all_records_pass_cleanly(self):
        validator = load_module("validator", "validate-harness-results.py")
        records = all_records(3)
        failures, reports = validator.validate(records, 3)
        self.assertEqual(failures, [])
        self.assertTrue(any("aggregate outcome delta +100%" in r for r in reports))

    def test_contract_checks_pass(self):
        contract = load_module("contract", "check-contract.py")
        failures = contract.validate_corpus()
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
