from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context


@dag(
    dag_id="iowa_liquor_etl",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["data-warehouse", "iowa-liquor"],
    params={
        "start_date": Param(
            "2023-01-01",
            type="string",
            format="date",
            description="Data początkowa zakresu danych. Format: YYYY-MM-DD, np. 2023-01-01.",
        ),
        "end_date": Param(
            "2023-12-31",
            type="string",
            format="date",
            description="Data końcowa zakresu danych. Format: YYYY-MM-DD, np. 2023-12-31.",
        ),
        "limit": Param(
            50000,
            type="integer",
            minimum=1,
            description="Limit wierszy pobieranych w jednej stronie API. Domyślnie: 50000.",
        ),
    },
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "execution_timeout": timedelta(minutes=30),
    },
)
def iowa_liquor_etl() -> None:
    @task
    def extract_iowa_liquor_sales() -> list[str]:
        from src.config import IowaLiquorExtractConfig
        from src.extract.socrata_extract import extract_iowa_liquor_sales

        context = get_current_context()
        dag_run_conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
        params = context.get("params", {})
        extract_config = IowaLiquorExtractConfig(
            start_date=str(dag_run_conf.get("start_date") or params.get("start_date")),
            end_date=str(dag_run_conf.get("end_date") or params.get("end_date")),
            limit=int(dag_run_conf.get("limit") or params.get("limit")),
        )
        return [
            str(file_path)
            for file_path in extract_iowa_liquor_sales(config=extract_config)
        ]

    @task
    def create_sql_objects() -> None:
        from src.transform.warehouse_transform import create_sql_objects

        create_sql_objects()

    @task
    def load_staging(raw_file_paths: list[str]) -> int:
        from pathlib import Path

        from src.load.sqlserver_loader import load_staging_from_raw_files

        return load_staging_from_raw_files([Path(file_path) for file_path in raw_file_paths])

    @task
    def load_dimensions() -> None:
        from src.transform.warehouse_transform import load_dimensions

        load_dimensions()

    @task
    def load_fact_sales() -> int:
        from src.transform.warehouse_transform import load_fact_sales

        return load_fact_sales()

    @task
    def create_semantic_views() -> None:
        from src.transform.warehouse_transform import create_semantic_views

        create_semantic_views()

    @task
    def run_quality_checks() -> list[tuple[str, str]]:
        from src.transform.warehouse_transform import run_quality_checks

        return run_quality_checks()

    raw_files = extract_iowa_liquor_sales()
    objects_created = create_sql_objects()
    staged_rows = load_staging(raw_files)
    dimensions_loaded = load_dimensions()
    fact_rows = load_fact_sales()
    views_created = create_semantic_views()
    checks = run_quality_checks()

    raw_files >> objects_created >> staged_rows >> dimensions_loaded >> fact_rows >> views_created >> checks


iowa_liquor_etl()
