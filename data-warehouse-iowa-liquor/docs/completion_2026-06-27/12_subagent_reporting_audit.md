# Subagent Brief - Semantic/Reporting Audit

## Role

Audit semantic layer and Streamlit reports against the 12 business questions. Use concise cavecrew-style output.

## Scope

Read:

- `data-warehouse-iowa-liquor/docs/business_requirements.md`
- `data-warehouse-iowa-liquor/sql/04_create_semantic_views.sql`
- `data-warehouse-iowa-liquor/app/streamlit_app.py`
- `data-warehouse-iowa-liquor/docs/warstwa_semantyczna.md`
- `data-warehouse-iowa-liquor/docs/presentation_notes.md`

Do not edit files.

## Questions To Answer

1. Are all 12 business questions answerable from semantic views and Streamlit charts/tables?
2. Which question-to-report mappings are weak or wrong?
3. Are any Streamlit charts likely to crash or mislead?
4. Does dashboard clearly prove semantic-layer usage?
5. What P0 reporting fixes are needed before presentation?

## Output Contract

Return:

```text
Reporting audit:
- path:line - issue/evidence - fix
P0:
- ...
P1:
- ...
```

Keep it compact. File path and line required when possible.

