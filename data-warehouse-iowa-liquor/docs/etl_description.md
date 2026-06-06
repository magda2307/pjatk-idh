# Opis ETL

## Orkiestracja

ETL jest orkiestracyjny przez Apache Airflow. DAG nazywa sie:

```text
iowa_liquor_etl
```

DAG jest uruchamiany recznie w Airflow UI, co spelnia wymaganie prezentacji procesu ETL na zywo.

## ETL w skrocie

Proces ETL w projekcie przebiega wedlug schematu:

```text
Ekstrakcja
-> Staging
-> Transformacja do modelu wymiarowego
-> Ladowanie wymiarow
-> Ladowanie faktu
-> Tworzenie warstwy semantycznej
-> Kontrola jakosci
```

## Mapowanie na Bronze / Silver / Gold

Proces mozna tez opisac w bardziej nowoczesnym jezyku warstw danych:

### Bronze

- surowe pliki `CSV` pobrane z API
- lokalizacja: `data/raw`
- cel: zachowanie surowego zrzutu danych zrodlowych

### Silver

- tabela `stg.iowa_liquor_sales_raw`
- cel: czyszczenie, standaryzacja i przygotowanie danych
- logika: typy, tekst, mapowanie kolumn, parsowanie lokalizacji

### Gold

- model wymiarowy w `dw`
- warstwa semantyczna w `sem`
- cel: analiza biznesowa i raportowanie

W tym projekcie warstwa Gold ma dwa poziomy:

1. `dw.*` - hurtownia danych w schemacie gwiazdy
2. `sem.*` - gotowe widoki raportowe i KPI

## Kroki DAG

1. `extract_iowa_liquor_sales`
   - pobiera dane z `https://data.iowa.gov/resource/m3tr-qhgy.csv`,
   - filtruje zakres dat,
   - uzywa paginacji `$limit` i `$offset`,
   - zapisuje pliki CSV w `data/raw`.

2. `create_sql_objects`
   - tworzy baze `IowaLiquorDW`,
   - tworzy schematy `stg`, `dw`, `sem`,
   - tworzy tabele staging, wymiary i fakt.

3. `load_staging`
   - czysci tabele `stg.iowa_liquor_sales_raw`,
   - normalizuje nazwy kolumn do `snake_case`,
   - wykonuje podstawowe konwersje typow,
   - laduje pliki CSV do SQL Server.

4. `load_dimensions`
   - odswieza `dw.dim_date`,
   - odswieza `dw.dim_store`,
   - odswieza `dw.dim_product`,
   - odswieza `dw.dim_category`,
   - odswieza `dw.dim_vendor`,
   - odswieza `dw.dim_packaging`.

5. `load_fact_sales`
   - laduje `dw.fact_sales`,
   - laczy rekordy staging z wymiarami,
   - wylicza `margin_amount`,
   - ustawia `sales_line_count = 1`,
   - zachowuje numer faktury jako wymiar zdegenerowany,
   - odrzuca z faktu rekordy z ujemnymi miarami, ale zachowuje je w stagingu.

6. `create_semantic_views`
   - tworzy lub aktualizuje widoki w schemacie `sem`.

7. `run_quality_checks`
   - drukuje w logach Airflow liczbe rekordow staging i faktu,
   - sprawdza puste klucze obce,
   - sprawdza ujemne wartosci miar w fakcie,
   - sprawdza duplikaty kluczy naturalnych,
   - sprawdza join fakt-wymiary,
   - porownuje sume sprzedazy staging vs fakt dla rekordow kwalifikowanych do faktu.

## Ekstrakcja

### Co pobieramy

Pobieramy rekordy transakcyjne Iowa Liquor Sales dla zadanego zakresu dat.

### Skad pobieramy

Zrodlo to publiczne API Socrata:

```text
https://data.iowa.gov/resource/m3tr-qhgy.csv
```

Typ zrodla:

- API CSV
- dane publiczne online
- dane rzeczywiste, niegenerowane

### Jakie pola sa potrzebne

W projekcie potrzebne sa przede wszystkim pola zrodlowe odpowiadajace:

- numerowi linii faktury,
- dacie,
- sklepowi,
- adresowi i geolokalizacji sklepu,
- kategorii,
- vendorowi,
- produktowi,
- opakowaniu,
- cenie kosztowej i detalicznej,
- liczbie butelek,
- wartosci sprzedazy,
- wolumenowi.

Mapowane pola obejmuja m.in.:

