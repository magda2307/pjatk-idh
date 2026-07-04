# Scenariusz obrony projektu od A do Z

Ten plik jest gotowym scenariuszem mowienia na prezentacji. Mozna isc punkt po punkcie i pokazywac projekt w tej samej kolejnosc.

## 0. Jednozdaniowy start

```text
Projekt przedstawia hurtownie danych dla publicznego zbioru Iowa Liquor Sales. Celem jest analiza sprzedazy detalicznej i dystrybucji wedlug czasu, sklepow, geografii, kategorii, vendorow, produktow i opakowan.
```

Wazne dopowiedzenie:

```text
Nie analizujemy konsumpcji alkoholu. Analizujemy sprzedaz, wolumen, marze, efektywnosc sklepow i strukture dystrybucji.
```

## 1. Problem biznesowy

Co mowic:

```text
Organizacja chce wiedziec, gdzie i kiedy sprzedaz jest najwyzsza, ktore kategorie i produkty generuja najwiekszy przychod, ktorzy vendorzy maja najwiekszy udzial, ktore sklepy i regiony sa najmocniejsze oraz gdzie wolumen jest wysoki, ale wartosc na litr jest nizsza.
```

Dlaczego to ma sens biznesowo:

- pozwala porownywac sklepy i regiony,
- pomaga ocenic kategorie i vendorow,
- pokazuje trendy w czasie,
- pokazuje marze, nie tylko przychod,
- daje podstawe do decyzji asortymentowych i dystrybucyjnych.

## 2. Dane zrodlowe

Co pokazac:

- folder `data/raw`,
- pliki `iowa_liquor_sales_2023_part_000.csv` itd.,
- `data/processed/extract_manifest.json`.

Co mowic:

```text
Dane sa realne i niegenerowane. Pochodza z publicznego zbioru Iowa Liquor Sales. ETL ma ekstraktor API, ale na potrzeby stabilnego demo potrafi tez uzyc lokalnego cache realnych plikow raw, jezeli publiczny endpoint jest niedostepny.
```

Jak odpowiedziec, jesli ktos pyta "czy fallback to generowanie danych?":

```text
Nie. Fallback nie generuje nowych danych. Bierze realne rekordy z lokalnych plikow raw i filtruje je do zakresu demo.
```

## 3. Architektura projektu

Glowny przeplyw:

```text
Iowa Liquor Sales
-> Airflow ETL
-> raw CSV
-> SQL Server staging
-> SQL Server DW star schema
-> SQL semantic views
-> Streamlit dashboard
```

Co mowic:

```text
Architektura jest klasyczna dla hurtowni danych: mamy warstwe surowa, staging, model wymiarowy, warstwe semantyczna i raportowanie. Orkiestracja jest w Airflow, baza hurtowni w SQL Server, raportowanie w Streamlit.
```

## 4. Bronze / Silver / Gold

Prowadzaca moze pytac o Bronze/Silver/Gold. W tym projekcie da sie to wyjasnic tak:

### Bronze

Bronze to najblizsza zrodlu warstwa surowa.

W projekcie:

- `data/raw/*.csv`,
- oryginalne pliki z danych Iowa Liquor Sales,
- minimalna ingerencja,
- zachowanie danych do ponownego ladowania.

Co mowic:

```text
Bronze to raw CSV files. To kopia realnych danych zrodlowych, ktora pozwala powtorzyc ETL bez ponownego pobierania wszystkiego z internetu.
```

### Silver

Silver to warstwa technicznie oczyszczona i ujednolicona.

W projekcie:

- `stg.iowa_liquor_sales_raw`,
- ujednolicone nazwy kolumn,
- konwersje typow,
- parsowanie dat, liczb i lokalizacji,
- staging przed modelem wymiarowym.

Co mowic:

```text
Silver to staging w SQL Server. Tu dane sa juz w bazie, maja techniczne typy i sa gotowe do transformacji do wymiarow i faktu.
```

### Gold

Gold to warstwa biznesowa gotowa do analizy.

W projekcie:

- `dw.fact_sales`,
- `dw.dim_date`,
- `dw.dim_store`,
- `dw.dim_product`,
- `dw.dim_category`,
- `dw.dim_vendor`,
- `dw.dim_packaging`,
- widoki `sem.*`,
- dashboard Streamlit.

Co mowic:

```text
Gold to model gwiazdy i widoki semantyczne. To z tej warstwy korzysta raportowanie.
```

Najkrotsza odpowiedz:

```text
Bronze to raw CSV, Silver to staging SQL, Gold to schemat gwiazdy plus widoki semantyczne i dashboard.
```

## 5. Pytania biznesowe

Co pokazac:

- `docs/business_requirements.md`.

