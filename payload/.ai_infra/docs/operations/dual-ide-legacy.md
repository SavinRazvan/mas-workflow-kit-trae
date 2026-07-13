<!--
File: dual-ide-legacy.md
Path: .ai_infra/docs/operations/dual-ide-legacy.md
Role: Documents dormant dual-IDE code paths in the Trae-only edition.
Used By:
 - README.md
 - enterprise-auditor alignment
Depends On:
 - ADR-009-trae-only-edition.md
 - ide_contract_paths.py
-->

# Dual-IDE legacy (Trae edition)

This repository is **Trae-only** per [ADR-009](../decisions/ADR-009-trae-only-edition.md). Contract SSOT is committed `.trae/` — not generated from `.cursor/` at install time.

## When dual-IDE code is dormant

[`ide_contract_paths.uses_trae_ssot()`](../../ide_contract_paths.py) returns **true** when:

- Activate profile is `default`, or
- `.cursor/rules/*.mdc` is absent (Trae edition kit-dev)

When true:

- **DRIFT-009** skips Cursor ↔ Trae rule count parity ([`drift_checks.py`](../../scripts/workflow/drift_checks.py))
- **MCP merge** targets `.trae/mcp.json` only
- **Doc facts** read agent/rule counts from `.trae/`

## Upstream parity code (retained, not deleted)

| Component | Role |
|-----------|------|
| `sync_trae_contract.py` | Generate `.trae/` from `.cursor/` for upstream mas-workflow-kit |
| `DUAL_IDE_PROFILE` (`dual_ide`) | Explicit profile when both planes are active |
| `check_trae_parity.py` | Regression tests for sync pipeline |

These paths support **upstream** dual-IDE development. They are **not** used in normal Trae edition consumer or kit-dev workflows.

## Contributor guidance

- Edit **`.trae/`** only for contract changes in this repo.
- Run **`make sync-plugin`** after contract JSON edits.
- Do not copy overlays to `.cursor/rules/` — see install README Trae edition banner.
- Optional cleanup: `make clean-legacy-contract` removes gitignored `.cursor/` trees locally.

## Accepted divergence

EA-011 / ALIGN: intentional retention per ADR-009 §5. Future **SCORE-DIST** or upstream sync may trim unused branches; deletion is out of scope for Trae edition unless upstream parity tests move to mas-workflow-kit.
