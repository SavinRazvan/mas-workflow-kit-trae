"""
File: test_coverage_gap_scaffold.py
Path: tests/modules/install/test_coverage_gap_scaffold.py
Role: In-process coverage for remaining scaffold.py branches.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/install/scaffold.py
Notes:
 - Prefer unit calls over full install; monkeypatch subprocess for verify/venv.
"""

from __future__ import annotations

import importlib.util
import runpy
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCAFFOLD_PATH = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "scaffold.py"


def _load():
    name = f"scaffold_gap_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, SCAFFOLD_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_resolve_profile_extends_and_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load()
    manifest = {
        "profiles": {
            "base": {
                "copy_dirs": ["a"],
                "copy_ai_infra": ["x"],
                "copy_files": ["f"],
                "scaffold_local": True,
                "agents_md": "stub",
                "mcp_json": False,
            },
            "child": {
                "extends": "base",
                "copy_dirs": ["b"],
                "copy_dirs_replace": ["only"],
                "scaffold_local": False,
                "overlay_rules": "overlays/rules",
            },
        }
    }
    monkeypatch.setattr(mod, "_load_manifest", lambda: manifest)
    with pytest.raises(ValueError, match="unknown profile"):
        mod._resolve_profile(manifest, "missing")
    merged = mod._resolve_profile(manifest, "child")
    assert merged["copy_dirs"] == ["only"]
    assert merged["scaffold_local"] is False
    assert merged["overlay_rules"] == "overlays/rules"
    assert "x" in merged["copy_ai_infra"]


def test_load_manifest_invalid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load()
    bad = tmp_path / "manifest.yaml"
    bad.write_text("not: a profile map\n", encoding="utf-8")
    monkeypatch.setattr(mod, "MANIFEST_PATH", bad)
    with pytest.raises(RuntimeError, match="invalid manifest"):
        mod._load_manifest()


def test_copy_helpers_missing_and_dry_run(tmp_path: Path) -> None:
    mod = _load()
    log: list[str] = []
    with pytest.raises(FileNotFoundError):
        mod._copy_tree(tmp_path / "nope", tmp_path / "dst", False, log)
    with pytest.raises(FileNotFoundError):
        mod._copy_file(tmp_path / "nope.txt", tmp_path / "d.txt", False, log)
    with pytest.raises(FileNotFoundError):
        mod._copy_file_if_missing(tmp_path / "nope.txt", tmp_path / "d.txt", False, log)

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("x", encoding="utf-8")
    mod._copy_tree(src, tmp_path / "out", True, log)
    assert any("DRY-RUN copytree" in line for line in log)
    f = tmp_path / "file.txt"
    f.write_text("y", encoding="utf-8")
    mod._copy_file(f, tmp_path / "copied.txt", True, log)
    assert any("DRY-RUN copy" in line for line in log)


def test_artifact_stub_skip_missing_src(tmp_path: Path) -> None:
    mod = _load()
    ui = tmp_path / "ui"
    (ui / "artifact-stubs").mkdir(parents=True)
    log: list[str] = []
    mod._scaffold_artifact_readme_stubs(ui, tmp_path / "t", False, log, ("missing-bucket",))
    assert log == []


def test_user_settings_skip_when_templates_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load()
    monkeypatch.setattr(
        mod,
        "user_settings_templates",
        lambda _s: (_ for _ in ()).throw(FileNotFoundError("no templates")),
    )
    log: list[str] = []
    mod._scaffold_user_settings(REPO_ROOT, tmp_path, False, log)
    assert any("SKIP user_settings" in line for line in log)


def test_apply_overlay_missing_and_copy(tmp_path: Path) -> None:
    mod = _load()
    log: list[str] = []
    mod._apply_overlay_rules(tmp_path, tmp_path / "t", "overlays/nope", False, log)
    assert any("SKIP overlay" in line for line in log)

    overlay = tmp_path / ".ai_infra" / "overlays" / "rules"
    overlay.mkdir(parents=True)
    (overlay / "extra.mdc").write_text("rule\n", encoding="utf-8")
    dest_root = tmp_path / "target"
    (dest_root / ".trae" / "rules").mkdir(parents=True)
    log2: list[str] = []
    mod._apply_overlay_rules(tmp_path, dest_root, "overlays/rules", False, log2)
    assert (dest_root / ".trae" / "rules" / "extra.mdc").is_file()


def test_sanity_check_failure_branches(tmp_path: Path) -> None:
    mod = _load()
    target = tmp_path / "bare"
    target.mkdir()
    (target / "examples").mkdir()
    log: list[str] = []
    errors = mod._sanity_check(target, log, with_tests=False)
    assert any("implementer.md" in e for e in errors)
    assert any("session-pointer" in e for e in errors)
    assert any("examples" in e for e in errors)
    assert any("smoke test" in e for e in errors)


