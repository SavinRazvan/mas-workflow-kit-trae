"""
File: ide_contract_paths.py
Path: .ai_infra/ide_contract_paths.py
Role: IDE-specific contract plane path resolver (Cursor, Trae).
Used By:
 - .ai_infra/scripts/release/sync_trae_contract.py
 - .ai_infra/scripts/install/plane_status.py
 - .ai_infra/mcp_servers/workflow_mcp/resources.py
 - .ai_infra/install/cursor_workflow/mcp_manage.py
Depends On:
 - pathlib (stdlib)
Notes:
 - SSOT for human edits: .cursor/ + .agents/. Generated: .trae/ (ADR-008).
"""

from __future__ import annotations

from pathlib import Path

CURSOR = "cursor"
TRAE = "trae"

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
