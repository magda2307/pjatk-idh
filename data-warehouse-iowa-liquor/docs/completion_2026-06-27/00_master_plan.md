# Project Completion Plan - 2026-06-27

## Goal

Make the Iowa Liquor Sales data warehouse project presentation-ready for 2026-06-28.

The project must prove, live or with clear evidence, that it satisfies the course rubric:

1. Team of 2-4 people.
2. Real, non-generated data.
3. 7-12 business questions.
4. Multidimensional model able to answer those questions.
5. Working data warehouse database.
6. ETL/integration process extracting, integrating, and loading source data.
7. Semantic layer.
8. Reporting layer with charts answering the business questions.

## Current Architecture

```text
Iowa Liquor Sales source / cached real raw CSV
-> Apache Airflow ETL
-> data/raw CSV files
-> SQL Server staging schema stg
-> SQL Server dimensional warehouse schema dw
-> SQL Server semantic views schema sem
-> Streamlit dashboard
```

## Evidence Already Found

- Real source data: Iowa Liquor Sales public dataset cached as real raw CSV files in the repository.
- Local raw extract exists: 53 CSV parts under `data/raw`.
- Full-year raw inventory exists under `data/raw`; the current demo manifest is for `2023-01-03`, with `10,634` rows and `3` fallback files generated from that real raw cache.
- Airflow DAG exists: `dags/iowa_liquor_etl_dag.py`.
- CLI ETL entrypoint exists: `python -m src.run_initial_etl`.
- SQL Server scripts exist for database, schemas, staging, dimensional tables, semantic views, and quality checks.
- Star schema exists in SQL: one fact table and six dimensions.
- Semantic layer exists as SQL views in schema `sem`.
- Streamlit dashboard exists with four report tabs and Plotly charts.
- Business requirements document defines 12 business questions.
- Existing docs include model, ETL, semantic layer, presentation notes, and validation report.

## Completion Definition

Project is considered ready when:

- `docker compose up -d sqlserver airflow streamlit` starts the stack. Verified.
- Airflow UI opens on `http://localhost:8080`. Verified.
- Streamlit opens on `http://localhost:8501`. Verified.
- A fast demo ETL can run live without manual code edits. Verified for `2023-01-03`.
- SQL Server contains staging, fact, dimension, and semantic objects after ETL. Verified by ETL quality output and dashboard semantic reads.
- Quality checks pass. Verified.
- Dashboard loads from semantic views and has no runtime exception. Verified by Playwright and fresh logs.
- Documentation gives a clear defense script for every rubric point. Updated.
- Known visual/reporting bugs are fixed or explicitly documented with a safe fallback. Fixed.

## Priority Plan

### P0 - Must Finish Before Presentation

1. Verify Docker stack startup.
   - Command: `docker compose up -d sqlserver airflow streamlit`
   - Evidence: `docker compose ps`, HTTP checks for Airflow and Streamlit.

2. Verify fast live ETL path.
   - Preferred demo command:
     ```powershell
     docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
     ```
   - Reason: one-day range is fast enough for live presentation.
   - Evidence: staging rows, fact rows, zero quality failures.

3. Fix dashboard presentation blockers.
   - Map section currently has likely county FIPS bug: it derives FIPS from county names, which cannot match GeoJSON county FIPS.
   - Decide: either fix county name/FIPS mapping or gracefully skip choropleth if merge is empty.
   - Verify Streamlit runs after fix.

4. Clean documentation encoding artifacts.
   - Existing docs show mojibake in several Polish words, for example `gotowoĹ›ci`.
   - Replace with ASCII-safe Polish transliteration or correct UTF-8 where file already uses UTF-8 consistently.
   - Presentation docs should look professional.

5. Create final defense checklist.
   - Short presenter script.
   - Rubric-to-evidence table.
   - Live demo commands.
   - Fallback plan if internet or Docker startup is slow.

### P1 - Strongly Recommended

1. Add final smoke-test script or documented checklist.
   - Validate import/compile.
   - Validate required SQL files exist.
   - Validate raw data exists.
   - Validate Streamlit file imports.

2. Update docs to say exactly which tool implements each architecture layer:
   - ETL/orchestration: Apache Airflow.
   - Warehouse: SQL Server.
   - Semantic layer: SQL Server views in schema `sem`.
   - Reporting: Streamlit + Plotly.

3. Align dashboard semantic view usage matrix.
   - Przeglad zarzadczy previously listed `Q1, Q10`; Q10 belongs mainly to Wyniki sklepow.
   - Keep matrix consistent with `business_requirements.md`.

4. Check that validation report matches current local truth.
   - Existing report says one-month run; manifest says full-year extract files exist.
   - Keep both if phrased clearly: full-year extract exists, live validated run can be one day/month.

### P2 - Nice To Have

1. Add screenshots for presentation backup.
2. Add a tiny `presentation_demo.md` with exact click path in Airflow and Streamlit.
3. Add GitHub-friendly notes if project will be shown from repository.

## Risk Register

| Risk | Severity | Evidence | Mitigation |
|---|---:|---|---|
| Docker not running on presentation machine | High | Docker stack required | Current machine verified; keep fallback screenshot and CLI output notes |
| Full-year ETL too slow live | High | Manifest has 2.6M rows | Demo with one day or one month; explain full-year extract is already available |
| Streamlit map exception | Closed | Bad Plotly `locations` update caused ValueError | Fixed and verified by Playwright |
| Docs overclaim unverified state | Closed | Validation docs and progress docs needed fresh evidence | Docker, ETL, HTTP, and browser smoke recorded |
| Encoding artifacts look unprofessional | Closed | Mojibake in README/docs | Visible docs cleaned |
| Manifest paths are container absolute paths | Low | Manifest lists `/opt/airflow/project/...` | Loader falls back to raw glob if manifest paths do not exist locally; document this |

## Subagent Coordination

Subagent briefs are written in this folder:

- `10_subagent_docs_audit.md`
- `11_subagent_implementation_audit.md`
- `12_subagent_reporting_audit.md`

Subagents should report findings back in compressed form. Main thread owns integration, edits, and final verification.

Subagent findings are consolidated in:

- `20_subagent_findings.md`
- `21_action_plan.md`

## Immediate Next Steps

1. Spawn three audit subagents from the briefs.
2. While they work, run local static checks and import checks.
3. Fix P0 blockers found by direct review and subagents.
4. Update final docs and presentation notes.
5. Run final verification.

## Work Log

### 2026-06-27 Initial Planning Pass

- Created completion folder and master plan.
- Created rubric status checklist.
- Created three read-only subagent briefs.
- Spawned documentation, implementation, and reporting audit subagents.
- Ran Python compile check for `src`, `app`, and `dags`: pass.
- Confirmed local raw data inventory: 53 CSV files.
- Confirmed extract manifest scope: full-year 2023, 2,639,557 rows.
- Confirmed P0/P1 candidates:
  - county choropleth FIPS mapping in Streamlit,
  - report matrix typo for Q10,
  - missing explicit team-member documentation.
- Integrated subagent audit results:
  - documentation/rubric audit,
  - ETL/warehouse audit,
  - semantic/reporting audit.
- Added consolidated action plan from audit findings.
- Built Docker images successfully.
- Started SQL Server, Airflow, and Streamlit successfully.
- Ran fast live ETL for `2023-01-03` successfully.
- Verified Streamlit dashboard in Playwright with no visible errors.
- Updated final verification and readiness reports.
