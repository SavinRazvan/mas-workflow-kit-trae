# MAS Workflow Kit

Multi-agent workflow infrastructure for **Cursor** and **Trae** — subagents (Cursor), agent rules (Trae), skills, governance rules, PR scripts, and `.local/` trackers.

Install into **your** project (not a standalone app). This repo is a **kit-dev** workspace with dual-IDE (`dual_ide`) support per [ADR-008](.ai_infra/docs/decisions/ADR-008-dual-ide-contract-plane.md).

> `_example_repo/` is a temporary Cursor reference checkout (informative only) — not a runtime dependency.

## Quick navigation

| Audience | Start here |
|----------|------------|
| **Cursor user** | [Consumer quickstart](.ai_infra/docs/operations/consumer-quickstart.md) · `/add-plugin` → `/workflow-activate` |
| **Trae user** | [Trae consumer quickstart](.ai_infra/docs/operations/trae-consumer-quickstart.md) · `activate --profile dual_ide` |
| **Full manual** | [PLUGIN-USER-GUIDE](.ai_infra/docs/operations/PLUGIN-USER-GUIDE.md) |
| **Kit maintainer** | [Developing the kit](#developing-the-kit) below |

---

## Get started — Cursor

1. **Agent chat:** `/add-plugin https://github.com/SavinRazvan/mas-workflow-kit`
2. Open **your app folder** → `/workflow-activate`
3. Edit `.local/user_settings/github.collaboration.yaml` → `python3 -m cursor_workflow contributors validate`
4. `/implementer` — read `session-pointer.md` → `plan.md` → `work-tracker.md`

Default activate profile: `with_mcp` (Cursor contract plane).

---

## Get started — Trae (parallel IDE)

Trae has no `/add-plugin`. From **your project root** (terminal):

```bash
python3 -m cursor_workflow activate --directory . --profile dual_ide
```

Then in Trae:

1. Enable **Include AGENTS.md** in Trae settings
2. Confirm `.trae/rules/` (13) and `.trae/skills/` (15) load
3. Connect **workflow-kit** MCP from `.trae/mcp.json`

**Invoke agents:** ask Trae to follow `.trae/rules/agent-implementer.md` (no `/implementer` slash).

Full runbook: [trae-consumer-quickstart.md](.ai_infra/docs/operations/trae-consumer-quickstart.md)

---

## What you get (dual IDE)

**Agents (7):** `implementer`, `test-runner`, `verifier`, `enterprise-auditor`, `integrator-mas-agent`, `workflow-drift-guard`, `researcher`

**6 universal rules** in `.cursor/rules/` (synced to `.trae/rules/` as `.md`).

| Piece | Cursor | Trae |
|-------|--------|------|
| Subagents / agent rules | `.cursor/agents/` (7) | `.trae/agents/` + `agent-*.md` rules |
| Skills | `.cursor/skills/` (10) + `.agents/skills/` (5) | `.trae/skills/` (15, generated) |
| MCP | `.cursor/mcp.json` | `.trae/mcp.json` |
| Shared | `.ai_infra/`, `cursor_workflow/`, `.local/` | same |

`.trae/` is **generated** from `.cursor/` SSOT — do not hand-edit; run `make sync-plugin` in kit-dev.

---

## Verify (kit-dev / this repo)

```bash
source .venv/bin/activate
make check-trae-parity
make check-plugin
make test
python3 -m cursor_workflow gates
python3 -m cursor_workflow integrate validate --directory .
python3 -m cursor_workflow mcp validate --directory .
```

---

## Developing the kit

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev,mcp]"
make sync-plugin          # regen .trae/ + payload/ (profile=dual_ide)
make gates
```

**Docs:** [workflow-architecture.md](.ai_infra/docs/architecture/workflow-architecture.md) · [ADR index](.ai_infra/docs/decisions/README.md) · [AGENTS.md](AGENTS.md)

## License

Apache 2.0 — see upstream [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) when published.
