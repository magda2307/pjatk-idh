# Hurtownia danych - Iowa Liquor Sales

Projekt to uczelniana hurtownia danych do analizy sprzedaży detalicznej i dystrybucji na podstawie publicznego zbioru Iowa Liquor Sales. Celem nie jest analiza konsumpcji alkoholu, tylko analiza sprzedaży, wolumenu, marży, sklepów, geografii, kategorii, vendorów, produktów i opakowań.

Architektura:

```text
Iowa Liquor Sales / cached real raw CSV
-> Apache Airflow
-> raw CSV files
-> SQL Server staging
-> SQL Server dimensional warehouse
-> SQL semantic views
-> Streamlit dashboard
```

Jeśli publiczny endpoint API jest niedostępny, ETL korzysta z lokalnego cache realnych plików raw. To nadal nie są dane generowane.

## Szybki start na komputerze z Dockerem

Wymagane:

- Docker Desktop,
- wolne porty `1433`, `8080`, `8501`,
- sklonowany lub skopiowany folder projektu.

Uruchom w katalogu projektu:

```powershell
docker compose up -d sqlserver airflow streamlit
docker compose ps
```

Oczekiwany stan:

- `iowa-liquor-sqlserver` ma status `healthy`,
- `iowa-liquor-airflow` ma status `Up`,
- `iowa-liquor-streamlit` ma status `Up`.

Adresy:

- Airflow: `http://localhost:8080`
- Streamlit: `http://localhost:8501`

Logowanie:

```text
Airflow: admin / admin
SQL Server: admin / admin
```

Szybkie uruchomienie ETL do prezentacji z terminala:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-01 -e IOWA_END_DATE=2023-12-31 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Ten sam proces można uruchomić w Airflow UI. W DAG-u `iowa_liquor_etl` kliknij trigger/play i podaj domyślną konfigurację pełnego roku 2023:

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "limit": 5000
}
```

W logach powinno być widać między innymi:

```text
Loaded 10634 total rows into stg.iowa_liquor_sales_raw
Loaded 10624 rows into dw.fact_sales
Quality check eligible_staging_fact_row_count_difference = 0
Quality check null_foreign_keys = 0
Quality check fact_dimension_join_failures = 0
Quality check eligible_staging_vs_fact_sales_difference = 0.0000
Initial ETL finished
```

Pełniejsza instrukcja jest w [docs/start_na_czystym_komputerze.md](docs/start_na_czystym_komputerze.md).

## Uruchomienie w GitHub Codespaces

Projekt można również uruchomić w chmurze za pomocą GitHub Codespaces (które ma wbudowaną obsługę Dockera):

1. Na stronie repozytorium na GitHubie kliknij zielony przycisk **Code** -> zakładka **Codespaces** -> **Create codespace on main**.
2. Poczekaj na uruchomienie środowiska (otworzy się VS Code w przeglądarce).
3. W terminalu na dole ekranu uruchom:
   ```bash
   docker compose up -d sqlserver airflow streamlit
   ```
4. Codespaces automatycznie wykryje usługi i przekieruje porty. Przejdź do zakładki **Ports** (obok Terminala).
5. Kliknij ikonę globu (Open in Browser) przy portach `8080` (Airflow) i `8501` (Streamlit).
6. Uruchom proces ETL identycznie jak w przypadku lokalnym (przez Airflow UI lub terminal).

## Jeśli Airflow nie odpowiada

Airflow w trybie `standalone` czasem potrzebuje chwili po starcie. Jeśli kontener działa, ale UI jeszcze nie odpowiada:

```powershell
docker compose up -d --force-recreate airflow
```

Poczekaj około 60 sekund i sprawdź:

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

## Ważne: `docker compose up` nie ładuje danych

`docker compose up -d` uruchamia usługi: SQL Server, Airflow i Streamlit. Dane do hurtowni ładuje dopiero ETL. Dlatego po starcie kontenerów trzeba uruchomić komendę `python -m src.run_initial_etl` w kontenerze Airflow albo odpalić DAG z UI Airflow.

## Jeśli nie ma Dockera

Ten projekt jest przygotowany do uruchomienia przez Docker Compose, bo Docker dostarcza jednocześnie SQL Server, Airflow, sterowniki ODBC i Streamlit. Bez Dockera da się uruchamiać fragmenty kodu lokalnie, ale nie jest to rekomendowana ścieżka na prezentację.

Minimalnie trzeba wtedy samodzielnie zainstalować:

- SQL Server,
- sterownik ODBC Driver 18 for SQL Server,
- Python 3.11,
- pakiety z `requirements.txt`,
- zmienne środowiskowe zgodne z `.env.example`.

W praktyce: na obronę użyj Dockera. Bez niego rośnie ryzyko problemów środowiskowych.

## Model danych

Model wymiarowy to schemat gwiazdy z centralną tabelą faktów `dw.fact_sales` i sześcioma wymiarami:

- `dw.dim_date` - czas transakcji,
- `dw.dim_store` - sklep i lokalizacja,
- `dw.dim_product` - produkt,
- `dw.dim_category` - kategoria,
- `dw.dim_vendor` - vendor,
- `dw.dim_packaging` - opakowanie.

Ziarno faktu:

```text
Jeden rekord w dw.fact_sales oznacza jedną linię sprzedaży produktu w sklepie, w konkretnym dniu i na konkretnej fakturze.
```

## Pytania biznesowe

Projekt odpowiada na 12 pytań biznesowych, czyli mieści się w wymaganym zakresie 7-12. Pytania obejmują czas, sklepy, geografię, kategorie, vendorów, produkty, marżę, weekendy i opakowania.

Lista pytań: [docs/business_requirements.md](docs/business_requirements.md).

## Warstwa semantyczna i raporty

Warstwa semantyczna to widoki SQL w schemacie `sem`. Dashboard Streamlit czyta widoki `sem.*`, a nie bezpośrednio tabele techniczne.

Dashboard ma cztery główne zakładki:

- Przegląd zarządczy,
- Produkty i kategorie,
- Geografia,
- Wyniki sklepów.

Raporty zawierają KPI, wykresy, mapy, tabele i eksport CSV.

## Status gotowości

- Realne dane: tak, Iowa Liquor Sales i lokalny cache realnych plików raw.
- Pytania biznesowe: tak, 12 pytań.
- Schemat gwiazdy: tak, `dw.fact_sales` plus 6 wymiarów.
- ETL live: tak, Airflow oraz `src.run_initial_etl`.
- Hurtownia danych: tak, SQL Server.
- Warstwa semantyczna: tak, widoki `sem.*`.
- Raporty: tak, Streamlit z wykresami.

Formalnie przed oddaniem trzeba tylko wpisać prawdziwy skład zespołu 2-4 osób, jeśli prowadząca wymaga tego wprost w dokumentach.

## Najważniejsze pliki

- [demo_techniczne.html](demo_techniczne.html) - osobna strona do prowadzenia technicznego demo.
- [docs/start_na_czystym_komputerze.md](docs/start_na_czystym_komputerze.md) - uruchomienie od zera.
- [docs/live_demo_checklista.md](docs/live_demo_checklista.md) - szybka checklista prezentacji.
- [docs/prezentacja_od_a_do_z.md](docs/prezentacja_od_a_do_z.md) - narracja prezentacji.
- [docs/pytania_i_odpowiedzi_techniczne.md](docs/pytania_i_odpowiedzi_techniczne.md) - pytania techniczne.
- [docs/nauka_projektu/01_projekt_od_zera_podrecznik.md](docs/nauka_projektu/01_projekt_od_zera_podrecznik.md) - duży podręcznik do nauczenia się projektu.
