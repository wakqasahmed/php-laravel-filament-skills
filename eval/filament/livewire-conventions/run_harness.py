#!/usr/bin/env python3
"""Run isolated enabled and disabled livewire-conventions trials."""
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
CASES = EVAL_DIR / "fixtures" / "held-out.json"
ADAPTER = EVAL_DIR / "target-agent-adapter.py"
HARNESS_VERSION = "1"
PROFILE = EVAL_DIR / "sterile-profile.json"
TARGETS = EVAL_DIR / "targets"


def prepare_workspace(workspace: Path, agent: Path, case: dict, condition: str) -> None:
    workspace.chmod(0o700)
    (workspace / "case.json").write_text(json.dumps({"prompt": case["prompt"]}))
    for source, target in ((ADAPTER, "runner"), (agent, "target-agent")):
        shutil.copy2(source, workspace / target)
        (workspace / target).chmod(0o755)
    if condition == "enabled":
        shutil.copy2(ROOT / "skills" / "filament" / "livewire-conventions" / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--user", f"{os.getuid()}:{os.getgid()}", "--pids-limit", "64",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--tmpfs", "/home/agent:rw,noexec,nosuid,size=8m",
        "--mount", f"type=bind,source={workspace},target=/workspace",
        "--env", "HARNESS_WORKSPACE=/workspace", "--env", "HOME=/home/agent", "--env", "PYTHONNOUSERSITE=1",
        "--env", "PATH=/usr/local/bin:/usr/bin:/bin", "--workdir", "/workspace", image, "/workspace/runner",
    ]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(path: Path, image: str, agent: Path) -> None:
    if not agent.is_relative_to(TARGETS):
        raise SystemExit("target agent must be in eval/targets")
    profile = json.loads(path.read_text())
    entry = {"path": str(agent.relative_to(ROOT)).replace("\\", "/"), "sha256": file_sha256(agent)}
    if image not in profile.get("images", []) or entry not in profile.get("targets", []):
        raise SystemExit("agent and image must be admitted by the reviewed sterile profile")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--output", type=Path, default=EVAL_DIR / "results.json")
    args = parser.parse_args()

    agent = args.agent.resolve()
    validate_profile(PROFILE, args.image, agent)
    cases = json.loads(CASES.read_text())["cases"]
    results = []

    for case in cases:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
                    workspace = Path(temp_dir)
                    prepare_workspace(workspace, agent, case, condition)
                    completed = subprocess.run(
                        isolated_command(workspace, args.image),
                        capture_output=True, text=True, check=True,
                    )
                    payload = json.loads(completed.stdout.strip())
                    results.append({
                        "case_id": case["id"],
                        "condition": condition,
                        "trial": trial,
                        "model": args.model,
                        "harness_version": HARNESS_VERSION,
                        "response": payload["response"],
                        "artifact": payload["artifact"],
                    })

    args.output.write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
