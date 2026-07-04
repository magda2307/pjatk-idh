from __future__ import annotations

import json
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from sqlalchemy import create_engine

from src.config import EXTRACT_MANIFEST_PATH, SqlServerConfig


st.set_page_config(
    page_title="Hurtownia Iowa Liquor Sales",
    layout="wide",
    initial_sidebar_state="expanded",
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
        return pd.read_sql(query, connection)


@st.cache_data(ttl=300)
def read_extract_manifest() -> dict[str, object] | None:
    if not EXTRACT_MANIFEST_PATH.exists():
        return None
    return json.loads(EXTRACT_MANIFEST_PATH.read_text(encoding="utf-8"))


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


def apply_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list]]:
    filtered = df.copy()
    filter_state: dict[str, list] = {}

    with st.sidebar:
        st.header("Filtry")
        if st.button("Odśwież dane semantyczne", width="stretch"):
            st.cache_data.clear()
            st.rerun()

        years = sorted(filtered["year"].dropna().unique().tolist())
        selected_years = st.multiselect("Rok", years, default=years, placeholder="Wybierz opcje")
        filter_state["year"] = selected_years
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

        months = sorted(filtered["month"].dropna().unique().tolist())
        selected_months = st.multiselect("Miesiąc", months, default=months, placeholder="Wybierz opcje")
        filter_state["month"] = selected_months
        if selected_months:
            filtered = filtered[filtered["month"].isin(selected_months)]

        categories = sorted(filtered["category_name"].dropna().unique().tolist())
        selected_categories = st.multiselect("Kategoria", categories, placeholder="Wybierz opcje")
        filter_state["category_name"] = selected_categories
        if selected_categories:
            filtered = filtered[filtered["category_name"].isin(selected_categories)]

        vendors = sorted(filtered["vendor_name"].dropna().unique().tolist())
        selected_vendors = st.multiselect("Dostawca", vendors, placeholder="Wybierz opcje")
        filter_state["vendor_name"] = selected_vendors
        if selected_vendors:
            filtered = filtered[filtered["vendor_name"].isin(selected_vendors)]

        counties = sorted(filtered["county"].dropna().unique().tolist())
        selected_counties = st.multiselect("County", counties, placeholder="Wybierz opcje")
        filter_state["county"] = selected_counties
        if selected_counties:
            filtered = filtered[filtered["county"].isin(selected_counties)]

        cities = sorted(filtered["city"].dropna().unique().tolist())
        selected_cities = st.multiselect("Miasto", cities, placeholder="Wybierz opcje")
        filter_state["city"] = selected_cities
        if selected_cities:
            filtered = filtered[filtered["city"].isin(selected_cities)]

        volume_groups = sorted(filtered["volume_group"].dropna().unique().tolist())
        selected_volume_groups = st.multiselect("Grupa opakowania", volume_groups, placeholder="Wybierz opcje")
        filter_state["volume_group"] = selected_volume_groups
        if selected_volume_groups:
            filtered = filtered[filtered["volume_group"].isin(selected_volume_groups)]

        day_type_options = {"Dzień roboczy": 0, "Weekend": 1}
        selected_day_types = st.multiselect("Typ dnia", list(day_type_options), default=list(day_type_options), placeholder="Wybierz opcje")
        selected_is_weekend = [day_type_options[day_type] for day_type in selected_day_types]
        filter_state["is_weekend"] = selected_is_weekend
        if selected_day_types and len(selected_day_types) < len(day_type_options):
            filtered = filtered[filtered["is_weekend"].isin(selected_is_weekend)]

        top_n = st.slider("Liczba pozycji Top N", min_value=5, max_value=25, value=10, step=5)
        filter_state["top_n"] = [top_n]

    return filtered, filter_state


def apply_filter_state(df: pd.DataFrame, filter_state: dict[str, list]) -> pd.DataFrame:
    filtered = df.copy()
    for column, selected_values in filter_state.items():
        if column in filtered.columns and selected_values:
            filtered = filtered[filtered[column].isin(selected_values)]
    return filtered


def aggregate(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            total_sales=("sale_dollars", "sum"),
            total_margin=("margin_amount", "sum"),
            total_bottles_sold=("bottles_sold", "sum"),
            total_volume_liters=("volume_sold_liters", "sum"),
            invoice_count=("invoice_number", "nunique"),
            store_count=("store_number", "nunique"),
        )
        .reset_index()
    )


def get_top_n(filter_state: dict[str, list], default: int = 10) -> int:
    values = filter_state.get("top_n", [default])
    return int(values[0]) if values else default


