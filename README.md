# MAS Workflow Kit for Trae

Multi-agent workflow infrastructure for **Trae IDE** — agent rules, skills, governance, PR scripts, MCP, and `.local/` trackers.

Install into **your** project (not a standalone app). This repository is the **Trae edition** kit-dev workspace: `.trae/` is the contract-plane SSOT per [ADR-009](.ai_infra/docs/decisions/ADR-009-trae-only-edition.md).

> Upstream [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) remains the Cursor Marketplace edition (dual-IDE). This fork is Trae-only.

## Quick navigation

| Audience | Start here |
|----------|------------|
| **Trae user** | [Trae consumer quickstart](.ai_infra/docs/operations/trae-consumer-quickstart.md) · `activate --profile default` |
| **Full manual** | [PLUGIN-USER-GUIDE](.ai_infra/docs/operations/PLUGIN-USER-GUIDE.md) |
| **Kit maintainer** | [Developing the kit](#developing-the-kit) below |

---

## Get started — Trae

From **your project root** (terminal):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m trae_workflow activate --directory . --profile default
```

Then in Trae:

1. Enable **Include AGENTS.md** in Trae AI settings
2. Confirm `.trae/rules/` (13) and `.trae/skills/` (15) load
3. Connect **workflow-kit** MCP from `.trae/mcp.json`
4. Edit `.local/user_settings/github.collaboration.yaml` → `python3 -m trae_workflow contributors validate`

**Invoke agents:** ask Trae to follow `.trae/rules/agent-implementer.md` (no slash subagents).

Full runbook: [trae-consumer-quickstart.md](.ai_infra/docs/operations/trae-consumer-quickstart.md)

---

## What you get

**Agents (7):** `implementer`, `test-runner`, `verifier`, `enterprise-auditor`, `integrator-mas-agent`, `workflow-drift-guard`, `researcher`

**6 universal governance rules** in `.trae/rules/` (plus 7 agent-requested rules).

| Piece | Path |
|-------|------|
| Agent rules | `.trae/rules/agent-*.md` |
| Agent prompts | `.trae/agents/*.md` |
| Skills | `.trae/skills/` (15) |
| Governance rules | `.trae/rules/*.md` (13) |
| MCP | `.trae/mcp.json` |
| Shared scripts | `.ai_infra/`, `trae_workflow/` |
| Runtime trackers | `.local/` |

`.trae/` is **editable SSOT** in this repo — not generated from `.cursor/`. Run `make sync-plugin` to refresh `payload/.trae/` for activate.

---

## Verify (kit-dev / this repo)

```bash
source .venv/bin/activate
make check-trae-parity
make check-plugin
make test
python3 -m trae_workflow gates
python3 -m trae_workflow integrate validate --directory .
python3 -m trae_workflow mcp validate --directory .
```

---

## Developing the kit

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev,mcp]"
make sync-plugin          # regen payload/.trae/ (profile=default)
make gates
```

### Contract plane (kit-dev)

- **SSOT:** edit [`.trae/`](.trae/) only — agents, skills, rules, MCP config.
- **Payload:** `make sync-plugin` copies committed `.trae/` → `payload/.trae/` (run after editing `.trae/mcp.json` or other contract JSON — `make check-plugin` fails on payload drift).
- **Legacy trees:** `.cursor/`, `.agents/`, `.cursor-plugin/` are **gitignored** remnants from upstream Cursor kit-dev. Do not edit them; they may drift from `.trae/`. Safe to remove locally:

```bash
make clean-legacy-contract   # removes gitignored .cursor/ .agents/ .cursor-plugin/
```

If you use **Cursor IDE** in this repo, load skills from `.trae/skills/`, not `.cursor/skills/`.

**Dual-IDE legacy:** upstream parity helpers (`sync_trae_contract`, `dual_ide` profile) are dormant when Trae SSOT is active — see [dual-ide-legacy.md](.ai_infra/docs/operations/dual-ide-legacy.md).

**Docs:** [workflow-architecture.md](.ai_infra/docs/architecture/workflow-architecture.md) · [ADR index](.ai_infra/docs/decisions/README.md) · [AGENTS.md](AGENTS.md)

## License

Apache 2.0 — see upstream [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) when published.
