<!--
File: rules-overlap-matrix.md
Path: .ai_infra/docs/governance/rules-overlap-matrix.md
Role: Inventory of `.trae/rules/*.md` overlaps and merge posture (Trae edition).
Used By:
 - Maintainers changing Trae rules
Depends On:
 - AGENTS.md
 - docs/operations/agent-workflow-procedures.md
Notes:
 - Trae edition: **13** rules under `.trae/rules/` (6 universal + 7 agent-requested).
-->

# Rules overlap matrix (Trae)

## Universal governance (6 — always applied in Trae)

| Rule file | Purpose | Overlap with | Posture |
|-----------|---------|--------------|---------|
| `pr-workflow-enforcement.md` | PR-first, artifacts, merge gates | `workflow-complete.md`, `pr-workflow/SKILL.md` | **Short pointer** to `local_workflow_paths.py` + `prepare.py` `GATES` |
| `implementation-workflow-governance.md` | Slice lifecycle, planning, testing | `agent-implementer.md`, `token-efficiency.md` | **Keep** |
| `advisory-audit-alignment-enforcement.md` | Alignment artifacts (`enterprise-auditor`) | `agent-workflow-procedures.md` | **Keep** |
| `commit-trailer-format.md` | Required commit trailers (`Author` + `GitHub-User` only) | `README.md`, `AGENTS.md` § Commits | **Keep separate** |
| `file-docstring-header-relations.md` | File headers on new sources | All new source files | **Keep** |
| `local-artifact-protection.md` | `.coverage`, `.env` | ops runbooks | **Keep** |

## Agent-requested rules (7 — invoke by name in Trae)

| Rule file | Agent | Posture |
|-----------|-------|---------|
| `agent-implementer.md` | implementer | **Keep** |
| `agent-test-runner.md` | test-runner | **Keep** |
| `agent-verifier.md` | verifier | **Keep** |
| `agent-enterprise-auditor.md` | enterprise-auditor | **Keep** |
| `agent-workflow-drift-guard.md` | workflow-drift-guard | **Keep** |
| `agent-researcher.md` | researcher | **Keep** |
| `agent-integrator-mas-agent.md` | integrator-mas-agent | **Keep** |

## Not in universal core

| Pack | Location | Notes |
|------|----------|-------|
| Product-specific rules | `overlays/rules/*.md` | Copy into target `.trae/rules/` at install — not in core kit |

## Status

- **Inventory:** 13 `.trae/rules/*.md` files tracked in git.
- **Posture:** short invariants + links to `prepare.py`; no duplicated gate command lists in rules.
