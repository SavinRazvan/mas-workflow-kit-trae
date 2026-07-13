"""
File: test_scaffold_dual_ide.py
Path: tests/modules/install/test_scaffold_dual_ide.py
Role: Tests scaffold install with dual_ide profile (ADR-008).
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/install/scaffold.py
Notes:
 - Uses temporary directories; does not modify kit root.
"""

from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCAFFOLD_PATH = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "scaffold.py"


def _load_scaffold():
    module_name = f"scaffold_dual_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, SCAFFOLD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scaffold_dual_ide_copies_trae_and_mcp(tmp_path: Path) -> None:
    mod = _load_scaffold()
    target = tmp_path / "consumer"
    mod.scaffold(target, REPO_ROOT, profile="dual_ide")
    assert (target / ".trae" / "mcp.json").is_file()
    assert (target / ".trae" / "rules" / "agent-implementer.md").is_file()
    assert (target / ".cursor" / "mcp.json").is_file()
    cursor_mcp = json.loads((target / ".cursor" / "mcp.json").read_text(encoding="utf-8"))
    trae_mcp = json.loads((target / ".trae" / "mcp.json").read_text(encoding="utf-8"))
    assert "mcpServers" in cursor_mcp
    assert "mcpServers" in trae_mcp
    assert "workflow-kit" in cursor_mcp["mcpServers"]
    assert "workflow-kit" in trae_mcp["mcpServers"]
