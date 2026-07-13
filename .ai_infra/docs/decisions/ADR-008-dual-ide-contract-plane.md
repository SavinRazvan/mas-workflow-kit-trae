# ADR-008: Dual IDE contract plane (Cursor + Trae)

**Status:** accepted  
**Date:** 2026-07-12

## Context

MAS Workflow Kit ships a **Cursor contract plane** (`.cursor/`, `.agents/`) via Marketplace plugin and `payload/.cursor/` activate source (ADR-001, ADR-003). Consumers increasingly want **parallel Cursor + Trae** on the same repo with identical rules, skills, and agent prompt text — without replacing Cursor.

Trae uses `.trae/rules/*.md`, `.trae/skills/`, and `.trae/mcp.json` (not `.cursor/` paths). Trae contract plane is generated per ADR-008 (`sync_trae_contract`); kit-dev and dual_ide consumers ship `.trae/` from activate.

## Decision

1. **SSOT (human edits):** kit-dev `.cursor/` + `.agents/` only.
2. **Generated Trae plane:** `.trae/` is produced by `sync_trae_contract` in the release pipeline — never hand-edited; files carry a `GENERATED — do not edit` banner.
3. **Cursor distribution unchanged:** plugin surface (`agents/`, `rules/`, `skills/`) + `payload/.cursor/` remain the Cursor activate path.
4. **Trae distribution:** `payload/.trae/` copied on activate with `--profile dual_ide`.
5. **Shared planes:** infrastructure (`.ai_infra/`, `cursor_workflow/`) and runtime (`.local/`) are IDE-agnostic.
6. **Path resolver:** `.ai_infra/ide_contract_paths.py` centralizes IDE-specific paths for scripts and MCP.
7. **Agent personas in Trae:** generated `.trae/rules/agent-<id>.md` (agent-requested mode) plus `.trae/agents/<id>.md` copies for MCP `workflow://agents/{id}` — not Cursor subagent delegation.

## Non-goals

- Renaming `cursor_workflow` package in v1.
- 1:1 slash-command or Task subagent UX in Trae (Trae SOLO Coder ≠ kit slice orchestration).
- Trae Marketplace plugin (distribution is sync + activate only in v1).

## Consequences

- `make sync-plugin` emits both Cursor plugin surface and `.trae/` dev mirror + `payload/.trae/`.
- New manifest profile `dual_ide` extends `with_mcp` with `.trae` copy_dirs.
- `install-contract.json` gains `dual_ide` required_paths under `.trae/`.
- `plane_status.py` reports `trae_contract` when profile is `dual_ide`.
- `mcp_manage.py` can emit merged MCP JSON for both `.cursor/` and `.trae/`.
- `check_trae_parity.py` gates contract-plane drift in kit-dev CI.
- ADR-003 consequences amended: plugin = Cursor contract; Trae contract = generated sibling plane.

## Related

- [ADR-001](ADR-001-distribution-activation.md) — activate payload layout
- [ADR-003](ADR-003-plugin-mcp-boundaries.md) — plugin vs MCP
- [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md) — Trae onboarding
