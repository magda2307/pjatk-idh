-- =============================================================================
-- PLIK:    06_warehouse_summary.sql
-- PROJEKT: Iowa Liquor Sales Data Warehouse
-- CEL:     Terminalowy raport po ETL: warstwy, wymiary, fact, widoki semantyczne
--          i kontrole jakosci. Skrypt jest tylko do odczytu: PRINT + SELECT.
--
-- URUCHOMIENIE:
--   sqlcmd -S localhost,1433 -U sa -P "<haslo>" -d IowaLiquorDW -i sql\06_warehouse_summary.sql
--
-- KOLEJNOSC RAPORTU:
--   A. Kontekst uruchomienia
--   B. Medallion flow: Bronze -> Silver -> Gold -> Semantic
--   C. Silver/staging: pliki zrodlowe, typowe transformacje, jakosc wejscia
--   D. Before/after: Silver przed Gold vs Gold po ladowaniu
--   E. Gold dimensions: 6 wymiarow
--   F. Gold fact_sales: ziarno, miary, integralnosc FK
--   G. Semantic views: katalog i probki wszystkich 16 widokow sem.*
--   H. Quality checks: replay PASS/FAIL
-- =============================================================================

USE IowaLiquorDW;
GO

SET NOCOUNT ON;
GO

PRINT '';
PRINT '===========================================================================';
PRINT '  A. KONTEKST URUCHOMIENIA';
PRINT '===========================================================================';
PRINT '';

SELECT
    DB_NAME() AS database_name,
    @@SERVERNAME AS server_name,
    SYSTEM_USER AS executed_by,
    SYSDATETIME() AS run_timestamp_local,
    SYSUTCDATETIME() AS run_timestamp_utc;
GO

-- =============================================================================
-- B. MEDALLION FLOW
-- Bronze jest poza SQL Serverem (CSV/cache). W SQL widzimy jego slad przez
-- source_file w stagingu. Silver to stg.*, Gold to dw.*, Semantic to sem.*.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  B. MEDALLION FLOW: BRONZE -> SILVER -> GOLD -> SEMANTIC';
PRINT '===========================================================================';
PRINT '';

SELECT
    '1 Bronze' AS layer_name,
    'data/raw + data/processed/fallback_raw' AS object_name,
    'CSV z API albo cache, bez modelowania hurtowni' AS purpose,
    CAST(COUNT(DISTINCT source_file) AS VARCHAR(40)) AS observed_count,
    'Widoczne w SQL jako source_file w stg.iowa_liquor_sales_raw' AS verification_hint
FROM stg.iowa_liquor_sales_raw
UNION ALL
SELECT
    '2 Silver',
    'stg.iowa_liquor_sales_raw',
    'Wiersze po czyszczeniu Python: typy, klucze, GPS, hash',
    CAST(COUNT_BIG(*) AS VARCHAR(40)),
    'COUNT_BIG(*), source_row_hash, load_timestamp'
FROM stg.iowa_liquor_sales_raw
UNION ALL
SELECT
    '3 Gold',
    'dw.dim_* + dw.fact_sales',
    'Model gwiazdy: 6 wymiarow + tabela faktow',
    CAST((
        (SELECT COUNT_BIG(*) FROM dw.fact_sales)
        + (SELECT COUNT_BIG(*) FROM dw.dim_date)
        + (SELECT COUNT_BIG(*) FROM dw.dim_store)
        + (SELECT COUNT_BIG(*) FROM dw.dim_product)
        + (SELECT COUNT_BIG(*) FROM dw.dim_category)
        + (SELECT COUNT_BIG(*) FROM dw.dim_vendor)
        + (SELECT COUNT_BIG(*) FROM dw.dim_packaging)
    ) AS VARCHAR(40)),
    'Licznik laczny faktow i wymiarow'
UNION ALL
SELECT
    '4 Semantic',
    'sem.*',
    'Widoki raportowe dla Streamlit i kontroli stanu',
    CAST(COUNT(*) AS VARCHAR(40)),
    'Powinno byc 16 widokow'
