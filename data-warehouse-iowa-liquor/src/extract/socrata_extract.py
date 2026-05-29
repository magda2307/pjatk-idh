from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import EXTRACT_MANIFEST_PATH, IowaLiquorExtractConfig, RAW_DATA_DIR
from src.utils.logging_utils import get_logger


logger = get_logger(__name__)


def validate_extract_config(config: IowaLiquorExtractConfig) -> None:
    try:
        start_date = datetime.strptime(config.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(config.end_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("IOWA_START_DATE and IOWA_END_DATE must use YYYY-MM-DD format") from exc

    if start_date > end_date:
        raise ValueError("IOWA_START_DATE cannot be later than IOWA_END_DATE")
    if config.limit <= 0:
        raise ValueError("SOCRATA_LIMIT must be greater than 0")


def build_requests_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def build_query_params(config: IowaLiquorExtractConfig, offset: int) -> dict[str, str | int]:
    return {
        "$where": (
            f"date between '{config.start_date}T00:00:00' "
            f"and '{config.end_date}T23:59:59'"
        ),
        "$limit": config.limit,
        "$offset": offset,
        "$order": "date, invoice_line_no",
    }


def count_csv_data_rows(file_path: Path) -> int:
    with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)
        if header is None:
            return 0
        return sum(1 for _ in reader)


def delete_existing_raw_parts(output_dir: Path, file_prefix: str) -> None:
    for file_path in output_dir.glob(f"{file_prefix}_part_*.csv"):
        file_path.unlink()


def write_extract_manifest(
    files: Iterable[Path],
    config: IowaLiquorExtractConfig,
    output_path: Path = EXTRACT_MANIFEST_PATH,
) -> None:
    files = list(files)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "start_date": config.start_date,
        "end_date": config.end_date,
        "limit": config.limit,
        "file_count": len(files),
        "total_rows": sum(count_csv_data_rows(file_path) for file_path in files),
        "files": [str(file_path) for file_path in files],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Wrote extract manifest to %s", output_path)


def download_page(
    config: IowaLiquorExtractConfig,
    offset: int,
    output_file: Path,
    session: requests.Session,
    timeout_seconds: int = 120,
) -> int:
    headers = {}
    if config.app_token:
        headers["X-App-Token"] = config.app_token

    logger.info("Requesting Iowa Liquor Sales page at offset %s", offset)
    response = session.get(
        config.base_url,
        params=build_query_params(config, offset),
        headers=headers,
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    output_file.write_bytes(response.content)
    row_count = count_csv_data_rows(output_file)
    logger.info("Saved %s rows to %s", row_count, output_file)
    return row_count


def extract_iowa_liquor_sales(
    output_dir: Path | str = RAW_DATA_DIR,
    config: IowaLiquorExtractConfig | None = None,
    clean_existing: bool = True,
) -> list[Path]:
    extract_config = config or IowaLiquorExtractConfig()
    validate_extract_config(extract_config)
    raw_dir = Path(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    year_label = extract_config.start_date[:4]
    file_prefix = f"iowa_liquor_sales_{year_label}"

    if clean_existing:
        delete_existing_raw_parts(raw_dir, file_prefix)

    downloaded_files: list[Path] = []
    offset = 0
    part_number = 0
    session = build_requests_session()
    try:
        while True:
            output_file = raw_dir / f"{file_prefix}_part_{part_number:03d}.csv"
            row_count = download_page(extract_config, offset, output_file, session=session)

            if row_count == 0:
                output_file.unlink(missing_ok=True)
                logger.info("No rows returned at offset %s. Extraction finished.", offset)
                break

            downloaded_files.append(output_file)
            offset += extract_config.limit
            part_number += 1
    finally:
        session.close()

    total_rows = sum(count_csv_data_rows(file_path) for file_path in downloaded_files)
    write_extract_manifest(downloaded_files, extract_config)
    logger.info("Extraction complete. Files: %s, total rows: %s", len(downloaded_files), total_rows)
    return downloaded_files


def format_file_list(files: Iterable[Path]) -> str:
    return "\n".join(str(file_path) for file_path in files)


if __name__ == "__main__":
    files = extract_iowa_liquor_sales()
    logger.info("Downloaded files:\n%s", format_file_list(files))
