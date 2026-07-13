# Install scripts

Scaffold the **MAS Workflow Kit for Trae** into a consumer project.

> **Trae edition:** This repository is [mas-workflow-kit-trae](https://github.com/SavinRazvan/mas-workflow-kit-trae). Contract plane is `.trae/` (see [ADR-009](../../docs/decisions/ADR-009-trae-only-edition.md)). Upstream Cursor plugin flow lives in [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit).

## Usage

From the **kit repo root** (or after `python -m trae_workflow activate` in a consumer tree):

```bash
# Preview
python .ai_infra/scripts/install/scaffold.py --target /path/to/new-project --dry-run

# Consumer install (minimal smoke test scaffolded automatically)
python .ai_infra/scripts/install/scaffold.py \
  --target /path/to/new-project \
  --with-venv \
  --with-mcp-json \
  --verify

# Kit dev: copy full tests/ tree
python .ai_infra/scripts/install/scaffold.py \
  --target /path/to/new-project \
  --with-tests \
  --with-venv \
  --verify
```

**Activate (Trae):** from the consumer project root:

```bash
python -m trae_workflow activate --directory . --profile default
```

Copies `project.config.yaml.example` to the target (rename to `project.config.yaml` after install). See [`docs/operations/project-config.md`](../../docs/operations/project-config.md).

## Options

| Flag | Effect |
|------|--------|
| `--target` | Destination directory (required) |
| `--source` | Kit root (default: auto-detect) |
| `--dry-run` | Print copy plan only |
| `--with-readme` | Copy kit `README.md` |
| `--with-tests` | Copy full kit `tests/` (kit dev only; consumer default uses minimal smoke scaffold) |
| `--with-venv` | Create `.venv`, install pytest + mcp |
| `--with-mcp-json` | Merge `mcp.json.kit.example` (+ `mcp.user.json` if present) → `mcp.json` |
| `--verify` | Run `check_testing_artifacts`, `pytest -q`, governance + debrand (4 steps) |

**Product rules:** optional overlays under `overlays/rules/` apply to Trae via `.trae/rules/` after install — not `.cursor/rules/`.

## Makefile

```bash
make install-dry-run
```

Installs to `/tmp/workflow-kit-dry-run` and runs verification gates.

See [`docs/operations/install-dry-run.md`](../../docs/operations/install-dry-run.md).
