# Audyt gotowości projektu - 2026-07-04

## Werdykt

Projekt jest gotowy do prezentacji i spełnia wymagania merytoryczne. Najważniejsze elementy działają: Docker Compose, SQL Server, Airflow, ETL, warstwa semantyczna i dashboard Streamlit.

Największe ryzyko operacyjne: samo `docker compose up` uruchamia usługi, ale nie ładuje danych. Po starcie kontenerów trzeba uruchomić ETL komendą z README albo ręcznie z Airflow.

## Spełnienie wymagań

| Wymaganie | Status | Dowód |
|---|---|---|
| Realne dane, niegenerowane | Spełnione | Publiczny zbiór Iowa Liquor Sales oraz lokalny cache realnych plików CSV w `data/raw`. |
| 7-12 pytań biznesowych | Spełnione | Jest 12 pytań w `docs/business_requirements.md`. |
| Model wielowymiarowy | Spełnione | Schemat gwiazdy: `dw.fact_sales` plus 6 wymiarów. |
| Hurtownia danych | Spełnione | SQL Server, baza `IowaLiquorDW`, schematy `stg`, `dw`, `sem`. |
| ETL live | Spełnione | Airflow oraz komenda `python -m src.run_initial_etl`. |
| Warstwa semantyczna | Spełnione | Widoki SQL `sem.*`. |
| Raporty z wykresami | Spełnione | Dashboard Streamlit z KPI, wykresami, mapami, tabelami i eksportem CSV. |

Formalna rzecz do dopisania poza kodem: prawdziwy skład zespołu 2-4 osób, jeśli prowadząca tego wymaga w oddawanych materiałach.

## Wyniki ostatniej weryfikacji

Uruchomione kontrole:

```powershell
docker compose config --quiet
python -m compileall app src dags
docker compose build airflow streamlit
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

Wynik:

- Docker Compose poprawny.
- Obrazy Airflow i Streamlit budują się poprawnie.
- SQL Server działa jako zdrowy kontener.
- Airflow odpowiada HTTP 200.
- Streamlit odpowiada HTTP 200.
- Python kompiluje moduły `app`, `src`, `dags`.

## Wynik live ETL

Ostatni szybki run demo:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Wynik:

- staging: 10634 wiersze,
- fakt: 10624 wiersze,
- `eligible_staging_fact_row_count_difference = 0`,
- `null_foreign_keys = 0`,
- `negative_measures = 0`,
- `fact_dimension_join_failures = 0`,
- `eligible_staging_vs_fact_sales_difference = 0.0000`,
- ETL zakończony sukcesem.

API zwróciło 404, więc ETL użył lokalnego cache realnych plików raw. To nie są dane syntetyczne.

## Dashboard

Sprawdzone w przeglądarce:

- tytuł strony: `Hurtownia Iowa Liquor Sales`,
- widoczny tytuł: `Analityka dystrybucji detalicznej Iowa`,
- zakładki: `Przegląd zarządczy`, `Produkty i kategorie`, `Geografia`, `Wyniki sklepów`,
- liczba błędów widocznych w aplikacji: 0,
- liczba krzaków kodowania w widocznym tekście: 0.

## Polski język

Najważniejsze pliki do prezentacji zostały poprawione na naturalny polski z polskimi znakami:

- `README.md`,
- `docs/start_na_czystym_komputerze.md`,
- `docs/live_demo_checklista.md`,
- `docs/prezentacja_od_a_do_z.md`,
- `docs/pytania_i_odpowiedzi_techniczne.md`,
- `docs/nauka_projektu/01_projekt_od_zera_podrecznik.md`.

Angielski zostaje tam, gdzie jest uzasadniony technicznie: nazwy technologii, tabel, widoków, kolumn, `vendor`, `county`, Iowa Liquor Sales.

## Czysty komputer

Na komputerze z Docker Desktop projekt powinien się uruchomić tak:

```powershell
cd D:\pjatk-idh\data-warehouse-iowa-liquor
docker compose up -d sqlserver airflow streamlit
docker compose ps
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Adresy:

- Airflow: `http://localhost:8080`
- Streamlit: `http://localhost:8501`

Jeśli Airflow wymaga hasła:

```powershell
Airflow: admin / admin
SQL Server: admin / admin
```

Bez Dockera projekt nie ma prostej ścieżki startu jednym poleceniem. Trzeba ręcznie zainstalować SQL Server, ODBC Driver 18, Python 3.11, pakiety z `requirements.txt` i ustawić zmienne środowiskowe. Na prezentację rekomendowany jest Docker.

## Poprawki wykonane po audycie

- Dodano `.dockerignore`, żeby build nie wysyłał 827 MB plików CSV do kontekstu obrazu.
- README dostał quick start, live ETL, informację o haśle Airflow i wariant bez Dockera.
- Dodano `docs/start_na_czystym_komputerze.md`.
- Poprawiono `docs/live_demo_checklista.md`.
- Poprawiono `docs/prezentacja_od_a_do_z.md`.
- Poprawiono `docs/pytania_i_odpowiedzi_techniczne.md`.
- Poprawiono `app/main.py`, żeby nie wyglądał jak stary angielski dashboard.

## Co powiedzieć prowadzącej

```text
Projekt jest gotowy do prezentacji. Uruchamiam usługi Docker Compose, potem odpalam ETL dla krótkiego zakresu demonstracyjnego, pokazuję quality checks, a następnie dashboard Streamlit. Dashboard korzysta z widoków semantycznych SQL Server i odpowiada na 12 pytań biznesowych. Bez Dockera da się uruchamiać elementy ręcznie, ale oficjalna ścieżka demo jest oparta na Docker Compose.
```