FROM sys.views v
JOIN sys.schemas s ON s.schema_id = v.schema_id
WHERE s.name = 'sem';
GO

PRINT '';
PRINT '--- B.1 Oczekiwane widoki semantyczne vs widoki obecne w bazie ---';

WITH expected_views AS (
    SELECT 'vw_sales_overview' AS view_name UNION ALL
    SELECT 'vw_sales_by_day_type' UNION ALL
    SELECT 'vw_sales_by_month' UNION ALL
    SELECT 'vw_category_sales_over_time' UNION ALL
    SELECT 'vw_sales_by_category' UNION ALL
    SELECT 'vw_sales_by_store' UNION ALL
    SELECT 'vw_sales_by_vendor' UNION ALL
    SELECT 'vw_sales_by_packaging' UNION ALL
    SELECT 'vw_sales_by_geography' UNION ALL
    SELECT 'vw_sales_map_points' UNION ALL
    SELECT 'vw_top_products' UNION ALL
    SELECT 'vw_margin_analysis' UNION ALL
    SELECT 'vw_volume_vs_revenue' UNION ALL
    SELECT 'vw_avg_sales_per_store_by_month_region' UNION ALL
    SELECT 'vw_kpi_summary' UNION ALL
    SELECT 'vw_etl_status'
)
SELECT
    e.view_name,
    CASE WHEN v.object_id IS NULL THEN 'MISSING' ELSE 'OK' END AS status
FROM expected_views e
LEFT JOIN sys.views v
    ON v.name = e.view_name
   AND SCHEMA_NAME(v.schema_id) = 'sem'
ORDER BY e.view_name;
GO

-- =============================================================================
-- C. SILVER / STAGING
-- Pokazuje co trafilo z Bronze do Silver, jakie sa zakresy dat i podstawowe
-- problemy danych przed modelem gwiazdy.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  C. SILVER / STAGING: SOURCE FILES, TRANSFORMACJE, JAKOSC';
PRINT '===========================================================================';
PRINT '';

PRINT '--- C.1 Pliki zrodlowe widoczne w stagingu (TOP 20) ---';

SELECT TOP 20
    source_file,
    COUNT_BIG(*) AS row_count,
    MIN([date]) AS min_date,
    MAX([date]) AS max_date,
    COUNT_BIG(CASE WHEN source_row_hash IS NULL THEN 1 END) AS null_hash_rows,
    COUNT_BIG(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) AS rows_with_gps
FROM stg.iowa_liquor_sales_raw
GROUP BY source_file
ORDER BY source_file;
GO

PRINT '';
PRINT '--- C.2 Podstawowa jakosc stagingu ---';

SELECT
    COUNT_BIG(*) AS staging_rows,
    COUNT_BIG(DISTINCT source_row_hash) AS distinct_hashes,
    COUNT_BIG(*) - COUNT_BIG(DISTINCT source_row_hash) AS duplicate_hash_candidates,
    COUNT_BIG(CASE WHEN [date] IS NULL THEN 1 END) AS null_date_rows,
    COUNT_BIG(CASE WHEN invoice_and_item_number IS NULL THEN 1 END) AS null_invoice_rows,
    COUNT_BIG(CASE WHEN store_number IS NULL THEN 1 END) AS null_store_number_rows,
    COUNT_BIG(CASE WHEN item_number IS NULL THEN 1 END) AS null_item_number_rows,
    COUNT_BIG(CASE WHEN sale_dollars < 0 OR bottles_sold < 0 OR volume_sold_liters < 0 THEN 1 END) AS negative_measure_rows,
    COUNT_BIG(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) AS rows_with_gps
FROM stg.iowa_liquor_sales_raw;
GO

PRINT '';
PRINT '--- C.3 Przykladowe rekordy Silver z wyliczeniem marzy tak jak w Gold ---';

SELECT TOP 10
    staging_key,
    source_file,
    invoice_and_item_number,
    [date],
    store_number,
    store_name,
    city,
    county,
    item_number,
    item_description,
    pack,
    bottle_volume_ml,
    state_bottle_cost,
    state_bottle_retail,
    bottles_sold,
    sale_dollars,
    CAST((COALESCE(state_bottle_retail, 0) - COALESCE(state_bottle_cost, 0))
         * COALESCE(bottles_sold, 0) AS DECIMAL(18,4)) AS margin_amount_if_loaded,
    source_row_hash
