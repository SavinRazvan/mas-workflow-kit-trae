# ADR-009: Trae-only edition (`.trae/` SSOT)

**Status:** accepted  
**Date:** 2026-07-13

## Context

[ADR-008](ADR-008-dual-ide-contract-plane.md) defines dual-IDE kit-dev: `.cursor/` + `.agents/` are SSOT; `.trae/` is generated with `GENERATED` banners. The **mas-workflow-kit-trae** repository is a Trae edition fork — consumers use Trae IDE only, not Cursor Marketplace plugin distribution.

Maintaining Cursor-first SSOT in a Trae-only repo creates drift, confusing docs, and unnecessary `.cursor/` dependency for parity gates.

## Decision

1. **Trae edition SSOT:** committed `.trae/` is authoritative for rules, skills, agents, and MCP in this repository.
2. **Install profile:** `default` (default in Makefile) copies `.trae/` + `trae_workflow/` + `.ai_infra/` — no `.cursor/` or `.agents/` on activate.
3. **Release pipeline:** `make sync-plugin` copies `.trae/` → `payload/.trae/` with path rewrites only; no `GENERATED` banners.
4. **Parity gate:** `check_trae_parity.py` compares committed `.trae/` to temp sync output (not regen from `.cursor/`).
5. **Dual-IDE code paths retained:** `sync_trae_contract_from_cursor` and `dual_ide` profile remain for upstream parity; gated via `ide_contract_paths.DUAL_IDE_PROFILE` and `uses_trae_ssot()` — unused in this repo.
6. **Upstream unchanged:** [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) Cursor edition keeps ADR-008 Cursor-first SSOT.

## Consequences

- `ide_contract_paths.uses_trae_ssot()` returns true when profile is `default` or `.cursor/rules` absent.
- `install-contract.json` gains standalone `default` required_paths under `.trae/`.
- `plane_status.py` requires Trae contract, not Cursor, for `default`.
- README, AGENTS, and trae-consumer-quickstart are Trae-first.
- INT-008 integration check accepts `default` manifest with `.trae` in `copy_dirs_replace`.

## Related

- [ADR-008](ADR-008-dual-ide-contract-plane.md) — dual-IDE (upstream)
- [ADR-001](ADR-001-distribution-activation.md) — activate payload layout
- [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md)
