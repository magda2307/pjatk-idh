IF OBJECT_ID('stg.iowa_liquor_sales_raw', 'U') IS NULL
BEGIN
    CREATE TABLE stg.iowa_liquor_sales_raw (
        staging_key BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        source_file NVARCHAR(260) NULL,
        load_timestamp DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        invoice_and_item_number NVARCHAR(80) NULL,
        date DATE NULL,
        store_number NVARCHAR(40) NULL,
        store_name NVARCHAR(255) NULL,
        address NVARCHAR(255) NULL,
        city NVARCHAR(120) NULL,
        zip_code NVARCHAR(20) NULL,
        store_location NVARCHAR(500) NULL,
        county_number NVARCHAR(40) NULL,
        county NVARCHAR(120) NULL,
        category NVARCHAR(40) NULL,
        category_name NVARCHAR(255) NULL,
        vendor_number NVARCHAR(40) NULL,
        vendor_name NVARCHAR(255) NULL,
        item_number NVARCHAR(40) NULL,
        item_description NVARCHAR(255) NULL,
        pack INT NULL,
        bottle_volume_ml INT NULL,
        proof DECIMAL(18,4) NULL,
        state_bottle_cost DECIMAL(18,4) NULL,
        state_bottle_retail DECIMAL(18,4) NULL,
        bottles_sold DECIMAL(18,4) NULL,
        sale_dollars DECIMAL(18,4) NULL,
        volume_sold_liters DECIMAL(18,4) NULL,
        volume_sold_gallons DECIMAL(18,4) NULL,
        latitude DECIMAL(18,8) NULL,
        longitude DECIMAL(18,8) NULL,
        source_row_hash CHAR(64) NULL
    );
END;
GO