FROM stg.iowa_liquor_sales_raw
ORDER BY [date] DESC, staging_key DESC;
GO

-- =============================================================================
-- D. BEFORE/AFTER: SILVER -> GOLD
-- Porownanie wierszy kwalifikujacych sie w stagingu z wierszami fact_sales.
-- To jest najkrotszy test, czy ladowanie Gold nie zgubilo danych.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  D. BEFORE/AFTER: SILVER PRZED GOLD VS GOLD PO LADOWANIU';
PRINT '===========================================================================';
PRINT '';

WITH silver AS (
    SELECT
        COUNT_BIG(*) AS all_rows,
        COUNT_BIG(CASE
            WHEN COALESCE(sale_dollars, 0) >= 0
             AND COALESCE(bottles_sold, 0) >= 0
             AND COALESCE(volume_sold_liters, 0) >= 0
            THEN 1 END) AS eligible_rows,
        SUM(CASE
            WHEN COALESCE(sale_dollars, 0) >= 0
             AND COALESCE(bottles_sold, 0) >= 0
             AND COALESCE(volume_sold_liters, 0) >= 0
            THEN COALESCE(sale_dollars, 0) ELSE 0 END) AS eligible_sales,
        SUM(CASE
            WHEN sale_dollars < 0 OR bottles_sold < 0 OR volume_sold_liters < 0
            THEN 1 ELSE 0 END) AS excluded_negative_rows
    FROM stg.iowa_liquor_sales_raw
),
gold AS (
    SELECT
        COUNT_BIG(*) AS fact_rows,
        SUM(sale_dollars) AS fact_sales,
        SUM(margin_amount) AS fact_margin,
        SUM(sales_line_count) AS sales_line_count
    FROM dw.fact_sales
)
SELECT
    silver.all_rows AS silver_all_rows,
    silver.eligible_rows AS silver_rows_eligible_for_fact,
    gold.fact_rows AS gold_fact_rows_after_load,
    silver.eligible_rows - gold.fact_rows AS row_difference,
    silver.excluded_negative_rows AS silver_rows_excluded_by_negative_measure_filter,
    CAST(silver.eligible_sales AS DECIMAL(18,4)) AS silver_eligible_sales,
    CAST(gold.fact_sales AS DECIMAL(18,4)) AS gold_fact_sales,
    CAST(ABS(COALESCE(silver.eligible_sales, 0) - COALESCE(gold.fact_sales, 0)) AS DECIMAL(18,4)) AS sales_difference,
    CAST(gold.fact_margin AS DECIMAL(18,4)) AS gold_total_margin,
    gold.sales_line_count
FROM silver
CROSS JOIN gold;
GO

-- =============================================================================
-- E. GOLD DIMENSIONS
-- Wymiary sa ladowane przed fact_sales. Dla store/product/category/vendor
-- deduplikacja jest SCD Type 1: ROW_NUMBER() po kluczu biznesowym.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  E. GOLD DIMENSIONS: 6 WYMIAROW';
PRINT '===========================================================================';
PRINT '';

PRINT '--- E.1 Liczniki wymiarow ---';

SELECT 'dw.dim_date' AS table_name, COUNT_BIG(*) AS row_count FROM dw.dim_date
UNION ALL SELECT 'dw.dim_store', COUNT_BIG(*) FROM dw.dim_store
UNION ALL SELECT 'dw.dim_product', COUNT_BIG(*) FROM dw.dim_product
UNION ALL SELECT 'dw.dim_category', COUNT_BIG(*) FROM dw.dim_category
UNION ALL SELECT 'dw.dim_vendor', COUNT_BIG(*) FROM dw.dim_vendor
UNION ALL SELECT 'dw.dim_packaging', COUNT_BIG(*) FROM dw.dim_packaging;
GO

PRINT '';
PRINT '--- E.2 Zakres dat i kompletna pokrywa dim_date ---';

