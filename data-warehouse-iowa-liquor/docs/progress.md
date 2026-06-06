# Progress

## Done

- [x] Repository structure
- [x] Socrata CSV extractor with pagination
- [x] Raw CSV files saved in `data/raw`
- [x] SQL Server connection helper
- [x] SQL Server database and schemas: `stg`, `dw`, `sem`
- [x] Staging table: `stg.iowa_liquor_sales_raw`
- [x] Star schema tables: one fact and six dimensions
- [x] Cleaned star schema: `dim_packaging` replaces duplicated `dim_geography`
- [x] Added `sales_line_count` additive measure
- [x] Marked unit prices as non-additive in model docs
- [x] Added Polish and English date labels in `dim_date`
- [x] Initial ETL runnable in Airflow and CLI
- [x] Quality checks printed in ETL logs
- [x] Business requirements with 10 questions
- [x] Mermaid architecture diagram
- [x] Mermaid star schema diagram
- [x] Semantic layer SQL views
- [x] Streamlit dashboard with four report pages
- [x] Dedicated semantic view for category sales structure over time
- [x] Dedicated semantic view for average sales per store by month and region
- [x] Dashboard chart for question 8: category structure over time
- [x] Dashboard chart for question 10: average sales per store by month and county
- [x] Dashboard tables added for all main report areas
- [x] Dashboard parameter `Top N` added for report scope control
- [x] Dashboard refresh button and scope summary added
- [x] Dashboard CSV export added for report tables
- [x] Extract manifest added for ETL traceability
- [x] Extract retries and config validation added
- [x] Loader now prefers manifest-selected raw files
- [x] Final business questions refined to 12 dimension-driven questions
- [x] KPI semantic view extended with invoice, margin, store, and liter metrics
- [x] Semantic layer usage matrix added to docs and dashboard
- [x] Dashboard chart mix expanded with grouped bar, treemap, heatmap, and box plot
- [x] Semantic hierarchy notes added visibly in dashboard
- [x] Docker services for SQL Server, Airflow, and Streamlit

## Verified

- [x] Real Socrata extract works
- [x] SQL Server container runs
- [x] Initial ETL loaded staging, dimensions, fact, semantic views
- [x] Semantic views return aggregates
- [x] Airflow UI shows DAG `iowa_liquor_etl`
- [x] Streamlit service starts and returns HTTP 200 on `http://localhost:8501`
- [x] Dashboard test run: 0 exceptions, 6 KPI metrics, 4 report tabs
- [x] New semantic views return rows

## Next

- [ ] Optional: run one larger date range for final presentation data
