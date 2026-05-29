IF OBJECT_ID('dw.fact_sales', 'U') IS NOT NULL
   AND (
       COL_LENGTH('dw.fact_sales', 'geography_key') IS NOT NULL
       OR COL_LENGTH('dw.fact_sales', 'packaging_key') IS NULL
       OR COL_LENGTH('dw.fact_sales', 'sales_line_count') IS NULL
   )
BEGIN
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_date;
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_store;
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_product;
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_category;
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_vendor;
    ALTER TABLE dw.fact_sales DROP CONSTRAINT IF EXISTS FK_fact_sales_dim_packaging;
    DROP TABLE dw.fact_sales;
END;
GO

IF OBJECT_ID('dw.dim_geography', 'U') IS NOT NULL
    DROP TABLE dw.dim_geography;
GO

IF OBJECT_ID('dw.dim_date', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_date (
        date_key INT NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        day INT NOT NULL,
        month INT NOT NULL,
        month_name_en VARCHAR(20) NOT NULL,
        quarter INT NOT NULL,
        year INT NOT NULL,
        day_of_week INT NOT NULL,
        day_name_en VARCHAR(20) NOT NULL,
        day_name_pl VARCHAR(20) NOT NULL,
        is_weekend BIT NOT NULL,
        year_month VARCHAR(7) NOT NULL,
        month_name_pl VARCHAR(20) NOT NULL
    );
END;
GO

IF COL_LENGTH('dw.dim_date', 'day_name_pl') IS NULL
    ALTER TABLE dw.dim_date ADD day_name_pl VARCHAR(20) NULL;
GO
IF COL_LENGTH('dw.dim_date', 'month_name_pl') IS NULL
    ALTER TABLE dw.dim_date ADD month_name_pl VARCHAR(20) NULL;
GO

IF OBJECT_ID('dw.dim_store', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_store (
        store_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        store_number NVARCHAR(40) NOT NULL,
        store_name NVARCHAR(255) NULL,
        store_type NVARCHAR(80) NULL,
        address NVARCHAR(255) NULL,
        city NVARCHAR(120) NULL,
        zip_code NVARCHAR(20) NULL,
        county NVARCHAR(120) NULL,
        state_name NVARCHAR(40) NOT NULL DEFAULT 'Iowa',
        source_store_location NVARCHAR(500) NULL,
        latitude DECIMAL(18,8) NULL,
        longitude DECIMAL(18,8) NULL
    );
END;
GO

IF COL_LENGTH('dw.dim_store', 'state_name') IS NULL
    ALTER TABLE dw.dim_store ADD state_name NVARCHAR(40) NOT NULL CONSTRAINT DF_dim_store_state_name DEFAULT 'Iowa';
GO

IF OBJECT_ID('dw.dim_product', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_product (
        product_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        item_number NVARCHAR(40) NOT NULL,
        item_description NVARCHAR(255) NULL
    );
END;
GO

IF COL_LENGTH('dw.dim_product', 'proof') IS NOT NULL
    ALTER TABLE dw.dim_product DROP COLUMN proof;
GO
IF COL_LENGTH('dw.dim_product', 'bottle_volume_ml') IS NOT NULL
    ALTER TABLE dw.dim_product DROP COLUMN bottle_volume_ml;
GO
IF COL_LENGTH('dw.dim_product', 'pack') IS NOT NULL
    ALTER TABLE dw.dim_product DROP COLUMN pack;
GO

IF OBJECT_ID('dw.dim_category', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_category (
        category_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        category_number NVARCHAR(40) NOT NULL,
        category_name NVARCHAR(255) NULL
    );
END;
GO

IF OBJECT_ID('dw.dim_vendor', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_vendor (
        vendor_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        vendor_number NVARCHAR(40) NOT NULL,
        vendor_name NVARCHAR(255) NULL
    );
END;
GO

IF OBJECT_ID('dw.dim_packaging', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_packaging (
        packaging_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        pack INT NOT NULL,
        bottle_volume_ml INT NOT NULL,
        volume_group NVARCHAR(40) NOT NULL
    );
END;
GO

IF OBJECT_ID('dw.fact_sales', 'U') IS NULL
BEGIN
    CREATE TABLE dw.fact_sales (
        sales_key BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        date_key INT NOT NULL,
        store_key INT NOT NULL,
        product_key INT NOT NULL,
        category_key INT NOT NULL,
        vendor_key INT NOT NULL,
        packaging_key INT NOT NULL,
        invoice_number NVARCHAR(80) NULL,
        source_row_hash CHAR(64) NULL,
        sales_line_count INT NOT NULL DEFAULT 1,
        bottles_sold DECIMAL(18,4) NOT NULL,
        sale_dollars DECIMAL(18,4) NOT NULL,
        volume_sold_liters DECIMAL(18,4) NOT NULL,
        volume_sold_gallons DECIMAL(18,4) NOT NULL,
        state_bottle_cost DECIMAL(18,4) NOT NULL,
        state_bottle_retail DECIMAL(18,4) NOT NULL,
        margin_amount DECIMAL(18,4) NOT NULL,
        load_timestamp DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_date')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_date FOREIGN KEY (date_key) REFERENCES dw.dim_date(date_key);
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_store')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_store FOREIGN KEY (store_key) REFERENCES dw.dim_store(store_key);
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_product')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_product FOREIGN KEY (product_key) REFERENCES dw.dim_product(product_key);
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_category')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_category FOREIGN KEY (category_key) REFERENCES dw.dim_category(category_key);
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_vendor')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_vendor FOREIGN KEY (vendor_key) REFERENCES dw.dim_vendor(vendor_key);
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_fact_sales_dim_packaging')
    ALTER TABLE dw.fact_sales ADD CONSTRAINT FK_fact_sales_dim_packaging FOREIGN KEY (packaging_key) REFERENCES dw.dim_packaging(packaging_key);
GO
