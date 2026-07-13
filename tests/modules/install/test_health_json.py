"""
File: test_health_json.py
Path: tests/modules/install/test_health_json.py
Role: Tests trae-workflow health --json output.
Used By:
 - pytest
Depends On:
 - .ai_infra/install/trae_workflow/cli.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_health_json_passes_on_kit_root(capsys) -> None:
    from trae_workflow.cli import cmd_health, kit_root

    class Args:
        directory = kit_root()
        json = True

    code = cmd_health(Args())
    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "pass"
    assert payload["issues"] == []
    assert payload["kit_version"]
