CREATE OR ALTER VIEW sem.vw_sales_overview AS
SELECT
    d.date,
    d.day,
    d.month,
    d.month_name_en,
    d.month_name_pl,
    d.quarter,
    d.year,
    d.year_month,
    s.store_number,
    s.store_name,
    s.address,
    s.city AS store_city,
    s.county AS store_county,
    s.state_name,
    s.county,
    s.city,
    s.zip_code,
    s.latitude,
    s.longitude,
    p.item_number,
    p.item_description,
    pk.pack,
    pk.bottle_volume_ml,
    pk.volume_group,
    c.category_number,
    c.category_name,
    v.vendor_number,
    v.vendor_name,
    f.invoice_number,
    f.sales_line_count,
    f.bottles_sold,
    f.sale_dollars,
    f.volume_sold_liters,
    f.volume_sold_gallons,
    f.state_bottle_cost,
    f.state_bottle_retail,
    f.margin_amount
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
JOIN dw.dim_store s ON s.store_key = f.store_key
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_packaging pk ON pk.packaging_key = f.packaging_key
JOIN dw.dim_category c ON c.category_key = f.category_key
JOIN dw.dim_vendor v ON v.vendor_key = f.vendor_key;
GO

CREATE OR ALTER VIEW sem.vw_sales_by_month AS
SELECT
    d.year,
    d.quarter,
    d.month,
    d.year_month,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    COUNT(DISTINCT f.invoice_number) AS invoice_count,
    COUNT(DISTINCT f.store_key) AS store_count
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.quarter, d.month, d.year_month;
GO

CREATE OR ALTER VIEW sem.vw_category_sales_over_time AS
SELECT
    d.year,
    d.quarter,
    d.month,
    d.year_month,
    c.category_name,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    COUNT(DISTINCT f.invoice_number) AS invoice_count,
    COUNT(DISTINCT f.store_key) AS store_count
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
JOIN dw.dim_category c ON c.category_key = f.category_key
GROUP BY d.year, d.quarter, d.month, d.year_month, c.category_name;
GO

CREATE OR ALTER VIEW sem.vw_sales_by_category AS
WITH totals AS (
    SELECT SUM(sale_dollars) AS all_sales FROM dw.fact_sales
)
SELECT
    c.category_name,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    SUM(f.margin_amount) / NULLIF(SUM(f.bottles_sold), 0) AS avg_margin_per_bottle,
    CAST(100.0 * SUM(f.sale_dollars) / NULLIF(MAX(t.all_sales), 0) AS DECIMAL(9,2)) AS sales_share_percent
FROM dw.fact_sales f
JOIN dw.dim_category c ON c.category_key = f.category_key
CROSS JOIN totals t
GROUP BY c.category_name;
GO

CREATE OR ALTER VIEW sem.vw_sales_by_store AS
SELECT
    s.store_number,
    s.store_name,
    s.city,
    s.county,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    COUNT(DISTINCT f.invoice_number) AS invoice_count
FROM dw.fact_sales f
JOIN dw.dim_store s ON s.store_key = f.store_key
GROUP BY s.store_number, s.store_name, s.city, s.county;
GO

CREATE OR ALTER VIEW sem.vw_sales_by_vendor AS
WITH totals AS (
    SELECT SUM(sale_dollars) AS all_sales FROM dw.fact_sales
)
SELECT
    v.vendor_name,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    CAST(100.0 * SUM(f.sale_dollars) / NULLIF(MAX(t.all_sales), 0) AS DECIMAL(9,2)) AS sales_share_percent
FROM dw.fact_sales f
JOIN dw.dim_vendor v ON v.vendor_key = f.vendor_key
CROSS JOIN totals t
GROUP BY v.vendor_name;
GO

CREATE OR ALTER VIEW sem.vw_sales_by_geography AS
SELECT
    s.state_name,
    s.county,
    s.city,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    COUNT(DISTINCT f.store_key) AS store_count
