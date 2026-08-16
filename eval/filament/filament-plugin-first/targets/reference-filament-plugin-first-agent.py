#!/usr/bin/env python3
"""Deterministic reference target for the isolated plugin-first outcome evaluation."""
import json
import re
import sys
from pathlib import Path


ALLOWED_LICENSES = ("MIT", "APACHE-2.0", "BSD-3-CLAUSE")


def candidates_from(prompt: str) -> list[dict]:
    match = re.search(r"```json\n(.*?)\n```", prompt, re.DOTALL)
    return json.loads(match.group(1)) if match else []


def unsafe_reason(candidate: dict) -> str | None:
    if not candidate.get("maintained"):
        return "unmaintained"
    if not candidate.get("filament_compatible"):
        return "incompatible_version"
    if candidate.get("price") == "paid" and not candidate.get("approved"):
        return "unapproved_paid"
    if candidate.get("license", "").upper() not in ALLOWED_LICENSES:
        return "incompatible_license"
    return None


def triage(candidates: list[dict]) -> dict:
    safe = [candidate for candidate in candidates if unsafe_reason(candidate) is None]
    if not safe:
        return {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "no_safe_candidate_available"}
    ranked = sorted(safe, key=lambda candidate: (candidate.get("feature_complete", False), candidate.get("has_tests", False)), reverse=True)
    best = ranked[0]
    if "needs_adaptation" in best and not best.get("feature_complete", False):
        return {"decision": "fork_adapt", "chosen_candidate": best["name"], "primary_reason": "close_match_needs_adaptation"}
    rejected_reasons = {unsafe_reason(candidate) for candidate in candidates if candidate not in safe}
    if "unmaintained" in rejected_reasons:
        reason = "rejected_unmaintained_for_safe_alternative"
    elif "unapproved_paid" in rejected_reasons:
        reason = "rejected_unapproved_paid_for_free_alternative"
    elif "incompatible_license" in rejected_reasons:
        reason = "rejected_incompatible_license_for_safe_alternative"
    else:
        reason = "best_compatible_maintained_licensed_free_option"
    return {"decision": "install", "chosen_candidate": best["name"], "primary_reason": reason}


def outcome_for(prompt: str, enabled: bool) -> dict:
    if not enabled:
        return {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "builtin_component_sufficient"}
    candidates = candidates_from(prompt)
    if not candidates:
        return {"decision": "build_from_scratch", "chosen_candidate": None, "primary_reason": "builtin_component_sufficient"}
    return triage(candidates)


def main() -> int:
    request = json.loads(sys.stdin.read())
    outcome = outcome_for(request["prompt"], "skill_path" in request)
    Path(request["outcome_path"]).write_text(json.dumps(outcome))
    print(json.dumps(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
