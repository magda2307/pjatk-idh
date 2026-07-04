from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
from urllib.parse import quote_plus

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config import SqlServerConfig

_DEMO_LOGIN_READY = False


def get_sqlserver_config() -> SqlServerConfig:
    return SqlServerConfig()


def _connection_string_for(
    config: SqlServerConfig,
    user: str,
    password: str,
    database: str | None = None,
) -> str:
    target_database = database or config.database
    return (
        f"DRIVER={{{config.driver}}};"
        f"SERVER={config.host},{config.port};"
        f"DATABASE={target_database};"
        f"UID={user};"
        f"PWD={password};"
        "Encrypt=yes;"
        f"TrustServerCertificate={config.trust_certificate};"
    )


def ensure_demo_sql_login(config: SqlServerConfig) -> None:
    global _DEMO_LOGIN_READY
    if _DEMO_LOGIN_READY or config.user.lower() == config.bootstrap_user.lower():
        return

    bootstrap_connection_string = _connection_string_for(
        config,
        user=config.bootstrap_user,
        password=config.bootstrap_password,
        database="master",
    )
    login_name = config.user.replace("]", "]]")
    login_password = config.password.replace("'", "''")
    setup_sql = f"""
    IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = N'{login_name}')
        CREATE LOGIN [{login_name}]
        WITH PASSWORD = N'{login_password}', CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF;
    ELSE
        ALTER LOGIN [{login_name}]
        WITH PASSWORD = N'{login_password}', CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF;

    IF IS_SRVROLEMEMBER('sysadmin', N'{login_name}') = 0
        ALTER SERVER ROLE sysadmin ADD MEMBER [{login_name}];
    """
    with pyodbc.connect(bootstrap_connection_string, autocommit=True) as connection:
        connection.cursor().execute(setup_sql)

    _DEMO_LOGIN_READY = True


def get_pyodbc_connection(
    config: SqlServerConfig | None = None,
    database: str | None = None,
    autocommit: bool = False,
) -> pyodbc.Connection:
    sql_config = config or get_sqlserver_config()
    ensure_demo_sql_login(sql_config)
    connection_string = sql_config.odbc_connection_string
    if database:
        connection_string = connection_string.replace(
            f"DATABASE={sql_config.database};", f"DATABASE={database};"
        )
    return pyodbc.connect(connection_string, autocommit=autocommit)


def get_sqlalchemy_engine(config: SqlServerConfig | None = None) -> Engine:
    sql_config = config or get_sqlserver_config()
    params = quote_plus(sql_config.odbc_connection_string)
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)


def split_sql_batches(script: str) -> list[str]:
    batches: list[str] = []
    current_batch: list[str] = []
    for line in script.splitlines(keepends=True):
        if line.strip().upper() == "GO":
            batch = "".join(current_batch).strip()
            if batch:
                batches.append(batch)
            current_batch = []
        else:
            current_batch.append(line)

    batch = "".join(current_batch).strip()
    if batch:
        batches.append(batch)
    return batches


@contextmanager
def sqlserver_connection(
    config: SqlServerConfig | None = None,
    database: str | None = None,
    autocommit: bool = False,
) -> Iterator[pyodbc.Connection]:
    connection = get_pyodbc_connection(config, database=database, autocommit=autocommit)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def run_sql_script(script_path: str, config: SqlServerConfig | None = None) -> None:
    with open(script_path, "r", encoding="utf-8") as sql_file:
        script = sql_file.read()

    with sqlserver_connection(config) as connection:
        cursor = connection.cursor()
        for batch in split_sql_batches(script):
            cursor.execute(batch)


def run_sql_script_on_master(script_path: str, config: SqlServerConfig | None = None) -> None:
    with open(script_path, "r", encoding="utf-8") as sql_file:
        script = sql_file.read()

    with sqlserver_connection(config, database="master", autocommit=True) as connection:
        cursor = connection.cursor()
        for batch in split_sql_batches(script):
            cursor.execute(batch)
