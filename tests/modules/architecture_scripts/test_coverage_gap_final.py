"""
File: test_coverage_gap_final.py
Path: tests/modules/architecture_scripts/test_coverage_gap_final.py
Role: Final in-process hits for the last ~20 uncovered shipped-source lines.
Used By:
 - pytest
Depends On:
 - cli, scaffold, validate, sync_*, doc_facts_checks
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_cli_syspath_and_relative_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Line 72: relative path that exists under kit_root / cwd
    pkg = str(REPO_ROOT / ".ai_infra/install/trae_workflow")
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    import cli as install_cli

    rel = Path("tests")
    resolved = install_cli._resolve_install_source(rel)
    assert resolved.is_dir()

    # Lines 27/40: load when .ai_infra and mcp pkg are NOT yet on sys.path
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)
    while pkg in sys.path:
        sys.path.remove(pkg)
    name = f"cli_reload_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / ".ai_infra/install/trae_workflow/cli.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert ai in sys.path
    assert pkg in sys.path


def test_cli_kit_root_else_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real_is_file = Path.is_file

    def fake_is_file(self: Path) -> bool:
        if self.name == "bootstrap.py" and self.parent.name == ".ai_infra":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    name = f"cli_else_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / ".ai_infra/install/trae_workflow/cli.py"
    )
    assert spec is not None and spec.loader is not None
    with pytest.raises(RuntimeError, match="kit root not found"):
        spec.loader.exec_module(importlib.util.module_from_spec(spec))


def test_scaffold_mcp_fallback_and_bootstrap_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = f"scaffold_final_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / ".ai_infra/scripts/install/scaffold.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # mcp fallback 579-582: source without mcp_manage.py but target has example
    source = tmp_path / "src"
    target = tmp_path / "tgt"
    monkeypatch.setattr(
        mod,
        "_load_manifest",
        lambda: {
            "profiles": {
                "default": {
                    "copy_dirs": [],
                    "copy_ai_infra": [],
                    "copy_files": [],
                    "scaffold_local": False,
                    "mcp_json": True,
                }
            }
        },
    )
    monkeypatch.setattr(mod, "_copy_tree", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_ai_infra_rel", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_file_if_missing", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_scaffold_minimal_tests", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_sanity_check", lambda *a, **k: [])

    (source / ".ai_infra" / "install" / "trae_workflow").mkdir(parents=True)
    (source / ".ai_infra" / ".kit-version").write_text("0\n", encoding="utf-8")
    (target / ".trae").mkdir(parents=True)
    (target / ".trae" / "mcp.json.kit.example").write_text('{"mcpServers":{}}', encoding="utf-8")

    copies: list[str] = []

    def capture_copy(src, dst, dry_run, log):
        copies.append(str(dst))
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    monkeypatch.setattr(mod, "_copy_file", capture_copy)
    log = mod.scaffold(target, source, with_mcp_json=True)
    assert any("mcp.json" in c for c in copies) or any("mcp" in line.lower() for line in log)

    # bootstrap else on real scaffold.py path
    real_is_file = Path.is_file

    def fake_is_file(self: Path) -> bool:
        if self.name == "bootstrap.py" and self.parent.name == ".ai_infra":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    name2 = f"scaffold_else_{uuid.uuid4().hex}"
    spec2 = importlib.util.spec_from_file_location(
        name2, REPO_ROOT / ".ai_infra/scripts/install/scaffold.py"
    )
    assert spec2 is not None and spec2.loader is not None
    with pytest.raises(RuntimeError, match="kit root not found"):
        spec2.loader.exec_module(importlib.util.module_from_spec(spec2))


def test_scaffold_arch_syspath_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    while arch in sys.path:
        sys.path.remove(arch)
    # Fresh load hits scaffold.py line 47 insert
    _load(f"scaffold_arch_{uuid.uuid4().hex}", ".ai_infra/scripts/install/scaffold.py")
    assert arch in sys.path


def test_validate_syspath_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    ai = str((REPO_ROOT / ".ai_infra").resolve())
    while ai in sys.path:
        sys.path.remove(ai)
    integ = str(REPO_ROOT / ".ai_infra/scripts/integration")
    if integ not in sys.path:
        sys.path.insert(0, integ)
    name = f"validate_sys_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / ".ai_infra/scripts/integration/validate.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    assert ai in sys.path


def test_validate_int014_partial_and_syspath(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    integ = str(REPO_ROOT / ".ai_infra/scripts/integration")
    if integ not in sys.path:
        sys.path.insert(0, integ)
    import validate

    # Force sys.path insert branches by removing then calling helpers
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    while arch in sys.path:
        sys.path.remove(arch)

    # Re-import path insert at module level already done; call _import_check_doc_facts
    try:
        validate._import_check_doc_facts(REPO_ROOT)
    except Exception:
        pass

    root = tmp_path
    rules = root / ".trae" / "rules"
    rules.mkdir(parents=True)
    (rules / "file-docstring-header-relations.md").write_text(
        "---\nalwaysApply: false\n---\n", encoding="utf-8"
    )
    agents = root / ".trae" / "agents"
    agents.mkdir(parents=True)
    (agents / "implementer.md").write_text("# no header ref\n", encoding="utf-8")
    skill = root / ".trae" / "skills" / "implementation-execution-loop"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# no header ref\n", encoding="utf-8")
    r = validate._check_int014(root)
    assert not r.passed
    assert "alwaysApply" in r.detail
    assert "implementer.md" in r.detail
    assert "SKILL.md" in r.detail or "file-docstring-header" in r.detail


def test_sync_plugin_rmtree_and_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load(f"spb_{uuid.uuid4().hex}", ".ai_infra/scripts/release/sync_plugin_bundle.py")
    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "old.txt").write_text("x", encoding="utf-8")

    monkeypatch.setattr(mod, "_load_manifest", lambda: {"profiles": {"default": {}}})
    monkeypatch.setattr(mod, "_resolve_profile", lambda m, n: {"copy_ai_infra": [], "copy_files": []})
    monkeypatch.setattr(mod, "_copy_tree", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_ai_infra_rel", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_file", lambda *a, **k: None)
    monkeypatch.setattr(mod, "TRAE_WORKFLOW_SRC", tmp_path / "missing-tw")
    (tmp_path / "missing-tw").mkdir()
    (tmp_path / "LICENSE").write_text("L\n", encoding="utf-8")
    (tmp_path / "NOTICE").write_text("N\n", encoding="utf-8")
    monkeypatch.setattr(mod, "KIT_ROOT", tmp_path)
    monkeypatch.setattr(mod, "LICENSE_FILES", ("LICENSE", "NOTICE"))
    mod.sync_payload(payload, tmp_path, "default")
    assert not (payload / "old.txt").exists()

    real_is_file = Path.is_file

    def fake_is_file(self: Path) -> bool:
        if self.name == "bootstrap.py" and self.parent.name == ".ai_infra":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    name = f"spb_else_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name, REPO_ROOT / ".ai_infra/scripts/release/sync_plugin_bundle.py"
    )
    assert spec is not None and spec.loader is not None
    with pytest.raises(RuntimeError, match="kit root not found"):
        spec.loader.exec_module(importlib.util.module_from_spec(spec))


def test_sync_trae_syspath_and_maintainer_skip(tmp_path: Path) -> None:
    # Force sys.path insert (line 23)
    ai = str(REPO_ROOT / ".ai_infra")
    while ai in sys.path:
        sys.path.remove(ai)
    sync = _load(f"stc_{uuid.uuid4().hex}", ".ai_infra/scripts/release/sync_trae_contract.py")
    assert ai in sys.path

    kit = tmp_path / "kit"
    cursor = kit / ".cursor"
    (cursor / "skills" / "already").mkdir(parents=True)
    (cursor / "skills" / "already" / "SKILL.md").write_text("from-cursor\n", encoding="utf-8")
    (cursor / "rules").mkdir()
    (cursor / "agents").mkdir()
    maint = kit / ".agents" / "skills"
    maint.mkdir(parents=True)
    (maint / "file-not-dir.txt").write_text("x\n", encoding="utf-8")  # continue at 153
    # maintainer skill with same name as cursor skill → skip copy (target.exists)
    (maint / "already").mkdir()
    (maint / "already" / "SKILL.md").write_text("from-maintainer\n", encoding="utf-8")
    dest = kit / ".trae"
    sync.sync_trae_contract_from_cursor(kit, dest)
    assert (dest / "skills" / "already" / "SKILL.md").read_text(encoding="utf-8") == "from-cursor\n"


def test_doc_facts_parse_none_and_no_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    import doc_facts_checks as dfc

    assert dfc._parse_handoff_test_count("nothing numeric matching patterns") is None

    (tmp_path / ".ai_infra" / "docs" / "handoff").mkdir(parents=True)
    (tmp_path / ".ai_infra" / "docs" / "handoff" / "IMPLEMENTATION-STATUS.md").write_text(
        "x\n", encoding="utf-8"
    )
    (tmp_path / ".ai_infra" / "docs" / "handoff" / "repository-map.md").write_text(
        "no count\n", encoding="utf-8"
    )
    (tmp_path / ".ai_infra" / "docs" / "handoff" / "PLUGIN-ARCHITECTURE.md").write_text(
        "no count\n", encoding="utf-8"
    )
    # Make collect succeed with a dummy count
    monkeypatch.setattr(dfc, "_collect_pytest_count", lambda _r: 99)
    paths = dfc.DocFactsPaths(
        root=tmp_path,
        agents_dir=tmp_path / "a",
        rules_dir=tmp_path / "r",
        exemplars_dir=tmp_path / "e",
        prepare_py=tmp_path / "p",
        readme=tmp_path / "R",
        agents_md=tmp_path / "A",
        workflow_architecture=tmp_path / "w",
        implementation_status=tmp_path
        / ".ai_infra"
        / "docs"
        / "handoff"
        / "IMPLEMENTATION-STATUS.md",
        gate_matrix=tmp_path / "g",
    )
    r = dfc.check_doc008_handoff_test_parity(paths)
    assert not r.passed
    assert "no test count found" in r.detail


def test_scaffold_real_file_else_and_arch_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hit scaffold.py:38 (else) and :47 (ARCH_SCRIPTS insert) on the real file path."""
    arch = str(REPO_ROOT / ".ai_infra/scripts/architecture")
    while arch in sys.path:
        sys.path.remove(arch)

    _load(f"scaffold_arch_{uuid.uuid4().hex}", ".ai_infra/scripts/install/scaffold.py")
    assert arch in sys.path

    real_is_file = Path.is_file

    def fake_is_file(self: Path) -> bool:
        if self.name == "bootstrap.py":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    with pytest.raises(RuntimeError, match="kit root not found"):
        _load(f"scaffold_else_{uuid.uuid4().hex}", ".ai_infra/scripts/install/scaffold.py")


