<!--
File: README.md
Path: .ai_infra/scripts/pr/README.md
Role: Hub for maintainer PR scripts and how they relate to git commit trailers vs `.local` artifacts.
Used By:
 - Maintainers, `.trae/skills/pr-workflow/SKILL.md`
Depends On:
 - scripts/pr/local_workflow_paths.py
 - scripts/pr/prepare.py
 - .trae/rules/commit-trailer-format.md
 - .trae/rules/pr-workflow-enforcement.md
Notes:
 - Gate order is canonical in prepare.py `GATES`.
-->

# PR workflow scripts (`scripts/pr/`)

| Script | Role |
|--------|------|
| `review.py` | Stamp `review.md` under `.local/workflow-artifacts/pr/` |
| `prepare.py` | Run merge gates (`GATES`) and stamp `prep.md` |
| `merge.py` | Preconditions + stamp `merge.md` |
| `finalize.py` | Post-merge branch cleanup |
| `verify_publish.py` | Branch / upstream sanity before merge workflow |
| `local_workflow_paths.py` | Canonical artifact paths (also referenced by rules) |

## Git commits vs PR markdown

- **Git** trailers live only in **commit messages**: **`.trae/rules/commit-trailer-format.md`** — required **`Author:`** / **`GitHub-User:`**, optional **`Assisted-by:`**; **do not** use **`Made-with:`**. See **`AGENTS.md`** § Commits.
- **`review.md` / `prep.md` / `merge.md`** use **PR-phase** headers (`Action-By`, `Agent/s`, …). Scripts write those paths via **`local_workflow_paths.py`**; they are **not** git trailers.