def build_csv_download(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


def show_scope_summary(df: pd.DataFrame, filter_state: dict[str, list]) -> None:
    years = ", ".join(str(year) for year in filter_state.get("year", [])) or "wszystkie"
    months = ", ".join(str(month) for month in filter_state.get("month", [])) or "wszystkie"
    st.caption(
        "Aktualny zakres: "
        f"lata={years} | miesiące={months} | wiersze={len(df):,} | "
        f"faktury={df['invoice_number'].nunique():,} | sklepy={df['store_number'].nunique():,}"
    )


def show_dataset_status(manifest: dict[str, object] | None) -> None:
    if not manifest:
        st.info("Nie znaleziono manifestu ekstrakcji. Uruchom ETL, aby zarejestrować aktualny zakres danych.")
        return
    st.caption(
        "Status danych: "
        f"zakres={manifest.get('start_date')} -> {manifest.get('end_date')} | "
        f"pliki={manifest.get('file_count')} | wiersze={manifest.get('total_rows')} | "
        f"wygenerowano={manifest.get('generated_at_utc')}"
    )


def show_semantic_layer_banner() -> None:
    with st.expander("Pokrycie warstwy semantycznej w dashboardzie", expanded=True):
        st.markdown(
            """
            Dashboard czyta widoki semantyczne SQL ze schematu `sem`.

            Hierarchie semantyczne:
            - Czas: dzień -> miesiąc -> kwartał -> rok
            - Geografia: sklep -> miasto -> county -> stan
            - Produkt: produkt -> kategoria
            - Dostawca: produkt -> vendor
            - Opakowanie: produkt -> pojemność butelki -> grupa pojemności

            Widoki semantyczne ładowane bezpośrednio przez aplikację:
            - `sem.vw_sales_overview`
            - `sem.vw_sales_map_points`
            - `sem.vw_margin_analysis`
            - `sem.vw_category_sales_over_time`
            - `sem.vw_avg_sales_per_store_by_month_region`
            - `sem.vw_kpi_summary`
            - `sem.vw_etl_status`

            Pozostałe widoki semantyczne są dostępne w SQL i pokrywają te same pytania biznesowe.
            """
        )
        usage_matrix = pd.DataFrame(
            [
                ("Przegląd zarządczy", "Q1, Q11", "vw_sales_overview, vw_kpi_summary", "vw_sales_by_month, vw_sales_by_day_type"),
                ("Produkty i kategorie", "Q2, Q5, Q6, Q7, Q8, Q12", "vw_sales_overview, vw_margin_analysis, vw_category_sales_over_time", "vw_sales_by_category, vw_top_products, vw_sales_by_vendor, vw_sales_by_packaging"),
                ("Geografia", "Q4, Q9", "vw_sales_overview, vw_sales_map_points", "vw_sales_by_geography, vw_volume_vs_revenue"),
                ("Wyniki sklepów", "Q3, Q10", "vw_sales_overview, vw_avg_sales_per_store_by_month_region", "vw_sales_by_store"),
            ],
            columns=["Strona dashboardu", "Pytania biznesowe", "Widoki ładowane bezpośrednio", "Dodatkowe widoki SQL"],
        )
        st.dataframe(usage_matrix, width="stretch", hide_index=True)


def show_semantic_sources(view_names: list[str]) -> None:
    st.caption("Pokrycie semantyczne tej strony: " + ", ".join(f"`sem.{view_name}`" for view_name in view_names))


def show_etl_status_panel(etl_status: pd.DataFrame) -> None:
    if etl_status.empty:
        return
    row = etl_status.iloc[0]
    with st.expander("Status ETL z warstwy semantycznej", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Wiersze staging", format_number(row["staging_row_count"]))
        c2.metric("Wiersze faktów", format_number(row["fact_row_count"]))
        c3.metric("Początek zakresu", str(row["min_date"]))
        c4.metric("Koniec zakresu", str(row["max_date"]))

        c5, c6, c7 = st.columns(3)
        c5.metric("Sklepy", format_number(row["dim_store_count"]))
        c6.metric("Produkty", format_number(row["dim_product_count"]))
        c7.metric("Grupy opakowań", format_number(row["dim_packaging_count"]))

        st.caption(
            "Migawka ETL: "
            f"wygenerowano={row['status_generated_at']} | "
            f"ostatni staging={row['last_staging_load_timestamp']} | "
            f"ostatni fakt={row['last_fact_load_timestamp']}"
        )


def show_global_kpi_reference(kpi_summary: pd.DataFrame) -> None:
    if kpi_summary.empty:
        return
    required_columns = {
        "avg_invoice_value",
        "avg_bottles_per_invoice",
        "avg_margin_percent",
        "sales_per_store",
        "sales_per_liter",
    }
    if not required_columns.issubset(kpi_summary.columns):
        st.info("Odśwież widoki semantyczne, aby pokazać rozszerzone KPI.")
        return
    row = kpi_summary.iloc[0]
    with st.expander("Globalne KPI z warstwy semantycznej", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Śr. wartość faktury", format_money(row["avg_invoice_value"]))
        c2.metric("Butelki / faktura", format_decimal(row["avg_bottles_per_invoice"]))
        c3.metric("Marża %", f"{row['avg_margin_percent']:.2f}%")
        c4.metric("Sprzedaż / sklep", format_money(row["sales_per_store"]))
        c5.metric("Sprzedaż / litr", format_money(row["sales_per_liter"]))

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
    styled = report_df.style
    if money_cols:
        styled = styled.format({display_columns[column]: "${:,.2f}" for column in money_cols if display_columns.get(column) in report_df.columns})
    if pct_cols:
        styled = styled.format({display_columns[column]: "{:,.2f}%" for column in pct_cols if display_columns.get(column) in report_df.columns})
    st.dataframe(styled, width="stretch", hide_index=True)
    st.download_button(
        "Pobierz CSV",
        data=build_csv_download(report_df),
        file_name=f"{file_stem}.csv",
        mime="text/csv",
        key=f"download_{file_stem}",
    )


def show_kpis(df: pd.DataFrame) -> None:
    cols = st.columns(6)
    cols[0].metric("Sprzedaż łącznie", format_money(df["sale_dollars"].sum()))
    cols[1].metric("Marża łącznie", format_money(df["margin_amount"].sum()))
    cols[2].metric("Sprzedane butelki", format_number(df["bottles_sold"].sum()))
    cols[3].metric("Wolumen (litry)", format_number(df["volume_sold_liters"].sum()))
    cols[4].metric("Sklepy", format_number(df["store_number"].nunique()))
    cols[5].metric("Produkty", format_number(df["item_number"].nunique()))


def show_advanced_kpis(df: pd.DataFrame) -> None:
    invoice_count = df["invoice_number"].nunique()
    store_count = df["store_number"].nunique()
    total_sales = df["sale_dollars"].sum()
    total_margin = df["margin_amount"].sum()
    total_volume = df["volume_sold_liters"].sum()
    total_bottles = df["bottles_sold"].sum()

    cols = st.columns(5)
    cols[0].metric("Śr. wartość faktury", format_money(total_sales / invoice_count if invoice_count else 0))
    cols[1].metric("Butelki / faktura", format_decimal(total_bottles / invoice_count if invoice_count else 0))
    cols[2].metric("Marża %", f"{(100 * total_margin / total_sales if total_sales else 0):.2f}%")
    cols[3].metric("Sprzedaż / sklep", format_money(total_sales / store_count if store_count else 0))
    cols[4].metric("Sprzedaż / litr", format_money(total_sales / total_volume if total_volume else 0))


def executive_overview(df: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state)
    show_kpis(df)
    show_advanced_kpis(df)
    show_semantic_sources(["vw_sales_overview", "vw_sales_by_month", "vw_sales_by_day_type", "vw_sales_by_category"])
    show_scope_summary(df, filter_state)
    monthly = aggregate(df, ["year_month"]).sort_values("year_month")
    quarterly = aggregate(df, ["year", "quarter"]).sort_values(["year", "quarter"])
    quarterly["year_quarter"] = (
        quarterly["year"].astype("Int64").astype(str)
        + " Q"
        + quarterly["quarter"].astype("Int64").astype(str)
    )
    yearly = aggregate(df, ["year"]).sort_values("year")
    categories = aggregate(df, ["category_name"]).sort_values("total_sales", ascending=False).head(12)
    stores = aggregate(df, ["store_number", "store_name"]).sort_values("total_sales", ascending=False).head(top_n)
    day_type_df = df.assign(day_type=df["is_weekend"].map({0: "Dzień roboczy", 1: "Weekend"}))
    day_type = aggregate(day_type_df, ["day_type"]).sort_values("day_type")
    day_type_month = aggregate(day_type_df, ["year_month", "day_type"])

    left, right = st.columns([1.45, 1])
    with left:
        fig = px.line(monthly, x="year_month", y="total_sales", markers=True, title="Jak zmieniała się sprzedaż w czasie?")
        show_chart(fig, key="exec_monthly_sales")
    with right:
        fig = px.bar(categories, x="total_sales", y="category_name", orientation="h", title="Które kategorie wygenerowały najwyższą sprzedaż?")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="exec_sales_by_category")

    q1_left, q1_right = st.columns(2)
    with q1_left:
        fig = px.bar(
            quarterly,
            x="year_quarter",
            y="total_sales",
            title="Q1: sprzedaż kwartalna",
        )
        show_chart(fig, key="exec_quarterly_sales")
    with q1_right:
        fig = px.bar(
            yearly,
            x="year",
            y="total_sales",
            title="Q1: sprzedaż roczna",
        )
        show_chart(fig, key="exec_yearly_sales")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(stores, x="total_sales", y="store_name", orientation="h", title="Które sklepy wygenerowały najwyższą sprzedaż?")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="exec_top_stores")
    with c2:
        fig = px.bar(day_type, x="day_type", y="total_sales", color="day_type", title="Porównanie sprzedaży: weekend i dni robocze")
        show_chart(fig, key="exec_day_type_sales")

    if not day_type.empty:
        fig = px.bar(
            day_type,
            x="day_type",
            y="total_volume_liters",
            color="day_type",
            title="Q11: wolumen w weekendy i dni robocze",
        )
        show_chart(fig, key="exec_day_type_volume")

    if not day_type_month.empty:
        fig = px.bar(
            day_type_month.sort_values("year_month"),
            x="year_month",
            y="invoice_count",
            color="day_type",
            barmode="group",
            title="Liczba faktur według typu dnia i miesiąca",
        )
        show_chart(fig, key="exec_day_type_invoice_month")

    show_report_table(
        "Podsumowanie sprzedaży miesięcznej",
        monthly.sort_values("year_month"),
        ["year_month", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="monthly_sales_summary",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "Podsumowanie sprzedaży kwartalnej",
        quarterly.sort_values(["year", "quarter"]),
        ["year", "quarter", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="quarterly_sales_summary",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "Podsumowanie sprzedaży rocznej",
        yearly.sort_values("year"),
        ["year", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="yearly_sales_summary",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "Q11: weekend a dzień roboczy",
        day_type.sort_values("day_type"),
        ["day_type", "total_sales", "total_volume_liters", "invoice_count", "total_bottles_sold", "total_margin"],
        file_stem="weekend_weekday_summary",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} sklepów według sprzedaży",
        stores.sort_values("total_sales", ascending=False),
        ["store_number", "store_name", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_stores_by_sales",
        money_cols=["total_sales", "total_margin"],
    )


def product_category_analysis(
    df: pd.DataFrame,
    category_over_time: pd.DataFrame,
    margin_analysis: pd.DataFrame,
    filter_state: dict[str, list],
) -> None:
    top_n = get_top_n(filter_state, default=15)
    show_semantic_sources(["vw_sales_overview", "vw_margin_analysis", "vw_category_sales_over_time", "vw_sales_by_category", "vw_top_products", "vw_sales_by_vendor", "vw_sales_by_packaging"])
    show_scope_summary(df, filter_state)
    categories = aggregate(df, ["category_name"]).sort_values("total_sales", ascending=False).head(top_n)
    products = aggregate(df, ["item_number", "item_description"]).sort_values("total_bottles_sold", ascending=False).head(top_n)
    vendors = aggregate(df, ["vendor_name"]).sort_values("total_sales", ascending=False).head(12)
    packaging = aggregate(df, ["volume_group", "bottle_volume_ml"]).sort_values("total_sales", ascending=False).head(top_n)

    margin_by_category = categories.copy()
    margin_by_category["avg_margin_per_bottle"] = (
        margin_by_category["total_margin"] / margin_by_category["total_bottles_sold"].replace(0, pd.NA)
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(categories, x="total_sales", y="category_name", orientation="h", title="Najlepsze kategorie według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="prod_top_categories")
    with c2:
        fig = px.bar(products, x="total_bottles_sold", y="item_description", orientation="h", title="Najlepsze produkty według liczby butelek")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="prod_top_products")

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(margin_by_category, x="total_margin", y="category_name", orientation="h", title="Marża według kategorii")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="prod_margin_by_category")
    with c4:
        fig = px.pie(vendors, names="vendor_name", values="total_sales", title="Udział vendorów w sprzedaży")
        show_chart(fig, key="prod_vendor_share")

    margin_columns = {"category_name", "vendor_name", "item_description", "avg_unit_margin", "total_margin", "total_sales"}
    if margin_columns.issubset(margin_analysis.columns):
        q7_margin = apply_filter_state(margin_analysis, filter_state).copy()
        for column in ["avg_unit_margin", "total_margin", "total_sales"]:
            q7_margin[column] = pd.to_numeric(q7_margin[column], errors="coerce")
        q7_margin = q7_margin.dropna(subset=["avg_unit_margin", "total_margin", "total_sales"])
        q7_margin = q7_margin.sort_values(["avg_unit_margin", "total_margin"], ascending=False).head(top_n)
        if q7_margin.empty:
            st.info("Analiza marży Q7 nie ma wierszy dla aktualnych filtrów kategorii/vendorów.")
        else:
            fig = px.bar(
                q7_margin.sort_values("avg_unit_margin"),
                x="avg_unit_margin",
                y="item_description",
                color="category_name",
                orientation="h",
                hover_data={
                    "vendor_name": True,
                    "total_margin": ":$,.2f",
                    "total_sales": ":$,.2f",
                    "avg_unit_margin": ":$,.2f",
                },
                title="Q7: najwyższa średnia marża jednostkowa według produktu i kategorii",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            show_chart(fig, key="prod_q7_unit_margin")

            q7_table = q7_margin.rename(columns={"item_description": "product"})
            show_report_table(
                f"Q7: analiza marży - top {top_n} produktów",
                q7_table,
                ["category_name", "product", "vendor_name", "avg_unit_margin", "total_margin", "total_sales"],
                file_stem="q7_margin_analysis",
                money_cols=["avg_unit_margin", "total_margin", "total_sales"],
            )
    else:
        st.info("Odśwież widoki semantyczne, aby pokazać analizę marży Q7 z `sem.vw_margin_analysis`.")

    top_categories = categories["category_name"].head(8).tolist()
    category_mix = category_over_time[category_over_time["category_name"].isin(top_categories)].copy()
    category_mix = category_mix.sort_values(["year_month", "category_name"])
    if not category_mix.empty:
        fig = px.area(
            category_mix,
            x="year_month",
            y="total_sales",
            color="category_name",
            groupnorm="percent",
            title="Struktura sprzedaży według kategorii w czasie",
        )
        show_chart(fig, key="prod_category_mix_time")

    show_report_table(
        f"Top {top_n} kategorii",
        categories.sort_values("total_sales", ascending=False),
        ["category_name", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="top_categories",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} produktów według liczby butelek",
        products.sort_values("total_bottles_sold", ascending=False),
        ["item_number", "item_description", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_products_by_bottles_sold",
        money_cols=["total_sales", "total_margin"],
    )
    vendor_table = vendors.copy()
    vendor_table["sales_share_percent"] = (
        100 * vendor_table["total_sales"] / df["sale_dollars"].sum()
    ).round(2)
    show_report_table(
        "Podsumowanie sprzedaży vendorów",
        vendor_table.sort_values("total_sales", ascending=False),
        ["vendor_name", "total_sales", "total_margin", "total_bottles_sold", "sales_share_percent"],
        file_stem="vendor_sales_summary",
        money_cols=["total_sales", "total_margin"],
        pct_cols=["sales_share_percent"],
    )
    fig = px.bar(
        packaging.sort_values("total_sales", ascending=False),
        x="total_sales",
        y="volume_group",
        color="bottle_volume_ml",
        orientation="h",
        title="Sprzedaż według grupy opakowania",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    show_chart(fig, key="prod_packaging_sales")

    treemap_df = aggregate(df, ["category_name", "item_description"]).sort_values("total_sales", ascending=False).head(80)
    if not treemap_df.empty:
        fig = px.treemap(
            treemap_df,
            path=["category_name", "item_description"],
            values="total_sales",
            color="total_margin",
            title="Mapa drzewa sprzedaży produktów według kategorii",
        )
        show_chart(fig, key="prod_category_product_treemap")

    show_report_table(
        "Wyniki według opakowania",
        packaging.sort_values("total_sales", ascending=False),
        ["volume_group", "bottle_volume_ml", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="packaging_performance",
        money_cols=["total_sales", "total_margin"],
    )


def load_iowa_counties_geojson() -> dict:
    geojson_path = Path(__file__).parent / "data" / "iowa_counties.geojson"
    if geojson_path.exists():
        return json.loads(geojson_path.read_text(encoding="utf-8"))
    return None


def geography_analysis(df: pd.DataFrame, map_points: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state, default=20)
    show_semantic_sources(["vw_sales_overview", "vw_sales_by_geography", "vw_sales_map_points", "vw_volume_vs_revenue"])
    show_scope_summary(df, filter_state)
    county = aggregate(df, ["county"]).sort_values("total_sales", ascending=False).head(top_n)
    city = aggregate(df, ["city", "county"]).sort_values("total_sales", ascending=False).head(top_n)
    volume_table = aggregate(df, ["county"])
    volume_table["sales_per_liter"] = (
        volume_table["total_sales"] / volume_table["total_volume_liters"].replace(0, pd.NA)
    )
    volume = volume_table.sort_values("total_volume_liters", ascending=False).head(top_n)
    high_volume_threshold = volume_table["total_volume_liters"].quantile(0.75)
    high_volume_low_value = volume_table[
        volume_table["total_volume_liters"].ge(high_volume_threshold)
    ].dropna(subset=["sales_per_liter"]).copy()
    if high_volume_low_value.empty:
        high_volume_low_value = volume_table.dropna(subset=["sales_per_liter"]).copy()
    high_volume_low_value = high_volume_low_value.sort_values(
        ["sales_per_liter", "total_volume_liters"],
        ascending=[True, False],
    ).head(top_n)
    high_volume_low_value.insert(0, "rank", range(1, len(high_volume_low_value) + 1))
    map_df = apply_filter_state(map_points, filter_state)
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

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(county, x="total_sales", y="county", orientation="h", title="Sprzedaż według county")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="geo_sales_by_county")
    with c2:
        fig = px.bar(city, x="total_sales", y="city", color="county", orientation="h", title="Najlepsze miasta według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="geo_top_cities")

    fig = px.scatter(
        volume,
        x="total_volume_liters",
        y="total_sales",
        size="store_count",
        hover_name="county",
        title="Wolumen a sprzedaż według county",
    )
    show_chart(fig, key="geo_volume_vs_revenue")

    if not high_volume_low_value.empty:
        fig = px.bar(
            high_volume_low_value.sort_values("sales_per_liter", ascending=False),
            x="sales_per_liter",
            y="county",
            color="total_volume_liters",
            orientation="h",
            title="Q9: county z wysokim wolumenem i niższą sprzedażą na litr",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="geo_q9_high_volume_low_value")

    heatmap_df = aggregate(df, ["county", "year_month"])
    top_counties = county["county"].head(10).tolist()
    heatmap_df = heatmap_df[heatmap_df["county"].isin(top_counties)]
    if not heatmap_df.empty:
        heatmap_matrix = heatmap_df.pivot_table(index="county", columns="year_month", values="total_sales", fill_value=0)
        fig = px.imshow(
            heatmap_matrix,
            title="Mapa ciepła: county x miesiąc",
        )
        show_chart(fig, key="geo_county_month_heatmap")

    st.markdown("### Mapa sprzedaży")
    geojson_data = load_iowa_counties_geojson()

    if geojson_data:
        geo_counties = pd.DataFrame(
            [
                {
                    "FIPS": feature.get("properties", {}).get("FIPS"),
                    "geo_county": feature.get("properties", {}).get("COUNTY"),
                    "county_name_key": normalize_county_name(feature.get("properties", {}).get("COUNTY")),
                }
                for feature in geojson_data.get("features", [])
            ]
        ).dropna(subset=["FIPS", "county_name_key"])

        county_sales = df.groupby("county", dropna=False).agg(
            total_sales=("sale_dollars", "sum"),
            total_margin=("margin_amount", "sum"),
            total_bottles_sold=("bottles_sold", "sum")
        ).reset_index()
        county_sales["county_name_key"] = county_sales["county"].apply(normalize_county_name)
        county_sales["county_fips"] = county_sales["county"].apply(county_to_iowa_fips)

        county_merge = county_sales.merge(geo_counties, on="county_name_key", how="left")
        missing_fips = county_merge["FIPS"].isna() & county_merge["county_fips"].notna()
        if missing_fips.any():
            fips_to_county = dict(zip(geo_counties["FIPS"], geo_counties["geo_county"]))
            county_merge.loc[missing_fips, "FIPS"] = county_merge.loc[missing_fips, "county_fips"]
            county_merge.loc[missing_fips, "geo_county"] = county_merge.loc[missing_fips, "county_fips"].map(fips_to_county)
        county_merge = county_merge[county_merge["FIPS"].notna()].copy()

        if county_merge.empty:
            st.info("Mapa choropletyczna county jest niedostępna dla aktualnych danych, bo nie dopasowano nazw county ani kodów FIPS.")
        else:
            fig_choropleth = px.choropleth_mapbox(
                county_merge,
                geojson=geojson_data,
                locations="FIPS",
                featureidkey="properties.FIPS",
                color="total_sales",
                color_continuous_scale="Blues",
                range_color=(county_merge["total_sales"].min(), county_merge["total_sales"].max()),
                mapbox_style="carto-positron",
                zoom=5,
                center={"lat": 42.0, "lon": -93.5},
                hover_name="county",
                hover_data={
                    "geo_county": True,
                    "total_sales": ":$,.0f",
                    "total_margin": ":$,.0f",
                    "total_bottles_sold": ",.0f"
                },
                height=550,
                title="Mapa choropletyczna county (sprzedaż łącznie)"
            )
            show_chart(fig_choropleth, key="geo_county_choropleth")
    else:
        st.info("Dane GeoJSON są niedostępne. Mapa choropletyczna county jest niedostępna.")

    if not city_map_df.empty:
        fig_city = px.scatter_mapbox(
            city_map_df,
            lat="latitude",
            lon="longitude",
            size="total_sales",
            color="total_volume_liters",
            hover_name="city",
            hover_data=["county", "store_count", "total_sales", "total_volume_liters"],
            zoom=5,
            height=550,
            title="Mapa bąbelkowa miast (jeden punkt na miasto, rozmiar=sprzedaż)"
        )
        fig_city.update_layout(mapbox_style="carto-positron")
        show_chart(fig_city, key="geo_city_bubble_map")

    store_map = map_df.sort_values("total_sales", ascending=False).head(max(top_n, 10))
    if not store_map.empty:
        fig_stores = px.scatter_mapbox(
            store_map,
            lat="latitude",
            lon="longitude",
            size="total_bottles_sold",
            color="total_margin",
            hover_name="store_name",
            hover_data=["store_number", "city", "county", "total_sales", "total_margin", "total_bottles_sold", "invoice_count"],
            zoom=5,
            height=550,
            title=f"Mapa bąbelkowa top {top_n} sklepów (rozmiar=butelki, kolor=marża)"
        )
        fig_stores.update_layout(mapbox_style="carto-positron")
        show_chart(fig_stores, key="geo_store_sales_map")
    else:
        st.info("Mapa sklepów jest niedostępna dla aktualnego zakresu filtrów, bo brakuje współrzędnych.")

    show_report_table(
        f"Top {top_n} county według sprzedaży",
        county.sort_values("total_sales", ascending=False),
        ["county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "store_count"],
        file_stem="top_counties_by_sales",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} miast według sprzedaży",
        city.sort_values("total_sales", ascending=False),
        ["city", "county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin"],
        file_stem="top_cities_by_sales",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "Q9: county z wysokim wolumenem i niższą sprzedażą na litr",
        high_volume_low_value,
        ["rank", "county", "total_volume_liters", "sales_per_liter", "total_sales", "store_count"],
        file_stem="q9_high_volume_lower_sales_per_liter",
        money_cols=["total_sales", "sales_per_liter"],
    )


def store_performance(df: pd.DataFrame, avg_sales_per_store: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state, default=15)
    show_semantic_sources(["vw_sales_overview", "vw_avg_sales_per_store_by_month_region"])
    show_scope_summary(df, filter_state)
    stores = aggregate(df, ["store_number", "store_name", "city", "county"]).sort_values("total_sales", ascending=False)
    low_value_volume = stores.copy()
    low_value_volume["sales_per_liter"] = (
        low_value_volume["total_sales"] / low_value_volume["total_volume_liters"].replace(0, pd.NA)
    )
    low_value_volume = low_value_volume.sort_values(
        ["total_volume_liters", "sales_per_liter"], ascending=[False, True]
    ).head(top_n)

    county_avg = stores.groupby("county", dropna=False).agg(
        avg_sales_per_store=("total_sales", "mean"),
        store_count=("store_number", "nunique"),
    ).reset_index().sort_values("avg_sales_per_store", ascending=False).head(top_n)

    c1, c2 = st.columns(2)
    with c1:
        top_stores = stores.head(top_n)
        fig = px.bar(top_stores, x="total_sales", y="store_name", orientation="h", title="Najlepsze sklepy według sprzedaży")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_chart(fig, key="store_top_stores")
    with c2:
        fig = px.scatter(
            low_value_volume,
            x="total_volume_liters",
            y="total_sales",
            size="total_volume_liters",
            hover_name="store_name",
            color="county",
            title="Sklepy z wysokim wolumenem i niższą sprzedażą",
        )
        show_chart(fig, key="store_high_volume_low_revenue")

    fig = px.bar(
        county_avg,
        x="avg_sales_per_store",
        y="county",
        orientation="h",
        title="Średnia sprzedaż na sklep według county",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    show_chart(fig, key="store_avg_sales_by_county")

    store_distribution = stores[stores["county"].isin(county_avg["county"].head(10).tolist())]
    if not store_distribution.empty:
        fig = px.box(
            store_distribution,
            x="county",
            y="total_sales",
            points="all",
            title="Rozkład sprzedaży sklepów według county",
        )
        show_chart(fig, key="store_sales_distribution_box")

    county_focus = (
        avg_sales_per_store.groupby("county", dropna=False)["avg_sales_per_store"]
        .mean()
        .sort_values(ascending=False)
        .head(8)
        .index.tolist()
    )
    avg_sales_focus = avg_sales_per_store[avg_sales_per_store["county"].isin(county_focus)].copy()
    if not avg_sales_focus.empty:
        fig = px.line(
            avg_sales_focus.sort_values("year_month"),
            x="year_month",
            y="avg_sales_per_store",
            color="county",
            markers=True,
            title="Średnia sprzedaż na sklep według miesiąca i county",
        )
        show_chart(fig, key="store_avg_sales_over_time")

    show_report_table(
        f"Top {top_n} sklepów",
        top_stores.sort_values("total_sales", ascending=False),
        ["store_number", "store_name", "city", "county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_stores",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "Sklepy z wysokim wolumenem i niższą sprzedażą",
        low_value_volume.sort_values(["total_volume_liters", "sales_per_liter"], ascending=[False, True]),
        ["store_number", "store_name", "city", "county", "total_volume_liters", "total_sales", "sales_per_liter", "total_margin"],
        file_stem="high_volume_lower_revenue_stores",
        money_cols=["total_sales", "sales_per_liter", "total_margin"],
    )
    show_report_table(
        "Średnia sprzedaż na sklep według county",
        county_avg.sort_values("avg_sales_per_store", ascending=False),
        ["county", "avg_sales_per_store", "store_count"],
        file_stem="average_sales_per_store_by_county",
        money_cols=["avg_sales_per_store"],
    )


st.title("Analityka dystrybucji detalicznej Iowa")
st.caption("Dashboard oparty na warstwie semantycznej SQL Server.")
show_dataset_status(read_extract_manifest())
show_semantic_layer_banner()

try:
    overview = read_view("vw_sales_overview")
    category_sales_over_time = read_view("vw_category_sales_over_time")
    avg_sales_per_store_by_month_region = read_view("vw_avg_sales_per_store_by_month_region")
    sales_map_points = read_view("vw_sales_map_points")
    margin_analysis = read_view("vw_margin_analysis")
    kpi_summary = read_view("vw_kpi_summary")
    etl_status = read_view("vw_etl_status")
except Exception as exc:
    st.error("Nie udało się połączyć z widokami semantycznymi SQL Server.")
    st.code(str(exc))
    st.stop()

show_etl_status_panel(etl_status)
show_global_kpi_reference(kpi_summary)

if overview.empty:
    st.warning("Widok semantyczny nie zwrócił wierszy. Najpierw uruchom DAG Airflow `iowa_liquor_etl`.")
    st.stop()

filtered_overview, filter_state = apply_filters(overview)
if filtered_overview.empty:
    st.warning("Żadne wiersze nie pasują do wybranych filtrów.")
    st.stop()

filtered_category_sales_over_time = apply_filter_state(category_sales_over_time, filter_state)
filtered_avg_sales_per_store = apply_filter_state(avg_sales_per_store_by_month_region, filter_state)
filtered_sales_map_points = apply_filter_state(sales_map_points, filter_state)
filtered_margin_analysis = apply_filter_state(margin_analysis, filter_state)

tabs = st.tabs(
    [
        "Przegląd zarządczy",
        "Produkty i kategorie",
        "Geografia",
        "Wyniki sklepów",
    ]
)

with tabs[0]:
    executive_overview(filtered_overview, filter_state)
with tabs[1]:
    product_category_analysis(filtered_overview, filtered_category_sales_over_time, filtered_margin_analysis, filter_state)
with tabs[2]:
    geography_analysis(filtered_overview, filtered_sales_map_points, filter_state)
with tabs[3]:
    store_performance(filtered_overview, filtered_avg_sales_per_store, filter_state)

