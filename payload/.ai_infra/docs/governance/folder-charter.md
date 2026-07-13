<!--
File: folder-charter.md
Path: .ai_infra/docs/governance/folder-charter.md
Role: Charter for three-plane layout (Trae contract, infrastructure, runtime) vs kit-dev-only paths.
Used By:
 - .ai_infra/docs/governance/README.md
Depends On:
 - .ai_infra/docs/operations/local-workspace-layout.md
 - .ai_infra/docs/decisions/ADR-009-trae-only-edition.md
Notes:
 - `.local/` is gitignored; this file is the versioned contract for what belongs where.
-->

# Folder charter: three planes + kit dev

## Planes (consumer project)

| Plane | Path | Git? | Purpose |
|-------|------|------|---------|
| Trae contract | `.trae/` | Yes | Rules, skills, agents, MCP wiring |
| Infrastructure | `.ai_infra/`, `trae_workflow/` | Yes (slim subset) | Scripts, docs, templates, kit MCP |
| Runtime | `.local/` | No (gitignored) | Trackers, PR artifacts, audits, generated data |
| Overlay | `overlays/rules/` | Yes | Per-project rules merged at install |

## `.ai_infra/` subtrees (consumer copy via manifest)

| Subtree | Purpose |
|---------|---------|
| `docs/operations/` | Runbooks, quickstart, local-workspace layout |
| `docs/governance/` | Charters, drift prevention, module boundaries |
| `docs/roadmap/` | Alignment audit schema |
| `docs/architecture/` | Consumer architecture (`workflow-architecture.md`) |
| `docs/decisions/` | ADR index and decision records |
| `scripts/pr/` | PR workflow scripts (`prepare.py` GATES) |
| `scripts/architecture/` | Governance and layer checks |
| `templates/local-workspace/` | Stubs copied into `.local/` at scaffold |
| `templates/user-settings/` | Exemplars → `.local/user_settings/` |
| `templates/agent-integration/` | Agent/skill templates for integrator |
| `mcp_servers/workflow_mcp/` | Kit MCP server (`default` profile + `mcp_json`) |

**Kit dev only (not copied to consumer by default):**

| Path | Purpose |
|------|---------|
| `tests/` | Kit test suite |
| `docs/handoff/` | Maintainer implementation status (upstream Cursor references) |
| `Makefile`, CI workflows | Kit-dev quality gates |

## `.local/` (local operating workspace)

See [local-workspace-layout.md](../operations/local-workspace-layout.md) for full bucket list.

## Protected local artifacts

Per `.trae/rules/local-artifact-protection.md`: do not delete `.env` secrets or `.coverage` without explicit approval.

## What does not belong in consumer install

- Filled runtime content under `.local/workflow-artifacts/*` (written during slices).
- Product application code — use consumer `overlays/rules/` when needed.
