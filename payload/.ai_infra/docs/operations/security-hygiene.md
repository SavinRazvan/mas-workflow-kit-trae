<!--
File: security-hygiene.md
Path: .ai_infra/docs/operations/security-hygiene.md
Role: Supply-chain and MCP security hygiene for kit maintainers.
Used By:
 - kit-quality.yml
 - enterprise-auditor
Depends On:
 - ADR-004-user-mcp-registry.md
-->

# Security hygiene (kit maintainers)

## Dependency audit

CI runs **`pip-audit`** after installing `.[dev,mcp]`. Fix or pin advisories before merging dependency upgrades.

```bash
.venv/bin/pip install pip-audit
.venv/bin/pip-audit
```

## MCP and secrets

- **Never commit** `.trae/mcp.user.json` or API keys — gitignored by activate/scaffold.
- User MCP registry: [ADR-004](../decisions/ADR-004-user-mcp-registry.md).
- `workflow_mcp` server invokes **subprocess** to kit scripts — treat MCP callers as trusted maintainers on local machines.

## User settings schema

`.local/user_settings/github.collaboration.yaml` must validate against [github-collaboration.schema.json](../../schemas/github-collaboration.schema.json) (`version: 1` required).

```bash
python3 -m trae_workflow contributors validate --directory .
```

## Contract JSON sync

Committed `.trae/mcp.json` must match `payload/.trae/mcp.json`:

```bash
make contract-json-check
```
