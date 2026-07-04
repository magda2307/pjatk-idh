# Final Readiness Report - 2026-06-27

## Current Status

The project is presentation-ready for a local Docker demo, with one human detail still missing: real team member names.

Completed:

- Business questions: 12 questions documented and mapped to reports.
- Star schema: `dw.fact_sales` plus 6 dimensions.
- ETL: Docker/Airflow path runs end to end.
- Data warehouse: SQL Server staging, dimensional warehouse, and semantic schemas are created.
- Semantic layer: `sem.*` SQL views are available and documented.
- Reporting: Streamlit dashboard reads semantic views and renders KPI, time, product, vendor, geography, margin, and store views.
- Quality checks: fact row count reconciles to eligible staging rows, foreign keys and duplicate checks pass, sales reconciliation passes.
- Demo safety: failed live API calls no longer delete cached raw files; fallback uses cached real raw data, not generated data.

## Verified Evidence

### Static Checks

```text
python -m compileall src app dags -> PASS
docker compose config -> PASS
```

### Docker Runtime

```text
docker compose build -> PASS
docker compose up -d sqlserver airflow streamlit -> PASS
docker compose ps -> sqlserver healthy, airflow up, streamlit up
```

### HTTP Smoke

```text
http://localhost:8080 -> 200
http://localhost:8501 -> 200
```

### Live ETL Demo

Command:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Result:

```text
PASS
```

Key output:

- `10634` staging rows.
- `10624` fact rows.
- `10` raw negative correction rows excluded from fact.
- Eligible staging rows match fact rows.
- Sales reconciliation difference is `0.0000`.

### Dashboard Browser Smoke

Playwright rendered:

```text
http://localhost:8501
```

Result:

```text
PASS
```

Evidence:

- Page title: `Iowa Liquor Sales DW`.
- Visible Streamlit error count: `0`.
- Current dashboard dataset status: `2023-01-03 -> 2023-01-03`, `3` files, `10634` rows.
- Fresh recent Streamlit logs after render contain no tracebacks/errors.
- Screenshot: `D:\pjatk-idh\streamlit-dashboard-final.png`.

## Demo Notes

The original Iowa Liquor Sales Socrata resource endpoint currently returns `404`. The extractor handles this safely:

- downloads into a temporary directory first,
- keeps existing raw files if the API call fails,
- builds the live demo extract from cached real raw CSV files,
- writes a manifest under `data/processed/extract_manifest.json`.

This still satisfies the "data cannot be generated" requirement because the fallback files are filtered from real raw source exports already present in the project.

## Final Demo Commands

Run from:

```powershell
D:\pjatk-idh\data-warehouse-iowa-liquor
```

Build:

```powershell
docker compose build
```

Start stack:

```powershell
docker compose up -d sqlserver airflow streamlit
```

Check containers:

```powershell
docker compose ps
```

Fast live ETL:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Open:

```text
Airflow: http://localhost:8080
Streamlit: http://localhost:8501
```

## Remaining Human Input

Team members are still unknown. Add the real 2-4 person team names before final submission/presentation.

Do not invent names.
