# Notatki do prezentacji

## Co pokazac na zywo

Pelny scenariusz obrony:

- `docs/scenariusz_obrony_od_a_do_z.md`
- `docs/pytania_i_odpowiedzi_techniczne.md`
- `docs/live_demo_checklista.md`

1. Docker containers
   - uruchomic:
     `docker compose up -d sqlserver airflow streamlit`
   - pokazac status:
     `docker compose ps`
   - wyjasnic, ze projekt uzywa Docker containers, nie Kubernetes pods.

2. Airflow UI
   - otworzyc `http://localhost:8080`,
   - zalogowac sie:
     `admin / admin`,
   - znalezc DAG `iowa_liquor_etl`,
   - uruchomic DAG recznie,
   - pokazac logi z ekstrakcji, ladowania i quality checks.

3. Pliki raw
    - pokazac katalog `data/raw`,
    - wskazac pliki `iowa_liquor_sales_2023_part_000.csv` itd.,
    - wyjasnic zakres: domyslna ekstrakcja raw obejmuje pelny rok 2023, ale szybki pokaz na zywo moze uzyc jednego dnia,
    - wyjasnic, ze jesli publiczny endpoint API jest czasowo niedostepny, ETL uzywa lokalnego cache z realnych plikow raw, a nie danych generowanych.

4. SQL Server
   - pokazac schematy `stg`, `dw`, `sem`,
   - pokazac `stg.iowa_liquor_sales_raw`,
   - pokazac `dw.fact_sales`,
   - pokazac wymiary, szczegolnie `dim_store` i `dim_packaging`.

5. Schemat gwiazdy
   - omowic ziarno faktu,
   - pokazac szesc wymiarow,
   - podkreslic, ze geografia jest w `dim_store`,
   - podkreslic, ze `state_bottle_cost` i `state_bottle_retail` sa miarami jednostkowymi, nieaddytywnymi.

6. Widoki semantyczne
   - uruchomic `SELECT TOP 10 * FROM sem.vw_sales_by_month`,
   - uruchomic `SELECT TOP 10 * FROM sem.vw_sales_by_category`,
   - uruchomic `SELECT * FROM sem.vw_kpi_summary`.

7. Streamlit dashboard
    - otworzyc `http://localhost:8501`,
    - pokazac zakladki: `Przeglad zarzadczy`, `Produkty i kategorie`, `Geografia`, `Wyniki sklepow`,
    - pokazac KPI, wykres miesieczny, kategorie, vendorow, geografie i sklepy,
    - podkreslic, ze raportowanie jest oparte o widoki `sem`, a lista widokow pokazuje pokrycie warstwy semantycznej.

## Krotka narracja

Projekt uzywa realnych danych publicznych. Dane sa pobierane przez API albo, przy niedostepnosci endpointu, odtwarzane z lokalnego cache realnych plikow raw. Nastepnie sa ladowane do SQL Server staging i przeksztalcane do modelu wymiarowego. SQL views w schemacie `sem` tworza warstwe semantyczna, a dashboard Streamlit korzysta z tej warstwy.

## Zakresy do wyjasnienia

| Zakres | Co oznacza | Jak mowic na prezentacji |
|---|---|---|
| Full-year raw extract | Domyslny zakres API: `2023-01-01` do `2023-12-31`; dane sa zapisywane jako partycje CSV. | Projekt jest przygotowany na pelny rok danych. |
| One-day live demo | Szybki run `2023-01-03`, dobry do pokazania ETL podczas zajec. | To zakres demonstracyjny, nie limit projektu. |
| One-month validation | Walidacja `2023-01-01` do `2023-01-31`, opisana w `docs/validation_report.md`. | Potwierdza, ze mechanizm dziala na wiekszym zakresie niz demo. |
| Full-year calendar dimension | `dw.dim_date` zawiera 365 dni roku 2023 niezaleznie od zakresu aktualnie zaladowanego faktu. | Wymiar czasu jest kalendarzem referencyjnym, nie dowodem liczby faktow. |

## Co powiedziec o uruchomieniu

- Airflow i Streamlit sa uruchamiane z Docker Compose.
- SQL Server dziala lokalnie w kontenerze.
- Status uslug sprawdzamy przez `docker compose ps`.
- Logi sprawdzamy przez `docker logs`.

## Rubryka i dowody

| Rubryka | Dowod w projekcie |
|---|---|
| Realne zrodlo danych | Iowa Liquor Sales, raw CSV w `data/raw`; awaryjny demo extract jest filtrowany z tych realnych plikow, nie generowany. |
| Model wymiarowy | `dw.fact_sales` + 6 wymiarow: date, store, product, category, vendor, packaging. |
| ETL / orkiestracja | DAG `iowa_liquor_etl` w `dags/iowa_liquor_etl_dag.py`. |
| Warstwa semantyczna | Widoki `sem.*`, opisane w `docs/warstwa_semantyczna.md`. |
| Pytania biznesowe | 12 pytan i mapowanie w `docs/business_requirements.md`. |
| Raportowanie | Dashboard Streamlit w `app/streamlit_app.py`. |
| Walidacja jakosci | `sql/05_quality_checks.sql` i `docs/validation_report.md`. |
