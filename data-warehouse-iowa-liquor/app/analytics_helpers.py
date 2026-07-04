from __future__ import annotations

from numbers import Number

import pandas as pd


DAY_TYPE_LABELS = {
    0: "Dzień roboczy",
    1: "Weekend",
}
UNKNOWN_DAY_TYPE_LABEL = "Nieznany typ dnia"

_TRUE_VALUES = {"1", "true", "t", "yes", "y", "weekend"}
_FALSE_VALUES = {
    "0",
    "false",
    "f",
    "no",
    "n",
    "weekday",
    "week day",
    "dzień roboczy",
    "dzien roboczy",
}


def normalize_is_weekend_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, Number):
        if value == 0:
            return 0
        if value == 1:
            return 1

    text_value = str(value).strip().lower()
    if text_value in _TRUE_VALUES:
        return 1
    if text_value in _FALSE_VALUES:
        return 0
    return pd.NA


def normalize_is_weekend(series: pd.Series) -> pd.Series:
    return series.map(normalize_is_weekend_value).astype("Int64")


def normalize_semantic_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if "is_weekend" not in df.columns:
        return df

    normalized = df.copy()
    normalized["is_weekend"] = normalize_is_weekend(normalized["is_weekend"])
    return normalized


def add_day_type(df: pd.DataFrame) -> pd.DataFrame:
    result = normalize_semantic_dataframe(df)
    if "is_weekend" not in result.columns:
        return result

    result["day_type"] = result["is_weekend"].map(DAY_TYPE_LABELS).fillna(UNKNOWN_DAY_TYPE_LABEL)
    return result


def add_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if "day_count" not in df.columns:
        return df

    result = df.copy()
    denominator = pd.to_numeric(result["day_count"], errors="coerce").astype(float)
    denominator = denominator.mask(denominator == 0)

    metric_sources = {
        "avg_daily_sales": "total_sales",
        "avg_daily_margin": "total_margin",
        "avg_daily_bottles_sold": "total_bottles_sold",
        "avg_daily_volume_liters": "total_volume_liters",
        "avg_daily_invoice_count": "invoice_count",
    }
    for target_column, source_column in metric_sources.items():
        if source_column in result.columns:
            result[target_column] = pd.to_numeric(result[source_column], errors="coerce").astype(float) / denominator

    return result
