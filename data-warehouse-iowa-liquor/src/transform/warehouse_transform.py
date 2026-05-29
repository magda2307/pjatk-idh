from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from src.config import SQL_DIR
from src.utils.db import run_sql_script, run_sql_script_on_master, sqlserver_connection
from src.utils.logging_utils import get_logger


logger = get_logger(__name__)


def create_sql_objects() -> None:
    run_sql_script_on_master(str(SQL_DIR / "00_create_database.sql"))
    for script_name in [
        "01_create_schemas.sql",
        "02_create_staging_tables.sql",
        "03_create_dw_tables.sql",
    ]:
        logger.info("Running SQL script %s", script_name)
        run_sql_script(str(SQL_DIR / script_name))


def create_semantic_views() -> None:
    run_sql_script(str(SQL_DIR / "04_create_semantic_views.sql"))
    logger.info("Semantic views created or updated")


def execute_non_query(sql: str) -> None:
    with sqlserver_connection() as connection:
        connection.cursor().execute(sql)


def fetch_scalar(sql: str) -> int:
    with sqlserver_connection() as connection:
        row = connection.cursor().execute(sql).fetchone()
        return int(row[0] or 0)


def load_dimensions() -> None:
    logger.info("Refreshing dimension tables")
    execute_non_query(
        """
        DELETE FROM dw.fact_sales;
        DELETE FROM dw.dim_store;
        DELETE FROM dw.dim_product;
        DELETE FROM dw.dim_category;
        DELETE FROM dw.dim_vendor;
        DELETE FROM dw.dim_packaging;
        DELETE FROM dw.dim_date;
        DBCC CHECKIDENT ('dw.dim_store', RESEED, 0);
        DBCC CHECKIDENT ('dw.dim_product', RESEED, 0);
        DBCC CHECKIDENT ('dw.dim_category', RESEED, 0);
        DBCC CHECKIDENT ('dw.dim_vendor', RESEED, 0);
        DBCC CHECKIDENT ('dw.dim_packaging', RESEED, 0);
        """
    )

    execute_non_query(
        """
        INSERT INTO dw.dim_date (
            date_key, date, day, month, month_name_en, quarter, year,
            day_of_week, day_name_en, day_name_pl, is_weekend, year_month, month_name_pl
        )
        SELECT DISTINCT
            CONVERT(INT, FORMAT(date, 'yyyyMMdd')) AS date_key,
            date,
            DAY(date) AS day,
            MONTH(date) AS month,
            DATENAME(month, date) AS month_name_en,
            DATEPART(quarter, date) AS quarter,
            YEAR(date) AS year,
            DATEPART(weekday, date) AS day_of_week,
            DATENAME(weekday, date) AS day_name_en,
            CASE DATENAME(weekday, date)
                WHEN 'Monday' THEN 'poniedzialek'
                WHEN 'Tuesday' THEN 'wtorek'
                WHEN 'Wednesday' THEN 'sroda'
                WHEN 'Thursday' THEN 'czwartek'
                WHEN 'Friday' THEN 'piatek'
                WHEN 'Saturday' THEN 'sobota'
                WHEN 'Sunday' THEN 'niedziela'
            END AS day_name_pl,
            CASE WHEN DATENAME(weekday, date) IN ('Saturday', 'Sunday') THEN 1 ELSE 0 END AS is_weekend,
            FORMAT(date, 'yyyy-MM') AS year_month,
            CASE MONTH(date)
                WHEN 1 THEN 'styczen'
                WHEN 2 THEN 'luty'
                WHEN 3 THEN 'marzec'
                WHEN 4 THEN 'kwiecien'
                WHEN 5 THEN 'maj'
                WHEN 6 THEN 'czerwiec'
                WHEN 7 THEN 'lipiec'
                WHEN 8 THEN 'sierpien'
                WHEN 9 THEN 'wrzesien'
                WHEN 10 THEN 'pazdziernik'
                WHEN 11 THEN 'listopad'
                WHEN 12 THEN 'grudzien'
            END AS month_name_pl
        FROM stg.iowa_liquor_sales_raw
        WHERE date IS NOT NULL;
        """
    )

    execute_non_query(
        """
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY COALESCE(NULLIF(store_number, ''), 'UNKNOWN')
                       ORDER BY date DESC, staging_key DESC
                   ) AS rn
            FROM stg.iowa_liquor_sales_raw
        )
        INSERT INTO dw.dim_store (
            store_number, store_name, store_type, address, city, zip_code,
            county, state_name, source_store_location, latitude, longitude
        )
        SELECT
            COALESCE(NULLIF(store_number, ''), 'UNKNOWN'),
            store_name,
            NULL AS store_type,
            address,
            city,
            zip_code,
            county,
            'Iowa',
            store_location,
            latitude,
            longitude
        FROM ranked
        WHERE rn = 1;
        """
    )

    execute_non_query(
        """
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY COALESCE(NULLIF(item_number, ''), 'UNKNOWN')
                       ORDER BY date DESC, staging_key DESC
                   ) AS rn
            FROM stg.iowa_liquor_sales_raw
        )
        INSERT INTO dw.dim_product (item_number, item_description)
        SELECT COALESCE(NULLIF(item_number, ''), 'UNKNOWN'), item_description
        FROM ranked
        WHERE rn = 1;
        """
    )

    execute_non_query(
        """
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY COALESCE(NULLIF(category, ''), 'UNKNOWN')
                       ORDER BY date DESC, staging_key DESC
                   ) AS rn
            FROM stg.iowa_liquor_sales_raw
        )
        INSERT INTO dw.dim_category (category_number, category_name)
        SELECT COALESCE(NULLIF(category, ''), 'UNKNOWN'), category_name
        FROM ranked
        WHERE rn = 1;
        """
    )

    execute_non_query(
        """
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY COALESCE(NULLIF(vendor_number, ''), 'UNKNOWN')
                       ORDER BY date DESC, staging_key DESC
                   ) AS rn
            FROM stg.iowa_liquor_sales_raw
        )
        INSERT INTO dw.dim_vendor (vendor_number, vendor_name)
        SELECT COALESCE(NULLIF(vendor_number, ''), 'UNKNOWN'), vendor_name
        FROM ranked
        WHERE rn = 1;
        """
    )

    execute_non_query(
        """
        WITH packaging AS (
            SELECT DISTINCT
                COALESCE(pack, 0) AS pack,
                COALESCE(bottle_volume_ml, 0) AS bottle_volume_ml
            FROM stg.iowa_liquor_sales_raw
        )
        INSERT INTO dw.dim_packaging (pack, bottle_volume_ml, volume_group)
        SELECT
            pack,
            bottle_volume_ml,
            CASE
                WHEN bottle_volume_ml = 0 THEN 'unknown'
                WHEN bottle_volume_ml < 500 THEN 'small'
                WHEN bottle_volume_ml < 1000 THEN 'standard'
                WHEN bottle_volume_ml < 1750 THEN 'large'
                ELSE 'extra_large'
            END AS volume_group
        FROM packaging;
        """
    )

    logger.info(
        "Dimension rows: date=%s store=%s product=%s category=%s vendor=%s packaging=%s",
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_date"),
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_store"),
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_product"),
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_category"),
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_vendor"),
        fetch_scalar("SELECT COUNT(*) FROM dw.dim_packaging"),
    )