SELECT
    MIN([date]) AS min_date,
    MAX([date]) AS max_date,
    COUNT_BIG(*) AS dim_date_rows,
    DATEDIFF(DAY, MIN([date]), MAX([date])) + 1 AS expected_calendar_days,
    DATEDIFF(DAY, MIN([date]), MAX([date])) + 1 - COUNT_BIG(*) AS missing_calendar_days
FROM dw.dim_date;
GO

PRINT '';
PRINT '--- E.3 Klucze UNKNOWN w wymiarach tekstowych ---';

SELECT 'dw.dim_store' AS table_name, COUNT_BIG(*) AS unknown_rows
FROM dw.dim_store
WHERE store_number = 'UNKNOWN'
UNION ALL
SELECT 'dw.dim_product', COUNT_BIG(*)
FROM dw.dim_product
WHERE item_number = 'UNKNOWN'
UNION ALL
SELECT 'dw.dim_category', COUNT_BIG(*)
FROM dw.dim_category
WHERE category_number = 'UNKNOWN'
UNION ALL
SELECT 'dw.dim_vendor', COUNT_BIG(*)
FROM dw.dim_vendor
WHERE vendor_number = 'UNKNOWN';
GO

PRINT '';
PRINT '--- E.4 dim_packaging: grupy objetosci ---';

SELECT
    volume_group,
    COUNT_BIG(*) AS packaging_variants,
    MIN(bottle_volume_ml) AS min_bottle_volume_ml,
    MAX(bottle_volume_ml) AS max_bottle_volume_ml
FROM dw.dim_packaging
GROUP BY volume_group
ORDER BY volume_group;
GO

PRINT '';
PRINT '--- E.5 Probki wymiarow ---';

SELECT TOP 5 * FROM dw.dim_store ORDER BY store_key;
SELECT TOP 5 * FROM dw.dim_product ORDER BY product_key;
SELECT TOP 5 * FROM dw.dim_category ORDER BY category_key;
SELECT TOP 5 * FROM dw.dim_vendor ORDER BY vendor_key;
SELECT TOP 5 * FROM dw.dim_packaging ORDER BY packaging_key;
GO

-- =============================================================================
-- F. GOLD FACT TABLE
-- Grain: jedna linia faktury, jeden SKU, jeden sklep, jeden dzien.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  F. GOLD FACT: dw.fact_sales';
PRINT '===========================================================================';
PRINT '';

PRINT '--- F.1 Podstawowe miary fact_sales ---';

SELECT
    COUNT_BIG(*) AS fact_rows,
    COUNT(DISTINCT invoice_number) AS invoice_count,
    SUM(sales_line_count) AS sales_line_count,
    SUM(bottles_sold) AS total_bottles_sold,
    SUM(sale_dollars) AS total_sales,
    SUM(margin_amount) AS total_margin,
    CAST(100.0 * SUM(margin_amount) / NULLIF(SUM(sale_dollars), 0) AS DECIMAL(9,2)) AS margin_percent,
    SUM(volume_sold_liters) AS total_volume_liters,
    MIN(load_timestamp) AS first_fact_load_timestamp,
    MAX(load_timestamp) AS last_fact_load_timestamp
FROM dw.fact_sales;
GO

PRINT '';
PRINT '--- F.2 Integralnosc kluczy obcych w fact_sales ---';

SELECT
    COUNT_BIG(CASE WHEN date_key IS NULL THEN 1 END) AS null_date_key,
    COUNT_BIG(CASE WHEN store_key IS NULL THEN 1 END) AS null_store_key,
    COUNT_BIG(CASE WHEN product_key IS NULL THEN 1 END) AS null_product_key,
    COUNT_BIG(CASE WHEN category_key IS NULL THEN 1 END) AS null_category_key,
    COUNT_BIG(CASE WHEN vendor_key IS NULL THEN 1 END) AS null_vendor_key,
    COUNT_BIG(CASE WHEN packaging_key IS NULL THEN 1 END) AS null_packaging_key
FROM dw.fact_sales;
GO

PRINT '';
PRINT '--- F.3 Sprzedaz po roku z dim_date ---';

