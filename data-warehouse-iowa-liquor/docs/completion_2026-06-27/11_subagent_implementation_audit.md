# Subagent Brief - ETL/Warehouse Audit

## Role

Audit implementation readiness for live ETL and SQL warehouse demonstration. Use concise cavecrew-style output.

## Scope

Read:

- `data-warehouse-iowa-liquor/docker-compose.yml`
- `data-warehouse-iowa-liquor/Dockerfile.airflow`
- `data-warehouse-iowa-liquor/Dockerfile.streamlit`
- `data-warehouse-iowa-liquor/dags/iowa_liquor_etl_dag.py`
- `data-warehouse-iowa-liquor/src/**/*.py`
- `data-warehouse-iowa-liquor/sql/*.sql`
- `data-warehouse-iowa-liquor/data/processed/extract_manifest.json`

Do not edit files.

## Questions To Answer

1. Can the ETL run live from Docker/Airflow?
2. Are there obvious SQL Server, pyodbc, path, manifest, or Docker risks?
3. Does the star schema match project docs?
4. Do quality checks actually fail on bad conditions?
5. What P0 fixes are needed before presentation?

## Output Contract

Return:

```text
Impl audit:
- path:line - issue/evidence - fix
P0:
- ...
P1:
- ...
```

Keep it compact. File path and line required when possible.

