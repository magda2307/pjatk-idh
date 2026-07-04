# Live demo - checklista

## Przed prezentacją

Otwórz terminal w:

```powershell
D:\pjatk-idh\data-warehouse-iowa-liquor
```

Sprawdź Docker:

```powershell
docker version
docker compose version
```

Uruchom stack:

```powershell
docker compose up -d sqlserver airflow streamlit
```

Sprawdź kontenery:

```powershell
docker compose ps
```

Oczekiwane:

- `iowa-liquor-sqlserver` - `healthy`,
- `iowa-liquor-airflow` - `Up`,
- `iowa-liquor-streamlit` - `Up`.

## Jeśli Airflow UI nie odpowiada

```powershell
docker compose up -d --force-recreate airflow
```

Poczekaj około 60 sekund i sprawdź:

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

## Sprawdzenie aplikacji

```powershell
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

Otwórz:

- Airflow: `http://localhost:8080`
- Streamlit: `http://localhost:8501`

Logowanie:

```text
Airflow: admin / admin
SQL Server: admin / admin
```

## Uruchomienie live ETL

Wariant rekomendowany na prezentacji: Airflow UI.

1. Otwórz DAG `iowa_liquor_etl`.
2. Kliknij `Trigger DAG` / ikonę play w prawym górnym rogu.
3. Na ekranie triggera sprawdź pola:
   - `start_date`
   - `end_date`
   - `limit`
4. Format dat to `YYYY-MM-DD`.
5. Domyślny zakres projektu to pełny rok 2023:

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "limit": 5000
}
```

6. Kliknij `Trigger`.

Ten sam pełny zakres obowiązuje także przy ręcznym wpisaniu konfiguracji:

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "limit": 5000
}
```

Wariant awaryjny z terminala dla pełnego roku 2023:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-01 -e IOWA_END_DATE=2023-12-31 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

## Co ma być w logach ETL

Szukaj nazw kroków i statusów, nie jednej konkretnej liczby wierszy. Liczby zależą od zakresu dat.

```text
Loaded ... total rows into stg.iowa_liquor_sales_raw
Loaded ... rows into dw.fact_sales
Quality check eligible_staging_fact_row_count_difference = 0
Quality check null_foreign_keys = 0
Quality check fact_dimension_join_failures = 0
Quality check eligible_staging_vs_fact_sales_difference = 0.0000
Initial ETL finished
```

## Co powiedzieć przy API 404

```text
Publiczny endpoint API jest czasowo niedostępny albo zmieniony. Projekt ma zabezpieczenie: nie usuwa raw danych, tylko odtwarza demo extract z lokalnego cache realnych plików raw. To nadal są dane niegenerowane.
```

## Kolejność pokazu

1. `docker compose ps`
2. Airflow UI i DAG `iowa_liquor_etl`
3. Live ETL w Airflow UI
4. Quality checks w logach
5. Streamlit dashboard
6. Zakładka `Przegląd zarządczy`
7. Zakładka `Produkty i kategorie`
8. Zakładka `Geografia`
9. Zakładka `Wyniki sklepów`
10. Podsumowanie rubryki

## Jednozdaniowe zamknięcie

```text
Projekt pokazuje pełną ścieżkę od realnych danych raw, przez ETL i model gwiazdy w SQL Server, po warstwę semantyczną i dashboard z raportami odpowiadającymi na 12 pytań biznesowych.
```
