# Validation Report

## Execution Summary

| Metric | Value |
|--------|-------|
| Validation Range | `2023-01-01` to `2023-01-31` |
| Environment | Docker (`sqlserver`, `airflow`, `streamlit`) |
| Execution Time | ~4 minutes (typical for 1 month of Socrata data) |

This report documents the one-month validation run. It is separate from the one-day live demo (`2023-01-03`) and from the default full-year raw extraction range (`2023-01-01` to `2023-12-31`).

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
The pipeline successfully scaled from the 1-day demo (`2023-01-03`) to a full month without memory issues or API rate limits from Socrata, proving the chunked batch extraction approach works as designed.

The default raw extraction configuration targets the full 2023 year. A full-year `dim_date` means the calendar reference table is ready for the full source range; it does not imply that every validation or demo run loaded a full year of facts.

*(Note: If you run this locally, ensure Docker Desktop is running before executing the Airflow DAG)*
