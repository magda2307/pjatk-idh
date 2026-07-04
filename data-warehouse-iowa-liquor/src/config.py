from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _project_root() -> Path:
    configured_root = os.getenv("PROJECT_ROOT")
    if configured_root:
        return Path(configured_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _project_root()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
EXTRACT_MANIFEST_PATH = PROCESSED_DATA_DIR / "extract_manifest.json"


@dataclass(frozen=True)
class IowaLiquorExtractConfig:
    start_date: str = os.getenv("IOWA_START_DATE", "2023-01-01")
    end_date: str = os.getenv("IOWA_END_DATE", "2023-12-31")
    limit: int = int(os.getenv("SOCRATA_LIMIT", "50000"))
    app_token: str | None = os.getenv("SOCRATA_APP_TOKEN") or None
    base_url: str = "https://data.iowa.gov/resource/m3tr-qhgy.csv"


@dataclass(frozen=True)
class SqlServerConfig:
    host: str = os.getenv("SQLSERVER_HOST", "localhost")
    port: int = int(os.getenv("SQLSERVER_PORT", "1433"))
    database: str = os.getenv("SQLSERVER_DATABASE", "IowaLiquorDW")
    user: str = os.getenv("SQLSERVER_USER", "admin")
    password: str = os.getenv("SQLSERVER_PASSWORD", "admin")
    driver: str = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    trust_certificate: str = os.getenv("SQLSERVER_TRUST_CERTIFICATE", "yes")
    bootstrap_user: str = os.getenv("SQLSERVER_BOOTSTRAP_USER", "sa")
    bootstrap_password: str = os.getenv("SQLSERVER_BOOTSTRAP_PASSWORD", "YourStrongPassword123")

    @property
    def odbc_connection_string(self) -> str:
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            "Encrypt=yes;"
            f"TrustServerCertificate={self.trust_certificate};"
        )