def load_fact_sales() -> int:
    logger.info("Refreshing fact_sales")
    execute_non_query("DELETE FROM dw.fact_sales; DBCC CHECKIDENT ('dw.fact_sales', RESEED, 0);")
    execute_non_query(
        """
        INSERT INTO dw.fact_sales (
            date_key, store_key, product_key, category_key, vendor_key, packaging_key,
            invoice_number, source_row_hash, sales_line_count, bottles_sold, sale_dollars,
            volume_sold_liters, volume_sold_gallons, state_bottle_cost,
            state_bottle_retail, margin_amount
        )
        SELECT
            d.date_key,
            s.store_key,
            p.product_key,
            c.category_key,
            v.vendor_key,
            pk.packaging_key,
            raw.invoice_and_item_number AS invoice_number,
            raw.source_row_hash,
            1 AS sales_line_count,
            COALESCE(raw.bottles_sold, 0),
            COALESCE(raw.sale_dollars, 0),
            COALESCE(raw.volume_sold_liters, 0),
            COALESCE(raw.volume_sold_gallons, 0),
            COALESCE(raw.state_bottle_cost, 0),
            COALESCE(raw.state_bottle_retail, 0),
            (COALESCE(raw.state_bottle_retail, 0) - COALESCE(raw.state_bottle_cost, 0))
                * COALESCE(raw.bottles_sold, 0) AS margin_amount
        FROM stg.iowa_liquor_sales_raw raw
        JOIN dw.dim_date d
            ON d.date = raw.date
        JOIN dw.dim_store s
            ON s.store_number = COALESCE(NULLIF(raw.store_number, ''), 'UNKNOWN')
        JOIN dw.dim_product p
            ON p.item_number = COALESCE(NULLIF(raw.item_number, ''), 'UNKNOWN')
        JOIN dw.dim_category c
            ON c.category_number = COALESCE(NULLIF(raw.category, ''), 'UNKNOWN')
        JOIN dw.dim_vendor v
            ON v.vendor_number = COALESCE(NULLIF(raw.vendor_number, ''), 'UNKNOWN')
        JOIN dw.dim_packaging pk
            ON pk.pack = COALESCE(raw.pack, 0)
           AND pk.bottle_volume_ml = COALESCE(raw.bottle_volume_ml, 0)
        WHERE COALESCE(raw.sale_dollars, 0) >= 0
          AND COALESCE(raw.bottles_sold, 0) >= 0
          AND COALESCE(raw.volume_sold_liters, 0) >= 0;
        """
    )
    row_count = fetch_scalar("SELECT COUNT(*) FROM dw.fact_sales")
    logger.info("Loaded %s rows into dw.fact_sales", row_count)
    return row_count


