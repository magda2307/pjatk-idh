# Rubric Status - 2026-06-27

## Score-Oriented Status

| Rubric Area | Points | Current Status | Evidence | Remaining Work |
|---|---:|---|---|---|
| Business questions | 5 | Complete | `docs/business_requirements.md` has 12 questions mapped to dimensions/views/reports | None |
| Star schema | 5 | Complete | `sql/03_create_dw_tables.sql`, `docs/dimensional_model.md` | None |
| Initial ETL live | 20 | Verified | `dags/iowa_liquor_etl_dag.py`, `src/run_initial_etl.py`, `sql/05_quality_checks.sql`; live Docker run passed for `2023-01-03` | None |
| Semantic layer | 10 | Verified | `sql/04_create_semantic_views.sql` has `sem.*` views; Streamlit reads semantic views after ETL | None |
| Reports with charts | 10 | Verified | `app/streamlit_app.py` has four tabs and Plotly charts; Playwright smoke passed | None |

## Requirement Coverage

### 1. Team of 2-4 People

Status: documentation gap.

The repository describes the project but does not clearly list team members. Add a short section in presentation notes or README:

```text
Zespol: [name 1], [name 2], [name 3 optional], [name 4 optional]
```

If names are unknown, leave a placeholder in planning docs only and avoid inventing names.

Current status:

```text
BLOCKED until real team member names are supplied by the project group.
```

### 2. Real Non-Generated Data

Status: complete.

Evidence:

- Source: Iowa Liquor Sales public dataset.
- Current demo source: cached real raw CSV files under `data/raw`, filtered into `data/processed/fallback_raw` when the public endpoint is unavailable.
- Local extract: 53 CSV files in `data/raw`.
- Manifest: `data/processed/extract_manifest.json`.

Presentation line:

```text
Dane nie sa generowane. Pochodza z publicznego zbioru Iowa Liquor Sales; szybki demo extract jest filtrowany z lokalnego cache realnych plikow raw, gdy publiczny endpoint API jest niedostepny.
```

### 3. Business Questions

Status: complete.

Evidence:

- `docs/business_requirements.md` lists 12 questions.
- Questions cover time, store, geography, category, vendor, product, margin, day type, and packaging.

Presentation warning:

- Rubric asks for about 7-12 questions. Project has exactly 12, which is acceptable.

### 4. Multidimensional Model

Status: complete.

Evidence:

- Fact: `dw.fact_sales`.
- Dimensions:
  - `dw.dim_date`
  - `dw.dim_store`
  - `dw.dim_product`
  - `dw.dim_category`
  - `dw.dim_vendor`
  - `dw.dim_packaging`

Grain:

```text
One fact row is one sales line for one product, in one store, on one date, on one invoice line.
```

### 5. Warehouse Database

Status: verified.

Evidence:

- SQL Server service in `docker-compose.yml`.
- Database script: `sql/00_create_database.sql`.
- Schemas: `stg`, `dw`, `sem`.

Verification:

```powershell
docker compose ps
```

Observed result: SQL Server healthy, Airflow up, Streamlit up.

### 6. ETL / Integration

Status: verified.

Evidence:

- Airflow service in `docker-compose.yml`.
- DAG: `iowa_liquor_etl`.
- Steps:
  1. extract from Socrata API,
  2. write raw CSV,
  3. create SQL objects,
  4. load staging,
  5. load dimensions,
  6. load fact,
  7. create semantic views,
  8. run quality checks.

Live demo recommendation:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

### 7. Semantic Layer

Status: complete.

Evidence:

- SQL views in `sql/04_create_semantic_views.sql`.
- Dashboard reads from `sem.*` views through `read_view`.

Important views:

- `sem.vw_sales_overview`
- `sem.vw_sales_by_month`
- `sem.vw_sales_by_category`
- `sem.vw_sales_by_store`
- `sem.vw_sales_by_vendor`
- `sem.vw_sales_by_packaging`
- `sem.vw_sales_by_geography`
- `sem.vw_sales_map_points`
- `sem.vw_top_products`
- `sem.vw_margin_analysis`
- `sem.vw_volume_vs_revenue`
- `sem.vw_category_sales_over_time`
- `sem.vw_avg_sales_per_store_by_month_region`
- `sem.vw_kpi_summary`
- `sem.vw_etl_status`

### 8. Reports

Status: verified.

Evidence:

- Streamlit app: `app/streamlit_app.py`.
- Report tabs:
  - Przeglad zarzadczy
  - Produkty i kategorie
  - Geografia
  - Wyniki sklepow

Charts present:

- line charts,
- bar charts,
- grouped bar charts,
- area chart,
- pie chart,
- scatter chart,
- heatmap,
- treemap,
- map charts,
- box plot.

Resolved issues:

- County choropleth now normalizes county names/FIPS and skips safely if no join is possible.
- Q7 margin analysis is exposed in Streamlit.
- Dashboard semantic usage wording no longer overclaims direct loaded views.

## Final Presentation Order

1. State topic and real data source.
2. Show business questions.
3. Show architecture diagram.
4. Show star schema and grain.
5. Run or show Airflow ETL.
6. Show quality checks.
7. Show semantic views.
8. Open Streamlit and answer 3-4 representative business questions live.
9. Mention that remaining questions are covered by mapped tabs/views.