SELECT
    d.year,
    COUNT_BIG(f.sales_key) AS sales_line_count,
    COUNT(DISTINCT f.invoice_number) AS invoice_count,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.margin_amount) AS total_margin
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
GROUP BY d.year
ORDER BY d.year;
GO

-- =============================================================================
-- G. SEMANTIC VIEWS
-- Wszystkie 16 widokow z sql/04_create_semantic_views.sql. TOP 5 pozwala szybko
-- zobaczyc ksztalt danych bez otwierania Streamlit.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  G. SEMANTIC VIEWS: KATALOG I PROBKI 16 WIDOKOW';
PRINT '===========================================================================';
PRINT '';

PRINT '--- G.0 Katalog widokow sem.* ---';

SELECT
    s.name AS schema_name,
    v.name AS view_name,
    o.modify_date
FROM sys.views v
JOIN sys.schemas s ON s.schema_id = v.schema_id
JOIN sys.objects o ON o.object_id = v.object_id
WHERE s.name = 'sem'
ORDER BY v.name;
GO

PRINT '';
PRINT '--- G.1 sem.vw_sales_overview: plaski widok faktow po nazwach ---';
SELECT TOP 5
    [date], store_number, store_name, city, county, item_number,
    item_description, category_name, vendor_name, sale_dollars, margin_amount
FROM sem.vw_sales_overview
ORDER BY [date] DESC;
GO

PRINT '';
PRINT '--- G.2 sem.vw_sales_by_day_type: weekend vs weekday ---';
SELECT TOP 5
    year, quarter, month, year_month, is_weekend, day_type,
    total_sales, total_bottles_sold, total_volume_liters, total_margin,
    sales_line_count, invoice_count
FROM sem.vw_sales_by_day_type
ORDER BY year DESC, month DESC, day_type;
GO

PRINT '';
PRINT '--- G.3 sem.vw_sales_by_month: trend miesieczny ---';
SELECT TOP 5
    year, quarter, month, year_month,
    total_sales, total_bottles_sold, total_volume_liters, total_margin,
    sales_line_count, invoice_count, store_count
FROM sem.vw_sales_by_month
ORDER BY year DESC, month DESC;
GO

PRINT '';
PRINT '--- G.4 sem.vw_category_sales_over_time: kategorie w czasie ---';
SELECT TOP 5
    year, quarter, month, year_month, category_name,
    total_sales, total_bottles_sold, total_volume_liters, total_margin,
    sales_line_count, invoice_count, store_count
FROM sem.vw_category_sales_over_time
ORDER BY year DESC, month DESC, total_sales DESC;
GO

PRINT '';
PRINT '--- G.5 sem.vw_sales_by_category: udzial kategorii ---';
SELECT TOP 5
    category_name, total_sales, total_bottles_sold, total_volume_liters,
    total_margin, sales_line_count, avg_margin_per_bottle, sales_share_percent
FROM sem.vw_sales_by_category
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.6 sem.vw_sales_by_store: ranking sklepow ---';
SELECT TOP 5
    store_number, store_name, city, county,
    total_sales, total_bottles_sold, total_volume_liters,
    total_margin, sales_line_count, invoice_count
FROM sem.vw_sales_by_store
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.7 sem.vw_sales_by_vendor: ranking dostawcow ---';
SELECT TOP 5
    vendor_name, total_sales, total_bottles_sold, total_margin,
    sales_line_count, sales_share_percent
FROM sem.vw_sales_by_vendor
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.8 sem.vw_sales_by_packaging: opakowania i volume_group ---';
SELECT TOP 5
    pack, bottle_volume_ml, volume_group,
    total_sales, total_bottles_sold, total_volume_liters,
    total_margin, sales_line_count, invoice_count, sales_share_percent
FROM sem.vw_sales_by_packaging
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.9 sem.vw_sales_by_geography: stan, county, miasto ---';
SELECT TOP 5
    state_name, county, city,
    total_sales, total_bottles_sold, total_volume_liters,
    total_margin, sales_line_count, store_count
