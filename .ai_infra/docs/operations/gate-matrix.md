<!--
File: gate-matrix.md
Path: .ai_infra/docs/operations/gate-matrix.md
Role: Explains prepare GATES vs kit-dev gates vs consumer verify.
Used By:
 - consumer-quickstart.md
 - enterprise-auditor alignment
Depends On:
 - .ai_infra/scripts/pr/prepare.py
 - .ai_infra/install/trae_workflow/cli.py
-->

# Gate matrix

> **Consumer installs:** use `scaffold --verify` or `trae-workflow gates` on your project. Sections mentioning `make gates`, `make verify-all`, `kit-quality.yml`, or `IMPLEMENTATION-STATUS.md` apply to **kit repository maintainers** only.

Three gate surfaces exist by design (Pattern A).

| Surface | When | Steps | Source of truth |
|---------|------|-------|-----------------|
| **`prepare.py` GATES** | PR merge prep | **2** universal (testing artifacts + pytest); **4** on kit-dev (auto-appends drift + doc facts) | `.ai_infra/scripts/pr/prepare.py` `resolve_gates()` |
| **`trae-workflow gates`** | Kit dev / maintainer hygiene | **6** base (testing artifacts + pytest + governance + debrand + doc facts + pyright when `.venv` present); **7** when `.trae/` present (+ `check_trae_parity.py`) | `.ai_infra/install/trae_workflow/cli.py` |
| **`make doc-validate`** | After doc/agent/rule changes | DOC-001…009 canonical fact checks | `.ai_infra/scripts/architecture/check_doc_facts.py` |
| **`make verify-all`** | Pre-audit / release readiness | 10–11 (+ optional ci-seed): sync-plugin → gates → drift → integrate → check-plugin → **check-payload-git** → contract-json-sync → type-check → trae-parity → health → contributors | `.ai_infra/scripts/architecture/verify_all.py` |
| **Preflight JSON** | After `verify all --write-preflight` | `.local/workflow-artifacts/audit/preflight.json` — per-step `duration_s`, `exit_code`, `output_tail` | `verify_all.write_preflight_json` |
| **`scaffold --verify`** | Post-install smoke on consumer | 4: testing artifacts + pytest + governance + debrand (no doc facts) | `.ai_infra/scripts/install/scaffold.py` `_run_verify` |
| **`make drift-validate`** | Slice closure / maintainer hygiene | Operational drift (DRIFT-001…008) | `.ai_infra/scripts/workflow/check_drift.py` |
| **Consumer drift** | Post-install verify on app projects | `drift validate --profile consumer` — DRIFT-005 (skip when `IMPLEMENTATION-STATUS.md` absent) + DRIFT-008 | [consumer-quickstart.md](consumer-quickstart.md#drift-on-consumer-apps) |
| **`kit-quality.yml` (CI)** | Push/PR on kit repo | seed → `make verify-all` → drift → install-dry-run → pip-audit → health `--json` | `.github/workflows/kit-quality.yml` |

**Rule:** Agents preparing a PR run **`prepare.py`** (or MCP `workflow_run_prepare`). Kit-dev `prepare.py` runs drift + doc facts automatically; consumers keep universal gates unless extended at install. Maintainers validating the kit repo may also run **`make gates`**, **`make drift-validate`**, or **`trae-workflow gates`**. GitHub Actions runs **`seed_kit_workspace.py`** first because `.local/` is gitignored.

Optional product gates: append once to consumer `prepare.py` at install; document in overlay README.
