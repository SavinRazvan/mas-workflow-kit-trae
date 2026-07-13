"""
File: test_plane_status_dual_ide.py
Path: tests/modules/install/test_plane_status_dual_ide.py
Role: Tests for dual_ide plane assessment (ADR-008).
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/install/plane_status.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PLANE_STATUS_PATH = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "plane_status.py"


def _load_plane_status():
    spec = importlib.util.spec_from_file_location("plane_status", PLANE_STATUS_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["plane_status"] = module
    spec.loader.exec_module(module)
    return module


def test_dual_ide_kit_repo_ready() -> None:
    plane_status = _load_plane_status()
    if not (REPO_ROOT / ".trae").is_dir():
        return  # skip until sync-plugin run in CI
    status = plane_status.assess_planes(REPO_ROOT, profile="dual_ide")
    assert status.cursor_contract
    assert status.trae_contract
    assert status.all_ready


def test_plane_for_path_trae_prefix() -> None:
    plane_status = _load_plane_status()
    assert plane_status._plane_for_path(".trae/rules/foo.md") == "trae"


def test_with_mcp_does_not_require_trae_paths(tmp_path: Path) -> None:
    plane_status = _load_plane_status()
    # Empty dir — trae_contract should not block when profile is with_mcp
    status = plane_status.assess_planes(tmp_path, profile="with_mcp")
    assert status.trae_contract is True
    assert not status.requires_trae


def test_dual_ide_missing_trae_not_all_ready(tmp_path: Path) -> None:
    """dual_ide without .trae/ must fail all_ready (AA-trae-101 regression)."""
    plane_status = _load_plane_status()
    contract = {
        "profiles": {
            "with_mcp": {"required_paths": ["AGENTS.md"]},
            "dual_ide": {
                "extends": "with_mcp",
                "required_paths": [".trae/mcp.json"],
            },
        }
    }
    contract_path = tmp_path / ".ai_infra" / "install-contract.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        __import__("json").dumps(contract),
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    status = plane_status.assess_planes(tmp_path, profile="dual_ide")
    assert status.requires_trae
    assert not status.trae_contract
    assert not status.all_ready
