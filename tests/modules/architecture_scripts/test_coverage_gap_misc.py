"""
File: test_coverage_gap_misc.py
Path: tests/modules/architecture_scripts/test_coverage_gap_misc.py
Role: Close remaining coverage gaps in architecture/release/ai_infra helpers.
Used By:
 - pytest
Depends On:
 - .ai_infra/ide_contract_paths.py
 - .ai_infra/scripts/architecture/check_contract_json_sync.py
 - .ai_infra/scripts/architecture/verify_all.py
 - .ai_infra/scripts/release/sync_plugin_bundle.py
 - .ai_infra/scripts/pr/user_settings.py
 - .ai_infra/scripts/install/plane_status.py
Notes:
 - In-process only so pytest-cov attributes hits to shipped source.
"""

from __future__ import annotations

import importlib.util
import json
import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_AI_INFRA = REPO_ROOT / ".ai_infra"
if str(_AI_INFRA) not in sys.path:
    sys.path.insert(0, str(_AI_INFRA))


def _load(name: str, rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_uses_trae_ssot_profiles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from ide_contract_paths import (
        DUAL_IDE_PROFILE,
        TRAE_ONLY_PROFILE,
        uses_trae_ssot,
    )

    assert uses_trae_ssot(tmp_path, TRAE_ONLY_PROFILE) is True
    assert uses_trae_ssot(tmp_path, DUAL_IDE_PROFILE) is False
    monkeypatch.setenv("TRAE_ONLY", "true")
    assert uses_trae_ssot(tmp_path, "") is True
    monkeypatch.delenv("TRAE_ONLY", raising=False)


def test_contract_json_sync_main_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    mod = _load("check_contract_json_sync", ".ai_infra/scripts/architecture/check_contract_json_sync.py")
    assert mod.main(["--directory", str(tmp_path)]) == 0
    assert "skipped" in capsys.readouterr().out

    (tmp_path / ".trae").mkdir()
    (tmp_path / ".trae" / "mcp.json").write_text("{}", encoding="utf-8")
    assert mod.main(["--directory", str(tmp_path)]) == 1
    assert "FAIL" in capsys.readouterr().out

    payload = tmp_path / "payload" / ".trae"
    payload.mkdir(parents=True)
    (payload / "mcp.json").write_text("{}", encoding="utf-8")
    assert mod.main(["--directory", str(tmp_path)]) == 0
    assert "PASS" in capsys.readouterr().out

    (payload / "mcp.json").write_text('{"x":1}', encoding="utf-8")
    assert mod.check_contract_json_sync(tmp_path)
    assert mod.main(["--directory", str(tmp_path)]) == 1


def test_contract_json_sync_dunder_main(monkeypatch: pytest.MonkeyPatch) -> None:
    path = REPO_ROOT / ".ai_infra/scripts/architecture/check_contract_json_sync.py"
    monkeypatch.setattr(sys, "argv", [str(path), "--directory", str(REPO_ROOT)])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


def test_verify_all_without_pyright_and_without_trae(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    import verify_all

    # No .venv/pyright, no .trae → skip those steps
    root = tmp_path
    (root / ".ai_infra/scripts/architecture").mkdir(parents=True)
    (root / ".ai_infra/scripts/release").mkdir(parents=True)
    steps = verify_all.run_verify_all(root, sys.executable)
    names = [s.name for s in steps]
    assert "type-check" not in names
    assert "check-trae-parity" not in names


def test_user_settings_assisted_by_and_coauthors(tmp_path: Path) -> None:
    pr = str(REPO_ROOT / ".ai_infra/scripts/pr")
    if pr not in sys.path:
        sys.path.insert(0, pr)
    import user_settings

    cfg = {
        "owner": {"display_name": "A", "github_user": "@a"},
        "commit_provenance": {
            "ai_disclosure_mode": "none",
            "assisted_by": ["x"],
            "human_coauthors": ["y"],
            "co_author_trailer": True,
        },
        "pr_collaboration": {"pipelines": {"default": {"agents": ["review-pr"]}}},
    }
    path = tmp_path / ".local/user_settings"
    path.mkdir(parents=True)
    (path / "github.collaboration.yaml").write_text(
        "version: 1\n"
        "owner:\n  display_name: A\n  github_user: '@a'\n"
        "commit_provenance:\n"
        "  ai_disclosure_mode: none\n"
        "  assisted_by: [x]\n"
        "  human_coauthors: [y]\n"
        "  co_author_trailer: true\n"
        "pr_collaboration:\n"
        "  pipelines:\n"
        "    default:\n"
        "      agents: [review-pr]\n",
        encoding="utf-8",
    )
    errors = user_settings.validate_github_collaboration(tmp_path)
    joined = "\n".join(errors)
    assert "assisted_by" in joined
    assert "human_coauthors" in joined
    assert "co_author_trailer" in joined


def test_plane_status_extends_and_missing_contract(tmp_path: Path) -> None:
    mod = _load("plane_status", ".ai_infra/scripts/install/plane_status.py")
    assert mod._load_contract(tmp_path) == {}
    assert mod._resolve_profile({}, "default") == {"required_paths": []}

    contract = {
        "profiles": {
            "base": {"required_paths": ["a"], "forbidden_paths": ["f"]},
            "child": {"extends": "base", "required_paths": ["b"], "forbidden_paths": ["g"]},
        }
    }
    merged = mod._resolve_profile(contract, "child")
    assert "a" in merged["required_paths"] and "b" in merged["required_paths"]
    assert "f" in merged["forbidden_paths"] and "g" in merged["forbidden_paths"]


def test_sync_plugin_bundle_main_check_and_sync(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load("sync_plugin_bundle", ".ai_infra/scripts/release/sync_plugin_bundle.py")
    monkeypatch.setattr(mod, "check_payload_git_clean", lambda: ["dirty"])
    # Use argparse via main with monkeypatched argv
    monkeypatch.setattr(sys, "argv", ["sync_plugin_bundle.py", "--check-git"])
    assert mod.main() == 1
    assert "failed" in capsys.readouterr().out.lower()

    monkeypatch.setattr(mod, "check_payload_git_clean", lambda: [])
    monkeypatch.setattr(sys, "argv", ["sync_plugin_bundle.py", "--check-git"])
    assert mod.main() == 0
    assert "passed" in capsys.readouterr().out.lower()

    monkeypatch.setattr(mod, "check_bundle", lambda profile: ["drift"])
    monkeypatch.setattr(sys, "argv", ["sync_plugin_bundle.py", "--check"])
    assert mod.main() == 1

    monkeypatch.setattr(mod, "check_bundle", lambda profile: [])
    monkeypatch.setattr(sys, "argv", ["sync_plugin_bundle.py", "--check"])
    assert mod.main() == 0

    called: list[str] = []
    monkeypatch.setattr(mod, "sync_all", lambda profile: called.append(profile))
    monkeypatch.setattr(sys, "argv", ["sync_plugin_bundle.py"])
    assert mod.main() == 0
    assert called == ["default"]
    assert "Synced" in capsys.readouterr().out


def test_sync_plugin_bundle_dunder_main(monkeypatch: pytest.MonkeyPatch) -> None:
    path = REPO_ROOT / ".ai_infra/scripts/release/sync_plugin_bundle.py"
    monkeypatch.setattr(sys, "argv", [str(path), "--check-git"])
    # May pass or fail depending on dirty tree; just exercise __main__
    with pytest.raises(SystemExit):
        runpy.run_path(str(path), run_name="__main__")


def test_resources_sys_path_and_flat_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mcp = str(REPO_ROOT / ".ai_infra/mcp_servers")
    if mcp not in sys.path:
        sys.path.insert(0, mcp)
    # Force resources.py insert branch by removing .ai_infra from path temporarily
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)

    import importlib
    import workflow_mcp.resources as resources

    importlib.reload(resources)
    assert ai in sys.path

    skills = tmp_path / ".trae" / "skills"
    skills.mkdir(parents=True)
    (skills / "flat-skill.md").write_text("# skill\n", encoding="utf-8")
    ids = resources._list_skill_ids(tmp_path)
    assert "flat-skill" in ids


def test_contract_json_sync_src_missing_continue(tmp_path: Path) -> None:
    mod = _load("check_contract_json_sync2", ".ai_infra/scripts/architecture/check_contract_json_sync.py")
    (tmp_path / ".trae").mkdir()
    # no mcp.json → continue at line 37
    assert mod.check_contract_json_sync(tmp_path) == []


def test_verify_all_includes_pyright_and_trae(monkeypatch: pytest.MonkeyPatch) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    import verify_all

    monkeypatch.setattr(
        verify_all,
        "_run_step",
        lambda name, cmd, root: verify_all.StepResult(name, cmd, 0, "", 0.01),
    )
    steps = verify_all.run_verify_all(REPO_ROOT, sys.executable)
    names = [s.name for s in steps]
    assert "type-check" in names  # kit has .venv/bin/pyright
    assert "check-trae-parity" in names


def test_plane_status_sys_path_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)
    # Fresh load triggers insert at line 24
    mod = _load("plane_status_syspath", ".ai_infra/scripts/install/plane_status.py")
    assert ai in sys.path
    assert mod is not None


def test_drift_checks_sys_path_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)
    workflow = str(REPO_ROOT / ".ai_infra/scripts/workflow")
    if workflow not in sys.path:
        sys.path.insert(0, workflow)
    path = REPO_ROOT / ".ai_infra/scripts/workflow/drift_checks.py"
    spec = importlib.util.spec_from_file_location("drift_checks_syspath", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["drift_checks_syspath"] = mod
    spec.loader.exec_module(mod)
    assert ai in sys.path


def test_doc_facts_mdc_count_and_consumer_skips(tmp_path: Path) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    import doc_facts_checks as dfc

    rules = tmp_path / ".cursor" / "rules"
    rules.mkdir(parents=True)
    (rules / "a.mdc").write_text("x\n", encoding="utf-8")
    paths = dfc.DocFactsPaths(
        root=tmp_path,
        agents_dir=tmp_path / ".trae" / "agents",
        rules_dir=rules,
        exemplars_dir=tmp_path / "ex",
        prepare_py=tmp_path / "prepare.py",
        readme=tmp_path / "README.md",
        agents_md=tmp_path / "AGENTS.md",
        workflow_architecture=tmp_path / "arch.md",
        implementation_status=tmp_path / "status.md",
        gate_matrix=tmp_path / "gate-matrix.md",
    )
    assert dfc.list_rule_count(paths) == 1

    r7 = dfc.check_doc007_trae_workflow_type_gate(paths)
    assert r7.passed and "consumer" in r7.detail.lower()
    r8 = dfc.check_doc008_handoff_test_parity(paths)
    assert r8.passed and "consumer" in r8.detail.lower()
    r9 = dfc.check_doc009_overlays_trae_paths(paths)
    assert r9.passed and "consumer" in r9.detail.lower()

    # kit-dev DOC-007 failure detail parts + DOC-008 missing counts
    (tmp_path / ".ai_infra" / "docs" / "handoff").mkdir(parents=True)
    (tmp_path / ".ai_infra" / "docs" / "handoff" / "IMPLEMENTATION-STATUS.md").write_text(
        "Tests: 1\n", encoding="utf-8"
    )
    bad_matrix = tmp_path / "gate-matrix.md"
    bad_matrix.write_text("no type checker here\n", encoding="utf-8")
    cli = tmp_path / ".ai_infra" / "install" / "trae_workflow" / "cli.py"
    cli.parent.mkdir(parents=True)
    cli.write_text("# no pyright\n", encoding="utf-8")
    kitish = dfc.DocFactsPaths(
        root=tmp_path,
        agents_dir=tmp_path / ".trae" / "agents",
        rules_dir=rules,
        exemplars_dir=tmp_path / "ex",
        prepare_py=tmp_path / "prepare.py",
        readme=tmp_path / "README.md",
        agents_md=tmp_path / "AGENTS.md",
        workflow_architecture=tmp_path / "arch.md",
        implementation_status=tmp_path
        / ".ai_infra"
        / "docs"
        / "handoff"
        / "IMPLEMENTATION-STATUS.md",
        gate_matrix=bad_matrix,
    )
    r7b = dfc.check_doc007_trae_workflow_type_gate(kitish)
    assert not r7b.passed
    assert "pyright" in r7b.detail

    handoff = tmp_path / ".ai_infra" / "docs" / "handoff"
    (handoff / "repository-map.md").write_text("no numbers here\n", encoding="utf-8")
    (handoff / "PLUGIN-ARCHITECTURE.md").write_text("still none\n", encoding="utf-8")
    r8b = dfc.check_doc008_handoff_test_parity(kitish)
    assert r8b.check_id == "DOC-008"


def test_mcp_manage_cursor_defaults_and_seed_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pkg = str(REPO_ROOT / ".ai_infra/install/trae_workflow")
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    import mcp_manage

    monkeypatch.setattr(mcp_manage, "uses_trae_ssot", lambda root: False)
    assert mcp_manage._default_ide(tmp_path) == mcp_manage.CURSOR
    (tmp_path / ".trae").mkdir()
    (tmp_path / ".trae" / "mcp.json.kit.example").write_text("{}", encoding="utf-8")
    assert mcp_manage._default_ide(tmp_path) == mcp_manage.TRAE

    assert mcp_manage._kit_fragment("trae").as_posix().endswith("mcp.json.kit.example")
    assert mcp_manage._user_fragment("trae").as_posix().endswith("mcp.user.json")
    assert mcp_manage._mcp_dest("trae").as_posix().endswith("mcp.json")
    assert mcp_manage._registry_path("trae").as_posix().endswith("mcp.registry.yaml")

    # seed early-return when planes incomplete
    mcp_manage.seed_trae_mcp_from_cursor(tmp_path / "empty")
    # seed copy of live mcp.registry.yaml / mcp.user.json
    cursor = tmp_path / "both" / ".cursor"
    trae = tmp_path / "both" / ".trae"
    cursor.mkdir(parents=True)
    trae.mkdir(parents=True)
    (cursor / "mcp.registry.yaml").write_text("servers: {}\n", encoding="utf-8")
    (cursor / "mcp.user.json").write_text("{}", encoding="utf-8")
    mcp_manage.seed_trae_mcp_from_cursor(tmp_path / "both")
    assert (trae / "mcp.registry.yaml").is_file()
    assert (trae / "mcp.user.json").is_file()
