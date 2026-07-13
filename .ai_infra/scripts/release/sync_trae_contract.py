"""
File: sync_trae_contract.py
Path: .ai_infra/scripts/release/sync_trae_contract.py
Role: Generate .trae/ contract plane from .cursor/ + .agents/ SSOT (ADR-008).
Used By:
 - sync_plugin_bundle.py
 - check_trae_parity.py
Depends On:
 - .ai_infra/ide_contract_paths.py
Notes:
 - Output files are GENERATED — do not edit by hand.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

_GENERATED_BANNER = "<!-- GENERATED — do not edit. Sync from .cursor/ via sync_trae_contract.py -->\n\n"
_AGENT_RULE_PREFIX = "agent-"

# Order matters: longer prefixes before shorter; .mdc → .md after path prefixes.
_PATH_REWRITES: tuple[tuple[str, str], ...] = (
    (".cursor/skills/", ".trae/skills/"),
    (".cursor/rules/", ".trae/rules/"),
    (".cursor/agents/", ".trae/agents/"),
    (".cursor/mcp.", ".trae/mcp."),
)
_MDC_IN_RULE_PATH = re.compile(r"(\.trae/rules/[^\s`\"')]+?)\.mdc\b")


def rewrite_cursor_paths_for_trae(content: str) -> str:
    """Rewrite Cursor contract paths to Trae equivalents in generated artifacts."""
    out = content
    for old, new in _PATH_REWRITES:
        out = out.replace(old, new)
    out = _MDC_IN_RULE_PATH.sub(r"\1.md", out)
    return out


def _write_trae_text(path: Path, content: str) -> None:
    path.write_text(rewrite_cursor_paths_for_trae(content), encoding="utf-8")


def _rewrite_trae_tree_markdown(root: Path) -> None:
    for md in sorted(root.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        rewritten = rewrite_cursor_paths_for_trae(text)
        if rewritten != text:
            md.write_text(rewritten, encoding="utf-8")


def _read_agent_description(agent_path: Path) -> str:
    text = agent_path.read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return f"MAS Workflow Kit agent: {agent_path.stem}"


def transform_rule_mdc_to_md(content: str) -> str:
    """Copy .mdc rule body; frontmatter unchanged; rewrite Cursor paths for Trae."""
    body = _GENERATED_BANNER + content.lstrip("\ufeff")
    return rewrite_cursor_paths_for_trae(body)


def transform_agent_to_rule(agent_path: Path) -> str:
    """Build Trae agent-requested rule from Cursor agent file."""
    agent_id = agent_path.stem
    description = _read_agent_description(agent_path)
    body = agent_path.read_text(encoding="utf-8")
    if body.startswith("---"):
        end = body.find("---", 3)
        if end != -1:
            body = body[end + 3 :].lstrip("\n")
    frontmatter = (
        f"---\n"
        f"description: {description}\n"
        f"alwaysApply: false\n"
        f"---\n\n"
    )
    header = (
        f"# Agent persona: {agent_id}\n\n"
        f"When the user invokes **{agent_id}** or asks to run as this kit agent, "
        f"follow the protocol below. Canonical source: `.trae/agents/{agent_id}.md`.\n\n"
    )
    return rewrite_cursor_paths_for_trae(_GENERATED_BANNER + frontmatter + header + body)


def sync_trae_contract(kit_root: Path, trae_dir: Path | None = None) -> Path:
    """
    Generate .trae/ tree under kit_root (or trae_dir).

    Returns path to generated .trae/ root.
    """
    dest = trae_dir if trae_dir is not None else kit_root / ".trae"
    cursor = kit_root / ".cursor"
    rules_src = cursor / "rules"
    skills_src = cursor / "skills"
    agents_src = cursor / "agents"
    maintainer_skills = kit_root / ".agents" / "skills"

    if dest.exists():
        shutil.rmtree(dest)

    trae_rules = dest / "rules"
    trae_skills = dest / "skills"
    trae_agents = dest / "agents"
    trae_rules.mkdir(parents=True)
    trae_skills.mkdir(parents=True)
    trae_agents.mkdir(parents=True)

    if rules_src.is_dir():
        for mdc in sorted(rules_src.glob("*.mdc")):
            content = mdc.read_text(encoding="utf-8")
            out = trae_rules / f"{mdc.stem}.md"
            out.write_text(transform_rule_mdc_to_md(content), encoding="utf-8")

    if agents_src.is_dir():
        for agent in sorted(agents_src.glob("*.md")):
            rule_out = trae_rules / f"{_AGENT_RULE_PREFIX}{agent.stem}.md"
            rule_out.write_text(transform_agent_to_rule(agent), encoding="utf-8")
            agent_dest = trae_agents / agent.name
            _write_trae_text(agent_dest, agent.read_text(encoding="utf-8"))

    if skills_src.is_dir():
        for skill_dir in sorted(skills_src.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
                target = trae_skills / skill_dir.name
                shutil.copytree(skill_dir, target)

    if maintainer_skills.is_dir():
        for skill_dir in sorted(maintainer_skills.iterdir()):
            if not skill_dir.is_dir():
                continue
            target = trae_skills / skill_dir.name
            if not target.exists():
                shutil.copytree(skill_dir, target)

    _rewrite_trae_tree_markdown(trae_skills)
    _rewrite_trae_tree_markdown(trae_agents)

    mcp_kit = cursor / "mcp.json.kit.example"
    if mcp_kit.is_file():
        shutil.copy2(mcp_kit, dest / "mcp.json.kit.example")
        shutil.copy2(mcp_kit, dest / "mcp.json")

    mcp_registry = cursor / "mcp.registry.yaml.example"
    if mcp_registry.is_file():
        shutil.copy2(mcp_registry, dest / "mcp.registry.yaml.example")
        shutil.copy2(mcp_registry, dest / "mcp.registry.yaml")

    mcp_user_example = cursor / "mcp.user.example.json"
    if mcp_user_example.is_file():
        shutil.copy2(mcp_user_example, dest / "mcp.user.example.json")

    return dest


def expected_rule_basenames(cursor_rules_dir: Path) -> set[str]:
    """Expected .trae/rules/*.md stems from .cursor/rules/*.mdc."""
    if not cursor_rules_dir.is_dir():
        return set()
    return {p.stem for p in cursor_rules_dir.glob("*.mdc")}


def expected_agent_rule_basenames(cursor_agents_dir: Path) -> set[str]:
    if not cursor_agents_dir.is_dir():
        return set()
    return {_AGENT_RULE_PREFIX + p.stem for p in cursor_agents_dir.glob("*.md")}
