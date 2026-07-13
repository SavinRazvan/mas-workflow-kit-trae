<!--
File: marketplace-publish.md
Path: .ai_infra/docs/handoff/marketplace-publish.md
Role: Upstream Cursor Marketplace publish reference (Trae edition does not publish).
Used By:
 - Maintainers comparing Trae vs upstream Cursor kit
Depends On:
 - upstream mas-workflow-kit repository
Notes:
 - Trae edition: N/A — see ADR-009.
-->

# Upstream Cursor Marketplace publish (reference only)

**Trae edition (`mas-workflow-kit-trae`):** does **not** publish to Cursor Marketplace. Contract SSOT is `.trae/`; install via `pip install -e .` + `trae_workflow activate`. See [ADR-009](../decisions/ADR-009-trae-only-edition.md).

**For Cursor Marketplace publishing:** use the upstream repository:

- [mas-workflow-kit](https://github.com/SavinRazvan/mas-workflow-kit)
- Plugin layout: `.cursor/`, `.agents/`, repo-root `agents/`, `rules/`, `skills/`, `payload/`
- `/add-plugin` consumer flow

---

## Why this file exists

Historical kit-dev checklist for REFACTOR-006 Cursor plugin publishing. Retained as a **pointer** so maintainers do not confuse Trae edition with Marketplace distribution.

---

## Trae edition release checklist (this repo)

Use instead of Marketplace publish:

```bash
pip install -e ".[dev,mcp]"
make sync-plugin && make check-plugin && make check-trae-parity
make gates
python3 -m trae_workflow integrate validate --directory .
python3 -m trae_workflow drift validate --directory .
```

**Shipped inventory:** [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md)

**Consumer onboarding:** [trae-consumer-quickstart.md](../operations/trae-consumer-quickstart.md)

---

## Upstream pre-publish (reference)

If maintaining parallel upstream Cursor kit:

1. `make gates` on upstream repo
2. `make sync-plugin` — regenerate Marketplace trees from `.cursor/` + `.agents/skills/`
3. `make check-plugin` — guard payload drift
4. Verify plugin template compliance
5. Submit via Cursor Marketplace review process

Details live in upstream `docs/handoff/marketplace-publish.md` after sync from Cursor kit-dev.

---

## Related

- [repository-map.md](repository-map.md) — Trae repo layout
- [PLUGIN-ARCHITECTURE.md](PLUGIN-ARCHITECTURE.md) — Trae three-plane architecture
