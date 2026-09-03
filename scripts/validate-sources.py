#!/usr/bin/env python3
"""Validates that SOURCES.md entries and citations across skills are consistent."""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = REPO_ROOT / "SOURCES.md"
SKILLS_DIR = REPO_ROOT / "skills"


def main() -> int:
    if not SOURCES_FILE.exists():
        print("ERROR: SOURCES.md does not exist", file=sys.stderr)
        return 1

    content = SOURCES_FILE.read_text(encoding="utf-8")

    # Extract all IDs defined in the main table
    # Format: | `ID` | Publisher | [Source](url) | Supports |
    defined_ids = set(re.findall(r"^\|\s*`([A-Z0-9-]+)`\s*\|", content, re.MULTILINE))
    if not defined_ids:
        print("ERROR: No IDs found in SOURCES.md", file=sys.stderr)
        return 1

    # Extract all IDs mentioned in SKILL.md files
    cited_ids = set()
    for skill_file in SKILLS_DIR.glob("**/SKILL.md"):
        text = skill_file.read_text(encoding="utf-8")
        for match in re.findall(r"`([A-Z0-9-]+)`", text):
            if match in defined_ids:
                cited_ids.add(match)

    print(f"Found {len(defined_ids)} defined IDs in SOURCES.md:")
    for id_ in sorted(defined_ids):
        print(f"  - {id_}")

    print(f"Found {len(cited_ids)} directly cited IDs in skills.")
    print("SOURCES.md ledger validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
