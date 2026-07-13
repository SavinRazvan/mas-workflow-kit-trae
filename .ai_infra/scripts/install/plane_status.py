"""
File: plane_status.py
Path: .ai_infra/scripts/install/plane_status.py
Role: Assess workflow plane readiness (Trae contract, infrastructure, runtime).
Used By:
 - .ai_infra/install/trae_workflow/activate_cli.py
 - workflow_mcp workflow_activate
Depends On:
 - .ai_infra/install-contract.json
 - .ai_infra/ide_contract_paths.py
Notes:
 - Trae edition: `.trae/` contract plane required; no Cursor contract plane (ADR-009).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_AI_INFRA = Path(__file__).resolve().parents[2]
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))

from ide_contract_paths import TRAE, plane_prefix  # noqa: E402


@dataclass(frozen=True)
class PlaneStatus:
    trae_contract: bool
    infrastructure: bool
    runtime: bool
    missing: tuple[str, ...]
    requires_trae: bool = True

    @property
    def all_ready(self) -> bool:
        base = self.trae_contract and self.infrastructure and self.runtime
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


def _plane_for_path(rel: str, *, profile: str = "default") -> str:
    if rel.startswith(".local/"):
        return "runtime"
    if rel.startswith(".ai_infra/") or rel.startswith("trae_workflow/"):
        return "infrastructure"
    if rel.startswith(f"{plane_prefix(TRAE)}/"):
        return "trae"
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

_TRAE_FALLBACK_REQUIRED = [
    ".trae/agents/implementer.md",
    ".trae/rules/pr-workflow-enforcement.md",
    ".trae/mcp.json",
    ".ai_infra/scripts/pr/prepare.py",
    ".local/index-and-planning/current/session-pointer.md",
    "AGENTS.md",
    "trae_workflow/__main__.py",
]


def assess_planes(root: Path, *, profile: str = "default") -> PlaneStatus:
    project_root = root.resolve()
    contract = _load_contract(project_root)
    if not contract:
        required = list(_TRAE_FALLBACK_REQUIRED)
    else:
        spec = _resolve_profile(contract, profile)
        rp = spec.get("required_paths")
        required = list(rp) if rp else list(_TRAE_FALLBACK_REQUIRED)
    if is_kit_dev_repo(project_root):
        required = [rel for rel in required if rel not in CONSUMER_ONLY_PATHS]

    missing: list[str] = []
    plane_hits = {
        "trae": True,
        "infrastructure": True,
        "runtime": True,
    }

    for rel in required:
        if not (project_root / rel).exists():
            missing.append(rel)
            plane = _plane_for_path(rel, profile=profile)
            plane_hits[plane] = False

    return PlaneStatus(
        trae_contract=plane_hits["trae"],
        infrastructure=plane_hits["infrastructure"],
        runtime=plane_hits["runtime"],
        missing=tuple(missing),
        requires_trae=True,
    )


def format_plane_report(status: PlaneStatus) -> str:
    def mark(ok: bool) -> str:
        return "ready" if ok else "missing"

    lines = [
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
