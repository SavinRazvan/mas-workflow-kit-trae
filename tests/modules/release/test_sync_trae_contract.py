"""
File: test_sync_trae_contract.py
Path: tests/modules/release/test_sync_trae_contract.py
Role: Tests for Trae contract sync from .cursor/ SSOT.
Used By:
 - pytest
Depends On:
 - .ai_infra/scripts/release/sync_trae_contract.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RELEASE = REPO_ROOT / ".ai_infra" / "scripts" / "release"


def _load_sync_trae():
    if str(RELEASE) not in sys.path:
        sys.path.insert(0, str(RELEASE))
    spec = importlib.util.spec_from_file_location(
        "sync_trae_contract", RELEASE / "sync_trae_contract.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sync_trae_contract_generates_rules_and_skills(tmp_path: Path) -> None:
    sync_trae = _load_sync_trae()
    kit = REPO_ROOT
    dest = tmp_path / ".trae"
    sync_trae.sync_trae_contract(kit, dest)

    assert (dest / "rules" / "pr-workflow-enforcement.md").is_file()
    assert (dest / "skills" / "workflow-activate" / "SKILL.md").is_file()
    assert (dest / "agents" / "implementer.md").is_file()
    assert (dest / "rules" / "agent-implementer.md").is_file()
    assert (dest / "mcp.json").is_file()


def test_transform_rule_preserves_frontmatter() -> None:
    sync_trae = _load_sync_trae()
    sample = "---\nalwaysApply: true\ndescription: test\n---\n\n# Body\n"
    out = sync_trae.transform_rule_mdc_to_md(sample)
    assert "alwaysApply: true" in out
    assert "# Body" in out
    assert out.startswith("<!-- GENERATED")


def test_payload_trae_present_after_sync() -> None:
    payload_trae = REPO_ROOT / "payload" / ".trae"
    assert payload_trae.is_dir(), "run make sync-plugin to generate payload/.trae/"
    assert (payload_trae / "rules" / "pr-workflow-enforcement.md").is_file()


def test_rewrite_cursor_paths_for_trae() -> None:
    sync_trae = _load_sync_trae()
    sample = (
        "See `.cursor/skills/foo/SKILL.md` and `.cursor/rules/bar.mdc` "
        "and `.cursor/agents/implementer.md` and `.cursor/mcp.json`"
    )
    out = sync_trae.rewrite_cursor_paths_for_trae(sample)
    assert ".trae/skills/foo/SKILL.md" in out
    assert ".trae/rules/bar.md" in out
    assert ".trae/agents/implementer.md" in out
    assert ".trae/mcp.json" in out
    assert ".cursor/" not in out
    assert ".ai_infra/" in sync_trae.rewrite_cursor_paths_for_trae("`.ai_infra/docs/`")


def test_agent_rule_uses_trae_paths(tmp_path: Path) -> None:
    sync_trae = _load_sync_trae()
    kit = tmp_path
    cursor = kit / ".cursor"
    (cursor / "agents").mkdir(parents=True)
    agent = cursor / "agents" / "test-agent.md"
    agent.write_text(
        "---\ndescription: test\n---\nUse `.cursor/skills/implementation-execution-loop/SKILL.md`\n",
        encoding="utf-8",
    )
    dest = kit / ".trae"
    sync_trae.sync_trae_contract(kit, dest)
    rule_text = (dest / "rules" / "agent-test-agent.md").read_text(encoding="utf-8")
    assert ".trae/skills/implementation-execution-loop/SKILL.md" in rule_text
    assert ".cursor/skills/" not in rule_text


def test_skill_copy_rewrites_paths(tmp_path: Path) -> None:
    sync_trae = _load_sync_trae()
    kit = tmp_path
    skill = kit / ".cursor" / "skills" / "my-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "Follow `.cursor/rules/foo.mdc` for governance.\n", encoding="utf-8"
    )
    (kit / ".cursor" / "rules").mkdir(parents=True)
    (kit / ".cursor" / "agents").mkdir(parents=True)
    dest = sync_trae.sync_trae_contract(kit)
    skill_text = (dest / "skills" / "my-skill" / "SKILL.md").read_text(encoding="utf-8")
    assert ".trae/rules/foo.md" in skill_text
    assert ".cursor/rules/" not in skill_text
