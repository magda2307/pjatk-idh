# Subagent Findings - 2026-06-27

## Documentation / Rubric Audit

### Finished / Strong

- Rubric is captured in the new completion plan.
- `docs/business_requirements.md` has 12 business questions mapped to dimensions, semantic views, and reports.
- `docs/dimensional_model.md` contains star-schema documentation and diagram.
- `docs/warstwa_semantyczna.md` maps dashboard pages to all 12 questions.

### P0 Findings

- Team of 2-4 people is not documented with actual names.
- Verification claims are inconsistent:
  - one-day verified run in root README,
  - one-month validation report,
  - full-year raw extract manifest,
  - current completion plan still says Docker/report smoke is needed.
- Presentation-facing docs contain visible mojibake:
  - `README.md`: `SkrĂłt`
  - `data-warehouse-iowa-liquor/README.md`: readiness section artifacts
  - `docs/warstwa_semantyczna.md`: `spĂłjny`
- Validation scope needs clearer wording:
  - one-day demo,
  - one-month validation,
  - full-year raw extract,
  - full-year calendar dimension.

### P1 Findings

- Root README still has absolute `/D:/...` links.
- Presentation notes need a compact rubric-to-evidence table.
- Business requirements list 10 report groups, while project has 12 questions; add note that report groups cover all 12 questions.

## Implementation / ETL Audit

### Finished / Strong

- Airflow DAG is wired:
  ```text
  extract -> create SQL objects -> staging -> dimensions -> fact -> semantic views -> quality checks
  ```
- Docker Compose parses.
- Star schema matches docs: one fact and six dimensions.
- Raw part count matches manifest: 53 files.

### P0 Findings

- `Dockerfile.streamlit` likely fails to build:
  - base image is Debian bullseye,
  - Microsoft repo is Debian 12/bookworm,
  - `python3` is used without installing Python.
- Quality checks report raw negative rows but do not fail on them.
- Quality checks reconcile sales amount only, not eligible staging row count vs fact row count.

### P1 Findings

- SQL Server healthcheck is TCP-only; Airflow may start before SQL login/database readiness.
- SQL script runner splits batches with raw `split("GO")`; fragile if `GO` appears in comments/strings.
- Manifest stores container-absolute raw paths; local host runs rely on fallback behavior.
- `Dockerfile.airflow` installs hand-picked dependencies instead of using `requirements.txt`.

## Semantic / Reporting Audit

### Finished / Strong

- All 12 questions are broadly covered by model and available semantic views.
- Dashboard has four business-facing tabs with charts and tables.
- Semantic banner explains hierarchy and listed views.

### P0 Findings

- Dashboard claims it uses many mapped aggregate semantic views, but it only directly loads:
  - `vw_sales_overview`
  - `vw_category_sales_over_time`
  - `vw_avg_sales_per_store_by_month_region`
  - `vw_sales_map_points`
  - `vw_kpi_summary`
  - `vw_etl_status`
- Q7 is weak in Streamlit:
  - business question asks product/category unit margin and total margin,
  - dashboard does not load/use `vw_margin_analysis`.
- County choropleth likely fails or appears blank:
  - code builds FIPS from county name with `zfill`,
  - GeoJSON has numeric FIPS and county names separately.

### P1 Findings

- Q1 asks month, quarter, and year; dashboard currently focuses on `year_month`.
- Q9 asks high volume with lower value per liter; table sorts mostly by volume.
- Q11 asks sales, volume, and invoice count for weekend/weekday; dashboard charts sales and invoices, not volume.
- Several reports recompute aggregates from `vw_sales_overview` instead of directly querying documented aggregate semantic views.

## Consolidated P0 Backlog

1. Add real team-member line to presentation docs or README.
2. Fix Streamlit Docker image build.
3. Fix county choropleth join and empty-merge guard.
4. Add or adjust dashboard reporting for Q7 using `vw_margin_analysis`.
5. Either load documented aggregate semantic views or revise dashboard text so it does not overclaim direct use.
6. Make quality checks fail on bad raw negative rows and add eligible row-count reconciliation.
7. Reconcile validation wording across docs.
8. Clean visible mojibake in presentation-facing docs.

## Consolidated P1 Backlog

1. Add quarter/year rollups for Q1.
2. Improve Q9 ranking by high volume and low `sales_per_liter`.
3. Add weekend/weekday volume chart/table for Q11.
4. Replace TCP-only SQL Server healthcheck.
5. Improve SQL `GO` batch parser.
6. Make manifest paths portable for local host and container runs.
7. Replace root README absolute links with relative links.
8. Add compact rubric-to-evidence table to `docs/presentation_notes.md`.

