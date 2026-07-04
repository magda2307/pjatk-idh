from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.analytics_helpers import add_daily_metrics, add_day_type


def test_add_day_type_handles_sql_driver_weekend_values_without_nan() -> None:
    df = pd.DataFrame(
        {
            "year_month": ["2023-01"] * 8,
            "is_weekend": ["0", "1", "False", "True", False, True, 0, 1],
            "invoice_number": [f"INV-{index}" for index in range(8)],
        }
    )

    result = add_day_type(df)
    invoices_by_month_day_type = (
        result.groupby(["year_month", "day_type"], dropna=False)
        .agg(invoice_count=("invoice_number", "nunique"))
        .reset_index()
    )

    assert result["is_weekend"].tolist() == [0, 1, 0, 1, 0, 1, 0, 1]
    assert result["day_type"].tolist() == [
        "Dzień roboczy",
        "Weekend",
        "Dzień roboczy",
        "Weekend",
        "Dzień roboczy",
        "Weekend",
        "Dzień roboczy",
        "Weekend",
    ]
    assert not invoices_by_month_day_type["day_type"].isna().any()
    assert set(invoices_by_month_day_type["day_type"]) == {"Dzień roboczy", "Weekend"}


def test_add_daily_metrics_normalizes_weekday_weekend_totals_by_day_count() -> None:
    df = pd.DataFrame(
        {
            "day_type": ["Dzień roboczy", "Weekend"],
            "day_count": [5, 2],
            "total_sales": [5000, 3000],
            "total_volume_liters": [100, 80],
            "invoice_count": [250, 120],
        }
    )

    result = add_daily_metrics(df)

    assert result["avg_daily_sales"].tolist() == [1000, 1500]
    assert result["avg_daily_volume_liters"].tolist() == [20, 40]
    assert result["avg_daily_invoice_count"].tolist() == [50, 60]
