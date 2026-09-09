#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "validate-workflows.py"
PINNED_CHECKOUT = "actions/checkout@" + ("a" * 40)


class ValidateWorkflowsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.scripts_dir = self.temp_path / "scripts"
        self.scripts_dir.mkdir()
        self.script_path = self.scripts_dir / "validate-workflows.py"
        shutil.copyfile(VALIDATE_SCRIPT, self.script_path)
        self.workflows_dir = self.temp_path / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_workflow(self, name: str, content: str) -> Path:
        path = self.workflows_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def run_validator(self):
        return subprocess.run(
            [sys.executable, str(self.script_path)],
            cwd=self.temp_path,
            capture_output=True,
            text=True,
        )

    def test_accepts_pinned_unquoted_uses(self):
        self.write_workflow(
            "ci.yml",
            f"""\
name: CI
on: push
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: {PINNED_CHECKOUT}
""",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_mutable_ref_behind_a_quoted_uses_key(self):
        self.write_workflow(
            "ci.yml",
            """\
name: Bad
on: push
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - 'uses': attacker/action@main
""",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attacker/action@main", result.stderr)

    def test_rejects_write_permission_behind_a_quoted_permissions_key(self):
        self.write_workflow(
            "ci.yml",
            f"""\
name: Bad permissions
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    'permissions':
      'pull-requests': 'write'
    steps:
      - uses: {PINNED_CHECKOUT}
""",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pull-requests", result.stderr)

    def test_accepts_quoted_pinned_uses_value(self):
        self.write_workflow(
            "ci.yml",
            f"""\
name: Quoted value
on: push
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: '{PINNED_CHECKOUT}'
""",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_short_sha(self):
        self.write_workflow(
            "ci.yml",
            """\
name: Bad SHA
on: push
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@1234567
""",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("action is not pinned to a full SHA", result.stderr)


if __name__ == "__main__":
    unittest.main()
