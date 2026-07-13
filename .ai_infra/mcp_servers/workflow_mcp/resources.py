"""
File: resources.py
Path: .ai_infra/mcp_servers/workflow_mcp/resources.py
Role: Resolve workflow:// MCP resource URIs to repo files (read-only).
Used By:
 - workflow_mcp/server.py
Depends On:
 - workflow_mcp/gates.py, workspace.py
 - ide_contract_paths (via sys.path bootstrap)
Notes:
 - P1 resources per IMPLEMENTATION-STATUS.md. No second GATES list in inventory.
 - Agents resolved from `.trae/agents` (Trae edition SSOT per ADR-009).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from workflow_mcp.gates import load_gates

_AI_INFRA = Path(__file__).resolve().parents[2]
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))

from ide_contract_paths import CURSOR, TRAE, agents_dir, maintainer_skills_dir, skills_dir  # noqa: E402

_PR_PHASES = {
    "review": "review.md",
    "prep": "prep.md",
    "prepare": "prep.md",
    "merge": "merge.md",
}

_TRACKER_NAMES = frozenset(
    {
        "session-pointer",
        "plan",
        "work-tracker",
        "change-index",
        "test-plan",
        "test-index",
        "coverage-index",
        "architecture",
    }
)


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def _find_agent_path(root: Path, agent_id: str) -> Path:
    for ide in (TRAE, CURSOR):
        candidate = agents_dir(root, ide) / f"{agent_id}.md"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"agent not found: {agent_id}")


def read_agent(root: Path, agent_id: str) -> str:
    return _read_text(_find_agent_path(root, agent_id))


def _find_skill_path(root: Path, skill_id: str) -> Path:
    candidates = [
        skills_dir(root, TRAE) / skill_id / "SKILL.md",
        skills_dir(root, CURSOR) / skill_id / "SKILL.md",
        maintainer_skills_dir(root) / skill_id / "SKILL.md",
        maintainer_skills_dir(root) / f"{skill_id}.md",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"skill not found: {skill_id}")


def read_skill(root: Path, skill_id: str) -> str:
    return _read_text(_find_skill_path(root, skill_id))


def read_pr_artifact(root: Path, phase: str) -> str:
    filename = _PR_PHASES.get(phase.lower())
    if filename is None:
        allowed = ", ".join(sorted(_PR_PHASES))
        raise ValueError(f"Unknown PR phase '{phase}'. Allowed: {allowed}")
    path = root / ".local" / "workflow-artifacts" / "pr" / filename
    return _read_text(path)


def read_tracker(root: Path, name: str) -> str:
    if name not in _TRACKER_NAMES:
        allowed = ", ".join(sorted(_TRACKER_NAMES))
        raise ValueError(f"Unknown tracker '{name}'. Allowed: {allowed}")
    path = root / ".local" / "index-and-planning" / "current" / f"{name}.md"
    return _read_text(path)


def _list_agent_ids(root: Path) -> list[str]:
    ids: set[str] = set()
    for ide in (TRAE, CURSOR):
        agents = agents_dir(root, ide)
        if agents.is_dir():
            ids.update(p.stem for p in agents.glob("*.md"))
    return sorted(ids)


def _list_skill_ids(root: Path) -> list[str]:
    ids: set[str] = set()
    for base in (skills_dir(root, TRAE), skills_dir(root, CURSOR), maintainer_skills_dir(root)):
        if not base.is_dir():
            continue
        for skill_md in base.rglob("SKILL.md"):
            if skill_md.parent != base:
                ids.add(skill_md.parent.name)
        for md in base.glob("*.md"):
            ids.add(md.stem)
    return sorted(ids)


def build_inventory(root: Path) -> str:
    """Minimal live inventory JSON — not a duplicate of prepare.py GATES commands."""
    payload = {
        "schema": "workflow-kit-inventory/v1",
        "agents": _list_agent_ids(root),
        "skills": _list_skill_ids(root),
        "gate_count": len(load_gates(root)),
        "workspace_root": str(root),
    }
    return json.dumps(payload, indent=2)


def read_project_config(root: Path) -> str:
    for candidate in (root / "project.config.yaml", root / ".ai_infra" / "project.config.yaml.example"):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    return "project.config.yaml not found; copy .ai_infra/project.config.yaml.example"


def _load_registry_yaml(root: Path) -> dict:
    for candidate in (
        root / ".trae" / "mcp.registry.yaml",
        root / ".trae" / "mcp.registry.yaml.example",
        root / ".cursor" / "mcp.registry.yaml",
        root / ".cursor" / "mcp.registry.yaml.example",
    ):
        if candidate.is_file():
            data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    raise FileNotFoundError("mcp.registry.yaml not found")


def read_mcp_registry(root: Path) -> str:
    return json.dumps(_load_registry_yaml(root), indent=2)


def read_mcp_connection_guide(root: Path) -> str:
    doc = root / ".ai_infra" / "docs" / "operations" / "connect-external-mcp.md"
    if not doc.is_file():
        raise FileNotFoundError(str(doc))
    return doc.read_text(encoding="utf-8")
