from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.config import EXTRACT_MANIFEST_PATH, RAW_DATA_DIR
from src.utils.db import sqlserver_connection
from src.utils.logging_utils import get_logger


logger = get_logger(__name__)


STAGING_COLUMNS = [
    "source_file",
    "invoice_and_item_number",
    "date",
    "store_number",
    "store_name",
    "address",
    "city",
    "zip_code",
    "store_location",
    "county_number",
    "county",
    "category",
    "category_name",
    "vendor_number",
    "vendor_name",
    "item_number",
    "item_description",
    "pack",
    "bottle_volume_ml",
    "proof",
    "state_bottle_cost",
    "state_bottle_retail",
    "bottles_sold",
    "sale_dollars",
    "volume_sold_liters",
    "volume_sold_gallons",
    "latitude",
    "longitude",
    "source_row_hash",
]

TEXT_COLUMNS = [
    "source_file",
    "invoice_and_item_number",
    "store_number",
    "store_name",
    "address",
    "city",
    "zip_code",
    "store_location",
    "county_number",
    "county",
    "category",
    "category_name",
    "vendor_number",
    "vendor_name",
    "item_number",
    "item_description",
    "source_row_hash",
]

NUMERIC_COLUMNS = [
    "pack",
    "bottle_volume_ml",
    "proof",
    "state_bottle_cost",
    "state_bottle_retail",
    "bottles_sold",
    "sale_dollars",
    "volume_sold_liters",
    "volume_sold_gallons",
    "latitude",
    "longitude",
]

SOURCE_COLUMN_ALIASES = {
    "invoice_line_no": "invoice_and_item_number",
    "store": "store_number",
    "name": "store_name",
    "zipcode": "zip_code",
    "vendor_no": "vendor_number",
    "itemno": "item_number",
    "im_desc": "item_description",
    "sale_bottles": "bottles_sold",
    "sale_liters": "volume_sold_liters",
    "sale_gallons": "volume_sold_gallons",
}


def normalize_column_name(column_name: str) -> str:
    column = column_name.strip().lower()
    column = re.sub(r"[^a-z0-9]+", "_", column)
    return column.strip("_")


def normalize_text_value(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_identifier_value(value: object) -> str | None:
    text = normalize_text_value(value)
    return text.upper() if text else None


def normalize_name_value(value: object) -> str | None:
    text = normalize_text_value(value)
    if not text:
        return None
    return text.title()


def normalize_zip_code(value: object) -> str | None:
    text = normalize_text_value(value)
    if not text:
        return None
    digits = re.sub(r"[^0-9]", "", text)
    if len(digits) >= 5:
        return digits[:5]
    return text


def parse_location_value(location: object) -> tuple[float | None, float | None]:
    if not isinstance(location, str):
        return None, None
    match = re.search(r"\((-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\)", location)
    if not match:
        return None, None
    return float(match.group(1)), float(match.group(2))


def clean_money_or_number(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def build_row_hash(row: pd.Series) -> str:
    values = ["" if pd.isna(value) else str(value) for value in row.tolist()]
    return hashlib.sha256("|".join(values).encode("utf-8")).hexdigest()


def read_and_prepare_csv(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    df.columns = [normalize_column_name(column) for column in df.columns]
    df = df.rename(columns=SOURCE_COLUMN_ALIASES)
    df["source_file"] = file_path.name

    if "latitude" not in df.columns or "longitude" not in df.columns:
        parsed_locations = df.get("store_location", pd.Series(dtype=str)).apply(parse_location_value)
        df["latitude"] = parsed_locations.apply(lambda value: value[0])
        df["longitude"] = parsed_locations.apply(lambda value: value[1])

    for column in STAGING_COLUMNS:
        if column not in df.columns:
            df[column] = None

    hash_input_columns = [
        "invoice_and_item_number",
        "date",
        "store_number",
        "item_number",
        "sale_dollars",
        "bottles_sold",
        "source_file",
    ]
    df["source_row_hash"] = df[hash_input_columns].apply(build_row_hash, axis=1)

    identifier_columns = [
        "invoice_and_item_number",
        "store_number",
        "county_number",
        "category",
        "vendor_number",
        "item_number",
    ]
    for column in identifier_columns:
        df[column] = df[column].apply(normalize_identifier_value)

    title_case_columns = [
        "city",
        "county",
    ]
    for column in title_case_columns:
        df[column] = df[column].apply(normalize_name_value)

    generic_text_columns = [
        "source_file",
        "store_name",
        "address",
        "store_location",
        "category_name",
        "vendor_name",
        "item_description",
    ]
    for column in generic_text_columns:
        df[column] = df[column].apply(normalize_text_value)

    df["zip_code"] = df["zip_code"].apply(normalize_zip_code)

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    for column in NUMERIC_COLUMNS:
        df[column] = clean_money_or_number(df[column])

    for column in TEXT_COLUMNS:
        df[column] = df[column].replace({"": None})

    return df[STAGING_COLUMNS].astype(object).where(pd.notnull(df[STAGING_COLUMNS]), None)


def find_raw_files(raw_dir: Path | str = RAW_DATA_DIR) -> list[Path]:
    if EXTRACT_MANIFEST_PATH.exists():
        manifest = json.loads(EXTRACT_MANIFEST_PATH.read_text(encoding="utf-8"))
        files = [Path(file_path) for file_path in manifest.get("files", [])]
        existing_files = [file_path for file_path in files if file_path.exists()]
        if existing_files:
            logger.info("Using %s raw files from extract manifest", len(existing_files))
            return existing_files
    return sorted(Path(raw_dir).glob("iowa_liquor_sales_*_part_*.csv"))


def truncate_staging() -> None:
    with sqlserver_connection() as connection:
        connection.cursor().execute("TRUNCATE TABLE stg.iowa_liquor_sales_raw")
    logger.info("Truncated stg.iowa_liquor_sales_raw")


def insert_dataframe_to_staging(df: pd.DataFrame, batch_size: int = 5000) -> None:
    placeholders = ", ".join(["?"] * len(STAGING_COLUMNS))
    columns = ", ".join(STAGING_COLUMNS)
    insert_sql = f"INSERT INTO stg.iowa_liquor_sales_raw ({columns}) VALUES ({placeholders})"

    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    with sqlserver_connection() as connection:
        cursor = connection.cursor()
        cursor.fast_executemany = True
        for start in range(0, len(rows), batch_size):
            cursor.executemany(insert_sql, rows[start : start + batch_size])


def load_staging_from_raw_files(raw_files: Iterable[Path] | None = None) -> int:
    files = list(raw_files) if raw_files is not None else find_raw_files()
    if not files:
        raise FileNotFoundError(f"No raw Iowa Liquor CSV files found in {RAW_DATA_DIR}")

    truncate_staging()
    total_rows = 0
    for file_path in files:
        df = read_and_prepare_csv(file_path)
        insert_dataframe_to_staging(df)
        total_rows += len(df)
        logger.info("Loaded %s rows from %s into staging", len(df), file_path.name)

    logger.info("Loaded %s total rows into stg.iowa_liquor_sales_raw", total_rows)
    return total_rows


if __name__ == "__main__":
    load_staging_from_raw_files()
