<!--
File: trae-consumer-quickstart.md
Path: .ai_infra/docs/operations/trae-consumer-quickstart.md
Role: Trae onboarding for MAS Workflow Kit — Trae edition.
Used By:
 - AGENTS.md
 - README.md
Depends On:
 - ADR-009-trae-only-edition.md
Notes:
 - Trae has no /add-plugin; activate installs .trae/ from payload.
 - This repo is Trae-only; .trae/ is SSOT (not generated from .cursor/).
-->

# Trae consumer quickstart

MAS Workflow Kit for **Trae IDE** — agent rules, skills, MCP, and shared `.local/` trackers.

**Full manual:** [PLUGIN-USER-GUIDE.md](PLUGIN-USER-GUIDE.md)

## Prerequisites

- Python 3.11+
- Trae IDE (macOS or Windows)
- MAS Workflow Kit installed (editable pip + activate)

## 1. Activate

From the **project root** (terminal — not Trae chat):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m trae_workflow activate --directory . --profile default
```

This installs:

| Path | Role |
|------|------|
| `.trae/` | Trae contract plane (rules, skills, agents, MCP) |
| `.ai_infra/`, `trae_workflow/` | Shared scripts (local dev) |
| `.local/` | Trackers and workflow artifacts |

Edit `.local/user_settings/github.collaboration.yaml`, then:

```bash
python3 -m trae_workflow contributors validate
```

**Minimal consumer layout:** see [`examples/consumer-minimal/`](../../../examples/consumer-minimal/) for a reference project tree after activate.

## 2. Trae settings

1. Open the **project folder** in Trae.
2. Enable **Include AGENTS.md** in Trae AI settings (project context).
3. Confirm `.trae/rules/` and `.trae/skills/` load in the rules/skills UI.
4. Verify **workflow-kit** MCP in Trae MCP panel (from `.trae/mcp.json`).

Reload Trae window after MCP config changes.

```bash
python3 -m trae_workflow mcp validate --directory .
```

**Suggested chat invocation:**

```text
Follow the agent-implementer rule in .trae/rules/ and read session-pointer.md first.
```

## 3. Invoke kit agents

Trae has no slash subagents. Use:

- **Agent rules:** `.trae/rules/agent-<id>.md` (e.g. `agent-implementer.md`)
- **MCP:** `workflow://agents/implementer` resource when MCP is connected
- **Canonical prompts:** `.trae/agents/<id>.md`

Read session anchors first every time:

1. `.local/index-and-planning/current/session-pointer.md`
2. `plan.md`
3. `work-tracker.md`

## 4. Gates and PR workflow

Run from terminal:

```bash
python .ai_infra/scripts/pr/prepare.py --pr <url> --actor "Your Name" --agents "implementer"
```

Or use MCP `workflow_run_prepare` when `workflow-kit` is connected.

**Trae maintainer flow:** ask Trae to follow each skill in order:

1. `.trae/skills/review-pr/SKILL.md`
2. `.trae/skills/prepare-pr/SKILL.md`
3. `.trae/skills/merge-pr/SKILL.md`

Architecture-impacting scope: follow `.trae/rules/agent-enterprise-auditor.md` before prepare.

## 5. Upgrade kit

Re-run activate (idempotent):

```bash
python3 -m trae_workflow activate --directory . --profile default
```

Maintainers: `make sync-plugin` refreshes `payload/.trae/` from committed `.trae/` SSOT.

## 6. Verification

| Check | Command |
|-------|---------|
| Trae parity | `make check-trae-parity` |
| Plugin bundle | `make check-plugin` |
| Integration | `python3 -m trae_workflow integrate validate --directory .` |
| MCP | `python3 -m trae_workflow mcp validate --directory .` |
| Full gates | `make gates` |
| Verify-all | `make verify-all` — maintainer matrix (11 steps; see [gate-matrix.md](gate-matrix.md)), includes `check-payload-git` and `contract-json-sync` |
| Acceptance spike | `.local/workflow-artifacts/acceptance/trae-ide-spike.md` |

## Troubleshooting

| Issue | Action |
|-------|--------|
| `.trae/` missing | `activate --profile default` |
| MCP not loading | Check `.trae/mcp.json`; reload window; ensure `.venv` exists |
| Tracker conflicts | One agent owns slice; use git branches |

See also: [README.md](../../../README.md) · [local-workspace-layout.md](local-workspace-layout.md)
