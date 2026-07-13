# Connect external MCP (<5 min)

Link **any** MCP server to kit agents without forking agent prompts.

## Prerequisites

- MAS Workflow Kit activated (`--profile default` installs `.trae/mcp.json`)
- Trae MCP enabled for the workspace

## Quick path

1. **Registry** — copy example and edit agent mappings:

```bash
cp .trae/mcp.registry.yaml.example .trae/mcp.registry.yaml
```

2. **User servers** — secrets stay gitignored:

```bash
cp .trae/mcp.user.example.json .trae/mcp.user.json
# edit mcpServers in mcp.user.json
```

Or link a fragment:

```bash
python3 -m trae_workflow mcp link --name my-api --file .trae/mcp.d/my-api.json
```

3. **Merge + validate:**

```bash
python3 -m trae_workflow mcp validate
```

4. Reload Trae MCP; agents read `.trae/mcp.registry.yaml` for which servers apply to their role.

**Worksheet:** complete **`.local/user_settings/mcp.agents.yaml`** (copied at install) — human-friendly server list and agent mapping — then apply to `.trae/mcp.user.json` and the registry.

## Two-tier model

| Tier | Config | Purpose |
|------|--------|---------|
| Kit | `mcp.json` (from activate) | `workflow-kit` tools (PR, trackers, gates) |
| User | `mcp.user.json` + registry YAML | External servers per agent |

See [ADR-004](../decisions/ADR-004-user-mcp-registry.md).

## Troubleshooting

- `mcp validate` fails: ensure every registry `servers` key exists in merged `mcp.json` `mcpServers`
- Secrets: never commit `mcp.user.json` — scaffold adds it to `.gitignore`
