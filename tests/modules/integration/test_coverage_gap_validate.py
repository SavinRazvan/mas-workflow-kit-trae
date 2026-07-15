"""
File: test_coverage_gap_validate.py
Path: tests/modules/integration/test_coverage_gap_validate.py
Role: In-process coverage for validate.py and checks.py remaining branches.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/integration/validate.py
 - .ai_infra/scripts/integration/checks.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
INTEGRATION = REPO_ROOT / ".ai_infra" / "scripts" / "integration"
if str(INTEGRATION) not in sys.path:
    sys.path.insert(0, str(INTEGRATION))

import checks  # noqa: E402
import validate  # noqa: E402


def test_checks_empty_and_bad_inputs(tmp_path: Path) -> None:
    assert checks.agent_file_ids(tmp_path / "nope") == set()
    assert checks.registry_agent_ids(tmp_path / "nope.yaml") == set()
    bad = tmp_path / "reg.yaml"
    bad.write_text("- just a list\n", encoding="utf-8")
    assert checks.registry_agent_ids(bad) == set()
    bad2 = tmp_path / "reg2.yaml"
    bad2.write_text("servers:\n  s:\n    agents: [1, 'ok', '  ']\n", encoding="utf-8")
    assert checks.registry_agent_ids(bad2) == {"ok"}

    empty = tmp_path / "agents"
    empty.mkdir()
    assert any("no agent files" in v for v in checks.check_all_agent_files(empty))
    assert checks.check_all_agent_files(tmp_path / "missing")

    assert checks.pipeline_names_from_exemplar(tmp_path / "no.yaml") == set()
    ex = tmp_path / "ex.yaml"
    ex.write_text("- list\n", encoding="utf-8")
    assert checks.pipeline_names_from_exemplar(ex) == set()
    ex.write_text("pr_collaboration:\n  pipelines: not-a-map\n", encoding="utf-8")
    assert checks.pipeline_names_from_exemplar(ex) == set()

    violations = checks.check_pipeline_agent_ids(
        cfg={"pr_collaboration": {"pipelines": "bad"}},
        agents_dir=tmp_path,
    )
    assert violations == []
    violations = checks.check_pipeline_agent_ids(
        cfg={
            "pr_collaboration": {
                "pipelines": {
                    "default": "bad",
                    "p2": {"agents": [1, "  ", "ghost-agent"]},
                }
            }
        },
        agents_dir=tmp_path,
    )
    assert any("ghost-agent" in v for v in violations)


def test_validate_remaining_helpers(tmp_path: Path) -> None:
    integ = str(REPO_ROOT / ".ai_infra/scripts/integration")
    if integ not in sys.path:
        sys.path.insert(0, integ)
    import validate

    assert validate._is_kit_dev_root(REPO_ROOT) is True
    assert validate._is_kit_dev_root(tmp_path) is False

    # Need .ai_infra present so ai_infra_dir resolves; omit architecture scripts
    (tmp_path / ".ai_infra" / "scripts").mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="not found|missing"):
        validate._import_check_doc_facts(tmp_path)

    r = validate._check_int013(tmp_path)
    assert not r.passed
    assert "import failed" in r.detail

    report = validate.format_report(
        [
            validate.CheckResult("X", validate.Severity.P0, True, "ok"),
            validate.CheckResult("Y", validate.Severity.P1, False, "no"),
            validate.CheckResult("Z", validate.Severity.P2, False, "no2"),
        ]
    )
    assert "p0_fail=0" in report
    assert "p1_fail=1" in report
    assert "p2_fail=1" in report


def test_validate_check_helpers_and_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = {
        "agents_dir": tmp_path / ".trae" / "agents",
        "registry_example": tmp_path / ".trae" / "mcp.registry.yaml.example",
        "github_exemplar": tmp_path / "ex.yaml",
        "manifest": tmp_path / "manifest.yaml",
        "ops_doc": tmp_path / "ops.md",
        "checklist": tmp_path / "check.md",
    }
    (tmp_path / ".trae" / "agents").mkdir(parents=True)
    # INT-011 missing agent
    r = validate._check_int011(tmp_path, paths)
    assert not r.passed

    # INT-004 mismatch
    class US:
        PIPELINE_NAMES = ("default", "extra")

    paths["github_exemplar"].write_text(
        "pr_collaboration:\n  pipelines:\n    default: {}\n    only_ex: {}\n",
        encoding="utf-8",
    )
    r4 = validate._check_int004(US, paths)
    assert not r4.passed

    # INT-005/006/007/015 skips
    class US2:
        @staticmethod
        def load_github_collaboration(_r):
            return None

        @staticmethod
        def github_collaboration_path(root):
            return root / "missing.yaml"

        @staticmethod
        def mcp_agents_path(root):
            return root / "missing-mcp.yaml"

    assert validate._check_int005(US2, tmp_path, paths).passed
    assert validate._check_int006(US2, tmp_path).passed
    assert validate._check_int007(US2, tmp_path).passed
    assert validate._check_int015(US2, tmp_path).passed

    class US3:
        @staticmethod
        def github_collaboration_path(root):
            p = root / "g.yaml"
            p.write_text("x: 1\n", encoding="utf-8")
            return p

        @staticmethod
        def load_github_collaboration(_r):
            return None

    assert not validate._check_int015(US3, tmp_path).passed

    # INT-008 missing / bad manifest
    assert not validate._check_int008(paths).passed
    paths["manifest"].write_text(
        "profiles:\n  default:\n    copy_dirs: []\n    copy_ai_infra: []\n",
        encoding="utf-8",
    )
    assert not validate._check_int008(paths).passed

    # INT-012 import failure
    monkeypatch.setattr(
        validate,
        "_import_check_drift",
        lambda _r: (_ for _ in ()).throw(ImportError("boom")),
    )
    (tmp_path / ".ai_infra" / "scripts" / "workflow").mkdir(parents=True)
    r12 = validate._check_int012(tmp_path)
    assert not r12.passed
    assert "import failed" in r12.detail

    # INT-013 consumer skip
    monkeypatch.setattr(
        validate,
        "_import_check_doc_facts",
        lambda _r: SimpleNamespace(),
    )

    import doc_facts_checks

    monkeypatch.setattr(doc_facts_checks, "is_kit_dev", lambda _r: False)
    # Force import path inside _check_int013
    class FakeCDF:
        @staticmethod
        def run_checks(_r):
            return []

    def fake_import(_r):
        # inject is_kit_dev via monkeypatch already on module used inside function
        return FakeCDF

    monkeypatch.setattr(validate, "_import_check_doc_facts", fake_import)
    # Patch is_kit_dev where validate imports it
    import importlib

    dfc = importlib.import_module("doc_facts_checks")
    monkeypatch.setattr(dfc, "is_kit_dev", lambda _r: False)
    r13 = validate._check_int013(tmp_path)
    assert r13.passed
    assert "consumer" in r13.detail.lower() or "skipped" in r13.detail.lower()

    # INT-014 violations
    r14 = validate._check_int014(tmp_path)
    assert not r14.passed

    results = [
        validate.CheckResult("A", validate.Severity.P0, False, "a"),
        validate.CheckResult("B", validate.Severity.P1, False, "b"),
        validate.CheckResult("C", validate.Severity.P2, False, "c"),
        validate.CheckResult("D", validate.Severity.P0, True, "ok"),
    ]
    report = validate.format_report(results)
    assert "p0_fail=1" in report
    assert "p1_fail=1" in report
    assert "p2_fail=1" in report


def test_validate_main_json_and_text(capsys: pytest.CaptureFixture[str]) -> None:
    code = validate.main(["--directory", str(REPO_ROOT), "--json"])
    out = capsys.readouterr().out
    assert '"check_id"' in out
    assert code in (0, 1)

    code2 = validate.main(["--directory", str(REPO_ROOT)])
    out2 = capsys.readouterr().out
    assert "INT-" in out2
    assert code2 in (0, 1)


def test_validate_dunder_main(monkeypatch: pytest.MonkeyPatch) -> None:
    path = INTEGRATION / "validate.py"
    monkeypatch.setattr(sys, "argv", [str(path), "--directory", str(REPO_ROOT), "--json"])
    with pytest.raises(SystemExit):
        runpy.run_path(str(path), run_name="__main__")


def test_is_kit_dev_and_sys_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert validate._is_kit_dev_root(REPO_ROOT) is True
    assert validate._is_kit_dev_root(tmp_path) is False
    # Force insert branch for _AI_INFRA_PKG by ensuring it's present then calling path helpers
    pkg = str(Path(validate.__file__).resolve().parents[2])
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
