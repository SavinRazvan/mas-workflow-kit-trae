# Consumer minimal example

Smallest Trae consumer project layout for documentation and integration tests.

## Steps

1. Clone [mas-workflow-kit-trae](https://github.com/SavinRazvan/mas-workflow-kit-trae).
2. Create a new app directory (or use this folder copied elsewhere).
3. From kit repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m trae_workflow activate --directory /path/to/your-app --profile default
```

4. Verify:

```bash
python3 -m trae_workflow health --directory /path/to/your-app
```

## Expected post-activate layout

| Path | Role |
|------|------|
| `.trae/` | Contract plane (agents, skills, rules) |
| `.ai_infra/` | Script spine (slim) |
| `.local/` | Trackers and workflow artifacts |
| `trae_workflow/` | CLI shim |

See [trae-consumer-quickstart.md](../../.ai_infra/docs/operations/trae-consumer-quickstart.md).
