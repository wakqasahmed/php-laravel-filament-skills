#!/usr/bin/env python3
"""Offline contract checks for the Filament plugin-first skill."""
import json
import re
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
HELD_OUT = EVAL_DIR / "fixtures" / "held-out.json"
TUNING = EVAL_DIR / "fixtures" / "tuning.json"
CONTRACT_RULES = {
    "search before building": r"Before writing custom code for these areas, search the ecosystem:",
    "no abandoned plugins": r"Do not trust abandoned plugins for production features\.",
    "verify before adding": r"Never add a dependency without verifying its source, maintenance status, and license\.",
    "paid requires approval": r"Require human approval for paid/proprietary plugins\.",
    "prefer tested packages": r"Prefer packages with tests and documented upgrade paths\.",
    "install choice": r"\*\*Install directly\*\* if compatible, maintained, and license matches\.",
    "fork choice": r"\*\*Fork/vendor and adapt\*\* if close but needs changes\.",
    "build choice": r"\*\*Build from scratch\*\* if no suitable candidate exists\.",
}
REQUIRED_FIELDS = {"id", "split", "prompt", "expected_outcome", "unsafe_candidates", "category"}
OUTCOME_FIELDS = {"decision", "chosen_candidate", "primary_reason"}
VALID_DECISIONS = {"install", "fork_adapt", "build_from_scratch"}
VALID_CATEGORIES = {"should_use", "near_miss", "safety"}


def validate_corpus(held_out_path: Path = HELD_OUT, tuning_path: Path = TUNING) -> list[str]:
    failures, prompts, ids = [], set(), set()
    cases = json.loads(held_out_path.read_text())["cases"]
    for case in cases:
        missing = REQUIRED_FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} is missing {sorted(missing)}")
            continue
        if case["id"] in ids:
            failures.append(f"duplicate held-out case id: {case['id']}")
        ids.add(case["id"])
        prompts.add(case["prompt"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if set(case["expected_outcome"]) != OUTCOME_FIELDS:
            failures.append(f"{case['id']} has an invalid expected outcome")
        elif case["expected_outcome"]["decision"] not in VALID_DECISIONS:
            failures.append(f"{case['id']} has an invalid decision")
        elif case["expected_outcome"]["decision"] == "build_from_scratch" and case["expected_outcome"]["chosen_candidate"] is not None:
            failures.append(f"{case['id']} builds from scratch but names a chosen_candidate")
        elif case["expected_outcome"]["decision"] != "build_from_scratch" and not case["expected_outcome"]["chosen_candidate"]:
            failures.append(f"{case['id']} is missing a chosen_candidate")
        if not isinstance(case["unsafe_candidates"], list):
            failures.append(f"{case['id']} has a non-list unsafe_candidates")
        elif case["expected_outcome"].get("chosen_candidate") in case["unsafe_candidates"]:
            failures.append(f"{case['id']} expects an unsafe candidate to be chosen")
        if case["category"] not in VALID_CATEGORIES:
            failures.append(f"{case['id']} has an invalid category")
        elif case["category"] == "safety" and not case["unsafe_candidates"]:
            failures.append(f"{case['id']} is tagged safety but has no unsafe_candidates")
    if len(cases) < 10:
        failures.append("held-out manifest needs at least ten cases")
    should_use = sum(case["category"] == "should_use" for case in cases)
    should_not_use = sum(case["category"] in ("near_miss", "safety") for case in cases)
    if should_use < 5:
        failures.append("held-out manifest needs at least five should-use triage cases")
    if should_not_use < 5:
        failures.append("held-out manifest needs at least five should-not-use/near-miss/safety cases")
    tuning_prompts = {case["prompt"] for case in json.loads(tuning_path.read_text())["cases"]}
    if prompts & tuning_prompts:
        failures.append("held-out prompt appears in tuning corpus")
    return failures


if __name__ == "__main__":
    text = SKILL.read_text()
    failures = [f"SKILL.md is missing required contract text: {name}" for name, pattern in CONTRACT_RULES.items() if not re.search(pattern, text)]
    failures.extend(validate_corpus())
    if failures:
        print("FAIL: deterministic filament-plugin-first contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        raise SystemExit(1)
    print("PASS: deterministic filament-plugin-first contract checks")
