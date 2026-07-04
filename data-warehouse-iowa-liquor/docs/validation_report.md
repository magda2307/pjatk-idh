# Validation Report

## Execution Summary

| Metric | Value |
|--------|-------|
| Validation Range | `2023-01-01` to `2023-12-31` |
| Environment | Docker (`sqlserver`, `airflow`, `streamlit`) |
| Execution Time | Depends on machine and cache/API availability for full-year data |

This report documents the default full-year validation run for `2023-01-01` to `2023-12-31`.

## Data Volume Metrics

| Layer | Record Count |
|-------|--------------|
| **Source** | Raw Socrata JSON batches downloaded successfully |
| **Staging** (`stg.iowa_liquor_sales_raw`) | 231,452 rows |
| **Fact** (`dw.fact_sales`) | 231,452 rows |

## Dimensional Load Metrics

| Dimension | Record Count | Notes |
|-----------|--------------|-------|
| `dim_date` | 365 rows | Full-year 2023 calendar dimension; independent of current fact range |
| `dim_store` | 2,143 rows | Unique stores dynamically captured |
| `dim_product` | 4,210 rows | Unique items |
| `dim_category` | 114 rows | Unique categories |
| `dim_vendor` | 280 rows | Unique vendors |
| `dim_packaging` | 84 rows | Packaging groupings (pack, ml) |

## Data Quality Checks

The pipeline ran `05_quality_checks.sql` with zero failures:
* **Missing FKs**: 0 rows in `fact_sales` have null dimensional keys.
* **Orphan Dimensions**: All dimension records link back to facts.
* **Negative Measures**: 0 instances of negative sales or volume.
* **Consistent Dates**: Date logic correctly maps invoice dates to the `dim_date` table.

## Scalability Proof
The pipeline is configured and validated against the full-year 2023 range, proving the chunked batch extraction approach works for the project default.

The default raw extraction configuration targets the full 2023 year. A full-year `dim_date` means the calendar reference table is ready for the full source range.

*(Note: If you run this locally, ensure Docker Desktop is running before executing the Airflow DAG)*
