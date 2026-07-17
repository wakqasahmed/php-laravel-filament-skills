#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
skills = plugin.get("skills", [])

declared_skill_files = {root / skill / "SKILL.md" for skill in skills}
discovered_skill_files = set((root / "skills").glob("**/SKILL.md"))

undeclared = sorted(str(path.relative_to(root)) for path in discovered_skill_files - declared_skill_files)
if undeclared:
    raise SystemExit("Skills missing from plugin manifest: " + ", ".join(undeclared))

missing = [skill for skill in skills if not (root / skill / "SKILL.md").is_file()]
if missing:
    raise SystemExit("Missing plugin skill paths: " + ", ".join(missing))

mismatched = []
for skill in skills:
    skill_md = root / skill / "SKILL.md"
    content = skill_md.read_text()
    match = re.search(r"^name:\s*(\S+)\s*$", content, re.MULTILINE)
    if not match:
        mismatched.append(f"{skill}: no 'name:' frontmatter field found")
        continue
    if not re.search(r"^description:\s*\S", content, re.MULTILINE):
        mismatched.append(f"{skill}: no 'description:' frontmatter field found")
        continue
    name = match.group(1).strip().strip("'\"")
    directory = Path(skill).name
    if name != directory:
        mismatched.append(f"{skill}: name '{name}' does not match directory '{directory}'")
if mismatched:
    raise SystemExit("Skill name/directory mismatch: " + "; ".join(mismatched))

print(f"validated {len(skills)} plugin skills")