```text
invoice_line_no -> invoice_and_item_number
date -> date
store -> store_number
name -> store_name
address -> address
city -> city
zipcode -> zip_code
store_location -> store_location
county -> county
category -> category
category_name -> category_name
vendor_no -> vendor_number
vendor_name -> vendor_name
itemno -> item_number
im_desc -> item_description
pack -> pack
bottle_volume_ml -> bottle_volume_ml
state_bottle_cost -> state_bottle_cost
state_bottle_retail -> state_bottle_retail
sale_bottles -> bottles_sold
sale_dollars -> sale_dollars
sale_liters -> volume_sold_liters
sale_gallons -> volume_sold_gallons
```

### Kiedy rekord zrodlowy staje sie rekordem do zaladowania

Rekord zrodlowy trafia najpierw do warstwy `stg`. Dopiero po:

- normalizacji nazw kolumn,
- konwersji typow,
- wyliczeniu technicznego hasha,
- podstawowym czyszczeniu,
- sprawdzeniu reguly miar,

moze zostac wykorzystany do budowy wymiarow i faktu.

### Kiedy rekord zrodlowy staje sie faktem w hurtowni

Rekord staje sie rekordem faktu wtedy, gdy:

- ma poprawna date,
- daje sie zmapowac do wszystkich wymaganych wymiarow,
- przechodzi regule miar nieujemnych dla faktu,
- otrzyma surrogate keys przez dolaczenie do wymiarow.

## Transformacja

Transformacja obejmuje zarowno przygotowanie stagingu, jak i budowe modelu wymiarowego.

### Czyszczenie danych

Projekt wykonuje:

- usuniecie znakow `$` i przecinkow z pol liczbowych,
- standaryzacje pustych tekstow do `NULL`,
- wydzielenie wspolrzednych z pola `store_location`,
- zachowanie rekordow surowych w stagingu.

### Ujednolicanie formatow

Projekt ujednolica:

- nazwy kolumn do `snake_case`,
- daty do typu `DATE`,
- wartosci liczbowe do `DECIMAL` lub `INT`,
- etykiety czasu w `dim_date`.

### Konwersje typow

Przyklady:

- `date` -> `DATE`
- `sale_dollars` -> `DECIMAL`
- `bottles_sold` -> `DECIMAL`
- `pack` -> `INT`
- `bottle_volume_ml` -> `INT`
- `latitude`, `longitude` -> `DECIMAL`

### Obsluga nulli

Projekt:

- zamienia puste napisy na `NULL` w stagingu,
- stosuje wartosci techniczne typu `UNKNOWN` przy budowie wybranych wymiarow natural-key based,
- zachowuje nullowalne pola opisowe tam, gdzie brak wartosci nie blokuje analizy.

### Duplikaty

Projekt nie usuwa duplikatow po cichu ze stagingu.

To jest swiadoma decyzja:

- staging ma zachowac rekordy zrodlowe,
- agregacja dzieje sie w widokach semantycznych,
- wymiarowe deduplikowanie dotyczy tylko budowy rekordow wymiarow na bazie kluczy naturalnych.

### Mapowanie pol zrodlowych na docelowe

Transformacja mapuje pola zrodla na:

- staging source-like structure,
- tabele wymiarow,
- tabele faktow.

Przyklady:

- `store`, `name`, `address`, `city`, `zipcode`, `county` -> `dw.dim_store`
- `itemno`, `im_desc` -> `dw.dim_product`
- `category`, `category_name` -> `dw.dim_category`
- `vendor_no`, `vendor_name` -> `dw.dim_vendor`
- `pack`, `bottle_volume_ml` -> `dw.dim_packaging`

### Wyliczanie nowych miar

Nowe miary i pola techniczne:

- `margin_amount = (state_bottle_retail - state_bottle_cost) * bottles_sold`
- `sales_line_count = 1`
- `source_row_hash` jako techniczny hash rekordu

### Klucze techniczne

Projekt tworzy surrogate keys dla:

- `dim_store`
- `dim_product`
- `dim_category`
- `dim_vendor`
- `dim_packaging`

`dim_date` uzywa klucza inteligentnego `YYYYMMDD`.

### Budowa wymiarow i faktu

Kolejnosc:

1. `dim_date`
2. `dim_store`
3. `dim_product`
4. `dim_category`
5. `dim_vendor`
6. `dim_packaging`
7. `fact_sales`

Fakt budowany jest dopiero po uzupelnieniu wymiarow.

## Ladowanie

### Ladowanie do stagingu

Pliki raw sa ladowane do:

```text
stg.iowa_liquor_sales_raw
```

To jest warstwa przyjmowania danych zrodlowych i podstawowego czyszczenia.

### Ladowanie wymiarow

Po stagingu ladowane sa wymiary w schemacie `dw`.

### Ladowanie faktu

