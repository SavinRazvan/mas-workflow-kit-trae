<!--
File: drift-prevention.md
Path: .ai_infra/docs/governance/drift-prevention.md
Role: Lightweight process to keep docs, `.local` layout docs, and script-first workflow aligned.
Used By:
 - .ai_infra/docs/governance/README.md
Depends On:
 - .ai_infra/scripts/pr/prepare.py
 - .ai_infra/scripts/architecture/check_governance_consistency.py
Notes:
 - Trae edition: contract plane `.trae/` (ADR-009).
-->

# Drift prevention (lightweight)

## Default merge gates (canonical)

Order and commands: **`.ai_infra/scripts/pr/prepare.py`** (`GATES`) only — **do not list** commands here; run `prepare.py` or read that file.

Additionally when changing governance, workflows, **`.trae/`**, or tracked policy docs: **`python .ai_infra/scripts/architecture/check_governance_consistency.py`**.

## After changing workflow gates or artifact paths

1. Update **`.ai_infra/scripts/pr/prepare.py`** (`GATES`) if commands change.
2. Update **`.trae/rules/pr-workflow-enforcement.md`** (short pointers only — no long gate lists in chat).
3. Update **`.ai_infra/docs/operations/workflow-complete.md`** and **`agent-workflow-procedures.md`** if checklist text references paths or commands.
4. Update **`README.md`** / **`AGENTS.md`** if onboarding paths change.
5. Run **`check_governance_consistency.py`** and targeted tests.

## After changing documentation lifecycle

1. Update **`.ai_infra/docs/governance/workflow-source-owners.md`** if ownership moved.
2. Run **documentation-maintenance-checklist.md** for kit doc surfaces (kit-dev).

## After changing `.local` layout

1. Update **`.ai_infra/docs/operations/local-workspace-layout.md`**.
2. Update **`.ai_infra/scripts/pr/local_workflow_paths.py`** (and `review.py` / `prepare.py` / `merge.py` consumers).
3. Refresh **`.local/agents-control-center/config/pages.json`** if dashboard tabs change.

## After changing **git commit** trailer policy

Follow **`agent-workflow-procedures.md` §3b**. Includes **`AGENTS.md`**, **`rules-overlap-matrix.md`**, **`workflow-source-owners.md`**, PR scripts, and mirrored **`.trae/skills/`**. Run **`check_governance_consistency.py`** when tracked policy paths change.

## Operational drift (workflow-drift-guard)

Script-first checks for plan ↔ tracker ↔ session-pointer coherence. See [ADR-007](../decisions/ADR-007-workflow-drift-guard.md).

**Kit-dev PR prep:** `prepare.py` auto-runs `drift validate`. Optional: **`workflow-drift-guard`** to refresh `.local/workflow-artifacts/drift/` artifacts.

| Concern | Owner | Do NOT duplicate in drift |
|---------|-------|---------------------------|
| Bare paths, brand terms | `check_governance_consistency.py`, `check_debrand.py` | Path/brand scans |
| Agent Anchor/MCP, registry parity | `integrate validate` INT-001…014 | Agent file structure |
| Canonical doc facts (roster, counts) | `check_doc_facts.py` / INT-013 | Path/brand scans |
| test-plan/index existence | `check_testing_artifacts.py` | File exists checks |
| Plugin/payload SHA drift | `sync_plugin_bundle.py --check` | Bundle sync |
| Architecture scorecard | `enterprise-auditor` | Module deep-dive |

**Command:** `python3 -m trae_workflow drift validate --directory .` or `make drift-validate`.

**Artifacts:** `.local/workflow-artifacts/drift/drift-audit.md`, `drift-todos.md`.

## Quarterly (or before kit releases)

- Confirm **`rules-overlap-matrix.md`** lists all **`.trae/rules/*.md`** files.
- Re-run **`make gates`**, **`make drift-validate`**, and **`make install-dry-run`** on the kit repo.
