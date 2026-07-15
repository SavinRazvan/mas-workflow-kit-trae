"""
File: test_cli_dispatchers.py
Path: tests/modules/install/test_cli_dispatchers.py
Role: Subprocess and direct tests for trae_workflow CLI dispatcher modules.
Used By:
 - pytest
Depends On:
 - .ai_infra/install/trae_workflow/{contributors_cli,doc_cli,drift_cli,integrate_cli,verify_cli}.py
 - trae_workflow/trae_workflow/*
Notes:
 - Exercises JSON and error paths to lift shipped-source coverage above 90%.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_PKG_DIR = REPO_ROOT / ".ai_infra" / "install" / "trae_workflow"

if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

import contributors_cli  # noqa: E402
import doc_cli  # noqa: E402
import drift_cli  # noqa: E402
import integrate_cli  # noqa: E402
import verify_cli  # noqa: E402


def _run_cli(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "trae_workflow", *argv],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_contributors_show_on_kit_repo() -> None:
    proc = _run_cli(["contributors", "show", "--directory", str(REPO_ROOT)])
    assert proc.returncode == 0
    assert "owner.display_name:" in proc.stdout


def test_contributors_validate_on_kit_repo() -> None:
    proc = _run_cli(["contributors", "validate", "--directory", str(REPO_ROOT)])
    assert proc.returncode == 0
    assert "contributors validate: PASS" in proc.stdout


def test_contributors_commit_trailers_on_kit_repo() -> None:
    proc = _run_cli(["contributors", "commit-trailers", "--directory", str(REPO_ROOT)])
    assert proc.returncode == 0
    assert "Author:" in proc.stdout
    assert "GitHub-User:" in proc.stdout


def test_contributors_pr_body_on_kit_repo() -> None:
    proc = _run_cli(
        [
            "contributors",
            "pr-body",
            "--directory",
            str(REPO_ROOT),
            "--summary",
            "- smoke summary",
            "--test-plan",
            "make gates",
        ]
    )
    assert proc.returncode == 0
    assert "smoke summary" in proc.stdout
    assert "make gates" in proc.stdout


def test_doc_validate_json_on_kit_repo() -> None:
    proc = _run_cli(["doc", "validate", "--directory", str(REPO_ROOT), "--json"])
    payload = json.loads(proc.stdout)
    assert any(r["check_id"] == "DOC-001" for r in payload["results"])
    assert proc.returncode == payload["exit_code"]


def test_integrate_validate_json_on_kit_repo() -> None:
    proc = _run_cli(["integrate", "validate", "--directory", str(REPO_ROOT), "--json"])
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["exit_code"] == 0
    assert any(r["check_id"].startswith("INT-") for r in payload["results"])


def test_verify_all_json_mocked(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    arch_dir = str(REPO_ROOT / ".ai_infra" / "scripts" / "architecture")
    if arch_dir not in sys.path:
        sys.path.insert(0, arch_dir)
    import verify_all

    class _Result:
        def __init__(self, name: str) -> None:
            self.name = name
            self.exit_code = 0
            self.command = f"mock-{name}"

    monkeypatch.setattr(
        verify_all,
        "run_verify_all",
        lambda root, py: [_Result("gates"), _Result("health")],
    )

    args = argparse.Namespace(
        directory=REPO_ROOT,
        json=True,
        write_preflight=False,
        preflight_out=None,
        verbose=False,
    )
    assert verify_cli.cmd_verify_all(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 0
    assert len(payload["steps"]) == 2


def test_doc_validate_write_preflight(tmp_path: Path) -> None:
    (tmp_path / ".ai_infra" / "scripts" / "architecture").mkdir(parents=True)
    arch = tmp_path / ".ai_infra" / "scripts" / "architecture" / "check_doc_facts.py"
    arch.write_text(
        "def run_checks(root):\n"
        "    class R:\n"
        "        check_id='X'; passed=True; detail='ok'\n"
        "        class severity:\n"
        "            value='P2'\n"
        "    return [R()]\n"
        "def exit_code_for(r): return 0\n"
        "def format_report(r): return 'ok'\n"
        "def write_preflight_json(r, p): p.write_text('{}', encoding='utf-8')\n",
        encoding="utf-8",
    )
    out = tmp_path / "preflight.json"
    args = argparse.Namespace(
        directory=tmp_path,
        json=False,
        write_preflight=False,
        preflight_out=out,
    )
    assert doc_cli.cmd_doc_validate(args) == 0
    assert out.is_file()


def test_contributors_validate_missing_pr_dir(tmp_path: Path) -> None:
    args = argparse.Namespace(directory=tmp_path, check_mcp=False)
    assert contributors_cli.cmd_contributors_validate(args) == 1


def test_contributors_show_missing_config(tmp_path: Path) -> None:
    pr = tmp_path / ".ai_infra" / "scripts" / "pr"
    pr.mkdir(parents=True)
    (pr / "user_settings.py").write_text(
        "GITHUB_COLLAB_REL='.local/user_settings/github.collaboration.yaml'\n"
        "def load_github_collaboration(root): return None\n"
        "def github_collaboration_path(root): return root / GITHUB_COLLAB_REL\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(directory=tmp_path)
    assert contributors_cli.cmd_contributors_show(args) == 1


def test_drift_validate_missing_workflow_dir(tmp_path: Path) -> None:
    args = argparse.Namespace(directory=tmp_path, profile=None, json=False)
    assert drift_cli.cmd_drift_validate(args) == 1


def test_integrate_validate_missing_integration_dir(tmp_path: Path) -> None:
    args = argparse.Namespace(directory=tmp_path, json=False)
    assert integrate_cli.cmd_integrate_validate(args) == 1


def test_nested_trae_workflow_package_cli_shim() -> None:
    import trae_workflow.trae_workflow.cli as nested_cli

    assert nested_cli.__version__ == "0.4.0"
    assert callable(nested_cli.main)


def test_nested_trae_workflow_module_help() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "trae_workflow.trae_workflow", "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0
    assert "install" in proc.stdout


def test_nested_trae_workflow_package_version() -> None:
    import trae_workflow.trae_workflow as nested

    assert nested.__version__ == "0.4.0"
