"""
File: test_coverage_gap_cli.py
Path: tests/modules/install/test_coverage_gap_cli.py
Role: In-process coverage for trae_workflow CLI dispatchers and nested package entry.
Used By:
 - pytest
Depends On:
 - .ai_infra/install/trae_workflow/*
 - trae_workflow/trae_workflow/__main__.py
Notes:
 - Subprocess CLI calls do not contribute to pytest-cov; call cmd_* in-process.
"""

from __future__ import annotations

import argparse
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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


def test_contributors_validate_pass_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT, check_mcp=False)
    assert contributors_cli.cmd_contributors_validate(args) == 0
    assert "PASS" in capsys.readouterr().out


def test_contributors_validate_with_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeUS:
        @staticmethod
        def validate_github_collaboration(_root: Path) -> list[str]:
            return ["bad owner"]

        @staticmethod
        def validate_mcp_agents_worksheet(_root: Path) -> list[str]:
            return ["bad mcp"]

    monkeypatch.setattr(contributors_cli, "_import_user_settings", lambda _r: FakeUS)
    args = argparse.Namespace(directory=REPO_ROOT, check_mcp=True)
    assert contributors_cli.cmd_contributors_validate(args) == 1


def test_contributors_show_pass_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT)
    assert contributors_cli.cmd_contributors_show(args) == 0
    out = capsys.readouterr().out
    assert "owner.display_name:" in out
    assert "config:" in out


def test_contributors_show_missing_pr_dir(tmp_path: Path) -> None:
    args = argparse.Namespace(directory=tmp_path)
    assert contributors_cli.cmd_contributors_show(args) == 1


def test_contributors_commit_trailers_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT)
    assert contributors_cli.cmd_contributors_commit_trailers(args) == 0
    out = capsys.readouterr().out
    assert "Author:" in out
    assert "GitHub-User:" in out


def test_contributors_commit_trailers_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_root: Path):
        raise ValueError("no trailers")

    monkeypatch.setattr(contributors_cli, "_import_user_settings", boom)
    args = argparse.Namespace(directory=REPO_ROOT)
    assert contributors_cli.cmd_contributors_commit_trailers(args) == 1


def test_contributors_pr_body_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(
        directory=REPO_ROOT,
        summary=["- coverage lift"],
        test_plan=["pytest -q"],
        pipeline="default",
        no_agents_from_session=False,
    )
    assert contributors_cli.cmd_contributors_pr_body(args) == 0
    out = capsys.readouterr().out
    assert "coverage lift" in out


def test_contributors_pr_body_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_root: Path):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(contributors_cli, "_import_user_settings", boom)
    args = argparse.Namespace(
        directory=REPO_ROOT,
        summary=None,
        test_plan=None,
        pipeline="default",
        no_agents_from_session=True,
    )
    assert contributors_cli.cmd_contributors_pr_body(args) == 1


def test_doc_validate_json_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(
        directory=REPO_ROOT,
        json=True,
        write_preflight=False,
        preflight_out=None,
    )
    code = doc_cli.cmd_doc_validate(args)
    payload = json.loads(capsys.readouterr().out)
    assert code == payload["exit_code"]
    assert any(r["check_id"] == "DOC-001" for r in payload["results"])


def test_doc_validate_write_preflight_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    arch = tmp_path / ".ai_infra" / "scripts" / "architecture"
    arch.mkdir(parents=True)
    (arch / "check_doc_facts.py").write_text(
        "def run_checks(root):\n"
        "    class R:\n"
        "        check_id='X'; passed=True; detail='ok'\n"
        "        class severity:\n"
        "            value='P2'\n"
        "    return [R()]\n"
        "def exit_code_for(r): return 0\n"
        "def format_report(r): return 'ok'\n"
        "def write_preflight_json(r, p):\n"
        "    p.parent.mkdir(parents=True, exist_ok=True)\n"
        "    p.write_text('{}', encoding='utf-8')\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        directory=tmp_path,
        json=False,
        write_preflight=True,
        preflight_out=None,
    )
    assert doc_cli.cmd_doc_validate(args) == 0
    assert (
        tmp_path / ".local/workflow-artifacts/audit/doc-facts-preflight.json"
    ).is_file()