def test_run_verify_fail_and_create_venv_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load()
    target = tmp_path / "proj"
    target.mkdir()
    (target / ".ai_infra" / "scripts" / "pr").mkdir(parents=True)
    (target / ".ai_infra" / "scripts" / "architecture").mkdir(parents=True)

    monkeypatch.setattr(mod, "resolve_project_python", lambda _t: sys.executable)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=7),
    )
    log: list[str] = []
    assert mod._run_verify(target, log) == 7
    assert any("VERIFY FAIL" in line for line in log)

    venv = target / ".venv"
    venv.mkdir()
    log2: list[str] = []
    mod._create_venv(target, False, log2)
    assert any("SKIP venv" in line for line in log2)

    venv2 = tmp_path / "proj2"
    venv2.mkdir()
    log3: list[str] = []
    mod._create_venv(venv2, True, log3)
    assert any("DRY-RUN python -m venv" in line for line in log3)

    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    proj3 = tmp_path / "proj3"
    proj3.mkdir()
    (proj3 / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
    (proj3 / "requirements-mcp.txt").write_text("mcp\n", encoding="utf-8")
    # Pretend venv already has bin/pip after first call creates it
    created = {"once": False}

    def fake_run2(cmd, **kwargs):
        calls.append(list(cmd))
        if not created["once"] and "venv" in cmd:
            created["once"] = True
            (proj3 / ".venv" / "bin").mkdir(parents=True)
            (proj3 / ".venv" / "bin" / "pip").write_text("#!/bin/sh\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(mod.subprocess, "run", fake_run2)
    log4: list[str] = []
    mod._create_venv(proj3, False, log4)
    assert any(any("requirements-dev.txt" in str(c) for c in cmd) for cmd in calls)
    assert any("VENV created" in line for line in log4)


def test_scaffold_with_readme_overlay_mcp_fallback_and_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load()
    target = tmp_path / "out"
    # Patch profile to include overlay + mcp_json without real mcp_manage path
    base = mod._load_manifest()
    spec = dict(base["profiles"]["default"])
    spec["overlay_rules"] = "overlays/does-not-exist"
    spec["mcp_json"] = True
    monkeypatch.setattr(mod, "_resolve_profile", lambda m, n: spec)
    monkeypatch.setattr(
        mod,
        "_sanity_check",
        lambda *a, **k: ["forced fail"],
    )
    with pytest.raises(RuntimeError, match="sanity check failed"):
        mod.scaffold(target, REPO_ROOT, with_readme=True, with_mcp_json=True)

    # mcp fallback when mcp_manage missing on source
    source = tmp_path / "src"
    # Minimal source: reuse kit but hide mcp_manage via monkeypatch on Path.is_file for that path
    monkeypatch.setattr(mod, "_sanity_check", lambda *a, **k: [])
    monkeypatch.setattr(mod, "_resolve_profile", lambda m, n: {**spec, "mcp_json": True})

    real_is_file = Path.is_file

    def patched_is_file(self: Path) -> bool:
        if self.name == "mcp_manage.py" and "trae_workflow" in str(self):
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", patched_is_file)
    # Need a real scaffoldable target — use dry_run to avoid heavy copy, still hits overlay + mcp branches
    log = mod.scaffold(tmp_path / "dry", REPO_ROOT, dry_run=True, with_readme=True, with_mcp_json=True)
    assert any("DRY-RUN" in line for line in log)


def test_scaffold_verify_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load()
    monkeypatch.setattr(mod, "_sanity_check", lambda *a, **k: [])
    monkeypatch.setattr(mod, "_run_verify", lambda *a, **k: 9)
    # Use dry_run=False but stub heavy work via early return after flags — call scaffold
    # with monkeypatched copy helpers to no-op
    monkeypatch.setattr(mod, "_copy_tree", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_ai_infra_rel", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_file", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_copy_file_if_missing", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_scaffold_local", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_scaffold_user_settings", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_scaffold_minimal_tests", lambda *a, **k: None)
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
                }
            }
        },
    )
    with pytest.raises(RuntimeError, match="verify failed"):
        mod.scaffold(tmp_path / "v", REPO_ROOT, verify=True)


def test_main_error_and_dunder_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load()
    monkeypatch.setattr(
        sys,
        "argv",
        ["scaffold", "--target", str(tmp_path / "t"), "--source", str(tmp_path / "missing")],
    )
    # Will fail on missing source during scaffold
    code = mod.main()
    assert code == 1

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scaffold",
            "--target",
            str(tmp_path / "ok"),
            "--source",
            str(REPO_ROOT),
            "--dry-run",
        ],
    )
    assert mod.main() == 0

    with pytest.raises(SystemExit):
        runpy.run_path(str(SCAFFOLD_PATH), run_name="__main__")


def test_sys_path_arch_already_present() -> None:
    arch = str(REPO_ROOT / ".ai_infra" / "scripts" / "architecture")
    if arch not in sys.path:
        sys.path.insert(0, arch)
    # Re-executing scaffold module hits "already in path" branch for ARCH_SCRIPTS
    _load()
