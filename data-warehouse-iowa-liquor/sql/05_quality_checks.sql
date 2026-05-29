SELECT 'staging_row_count' AS check_name, COUNT_BIG(*) AS check_value
FROM stg.iowa_liquor_sales_raw;

SELECT 'fact_row_count' AS check_name, COUNT_BIG(*) AS check_value
FROM dw.fact_sales;

SELECT 'null_foreign_keys' AS check_name, COUNT_BIG(*) AS check_value
FROM dw.fact_sales
WHERE date_key IS NULL
   OR store_key IS NULL
   OR product_key IS NULL
   OR category_key IS NULL
   OR vendor_key IS NULL
   OR packaging_key IS NULL;

SELECT 'negative_measures' AS check_name, COUNT_BIG(*) AS check_value
FROM dw.fact_sales
WHERE sale_dollars < 0
   OR bottles_sold < 0
   OR volume_sold_liters < 0;

SELECT 'duplicate_store_numbers' AS check_name, COUNT_BIG(*) AS check_value
FROM (
    SELECT store_number
    FROM dw.dim_store
    GROUP BY store_number
    HAVING COUNT(*) > 1
) d;

SELECT 'duplicate_product_numbers' AS check_name, COUNT_BIG(*) AS check_value
FROM (
    SELECT item_number
    FROM dw.dim_product
    GROUP BY item_number
    HAVING COUNT(*) > 1
) d;

SELECT 'duplicate_category_numbers' AS check_name, COUNT_BIG(*) AS check_value
FROM (
    SELECT category_number
    FROM dw.dim_category
    GROUP BY category_number
    HAVING COUNT(*) > 1
) d;

SELECT 'duplicate_vendor_numbers' AS check_name, COUNT_BIG(*) AS check_value
FROM (
    SELECT vendor_number
    FROM dw.dim_vendor
    GROUP BY vendor_number
    HAVING COUNT(*) > 1
) d;

SELECT 'duplicate_packaging_keys' AS check_name, COUNT_BIG(*) AS check_value
FROM (
    SELECT pack, bottle_volume_ml
    FROM dw.dim_packaging
    GROUP BY pack, bottle_volume_ml
    HAVING COUNT(*) > 1
) d;

SELECT 'fact_dimension_join_failures' AS check_name, COUNT_BIG(*) AS check_value
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
   OR pk.packaging_key IS NULL;

SELECT 'raw_negative_measure_rows_excluded_from_fact' AS check_name, COUNT_BIG(*) AS check_value
FROM stg.iowa_liquor_sales_raw
WHERE sale_dollars < 0
   OR bottles_sold < 0
   OR volume_sold_liters < 0;

SELECT 'eligible_staging_vs_fact_sales_difference' AS check_name,
       CAST(ABS(stg.total_sales - fact.total_sales) AS DECIMAL(18,4)) AS check_value
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
) fact;
