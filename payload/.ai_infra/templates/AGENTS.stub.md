# AGENTS.md

## Installing (Trae edition)

From terminal in **your project root**:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m trae_workflow activate --directory . --profile default
```

Full runbook: [trae-consumer-quickstart.md](.ai_infra/docs/operations/trae-consumer-quickstart.md)

## Just installed?

1. Edit `.local/user_settings/github.collaboration.yaml` → your name + `@handle`
2. `source .venv/bin/activate && python3 -m trae_workflow contributors validate`
3. Read `.local/index-and-planning/current/session-pointer.md` → `plan.md` → `work-tracker.md`
4. Invoke agents by name — e.g. ask Trae to follow `.trae/rules/agent-implementer.md` (agents: `implementer`, `test-runner`, `verifier`, `enterprise-auditor`, `integrator-mas-agent`, `workflow-drift-guard`, `researcher`)

### Trae first run

1. `python3 -m trae_workflow activate --directory . --profile default` (terminal)
2. Enable **Include AGENTS.md** in Trae AI settings
3. Same YAML + `contributors validate` as above
4. Invoke agents via `.trae/rules/agent-<id>.md` or `.trae/agents/<id>.md`

**Dashboards (optional):** from project root:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000/.local/agents-control-center/dashboards/index.html *(not `file://`)*.

Full walkthrough: [PLUGIN-USER-GUIDE.md](.ai_infra/docs/operations/PLUGIN-USER-GUIDE.md) · [trae-consumer-quickstart.md](.ai_infra/docs/operations/trae-consumer-quickstart.md)

---

## Project intent

**MAS Workflow Kit for Trae** — multi-agent workflow for Trae IDE. Agents call **one script command** per maintainer action; `GATES` live in `.ai_infra/scripts/pr/prepare.py`.

## First reads

1. [`.ai_infra/docs/operations/trae-consumer-quickstart.md`](.ai_infra/docs/operations/trae-consumer-quickstart.md)
2. [`.ai_infra/docs/operations/PLUGIN-USER-GUIDE.md`](.ai_infra/docs/operations/PLUGIN-USER-GUIDE.md)
3. [`.ai_infra/docs/operations/local-workspace-layout.md`](.ai_infra/docs/operations/local-workspace-layout.md) — artifact tiers
4. [`.ai_infra/docs/operations/token-efficiency.md`](.ai_infra/docs/operations/token-efficiency.md)
5. `.local/index-and-planning/current/session-pointer.md` → `plan.md` → `work-tracker.md`

## Rules (always applied in Trae)

| Rule | Topic |
|------|--------|
| `.trae/rules/implementation-workflow-governance.md` | Slice lifecycle, trackers, tests |
| `.trae/rules/pr-workflow-enforcement.md` | PR-first, artifacts, branch safety |
| `.trae/rules/commit-trailer-format.md` | Commit trailers + optional `Assisted-by` |
| `.trae/rules/file-docstring-header-relations.md` | **File headers** on new sources |
| `.trae/rules/local-artifact-protection.md` | Protected paths (`.coverage`, `.env`) |
| `.trae/rules/advisory-audit-alignment-enforcement.md` | Architecture audits → alignment artifacts |

## Commits

Required trailers: `.trae/rules/commit-trailer-format.md` — set identity in `github.collaboration.yaml`, then `python3 -m trae_workflow contributors validate`.

## Quality gates

`GATES` in `.ai_infra/scripts/pr/prepare.py` — say *prepare gates green* in chat; do not paste full gate lists.
