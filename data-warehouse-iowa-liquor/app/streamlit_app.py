from __future__ import annotations

import json
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from sqlalchemy import create_engine

from app.analytics_helpers import DAY_TYPE_LABELS, add_daily_metrics, add_day_type, normalize_semantic_dataframe
from src.config import EXTRACT_MANIFEST_PATH, SqlServerConfig


st.set_page_config(
    page_title="Hurtownia Iowa Liquor Sales",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1.25rem;
            max-width: 1480px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        [data-testid="stMetric"] {
            background: #f8faf8;
            border: 1px solid #dce5dd;
            border-radius: 6px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] {
            color: #465449;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px;
            padding: 8px 14px;
        }
        [data-testid="stToolbar"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_engine():
    config = SqlServerConfig()
    params = quote_plus(config.odbc_connection_string)
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


@st.cache_data(ttl=300)
def read_view(view_name: str) -> pd.DataFrame:
    engine = get_engine()
    query = f"SELECT * FROM sem.{view_name}"
    with engine.connect() as connection:
        return normalize_semantic_dataframe(pd.read_sql(query, connection))


@st.cache_data(ttl=300)
def read_extract_manifest() -> dict[str, object] | None:
    if not EXTRACT_MANIFEST_PATH.exists():
        return None
    return json.loads(EXTRACT_MANIFEST_PATH.read_text(encoding="utf-8"))


def load_iowa_counties_geojson() -> dict | None:
    geojson_path = Path(__file__).parent / "data" / "iowa_counties.geojson"
    if geojson_path.exists():
        return json.loads(geojson_path.read_text(encoding="utf-8"))
    return None

def normalize_county_name(value: object) -> str | None:
    if pd.isna(value):
        return None
    county = str(value).strip()
    if not county:
        return None
    county = re.sub(r"\bcounty\b", "", county, flags=re.IGNORECASE)
    county = re.sub(r"[^0-9a-zA-Z]+", " ", county).strip().lower()
    return re.sub(r"\s+", " ", county) or None


def county_to_iowa_fips(value: object) -> str | None:
    if pd.isna(value):
        return None
    county = str(value).strip()
    if not county.isdigit():
        return None
    code = int(county)
    if len(county) == 5 and county.startswith("19"):
        return county
    if 1 <= code <= 999:
        return f"19{code:03d}"
    return None

def format_money(value: float) -> str:
    return f"${value:,.0f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_decimal(value: float) -> str:
    return f"{value:,.2f}"


COLUMN_LABELS = {
    "year": "Rok",
    "quarter": "Kwartał",
    "year_quarter": "Rok i kwartał",
    "year_month": "Miesiąc",
    "month": "Miesiąc",
    "day_type": "Typ dnia",
    "day_count": "Liczba dni w danych",
    "category_name": "Kategoria",
    "vendor_name": "Dostawca",
    "item_number": "Kod produktu",
    "item_description": "Produkt",
    "product": "Produkt",
    "volume_group": "Grupa opakowania",
    "bottle_volume_ml": "Pojemność butelki (ml)",
    "county": "County",
    "city": "Miasto",
    "geo_county": "County z mapy",
    "store_number": "Numer sklepu",
    "store_name": "Sklep",
    "rank": "Ranking",
    "total_sales": "Sprzedaż",
    "total_margin": "Marża",
    "total_bottles_sold": "Sprzedane butelki",
    "total_volume_liters": "Wolumen (litry)",
    "invoice_count": "Liczba faktur",
    "store_count": "Liczba sklepów",
    "avg_unit_margin": "Średnia marża jednostkowa",
    "avg_daily_sales": "Śr. sprzedaż / dzień",
    "avg_daily_margin": "Śr. marża / dzień",
    "avg_daily_bottles_sold": "Śr. butelki / dzień",
    "avg_daily_volume_liters": "Śr. wolumen / dzień",
    "avg_daily_invoice_count": "Śr. faktury / dzień",
    "avg_sales_per_store": "Średnia sprzedaż na sklep",
    "sales_share_percent": "Udział sprzedaży (%)",
    "sales_per_liter": "Sprzedaż na litr",
    "latitude": "Szerokość geogr.",
    "longitude": "Długość geogr.",
}


def localize_figure(fig):
    def localize_axis(axis) -> None:
        current = axis.title.text
        if current in COLUMN_LABELS:
            axis.update(title_text=COLUMN_LABELS[current])

    fig.for_each_xaxis(localize_axis)
    fig.for_each_yaxis(localize_axis)
    if fig.layout.legend and fig.layout.legend.title and fig.layout.legend.title.text in COLUMN_LABELS:
        fig.update_layout(legend_title_text=COLUMN_LABELS[fig.layout.legend.title.text])
    if fig.layout.coloraxis and fig.layout.coloraxis.colorbar.title.text in COLUMN_LABELS:
        fig.update_coloraxes(colorbar_title_text=COLUMN_LABELS[fig.layout.coloraxis.colorbar.title.text])
    return fig


def show_chart(fig, key: str) -> None:
    st.plotly_chart(localize_figure(fig), width="stretch", key=key)


def build_csv_download(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


def show_dataset_status(manifest: dict[str, object] | None) -> None:
    parts: list[str] = []
    if manifest:
        parts.append(
            f"zakres={manifest.get('start_date')} -> {manifest.get('end_date')} | "
            f"pliki={manifest.get('file_count')} | wiersze={manifest.get('total_rows')} | "
            f"wygenerowano={manifest.get('generated_at_utc')}"
        )
    try:
        etl_df = read_view("vw_etl_status")
        if not etl_df.empty:
            row = etl_df.iloc[0]
            parts.append(
                f"fact_sales={int(row.get('fact_row_count', 0)):,} | "
                f"dim_store={int(row.get('dim_store_count', 0)):,} | "
                f"dim_product={int(row.get('dim_product_count', 0)):,} | "
                f"min_date={row.get('min_date')} | max_date={row.get('max_date')} | "
                f"ostatnie ładowanie={row.get('last_fact_load_timestamp')}"
            )
    except Exception:
        pass
    if parts:
        st.caption(" \u2502 ".join(parts))
    else:
        st.info("Nie znaleziono manifestu ekstrakcji. Uruchom ETL, aby zarejestrować aktualny zakres danych.")


def show_semantic_sources(view_names: list[str]) -> None:
    st.caption("Widoki semantyczne dla tej zakładki: " + ", ".join(f"`sem.{view_name}`" for view_name in view_names))


INT_COLUMNS = {"invoice_count", "store_count", "total_bottles_sold", "day_count"}
FLOAT_COLUMNS = {"total_volume_liters", "sales_per_liter", "avg_sales_per_store"}

def show_report_table(
    title: str,
    df: pd.DataFrame,
    columns: list[str],
    file_stem: str,
    money_cols: list[str] | None = None,
    pct_cols: list[str] | None = None,
) -> None:
    st.markdown(f"#### {title}")
    report_df = df[columns].copy()
    display_columns = {column: COLUMN_LABELS.get(column, column) for column in report_df.columns}
    report_df = report_df.rename(columns=display_columns)
    
    # Zbuduj słownik formatowań
    format_dict = {}
    for col in report_df.columns:
        orig_col = [k for k, v in display_columns.items() if v == col][0]
        if money_cols and orig_col in money_cols:
            format_dict[col] = "${:,.2f}"
        elif pct_cols and orig_col in pct_cols:
            format_dict[col] = "{:,.2f}%"
        elif orig_col in INT_COLUMNS:
            format_dict[col] = "{:,.0f}"
        elif orig_col in FLOAT_COLUMNS:
            format_dict[col] = "{:,.2f}"

    styled = report_df.style
    if format_dict:
        styled = styled.format(format_dict)
        
    st.dataframe(styled, width="stretch", hide_index=True)
    st.download_button(
        "Pobierz CSV",
        data=build_csv_download(report_df),
        file_name=f"{file_stem}.csv",
        mime="text/csv",
        key=f"download_{file_stem}",
    )

def render_kpi_header() -> None:
    """Top-level KPI tiles from vw_kpi_summary — one row per dataset."""
    try:
        df = read_view("vw_kpi_summary")
    except Exception:
        return
    if df.empty:
        return
    row = df.iloc[0]

    def _money(col: str) -> str:
        v = row.get(col, 0)
        try:
            return f"${float(v):,.0f}"
        except (TypeError, ValueError):
            return "—"

    def _num(col: str, decimals: int = 0) -> str:
        v = row.get(col, 0)
        try:
            f = float(v)
            return f"{f:,.{decimals}f}"
        except (TypeError, ValueError):
            return "—"

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.metric("Łączna sprzedaż", _money("total_sales"))
    c2.metric("Łączna marża", _money("total_margin"))
    c3.metric("Marża %", _num("avg_margin_percent", 1) + " %")
    c4.metric("Transakcje", _num("sales_line_count"))
    c5.metric("Faktury", _num("invoice_count"))
    c6.metric("Sklepy", _num("store_count"))
    c7.metric("Produkty", _num("product_count"))
    c8.metric("Śr. faktura", _money("avg_invoice_value"))
    show_semantic_sources(["vw_kpi_summary"])


def render_q1():
    st.header("Q1: Jak zmieniały się całkowita sprzedaż, marża i liczba faktur według miesiąca, kwartału i roku?")
    show_semantic_sources(["vw_sales_by_month"])
    df = read_view("vw_sales_by_month")
    
    if df.empty:
        st.warning("Brak danych.")
        return

    monthly = df.sort_values("year_month")
    
    fig = px.line(monthly, x="year_month", y="total_sales", markers=True, title="Sprzedaż według miesiąca")
    show_chart(fig, key="q1_monthly_sales")

    quarterly = df.groupby(["year", "quarter"], dropna=False).sum(numeric_only=True).reset_index()
    quarterly["year_quarter"] = quarterly["year"].astype(str) + " Q" + quarterly["quarter"].astype(str)
    quarterly = quarterly.sort_values(["year", "quarter"])

    yearly = df.groupby(["year"], dropna=False).sum(numeric_only=True).reset_index().sort_values("year")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(quarterly, x="year_quarter", y="total_sales", title="Sprzedaż kwartalna")
        show_chart(fig, key="q1_quarterly_sales")
    with c2:
        fig = px.bar(yearly, x="year", y="total_sales", title="Sprzedaż roczna", text_auto=".2s")
        show_chart(fig, key="q1_yearly_sales")

    show_report_table(
        "Podsumowanie sprzedaży miesięcznej",
        monthly,
        ["year_month", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="q1_monthly",
        money_cols=["total_sales", "total_margin"],
    )

def render_q2():
    st.header("Q2: Które kategorie generowały najwyższy przychód i marżę?")
    show_semantic_sources(["vw_sales_by_category"])
    df = read_view("vw_sales_by_category")
    if df.empty:
        st.warning("Brak danych.")
        return
    
    df = df.sort_values("total_sales", ascending=False)
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df.head(15), x="total_sales", y="category_name", orientation="h", title="Top 15 kategorii według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q2_sales")
    with c2:
        fig = px.bar(df.sort_values("total_margin", ascending=False).head(15), x="total_margin", y="category_name", orientation="h", title="Top 15 kategorii według marży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q2_margin")

    show_report_table(
        "Podsumowanie kategorii",
        df,
        ["category_name", "total_sales", "total_margin", "total_bottles_sold", "total_volume_liters", "sales_share_percent"],
        file_stem="q2_categories",
        money_cols=["total_sales", "total_margin"],
        pct_cols=["sales_share_percent"],
    )

def render_q3():
    st.header("Q3: Które sklepy generowały najwyższą sprzedaż i marżę?")
    show_semantic_sources(["vw_sales_by_store"])
    df = read_view("vw_sales_by_store")
    if df.empty:
        st.warning("Brak danych.")
        return

    df = df.sort_values("total_sales", ascending=False)
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df.head(15), x="total_sales", y="store_name", orientation="h", title="Top 15 sklepów według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q3_sales")
    with c2:
        fig = px.bar(df.sort_values("total_margin", ascending=False).head(15), x="total_margin", y="store_name", orientation="h", title="Top 15 sklepów według marży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q3_margin")

    show_report_table(
        "Top Sklepy",
        df.head(50),
        ["store_number", "store_name", "city", "county", "total_sales", "total_margin", "invoice_count"],
        file_stem="q3_stores",
        money_cols=["total_sales", "total_margin"],
    )

def render_q4():
    st.header("Q4: Które miasta i county generowały najwyższy przychód i wolumen?")
    show_semantic_sources(["vw_sales_by_geography", "vw_sales_map_points"])
    df = read_view("vw_sales_by_geography")
    if df.empty:
        st.warning("Brak danych.")
        return

    county_sales = df.groupby("county", dropna=False).sum(numeric_only=True).reset_index().sort_values("total_sales", ascending=False)
    city_sales = df.groupby(["city", "county"], dropna=False).sum(numeric_only=True).reset_index().sort_values("total_sales", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(county_sales.head(15), x="total_sales", y="county", orientation="h", title="Top 15 County według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q4_county")
    with c2:
        fig = px.bar(city_sales.head(15), x="total_sales", y="city", color="county", orientation="h", title="Top 15 Miast według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q4_city")

    # Mapa punktowa
    map_df = read_view("vw_sales_map_points")
    if not map_df.empty:
        st.markdown("### Mapa miast")
        city_map_df = (
            map_df.groupby(["city", "county"], dropna=False)
            .agg(
                latitude=("latitude", "mean"),
                longitude=("longitude", "mean"),
                total_sales=("total_sales", "sum"),
                total_volume_liters=("total_volume_liters", "sum"),
                store_count=("store_number", "nunique")
            )
            .reset_index()
        )
        city_map_df["log_sales"] = np.log1p(city_map_df["total_sales"])
        fig_city = px.scatter_mapbox(
            city_map_df, lat="latitude", lon="longitude", size="log_sales", color="total_volume_liters",
            hover_name="city", hover_data=["county", "store_count", "total_sales", "total_volume_liters"],
            zoom=5, height=550, title="Mapa miast (wielkość punktów: skala logarytmiczna)"
        )
        fig_city.update_layout(mapbox_style="carto-positron")
        show_chart(fig_city, key="q4_city_map")

def render_q5():
    st.header("Q5: Którzy vendorzy mieli najwyższy udział w sprzedaży i wkład w marżę?")
    show_semantic_sources(["vw_sales_by_vendor"])
    df = read_view("vw_sales_by_vendor")
    if df.empty:
        st.warning("Brak danych.")
        return

    df = df.sort_values("total_sales", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df.head(15), x="total_sales", y="vendor_name", orientation="h", title="Top 15 dostawców według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q5_sales")
    with c2:
        fig = px.treemap(df.head(20), path=["vendor_name"], values="total_sales", title="Udział w sprzedaży (Top 20 dostawców)")
        show_chart(fig, key="q5_treemap")

    show_report_table(
        "Podsumowanie dostawców",
        df,
        ["vendor_name", "total_sales", "total_margin", "total_bottles_sold", "sales_share_percent"],
        file_stem="q5_vendors",
        money_cols=["total_sales", "total_margin"],
        pct_cols=["sales_share_percent"],
    )

def render_q6():
    st.header("Q6: Które produkty sprzedawały się najlepiej według liczby butelek i wartości sprzedaży?")
    show_semantic_sources(["vw_top_products"])
    df = read_view("vw_top_products")
    if df.empty:
        st.warning("Brak danych.")
        return

    c1, c2 = st.columns(2)
    with c1:
        top_bottles = df.sort_values("total_bottles_sold", ascending=False).head(15)
        fig = px.bar(top_bottles, x="total_bottles_sold", y="item_description", orientation="h", title="Top 15 produktów (liczba butelek)")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q6_bottles")
    with c2:
        top_sales = df.sort_values("total_sales", ascending=False).head(15)
        fig = px.bar(top_sales, x="total_sales", y="item_description", orientation="h", title="Top 15 produktów (wartość sprzedaży)")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="q6_sales")

    st.markdown("### Porównanie: Przychód vs Wolumen dla Top 50 produktów")
    top_50 = df.sort_values("total_sales", ascending=False).head(50)
    fig_scatter = px.scatter(
        top_50, x="total_bottles_sold", y="total_sales", color="category_name", size="total_margin",
        hover_name="item_description", log_x=True, log_y=True,
        title="Sprzedaż vs Liczba Butelek (skala logarytmiczna)"
    )
    show_chart(fig_scatter, key="q6_scatter")

    show_report_table(
        "Top Produkty",
        top_sales.head(50),
        ["item_number", "item_description", "category_name", "vendor_name", "total_sales", "total_bottles_sold", "total_margin"],
        file_stem="q6_products",
        money_cols=["total_sales", "total_margin"],
    )

def render_q7():
    st.header("Q7: Które kategorie i produkty miały najwyższą marżę jednostkową i całkowitą?")
    show_semantic_sources(["vw_margin_analysis"])
    df = read_view("vw_margin_analysis")
    if df.empty:
        st.warning("Brak danych.")
        return

    df["avg_unit_margin"] = pd.to_numeric(df["avg_unit_margin"], errors="coerce")
    
    # KRYTYCZNE: Odfiltrowanie produktów-widm (sprzedaż < $5000), żeby absurdalne pojedyczne butelki nie psuły wizualizacji
    df = df[df["total_sales"] >= 5000]
    
    df = df.dropna(subset=["avg_unit_margin"]).sort_values("avg_unit_margin", ascending=False)
    
    top_margin = df.head(20)
    fig = px.bar(
        top_margin.sort_values("avg_unit_margin"),
        x="avg_unit_margin", y="item_description", color="category_name", orientation="h",
        title="Top 20 produktów według średniej marży jednostkowej",
        hover_data={"vendor_name": True, "total_margin": ":$,.2f", "total_sales": ":$,.2f"}
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    show_chart(fig, key="q7_unit_margin")

    show_report_table(
        "Analiza marży",
        top_margin,
        ["category_name", "item_description", "vendor_name", "avg_unit_margin", "total_margin", "total_sales"],
        file_stem="q7_margin",
        money_cols=["avg_unit_margin", "total_margin", "total_sales"],
    )

def render_q8():
    st.header("Q8: Jak zmieniała się struktura sprzedaży kategorii w czasie?")
    show_semantic_sources(["vw_category_sales_over_time"])
    df = read_view("vw_category_sales_over_time")
    if df.empty:
        st.warning("Brak danych.")
        return

    top_categories = df.groupby("category_name")["total_sales"].sum().nlargest(10).index
    df_top = df[df["category_name"].isin(top_categories)].sort_values(["year_month", "category_name"])

    fig = px.area(df_top, x="year_month", y="total_sales", color="category_name", groupnorm="percent", title="Struktura sprzedaży (Top 10 kategorii) w czasie")
    show_chart(fig, key="q8_area")

    show_report_table(
        "Dane w czasie (Top 10 kategorii)",
        df_top,
        ["year_month", "category_name", "total_sales", "total_margin"],
        file_stem="q8_categories_over_time",
        money_cols=["total_sales", "total_margin"],
    )

def render_q9():
    st.header("Q9: Które regiony miały wysoki wolumen, ale niższą wartość sprzedaży na litr?")
    show_semantic_sources(["vw_volume_vs_revenue"])
    st.info(
        "**Jak interpretować tę analizę?**\n\n"
        "Wartość sprzedaży na litr to stosunek `SUM(sale_dollars) / SUM(volume_sold_liters)` liczony dla każdego county. "
        "Wysoki wolumen oznacza regiony znajdujące się w górnym kwartylu wolumenu, czyli od 75. percentyla wzwyż. "
        "Tabela pokazuje więc county, które sprzedają dużo litrów, ale mają relatywnie niższą sprzedaż na 1 litr. "
        "Może to oznaczać bardziej wolumenowy, tańszy lub mniej premium miks sprzedaży."
    )
    df = read_view("vw_volume_vs_revenue")
    if df.empty:
        st.warning("Brak danych.")
        return

    fig = px.scatter(
        df, x="total_volume_liters", y="total_sales", size="store_count", hover_name="county",
        log_x=True, log_y=True, title="Wolumen a sprzedaż według regionu (Skala Logarytmiczna)"
    )
    show_chart(fig, key="q9_scatter")

    df["sales_per_liter"] = pd.to_numeric(df["sales_per_liter"], errors="coerce")
    high_volume_threshold = df["total_volume_liters"].quantile(0.75)
    high_volume = df[df["total_volume_liters"] >= high_volume_threshold].sort_values("sales_per_liter")

    fig2 = px.bar(
        high_volume.head(15).sort_values("sales_per_liter", ascending=False),
        x="sales_per_liter", y="county", color="total_volume_liters", orientation="h",
        title="County z wysokim wolumenem i najniższą sprzedażą na litr"
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    show_chart(fig2, key="q9_bar")

    show_report_table(
        "Wysoki wolumen, niska sprzedaż na litr",
        high_volume.head(20),
        ["county", "total_volume_liters", "sales_per_liter", "total_sales", "store_count"],
        file_stem="q9_volume",
        money_cols=["sales_per_liter", "total_sales"],
    )

def render_q10():
    st.header("Q10: Jak zmieniała się średnia sprzedaż na sklep według miesiąca i county?")
    show_semantic_sources(["vw_avg_sales_per_store_by_month_region"])
    df = read_view("vw_avg_sales_per_store_by_month_region")
    if df.empty:
        st.warning("Brak danych.")
        return

    county_focus = df.groupby("county")["avg_sales_per_store"].mean().nlargest(8).index
    df_focus = df[df["county"].isin(county_focus)].sort_values("year_month")

    fig = px.line(
        df_focus, x="year_month", y="avg_sales_per_store", color="county", markers=True,
        title="Średnia sprzedaż na sklep według miesiąca (Top 8 county)"
    )
    show_chart(fig, key="q10_line")

    show_report_table(
        "Dane dla Top 8 county",
        df_focus,
        ["year_month", "county", "avg_sales_per_store", "store_count"],
        file_stem="q10_avg_sales",
        money_cols=["avg_sales_per_store"],
    )

def render_q11():
    st.header("Q11: Jak różnią się sprzedaż, wolumen i liczba faktur w weekendy oraz dni robocze?")
    show_semantic_sources(["vw_sales_by_day_type"])
    df = read_view("vw_sales_by_day_type")
    if df.empty:
        st.warning("Brak danych.")
        return

    day_type = df.groupby("day_type", dropna=False).sum(numeric_only=True).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(day_type, x="day_type", y="total_sales", color="day_type", log_y=True, title="Sprzedaż (Oś logarytmiczna)")
        show_chart(fig, key="q11_sales")
    with c2:
        fig = px.bar(day_type, x="day_type", y="total_volume_liters", color="day_type", log_y=True, title="Wolumen (Oś logarytmiczna)")
        show_chart(fig, key="q11_volume")

    st.info(
        "**Dlaczego sprzedaż w weekendy jest bliska zeru?**\n\n"
        "**Zbiór danych 'Iowa Liquor Sales' rejestruje sprzedaż HURTOWĄ (dostawy ze stanu Iowa do sklepów detalicznych), a nie sprzedaż detaliczną do konsumentów końcowych. Stanowe centrum dystrybucji realizuje zamówienia i dostawy głównie w dni robocze, dlatego faktury z weekendów stanowią ułamek procenta.**"
    )

    show_report_table(
        "Podsumowanie",
        day_type,
        ["day_type", "total_sales", "total_volume_liters", "invoice_count", "total_bottles_sold", "total_margin"],
        file_stem="q11_day_type",
        money_cols=["total_sales", "total_margin"],
    )

def render_q12():
    st.header("Q12: Które grupy opakowań i pojemności butelek generowały najwyższą sprzedaż, wolumen i marżę?")
    show_semantic_sources(["vw_sales_by_packaging"])
    df = read_view("vw_sales_by_packaging")
    if df.empty:
        st.warning("Brak danych.")
        return

    df = df.sort_values("total_sales", ascending=False)
    
    fig = px.treemap(
        df.head(30), path=["volume_group", "bottle_volume_ml"], values="total_sales",
        title="Drzewo sprzedaży (Treemap) według grupy opakowania i pojemności"
    )
    show_chart(fig, key="q12_treemap")

    show_report_table(
        "Podsumowanie opakowań",
        df,
        ["volume_group", "bottle_volume_ml", "total_sales", "total_bottles_sold", "total_margin"],
        file_stem="q12_packaging",
        money_cols=["total_sales", "total_margin"],
    )


st.title("Analityka dystrybucji detalicznej Iowa")
st.caption("Dashboard oparty na warstwie semantycznej SQL Server.")
show_dataset_status(read_extract_manifest())
render_kpi_header()
st.divider()

tabs = st.tabs([f"Q{i}" for i in range(1, 13)])

with tabs[0]: render_q1()
with tabs[1]: render_q2()
with tabs[2]: render_q3()
with tabs[3]: render_q4()
with tabs[4]: render_q5()
with tabs[5]: render_q6()
with tabs[6]: render_q7()
with tabs[7]: render_q8()
with tabs[8]: render_q9()
with tabs[9]: render_q10()
with tabs[10]: render_q11()
with tabs[11]: render_q12()