FROM dw.fact_sales f
JOIN dw.dim_store s ON s.store_key = f.store_key
GROUP BY s.state_name, s.county, s.city;
GO

CREATE OR ALTER VIEW sem.vw_top_products AS
SELECT
    p.item_number,
    p.item_description,
    c.category_name,
    v.vendor_name,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count
FROM dw.fact_sales f
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_category c ON c.category_key = f.category_key
JOIN dw.dim_vendor v ON v.vendor_key = f.vendor_key
GROUP BY p.item_number, p.item_description, c.category_name, v.vendor_name;
GO

DROP VIEW IF EXISTS sem.vw_margin_analysis;
GO

CREATE VIEW sem.vw_margin_analysis AS
SELECT
    c.category_name,
    v.vendor_name,
    p.item_description,
    AVG(f.state_bottle_cost) AS state_bottle_cost,
    AVG(f.state_bottle_retail) AS state_bottle_retail,
    AVG(f.state_bottle_retail - f.state_bottle_cost) AS avg_unit_margin,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sale_dollars) AS total_sales
FROM dw.fact_sales f
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_category c ON c.category_key = f.category_key
JOIN dw.dim_vendor v ON v.vendor_key = f.vendor_key
GROUP BY c.category_name, v.vendor_name, p.item_description;
GO

CREATE OR ALTER VIEW sem.vw_volume_vs_revenue AS
SELECT
    s.state_name,
    s.county,
    s.city,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.sale_dollars) / NULLIF(SUM(f.volume_sold_liters), 0) AS sales_per_liter,
    COUNT(DISTINCT f.store_key) AS store_count
FROM dw.fact_sales f
JOIN dw.dim_store s ON s.store_key = f.store_key
GROUP BY s.state_name, s.county, s.city;
GO

CREATE OR ALTER VIEW sem.vw_avg_sales_per_store_by_month_region AS
WITH monthly_store_sales AS (
    SELECT
        d.year,
        d.quarter,
        d.month,
        d.year_month,
        s.state_name,
        s.county,
        s.city,
        s.store_key,
        SUM(f.sale_dollars) AS store_month_sales,
        SUM(f.bottles_sold) AS store_month_bottles,
        SUM(f.volume_sold_liters) AS store_month_volume_liters,
        SUM(f.margin_amount) AS store_month_margin
    FROM dw.fact_sales f
    JOIN dw.dim_date d ON d.date_key = f.date_key
    JOIN dw.dim_store s ON s.store_key = f.store_key
    GROUP BY
        d.year,
        d.quarter,
        d.month,
        d.year_month,
        s.state_name,
        s.county,
        s.city,
        s.store_key
)
SELECT
    year,
    quarter,
    month,
    year_month,
    state_name,
    county,
    city,
    COUNT(*) AS store_count,
    AVG(store_month_sales) AS avg_sales_per_store,
    AVG(store_month_bottles) AS avg_bottles_per_store,
    AVG(store_month_volume_liters) AS avg_volume_liters_per_store,
    AVG(store_month_margin) AS avg_margin_per_store
FROM monthly_store_sales
GROUP BY year, quarter, month, year_month, state_name, county, city;
GO

CREATE OR ALTER VIEW sem.vw_kpi_summary AS
SELECT
    SUM(f.sale_dollars) AS total_sales,
    SUM(f.margin_amount) AS total_margin,
    SUM(f.sales_line_count) AS sales_line_count,
    SUM(f.bottles_sold) AS total_bottles_sold,
    SUM(f.volume_sold_liters) AS total_volume_liters,
    COUNT(DISTINCT f.invoice_number) AS invoice_count,
    COUNT(DISTINCT f.store_key) AS store_count,
    COUNT(DISTINCT f.product_key) AS product_count,
    COUNT(DISTINCT f.category_key) AS category_count,
    COUNT(DISTINCT f.vendor_key) AS vendor_count
FROM dw.fact_sales f;
GO
