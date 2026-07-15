"""
File: test_coverage_gap_release.py
Path: tests/modules/release/test_coverage_gap_release.py
Role: In-process coverage for sync_plugin_bundle and sync_trae_contract gaps.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/release/sync_plugin_bundle.py
 - .ai_infra/scripts/release/sync_trae_contract.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RELEASE = REPO_ROOT / ".ai_infra" / "scripts" / "release"


def _load(name: str, filename: str):
    path = RELEASE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_sync_plugin_resolve_profile_and_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load("sync_plugin_bundle_gap", "sync_plugin_bundle.py")
    with pytest.raises(ValueError, match="unknown profile"):
        mod._resolve_profile({"profiles": {}}, "nope")

    manifest = {
        "profiles": {
            "base": {"copy_dirs": ["a"], "copy_ai_infra": ["x"], "copy_files": ["f"]},
            "child": {
                "extends": "base",
                "copy_dirs": ["b"],
                "copy_dirs_replace": ["only"],
                "copy_ai_infra": ["y"],
            },
        }
    }
    merged = mod._resolve_profile(manifest, "child")
    assert merged["copy_dirs"] == ["only"]
    assert "x" in merged["copy_ai_infra"] and "y" in merged["copy_ai_infra"]

    bad = tmp_path / "m.yaml"
    bad.write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(mod, "MANIFEST_PATH", bad)
    with pytest.raises(RuntimeError, match="invalid manifest"):
        mod._load_manifest()

    with pytest.raises(FileNotFoundError):
        mod._copy_tree(tmp_path / "missing", tmp_path / "dst")
    with pytest.raises(FileNotFoundError):
        mod._copy_file(tmp_path / "missing.txt", tmp_path / "out.txt")


def test_check_bundle_missing_payload_and_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mod = _load("sync_plugin_bundle_gap2", "sync_plugin_bundle.py")
    monkeypatch.setattr(mod, "PAYLOAD_DIR", tmp_path / "no-payload")
    errs = mod.check_bundle("default")
    assert any("payload/ missing" in e for e in errs)

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "extra.txt").write_text("x", encoding="utf-8")
    monkeypatch.setattr(mod, "PAYLOAD_DIR", payload)
    monkeypatch.setattr(mod, "KIT_ROOT", tmp_path)

    def fake_sync(expected_payload, _plugin, profile="default"):
        expected_payload.mkdir(parents=True)
        (expected_payload / "needed.txt").write_text("a", encoding="utf-8")
        (expected_payload / "changed.txt").write_text("old", encoding="utf-8")

    (payload / "changed.txt").write_text("new", encoding="utf-8")
    monkeypatch.setattr(mod, "sync_payload", fake_sync)
    errs = mod.check_bundle("default")
    joined = "\n".join(errs)
    assert "missing files" in joined or "extra files" in joined or "content drift" in joined
    assert any("missing required bundle file" in e for e in errs)

    assert mod._collect_files(tmp_path / "does-not-exist") == {}
    sync_called: list[str] = []
    monkeypatch.setattr(mod, "sync_payload", lambda *a, **k: sync_called.append("ok"))
    monkeypatch.setattr(mod, "PAYLOAD_DIR", tmp_path / "p2")
    mod.sync_all("default")
    assert sync_called


def test_copy_ai_infra_rel_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load("sync_plugin_bundle_gap3", "sync_plugin_bundle.py")
    ai_src = tmp_path / "ai"
    ai_dst = tmp_path / "dst"
    (ai_src / "docs" / "operations").mkdir(parents=True)
    (ai_src / "docs" / "operations" / "x.md").write_text("x", encoding="utf-8")
    (ai_src / "templates" / "local-workspace").mkdir(parents=True)
    (ai_src / "templates" / "local-workspace" / "y.md").write_text("y", encoding="utf-8")
    (ai_src / "plain").mkdir()
    (ai_src / "plain" / "z.md").write_text("z", encoding="utf-8")

    cbp = mod._load_consumer_bundle_paths()
    monkeypatch.setattr(cbp, "is_local_workspace_copy", lambda rel: "local-workspace" in rel)
    monkeypatch.setattr(cbp, "is_operations_copy", lambda rel: "operations" in rel)
    monkeypatch.setattr(cbp, "ignore_local_workspace_ci", None)
    monkeypatch.setattr(cbp, "ignore_operations_maintainer", None)

    mod._copy_ai_infra_rel(ai_src, ai_dst, "templates/local-workspace")
    mod._copy_ai_infra_rel(ai_src, ai_dst, "docs/operations")
    mod._copy_ai_infra_rel(ai_src, ai_dst, "plain")
    assert (ai_dst / "plain" / "z.md").is_file()


def test_sync_trae_ssot_and_from_cursor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sync = _load("sync_trae_contract_gap", "sync_trae_contract.py")

    with pytest.raises(FileNotFoundError, match="missing Trae SSOT"):
        sync.sync_trae_contract_from_ssot(tmp_path, tmp_path / ".trae")

    src = tmp_path / "kit" / ".trae"
    (src / "rules").mkdir(parents=True)
    (src / "rules" / "a.md").write_text("See `.cursor/skills/x/SKILL.md`\n", encoding="utf-8")
    dest = tmp_path / "out" / ".trae"
    dest.mkdir(parents=True)
    (dest / "old.txt").write_text("stale", encoding="utf-8")
    out = sync.sync_trae_contract_from_ssot(tmp_path / "kit", dest)
    assert (out / "rules" / "a.md").is_file()
    assert ".trae/skills" in (out / "rules" / "a.md").read_text(encoding="utf-8")

    agent = tmp_path / "agent.md"
    agent.write_text("# no frontmatter desc\n", encoding="utf-8")
    assert "MAS Workflow Kit agent" in sync._read_agent_description(agent)

    kit = tmp_path / "dual"
    cursor = kit / ".cursor"
    (cursor / "rules").mkdir(parents=True)
    (cursor / "agents").mkdir(parents=True)
    (cursor / "skills" / "s1").mkdir(parents=True)
    (cursor / "rules" / "r.mdc").write_text("---\nalwaysApply: true\n---\nbody\n", encoding="utf-8")
    (cursor / "agents" / "impl.md").write_text(
        "---\ndescription: d\n---\nUse `.cursor/rules/r.mdc`\n", encoding="utf-8"
    )
    (cursor / "skills" / "s1" / "SKILL.md").write_text("skill\n", encoding="utf-8")
    maint = kit / ".agents" / "skills" / "extra"
    maint.mkdir(parents=True)
    (maint / "SKILL.md").write_text("extra\n", encoding="utf-8")
    (cursor / "mcp.json.kit.example").write_text('{"mcpServers":{}}', encoding="utf-8")
    (cursor / "mcp.registry.yaml.example").write_text("servers: {}\n", encoding="utf-8")
    (cursor / "mcp.user.example.json").write_text("{}", encoding="utf-8")

    dest2 = kit / ".trae"
    dest2.mkdir()
    (dest2 / "stale").mkdir()
    sync.sync_trae_contract_from_cursor(kit, dest2)
    assert (dest2 / "rules" / "r.md").is_file()
    assert (dest2 / "rules" / "agent-impl.md").is_file()
    assert (dest2 / "skills" / "s1" / "SKILL.md").is_file()
    assert (dest2 / "skills" / "extra" / "SKILL.md").is_file()
    assert (dest2 / "mcp.json").is_file()
    assert (dest2 / "mcp.registry.yaml").is_file()
    assert (dest2 / "mcp.user.example.json").is_file()

    assert sync.expected_rule_basenames(tmp_path / "missing") == set()
    assert sync.expected_agent_rule_basenames(tmp_path / "missing") == set()
    assert "r" in sync.expected_rule_basenames(cursor / "rules")
    assert "agent-impl" in sync.expected_agent_rule_basenames(cursor / "agents")

    monkeypatch.setattr(sync, "uses_trae_ssot", lambda root, profile="": False)
    out3 = sync.sync_trae_contract(kit, kit / ".trae-gen")
    assert (out3 / "rules" / "r.md").is_file()
