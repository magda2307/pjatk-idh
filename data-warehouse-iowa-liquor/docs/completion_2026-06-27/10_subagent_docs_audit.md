# Subagent Brief - Documentation/Rubric Audit

## Role

Audit documentation against the course rubric. Use concise cavecrew-style output.

## Scope

Read:

- `README.md`
- `data-warehouse-iowa-liquor/README.md`
- `data-warehouse-iowa-liquor/docs/*.md`
- `data-warehouse-iowa-liquor/docs/completion_2026-06-27/*.md`

Do not edit files.

## Questions To Answer

1. Which rubric points are clearly documented?
2. Which rubric points are missing, weak, or overclaimed?
3. Which docs have contradictions?
4. Which docs have visible encoding/mojibake or presentation-quality problems?
5. What exact documentation edits are P0 before presentation?

## Output Contract

Return:

```text
Docs audit:
- path:line - issue/evidence - fix
P0:
- ...
P1:
- ...
```

Keep it compact. File path and line required when possible.

