"""
File: test_ide_contract_paths.py
Path: tests/modules/ai_infra/test_ide_contract_paths.py
Role: Tests for ide_contract_paths module (ADR-008).
Used By:
 - pytest
Depends On:
 - .ai_infra/ide_contract_paths.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_AI_INFRA = REPO_ROOT / ".ai_infra"
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))

from ide_contract_paths import (
    CURSOR,
    TRAE,
    agents_dir,
    all_ides,
    contract_root,
    mcp_json,
    normalize_ide,
    plane_prefix,
    rules_dir,
    skills_dir,
)


def test_normalize_ide_cursor_variants() -> None:
    assert normalize_ide("cursor") == CURSOR
    assert normalize_ide(".cursor") == CURSOR
    assert normalize_ide("Cursor") == CURSOR


def test_normalize_ide_trae() -> None:
    assert normalize_ide("trae") == TRAE
    assert normalize_ide(".trae") == TRAE


def test_normalize_ide_invalid() -> None:
    with pytest.raises(ValueError, match="unsupported IDE"):
        normalize_ide("vscode")


def test_path_helpers(tmp_path: Path) -> None:
    root = tmp_path
    assert contract_root(root, CURSOR) == root / ".cursor"
    assert contract_root(root, TRAE) == root / ".trae"
    assert agents_dir(root, TRAE) == root / ".trae" / "agents"
    assert rules_dir(root, CURSOR) == root / ".cursor" / "rules"
    assert skills_dir(root, TRAE) == root / ".trae" / "skills"
    assert mcp_json(root, CURSOR) == root / ".cursor" / "mcp.json"


def test_plane_prefix() -> None:
    assert plane_prefix(CURSOR) == ".cursor"
    assert plane_prefix(TRAE) == ".trae"


def test_all_ides() -> None:
    assert CURSOR in all_ides()
    assert TRAE in all_ides()
