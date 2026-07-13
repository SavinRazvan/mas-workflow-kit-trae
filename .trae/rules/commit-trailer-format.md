---
description: Required git commit trailers (Author + GitHub-User only)
alwaysApply: true
---

# Commit trailer format

## Required (git commits)

- Every commit message body **must** include exactly these two lines **in this order**, with **no other lines between them**:
  - `Author: <Your Full Name>`
  - `GitHub-User: @<yourhandle>`
- Values **must** match `.local/user_settings/github.collaboration.yaml` (`owner.display_name`, `owner.github_user`).
- **Render from config:** `python -m trae_workflow contributors commit-trailers` reads **`.local/user_settings/github.collaboration.yaml`** (copied at install).

## Forbidden in commits

Do **not** add any of the following to commit messages:

- `Assisted-by:`
- `Co-authored-by:`
- `Made-with:` or `Made with …` (editor footers)

Human accountability is expressed by **`Author:`** / **`GitHub-User:`** only.

## Responsibility

- The human author remains responsible for reviewing and validating the change.
- **Do not** use AI or scripts to insert human certification, approval, or DCO-style assertions the person did not explicitly intend.

## Example

```text
Author: Your Full Name
GitHub-User: @yourhandle
```
