"""
File: test_coverage_gap_deep.py
Path: tests/modules/architecture_scripts/test_coverage_gap_deep.py
Role: Deep branch coverage for checks, verify_all, mcp_manage, sync helpers.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/integration/checks.py
 - .ai_infra/scripts/architecture/verify_all.py
 - .ai_infra/install/trae_workflow/mcp_manage.py
 - .ai_infra/scripts/release/sync_plugin_bundle.py
Notes:
 - Monkeypatch heavy subprocess paths; keep in-process for cov attribution.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
_AI_INFRA = REPO_ROOT / ".ai_infra"
_PKG = _AI_INFRA / "install" / "trae_workflow"


def _load(name: str, rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_checks_edge_branches(tmp_path: Path) -> None:
    integ = str(REPO_ROOT / ".ai_infra/scripts/integration")
    if integ not in sys.path:
        sys.path.insert(0, integ)
    import checks

    assert checks.agent_file_ids(tmp_path / "missing") == set()
    assert checks.registry_agent_ids(tmp_path / "no.yaml") == set()
    bad = tmp_path / "reg.yaml"
    bad.write_text("- not a dict\n", encoding="utf-8")
    assert checks.registry_agent_ids(bad) == set()
    ok = tmp_path / "reg2.yaml"
    ok.write_text(
        "servers:\n  s:\n    agents: [a, '', 1]\n  t: notdict\n",
        encoding="utf-8",
    )
    assert checks.registry_agent_ids(ok) == {"a"}

    assert checks.check_all_agent_files(tmp_path / "agents") == [
        f"no agent files in {tmp_path / 'agents'}"
    ]

    assert checks.pipeline_names_from_exemplar(tmp_path / "x.yaml") == set()
    (tmp_path / "x.yaml").write_text("- list\n", encoding="utf-8")
    assert checks.pipeline_names_from_exemplar(tmp_path / "x.yaml") == set()
    (tmp_path / "y.yaml").write_text(
        "pr_collaboration:\n  pipelines: notdict\n",
        encoding="utf-8",
    )
    assert checks.pipeline_names_from_exemplar(tmp_path / "y.yaml") == set()

    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "impl.md").write_text("ok", encoding="utf-8")
    viol = checks.check_pipeline_agent_ids(
        cfg={"pr_collaboration": {"pipelines": "bad"}},
        agents_dir=agents,
    )
    assert viol == []
    viol = checks.check_pipeline_agent_ids(
        cfg={
            "pr_collaboration": {
                "pipelines": {
                    "default": "bad",
                    "p2": {"agents": [1, " missing ", "impl", "ghost"]},
                }
            }
        },
        agents_dir=agents,
    )
    assert any("ghost" in v for v in viol)


def test_verify_all_builds_typecheck_and_trae_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    import verify_all

    monkeypatch.setattr(
        verify_all,
        "_run_step",
        lambda name, cmd, root: verify_all.StepResult(name, cmd, 0, "", 0.0),
    )
    results = verify_all.run_verify_all(REPO_ROOT, sys.executable)
    names = [r.name for r in results]
    assert "type-check" in names
    assert "check-trae-parity" in names


def test_contract_json_skip_missing_src(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mod = _load("check_contract_json_sync2", ".ai_infra/scripts/architecture/check_contract_json_sync.py")
    monkeypatch.setattr(mod, "CONTRACT_FILES", (".trae/missing.json", ".trae/mcp.json"))
    (tmp_path / ".trae").mkdir()
    (tmp_path / ".trae" / "mcp.json").write_text("{}", encoding="utf-8")
    payload = tmp_path / "payload" / ".trae"
    payload.mkdir(parents=True)
    (payload / "mcp.json").write_text("{}", encoding="utf-8")
    # missing.json skipped via continue; mcp.json matches
    assert mod.check_contract_json_sync(tmp_path) == []


def test_mcp_manage_default_ide_and_seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if str(_PKG) not in sys.path:
        sys.path.insert(0, str(_PKG))
    # Force sys.path insert branch
    ai = str(_AI_INFRA)
    while ai in sys.path:
        sys.path.remove(ai)
    import importlib
    import mcp_manage

    importlib.reload(mcp_manage)
    assert ai in sys.path

    # Non-SSOT path: no .trae rules → may still be Trae if kit layout; force dual
    monkeypatch.setattr(mcp_manage, "uses_trae_ssot", lambda root: False)
    assert mcp_manage._default_ide(tmp_path) == mcp_manage.CURSOR
    (tmp_path / ".trae").mkdir()
    (tmp_path / ".trae" / "mcp.json.kit.example").write_text("{}", encoding="utf-8")
    assert mcp_manage._default_ide(tmp_path) == mcp_manage.TRAE

    assert mcp_manage._kit_fragment("trae").parts[-1] == "mcp.json.kit.example"
    assert mcp_manage._user_fragment("trae").parts[-1] == "mcp.user.json"
    assert mcp_manage._mcp_dest("trae").parts[-1] == "mcp.json"
    assert mcp_manage._registry_path("trae").parts[-1] == "mcp.registry.yaml"

    # seed early return
    mcp_manage.seed_trae_mcp_from_cursor(tmp_path)  # no .cursor
    cursor = tmp_path / ".cursor"
    cursor.mkdir()
    (cursor / "mcp.json.kit.example").write_text("kit", encoding="utf-8")
    (cursor / "mcp.registry.yaml").write_text("r: 1\n", encoding="utf-8")
    mcp_manage.seed_trae_mcp_from_cursor(tmp_path)
    assert (tmp_path / ".trae" / "mcp.json.kit.example").is_file()
    assert (tmp_path / ".trae" / "mcp.registry.yaml").is_file()


def test_sync_plugin_bundle_error_and_extend_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load("sync_plugin_bundle_deep", ".ai_infra/scripts/release/sync_plugin_bundle.py")
    real_manifest = REPO_ROOT / ".ai_infra" / "manifest.yaml"

    (tmp_path / "bad.yaml").write_text("not: ok\n", encoding="utf-8")
    monkeypatch.setattr(mod, "MANIFEST_PATH", tmp_path / "bad.yaml")
    with pytest.raises(RuntimeError):
        mod._load_manifest()
    monkeypatch.setattr(mod, "MANIFEST_PATH", real_manifest)

    man = {"profiles": {}}
    with pytest.raises(ValueError, match="unknown profile"):
        mod._resolve_profile(man, "nope")

    man = {
        "profiles": {
            "base": {"copy_dirs": ["a"], "copy_ai_infra": ["x"], "copy_files": ["f"]},
            "child": {
                "extends": "base",
                "copy_dirs": ["b"],
                "copy_ai_infra": ["y"],
                "copy_files": ["g"],
                "copy_dirs_replace": ["only"],
            },
        }
    }
    merged = mod._resolve_profile(man, "child")
    assert merged["copy_dirs"] == ["only"]
    assert "x" in merged["copy_ai_infra"] and "y" in merged["copy_ai_infra"]

    with pytest.raises(FileNotFoundError):
        mod._copy_tree(tmp_path / "missing", tmp_path / "dst")
    with pytest.raises(FileNotFoundError):
        mod._copy_file(tmp_path / "nofile", tmp_path / "out")

    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    while arch in sys.path:
        sys.path.remove(arch)
    mod._load_consumer_bundle_paths()
    assert arch in sys.path

    monkeypatch.setattr(mod, "PAYLOAD_DIR", tmp_path / "payload")
    monkeypatch.setattr(mod, "MANIFEST_PATH", real_manifest)
    mod.sync_all("default")
    assert (tmp_path / "payload" / ".trae").is_dir()
