#!/usr/bin/env python3
"""Offline contract checks for the Laravel security hardening skill."""
import json
import re
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parents[2] if len(EVAL_DIR.parents) >= 3 else EVAL_DIR.parent
SKILL = (EVAL_DIR.parent / "SKILL.md") if (EVAL_DIR.parent / "SKILL.md").exists() else (ROOT / "skills" / "laravel" / "laravel-security" / "SKILL.md")
HELD_OUT = EVAL_DIR / "fixtures" / "held-out.json"
TUNING = EVAL_DIR / "fixtures" / "tuning.json"
CONTRACT_RULES = {
    "mass assignment form request validated": r"Never pass `\$request->all\(\)` into `fill\(\)`/`create\(\)`/`update\(\)`; pass `\$request->validated\(\)`",
    "prefer fillable allowlist": r"Prefer `\$fillable` \(allowlist\) over `\$guarded` for any model reachable from user input",
    "parameterize bindings in raw sql": r"If a raw clause is unavoidable, pass user values as bindings, not interpolated strings",
    "allowlist dynamic identifiers": r"Allowlist the identifier against a fixed set of permitted values before use, never interpolate the request value directly",
    "blade double curly escaping default": r"`\{\{ \$value \}\}` HTML-escapes output automatically",
    "raw blade unescaped warning": r"`\{!! \$value !!\}` prints raw, unescaped HTML\. Only use it for content the application itself controls",
    "webhook signature verification on csrf exclusion": r"A CSRF exclusion is only safe if the route verifies the request some other way\. For webhooks, that means signature verification",
    "explicit policy authorization for idor": r"Every controller action that reads or mutates a specific record must have an explicit authorization check tied to that record",
}
REQUIRED_FIELDS = {"id", "split", "prompt", "expected_outcome", "unsafe_patterns", "category"}
OUTCOME_FIELDS = {"decision", "chosen_pattern", "primary_reason"}
VALID_DECISIONS = {"enforce_security", "refactor_vulnerability", "preserve_existing", "hold_for_clarification"}
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
    if not any(case["expected_outcome"].get("decision") == "hold_for_clarification" for case in cases):
        failures.append("held-out manifest needs at least one refusal/hold case")
    tuning_prompts = {case["prompt"] for case in json.loads(tuning_path.read_text(encoding="utf-8"))["cases"]}
    if prompts & tuning_prompts:
        failures.append("held-out prompt appears in tuning corpus")
    return failures


if __name__ == "__main__":
    text = SKILL.read_text(encoding="utf-8")
    failures = [f"SKILL.md is missing required contract text: {name}" for name, pattern in CONTRACT_RULES.items() if not re.search(pattern, text)]
    failures.extend(validate_corpus())
    if failures:
        print("FAIL: deterministic laravel-security contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        raise SystemExit(1)
    print("PASS: deterministic laravel-security contract checks")
