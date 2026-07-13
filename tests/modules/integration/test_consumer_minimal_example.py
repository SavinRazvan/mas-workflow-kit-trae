"""
File: test_consumer_minimal_example.py
Path: tests/modules/integration/test_consumer_minimal_example.py
Role: Integration test for examples/consumer-minimal activate path.
Used By:
 - pytest
Depends On:
 - .ai_infra/install/trae_workflow/activate_cli.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_README = REPO_ROOT / "examples" / "consumer-minimal" / "README.md"


def test_consumer_minimal_example_readme_exists() -> None:
    assert EXAMPLE_README.is_file()
    text = EXAMPLE_README.read_text(encoding="utf-8")
    assert "trae_workflow activate" in text


def test_activate_into_empty_consumer_dir(tmp_path: Path) -> None:
    target = tmp_path / "consumer-app"
    target.mkdir()
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "trae_workflow",
            "activate",
            "--directory",
            str(target),
            "--profile",
            "default",
            "--source",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert (target / ".trae" / "agents" / "implementer.md").is_file()
    assert (target / ".local" / "index-and-planning" / "current" / "session-pointer.md").is_file()
