<!--
File: workflow-source-owners.md
Path: .ai_infra/docs/governance/workflow-source-owners.md
Role: Canonical ownership map for workflow surfaces (scripts vs docs vs agents).
Used By:
 - .ai_infra/docs/governance/README.md
 - Maintainers resolving conflicts between README, rules, and skills
Depends On:
 - .ai_infra/docs/operations/workflow-complete.md
 - .ai_infra/scripts/pr/prepare.py
 - .ai_infra/scripts/pr/local_workflow_paths.py
Notes:
 - Trae edition: contract plane is `.trae/` (ADR-009).
 - Executable behavior wins over prose; prose must link to scripts instead of copying steps.
-->

# Workflow source owners

| Concern | Canonical owner | Consumers |
|---------|-----------------|-----------|
| Prepare gate **order** and commands | `.ai_infra/scripts/pr/prepare.py` (`GATES`) | Rules, skills, `workflow-complete.md`, `AGENTS.md` |
| PR artifact **paths** | `.ai_infra/scripts/pr/local_workflow_paths.py` | `review.py`, `prepare.py`, `merge.py`, rules |
| PR publish verification | `.ai_infra/scripts/pr/verify_publish.py` | Pre-PR branch health |
| Merge preconditions | `.ai_infra/scripts/pr/merge.py` | `merge-pr` skill |
| Post-merge cleanup | `.ai_infra/scripts/pr/finalize.py` | `merge-pr` skill |
| Maintainer PR narrative order | `.trae/skills/pr-workflow/SKILL.md` → `review-pr` / `prepare-pr` / `merge-pr` | Humans + Trae agents |
| Trae contract skills | `.trae/skills/` (15 folders) | Activate bundle, agents |
| Trae agent prompts | `.trae/agents/*.md` | Trae chat + MCP resources |
| Trae agent-requested rules | `.trae/rules/agent-*.md` | Invoked by agent name in Trae |
| Universal governance rules | `.trae/rules/*.md` (6 always-applied) | All Trae sessions |
| Durable maintainer checklist | `.ai_infra/docs/operations/workflow-complete.md` | Everyone (versioned) |
| Audit / dedup rules | `.ai_infra/docs/operations/agent-workflow-procedures.md` | Alignment + governance |
| Alignment finding shape | `.ai_infra/docs/roadmap/alignment-audit-schema.md` | `enterprise-auditor` focused pass |
| Full enterprise audit outputs | `.trae/skills/enterprise-architecture-audit/SKILL.md` → `.local/workflow-artifacts/enterprise-architecture-audit/` | Deep audits |
| Focused alignment outputs | Same skill § focused pass → `.local/workflow-artifacts/alignment/` | Architecture-impacting PRs |
| Git **commit** trailers | `.trae/rules/commit-trailer-format.md` | `AGENTS.md` § Commits |
| Governance drift scan | `.ai_infra/scripts/architecture/check_governance_consistency.py` | CI + local policy edits |
| Operational drift validate | `.ai_infra/scripts/workflow/check_drift.py` | `make drift-validate`, implementer closure |
| Infrastructure integrate validate | `.ai_infra/scripts/integration/validate.py` | `make integrate-validate`, INT-001…014 |
| Three-plane activate | `.ai_infra/install/trae_workflow/activate_cli.py` | `workflow-activate` skill, MCP `workflow_activate` |
| Path resolution | `.ai_infra/paths.py` | MCP, install scaffold, tests |
| MCP registry mapping | `.trae/mcp.registry.yaml` | Agents, `connect-external-mcp.md` |
| External MCP connect procedure | `.ai_infra/docs/operations/connect-external-mcp.md` | Users + agents |
| Repository orientation | `AGENTS.md`, `README.md` | All agents |

> **Upstream Cursor edition:** [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) uses `.cursor/` + `.agents/` — not shipped from this repo.

**Rule:** If text disagrees with `prepare.py` or `local_workflow_paths.py`, update the text in the **same PR** as the script change, or immediately after.

**PR artifacts vs git commits:** `.local/workflow-artifacts/pr/*.md` use `Action-By` / `Prepared-By` headers. Git commits use `Author:` / `GitHub-User:` only per commit-trailer rule — never conflate the two.
