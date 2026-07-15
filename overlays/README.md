# Project overlays

> **Trae edition (ADR-009):** Contract plane SSOT is `.trae/` — not `.cursor/`. Install overlay rules into consumer **`.trae/rules/`**. See [ADR-009](../.ai_infra/docs/decisions/ADR-009-trae-only-edition.md).

Per-project rules and optional docs that **extend** the universal **MAS Workflow Kit** — not part of core.

## Convention

| Path | Purpose |
|------|---------|
| `overlays/rules/*.mdc` | Product- or domain-specific Trae rules (install → target `.trae/rules/`) |
| `overlays/docs/` | Optional ops docs merged into project `docs/` at install |

**Core ships 13 rules** in `.trae/rules/` (6 universal governance + 7 agent-requested). Overlays add constraints for *your* product (adapter walls, layer policies, protected paths, etc.).

## Install

At scaffold time, copy overlay files into the target project:

```bash
cp overlays/rules/*.mdc /path/to/project/.trae/rules/
```

Also customize `.ai_infra/scripts/pr/prepare.py` `GATES` once — document extra gates in your overlay README.

## This directory in the kit repo

- `overlays/rules/` — **empty** in core (placeholder for your project's overlay source)
- [`project-rules/`](../project-rules/) — same overlay concept (alias README for installs that prefer that name)

## Anti-patterns

- Do not put product rules in universal `.trae/rules/` in the **mas-workflow-kit** repo
- Do not duplicate `GATES` in overlay markdown — point to `prepare.py`
- Do not treat overlays as agent runtime config (Pattern A: hardcoded scripts)

See [`.ai_infra/docs/operations/trae-consumer-quickstart.md`](../.ai_infra/docs/operations/trae-consumer-quickstart.md) and [`.ai_infra/docs/handoff/IMPLEMENTATION-STATUS.md`](../.ai_infra/docs/handoff/IMPLEMENTATION-STATUS.md).
