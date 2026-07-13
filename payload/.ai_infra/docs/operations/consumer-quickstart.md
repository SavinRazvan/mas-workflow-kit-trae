<!--
File: consumer-quickstart.md
Path: .ai_infra/docs/operations/consumer-quickstart.md
Role: Redirect stub — Trae edition uses trae-consumer-quickstart.md.
Used By:
 - Legacy links from README and PLUGIN-USER-GUIDE
Depends On:
 - trae-consumer-quickstart.md
Notes:
 - This repository is mas-workflow-kit-trae (Trae-only). Cursor edition: upstream mas-workflow-kit.
-->

# Consumer quickstart

**This repository is the Trae edition.** Use the Trae runbook:

→ **[trae-consumer-quickstart.md](trae-consumer-quickstart.md)** — activate, Trae settings, agents, gates, PR workflow.

**Full manual:** [PLUGIN-USER-GUIDE.md](PLUGIN-USER-GUIDE.md)

---

## Cursor Marketplace edition

If you use **Cursor IDE** with `/add-plugin`, see upstream **[mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit)** — separate repository with `.cursor/` contract plane and plugin install flow.

---

## One-liner (Trae)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m trae_workflow activate --directory . --profile default
```

Then enable **Include AGENTS.md** in Trae and follow `.trae/rules/agent-implementer.md`.
