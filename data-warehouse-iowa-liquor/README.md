# Hurtownia danych do analizy sprzedazy, produktow, sklepow i regionow na podstawie danych Iowa Liquor Sales

Projekt przedstawia kompletna hurtownie danych dla analizy sprzedazy detalicznej i dystrybucji regulowanych produktow. Dane pochodza z publicznego zbioru Iowa Liquor Sales udostepnianego przez Socrata API. Projekt jest przygotowany pod kurs z architektury hurtowni danych i obejmuje:

- realne dane publiczne,
- pytania biznesowe,
- model wymiarowy i schemat gwiazdy,
- ETL w Apache Airflow,
- SQL Server jako warstwe hurtowni,
- SQL views jako warstwe semantyczna,
- dashboard Streamlit z raportami i wykresami.

## Cel projektu

Projekt wspiera analize sprzedazy na poziomie daty, sklepu, regionu, kategorii, vendora, produktu i opakowania. Narracja projektu dotyczy retail distribution analytics, nie analizy konsumpcji.

## Zrodlo danych

Publiczny zbior danych:

```text
Iowa Liquor Sales
Socrata resource ID: m3tr-qhgy
Endpoint: https://data.iowa.gov/resource/m3tr-qhgy.csv
```

Domyslny zakres ekstrakcji:

```text
2023-01-01 to 2023-12-31
```

Paginacja:

```text
$limit=50000
$offset=0
$offset=50000
$offset=100000
...
```

Pliki raw zapisywane sa lokalnie:

```text
data/raw/iowa_liquor_sales_2023_part_000.csv
data/raw/iowa_liquor_sales_2023_part_001.csv
...
```

## Architektura

```mermaid
flowchart LR
    A[Iowa Liquor Sales Socrata CSV API] --> B[Airflow Extract]
    B --> C[Raw CSV Files]
    C --> D[SQL Server Staging]
    D --> E[SQL Server DW Star Schema]
    E --> F[SQL Semantic Views]
    F --> G[Streamlit Dashboard]
```

## Stack

- Apache Airflow
- SQL Server
- SQL views w schemacie `sem`
- Streamlit
- Docker Compose

## Model wymiarowy

Schemat gwiazdy zawiera:

- `dw.fact_sales`
- `dw.dim_date`
- `dw.dim_store`
- `dw.dim_product`
- `dw.dim_category`
- `dw.dim_vendor`
- `dw.dim_packaging`

Kluczowe zalozenia modelu:

- ziarno faktu: jedna linia sprzedazy produktu w sklepie, w danym dniu i na danej fakturze,
- `sales_line_count` jest miara addytywna,
- `state_bottle_cost` i `state_bottle_retail` sa miarami jednostkowymi, nieaddytywnymi,
- geografia jest utrzymywana w `dim_store`,
- szosty wymiar to `dim_packaging`, a nie zduplikowana geografia.

Szczegoly: [dimensional_model.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/dimensional_model.md)

## Pytania biznesowe

Projekt odpowiada na 10 pytan biznesowych, miedzy innymi:

1. Jak zmieniala sie wartosc sprzedazy w miesiacach i kwartalach?
2. Ktore kategorie generowaly najwyzszy przychod?
3. Ktore sklepy osiagnely najwyzsza sprzedaz wartosciowa?
4. Ktore miasta i hrabstwa generowaly najwiekszy obrot?
5. Ktorzy vendorzy mieli najwiekszy udzial w sprzedazy?
6. Ktore produkty sprzedawaly sie najlepiej ilosciowo?
7. Ktore produkty lub kategorie generowaly najwyzsza marze?
8. Jak zmieniala sie struktura sprzedazy wedlug kategorii w czasie?
9. Ktore regiony mialy wysoki wolumen i nizsza wartosc sprzedazy?
10. Jaka byla srednia wartosc sprzedazy na sklep w podziale na miesiace i regiony?

Pelne mapowanie: [business_requirements.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/business_requirements.md)

## ETL Process

DAG Airflow `iowa_liquor_etl` wykonuje:

1. `extract_iowa_liquor_sales`
2. `create_sql_objects`
3. `load_staging`
4. `load_dimensions`
5. `load_fact_sales`
6. `create_semantic_views`
7. `run_quality_checks`

Projekt uzywa prostego full refresh. To celowy wybor dla projektu studenckiego: latwiej pokazac i obronic ETL na prezentacji.

Szczegoly ETL: [etl_description.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/etl_description.md)

## Semantic Layer

Warstwa semantyczna to SQL views w schemacie `sem`:

