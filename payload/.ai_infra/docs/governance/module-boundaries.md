<!--
File: module-boundaries.md
Path: .ai_infra/docs/governance/module-boundaries.md
Role: Machine-readable charter for cross-plane boundaries in the MAS Workflow Kit (Trae edition).
Used By:
 - .ai_infra/docs/governance/README.md
Depends On:
 - .ai_infra/docs/decisions/ADR-009-trae-only-edition.md
Notes:
 - Product application code belongs in consumer repos or overlay rules, not universal agents.
-->

# Module boundaries

## Planes

| Plane | Path | May import Python? | May invoke scripts? |
|-------|------|--------------------|---------------------|
| Trae contract | `.trae/` | No | Via documented `python .ai_infra/scripts/...` only |
| Infrastructure | `.ai_infra/scripts/`, `.ai_infra/mcp_servers/` | Yes (kit scripts) | N/A |
| Runtime | `.local/` | No | Read/write artifacts only |

## Rules

1. **`.trae/`** — prose, skills, rules, MCP config only. No embedded gate command lists; point to `prepare.py` `GATES`.
2. **`.ai_infra/scripts/`** — deterministic workflow spine. May read `.local/` only via paths in `local_workflow_paths.py`.
3. **`.ai_infra/mcp_servers/workflow_mcp/`** — wraps scripts; does not reimplement gate logic.
4. **Overlays** (`overlays/rules/`) — product-specific rules; copy into consumer `.trae/rules/` at install.
5. **Kit dev** (`tests/`, `docs/handoff/`) — not installed to consumers by default.

## ADR-009 (Trae-only edition)

See [ADR-009](../decisions/ADR-009-trae-only-edition.md) §5 and [dual-ide-legacy.md](../operations/dual-ide-legacy.md) for how Cursor plugin paths relate to the Trae contract plane without duplicating gate logic in `.trae/`.

## Forbidden

- Provider SDK imports in `.trae/` agent files
- Duplicating `GATES` command lists in agent surfaces
- Bare `scripts/pr/` paths in agent surfaces (use `.ai_infra/scripts/pr/`)
