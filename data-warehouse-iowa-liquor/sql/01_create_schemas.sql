IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'sem')
    EXEC('CREATE SCHEMA sem');
GO
