<!--
File: repository-map.md
Path: .ai_infra/docs/handoff/repository-map.md
Role: Kit-maintainer repository map — Trae edition SSOT, payload sync, consumer install surface.
Used By:
 - AGENTS.md (kit dev onboarding)
 - README.md § Developing the kit
Depends On:
 - .ai_infra/manifest.yaml
 - .ai_infra/scripts/release/sync_plugin_bundle.py
 - ADR-009
Notes:
 - Kit-dev only — not copied to consumer projects via manifest.
-->

# Repository map (Trae edition — kit maintainers)

**Audience:** Maintainers of **mas-workflow-kit-trae** — not consumer app projects.

**Not shipped to consumers.** Lives under `docs/handoff/` (excluded from `manifest.yaml` `copy_ai_infra`).

**Consumer docs:** [workflow-architecture.md](../architecture/workflow-architecture.md) · [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md) · [PLUGIN-USER-GUIDE.md](../operations/PLUGIN-USER-GUIDE.md)

> **Upstream Cursor edition:** [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit) uses `.cursor/` + Marketplace plugin — separate repository.

---

## Top-level layout

```
mas-workflow-kit-trae/
├── .trae/                    # Contract plane SSOT (tracked)
│   ├── agents/               # 7 agent prompts
│   ├── rules/                # 13 rules (6 governance + 7 agent-requested)
│   ├── skills/               # 15 protocol + PR workflow skills
│   └── mcp.*                 # MCP registry + examples
├── payload/                  # Activate source (tracked)
│   ├── .trae/                # Synced from root .trae/ via make sync-plugin
│   └── trae_workflow/        # CLI package copy
├── .ai_infra/                # Infrastructure plane (slim subset → consumers)
│   ├── scripts/              # PR, install, architecture, workflow, integration
│   ├── install/trae_workflow/  # activate CLI
│   ├── mcp_servers/workflow_mcp/
│   ├── docs/                 # operations, governance, decisions, architecture
│   └── templates/            # local-workspace, user-settings, agent-integration
├── trae_workflow/            # Editable install entry (pyproject.toml)
├── tests/modules/            # Kit test suite (488 tests)
├── AGENTS.md                 # Onboarding hub
└── .local/                   # Runtime (gitignored) — trackers, PR artifacts
```

**Gitignored legacy (do not edit):** `.cursor/`, `.agents/`, `.cursor-plugin/` — upstream remnants. See `make clean-legacy-contract`.

---

## SSOT vs generated

| Path | Role | Edit here? |
|------|------|------------|
| `.trae/` | Human-edited contract SSOT | **Yes** |
| `payload/.trae/` | Activate bundle | **No** — `make sync-plugin` |
| `payload/trae_workflow/` | CLI copy for activate | **No** — sync-plugin |
| `.ai_infra/` | Scripts + docs | **Yes** (kit-dev) |
| `.local/` | Runtime trackers/artifacts | **Yes** (local only) |

---

## Consumer install surface (`manifest.yaml` profile `default`)

Copied on `trae_workflow activate`:

- `.trae/` (from `payload/.trae/`)
- `trae_workflow/`
- Slim `.ai_infra/` subtrees (scripts, docs, templates, MCP server)
- Scaffolded `.local/` tier-1 paths + `AGENTS.md` stub

Path SSOT for artifact buckets: `.ai_infra/scripts/pr/local_workflow_paths.py`

---

## Verification (kit-dev)

```bash
pip install -e ".[dev,mcp]"
make sync-plugin && make check-plugin && make check-trae-parity
make gates
python3 -m trae_workflow integrate validate --directory .
```

---

## Maintainer workflow

1. Edit contract plane under **`.trae/`** only.
2. `make sync-plugin` before commit when `.trae/` changes.
3. `make gates` before PR.
4. See [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md) for shipped inventory.

---

## Related

- [PLUGIN-ARCHITECTURE.md](PLUGIN-ARCHITECTURE.md) — three-plane architecture
- [ADR-009](../decisions/ADR-009-trae-only-edition.md) — Trae-only edition decision