def run_quality_checks(script_path: Path | str = SQL_DIR / "05_quality_checks.sql") -> list[tuple[str, str]]:
    with open(script_path, "r", encoding="utf-8") as sql_file:
        statements = [statement.strip() for statement in sql_file.read().split(";") if statement.strip()]

    results: list[tuple[str, str]] = []
    with sqlserver_connection() as connection:
        cursor = connection.cursor()
        for statement in statements:
            row = cursor.execute(statement).fetchone()
            if row:
                results.append((str(row[0]), str(row[1])))
                logger.info("Quality check %s = %s", row[0], row[1])
    validate_quality_check_results(results)
    return results


def validate_quality_check_results(results: list[tuple[str, str]]) -> None:
    result_map = {name: value for name, value in results}
    errors: list[str] = []

    if int(result_map.get("staging_row_count", "0")) <= 0:
        errors.append("staging_row_count must be greater than 0")
    if int(result_map.get("fact_row_count", "0")) <= 0:
        errors.append("fact_row_count must be greater than 0")

    zero_required_checks = [
        "null_foreign_keys",
        "negative_measures",
        "duplicate_store_numbers",
        "duplicate_product_numbers",
        "duplicate_category_numbers",
        "duplicate_vendor_numbers",
        "duplicate_packaging_keys",
        "fact_dimension_join_failures",
    ]
    for check_name in zero_required_checks:
        if int(result_map.get(check_name, "0")) != 0:
            errors.append(f"{check_name} must equal 0")

    sales_difference_raw = result_map.get("eligible_staging_vs_fact_sales_difference", "0")
    try:
        sales_difference = Decimal(str(sales_difference_raw or "0"))
    except Exception:
        errors.append("eligible_staging_vs_fact_sales_difference must be numeric")
    else:
        if sales_difference > Decimal("0.01"):
            errors.append("eligible_staging_vs_fact_sales_difference must be <= 0.01")

    if errors:
        raise ValueError("Quality checks failed: " + "; ".join(errors))


def refresh_warehouse() -> int:
    load_dimensions()
    fact_rows = load_fact_sales()
    create_semantic_views()
    run_quality_checks()
    return fact_rows
