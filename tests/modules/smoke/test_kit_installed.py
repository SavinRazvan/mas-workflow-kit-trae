"""
File: test_kit_installed.py
Path: tests/modules/smoke/test_kit_installed.py
Role: Smoke test that core kit paths exist after consumer install.
Used By:
 - pytest (consumer default scaffold)
Depends On:
 - scaffold minimal test layout
Notes:
 - Replaced when install uses --with-tests (kit dev only).
"""
from pathlib import Path


def test_core_layout_installed() -> None:
    assert Path(".cursor/agents/implementer.md").is_file()
    assert Path(".ai_infra/scripts/pr/prepare.py").is_file()
    assert Path("AGENTS.md").is_file()
    assert Path(".local/index-and-planning/current/session-pointer.md").is_file()
    assert Path(".local/workflow-artifacts/drift").is_dir()
    assert Path(".trae/mcp.json").is_file()
    assert Path(".trae/rules/agent-implementer.md").is_file()
    agent_rule = Path(".trae/rules/agent-implementer.md").read_text(encoding="utf-8")
    assert ".trae/skills/" in agent_rule
    assert ".cursor/skills/" not in agent_rule
