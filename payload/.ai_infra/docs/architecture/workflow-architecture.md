<!--
File: workflow-architecture.md
Path: .ai_infra/docs/architecture/workflow-architecture.md
Role: Canonical consumer-facing architecture overview (three planes, agents, Pattern A gates).
Used By:
 - README.md
 - Onboarding
Depends On:
 - .ai_infra/docs/decisions/ADR-009-trae-only-edition.md
Notes:
 - Trae edition consumer-facing architecture.
-->

# Workflow architecture (MAS Workflow Kit for Trae)

## Planes

| Plane | Path | Purpose |
|-------|------|---------|
| Trae contract (SSOT) | `.trae/` | Rules, skills, agents, MCP — editable SSOT ([ADR-009](../decisions/ADR-009-trae-only-edition.md)) |
| Infrastructure | `.ai_infra/`, `trae_workflow/` | Scripts, docs, templates, MCP server |
| Runtime | `.local/` | Trackers, PR artifacts, audits (see [Artifact tiers](../operations/local-workspace-layout.md#artifact-tiers)) |

**Activate:** `python3 -m trae_workflow activate --directory . --profile default` installs all three planes. See [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md).

> **Upstream Cursor edition:** [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) uses plugin install + `.cursor/` — separate repository.

**Install** scaffolds Tier 1 base paths (trackers, `workflow-artifacts/*` buckets). Agents and PR scripts write Tier 2 runtime content during work. Path SSOT: `.ai_infra/scripts/pr/local_workflow_paths.py`.

## Pattern A (maintainer PR)

Hub: `.trae/skills/pr-workflow/SKILL.md` → `review-pr` → `prepare-pr` (`prepare.py` GATES) → `merge-pr` → `finalize.py`

Gate order: read `.ai_infra/scripts/pr/prepare.py` only — do not duplicate here.

## Anchoring

Every session: `.local/index-and-planning/current/session-pointer.md` → `plan.md` → `work-tracker.md`.

## Core agents (kit)

| Agent | Trae invocation | Role |
|-------|-----------------|------|
| `implementer` | `.trae/rules/agent-implementer.md` | Slices, code, trackers |
| `test-runner` | `.trae/rules/agent-test-runner.md` | Module tests, coverage |
| `verifier` | `.trae/rules/agent-verifier.md` | Evidence checks |
| `enterprise-auditor` | `.trae/rules/agent-enterprise-auditor.md` | Architecture audits |
| `researcher` | `.trae/rules/agent-researcher.md` | Research corpus (local) |
| `integrator-mas-agent` | `.trae/rules/agent-integrator-mas-agent.md` | Add agents/skills/MCP |
| `workflow-drift-guard` | `.trae/rules/agent-workflow-drift-guard.md` | Operational drift — [ADR-007](../decisions/ADR-007-workflow-drift-guard.md) |

Integration: [mas-infrastructure-integration.md](../operations/mas-infrastructure-integration.md).  
Drift: `make drift-validate` — [gate-matrix.md](../operations/gate-matrix.md).

## Skills layout

| Root | Contents |
|------|----------|
| `.trae/skills/` | 15 protocol skills: `workflow-activate`, `enterprise-architecture-audit`, `workflow-drift-audit`, `implementation-execution-loop`, `review-pr`, `prepare-pr`, `merge-pr`, `pr-workflow`, … |

Activate bundle: `make sync-plugin` refreshes `payload/.trae/` from committed `.trae/` SSOT.

See [folder-charter.md](../governance/folder-charter.md) and [decisions/README.md](../decisions/README.md).
