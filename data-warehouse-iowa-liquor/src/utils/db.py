from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
from urllib.parse import quote_plus

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config import SqlServerConfig


def get_sqlserver_config() -> SqlServerConfig:
    return SqlServerConfig()


def get_pyodbc_connection(
    config: SqlServerConfig | None = None,
    database: str | None = None,
    autocommit: bool = False,
) -> pyodbc.Connection:
    sql_config = config or get_sqlserver_config()
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

    batches = [batch.strip() for batch in script.split("GO") if batch.strip()]
    with sqlserver_connection(config) as connection:
        cursor = connection.cursor()
        for batch in batches:
            cursor.execute(batch)


def run_sql_script_on_master(script_path: str, config: SqlServerConfig | None = None) -> None:
    with open(script_path, "r", encoding="utf-8") as sql_file:
        script = sql_file.read()

    batches = [batch.strip() for batch in script.split("GO") if batch.strip()]
    with sqlserver_connection(config, database="master", autocommit=True) as connection:
        cursor = connection.cursor()
        for batch in batches:
            cursor.execute(batch)
