<!--
File: IMPLEMENTATION-STATUS.md
Path: .ai_infra/docs/handoff/IMPLEMENTATION-STATUS.md
Role: Shipped vs spec — single source when maintainer megadocs lag the repo.
Used By:
 - README.md
 - enterprise-auditor alignment passes
Depends On:
 - .ai_infra/scripts/pr/prepare.py
 - .ai_infra/mcp_servers/workflow_mcp/
 - .ai_infra/scripts/install/scaffold.py
Notes:
 - Update this file each material slice; do not rewrite full maintainer megadocs for every change.
-->

# Implementation status (MAS Workflow Kit)

**Last updated:** 2026-07-15 (SLICE-HANDOFF-DOC-SYNC — verify-all steps, DOC-008, coverage refresh)  
**Product:** MAS Workflow Kit for Trae (`mas-workflow-kit-trae`) · CLI: `trae-workflow` 0.4.0 · **Tests:** 501

## Shipped (confirmed in repo)

| Area | Status | Location |
|------|--------|----------|
| Universal rules | 6 governance `.md` + 7 agent-requested | `.trae/rules/` (13 total; Trae SSOT) |
| Agents | 7 core; `model: auto`; audit agents write `.local/` artifacts only | `.trae/agents/` |
| Skills | 15 folders (protocol + PR workflow + alignment) | `.trae/skills/` |
| Payload sync | `make sync-plugin` copies `.trae/` → `payload/.trae/` | `sync_plugin_bundle.py` |
| workflow-activate skill | Consumer + kit-dev | `.trae/skills/workflow-activate/` |
| PR scripts + prepare gates | Pattern A — **2** universal; **4** on kit-dev (drift + doc facts) | `.ai_infra/scripts/pr/prepare.py` |
| Governance + debrand scanners | CI-ready | `.ai_infra/scripts/architecture/` |
| Workflow drift validate | ADR-007 | `.ai_infra/scripts/workflow/check_drift.py` |
| Doc facts validate | DOC-001…009 | `.ai_infra/scripts/architecture/check_doc_facts.py` |
| Verify-all matrix | 11 steps (+ optional ci-seed): sync-plugin → gates → drift → integrate → check-plugin → check-payload-git → contract-json-sync → type-check → trae-parity → health → contributors | `.ai_infra/scripts/architecture/verify_all.py` |
| Anchoring | session-pointer, change-index | `.local/.../current/` |
| MCP tools + resources | 20 tools + 6 resources | `.ai_infra/mcp_servers/workflow_mcp/` |
| Install scaffold + contract | `install-contract.json`; idempotent trackers/`AGENTS.md`/`pages.json` on re-activate | `.ai_infra/scripts/install/scaffold.py` |
| Local artifact tiers | Tier 1 scaffold: all `workflow-artifacts/*` buckets + README stubs; SSOT `local_workflow_paths.py` | `.ai_infra/templates/local-workspace/`, `pages.json` |
| Integrate validate | INT-001…015 (incl. schema version gate) | `.ai_infra/scripts/integration/validate.py` |
| Install CLI | install, **activate**, gates, health, mcp, contributors, integrate, drift, doc, verify | `.ai_infra/install/trae_workflow/cli.py` |
| Editable install | `pyproject.toml` — `pip install -e ".[dev,mcp]"` | repo root |
| Three-plane activate | `default` profile — `.trae/` + slim `.ai_infra/` + `.local/` scaffold | `activate_cli.py`, `plane_status.py` |
| User MCP registry | ADR-004 | `.trae/mcp.registry.yaml.example`, `mcp_manage.py` |
| Cursor Marketplace plugin | **N/A Trae edition** — upstream [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) | see [ADR-009](../decisions/ADR-009-trae-only-edition.md) |
| Kit version on install | `kit_version` 0.4.0 | `.ai_infra/manifest.yaml`, `.ai_infra/.kit-version` |
| Tests | 501 | `tests/modules/` |

## Coverage scope (shipped source)

`pytest --cov=.ai_infra --cov=trae_workflow` measures the **import surface** of the
installable kit (CLI, scripts invoked in-process, MCP server). As of 2026-07-15: **49 files,
4012 statements, 89.23%** when the full suite passes (`make coverage-index`; see
`.local/index-and-planning/current/coverage-index.md`). `generate_coverage_index.py` and
`migrate_local_workspace_layout.py` are maintainer tooling — omitted from `--cov` per
`pyproject.toml`). Subprocess-only maintainer scanners
(`check_governance_consistency.py`, `check_debrand.py`, `check_consumer_purity.py`,
`check_file_headers.py`) have dedicated module tests but are excluded from this metric by
design — they are launched via `subprocess` / `make gates`, not imported by the coverage
run. Running `--cov=.` (tests included) reports ~99% because of order-dependent branches in
test-helper cleanup code; scope shipped source for Trae edition readiness claims.

## Verification commands

```bash
pip install -e ".[dev,mcp]"
make gates
make drift-validate
make doc-validate
make verify-all
make check-payload-git
make install-dry-run
make check-plugin
make smoke-consumer   # manual pre-release (not in CI; see Makefile smoke_marketplace.sh)
trae-workflow activate --directory .
trae-workflow health
trae-workflow mcp validate
pytest -m live tests/modules/workflow_mcp/test_workflow_mcp.py::test_workflow_mcp_stdio_initialize_smoke
trae-workflow drift validate
```

## Not yet shipped

| Item | Target | When to ship |
|------|--------|--------------|
| PyPI publish (`trae-workflow` on PyPI) | out of scope for now | When external consumers need `pip install trae-workflow` without git clone |
| GitHub release tarball | optional | Tag + `python -m build` sdist/wheel attached to GitHub Release when version cadence warrants (no PyPI required) |

**Current distribution (shipped):** editable install via `pip install -e ".[dev,mcp]"` from git clone; `trae-workflow activate` for consumer layout. See [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md).

## Maintainer doc sync

When this file changes, skim-update related maintainer docs under `.ai_infra/docs/maintainer/` — do not full-rewrite megadocs per slice.
