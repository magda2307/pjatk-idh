from __future__ import annotations

import json
from io import BytesIO
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

from src.config import EXTRACT_MANIFEST_PATH, SqlServerConfig


st.set_page_config(
    page_title="Iowa Liquor Sales DW",
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
    </style>
    """,
    unsafe_allow_html=True,
)


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


def apply_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list]]:
    filtered = df.copy()
    filter_state: dict[str, list] = {}

    with st.sidebar:
        st.header("Filters")
        if st.button("Refresh semantic data", width="stretch"):
            st.cache_data.clear()
            st.rerun()

        years = sorted(filtered["year"].dropna().unique().tolist())
        selected_years = st.multiselect("Year", years, default=years)
        filter_state["year"] = selected_years
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

        months = sorted(filtered["month"].dropna().unique().tolist())
        selected_months = st.multiselect("Month", months, default=months)
        filter_state["month"] = selected_months
        if selected_months:
            filtered = filtered[filtered["month"].isin(selected_months)]

        categories = sorted(filtered["category_name"].dropna().unique().tolist())
        selected_categories = st.multiselect("Category", categories)
        filter_state["category_name"] = selected_categories
        if selected_categories:
            filtered = filtered[filtered["category_name"].isin(selected_categories)]

        vendors = sorted(filtered["vendor_name"].dropna().unique().tolist())
        selected_vendors = st.multiselect("Vendor", vendors)
        filter_state["vendor_name"] = selected_vendors
        if selected_vendors:
            filtered = filtered[filtered["vendor_name"].isin(selected_vendors)]

        counties = sorted(filtered["county"].dropna().unique().tolist())
        selected_counties = st.multiselect("County", counties)
        filter_state["county"] = selected_counties
        if selected_counties:
            filtered = filtered[filtered["county"].isin(selected_counties)]

        cities = sorted(filtered["city"].dropna().unique().tolist())
        selected_cities = st.multiselect("City", cities)
        filter_state["city"] = selected_cities
        if selected_cities:
            filtered = filtered[filtered["city"].isin(selected_cities)]

        top_n = st.slider("Top N", min_value=5, max_value=25, value=10, step=5)
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
    years = ", ".join(str(year) for year in filter_state.get("year", [])) or "all"
    months = ", ".join(str(month) for month in filter_state.get("month", [])) or "all"
    st.caption(
        "Current scope: "
        f"years={years} | months={months} | rows={len(df):,} | "
        f"invoices={df['invoice_number'].nunique():,} | stores={df['store_number'].nunique():,}"
    )


def show_dataset_status(manifest: dict[str, object] | None) -> None:
    if not manifest:
        st.info("Extract manifest not found. Run ETL to register current dataset scope.")
        return
    st.caption(
        "Dataset status: "
        f"range={manifest.get('start_date')} -> {manifest.get('end_date')} | "
        f"files={manifest.get('file_count')} | rows={manifest.get('total_rows')} | "
        f"generated={manifest.get('generated_at_utc')}"
    )


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
    styled = report_df.style
    if money_cols:
        styled = styled.format({column: "${:,.2f}" for column in money_cols if column in report_df.columns})
    if pct_cols:
        styled = styled.format({column: "{:,.2f}%" for column in pct_cols if column in report_df.columns})
    st.dataframe(styled, width="stretch", hide_index=True)
    st.download_button(
        "Download CSV",
        data=build_csv_download(report_df),
        file_name=f"{file_stem}.csv",
        mime="text/csv",
        key=f"download_{file_stem}",
    )


def show_kpis(df: pd.DataFrame) -> None:
    cols = st.columns(6)
    cols[0].metric("Total sales", format_money(df["sale_dollars"].sum()))
    cols[1].metric("Total margin", format_money(df["margin_amount"].sum()))
    cols[2].metric("Bottles sold", format_number(df["bottles_sold"].sum()))
    cols[3].metric("Volume liters", format_number(df["volume_sold_liters"].sum()))
    cols[4].metric("Stores", format_number(df["store_number"].nunique()))
    cols[5].metric("Products", format_number(df["item_number"].nunique()))


def executive_overview(df: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state)
    show_kpis(df)
    show_scope_summary(df, filter_state)
    monthly = aggregate(df, ["year_month"]).sort_values("year_month")
    categories = aggregate(df, ["category_name"]).sort_values("total_sales", ascending=False).head(12)
    stores = aggregate(df, ["store_number", "store_name"]).sort_values("total_sales", ascending=False).head(top_n)

    left, right = st.columns([1.45, 1])
    with left:
        fig = px.line(monthly, x="year_month", y="total_sales", markers=True, title="Monthly sales")
        st.plotly_chart(fig, width="stretch", key="exec_monthly_sales")
    with right:
        fig = px.bar(categories, x="total_sales", y="category_name", orientation="h", title="Sales by category")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="exec_sales_by_category")

    fig = px.bar(stores, x="total_sales", y="store_name", orientation="h", title="Top stores by sales")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch", key="exec_top_stores")

    show_report_table(
        "Monthly sales summary",
        monthly.sort_values("year_month"),
        ["year_month", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="monthly_sales_summary",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} stores by sales",
        stores.sort_values("total_sales", ascending=False),
        ["store_number", "store_name", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_stores_by_sales",
        money_cols=["total_sales", "total_margin"],
    )


def product_category_analysis(df: pd.DataFrame, category_over_time: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state, default=15)
    show_scope_summary(df, filter_state)
    categories = aggregate(df, ["category_name"]).sort_values("total_sales", ascending=False).head(top_n)
    products = aggregate(df, ["item_number", "item_description"]).sort_values("total_bottles_sold", ascending=False).head(top_n)
    vendors = aggregate(df, ["vendor_name"]).sort_values("total_sales", ascending=False).head(12)

    margin_by_category = categories.copy()
    margin_by_category["avg_margin_per_bottle"] = (
        margin_by_category["total_margin"] / margin_by_category["total_bottles_sold"].replace(0, pd.NA)
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(categories, x="total_sales", y="category_name", orientation="h", title="Top categories by revenue")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="prod_top_categories")
    with c2:
        fig = px.bar(products, x="total_bottles_sold", y="item_description", orientation="h", title="Top products by bottles sold")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="prod_top_products")

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(margin_by_category, x="total_margin", y="category_name", orientation="h", title="Margin by category")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="prod_margin_by_category")
    with c4:
        fig = px.pie(vendors, names="vendor_name", values="total_sales", title="Vendor share of sales")
        st.plotly_chart(fig, width="stretch", key="prod_vendor_share")

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
            title="Sales structure by category over time",
        )
        st.plotly_chart(fig, width="stretch", key="prod_category_mix_time")

    show_report_table(
        f"Top {top_n} categories",
        categories.sort_values("total_sales", ascending=False),
        ["category_name", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count", "store_count"],
        file_stem="top_categories",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} products by bottles sold",
        products.sort_values("total_bottles_sold", ascending=False),
        ["item_number", "item_description", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_products_by_bottles_sold",
        money_cols=["total_sales", "total_margin"],
    )
    vendor_table = vendors.copy()
    vendor_table["sales_share_percent"] = (
        100 * vendor_table["total_sales"] / vendor_table["total_sales"].sum()
    ).round(2)
    show_report_table(
        "Vendor sales summary",
        vendor_table.sort_values("total_sales", ascending=False),
        ["vendor_name", "total_sales", "total_margin", "total_bottles_sold", "sales_share_percent"],
        file_stem="vendor_sales_summary",
        money_cols=["total_sales", "total_margin"],
        pct_cols=["sales_share_percent"],
    )


def geography_analysis(df: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state, default=20)
    show_scope_summary(df, filter_state)
    county = aggregate(df, ["county"]).sort_values("total_sales", ascending=False).head(top_n)
    city = aggregate(df, ["city", "county"]).sort_values("total_sales", ascending=False).head(top_n)
    volume = aggregate(df, ["county"]).sort_values("total_volume_liters", ascending=False).head(top_n)
    map_df = (
        df.dropna(subset=["latitude", "longitude"])
        .groupby(["city", "county", "latitude", "longitude"], dropna=False)
        .agg(total_sales=("sale_dollars", "sum"), total_volume_liters=("volume_sold_liters", "sum"))
        .reset_index()
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(county, x="total_sales", y="county", orientation="h", title="Sales by county")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="geo_sales_by_county")
    with c2:
        fig = px.bar(city, x="total_sales", y="city", color="county", orientation="h", title="Top cities by revenue")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="geo_top_cities")

    fig = px.scatter(
        volume,
        x="total_volume_liters",
        y="total_sales",
        size="store_count",
        hover_name="county",
        title="Volume vs revenue by county",
    )
    st.plotly_chart(fig, width="stretch", key="geo_volume_vs_revenue")

    if not map_df.empty:
        fig = px.scatter_mapbox(
            map_df,
            lat="latitude",
            lon="longitude",
            size="total_sales",
            color="total_volume_liters",
            hover_name="city",
            hover_data=["county", "total_sales"],
            zoom=5,
            height=520,
            title="Sales map by city",
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, width="stretch", key="geo_sales_map")
    else:
        st.info("Map unavailable for current filter scope because latitude/longitude are missing.")

    show_report_table(
        f"Top {top_n} counties by sales",
        county.sort_values("total_sales", ascending=False),
        ["county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "store_count"],
        file_stem="top_counties_by_sales",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        f"Top {top_n} cities by sales",
        city.sort_values("total_sales", ascending=False),
        ["city", "county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin"],
        file_stem="top_cities_by_sales",
        money_cols=["total_sales", "total_margin"],
    )
    volume_table = volume.copy()
    volume_table["sales_per_liter"] = (
        volume_table["total_sales"] / volume_table["total_volume_liters"].replace(0, pd.NA)
    )
    show_report_table(
        "Volume vs revenue by county",
        volume_table.sort_values("total_volume_liters", ascending=False),
        ["county", "total_volume_liters", "total_sales", "sales_per_liter", "store_count"],
        file_stem="volume_vs_revenue_by_county",
        money_cols=["total_sales", "sales_per_liter"],
    )


def store_performance(df: pd.DataFrame, avg_sales_per_store: pd.DataFrame, filter_state: dict[str, list]) -> None:
    top_n = get_top_n(filter_state, default=15)
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
        fig = px.bar(top_stores, x="total_sales", y="store_name", orientation="h", title="Top stores by sales")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch", key="store_top_stores")
    with c2:
        fig = px.scatter(
            low_value_volume,
            x="total_volume_liters",
            y="total_sales",
            size="store_count",
            hover_name="store_name",
            color="county",
            title="High volume stores with lower revenue",
        )
        st.plotly_chart(fig, width="stretch", key="store_high_volume_low_revenue")

    fig = px.bar(
        county_avg,
        x="avg_sales_per_store",
        y="county",
        orientation="h",
        title="Average sales per store by county",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch", key="store_avg_sales_by_county")

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
            title="Average sales per store by month and county",
        )
        st.plotly_chart(fig, width="stretch", key="store_avg_sales_over_time")

    show_report_table(
        f"Top {top_n} stores",
        top_stores.sort_values("total_sales", ascending=False),
        ["store_number", "store_name", "city", "county", "total_sales", "total_bottles_sold", "total_volume_liters", "total_margin", "invoice_count"],
        file_stem="top_stores",
        money_cols=["total_sales", "total_margin"],
    )
    show_report_table(
        "High volume, lower revenue stores",
        low_value_volume.sort_values(["total_volume_liters", "sales_per_liter"], ascending=[False, True]),
        ["store_number", "store_name", "city", "county", "total_volume_liters", "total_sales", "sales_per_liter", "total_margin"],
        file_stem="high_volume_lower_revenue_stores",
        money_cols=["total_sales", "sales_per_liter", "total_margin"],
    )
    show_report_table(
        "Average sales per store by county",
        county_avg.sort_values("avg_sales_per_store", ascending=False),
        ["county", "avg_sales_per_store", "store_count"],
        file_stem="average_sales_per_store_by_county",
        money_cols=["avg_sales_per_store"],
    )


st.title("Iowa Retail Distribution Analytics")
st.caption("Semantic-layer dashboard powered by SQL Server views.")
show_dataset_status(read_extract_manifest())

try:
    overview = read_view("vw_sales_overview")
    category_sales_over_time = read_view("vw_category_sales_over_time")
    avg_sales_per_store_by_month_region = read_view("vw_avg_sales_per_store_by_month_region")
except Exception as exc:
    st.error("Could not connect to SQL Server semantic views.")
    st.code(str(exc))
    st.stop()

if overview.empty:
    st.warning("Semantic view returned no rows. Run Airflow DAG `iowa_liquor_etl` first.")
    st.stop()

filtered_overview, filter_state = apply_filters(overview)
if filtered_overview.empty:
    st.warning("No rows match selected filters.")
    st.stop()

filtered_category_sales_over_time = apply_filter_state(category_sales_over_time, filter_state)
filtered_avg_sales_per_store = apply_filter_state(avg_sales_per_store_by_month_region, filter_state)

tabs = st.tabs(
    [
        "Executive overview",
        "Product and category analysis",
        "Geography analysis",
        "Store performance",
    ]
)

with tabs[0]:
    executive_overview(filtered_overview, filter_state)
with tabs[1]:
    product_category_analysis(filtered_overview, filtered_category_sales_over_time, filter_state)
with tabs[2]:
    geography_analysis(filtered_overview, filter_state)
with tabs[3]:
    store_performance(filtered_overview, filtered_avg_sales_per_store, filter_state)