def test_validate_real_file_ai_infra_insert() -> None:
    """Hit validate.py:42 sys.path.insert on the real module file."""
    integ = str(REPO_ROOT / ".ai_infra/scripts/integration")
    if integ not in sys.path:
        sys.path.insert(0, integ)
    pkg = str(REPO_ROOT / ".ai_infra")
    while pkg in sys.path:
        sys.path.remove(pkg)
    for key in list(sys.modules):
        if key in ("validate", "checks") or key.startswith("validate."):
            del sys.modules[key]
    _load(f"validate_ins_{uuid.uuid4().hex}", ".ai_infra/scripts/integration/validate.py")
    assert pkg in sys.path


def test_cli_and_sync_real_file_else(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hit cli.py:33 and sync_plugin_bundle.py:38 on the real files."""
    real_is_file = Path.is_file

    def fake_is_file(self: Path) -> bool:
        if self.name == "bootstrap.py":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    with pytest.raises(RuntimeError, match="kit root not found"):
        _load(f"cli_else_{uuid.uuid4().hex}", ".ai_infra/install/trae_workflow/cli.py")
    with pytest.raises(RuntimeError, match="kit root not found"):
        _load(f"spb_else_{uuid.uuid4().hex}", ".ai_infra/scripts/release/sync_plugin_bundle.py")
