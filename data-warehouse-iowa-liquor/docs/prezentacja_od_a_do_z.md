# Prezentacja projektu od A do Z

## 1. Temat i cel

Projekt to hurtownia danych dla publicznego zbioru Iowa Liquor Sales. Analizujemy sprzedaż detaliczną i dystrybucję: czas, sklepy, geografię, kategorie, vendorów, produkty, opakowania, wolumen i marżę.

Najważniejsze zdanie:

```text
Projekt nie analizuje konsumpcji, tylko wyniki sprzedaży i dystrybucji w sieci detalicznej.
```

## 2. Dane

Dane są realne i niegenerowane.

- Źródło: publiczny zbiór Iowa Liquor Sales.
- Warstwa raw: pliki CSV w `data/raw`.
- Demo ETL może użyć lokalnego cache realnych plików raw, jeśli publiczny endpoint API jest niedostępny.

Co powiedzieć:

```text
Dane nie są generowane. ETL pobiera dane przez API albo, przy niedostępności endpointu, filtruje lokalny cache realnych plików raw.
```

## 3. Architektura

Przepływ:

```text
Iowa Liquor Sales -> Airflow ETL -> raw CSV -> SQL Server staging -> SQL Server DW -> widoki sem -> Streamlit
```

Warstwy:

- ETL / orkiestracja: Apache Airflow.
- Hurtownia: SQL Server.
- Warstwa semantyczna: widoki SQL w schemacie `sem`.
- Raportowanie: Streamlit + Plotly.

## 4. Pytania biznesowe

Projekt ma 12 pytań biznesowych, czyli mieści się w wymaganym zakresie 7-12.

Najkrócej:

```text
Pytania pokrywają czas, sklepy, geografię, kategorie, vendorów, produkty, marżę, weekendy i opakowania.
```

Najważniejsze pliki:

- `docs/business_requirements.md`
- `docs/warstwa_semantyczna.md`

## 5. Model wielowymiarowy

Model to schemat gwiazdy.

Tabela faktów:

- `dw.fact_sales`

Wymiary:

- `dw.dim_date`
- `dw.dim_store`
- `dw.dim_product`
- `dw.dim_category`
- `dw.dim_vendor`
- `dw.dim_packaging`

Ziarno faktu:

```text
Jeden rekord faktu to jedna linia sprzedaży produktu w sklepie, w konkretnym dniu i na konkretnej fakturze.
```

Ważne przy obronie:

- Geografia jest w `dim_store`, bo lokalizacja jest cechą sklepu.
- `state_bottle_cost` i `state_bottle_retail` są cenami jednostkowymi, więc nie sumujemy ich bezpośrednio.
- `margin_amount` jest liczona jako różnica ceny detalicznej i kosztu, pomnożona przez liczbę butelek.

## 6. ETL

ETL robi:

1. Ekstrakcję danych.
2. Zapis raw CSV.
3. Tworzenie obiektów SQL.
4. Ładowanie staging.
5. Ładowanie wymiarów.
6. Ładowanie tabeli faktów.
7. Tworzenie widoków semantycznych.
8. Quality checks.

Komenda demo:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Co powiedzieć:

```text
Na prezentacji uruchamiam szybki jednodniowy zakres, żeby pokazać proces na żywo. Projekt jest przygotowany na szerszy zakres danych, ale pełny rok jest cięższy do demo.
```

## 7. Kontrola jakości

Quality checks sprawdzają między innymi:

- czy staging ma dane,
- czy fakt ma dane,
- czy liczba rekordów kwalifikujących się do faktu zgadza się z faktem,
- czy nie ma pustych kluczy obcych,
- czy nie ma duplikatów technicznych,
- czy fakt łączy się z wymiarami,
- czy sprzedaż w staging i fakcie się zgadza.

Ważne:

```text
Ujemne korekty w raw są realnymi rekordami źródłowymi. Pokazujemy je jako informacyjną metrykę, ale nie ładujemy ich do faktu sprzedaży.
```

## 8. Warstwa semantyczna

Warstwa semantyczna to widoki `sem.*`.

Przykłady:

- `sem.vw_sales_overview`
- `sem.vw_sales_by_month`
- `sem.vw_sales_by_category`
- `sem.vw_sales_by_store`
- `sem.vw_margin_analysis`
- `sem.vw_kpi_summary`
- `sem.vw_etl_status`

Co powiedzieć:

```text
Dashboard nie odpytuje bezpośrednio tabel faktów i wymiarów. Korzysta z warstwy semantycznej, czyli widoków SQL w schemacie sem.
```

## 9. Raportowanie

Dashboard Streamlit jest po polsku.

Zakładki:

- Przegląd zarządczy
- Produkty i kategorie
- Geografia
- Wyniki sklepów

W dashboardzie są:

- KPI,
- filtry,
- wykresy liniowe,
- wykresy słupkowe,
- wykresy kołowe,
- mapa,
- heatmapa,
- tabele,
- eksport CSV.

## 10. Co zostaje po angielsku

Celowo zostają po angielsku:

- nazwy technologii: Docker, Airflow, SQL Server, Streamlit, Plotly,
- nazwy schematów i widoków SQL: `stg`, `dw`, `sem`, `sem.vw_sales_overview`,
- nazwy kolumn technicznych: `sale_dollars`, `margin_amount`, `invoice_number`,
- nazwa zbioru danych: Iowa Liquor Sales,
- słowa domenowe ze źródła: vendor, county.

Po polsku są:

- interfejs dashboardu,
- zakładki dashboardu,
- filtry,
- KPI,
- tytuły wykresów,
- komunikaty,
- najważniejsze dokumenty opisowe i notatki do prezentacji.

## 11. Kolejność pokazu na żywo

1. Pokazać `docker compose ps`.
2. Otworzyć Airflow: `http://localhost:8080`.
3. Pokazać DAG `iowa_liquor_etl`.
4. Uruchomić szybki ETL albo pokazać ostatnie logi.
5. Pokazać SQL Server: schematy `stg`, `dw`, `sem`.
6. Pokazać model gwiazdy.
7. Otworzyć Streamlit: `http://localhost:8501`.
8. Przejść przez 4 zakładki.
9. Wskazać, które pytania biznesowe są pokryte przez raporty.
10. Zakończyć quality checks i wnioskiem, że projekt spełnia wymagania.

## 12. Jednozdaniowe podsumowanie

```text
Projekt spełnia wymagania, bo ma realne dane, 12 pytań biznesowych, schemat gwiazdy, działający ETL w Airflow, hurtownię w SQL Server, warstwę semantyczną w widokach SQL i polski dashboard Streamlit z wykresami odpowiadającymi na pytania biznesowe.
```
