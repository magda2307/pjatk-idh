from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def test_iowa_liquor_extract_defaults_use_full_year_2023_with_laptop_safe_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.delenv("IOWA_START_DATE", raising=False)
    monkeypatch.delenv("IOWA_END_DATE", raising=False)
    monkeypatch.delenv("SOCRATA_LIMIT", raising=False)

    import src.config as config_module

    config_module = importlib.reload(config_module)
    config = config_module.IowaLiquorExtractConfig()

    assert config.start_date == "2023-01-01"
    assert config.end_date == "2023-12-31"
    assert config.limit == 5000
