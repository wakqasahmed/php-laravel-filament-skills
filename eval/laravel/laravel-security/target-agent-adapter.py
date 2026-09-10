#!/usr/bin/env python3
"""Adapt a target agent's observable laravel-security decision."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


WORKSPACE = Path(os.environ.get("HARNESS_WORKSPACE", "/workspace"))


def main() -> int:
    case = json.loads((WORKSPACE / "case.json").read_text())
    outcome_path = WORKSPACE / "outcome.json"
    model = case.get("model") or os.environ.get("HARNESS_MODEL", "")
    request = {
        "prompt": case["prompt"],
        "model": model,
        "outcome_path": str(outcome_path),
        "response_format": "JSON object describing the user-visible Laravel security decision",
    }
    skill = WORKSPACE / "SKILL.md"
    if skill.is_file():
        request["skill_path"] = str(skill)

    env = {
        "HOME": "/home/agent",
        "LANG": "C",
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "PYTHONNOUSERSITE": "1",
        "NO_PROXY": "*",
        "no_proxy": "*",
    }
    for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_BASE_URL", "HARNESS_MODEL_URL", "HARNESS_LOG_INVOCATIONS", "HARNESS_MODEL"):
        if var in os.environ:
            env[var] = os.environ[var]

    result = subprocess.run(
        [sys.executable, str(WORKSPACE / "target-agent")], input=json.dumps(request), text=True, capture_output=True,
        check=True, cwd=WORKSPACE,
        env=env,
    )
    response = result.stdout.strip()
    if not response:
        raise SystemExit("target agent returned an empty response")
    if not outcome_path.is_file():
        raise SystemExit("target agent did not write outcome.json")
    artifact = json.loads(outcome_path.read_text())
    if not isinstance(artifact, dict):
        raise SystemExit("outcome.json must contain an object")
    if artifact.get("model") != model:
        raise SystemExit(f"target agent ignored requested model: expected {model}, got {artifact.get('model')}")
    if artifact.get("is_canned"):
        raise SystemExit("target agent returned a canned skill-path-dependent result")
    print(json.dumps({"response": response, "artifact": artifact}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
