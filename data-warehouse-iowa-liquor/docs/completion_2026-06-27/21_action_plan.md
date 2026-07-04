# Action Plan - From Plan To Presentation

## Phase 1 - Fix Presentation Blockers

### 1. Streamlit Docker Build

Owner: implementation

Files:

- `Dockerfile.streamlit`

Change:

- Use a Python image compatible with Microsoft ODBC packages, preferably `python:3.11-slim-bookworm`.
- Install Microsoft ODBC Driver 18 using the Debian 12 repo.
- Install app requirements from `requirements.txt`.

Verification:

```powershell
docker compose build streamlit
```

### 2. Dashboard Semantic Honesty + Q7

Owner: reporting

Files:

- `app/streamlit_app.py`
- `sql/04_create_semantic_views.sql` only if missing fields are discovered

Change:

- Load `sem.vw_margin_analysis`.
- Add Q7 chart/table showing:
  - category,
  - product,
  - vendor,
  - average unit margin,
  - total margin,
  - total sales.
- Either load more aggregate semantic views directly or change banner wording from "views used" to "semantic views available / semantic layer coverage" while keeping direct loaded views accurate.

Verification:

```powershell
python -m compileall app
```

Then run Streamlit smoke after Docker stack is live.

### 3. County Choropleth

Owner: reporting

Files:

- `app/streamlit_app.py`
- `app/data/iowa_counties.geojson`

Change:

- Join county sales to GeoJSON by normalized county name, or use a proper county-name-to-FIPS map from the GeoJSON.
- Add guard when merge is empty:
  ```text
  show info message, do not build empty choropleth
  ```

Verification:

- No exception when GeoJSON exists.
- Choropleth either renders or fails gracefully with a clear message.

### 4. Quality Checks

Owner: implementation

Files:

- `sql/05_quality_checks.sql`
- `src/transform/warehouse_transform.py`

Change:

- Add `eligible_staging_row_count`.
- Add `fact_row_count`.
- Fail if eligible staging row count differs from fact row count.
- Decide how to handle raw negative rows:
  - fail if any exist, or
  - document that excluded rows are expected and fail only if exclusions are not equal to staging/fact difference.

Recommended for presentation:

- Fail on negative raw rows because it is easier to defend data quality.

Verification:

```powershell
python -m compileall src
```

Then run fast ETL.

### 5. Documentation Cleanup

Owner: docs

Files:

- `README.md`
- `data-warehouse-iowa-liquor/README.md`
- `docs/presentation_notes.md`
- `docs/validation_report.md`
- `docs/warstwa_semantyczna.md`

Change:

- Add real team line when names are available.
- Clean visible mojibake.
- Explain verification scopes:
  - full-year raw extract exists,
  - one-day live demo is fastest,
  - one-month validation proves larger-range load,
  - `dim_date` may contain a full calendar independent of fact range.
- Add rubric-to-evidence table.

Verification:

```powershell
rg -n "Ă|Ä|Ĺ|Å|�|/D:/" README.md data-warehouse-iowa-liquor/README.md data-warehouse-iowa-liquor/docs
```

## Phase 2 - Fresh Verification

### Static

```powershell
python -m compileall src app dags
docker compose config
```

### Docker Build / Startup

```powershell
docker compose build
docker compose up -d sqlserver airflow streamlit
docker compose ps
```

### HTTP Smoke

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
```

### Fast ETL Demo

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

### Evidence To Capture

- staging row count,
- fact row count,
- quality check results,
- Airflow DAG visible,
- Streamlit dashboard loads,
- dashboard can show at least:
  - monthly sales,
  - category/vendor/product,
  - margin analysis,
  - geography,
  - store performance.

## Phase 3 - Presentation Pack

Create or update:

- `docs/presentation_notes.md`
- `docs/final_demo_checklist.md`
- `docs/completion_2026-06-27/30_final_readiness_report.md`

Final readiness report should say:

- what is complete,
- what was verified,
- what demo command to run,
- what fallback exists if Docker/internet is slow.

