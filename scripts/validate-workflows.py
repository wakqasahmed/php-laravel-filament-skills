#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import yaml

FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")
ALLOWED_WRITE_PERMISSIONS = {
    "ocr-manual-review.yml": {"issues", "pull-requests"},
    "open-code-review.yml": {"pull-requests"},
}


def iter_uses(workflow: dict):
    jobs = workflow.get("jobs") or {}
    if not isinstance(jobs, dict):
        return
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and "uses" in step:
                yield step["uses"]


def iter_permission_blocks(workflow: dict):
    top = workflow.get("permissions")
    if top is not None:
        yield top
    jobs = workflow.get("jobs") or {}
    if not isinstance(jobs, dict):
        return
    for job in jobs.values():
        if isinstance(job, dict) and "permissions" in job:
            yield job["permissions"]


root = Path(__file__).resolve().parents[1]
workflows_dir = root / ".github" / "workflows"
workflow_paths = sorted((*workflows_dir.glob("*.yml"), *workflows_dir.glob("*.yaml")))
errors = []
action_count = 0

for path in workflow_paths:
    relative_path = path.relative_to(root)
    text = path.read_text()
    try:
        workflow = yaml.safe_load(text)
    except yaml.YAMLError as error:
        errors.append(f"{relative_path}: could not parse YAML: {error}")
        continue
    if not isinstance(workflow, dict):
        errors.append(f"{relative_path}: workflow did not parse to a mapping")
        continue

    for action in iter_uses(workflow):
        if not isinstance(action, str) or action.startswith("./"):
            continue
        action_count += 1
        if "@" not in action or not FULL_SHA.fullmatch(action.rsplit("@", 1)[1]):
            errors.append(f"{relative_path}: action is not pinned to a full SHA: {action}")

    blocks = list(iter_permission_blocks(workflow))
    allowed_writes = ALLOWED_WRITE_PERMISSIONS.get(path.name.lower(), set())
    for block in blocks:
        if isinstance(block, str):
            if block not in {"read-all"}:
                errors.append(f"{relative_path}: unsupported or writable inline permissions")
            continue
        if not isinstance(block, dict):
            errors.append(f"{relative_path}: unrecognized permissions value: {block!r}")
            continue
        for permission, access in block.items():
            if access == "write" and permission not in allowed_writes:
                errors.append(f"{relative_path}: unexpected write permission: {permission}")

    if path.name.endswith("-outcome-eval.yml") and not any(b == {"contents": "read"} for b in blocks):
        errors.append(f"{relative_path}: eval workflow permissions must declare contents: read")

    if path.name == "ci.yml" and not any(b == {"contents": "read"} for b in blocks):
        errors.append(f"{relative_path}: CI workflow permissions must declare contents: read")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)

print(f"validated {action_count} pinned action references across {len(workflow_paths)} workflows")
