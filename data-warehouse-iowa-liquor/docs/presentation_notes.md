# Notatki do prezentacji

## Co pokazac na zywo

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
   - wskazac pliki `iowa_liquor_sales_2023_part_000.csv` itd.

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
   - pokazac KPI, wykres miesieczny, kategorie, vendorow, geografie i sklepy,
   - podkreslic, ze aplikacja czyta tylko z widokow `sem`.

## Krotka narracja

Projekt uzywa realnych danych publicznych. Dane sa pobierane przez API, zapisywane jako warstwa raw, ladowane do SQL Server staging, a nastepnie przeksztalcane do modelu wymiarowego. SQL views w schemacie `sem` tworza warstwe semantyczna, a dashboard Streamlit korzysta tylko z tej warstwy.

## Co powiedziec o uruchomieniu

- Airflow i Streamlit sa uruchamiane z Docker Compose.
- SQL Server dziala lokalnie w kontenerze.
- Status uslug sprawdzamy przez `docker compose ps`.
- Logi sprawdzamy przez `docker logs`.

## Elementy punktowane

- Pytania biznesowe: [business_requirements.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/business_requirements.md)
- Schemat gwiazdy: [dimensional_model.md](/D:/pjatk-idh/data-warehouse-iowa-liquor/docs/dimensional_model.md)
- ETL poczatkowy: [iowa_liquor_etl_dag.py](/D:/pjatk-idh/data-warehouse-iowa-liquor/dags/iowa_liquor_etl_dag.py)
- Warstwa semantyczna: widoki `sem.*`
- Raporty: [streamlit_app.py](/D:/pjatk-idh/data-warehouse-iowa-liquor/app/streamlit_app.py)