Po wymiarach ladowany jest `dw.fact_sales`.

To odpowiada klasycznej zasadzie:

```text
najpierw wymiary
potem fakty
```

### Ladowanie poczatkowe

Projekt implementuje ladowanie poczatkowe jako full refresh:

- staging jest czyszczony i ladowany od nowa,
- wymiary sa odswiezane,
- fakt jest odswiezany,
- widoki semantyczne sa przebudowywane.

To jest najbezpieczniejsze i najlatwiejsze do obrony w projekcie studenckim.

### Jak wygladaloby ladowanie przyrostowe

Projekt domyslnie go nie implementuje, ale mozna je opisac tak:

- ekstrakcja tylko nowych lub zmienionych dat,
- doladowanie stagingu nowymi partiami,
- identyfikacja nowych rekordow wymiarow po kluczach naturalnych,
- doladowanie nowych rekordow faktu po kluczu biznesowym lub hashu,
- zachowanie historii wedlug potrzeb biznesowych.

W obecnej wersji wybrano full refresh, bo jest prostszy, bardziej przewidywalny i lepszy do prezentacji na kursie.

## Warstwa staging

Projekt posiada realna warstwe staging:

```text
stg - dane zrodlowe / oczyszczone
dw  - fakty i wymiary
sem - widoki analityczne / raportowe
```

### Po co jest staging

Warstwa `stg` sluzy do:

- przyjecia danych zrodlowych,
- zachowania surowych lub czesciowo oczyszczonych danych,
- przygotowania danych przed ladowaniem do wymiarow i faktu,
- rozdzielenia zrodla od hurtowni docelowej.

To odpowiada dobrym praktykom ETL i wymaganiom projektu.

## Warstwa semantyczna

Warstwa `sem` jest nowoczesnym odpowiednikiem warstwy analitycznej dla raportowania.

### Co zawiera

- widoki gotowe do raportowania,
- biznesowe nazwy kolumn,
- agregacje,
- wyliczone miary,
- logike KPI,
- uproszczony model pod dashboard.

### Po co istnieje

- ukrywa techniczne szczegoly modelu `dw`,
- upraszcza dashboard Streamlit,
- centralizuje logike raportowa,
- zapewnia spojnosc wynikow.

### Przyklady widokow

- `sem.vw_sales_by_month`
- `sem.vw_sales_by_store`
- `sem.vw_sales_by_category`
- `sem.vw_sales_by_vendor`
- `sem.vw_margin_analysis`
- `sem.vw_top_products`
- `sem.vw_sales_by_geography`
- `sem.vw_volume_vs_revenue`
- `sem.vw_category_sales_over_time`
- `sem.vw_avg_sales_per_store_by_month_region`

## Raporty

Raporty wynikaja bezposrednio z pytan biznesowych.

Projekt zawiera minimum:

- sprzedaz w czasie,
- sprzedaz wedlug sklepow,
- sprzedaz wedlug produktow i kategorii,
- sprzedaz geograficzna,
- analize marzy,
- analize vendorow,
- strukture sprzedazy kategorii w czasie,
- srednia sprzedaz na sklep wedlug miesiaca i county.

Dashboard dostarcza:

- tabele i agregacje,
- filtrowanie,
- sortowanie,
- mozliwosc wyboru zakresu,
- wykresy,
- kilka perspektyw analizy.

## Tryb odswiezania

Projekt uzywa prostego pelnego odswiezania. To celowy wybor dla projektu studenckiego: latwiej pokazac i wyjasnic dzialanie ETL bez zlozonej logiki incremental load.

## Jak zobaczyc Airflow

Uruchom uslugi:

```powershell
docker compose up -d sqlserver airflow streamlit
```

Sprawdz status:

```powershell
docker compose ps
```

Otworz UI:

```text
http://localhost:8080
```

Login:

```text
username: admin
password: admin
```

## Jak uruchomic DAG

W Airflow:

1. Znajdz `iowa_liquor_etl`.
2. Unpause DAG, jesli jest paused.
3. Kliknij `Trigger DAG`.
4. Otworz `Graph` albo `Grid`.
5. Wejdz w task logs dla `extract_iowa_liquor_sales`, `load_staging`, `load_fact_sales`, `run_quality_checks`.

## Jak sprawdzic, czy uslugi zyja

To nie sa Kubernetes pods. To sa Docker containers.

Status:

```powershell
docker compose ps
```

Logi:

```powershell
docker logs iowa-liquor-airflow --tail 100
docker logs iowa-liquor-streamlit --tail 100
docker logs iowa-liquor-sqlserver --tail 100
```

## Szybki terminalowy run ETL

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```