Co mowic:

```text
Projekt ma 12 pytan biznesowych, czyli miesci sie w wymaganym zakresie 7-12. Pytania pokrywaja czas, geografie, sklepy, produkty, kategorie, vendorow, marze, weekendy i opakowania.
```

Przykladowe pytania:

- Jak zmieniala sie sprzedaz wedlug miesiaca, kwartalu i roku?
- Ktore kategorie i produkty generuja najwyzsza sprzedaz i marze?
- Ktore sklepy i regiony sa najmocniejsze?
- Ktore regiony maja wysoki wolumen, ale nizsza sprzedaz na litr?
- Jak weekendy roznia sie od dni roboczych?

## 6. Model wielowymiarowy

Co pokazac:

- `docs/dimensional_model.md`,
- `sql/03_create_dw_tables.sql`,
- w bazie: schemat `dw`.

Co mowic:

```text
Model jest schematem gwiazdy. W centrum jest tabela faktow `dw.fact_sales`, a dookola sa wymiary: data, sklep, produkt, kategoria, vendor i opakowanie.
```

Tabela faktow:

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
Jeden rekord w `dw.fact_sales` oznacza jedna linie sprzedazy produktu w konkretnym sklepie, w konkretnym dniu i na konkretnej fakturze.
```

Dlaczego taki model:

- czas jest osobnym wymiarem, bo analizujemy trendy,
- sklep zawiera miasto/county, bo geografia jest cecha sklepu,
- produkt i kategoria sa rozdzielone, bo mozna analizowac szczegol i agregat,
- vendor jest osobnym wymiarem, bo pytamy o udzial dostawcow,
- opakowanie jest osobnym wymiarem, bo pytamy o pojemnosci i grupy opakowan.

Wazna odpowiedz o geografii:

```text
Nie robilismy osobnej `dim_geography`, bo w tym projekcie lokalizacja jest atrybutem sklepu. To ogranicza duplikacje i wystarcza do pytan biznesowych.
```

## 7. Miary

Najwazniejsze miary w fakcie:

- `sale_dollars` - wartosc sprzedazy,
- `bottles_sold` - liczba butelek,
- `volume_sold_liters` - wolumen,
- `margin_amount` - marza,
- `sales_line_count` - liczba linii sprzedazy.

Wazne:

```text
`state_bottle_cost` i `state_bottle_retail` sa miarami jednostkowymi, czyli nieaddytywnymi. Nie powinno sie ich po prostu sumowac. Do marzy uzywamy wyliczonej miary `margin_amount`.
```

## 8. ETL

Co pokazac:

- `dags/iowa_liquor_etl_dag.py`,
- `src/run_initial_etl.py`,
- logi z uruchomienia,
- Airflow UI.

Kroki ETL:

1. Extract danych.
2. Zapis raw CSV.
3. Utworzenie schematow i tabel SQL.
4. Ladowanie staging.
5. Ladowanie wymiarow.
6. Ladowanie faktu.
7. Utworzenie widokow semantycznych.
8. Quality checks.

Komenda live:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Co powiedziec o zakresie demo:

```text
Na zywo uruchamiam jeden dzien, bo pelny rok jest ciezki czasowo na prezentacje. To jest zakres demonstracyjny. Mechanizm ETL jest ten sam.
```

## 9. Quality checks

Co pokazac:

- `sql/05_quality_checks.sql`,
- output live ETL.

Co sprawdzamy:

- staging ma dane,
- fact ma dane,
- eligible staging rows = fact rows,
- brak null foreign keys,
- brak ujemnych miar w fakcie,
- brak duplikatow kluczy biznesowych w wymiarach,
- fakt laczy sie z wymiarami,
- sprzedaz w staging i fakcie sie zgadza.

Aktualny wynik live demo:

```text
staging rows = 10634
eligible staging rows = 10624
fact rows = 10624
eligible staging fact row count difference = 0
null foreign keys = 0
fact dimension join failures = 0
sales reconciliation difference = 0.0000
```

Co powiedziec o 10 ujemnych rekordach:

```text
W raw sa realne ujemne korekty zrodlowe. Pokazujemy je jako informacyjna kontrole `raw_negative_measure_rows_excluded_from_fact`, ale nie ladujemy ich do faktu sprzedazy, zeby raport nie mial ujemnej sprzedazy.
```

## 10. Warstwa semantyczna

Co pokazac:

- `sql/04_create_semantic_views.sql`,
- `docs/warstwa_semantyczna.md`,
- w dashboardzie sekcje "Pokrycie warstwy semantycznej".

Co mowic:

```text
Warstwa semantyczna to widoki SQL w schemacie `sem`. Dashboard korzysta z widokow `sem`, a nie bezposrednio z tabel `dw`.
```

Najwazniejsze widoki:

- `sem.vw_sales_overview`,
- `sem.vw_sales_by_month`,
- `sem.vw_sales_by_category`,
- `sem.vw_sales_by_store`,
- `sem.vw_sales_by_vendor`,
- `sem.vw_margin_analysis`,
- `sem.vw_volume_vs_revenue`,
- `sem.vw_kpi_summary`,
- `sem.vw_etl_status`.

Dlaczego warstwa semantyczna:

- upraszcza raportowanie,
- ukrywa zlozonosc modelu,
- daje biznesowe agregacje,
- zapewnia jedno miejsce definicji KPI.

## 11. Dashboard Streamlit

Co pokazac:

- `http://localhost:8501`.

