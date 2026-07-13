"""
File: test_scaffold_trae_only.py
Path: tests/modules/install/test_scaffold_trae_only.py
Role: Tests scaffold install with default profile (ADR-009).
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/install/scaffold.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCAFFOLD_PATH = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "scaffold.py"


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("scaffold", SCAFFOLD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["scaffold"] = module
    spec.loader.exec_module(module)
    return module


def test_scaffold_default_copies_trae_not_cursor(tmp_path: Path) -> None:
    mod = _load_scaffold()
    target = tmp_path / "consumer"
    mod.scaffold(target, REPO_ROOT, profile="default")
    assert (target / ".trae" / "agents" / "implementer.md").is_file()
    assert (target / "trae_workflow" / "__main__.py").is_file()
    assert not (target / ".cursor" / "agents" / "implementer.md").is_file()
