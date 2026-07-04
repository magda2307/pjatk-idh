from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import IowaLiquorExtractConfig


def test_iowa_liquor_extract_defaults_use_full_year_2023_with_laptop_safe_pages() -> None:
    config = IowaLiquorExtractConfig()

    assert config.start_date == "2023-01-01"
    assert config.end_date == "2023-12-31"
    assert config.limit == 5000
