# Test Index

## Format

- Module: `<source module or area>`
- Owned tests: `<tests/... paths>`
- Coverage status: `healthy | partial | gap`
- Notes: cleanup tasks, migration notes

## Current index

- Module: `pr_workflow`
  - Owned tests: `tests/modules/pr_workflow/test_pr_workflow_scripts.py`, `tests/modules/pr_workflow/test_user_settings.py`, `tests/modules/pr_workflow/test_user_settings_schemas.py`
  - Coverage status: `healthy`
  - Notes: PR script attribution + verify_publish smoke

- Module: `architecture`
  - Owned tests: `tests/modules/architecture/test_check_contract_json_sync.py`
  - Coverage status: `healthy`
  - Notes: contract JSON sync guard

- Module: `architecture_scripts`
  - Owned tests: `tests/modules/architecture_scripts/test_check_governance_consistency.py`, `tests/modules/architecture_scripts/test_check_debrand.py`, `tests/modules/architecture_scripts/test_path_drift_ban.py`, `tests/modules/architecture_scripts/test_check_doc_facts.py`
  - Coverage status: `healthy`
  - Notes: governance, debrand, path-drift, doc-facts scanners

- Module: `workflow_mcp`
  - Owned tests: `tests/modules/workflow_mcp/test_workflow_mcp.py`
  - Coverage status: `healthy`
  - Notes: MCP tools and tracker read

- Module: `release`
  - Owned tests: `tests/modules/release/test_sync_plugin_bundle.py`, `tests/modules/release/test_sync_trae_contract.py`
  - Coverage status: `healthy`
  - Notes: Trae contract generation; `rewrite_cursor_paths_for_trae` unit tests

- Module: `smoke`
  - Owned tests: `tests/modules/smoke/test_kit_installed.py`
  - Coverage status: `healthy`
  - Notes: default layout + `.trae/` path rewrite smoke

- Module: `install`
  - Owned tests: `tests/modules/install/test_*.py` incl. `tests/modules/install/test_scaffold_trae_only.py`
  - Coverage status: `healthy`
  - Notes: default scaffold; cmd_gates 7 steps (pyright + trae parity)

- Module: `mcp_registry`
  - Owned tests: `tests/modules/mcp_registry/test_*.py`
  - Coverage status: `healthy`
  - Notes: schema, merge, validate CLI

- Module: `integration`
  - Owned tests: `tests/modules/integration/test_integrate_validate.py`, `tests/modules/integration/test_consumer_minimal_example.py`
  - Coverage status: `healthy`
  - Notes: integrate validate P0 checks

- Module: `workflow_drift`
  - Owned tests: `tests/modules/workflow_drift/test_drift_checks.py`, `tests/modules/workflow_drift/test_drift_cli.py`
  - Coverage status: `healthy`
  - Notes: DRIFT-001–009 and CLI wiring

- Module: `ci`
  - Owned tests: `tests/modules/ci/test_seed_kit_workspace.py`
  - Coverage status: `healthy`
  - Notes: CI workspace seed

**Total:** 501 pytest (kit-dev)
