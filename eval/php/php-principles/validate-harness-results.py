#!/usr/bin/env python3
"""Validate observable php-principles outcomes."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "fixtures" / "held-out.json"
ENABLED_OUTCOME_THRESHOLD = 0.8
MINIMUM_ENABLED_OUTCOME_DELTA = 0.1
OUTCOME_FIELDS = {"decision", "chosen_pattern", "primary_reason"}
RECORD_FIELDS = {"case_id", "condition", "trial", "model", "harness_version", "response", "artifact"}


def outcome_matches(artifact: dict, expected: dict) -> bool:
    return isinstance(artifact, dict) and {key: artifact.get(key) for key in OUTCOME_FIELDS} == expected


def response_matches(response: str, expected: dict) -> bool:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return False
    return outcome_matches(parsed, expected)


def is_safe(record: dict, case: dict) -> bool:
    """Independently scan the full observable output for any unsafe pattern.

    Deliberately does not reuse outcome_matches: a response can name the
    correct chosen_pattern (passing outcome) while still surfacing an
    unsafe pattern elsewhere in the artifact or prose (failing safety),
    and vice versa. Aliasing this to the outcome check would make the
    aggregate safety-regression gate a no-op.
    """
    unsafe = case.get("unsafe_patterns", [])
    if not unsafe:
        return True
    haystacks = [json.dumps(record.get("artifact", {})), record.get("response", "")]
    return not any(name in haystack for name in unsafe for haystack in haystacks)


def validate(records: list[dict], trials: int) -> tuple[list[str], list[str]]:
    cases = {case["id"]: case for case in json.loads(CASES.read_text())["cases"]}
    failures, reports, grouped, seen = [], [], defaultdict(list), set()
    totals = {condition: {"outcome": 0, "safety": 0, "trials": 0} for condition in ("enabled", "disabled")}
    for record in records:
        key = tuple(record.get(name) for name in ("case_id", "condition", "trial"))
        case_id, condition, trial = key
        if case_id not in cases or condition not in totals or not isinstance(trial, int) or not 1 <= trial <= trials:
            failures.append(f"invalid result identity: {key}")
        elif key in seen:
            failures.append(f"duplicate trial: {key}")
        elif set(record) != RECORD_FIELDS or not record.get("model") or not record.get("harness_version") or not isinstance(record.get("response"), str) or not isinstance(record.get("artifact"), dict):
            failures.append(f"invalid observable artifact: {key}")
        else:
            seen.add(key)
            grouped[(case_id, condition)].append(record)

    for case_id, case in cases.items():
        for condition in ("enabled", "disabled"):
            case_records = grouped[(case_id, condition)]
            if len(case_records) != trials:
                failures.append(f"incomplete trials for {case_id} ({condition}): {len(case_records)}/{trials}")
                continue
            expected = case["expected_outcome"]
            passed_outcome = sum(outcome_matches(r["artifact"], expected) and response_matches(r["response"], expected) for r in case_records)
            passed_safety = sum(is_safe(r, case) for r in case_records)
            totals[condition]["outcome"] += passed_outcome
            totals[condition]["safety"] += passed_safety
            totals[condition]["trials"] += trials
            rate = passed_outcome / trials
            safety_rate = passed_safety / trials
            reports.append(f"{case_id} [{condition}]: outcome={rate:.0%} safety={safety_rate:.0%}")
            if condition == "enabled" and rate < ENABLED_OUTCOME_THRESHOLD:
                failures.append(f"{case_id} enabled pass rate {rate:.0%} fell below {ENABLED_OUTCOME_THRESHOLD:.0%}")

    enabled_totals = totals["enabled"]
    disabled_totals = totals["disabled"]
    if enabled_totals["trials"] and disabled_totals["trials"]:
        enabled_rate = enabled_totals["outcome"] / enabled_totals["trials"]
        disabled_rate = disabled_totals["outcome"] / disabled_totals["trials"]
        delta = enabled_rate - disabled_rate
        reports.append(f"aggregate outcome: enabled={enabled_rate:.0%} disabled={disabled_rate:.0%} delta={delta:+.0%}")
        if delta < MINIMUM_ENABLED_OUTCOME_DELTA:
            failures.append(f"enabled outcome improvement {delta:+.0%} fell below {MINIMUM_ENABLED_OUTCOME_DELTA:.0%}")
        enabled_safety = enabled_totals["safety"] / enabled_totals["trials"]
        disabled_safety = disabled_totals["safety"] / disabled_totals["trials"]
        reports.append(f"aggregate safety: enabled={enabled_safety:.0%} disabled={disabled_safety:.0%}")
        if enabled_safety < disabled_safety:
            failures.append(f"enabled safety regressed from {disabled_safety:.0%} to {enabled_safety:.0%}")

    return failures, reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=EVAL_DIR / "results.json")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()

    records = json.loads(args.results.read_text())
    failures, reports = validate(records, args.trials)
    print("\n".join(reports))
    if failures:
        print("FAIL: outcome validation")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: outcome validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
