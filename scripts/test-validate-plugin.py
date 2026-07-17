#!/usr/bin/env python3
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "validate-plugin.py"


class ValidatePluginTest(unittest.TestCase):
    def create_plugin(self, skill_content):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        (root / "scripts").mkdir()
        shutil.copy(VALIDATOR, root / "scripts" / "validate-plugin.py")
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "skills": ["./skills/example"],
        }))
        skill = root / "skills" / "example" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(skill_content)
        return directory, root

    def validate(self, root):
        return subprocess.run(
            ["python3", "scripts/validate-plugin.py"],
            cwd=root,
            capture_output=True,
            text=True,
        )

    def test_ignores_skills_in_node_modules(self):
        directory, root = self.create_plugin("---\nname: example\ndescription: Example skill\n---\n")
        self.addCleanup(directory.cleanup)
        dependency_skill = root / "skills" / "example" / "node_modules" / "dependency" / "SKILL.md"
        dependency_skill.parent.mkdir(parents=True)
        dependency_skill.write_text("---\nname: dependency\ndescription: Dependency skill\n---\n")

        result = self.validate(root)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_description_outside_frontmatter(self):
        directory, root = self.create_plugin("---\nname: example\n---\n\ndescription: Not frontmatter\n")
        self.addCleanup(directory.cleanup)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no 'description:' frontmatter field found", result.stderr)

    def test_rejects_name_outside_frontmatter(self):
        directory, root = self.create_plugin("---\ndescription: Example skill\n---\n\nname: example\n")
        self.addCleanup(directory.cleanup)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no 'name:' frontmatter field found", result.stderr)


if __name__ == "__main__":
    unittest.main()
