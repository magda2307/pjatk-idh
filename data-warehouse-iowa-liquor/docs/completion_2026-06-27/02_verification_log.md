# Verification Log - 2026-06-27

## Static Checks

### Python Compile Check

Command:

```powershell
python -m compileall src app dags
```

Working directory:

```text
D:\pjatk-idh\data-warehouse-iowa-liquor
```

Result:

```text
PASS
```

Evidence:

- `src` compiled.
- `app/streamlit_app.py` compiled.
- `dags/iowa_liquor_etl_dag.py` compiled.

### Docker Compose Config

Command:

```powershell
docker compose config
```

Result:

```text
PASS
```

## Docker Runtime Checks

### Build

Command:

```powershell
docker compose build
```

Result:

```text
PASS
```

### Services

Command:

```powershell
docker compose up -d sqlserver airflow streamlit
docker compose ps
```

Result:

```text
PASS
```

Observed services:

- `iowa-liquor-sqlserver` - up and healthy on port `1433`.
- `iowa-liquor-airflow` - up on port `8080`.
- `iowa-liquor-streamlit` - up on port `8501`.

### HTTP Smoke

Commands:

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
```

Result:

```text
PASS
Airflow=200
Streamlit=200
```

## Live ETL Demo Check

Command:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Result:

```text
PASS
```

Observed output:

- Current public Socrata endpoint for the original resource returned `404`.
- Extractor did not delete existing raw files after API failure.
- Extractor built a fallback extract from cached real raw CSV files under `data/raw`.
- Manifest generated for the live demo:
  - `start_date`: `2023-01-03`
  - `end_date`: `2023-01-03`
  - `file_count`: `3`
  - `total_rows`: `10634`
- Staging rows: `10634`.
- Fact rows: `10624`.
- Raw negative correction rows excluded from fact: `10`.

Quality checks:

```text
PASS
eligible_staging_row_count = 10624
eligible_staging_fact_row_count_difference = 0
null_foreign_keys = 0
negative_measures = 0
duplicate_fact_business_keys = 0
fact_dimension_join_failures = 0
eligible_staging_vs_fact_sales_difference = 0.0000
```

## Dashboard Browser Check

Tool:

```text
Playwright
```

URL:

```text
http://localhost:8501
```

Result:

```text
PASS
```

Evidence:

- Browser page title: `Iowa Liquor Sales DW`.
- Dashboard displayed dataset status: `range=2023-01-03 -> 2023-01-03 | files=3 | rows=10634`.
- Visible Streamlit error count after render: `0`.
- Fresh post-render Streamlit logs over the recent window had no `Traceback`, `Exception`, `Error`, `Could not connect`, or `ValueError`.
- Screenshot saved at `D:\pjatk-idh\streamlit-dashboard-final.png`.

## Inventory Checks

### Raw Data

Command:

```powershell
(Get-ChildItem data\raw -Filter *.csv | Measure-Object).Count
```

Result:

```text
53 CSV files
```

### Current Extract Manifest

File:

```text
data/processed/extract_manifest.json
```

Current manifest says:

```text
start_date: 2023-01-03
end_date: 2023-01-03
file_count: 3
total_rows: 10634
files: data/processed/fallback_raw/*.csv inside the container path
```

Important note:

The manifest stores container paths such as `/opt/airflow/project/...`. On Windows host, `load_staging_from_raw_files()` falls back to scanning `data/raw` if manifest paths do not exist, so local CLI loading still has a recovery path.

## Quality Check Integration Note

The raw Iowa data includes negative correction rows. On the fast demo date `2023-01-03`, there are `10` such rows.

Decision:

- Negative raw rows remain visible as `raw_negative_measure_rows_excluded_from_fact`.
- Fact loading continues to exclude negative sales/bottle/volume rows.
- Quality checks fail if eligible staging row count does not match fact row count.
- Quality checks fail if eligible staging sales do not reconcile to fact sales.

Reason:

This keeps real source-data correction rows transparent without breaking the live ETL demo.