- `sem.vw_sales_overview`
- `sem.vw_sales_by_month`
- `sem.vw_sales_by_category`
- `sem.vw_sales_by_store`
- `sem.vw_sales_by_vendor`
- `sem.vw_sales_by_geography`
- `sem.vw_top_products`
- `sem.vw_margin_analysis`
- `sem.vw_volume_vs_revenue`
- `sem.vw_category_sales_over_time`
- `sem.vw_avg_sales_per_store_by_month_region`
- `sem.vw_kpi_summary`

Dashboard czyta tylko z tych widokow.

## Reports

Dashboard Streamlit ma 4 strony:

- `Executive overview`
- `Product and category analysis`
- `Geography analysis`
- `Store performance`

Mapowanie pytan do raportow:

| Pytanie | Strona dashboardu | Widoki SQL |
|---:|---|---|
| 1 | Executive overview | `sem.vw_sales_by_month`, `sem.vw_sales_overview` |
| 2 | Product and category analysis | `sem.vw_sales_by_category` |
| 3 | Store performance | `sem.vw_sales_by_store` |
| 4 | Geography analysis | `sem.vw_sales_by_geography` |
| 5 | Product and category analysis | `sem.vw_sales_by_vendor` |
| 6 | Product and category analysis | `sem.vw_top_products` |
| 7 | Product and category analysis | `sem.vw_margin_analysis`, `sem.vw_sales_by_category` |
| 8 | Product and category analysis | `sem.vw_category_sales_over_time` |
| 9 | Geography analysis, Store performance | `sem.vw_volume_vs_revenue` |
| 10 | Store performance | `sem.vw_avg_sales_per_store_by_month_region` |

## How To Run

### 1. Start stack

```powershell
docker compose up -d sqlserver airflow streamlit
```

### 2. Check services live

This project uses Docker containers, not Kubernetes pods.

To see live containers:

```powershell
docker compose ps
```

Expected services:

```text
sqlserver
airflow
streamlit
```

To inspect logs:

```powershell
docker logs iowa-liquor-airflow --tail 100
docker logs iowa-liquor-streamlit --tail 100
docker logs iowa-liquor-sqlserver --tail 100
```

### 3. Open Airflow

```text
http://localhost:8080
```

Login:

```text
username: admin
password: admin
```

### 4. Run ETL in Airflow UI

In Airflow:

1. Open DAG list.
2. Find `iowa_liquor_etl`.
3. Unpause if needed.
4. Trigger DAG manually.
5. Open task logs for:
   - `extract_iowa_liquor_sales`
   - `load_staging`
   - `load_fact_sales`
   - `run_quality_checks`

### 5. Run ETL from terminal

Quick demo run for one day:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Python local run:

```powershell
python -m src.run_initial_etl
```

### 6. Open dashboard

```text
http://localhost:8501
```

## How To Verify Project Works

### Raw files

```powershell
Get-ChildItem data\\raw
```

### Airflow DAG exists

```powershell
docker exec iowa-liquor-airflow airflow dags list
```

### SQL Server schemas and tables

Use SQL Server client or Airflow container shell.

Example:

```powershell
docker exec -it iowa-liquor-airflow bash
```

Then run Python or SQL checks.

### Semantic views

Check that views return rows:

```text
sem.vw_sales_overview
sem.vw_sales_by_month
sem.vw_sales_by_category
sem.vw_sales_by_store
sem.vw_sales_by_vendor
sem.vw_sales_by_geography
sem.vw_top_products
sem.vw_margin_analysis
sem.vw_volume_vs_revenue
sem.vw_kpi_summary
```

### Streamlit live

HTTP check:

```powershell
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
```

## Current Verified Demo State

Verified run for `2023-01-03`:

```text
staging rows: 10634
fact rows: 10624
null foreign keys: 0
negative fact measures: 0
semantic views: 12 views returning data
streamlit app: 0 exceptions in smoke test
```

## Documentation

- [project_description.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/project_description.md)
- [business_requirements.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/business_requirements.md)
- [dimensional_model.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/dimensional_model.md)
- [model_wielowymiarowy_etap2.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/model_wielowymiarowy_etap2.md)
- [uzasadnienie_modelu.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/uzasadnienie_modelu.md)
- [warstwa_semantyczna.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/warstwa_semantyczna.md)
- [etl_description.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/etl_description.md)
- [presentation_notes.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/presentation_notes.md)
- [progress.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/progress.md)

## Limitations

- Default verified run used one-day slice for fast demo.
- Full-year extract is possible but heavier on laptop resources.
- Project uses full refresh, not incremental loading.
- Container orchestration is Docker Compose, not Kubernetes.
