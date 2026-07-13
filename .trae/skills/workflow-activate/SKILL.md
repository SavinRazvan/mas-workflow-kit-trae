---
name: workflow-activate
description: Install MAS Workflow Kit (Trae edition) into the current workspace (ADR-001 Option B).
---
<!--
File: SKILL.md
Path: .trae/skills/workflow-activate/SKILL.md
Role: Install MAS Workflow Kit three planes into the open workspace (Trae edition).
Used By:
 - PLUGIN-ARCHITECTURE.md
 - sync_plugin_bundle.py
Depends On:
 - .ai_infra/install/trae_workflow/activate_cli.py
Notes:
 - Pattern A: one script command per action.
 - Trae edition: no Cursor plugin or slash subagents.
-->

# Workflow activate (Trae edition)

## When

User opened **their project** (not the kit-dev repo) and needs workflow infrastructure installed or refreshed.

## Guide the user (keep it simple)

1. Confirm the open folder is **their app**, not `mas-workflow-kit-trae`.
2. Run activate (below) from terminal with venv active.
3. Tell them to edit `.local/user_settings/github.collaboration.yaml` → `contributors validate`.
4. Enable **Include AGENTS.md** in Trae AI settings.
5. Point them to `session-pointer.md` and `.trae/rules/agent-implementer.md`.

Do **not** dump gate lists or maintainer `make` commands.

## One command

From the **open workspace** (Pattern A — one script command):

```bash
python3 -m trae_workflow activate --directory . --profile default
```

**Auto source resolution:** `WORKFLOW_KIT_PAYLOAD` env → `./payload/` → kit `payload/`. Override with `--source /path/to/payload`.

**MCP:** `workflow_activate` on the `workflow-kit` server (same behavior).

Full runbook: [trae-consumer-quickstart.md](../../.ai_infra/docs/operations/trae-consumer-quickstart.md)

## What `activate` does

| Plane | Paths installed | Trae loads? |
|-------|-----------------|-------------|
| Trae contract | `.trae/` (rules, skills, agents, MCP) | Yes |
| Infrastructure | `.ai_infra/`, `trae_workflow/` | No — scripts/CLI |
| Runtime | `.local/` Tier 1 scaffold: trackers, `workflow-artifacts/*` buckets, dashboards | No — gitignored |

Tier 1 paths are created on first install; Tier 2 runtime `.md` files appear when agents/scripts run. See [local-workspace-layout.md](../../.ai_infra/docs/operations/local-workspace-layout.md).

- Idempotent: skips full install when all planes already pass `install-contract.json`, but still refreshes dashboards
- Creates `.venv`, merges MCP json, runs verify gates when requested
- Prints **settings-only** next steps (no re-install)

**MCP config files:** Examples (`mcp.json.kit.example`, `mcp.registry.yaml.example`, `mcp.user.example.json`) install under `.trae/` from **payload** when `activate` runs. Use skill **connect-external-mcp** after activate.

## Post-activate (tell the user)

1. Open `.local/user_settings/github.collaboration.yaml` — set **display_name** and **github_user**
2. Terminal: `source .venv/bin/activate && python3 -m trae_workflow contributors validate` (must PASS before git/PR)
3. Read `session-pointer.md` · ask Trae to follow `.trae/rules/agent-implementer.md`

**Dashboards (optional):** from project root run `python3 -m http.server 8000`, then open
http://localhost:8000/.local/agents-control-center/dashboards/index.html (not `file://`).

Optional: `integrate validate`, `health`. Add infrastructure later: `.trae/rules/agent-integrator-mas-agent.md`.

## Adding agents/skills/MCP later

Ask Trae to follow `.trae/rules/agent-integrator-mas-agent.md` with skill `.trae/skills/mas-infrastructure-integration/SKILL.md` — not shell commands.

## Maintainer (kit-dev repo only)

```bash
make sync-plugin    # refresh payload/.trae + payload/trae_workflow
make check-plugin
make gates
```

See [ADR-009](../../.ai_infra/docs/decisions/ADR-009-trae-only-edition.md).
