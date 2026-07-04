# Przewodnik Live Demo

Ten przewodnik to techniczna checklista i notatki wspierające demonstrację projektu na żywo.

## 1. Przed prezentacją

**Otwórz terminal w folderze projektu:**
```powershell
cd D:\pjatk-idh\data-warehouse-iowa-liquor
```

**Sprawdź Docker:**
```powershell
docker version
docker compose version
```

**Uruchom stack:**
```powershell
docker compose up -d sqlserver airflow streamlit
```

**Sprawdź kontenery:**
```powershell
docker compose ps
```
> [!IMPORTANT]
> Oczekiwane statusy to: `iowa-liquor-sqlserver` - `healthy`, `iowa-liquor-airflow` - `Up`, `iowa-liquor-streamlit` - `Up`. Ważne: projekt używa Docker containers, a nie Kubernetes pods.

**Gdyby Airflow UI nie odpowiadał:**
```powershell
docker compose up -d --force-recreate airflow
```

## 2. Kolejność pokazu Live Demo

### Krok 1 - Kontenery
- Pokaż status z terminala (`docker compose ps`).

### Krok 2 - Airflow UI (Orkiestracja i ETL)
- **URL**: `http://localhost:8080`
- **Logowanie**: `admin / admin`
- Otwórz DAG `iowa_liquor_etl`.
- Kliknij `Trigger DAG` w prawym górnym rogu.
- **Parametry**: Zostaw domyślne. Będą to `start_date`=2023-01-01, `end_date`=2023-12-31, `limit`=5000. Domyślny zakres projektu to pełny rok 2023.
- Kliknij `Trigger`.

**Zastępcza komenda ETL z terminala (jeśli Airflow UI zawiedzie):**
```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-01 -e IOWA_END_DATE=2023-12-31 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

### Krok 3 - Omówienie danych (Raw)
- Pokaż katalog `data/raw`.
- Wskaż pliki `iowa_liquor_sales_2023_part_000.csv` itd.
- **Co powiedzieć o API 404 (opcjonalnie):** "Jeśli publiczny endpoint API jest czasowo niedostępny, ETL używa lokalnego cache z realnych plików raw, a nie danych generowanych."

### Krok 4 - SQL Server (Hurtownia i Model)
- **Logowanie**: `admin / admin` (np. przez SSMS/DBeaver)
- Pokaż schematy `stg`, `dw`, `sem`.
- Pokaż tabelę stagingową `stg.iowa_liquor_sales_raw`.
- Pokaż `dw.fact_sales` i 6 wymiarów.
- **Uwagi do modelu**: Geografia jest zaszyta w `dim_store`. `state_bottle_cost` to miara jednostkowa, nieaddytywna.

### Krok 5 - Warstwa Semantyczna
- Możesz wykonać testowe zapytania, np.:
  `SELECT TOP 10 * FROM sem.vw_sales_by_month`
  `SELECT * FROM sem.vw_kpi_summary`
- Jest to pomost między hurtownią a aplikacją raportującą.

### Krok 6 - Quality Checks (w logach Airflow)
Czego szukać w logach ETL:
- `Loaded ... total rows into stg.iowa_liquor_sales_raw`
- `Loaded ... rows into dw.fact_sales`
- `Quality check eligible_staging_fact_row_count_difference = 0`
- `Quality check null_foreign_keys = 0`
- `Quality check fact_dimension_join_failures = 0`
- `Quality check eligible_staging_vs_fact_sales_difference = 0.0000`

### Krok 7 - Streamlit Dashboard
- **URL**: `http://localhost:8501`
- Pokazujemy poszczególne zakładki:
  1. Przegląd zarządczy
  2. Produkty i kategorie
  3. Geografia
  4. Wyniki sklepów

## 3. Podsumowanie (Jednozdaniowe zamknięcie)

> Projekt pokazuje pełną ścieżkę od realnych danych raw, przez ETL i model gwiazdy w SQL Server, po warstwę semantyczną i dashboard z raportami odpowiadającymi na 12 pytań biznesowych.
