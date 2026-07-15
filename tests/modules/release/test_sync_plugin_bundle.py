"""
File: test_sync_plugin_bundle.py
Path: tests/modules/release/test_sync_plugin_bundle.py
Role: Tests for Trae edition payload sync and parity check.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/release/sync_plugin_bundle.py
Notes:
 - Uses temporary output dirs; verifies payload/.trae + payload/trae_workflow only.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNC_PATH = REPO_ROOT / ".ai_infra" / "scripts" / "release" / "sync_plugin_bundle.py"


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_plugin_bundle", SYNC_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_plugin_bundle"] = module
    spec.loader.exec_module(module)
    return module


def test_sync_builds_trae_payload(tmp_path: Path) -> None:
    mod = _load_sync()
    payload_dir = tmp_path / "payload"
    mod.sync_payload(payload_dir, REPO_ROOT, profile="default")

    assert (payload_dir / ".ai_infra" / "scripts" / "pr" / "prepare.py").is_file()
    assert (payload_dir / "trae_workflow" / "__main__.py").is_file()
    assert (payload_dir / ".trae" / "agents" / "implementer.md").is_file()
    assert (payload_dir / "LICENSE").is_file()
    assert (payload_dir / "NOTICE").is_file()


def test_check_bundle_passes_after_sync(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_sync()
    payload_dir = tmp_path / "payload"
    mod.sync_payload(payload_dir, REPO_ROOT, profile="default")

    monkeypatch.setattr(mod, "PAYLOAD_DIR", payload_dir)

    errors = mod.check_bundle("default")
    assert errors == []


def test_payload_install_verify_green(tmp_path: Path) -> None:
    mod = _load_sync()
    payload_dir = tmp_path / "payload"
    target = tmp_path / "consumer"
    mod.sync_payload(payload_dir, REPO_ROOT, profile="default")

    scaffold_path = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "scaffold.py"
    spec = importlib.util.spec_from_file_location("scaffold", scaffold_path)
    assert spec is not None and spec.loader is not None
    scaffold = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scaffold)

    log = scaffold.scaffold(
        target,
        payload_dir,
        profile="default",
        with_venv=True,
        with_mcp_json=True,
        verify=True,
    )
    assert "VERIFY PASS: all gates green" in "\n".join(log)


def test_payload_install_dry_run(tmp_path: Path) -> None:
    mod = _load_sync()
    payload_dir = tmp_path / "payload"
    target = tmp_path / "consumer"
    mod.sync_payload(payload_dir, REPO_ROOT, profile="default")

    scaffold_path = REPO_ROOT / ".ai_infra" / "scripts" / "install" / "scaffold.py"
    spec = importlib.util.spec_from_file_location("scaffold", scaffold_path)
    assert spec is not None and spec.loader is not None
    scaffold = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scaffold)

    log = scaffold.scaffold(
        target,
        payload_dir,
        profile="default",
        dry_run=True,
        with_mcp_json=True,
    )
    joined = "\n".join(log)
    assert ".ai_infra" in joined
    assert ".trae" in joined
    assert "SCAFFOLD DONE" in joined


def test_sync_payload_default_includes_trae(tmp_path: Path) -> None:
    mod = _load_sync()
    payload_dir = tmp_path / "payload"
    mod.sync_payload(payload_dir, REPO_ROOT, profile="default")

    assert (payload_dir / ".trae" / "rules" / "pr-workflow-enforcement.md").is_file()
    assert (payload_dir / ".trae" / "skills" / "workflow-activate" / "SKILL.md").is_file()
    assert (payload_dir / ".trae" / "mcp.json").is_file()
    assert (payload_dir / ".trae" / "agents" / "implementer.md").is_file()


def test_check_payload_git_clean_passes_when_clean(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mod = _load_sync()
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: __import__("types").SimpleNamespace(stdout="", returncode=0),
    )
    assert mod.check_payload_git_clean(tmp_path) == []


def test_check_payload_git_clean_fails_when_dirty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mod = _load_sync()
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: __import__("types").SimpleNamespace(
            stdout=" M payload/.ai_infra/scripts/integration/validate.py\n",
            returncode=0,
        ),
    )
    errors = mod.check_payload_git_clean(tmp_path)
    assert len(errors) == 1
    assert "payload/" in errors[0]


def test_check_payload_git_clean_skips_without_git(tmp_path: Path) -> None:
    mod = _load_sync()
    assert mod.check_payload_git_clean(tmp_path) == []
