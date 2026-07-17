#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
skills = plugin.get("skills", [])

missing = [skill for skill in skills if not (root / skill / "SKILL.md").is_file()]
if missing:
    raise SystemExit("Missing plugin skill paths: " + ", ".join(missing))

mismatched = []
for skill in skills:
    skill_md = root / skill / "SKILL.md"
    match = re.search(r"^name:\s*(\S+)\s*$", skill_md.read_text(), re.MULTILINE)
    if not match:
        mismatched.append(f"{skill}: no 'name:' frontmatter field found")
        continue
    name = match.group(1).strip().strip("'\"")
    directory = Path(skill).name
    if name != directory:
        mismatched.append(f"{skill}: name '{name}' does not match directory '{directory}'")
if mismatched:
    raise SystemExit("Skill name/directory mismatch: " + "; ".join(mismatched))

print(f"validated {len(skills)} plugin skills")