Zakladki:

1. Przeglad zarzadczy
2. Produkty i kategorie
3. Geografia
4. Wyniki sklepow

Co mowic:

```text
Dashboard jest po polsku i odpowiada na pytania biznesowe przez KPI, wykresy, mapy, tabele i eksport CSV.
```

Co pokazac w kazdej zakladce:

### Przeglad zarzadczy

- KPI globalne,
- sprzedaz w czasie,
- kwartal/rok,
- weekend vs dzien roboczy.

Pokrywa pytania:

- Q1,
- Q11.

### Produkty i kategorie

- top kategorie,
- top produkty,
- marza,
- vendorzy,
- opakowania.

Pokrywa pytania:

- Q2,
- Q5,
- Q6,
- Q7,
- Q8,
- Q12.

### Geografia

- county,
- miasta,
- mapa,
- wolumen vs sprzedaz,
- Q9: wysoki wolumen i nizsza sprzedaz na litr.

Pokrywa pytania:

- Q4,
- Q9.

### Wyniki sklepow

- top sklepy,
- sklepy o wysokim wolumenie i nizszej sprzedazy,
- srednia sprzedaz na sklep wedlug county i miesiaca.

Pokrywa pytania:

- Q3,
- Q10.

## 12. Co jest po polsku, a co po angielsku

Po polsku:

- interfejs dashboardu,
- zakladki,
- filtry,
- KPI,
- tytuly wykresow,
- komunikaty,
- glowne notatki do prezentacji.

Celowo po angielsku:

- nazwy technologii: Docker, Airflow, SQL Server, Streamlit, Plotly,
- nazwy obiektow technicznych: `dw.fact_sales`, `sem.vw_sales_overview`,
- nazwy kolumn: `sale_dollars`, `margin_amount`,
- nazwa zbioru: Iowa Liquor Sales,
- slowa domenowe ze zrodla: vendor, county.

## 13. Kolejnosc live demo

### Krok 1 - terminal

```powershell
cd D:\pjatk-idh\data-warehouse-iowa-liquor
docker compose up -d sqlserver airflow streamlit
docker compose ps
```

Co mowic:

```text
Tu widac trzy uslugi: SQL Server jako hurtownia, Airflow jako orkiestrator ETL i Streamlit jako raportowanie.
```

### Krok 2 - Airflow

Otworzyc:

```text
http://localhost:8080
```

Pokazac DAG:

```text
iowa_liquor_etl
```

Co mowic:

```text
Ten DAG reprezentuje caly proces ETL: extract, create SQL objects, load staging, load dimensions, load fact, semantic views, quality checks.
```

### Krok 3 - live ETL

Uruchomic:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

Co pokazac w logach:

- staging rows,
- fact rows,
- quality checks,
- `Initial ETL finished`.

### Krok 4 - Streamlit

Otworzyc:

```text
http://localhost:8501
```

Pokazac:

- status danych,
- warstwe semantyczna,
- KPI,
- 4 zakladki.

### Krok 5 - podsumowanie

```text
Projekt spelnia wymagania: realne dane, 12 pytan biznesowych, schemat gwiazdy, dzialajacy ETL, SQL Server jako hurtownia, widoki semantyczne i polski dashboard z wykresami.
```

## 14. Najwazniejsze zdania do zapamietania

```text
Ziarno faktu to jedna linia sprzedazy produktu w sklepie, w dniu i na fakturze.
```

```text
Bronze to raw CSV, Silver to staging SQL, Gold to model gwiazdy plus widoki semantyczne.
```

```text
Dashboard korzysta z warstwy semantycznej `sem`, a nie bezposrednio z tabel faktow i wymiarow.
```

```text
Ujemne korekty z raw sa transparentnie pokazywane w quality checks, ale nie trafiaja do faktu sprzedazy.
```

```text
Zakres jednodniowy jest zakresem demo, a nie ograniczeniem architektury.
```

