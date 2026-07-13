"""
File: plane_status.py
Path: .ai_infra/scripts/install/plane_status.py
Role: Assess workflow plane readiness (IDE contract, infrastructure, runtime; dual IDE adds Trae contract).
Used By:
 - .ai_infra/install/cursor_workflow/activate_cli.py
 - workflow_mcp workflow_activate
Depends On:
 - .ai_infra/install-contract.json
 - .ai_infra/ide_contract_paths.py
Notes:
 - Uses install-contract required_paths grouped by plane prefix.
 - dual_ide profile requires both cursor and trae contract planes (ADR-008).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_AI_INFRA = Path(__file__).resolve().parents[2]
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))

from ide_contract_paths import CURSOR, TRAE, plane_prefix  # noqa: E402


@dataclass(frozen=True)
class PlaneStatus:
    cursor_contract: bool
    trae_contract: bool
    infrastructure: bool
    runtime: bool
    missing: tuple[str, ...]
    requires_trae: bool = False

    @property
    def all_ready(self) -> bool:
        base = self.cursor_contract and self.infrastructure and self.runtime
        if self.requires_trae:
            return base and self.trae_contract
        return base


def _contract_path(root: Path) -> Path:
    return root / ".ai_infra" / "install-contract.json"


def _load_contract(root: Path) -> dict:
    path = _contract_path(root)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_profile(contract: dict, name: str) -> dict:
    if not contract:
        return {"required_paths": []}
    raw = contract.get("profiles", {}).get(name, {})
    if "extends" not in raw:
        return raw
    base = _resolve_profile(contract, raw["extends"])
    merged = {
        "required_paths": list(base.get("required_paths", [])),
        "forbidden_paths": list(base.get("forbidden_paths", [])),
    }
    merged["required_paths"].extend(raw.get("required_paths", []))
    merged["forbidden_paths"].extend(raw.get("forbidden_paths", []))
    return merged


def _plane_for_path(rel: str, *, profile: str = "with_mcp") -> str:
    if rel.startswith(".local/"):
        return "runtime"
    if rel.startswith(".ai_infra/") or rel.startswith("cursor_workflow/"):
        return "infrastructure"
    if rel.startswith(f"{plane_prefix(TRAE)}/"):
        return "trae"
    if rel.startswith(f"{plane_prefix(CURSOR)}/") or rel.startswith(".agents/") or rel == "AGENTS.md":
        return "cursor"
    if rel.startswith("tests/"):
        return "infrastructure"
    return "infrastructure"


def is_kit_dev_repo(root: Path) -> bool:
    return (root / "tests" / "modules" / "install" / "test_scaffold.py").is_file()


CONSUMER_ONLY_PATHS = frozenset(
    {
        "tests/modules/smoke/test_kit_installed.py",
    }
)


def assess_planes(root: Path, *, profile: str = "with_mcp") -> PlaneStatus:
    project_root = root.resolve()
    contract = _load_contract(project_root)
    spec = _resolve_profile(contract, profile)
    required = list(spec.get("required_paths") or [
        ".cursor/agents/implementer.md",
        ".ai_infra/scripts/pr/prepare.py",
        ".local/index-and-planning/current/session-pointer.md",
        "AGENTS.md",
    ])
    if is_kit_dev_repo(project_root):
        required = [rel for rel in required if rel not in CONSUMER_ONLY_PATHS]

    missing: list[str] = []
    needs_trae = profile == "dual_ide"
    plane_hits = {
        "cursor": True,
        "trae": True if needs_trae else True,
        "infrastructure": True,
        "runtime": True,
    }
    if not needs_trae:
        plane_hits["trae"] = True  # not required

    for rel in required:
        if not (project_root / rel).exists():
            missing.append(rel)
            plane = _plane_for_path(rel, profile=profile)
            plane_hits[plane] = False

    trae_ready = plane_hits["trae"] if needs_trae else True

    return PlaneStatus(
        cursor_contract=plane_hits["cursor"],
        trae_contract=trae_ready,
        infrastructure=plane_hits["infrastructure"],
        runtime=plane_hits["runtime"],
        missing=tuple(missing),
        requires_trae=needs_trae,
    )


def format_plane_report(status: PlaneStatus) -> str:
    def mark(ok: bool) -> str:
        return "ready" if ok else "missing"

    lines = [
        f"cursor_contract: {mark(status.cursor_contract)}",
        f"trae_contract: {mark(status.trae_contract)}",
        f"infrastructure: {mark(status.infrastructure)}",
        f"runtime: {mark(status.runtime)}",
    ]
    if status.missing:
        lines.append("missing_paths:")
        for path in status.missing[:12]:
            lines.append(f"  - {path}")
        if len(status.missing) > 12:
            lines.append(f"  - ... +{len(status.missing) - 12} more")
    return "\n".join(lines)
