#!/usr/bin/env python3
"""Validates that SOURCES.md entries and citations across skills are consistent."""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = REPO_ROOT / "SOURCES.md"
SKILLS_DIR = REPO_ROOT / "skills"
SOURCE_ID_PATTERN = re.compile(r"`([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+-\d{2})`")


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
        cited_ids.update(SOURCE_ID_PATTERN.findall(text))

    undefined_ids = cited_ids - defined_ids
    uncited_ids = defined_ids - cited_ids

    if undefined_ids:
        print("ERROR: Source IDs cited by skills but not defined in SOURCES.md:", file=sys.stderr)
        for id_ in sorted(undefined_ids):
            print(f"  - {id_}", file=sys.stderr)

    if uncited_ids:
        print("ERROR: Source IDs defined in SOURCES.md but not cited by any skill:", file=sys.stderr)
        for id_ in sorted(uncited_ids):
            print(f"  - {id_}", file=sys.stderr)

    if undefined_ids or uncited_ids:
        return 1

    print(f"Found {len(defined_ids)} defined IDs in SOURCES.md:")
    for id_ in sorted(defined_ids):
        print(f"  - {id_}")

    print(f"Found {len(cited_ids)} directly cited IDs in skills.")
    print("SOURCES.md ledger validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
