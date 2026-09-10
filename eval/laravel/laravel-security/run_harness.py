#!/usr/bin/env python3
"""Run isolated enabled and disabled laravel-security trials."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parents[2]
SKILL_DIR = ROOT / "skills" / "laravel" / "laravel-security"
CASES = EVAL_DIR / "fixtures" / "held-out.json"
ADAPTER = EVAL_DIR / "target-agent-adapter.py"
HARNESS_VERSION = "1"
PROFILE = EVAL_DIR / "sterile-profile.json"
TARGETS = EVAL_DIR / "targets"


def prepare_workspace(workspace: Path, agent: Path, case: dict, condition: str, model: str = "default") -> None:
    workspace.chmod(0o700)
    (workspace / "case.json").write_text(json.dumps({"id": case.get("id", "case"), "prompt": case["prompt"], "model": model}))
    for source, target in ((ADAPTER, "runner"), (agent, "target-agent")):
        shutil.copy2(source, workspace / target)
        (workspace / target).chmod(0o755)
    if condition == "enabled":
        shutil.copy2(SKILL_DIR / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, model: str = "default", network: str = "none") -> list[str]:
    cmd = [
        "docker", "run", "--rm", "--network", network, "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--user", f"{os.getuid()}:{os.getgid()}", "--pids-limit", "64",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--tmpfs", "/home/agent:rw,noexec,nosuid,size=8m",
        "--mount", f"type=bind,source={workspace},target=/workspace",
        "--env", "HARNESS_WORKSPACE=/workspace", "--env", "HOME=/home/agent", "--env", "PYTHONNOUSERSITE=1",
        "--env", "PATH=/usr/local/bin:/usr/bin:/bin", "--env", f"HARNESS_MODEL={model}",
        "--workdir", "/workspace",
    ]
    for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_BASE_URL", "HARNESS_MODEL_URL", "HARNESS_LOG_INVOCATIONS"):
        if var in os.environ:
            cmd.extend(["--env", f"{var}={os.environ[var]}"])
    cmd.extend([image, "/workspace/runner"])
    return cmd


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(path: Path, image: str, agent: Path) -> None:
    if not agent.is_relative_to(TARGETS):
        raise SystemExit("target agent must be in eval/targets")
    profile = json.loads(path.read_text())
    entry = {"path": str(agent.relative_to(ROOT)).replace("\\", "/"), "sha256": file_sha256(agent)}
    if image not in profile.get("images", []) or entry not in profile.get("targets", []):
        raise SystemExit("agent and image must be admitted by the reviewed sterile profile")


def validate_record(record: dict, expected_model: str) -> None:
    if set(record) != {"response", "artifact"} or not isinstance(record["response"], str) or not isinstance(record["artifact"], dict):
        raise SystemExit("target-agent adapter must emit text plus an outcome artifact")
    artifact = record["artifact"]
    if artifact.get("is_canned"):
        raise SystemExit("adapter returned a canned skill-path-dependent result")
    if artifact.get("model") != expected_model:
        raise SystemExit(f"adapter ignored requested model: expected {expected_model}, got {artifact.get('model')}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, choices=[3, 4, 5, 6], default=5)
    parser.add_argument("--output", type=Path, default=EVAL_DIR / "results.json")
    parser.add_argument("--network", default="none", choices=["none", "bridge", "host"])
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    agent = args.agent.resolve()
    if not agent.is_file() or not agent.is_relative_to(ROOT):
        raise SystemExit("agent must be a repository-controlled file")
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")
    validate_profile(PROFILE, args.image, agent)

    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    prepare_workspace(workspace, agent, case, condition, args.model)
                    result = subprocess.run(
                        isolated_command(workspace, args.image, args.model, args.network), text=True, capture_output=True, check=True,
                        env={"PATH": os.environ["PATH"], "HOME": "/nonexistent", "LANG": "C"},
                    )
                record = json.loads(result.stdout)
                validate_record(record, args.model)
                records.append({**record, "case_id": case["id"], "condition": condition, "trial": trial, "model": args.model, "harness_version": HARNESS_VERSION})
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
