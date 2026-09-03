#!/usr/bin/env python3
"""Offline contract checks for the Filament conventions skill."""
import json
import re
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parents[2] if len(EVAL_DIR.parents) >= 3 else EVAL_DIR.parent
SKILL = (EVAL_DIR.parent / "SKILL.md") if (EVAL_DIR.parent / "SKILL.md").exists() else (ROOT / "skills" / "filament" / "filament-conventions" / "SKILL.md")
HELD_OUT = EVAL_DIR / "fixtures" / "held-out.json"
TUNING = EVAL_DIR / "fixtures" / "tuning.json"
CONTRACT_RULES = {
    "version check command": r"composer show filament/filament \| grep versions",
    "v4 schema unification": r"v4 represents schemas with `Filament\\Schemas\\Schema`",
    "one resource per model": r"One resource per model",
    "relation managers": r"Use relation managers for related data, not custom inline tables",
    "policies over gates": r"Prefer policies for authorization over inline gate checks",
    "schema components over raw html": r"Build forms with schema components, not raw HTML",
    "eager load relationships": r"Prevent N\+1 queries on relationship columns",
    "custom action classes": r"Implement custom actions as action classes, not inline closures",
    "centralize tenant scope": r"Centralize tenant scope in the panel provider or middleware",
}
REQUIRED_FIELDS = {"id", "split", "prompt", "expected_outcome", "unsafe_patterns", "category"}
OUTCOME_FIELDS = {"decision", "chosen_pattern", "primary_reason"}
VALID_DECISIONS = {"apply_convention", "refactor_pattern", "preserve_existing"}
VALID_CATEGORIES = {"should_use", "near_miss", "safety"}


def validate_corpus(held_out_path: Path = HELD_OUT, tuning_path: Path = TUNING) -> list[str]:
    failures, prompts, ids = [], set(), set()
    cases = json.loads(held_out_path.read_text(encoding="utf-8"))["cases"]
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
        elif not case["expected_outcome"]["chosen_pattern"]:
            failures.append(f"{case['id']} is missing a chosen_pattern")
        if not isinstance(case["unsafe_patterns"], list):
            failures.append(f"{case['id']} has a non-list unsafe_patterns")
        elif case["expected_outcome"].get("chosen_pattern") in case["unsafe_patterns"]:
            failures.append(f"{case['id']} expects an unsafe pattern to be chosen")
        if case["category"] not in VALID_CATEGORIES:
            failures.append(f"{case['id']} has an invalid category")
        elif case["category"] == "safety" and not case["unsafe_patterns"]:
            failures.append(f"{case['id']} is tagged safety but has no unsafe_patterns")
    if len(cases) < 10:
        failures.append("held-out manifest needs at least ten cases")
    should_use = sum(case["category"] == "should_use" for case in cases)
    should_not_use = sum(case["category"] in ("near_miss", "safety") for case in cases)
    if should_use < 5:
        failures.append("held-out manifest needs at least five should-use cases")
    if should_not_use < 5:
        failures.append("held-out manifest needs at least five should-not-use/near-miss/safety cases")
    tuning_prompts = {case["prompt"] for case in json.loads(tuning_path.read_text(encoding="utf-8"))["cases"]}
    if prompts & tuning_prompts:
        failures.append("held-out prompt appears in tuning corpus")
    return failures


if __name__ == "__main__":
    text = SKILL.read_text(encoding="utf-8")
    failures = [f"SKILL.md is missing required contract text: {name}" for name, pattern in CONTRACT_RULES.items() if not re.search(pattern, text)]
    failures.extend(validate_corpus())
    if failures:
        print("FAIL: deterministic filament-conventions contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        raise SystemExit(1)
    print("PASS: deterministic filament-conventions contract checks")