FROM sem.vw_sales_by_geography
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.10 sem.vw_sales_map_points: sklepy z GPS ---';
SELECT TOP 5
    store_number, store_name, state_name, county, city, zip_code,
    latitude, longitude, total_sales, total_bottles_sold,
    total_volume_liters, total_margin, sales_line_count, invoice_count
FROM sem.vw_sales_map_points
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.11 sem.vw_top_products: produkty ---';
SELECT TOP 5
    item_number, item_description, category_name, vendor_name,
    total_sales, total_bottles_sold, total_margin, sales_line_count
FROM sem.vw_top_products
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.12 sem.vw_margin_analysis: marza jednostkowa ---';
SELECT TOP 5
    category_name, vendor_name, item_description,
    state_bottle_cost, state_bottle_retail,
    avg_unit_margin, total_margin, total_sales
FROM sem.vw_margin_analysis
ORDER BY total_margin DESC;
GO

PRINT '';
PRINT '--- G.13 sem.vw_volume_vs_revenue: wolumen vs revenue ---';
SELECT TOP 5
    state_name, county, city,
    total_volume_liters, total_sales, sales_per_liter, store_count
FROM sem.vw_volume_vs_revenue
ORDER BY total_sales DESC;
GO

PRINT '';
PRINT '--- G.14 sem.vw_avg_sales_per_store_by_month_region: srednia per sklep ---';
SELECT TOP 5
    year, quarter, month, year_month, state_name, county, city,
    store_count, avg_sales_per_store, avg_bottles_per_store,
    avg_volume_liters_per_store, avg_margin_per_store
FROM sem.vw_avg_sales_per_store_by_month_region
ORDER BY year DESC, month DESC, avg_sales_per_store DESC;
GO

PRINT '';
PRINT '--- G.15 sem.vw_kpi_summary: jeden wiersz KPI ---';
SELECT
    total_sales, total_margin, sales_line_count,
    total_bottles_sold, total_volume_liters,
    invoice_count, store_count, product_count, category_count, vendor_count,
    avg_invoice_value, avg_bottles_per_invoice,
    avg_margin_percent, sales_per_store, sales_per_liter
FROM sem.vw_kpi_summary;
GO

PRINT '';
PRINT '--- G.16 sem.vw_etl_status: status techniczny ETL ---';
SELECT
    status_generated_at, staging_row_count, fact_row_count,
    dim_date_count, dim_store_count, dim_product_count,
    dim_category_count, dim_vendor_count, dim_packaging_count,
    min_date, max_date, last_staging_load_timestamp, last_fact_load_timestamp
FROM sem.vw_etl_status;
GO

-- =============================================================================
-- H. QUALITY CHECKS
-- Warunki sa zgodne z walidacja Python w validate_quality_check_results().
-- raw_negative_measure_rows_excluded_from_fact jest informacyjne.
-- =============================================================================

PRINT '';
PRINT '===========================================================================';
PRINT '  H. QUALITY CHECKS: PASS / FAIL';
PRINT '===========================================================================';
PRINT '';

WITH quality_checks AS (
SELECT
    1 AS sort_order,
    'staging_row_count' AS check_name,
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)) AS check_value,
    CASE WHEN COUNT_BIG(*) > 0 THEN 'PASS' ELSE 'FAIL' END AS result
FROM stg.iowa_liquor_sales_raw
UNION ALL
SELECT
    2,
    'eligible_staging_row_count',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) > 0 THEN 'PASS' ELSE 'FAIL' END
FROM stg.iowa_liquor_sales_raw
WHERE COALESCE(sale_dollars, 0) >= 0
  AND COALESCE(bottles_sold, 0) >= 0
  AND COALESCE(volume_sold_liters, 0) >= 0
UNION ALL
SELECT
    3,
    'fact_row_count',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) > 0 THEN 'PASS' ELSE 'FAIL' END