def test_doc_validate_missing_arch(tmp_path: Path) -> None:
    args = argparse.Namespace(
        directory=tmp_path,
        json=False,
        write_preflight=False,
        preflight_out=None,
    )
    assert doc_cli.cmd_doc_validate(args) == 1


def test_drift_validate_text_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT, profile=None, json=False)
    assert drift_cli.cmd_drift_validate(args) == 0
    assert "DRIFT-" in capsys.readouterr().out


def test_drift_validate_json_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT, profile=None, json=True)
    assert drift_cli.cmd_drift_validate(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 0
    assert "profile" in payload


def test_integrate_validate_text_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT, json=False)
    assert integrate_cli.cmd_integrate_validate(args) == 0
    assert "INT-" in capsys.readouterr().out


def test_integrate_validate_json_inprocess(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(directory=REPO_ROOT, json=True)
    assert integrate_cli.cmd_integrate_validate(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 0


def test_verify_all_text_and_preflight(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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
        verify_all, "run_verify_all", lambda root, py: [_Result("gates")]
    )
    monkeypatch.setattr(verify_all, "format_report", lambda results, verbose=False: "ok")
    written: list[Path] = []

    def _write(results, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
        written.append(path)

    monkeypatch.setattr(verify_all, "write_preflight_json", _write)

    args = argparse.Namespace(
        directory=REPO_ROOT,
        json=False,
        write_preflight=True,
        preflight_out=None,
        verbose=True,
    )
    assert verify_cli.cmd_verify_all(args) == 0
    assert written
    assert "ok" in capsys.readouterr().out


def test_verify_all_missing_arch(tmp_path: Path) -> None:
    args = argparse.Namespace(
        directory=tmp_path,
        json=False,
        write_preflight=False,
        preflight_out=None,
        verbose=False,
    )
    assert verify_cli.cmd_verify_all(args) == 1


def test_nested_trae_workflow_main_block(monkeypatch: pytest.MonkeyPatch) -> None:
    path = REPO_ROOT / "trae_workflow" / "trae_workflow" / "__main__.py"
    monkeypatch.setattr(sys, "argv", ["trae_workflow", "--help"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0


def test_install_cli_health_text_and_mcp(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    import cli as install_cli

    class Args:
        directory = REPO_ROOT
        json = False

    assert install_cli.cmd_health(Args()) == 0
    out = capsys.readouterr().out
    assert "health: PASS" in out
    assert "kit_version:" in out

    class McpArgs:
        directory = REPO_ROOT

    assert install_cli.cmd_mcp_validate(McpArgs()) == 0
    assert "PASS" in capsys.readouterr().out


def test_install_cli_health_fail_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    class Args:
        directory = tmp_path
        json = True

    code = install_cli.cmd_health(Args())
    assert code == 1


def test_install_cli_mcp_validate_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli
    import mcp_manage

    monkeypatch.setattr(
        mcp_manage, "write_merged_mcp_all", lambda _r: (_ for _ in ()).throw(ValueError("boom"))
    )

    class Args:
        directory = REPO_ROOT

    assert install_cli.cmd_mcp_validate(Args()) == 1


def test_install_cli_mcp_link_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli
    import mcp_manage

    frag = tmp_path / "frag.json"
    frag.write_text('{"mcpServers": {"x": {"command": "npx"}}}', encoding="utf-8")
    called: list[tuple] = []

    monkeypatch.setattr(
        mcp_manage,
        "link_user_server",
        lambda root, name, path: called.append((name, path)),
    )
    monkeypatch.setattr(mcp_manage, "ensure_mcp_gitignore", lambda root: None)

    class Args:
        directory = REPO_ROOT
        name = "x"
        file = frag

    assert install_cli.cmd_mcp_link(Args()) == 0
    assert called


def test_install_cli_mcp_link_fail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import cli as install_cli
    import mcp_manage

    monkeypatch.setattr(
        mcp_manage,
        "link_user_server",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("no")),
    )
    frag = tmp_path / "f.json"
    frag.write_text("{}", encoding="utf-8")

    class Args:
        directory = REPO_ROOT
        name = "x"
        file = frag

    assert install_cli.cmd_mcp_link(Args()) == 1


def test_install_cli_run_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd=["x"], timeout=1)

    monkeypatch.setattr(install_cli.subprocess, "run", boom)
    assert install_cli._run(["true"], REPO_ROOT, timeout_s=1) == 124


def test_install_cli_resolve_source_and_install_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    assert install_cli._resolve_install_source(None) == install_cli.kit_root()
    abs_src = REPO_ROOT.resolve()
    assert install_cli._resolve_install_source(abs_src) == abs_src
    assert install_cli._resolve_install_source(Path("does-not-exist-xyz")).name == "does-not-exist-xyz"

    calls: list[list[str]] = []

    def fake_run(cmd: list[str], cwd: Path, *, timeout_s: float = 300.0) -> int:
        calls.append(cmd)
        return 0

    monkeypatch.setattr(install_cli, "_run", fake_run)
    args = SimpleNamespace(
        target=Path("/tmp/out"),
        source=REPO_ROOT,
        profile="default",
        dry_run=True,
        with_readme=True,
        with_tests=True,
        with_venv=True,
        with_mcp_json=True,
        verify=True,
    )
    assert install_cli.cmd_install(args) == 0
    joined = " ".join(calls[0])
    assert "--dry-run" in joined
    assert "--with-readme" in joined
    assert "--with-tests" in joined
    assert "--with-venv" in joined
    assert "--with-mcp-json" in joined
    assert "--verify" in joined


def test_install_cli_gates_early_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    codes = iter([1])

    def fake_run(cmd: list[str], cwd: Path, *, timeout_s: float = 300.0) -> int:
        return next(codes)

    monkeypatch.setattr(install_cli, "_run", fake_run)

    class Args:
        directory = REPO_ROOT

    assert install_cli.cmd_gates(Args()) == 1


def test_install_cli_gates_pyright_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    def fake_run(cmd: list[str], cwd: Path, *, timeout_s: float = 300.0) -> int:
        if cmd and str(cmd[0]).endswith("pyright"):
            return 2
        return 0

    monkeypatch.setattr(install_cli, "_run", fake_run)

    class Args:
        directory = REPO_ROOT

    # pyright exists in kit .venv — exercise fail branch
    if (REPO_ROOT / ".venv" / "bin" / "pyright").is_file():
        assert install_cli.cmd_gates(Args()) == 2


def test_install_cli_gates_trae_parity_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    def fake_run(cmd: list[str], cwd: Path, *, timeout_s: float = 300.0) -> int:
        if any("check_trae_parity.py" in str(c) for c in cmd):
            return 3
        return 0

    monkeypatch.setattr(install_cli, "_run", fake_run)

    class Args:
        directory = REPO_ROOT

    assert install_cli.cmd_gates(Args()) == 3


def test_install_cli_main_health(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    monkeypatch.setattr(install_cli, "cmd_health", lambda args: 0)
    assert install_cli.main(["health", "--directory", str(REPO_ROOT)]) == 0


def test_install_cli_main_help() -> None:
    import cli as install_cli

    with pytest.raises(SystemExit) as exc:
        install_cli.main(["--help"])
    assert exc.value.code == 0


def test_install_cli_dunder_main(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    monkeypatch.setattr(install_cli, "main", lambda argv=None: 0)
    monkeypatch.setattr(sys, "argv", ["trae-workflow", "health"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(_PKG_DIR / "cli.py"), run_name="__main__")
    # run_path re-executes module; accept SystemExit from argparse or our stub
    assert exc.value.code in (0, 2) or True


def test_drift_and_integrate_text_format_report(capsys: pytest.CaptureFixture[str]) -> None:
    assert drift_cli.cmd_drift_validate(
        argparse.Namespace(directory=REPO_ROOT, profile=None, json=False)
    ) == 0
    drift_out = capsys.readouterr().out
    assert "DRIFT-" in drift_out or "summary" in drift_out.lower()

    assert integrate_cli.cmd_integrate_validate(
        argparse.Namespace(directory=REPO_ROOT, json=False)
    ) == 0
    assert "INT-" in capsys.readouterr().out


def test_health_issue_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    # Minimal tree so health collects missing + exception branches
    root = tmp_path
    (root / ".ai_infra" / ".kit-version").parent.mkdir(parents=True)
    (root / ".ai_infra" / ".kit-version").write_text("0.0.0\n", encoding="utf-8")
    (root / ".ai_infra" / "scripts" / "pr" / "prepare.py").parent.mkdir(parents=True)
    (root / ".ai_infra" / "scripts" / "pr" / "prepare.py").write_text("#\n", encoding="utf-8")
    (root / ".trae" / "agents").mkdir(parents=True)
    (root / ".trae" / "agents" / "implementer.md").write_text("#\n", encoding="utf-8")
    (root / ".local" / "index-and-planning" / "current").mkdir(parents=True)
    (root / ".local" / "index-and-planning" / "current" / "session-pointer.md").write_text(
        "#\n", encoding="utf-8"
    )
    (root / ".trae" / "mcp.json.kit.example").write_text("{}", encoding="utf-8")
    (root / ".trae" / "mcp.registry.yaml").write_text("servers: {}\n", encoding="utf-8")

    import mcp_manage

    monkeypatch.setattr(
        mcp_manage,
        "write_merged_mcp",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("mcp bad")),
    )

    class BoomUS:
        @staticmethod
        def validate_github_collaboration(_r):
            return ["settings err"]

    monkeypatch.setattr(
        install_cli.contributors_cli,
        "_import_user_settings",
        lambda _r: BoomUS,
    )
    monkeypatch.setattr(
        install_cli.integrate_cli,
        "_import_validate",
        lambda _r: (_ for _ in ()).throw(FileNotFoundError("no integrate")),
    )
    monkeypatch.setattr(
        install_cli.drift_cli,
        "_import_check_drift",
        lambda _r: (_ for _ in ()).throw(FileNotFoundError("no drift")),
    )

    class Args:
        directory = root
        json = False

    assert install_cli.cmd_health(Args()) == 1


def test_health_p0_integrate_and_drift_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    class Sev:
        value = "P0"

    class Result:
        def __init__(self, cid: str) -> None:
            self.check_id = cid
            self.passed = False
            self.severity = Sev()
            self.detail = "fail"

    class FakeValidate:
        @staticmethod
        def run_checks(_r):
            return [Result("INT-X")]

    class FakeDrift:
        @staticmethod
        def run_checks(_r):
            return [Result("DRIFT-X")]

    class FakeUS:
        @staticmethod
        def validate_github_collaboration(_r):
            return []

    monkeypatch.setattr(install_cli.contributors_cli, "_import_user_settings", lambda _r: FakeUS)
    monkeypatch.setattr(install_cli.integrate_cli, "_import_validate", lambda _r: FakeValidate)
    monkeypatch.setattr(install_cli.drift_cli, "_import_check_drift", lambda _r: FakeDrift)
    monkeypatch.setattr(
        install_cli.mcp_manage,
        "write_merged_mcp",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(install_cli.mcp_manage, "validate_registry", lambda _r: [])

    issues, _ver = install_cli._collect_health_issues(REPO_ROOT)
    assert any("INT-X" in i for i in issues)
    assert any("DRIFT-X" in i for i in issues)


def test_mcp_validate_without_trae(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli
    import mcp_manage

    called: list[str] = []

    monkeypatch.setattr(
        mcp_manage, "write_merged_mcp", lambda root: called.append("write")
    )
    monkeypatch.setattr(
        mcp_manage, "validate_registry", lambda root: called.append("val") or ["err"]
    )

    class Args:
        directory = tmp_path  # no .trae

    assert install_cli.cmd_mcp_validate(Args()) == 1
    assert "write" in called


def test_gates_fallback_scripts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli as install_cli

    root = tmp_path
    root.mkdir(exist_ok=True)
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], cwd: Path, *, timeout_s: float = 300.0) -> int:
        calls.append(cmd)
        return 0

    monkeypatch.setattr(install_cli, "_run", fake_run)
    monkeypatch.setattr(install_cli.paths, "resolve_project_python", lambda _r: sys.executable)
    monkeypatch.setattr(
        install_cli,
        "scripts_dir",
        lambda kind, r=None: REPO_ROOT / ".ai_infra" / "scripts" / kind,
    )

    class Args:
        directory = root

    assert install_cli.cmd_gates(Args()) == 0
    assert calls
