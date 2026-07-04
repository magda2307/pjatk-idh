from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.load.sqlserver_loader import parse_location_value, read_and_prepare_csv


def test_parse_location_value_handles_socrata_point_lon_lat() -> None:
    latitude, longitude = parse_location_value("POINT (-93.61378 41.60575)")

    assert latitude == 41.60575
    assert longitude == -93.61378


def test_read_and_prepare_csv_populates_coordinates_from_store_location() -> None:
    raw_file = PROJECT_ROOT / "data" / "raw" / "iowa_liquor_sales_2023_part_000.csv"

    df = read_and_prepare_csv(raw_file)

    first_row = df.iloc[0]
    assert first_row["latitude"] == 41.60575
    assert first_row["longitude"] == -93.61378
    assert df["latitude"].notna().any()
    assert df["longitude"].notna().any()
