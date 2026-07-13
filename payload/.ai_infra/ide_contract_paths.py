"""
File: ide_contract_paths.py
Path: .ai_infra/ide_contract_paths.py
Role: IDE-specific contract plane path resolver (Cursor, Trae).
Used By:
 - .ai_infra/scripts/release/sync_trae_contract.py
 - .ai_infra/scripts/install/plane_status.py
 - .ai_infra/mcp_servers/workflow_mcp/resources.py
 - .ai_infra/install/trae_workflow/mcp_manage.py
Depends On:
 - pathlib (stdlib)
Notes:
 - Trae edition (default): .trae/ is SSOT (ADR-009). Dual-IDE: .cursor/ SSOT (ADR-008).
"""

from __future__ import annotations

import os
from pathlib import Path

CURSOR = "cursor"
TRAE = "trae"
TRAE_ONLY_PROFILE = "default"

_IDE_ROOTS: dict[str, str] = {
    CURSOR: ".cursor",
    TRAE: ".trae",
}

_SUPPORTED_IDES = frozenset(_IDE_ROOTS)


def normalize_ide(ide: str) -> str:
    key = ide.strip().lower().lstrip(".")
    if key not in _SUPPORTED_IDES:
        allowed = ", ".join(sorted(_SUPPORTED_IDES))
        raise ValueError(f"unsupported IDE '{ide}'; allowed: {allowed}")
    return key


def contract_root(root: Path, ide: str) -> Path:
    return root / _IDE_ROOTS[normalize_ide(ide)]


def agents_dir(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "agents"


def rules_dir(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "rules"


def skills_dir(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "skills"


def mcp_json(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.json"


def mcp_kit_example(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.json.kit.example"


def mcp_user_json(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.user.json"


def mcp_user_example(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.user.example.json"


def mcp_registry(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.registry.yaml"


def mcp_registry_example(root: Path, ide: str) -> Path:
    return contract_root(root, ide) / "mcp.registry.yaml.example"


def maintainer_skills_dir(root: Path) -> Path:
    """Maintainer slash skills — shared across IDEs (.agents/skills/)."""
    return root / ".agents" / "skills"


def plane_prefix(ide: str) -> str:
    return _IDE_ROOTS[normalize_ide(ide)]


def all_ides() -> tuple[str, ...]:
    return (CURSOR, TRAE)


def uses_trae_ssot(root: Path, profile: str = "") -> bool:
    """True when Trae contract plane is authoritative (Trae edition or Cursor absent)."""
    if profile == TRAE_ONLY_PROFILE:
        return True
    env = os.environ.get("TRAE_ONLY", "").strip().lower()
    if env in ("1", "true", "yes"):
        return True
    cursor_rules = root / ".cursor" / "rules"
    if cursor_rules.is_dir() and any(cursor_rules.glob("*.mdc")):
        return False
    return (root / ".trae" / "rules").is_dir()


def ssot_ide(root: Path, profile: str = "") -> str:
    return TRAE if uses_trae_ssot(root, profile) else CURSOR
