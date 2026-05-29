from __future__ import annotations

from src.extract.socrata_extract import extract_iowa_liquor_sales
from src.load.sqlserver_loader import load_staging_from_raw_files
from src.transform.warehouse_transform import (
    create_semantic_views,
    create_sql_objects,
    load_dimensions,
    load_fact_sales,
    run_quality_checks,
)
from src.utils.logging_utils import get_logger


logger = get_logger(__name__)


def run_initial_etl() -> None:
    logger.info("Starting initial ETL pipeline")
    raw_files = extract_iowa_liquor_sales()
    create_sql_objects()
    staging_rows = load_staging_from_raw_files(raw_files)
    load_dimensions()
    fact_rows = load_fact_sales()
    create_semantic_views()
    checks = run_quality_checks()

    logger.info(
        "Initial ETL finished. Files=%s, staging rows=%s, fact rows=%s, quality checks=%s",
        len(raw_files),
        staging_rows,
        fact_rows,
        len(checks),
    )


if __name__ == "__main__":
    run_initial_etl()
