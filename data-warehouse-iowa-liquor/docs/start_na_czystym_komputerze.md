# Uruchomienie na czystym komputerze

Ten dokument odpowiada na pytanie: czy projekt da się uruchomić na komputerze, który ma tylko Docker Desktop?

Krótka odpowiedź: tak, jeśli Docker działa poprawnie i porty `1433`, `8080`, `8501` są wolne.

## 1. Co musi być zainstalowane

Wariant rekomendowany:

- Docker Desktop,
- dostęp do terminala PowerShell,
- folder projektu `data-warehouse-iowa-liquor`.

Nie trzeba lokalnie instalować SQL Server, Airflow, Streamlit ani sterowników ODBC. Są instalowane w kontenerach.

## 2. Pierwszy start

Wejdź do katalogu projektu:

```powershell
cd D:\pjatk-idh\data-warehouse-iowa-liquor
```

Uruchom usługi:

```powershell
docker compose up -d sqlserver airflow streamlit
```

Sprawdź status:

```powershell
docker compose ps
```

Oczekiwane:

```text
iowa-liquor-sqlserver   Up ... healthy
iowa-liquor-airflow     Up
iowa-liquor-streamlit   Up
```

## 3. Adresy aplikacji

Airflow:

```text
http://localhost:8080
```

Streamlit:

```text
http://localhost:8501
```

Logowanie do narzędzi używanych na prezentacji:

```text
Airflow: admin / admin
SQL Server: admin / admin
```

## 4. Live ETL do prezentacji

ETL można uruchomić z Airflow UI albo z terminala. Na prezentacji lepszy jest Airflow UI, bo widać graf zadań, statusy i logi.

W Airflow:

1. Wejdź w `http://localhost:8080`.
2. Zaloguj się `admin / admin`.
3. Otwórz DAG `iowa_liquor_etl`.
4. Kliknij `Trigger DAG` / ikonę play.
5. Sprawdź pola `start_date`, `end_date` i `limit`.
6. Daty wpisuje się w formacie `YYYY-MM-DD`.
7. Domyślny zakres projektu to pełny rok 2023:

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "limit": 5000
}
```

8. Kliknij `Trigger`.

Domyślny i rekomendowany zakres projektu to pełny rok `2023-01-01` do `2023-12-31`.

Z terminala można uruchomić ten sam pełny zakres:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-01 -e IOWA_END_DATE=2023-12-31 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Samo `docker compose up` uruchamia usługi, ale nie ładuje danych do hurtowni. Ten krok ETL jest potrzebny, żeby dashboard miał aktualnie załadowane dane.

Dlaczego można zawęzić zakres?

```text
Domyślnie projekt używa pełnego roku 2023. Zawężenie zakresu w Airflow jest tylko sposobem na krótszy test techniczny, gdy na prezentacji liczy się czas.
```

## 5. Co powinno być w logach

Najważniejsze linie i warunki. Konkretne liczby wierszy zależą od zakresu dat:

```text
Loaded ... total rows into stg.iowa_liquor_sales_raw
Loaded ... rows into dw.fact_sales
Quality check eligible_staging_fact_row_count_difference = 0
Quality check null_foreign_keys = 0
Quality check negative_measures = 0
Quality check fact_dimension_join_failures = 0
Quality check eligible_staging_vs_fact_sales_difference = 0.0000
Initial ETL finished
```

Może pojawić się też:

```text
Source API extraction failed: 404 Client Error
Source API unavailable. Reused cached real raw files
```

To nie jest problem na demo. Oznacza, że publiczny endpoint API był niedostępny, więc projekt użył lokalnego cache realnych plików raw.

## 6. Co jeśli Airflow nie odpowiada

Jeżeli `docker compose ps` pokazuje, że Airflow działa, ale przeglądarka nie otwiera `http://localhost:8080`, odtwórz kontener:

```powershell
docker compose up -d --force-recreate airflow
```

Poczekaj około 60 sekund i sprawdź:

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

Kod `200` oznacza, że UI odpowiada.

## 7. Co jeśli Streamlit nie odpowiada

Sprawdź:

```powershell
docker compose ps
docker compose logs streamlit --tail=80
```

Najczęstsze przyczyny:

- port `8501` jest zajęty,
- SQL Server jeszcze nie jest gotowy,
- Docker Desktop nie ma wystarczających zasobów.

## 8. Uruchomienie w GitHub Codespaces (Chmura)

Jeśli nie masz lokalnie Dockera lub brakuje zasobów na komputerze, bardzo dobrą ścieżką jest GitHub Codespaces:

1. Przejdź do repozytorium na GitHubie.
2. Kliknij zielony przycisk **Code** -> zakładka **Codespaces** -> **Create codespace on main**.
3. Po załadowaniu środowiska (VS Code w oknie przeglądarki), w terminalu uruchom:
   ```bash
   docker compose up -d sqlserver airflow streamlit
   ```
4. Codespaces automatycznie przekieruje porty. W zakładce **Ports** znajdziesz port `8080` (Airflow) i `8501` (Streamlit). Kliknij ikonę globu przy każdym z nich, aby otworzyć odpowiednie narzędzie w nowej karcie.
5. Uruchom proces ETL w Airflow tak samo jak opisano w punkcie 4.

## 9. Co jeśli nie ma Dockera ani Codespaces

Bez Dockera projekt nie jest gotowy do prostego uruchomienia jednym poleceniem.

Trzeba wtedy samodzielnie przygotować:

- SQL Server,
- ODBC Driver 18 for SQL Server,
- Python 3.11,
- pakiety z `requirements.txt`,
- zmienne środowiskowe z `.env.example`,
- bazę `IowaLiquorDW`,
- dostęp aplikacji do SQL Server.

To jest możliwe technicznie, ale nie jest dobrą ścieżką na obronę. Docker jest tutaj częścią architektury demonstracyjnej, bo zamyka zależności w kontenerach.

## 10. Minimalna odpowiedź dla prowadzącej

```text
Projekt jest przygotowany do uruchomienia przez Docker Compose. Na czystym komputerze z Docker Desktop wystarczy uruchomić docker compose up -d, poczekać aż SQL Server będzie healthy, a potem odpalić ETL i dashboard. Bez Dockera trzeba ręcznie instalować SQL Server, Airflow, Streamlit i sterowniki ODBC, więc na prezentację używamy Dockera.
```