FROM dw.fact_sales
UNION ALL
SELECT
    4,
    'eligible_staging_fact_row_count_difference',
    CAST(ABS(stg.row_count - fact.row_count) AS DECIMAL(38,4)),
    CASE WHEN ABS(stg.row_count - fact.row_count) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT COUNT_BIG(*) AS row_count
    FROM stg.iowa_liquor_sales_raw
    WHERE COALESCE(sale_dollars, 0) >= 0
      AND COALESCE(bottles_sold, 0) >= 0
      AND COALESCE(volume_sold_liters, 0) >= 0
) stg
CROSS JOIN (
    SELECT COUNT_BIG(*) AS row_count
    FROM dw.fact_sales
) fact
UNION ALL
SELECT
    5,
    'null_foreign_keys',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM dw.fact_sales
WHERE date_key IS NULL
   OR store_key IS NULL
   OR product_key IS NULL
   OR category_key IS NULL
   OR vendor_key IS NULL
   OR packaging_key IS NULL
UNION ALL
SELECT
    6,
    'negative_measures',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM dw.fact_sales
WHERE sale_dollars < 0
   OR bottles_sold < 0
   OR volume_sold_liters < 0
UNION ALL
SELECT
    7,
    'duplicate_store_numbers',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT store_number
    FROM dw.dim_store
    GROUP BY store_number
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT
    8,
    'duplicate_product_numbers',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT item_number
    FROM dw.dim_product
    GROUP BY item_number
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT
    9,
    'duplicate_category_numbers',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT category_number
    FROM dw.dim_category
    GROUP BY category_number
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT
    10,
    'duplicate_vendor_numbers',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT vendor_number
    FROM dw.dim_vendor
    GROUP BY vendor_number
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT
    11,
    'duplicate_packaging_keys',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT pack, bottle_volume_ml
    FROM dw.dim_packaging
    GROUP BY pack, bottle_volume_ml
    HAVING COUNT(*) > 1
) d
UNION ALL
SELECT
    12,
    'fact_dimension_join_failures',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM dw.fact_sales f
LEFT JOIN dw.dim_date d ON d.date_key = f.date_key
LEFT JOIN dw.dim_store s ON s.store_key = f.store_key
LEFT JOIN dw.dim_product p ON p.product_key = f.product_key
LEFT JOIN dw.dim_category c ON c.category_key = f.category_key
LEFT JOIN dw.dim_vendor v ON v.vendor_key = f.vendor_key
LEFT JOIN dw.dim_packaging pk ON pk.packaging_key = f.packaging_key
WHERE d.date_key IS NULL
   OR s.store_key IS NULL
   OR p.product_key IS NULL
   OR c.category_key IS NULL
   OR v.vendor_key IS NULL
   OR pk.packaging_key IS NULL
UNION ALL
SELECT
    13,
    'raw_negative_measure_rows_excluded_from_fact',
    CAST(COUNT_BIG(*) AS DECIMAL(38,4)),
    'INFO'
FROM stg.iowa_liquor_sales_raw
WHERE sale_dollars < 0
   OR bottles_sold < 0
   OR volume_sold_liters < 0
UNION ALL
SELECT
    14,
    'eligible_staging_vs_fact_sales_difference',
    CAST(ABS(COALESCE(stg.total_sales, 0) - COALESCE(fact.total_sales, 0)) AS DECIMAL(38,4)),
    CASE
        WHEN ABS(COALESCE(stg.total_sales, 0) - COALESCE(fact.total_sales, 0)) <= 0.01
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM (
    SELECT SUM(COALESCE(sale_dollars, 0)) AS total_sales
    FROM stg.iowa_liquor_sales_raw
    WHERE COALESCE(sale_dollars, 0) >= 0
      AND COALESCE(bottles_sold, 0) >= 0
      AND COALESCE(volume_sold_liters, 0) >= 0
) stg
CROSS JOIN (
    SELECT SUM(sale_dollars) AS total_sales
    FROM dw.fact_sales
) fact
)
SELECT
    check_name,
    check_value,
    result
FROM quality_checks
ORDER BY sort_order;
GO

PRINT '';
PRINT '===========================================================================';
PRINT '  RAPORT ZAKONCZONY';
PRINT '===========================================================================';
PRINT '';

SELECT
    'Raport 06 zakonczony' AS status,
    SYSDATETIME() AS finished_at_local,
    SYSUTCDATETIME() AS finished_at_utc;
GO
