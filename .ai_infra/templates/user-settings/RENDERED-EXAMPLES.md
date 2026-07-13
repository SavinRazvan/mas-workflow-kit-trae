# Rendered examples — GitHub collaboration

Examples from `github.collaboration.yaml` after install. Replace `Your Full Name` and `@yourhandle` with values from `.local/user_settings/github.collaboration.yaml`.

---

## Commit message

### Kit default (`ai_disclosure_mode: none`)

```text
docs(notebooks): frame notebooks as assertion-backed proof artifacts

Update root README, architecture docs, notebook standards, and evaluator
guides to describe hardened tutorial/check outputs, flagship proof paths, and
what governed vs live notebooks demonstrate for reviewers.

Author: Your Full Name
GitHub-User: @yourhandle
```

**Do not** append `Assisted-by:`, `Co-authored-by:`, or editor `Made with …` footers.

---

## Pull request body

```markdown
## Summary
- Shared local-shell.css + site-nav.js for local HTML dashboards
- Landing index.html, aligned ICC + module-audit stub; docs + folder charter updates

## Test plan
- [ ] pytest -q
- [ ] make gates

## Collaboration
- Action-By: Your Full Name
- GitHub-User: @yourhandle
- Agent/s: review-pr | prepare-pr | merge-pr
```

### Architecture-impacting PR (add alignment)

```markdown
## Collaboration
- Action-By: Your Full Name
- GitHub-User: @yourhandle
- Agent/s: enterprise-auditor | review-pr | prepare-pr | merge-pr
- Alignment: `.local/workflow-artifacts/alignment/`
```

---

## Local phase artifact header (`prep.md`)

Scripts stamp this; values should match `.local/user_settings/github.collaboration.yaml`:

```markdown
## Attribution
- Action-By: Your Full Name
- Prepared-By: Your Full Name
- GitHub-User: @yourhandle
- Agent/s: review-pr | prepare-pr | merge-pr
- Branch: feature/my-branch
- HEAD SHA: abc123...
```

---

## Multi-agent feature slice

When several agents touch one PR, list the pipeline in PR artifacts (not commit trailers):

```yaml
# github.collaboration.yaml
pipelines:
  multi_agent_feature:
    agents: [implementer, test-runner, verifier, review-pr, prepare-pr]
```

```markdown
- Agent/s: implementer | test-runner | verifier | review-pr | prepare-pr
```

Commit trailers remain **Author + GitHub-User only**.
