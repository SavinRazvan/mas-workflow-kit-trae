<!--
File: workflow-architecture.md
Path: .ai_infra/docs/architecture/workflow-architecture.md
Role: Canonical consumer-facing architecture overview (three planes, agents, Pattern A gates).
Used By:
 - README.md
 - Onboarding
Depends On:
 - .ai_infra/docs/decisions/README.md
Notes:
 - Consumer-facing; maintainer deep-dive: `.ai_infra/docs/handoff/PLUGIN-ARCHITECTURE.md` (kit-dev only).
-->

# Workflow architecture (MAS Workflow Kit)

## Planes

| Plane | Path | Purpose |
|-------|------|---------|
| IDE contract (Trae, SSOT) | `.trae/` | Rules, skills, agent rules, MCP — editable SSOT in Trae edition ([ADR-009](../decisions/ADR-009-trae-only-edition.md)) |
| IDE contract (Cursor, upstream) | `.cursor/`, `.agents/` | Agents, skills, rules — SSOT in upstream kit-dev |
| Infrastructure | `.ai_infra/` | Scripts, docs, templates, MCP |
| Runtime | `.local/` | Trackers, PR artifacts, audits (see [Artifact tiers](../operations/local-workspace-layout.md#artifact-tiers)) |

**Trae edition:** activate with `--profile default` installs `.trae/` contract plane. Trae users: [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md).

**Dual IDE (upstream):** activate with `--profile default` installs both `.cursor/` and `.trae/` per [ADR-008](../decisions/ADR-008-dual-ide-contract-plane.md).

**Install** scaffolds Tier 1 base paths (trackers, `workflow-artifacts/*` buckets, README stubs). Agents and PR scripts write Tier 2 runtime content during work. Path SSOT: `.ai_infra/scripts/pr/local_workflow_paths.py`.

## Activation

Enabling the **plugin** loads agents/skills/rules in the IDE only — it does **not** write files to your project. Run activate to install all three planes on disk:

1. **Plugin from GitHub (recommended):** Agent chat → `/add-plugin https://github.com/SavinRazvan/mas-workflow-kit` → open your app → **`/workflow-activate`** (or `python -m trae_workflow activate --directory .`)
2. **Marketplace (when listed):** same flow after **Cursor → Marketplace** install
3. **Kit clone / advanced:** `python -m trae_workflow install --target . --verify`

See [PLUGIN-USER-GUIDE.md](../operations/PLUGIN-USER-GUIDE.md) §1 for the plugin-vs-disk diagram and file tree.

## Pattern A (maintainer PR)

Hub: `.agents/skills/pr-workflow/SKILL.md` → `review-pr` → `prepare-pr` (`prepare.py` GATES) → `merge-pr` → `finalize.py`

Gate order: read `.ai_infra/scripts/pr/prepare.py` only — do not duplicate here.

## Anchoring

Every session: `.local/index-and-planning/current/session-pointer.md` → `plan.md` → `work-tracker.md`.

## Core agents (kit)

| Agent | Role |
|-------|------|
| `implementer` | Slices, code, trackers |
| `test-runner` | Module tests, coverage |
| `verifier` | Evidence checks |
| `enterprise-auditor` | Architecture audits |
| `researcher` | Research corpus (local) |
| `integrator-mas-agent` | Add agents/skills/MCP to infrastructure |
| `workflow-drift-guard` | Operational drift (plan ↔ tracker ↔ docs) — [ADR-007](../decisions/ADR-007-workflow-drift-guard.md) |

Integration procedure: [mas-infrastructure-integration.md](../operations/mas-infrastructure-integration.md).  
Drift validation: `make drift-validate` — see [gate-matrix.md](../operations/gate-matrix.md).

## Skills layout

| Root | Contents |
|------|----------|
| `.cursor/skills/` | Canonical protocols: `enterprise-architecture-audit`, `workflow-drift-audit`, `implementation-execution-loop`, `workflow-activate`, … |
| `.agents/skills/` | Maintainer slash skills: `review-pr`, `prepare-pr`, `merge-pr`, `pr-workflow`, `audit-alignment` (redirect) |

Plugin bundle copies `.cursor/skills/` first; maintainer skills are **additive only** (no overwrite).

See [folder-charter.md](../governance/folder-charter.md) and [decisions/README.md](../decisions/README.md).
