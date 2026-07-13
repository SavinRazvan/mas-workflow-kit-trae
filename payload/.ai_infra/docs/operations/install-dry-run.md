<!--
File: install-dry-run.md
Path: .ai_infra/docs/operations/install-dry-run.md
Role: Manual install verification checklist for consuming the MAS Workflow Kit in a fresh project.
Used By:
 - README.md Quick install
Depends On:
 - .ai_infra/templates/local-workspace/
Notes:
 - Automated: `python -m trae_workflow install` and `make install-dry-run`.
 - Entry doc: `.ai_infra/docs/operations/trae-consumer-quickstart.md`.
 - Trae edition: contract plane is `.trae/` (ADR-009).
-->

# Install dry-run (manual or automated)

Verify the kit installs into an empty or greenfield project **without** product-specific rule contamination in core `.trae/rules/`.

**Consumer path:** [`trae-consumer-quickstart.md`](trae-consumer-quickstart.md) — recommended first read.

## Automated (recommended)

From the **MAS Workflow Kit for Trae** repo:

```bash
make install-dry-run
# or:
python -m trae_workflow install \
  --target /path/to/new-project \
  --source payload \
  --profile default \
  --with-venv \
  --with-mcp-json \
  --verify
# Kit dev only (full tests tree):
python -m trae_workflow install \
  --target /path/to/new-project \
  --with-tests \
  --with-venv \
  --verify
```

See [`scripts/install/README.md`](../../scripts/install/README.md).

## Manual steps

Use the sections below if you prefer hand-copying or need to debug scaffold behavior.

## Prerequisites

- Python 3.11+ with `venv`
- Git
- Trae IDE (for rules, skills, optional MCP)

## 1. Copy core (manual — deprecated)

> **Prefer the [Automated](#automated-recommended) section above.** Hand-copy paths drift from `manifest.yaml` and `trae_workflow install`.

```bash
TARGET=/tmp/workflow-kit-dry-run
SOURCE=/path/to/mas-workflow-kit-trae/payload
python3 -m trae_workflow install --target "$TARGET" --source "$SOURCE" --profile default --dry-run
```

## 2. Scaffold `.local/` (prefer automated)

**Recommended:** use `scaffold.py` / `trae_workflow install` — do not hand-mkdir buckets.

```bash
python -m trae_workflow install --target "$TARGET" --source "$SOURCE" --profile default
```

Tier 1 base layout created by scaffold (see [local-workspace-layout.md](local-workspace-layout.md) § Artifact tiers):

| Path | Created |
|------|---------|
| `.local/index-and-planning/current/` | Exemplar trackers (if missing), including `coverage-index.md` |
| `.local/index-and-planning/history/` | `updates-log.md` (if missing) |
| `.local/workflow-artifacts/{pr,alignment,drift,enterprise-architecture-audit,release,audit}/` | Dirs + README stubs (if missing) |
| `.local/agents-control-center/config/pages.json` | Cockpit tabs (if missing) |
| `.local/agents-control-center/dashboards/` | Optional HTML/CSS (if missing) |
| `AGENTS.md` | From `.ai_infra/templates/AGENTS.stub.md` (if missing) |

Re-activate is idempotent: existing trackers, `AGENTS.md`, and `pages.json` are not overwritten.

Edit `session-pointer.md` and `plan.md` for the target project name after first install.

## 3. Python environment

```bash
cd "$TARGET"
python3 -m venv .venv
.venv/bin/pip install pytest
.venv/bin/pip install -r requirements-mcp.txt
```

Copy kit tests only for kit-dev installs (`--with-tests`). Consumer default scaffolds `tests/modules/smoke/test_kit_installed.py`:

```bash
# Default consumer install — no copy needed (scaffold writes smoke test)
# Kit dev:
cp -r "$SOURCE/tests" "$TARGET/"
```

## 4. Customize once

- [ ] `project.config.yaml` — copy from `project.config.yaml.example` (optional metadata)
- [ ] `.ai_infra/scripts/pr/prepare.py` — `GATES` (default 2 gates OK)
- [ ] `.ai_infra/scripts/pr/local_workflow_paths.py` — `DEFAULT_GITHUB_USER`
- [ ] `AGENTS.md` — project first-reads
- [ ] Optional: overlay rules via `cp overlays/rules/*.md .trae/rules/`

## 5. Verification gates

```bash
cd "$TARGET"
.venv/bin/python .ai_infra/scripts/pr/check_testing_artifacts.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/architecture/check_governance_consistency.py
```

Expected: all PASS (governance may skip CI workflow if `.github/` absent).

## 6. MCP smoke (optional)

```bash
# activate --with-mcp-json merges kit MCP into .trae/mcp.json
python3 -m trae_workflow mcp validate --directory "$TARGET"
WORKFLOW_KIT_ROOT="$TARGET" .venv/bin/python -m workflow_mcp
```

In Trae: enable MCP server; call `workflow_list_agents` and `workflow_gate_count`.

## 7. Trae contract plane

- [ ] Seven agent files under `.trae/agents/`
- [ ] Thirteen rules under `.trae/rules/` (6 universal + 7 agent-requested)
- [ ] Fifteen skills under `.trae/skills/` (including PR skills)

## Success criteria

| Check | Pass |
|-------|------|
| `prepare.py` has 2 default gates | |
| No product overlay rules in core `.trae/rules/` (universal only) | |
| `.local/index-and-planning/current/session-pointer.md` exists | |
| All six `workflow-artifacts/*/README.md` stubs (recommended_paths) | |
| `AGENTS.md` present | |
| `pytest -q` green | |
| `workflow_mcp` imports and `workflow_gate_count` → `2` | |

## Trae IDE smoke (manual)

1. Open `$TARGET` in Trae
2. Enable **Include AGENTS.md**
3. Confirm rules/skills load from `.trae/`
4. Ask Trae to follow `agent-implementer` and read `session-pointer.md`
