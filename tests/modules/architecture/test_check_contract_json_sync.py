"""
File: test_check_contract_json_sync.py
Path: tests/modules/architecture/test_check_contract_json_sync.py
Role: Tests contract JSON sync guard between .trae/ and payload/.trae/.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/architecture/check_contract_json_sync.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / ".ai_infra" / "scripts" / "architecture" / "check_contract_json_sync.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_contract_json_sync", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_contract_json_sync"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_contract_json_sync_passes_when_matching(tmp_path: Path) -> None:
    mod = _load()
    trae = tmp_path / ".trae"
    payload = tmp_path / "payload" / ".trae"
    trae.mkdir(parents=True)
    payload.mkdir(parents=True)
    content = '{"mcpServers": {}}\n'
    (trae / "mcp.json").write_text(content, encoding="utf-8")
    (payload / "mcp.json").write_text(content, encoding="utf-8")
    assert mod.check_contract_json_sync(tmp_path) == []


def test_contract_json_sync_fails_on_drift(tmp_path: Path) -> None:
    mod = _load()
    trae = tmp_path / ".trae"
    payload = tmp_path / "payload" / ".trae"
    trae.mkdir(parents=True)
    payload.mkdir(parents=True)
    (trae / "mcp.json").write_text('{"a": 1}\n', encoding="utf-8")
    (payload / "mcp.json").write_text('{"a": 2}\n', encoding="utf-8")
    errors = mod.check_contract_json_sync(tmp_path)
    assert errors
    assert "mcp.json" in errors[0]


def test_main_passes_on_repo_root() -> None:
    mod = _load()
    assert mod.main(["--directory", str(REPO_ROOT)]) == 0
