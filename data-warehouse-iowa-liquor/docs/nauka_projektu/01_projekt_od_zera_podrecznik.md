# Projekt od zera: podręcznik do zrozumienia i obrony

Ten dokument jest po to, żeby nauczyć Cię projektu od absolutnego początku. Nie tylko "co kliknąć", ale też:

- co zostało zbudowane,
- po co to zostało zbudowane,
- dlaczego wybrano takie rozwiązania,
- czemu nie wybrano innych rozwiązań,
- jak działa każda warstwa,
- jak uruchomić projekt live,
- jak opowiedzieć projekt prowadzącej,
- jak odpowiadać na pytania techniczne.

Najważniejsza myśl:

```text
To nie jest tylko dashboard. To jest pełny projekt hurtowni danych: od realnych danych raw, przez ETL, staging, model gwiazdy, warstwę semantyczną, aż do raportów.
```

---

## 1. Najkrótsze wyjaśnienie projektu

Projekt jest hurtownią danych dla publicznego zbioru Iowa Liquor Sales. Dane opisują sprzedaż detaliczną w stanie Iowa: daty sprzedaży, sklepy, miasta, county, produkty, kategorie, vendorów, opakowania, liczbę butelek, wolumen, ceny i wartość sprzedaży.

Celem projektu jest analiza sprzedaży i dystrybucji, a nie analiza konsumpcji alkoholu.

To rozróżnienie jest bardzo ważne. Na obronie nie mów:

```text
Analizujemy, gdzie ludzie piją więcej.
```

Mów:

```text
Analizujemy sprzedaż detaliczną i dystrybucję: przychody, wolumen, marżę, sklepy, regiony, produkty i vendorów.
```

Wersja do powiedzenia prowadzącej:

```text
Projekt pokazuje pełną ścieżkę od realnych danych Iowa Liquor Sales, przez ETL w Airflow i hurtownię w SQL Server, po warstwę semantyczną i dashboard Streamlit odpowiadający na 12 pytań biznesowych.
```

---

## 2. Co było wymagane w projekcie

Wymagania prowadzącej były następujące:

1. Zespół 2-4 osoby.
2. Realne dane, niegenerowane.
3. 7-12 pytań biznesowych.
4. Model wielowymiarowy.
5. Postawiona baza hurtowni.
6. ETL lub narzędzie integracyjne.
7. Warstwa semantyczna.
8. Raporty z wykresami.

Projekt odpowiada na te wymagania tak:

| Wymaganie | Jak projekt spełnia wymaganie |
|---|---|
| Zespół 2-4 osoby | To formalnie trzeba uzupełnić prawdziwymi nazwiskami zespołu. |
| Dane niegenerowane | Dane pochodzą z publicznego zbioru Iowa Liquor Sales i są zapisane jako realne CSV. |
| 7-12 pytań biznesowych | Projekt ma 12 pytań biznesowych w `docs/business_requirements.md`. |
| Model wielowymiarowy | Jest schemat gwiazdy: `dw.fact_sales` + 6 wymiarów. |
| Hurtownia danych | Hurtownia działa w SQL Server. |
| ETL / integracja | ETL jest uruchamiany przez Airflow oraz kod Python/SQL. |
| Warstwa semantyczna | Warstwa semantyczna to widoki SQL w schemacie `sem`. |
| Raporty z wykresami | Dashboard Streamlit pokazuje KPI, wykresy, mapy i tabele. |

Jak to powiedzieć:

```text
Projekt spełnia pełną ścieżkę wymagań: od danych, przez model i ETL, po semantykę oraz raportowanie.
```

Jedyny element, którego nie da się technicznie "wygenerować" w repozytorium, to prawdziwy skład zespołu. To trzeba po prostu powiedzieć albo wpisać w dokumentacji przed oddaniem.

---

## 3. Problem biznesowy: po co w ogóle ten projekt

Hurtownia danych nie powinna zaczynać się od tabel. Powinna zaczynać się od pytań biznesowych.

Tutaj problem biznesowy można opisać tak:

```text
Organizacja chce analizować sprzedaż detaliczną według czasu, sklepów, regionów, kategorii, produktów, vendorów i opakowań, żeby lepiej rozumieć strukturę sprzedaży, wolumen i marżę.
```

Czyli biznes chce wiedzieć:

- kiedy sprzedaż jest najwyższa,
- które kategorie generują największy przychód,
- które produkty sprzedają się najlepiej,
- którzy vendorzy mają największy udział,
- które sklepy są najmocniejsze,
- które miasta i county mają najwyższy wolumen,
- gdzie wolumen jest wysoki, ale sprzedaż na litr jest niższa,
- jak weekendy różnią się od dni roboczych,
- które opakowania i pojemności dają najlepsze wyniki.

To są pytania, które naturalnie prowadzą do hurtowni danych. Dlaczego? Bo trzeba analizować te same fakty sprzedażowe w różnych przekrojach:

- po czasie,
- po sklepie,
- po geografii,
- po produkcie,
- po kategorii,
- po vendorze,
- po opakowaniu.

To właśnie są wymiary analizy.

---

## 4. Jak wyglądała praca nad projektem

Praca nad takim projektem logicznie idzie warstwami. Nie zaczyna się od Streamlita. Streamlit jest końcem, nie początkiem.

Kolejność pracy wyglądała tak:

1. Wybranie realnego źródła danych.
2. Zrozumienie, co oznaczają kolumny w danych.
3. Ustalenie pytań biznesowych.
4. Zaprojektowanie modelu wielowymiarowego.
5. Zaprojektowanie warstw danych: raw, staging, warehouse, semantyka.
6. Przygotowanie SQL Server jako hurtowni.
7. Przygotowanie skryptów SQL dla schematów i tabel.
8. Przygotowanie ekstrakcji danych.
9. Przygotowanie ładowania staging.
10. Przygotowanie transformacji do wymiarów i faktu.
11. Przygotowanie quality checks.
12. Przygotowanie widoków semantycznych.
13. Przygotowanie dashboardu.
14. Przetestowanie live demo.
15. Dopisanie dokumentacji i narracji do obrony.

Dlaczego taka kolejność?

Bo dashboard bez modelu danych byłby tylko wizualizacją CSV. Projekt hurtowniany musi pokazać, że dane przeszły przez uporządkowaną architekturę:

```text
źródło -> integracja -> staging -> model -> semantyka -> raport
```

---

## 5. Dane źródłowe

Źródłem jest publiczny zbiór Iowa Liquor Sales. Dane są realne i niegenerowane.

W projekcie raw dane są w:

```text
data/raw
```

Aktualny manifest ekstrakcji jest w:

```text
data/processed/extract_manifest.json
```

Manifest mówi między innymi:

- jaki zakres dat został użyty,
- ile plików weszło do ekstraktu,
- ile wierszy zostało przetworzonych,
- które pliki były źródłem dla runu.

Na live demo aktualny zakres może być jednodniowy, np.:

```text
2023-01-03 -> 2023-01-03
```

To nie oznacza, że projekt jest tylko jednodniowy. To oznacza, że do prezentacji używa się krótszego zakresu, żeby ETL przeszedł szybko i stabilnie.

Jak to tłumaczyć:

```text
Pełny zakres danych może być większy, ale na prezentacji uruchamiamy jeden dzień, żeby pokazać cały mechanizm ETL live bez czekania na długi pełnoroczny run.
```

---

## 6. API, raw CSV i fallback cache

Projekt ma ekstraktor API. Próbuje pobrać dane z publicznego endpointu Socrata.

Ale publiczne endpointy mogą:

- zmienić adres,
- zwrócić 404,
- działać wolno,
- mieć limit,
- być chwilowo niedostępne.

Dlatego projekt ma fallback cache.

To znaczy:

1. ETL najpierw próbuje pobrać dane z API.
2. Jeśli API działa, zapisuje dane do raw CSV.
3. Jeśli API zwróci błąd, ETL nie generuje sztucznych danych.
4. ETL używa lokalnych, realnych plików raw z wcześniejszego pobrania.
5. Filtruje je do zakresu demo.
6. Zapisuje roboczy ekstrakt do `data/processed/fallback_raw`.

Najważniejsze zdanie:

```text
Fallback cache nie generuje danych. On używa realnych rekordów zapisanych wcześniej w raw CSV.
```

Jeśli prowadząca zapyta, czy to łamie wymaganie "dane nie mogą być generowane", odpowiedź brzmi:

```text
Nie, bo fallback nie tworzy nowych rekordów. To nadal są realne dane źródłowe Iowa Liquor Sales, tylko odczytane z lokalnego cache zamiast pobrane w tej sekundzie z API.
```

Dlaczego to dobra decyzja?

Bo obrona projektu nie powinna zależeć od tego, czy zewnętrzny portal działa dokładnie w czasie prezentacji. Projekt pokazuje architekturę, ETL i hurtownię. Cache zapewnia powtarzalność demo.

---

## 7. Architektura projektu

Cały przepływ wygląda tak:

```text
Iowa Liquor Sales
-> Apache Airflow
-> raw CSV files
-> SQL Server staging
-> SQL Server dimensional warehouse
-> SQL semantic views
-> Streamlit dashboard
```

Rola każdej części:

| Element | Rola |
|---|---|
| Iowa Liquor Sales | Źródło danych. |
| Airflow | Orkiestracja ETL. |
| Raw CSV | Kopia danych źródłowych. |
| SQL Server `stg` | Staging, czyli dane technicznie przygotowane. |
| SQL Server `dw` | Model wymiarowy: fakt i wymiary. |
| SQL Server `sem` | Warstwa semantyczna, czyli widoki raportowe. |
| Streamlit | Dashboard i raportowanie. |

Jak powiedzieć to prosto:

```text
Dane najpierw trafiają do warstwy raw, potem do stagingu, potem do schematu gwiazdy, następnie do widoków semantycznych, a na końcu są pokazywane w dashboardzie.
```

Dlaczego nie prościej, np. CSV prosto do Streamlita?

Bo wtedy nie byłoby hurtowni danych. Byłby tylko dashboard na pliku. Wymagania projektu mówią o ETL, hurtowni, modelu wielowymiarowym i warstwie semantycznej. Bez tych warstw projekt nie spełniałby założeń.

---

## 8. Bronze / Silver / Gold

Prowadząca może użyć pojęć Bronze, Silver i Gold. To są popularne nazwy warstw danych.

W tym projekcie odpowiadają im:

| Warstwa | Gdzie jest | Co zawiera | Po co istnieje |
|---|---|---|---|
| Bronze | `data/raw` oraz awaryjnie `data/processed/fallback_raw` | surowe CSV | zachowanie kopii danych źródłowych |
| Silver | `stg.iowa_liquor_sales_raw` | dane oczyszczone technicznie | przygotowanie do modelu wymiarowego |
| Gold | `dw.*`, `sem.*`, Streamlit | model gwiazdy, semantyka, raporty | analiza biznesowa |

### Bronze

Bronze to warstwa najbliższa źródłu.

W projekcie:

```text
data/raw/*.csv
```

Bronze nie jest jeszcze wygodny do raportowania. To kopia danych źródłowych. Jej celem jest:

- mieć dowód, skąd dane przyszły,
- móc powtórzyć ETL,
- móc debugować błędy,
- nie zależeć za każdym razem od API.

Co powiedzieć:

```text
Bronze to surowe pliki CSV. To jeszcze nie jest model analityczny, tylko bezpieczna kopia źródła.
```

### Silver

Silver to staging.

W projekcie:

```text
stg.iowa_liquor_sales_raw
```

Tutaj dane są już w SQL Server i są technicznie uporządkowane:

- kolumny mają ujednolicone nazwy,
- wartości liczbowe są konwertowane,
- daty są parsowane,
- puste teksty są zamieniane na `NULL`,
- lokalizacje mogą być parsowane,
- tworzony jest `source_row_hash`.

Co powiedzieć:

```text
Silver to staging w SQL Server. Dane są nadal blisko źródła, ale są już technicznie przygotowane do transformacji.
```

### Gold

Gold to warstwa biznesowa.

W projekcie:

```text
dw.*
sem.*
Streamlit dashboard
```

Gold zawiera:

- tabelę faktów,
- wymiary,
- widoki semantyczne,
- KPI,
- agregacje,
- dashboard.

Co powiedzieć:

```text
Gold to model gwiazdy i widoki semantyczne, czyli warstwa gotowa do analizy biznesowej.
```

Najkrótsza odpowiedź:

```text
Bronze to raw CSV, Silver to staging SQL, Gold to schemat gwiazdy plus widoki semantyczne i dashboard.
```

---

## 9. ETL krok po kroku

ETL jest uruchamiany przez Airflow. DAG nazywa się:

```text
iowa_liquor_etl
```

Kroki są liniowe:

```text
extract_iowa_liquor_sales
-> create_sql_objects
-> load_staging
-> load_dimensions
-> load_fact_sales
-> create_semantic_views
-> run_quality_checks
```

### Krok 1: Extract

Ekstraktor pobiera dane z API Socrata albo korzysta z fallback cache.

Parametry zakresu:

```text
IOWA_START_DATE
IOWA_END_DATE
SOCRATA_LIMIT
```

Na demo:

```text
2023-01-03 -> 2023-01-03
```

Po co ten krok?

Żeby oddzielić pobieranie danych od dalszej transformacji. Najpierw chcemy mieć pliki raw.

### Krok 2: Create SQL objects

Tworzone są schematy i tabele:

- `stg`,
- `dw`,
- `sem`.

Uruchamiane są skrypty SQL z folderu:

```text
sql
```

Po co?

Żeby baza miała strukturę, do której można ładować dane.

### Krok 3: Load staging

Pliki CSV trafiają do:

```text
stg.iowa_liquor_sales_raw
```

W tym kroku dane są technicznie czyszczone:

- normalizacja nazw kolumn,
- konwersja dat,
- konwersja liczb,
- obsługa pustych wartości,
- hash rekordu źródłowego.

Po co staging?

Bo nie chcemy ładować hurtowni bezpośrednio ze źródła. Źródło może mieć brudne typy, dziwne nazwy kolumn, puste wartości albo korekty.

### Krok 4: Load dimensions

Tworzone/odświeżane są wymiary:

- `dim_date`,
- `dim_store`,
- `dim_product`,
- `dim_category`,
- `dim_vendor`,
- `dim_packaging`.

Wymiary są deduplikowane po kluczach naturalnych, np. numerze sklepu albo numerze produktu.

### Krok 5: Load fact

Ładowana jest:

```text
dw.fact_sales
```

Rekord staging trafia do faktu, jeśli da się go poprawnie połączyć z wymiarami.

W fakcie jest między innymi:

- `date_key`,
- `store_key`,
- `product_key`,
- `category_key`,
- `vendor_key`,
- `packaging_key`,
- `invoice_number`,
- `sale_dollars`,
- `bottles_sold`,
- `volume_sold_liters`,
- `margin_amount`.

Marża:

```text
margin_amount = (state_bottle_retail - state_bottle_cost) * bottles_sold
```

### Krok 6: Create semantic views

Tworzone są widoki w:

```text
sem.*
```

Po co?

Żeby dashboard nie musiał sam łączyć faktu z wymiarami i liczyć KPI. Widoki robią to centralnie.

### Krok 7: Quality checks

ETL kończy się kontrolami jakości.

Sprawdzane jest m.in.:

- czy staging ma dane,
- czy fakt ma dane,
- czy liczba kwalifikujących się rekordów staging zgadza się z faktem,
- czy nie ma pustych kluczy obcych,
- czy nie ma ujemnych miar w fakcie,
- czy nie ma duplikatów wymiarów,
- czy fakt łączy się z wymiarami,
- czy sprzedaż w staging zgadza się ze sprzedażą w fakcie.

To jest bardzo ważne na obronie, bo pokazuje, że projekt nie tylko ładuje dane, ale też sprawdza ich poprawność.

---

## 10. Dlaczego full refresh, a nie incremental load

Projekt używa podejścia full refresh.

To znaczy, że przy uruchomieniu procesu dane są odświeżane całościowo dla wybranego zakresu, zamiast dopisywać tylko nowe rekordy.

Dlaczego tak?

- to prostsze,
- jest przewidywalne,
- łatwiejsze do pokazania na prezentacji,
- łatwiejsze do debugowania,
- lepiej pasuje do projektu dydaktycznego,
- zmniejsza ryzyko błędów w logice incremental.

Dlaczego nie incremental?

Incremental load wymagałby dodatkowej logiki:

- wykrywania nowych rekordów,
- obsługi zmian w źródle,
- obsługi korekt,
- strategii ponownego przetwarzania,
- kontroli historii,
- idempotencji przy częściowych błędach.

To byłoby bardziej produkcyjne, ale znacznie trudniejsze do obrony w krótkim projekcie. Full refresh pokazuje całą ścieżkę hurtownianą czytelniej.

Jak odpowiedzieć:

```text
Wybraliśmy full refresh, bo projekt jest edukacyjny i ma pokazać pełny przepływ danych w sposób stabilny. Incremental load byłby możliwy jako rozwinięcie, ale nie był konieczny do spełnienia wymagań.
```

---

## 11. Pytania biznesowe

Projekt ma 12 pytań biznesowych. To jest maksymalna liczba mieszcząca się w wymaganiu 7-12.

Pytania są potrzebne, bo od nich zależy model.

Nie projektujemy tabel "bo tak". Projektujemy je, bo muszą odpowiedzieć na pytania.

Przykłady:

| Pytanie | Co wymusza w modelu |
|---|---|
| Sprzedaż według miesiąca, kwartału, roku | `dim_date` |
| Najlepsze sklepy | `dim_store` |
| Najlepsze kategorie | `dim_category` |
| Najlepsze produkty | `dim_product` |
| Vendorzy | `dim_vendor` |
| Opakowania | `dim_packaging` |
| Weekend vs dzień roboczy | `dim_date.is_weekend` |
| County i miasta | geografia w `dim_store` |

Jak to powiedzieć:

```text
Pytania biznesowe były punktem startowym. Każde pytanie ma odzwierciedlenie w wymiarach, miarach, widokach semantycznych i dashboardzie.
```

---

## 12. Model wielowymiarowy

Projekt używa schematu gwiazdy.

W centrum:

```text
dw.fact_sales
```

Dookoła:

```text
dw.dim_date
dw.dim_store
dw.dim_product
dw.dim_category
dw.dim_vendor
dw.dim_packaging
```

Dlaczego schemat gwiazdy?

Bo głównym procesem biznesowym jest sprzedaż. Sprzedaż ma miary, a miary analizuje się przez wymiary.

Sprzedaż można analizować:

- po dacie,
- po sklepie,
- po mieście,
- po county,
- po produkcie,
- po kategorii,
- po vendorze,
- po opakowaniu.

To jest klasyczny przypadek dla modelu wymiarowego.

Dlaczego nie jedna płaska tabela?

Jedna tabela byłaby prostsza, ale:

- powtarzałaby teksty sklepów, produktów, kategorii i vendorów,
- byłaby trudniejsza do utrzymania,
- nie pokazywałaby modelu wielowymiarowego,
- nie spełniałaby dobrze wymagań hurtowni,
- mieszałaby fakty z opisami.

Dlaczego nie snowflake?

Snowflake, czyli mocniej znormalizowany model, byłby możliwy, ale:

- zwiększyłby liczbę tabel,
- zwiększyłby liczbę joinów,
- byłby trudniejszy do tłumaczenia,
- nie dawałby dużej korzyści w tym projekcie.

Jak odpowiedzieć:

```text
Schemat gwiazdy jest najlepszy dla tego projektu, bo jest czytelny, raportowy i naturalnie odpowiada na pytania biznesowe.
```

---

## 13. Ziarno faktu

Najważniejsza rzecz w tabeli faktów to ziarno.

Ziarno mówi, co oznacza jeden rekord.

W tym projekcie:

```text
Jeden rekord w `dw.fact_sales` oznacza jedną linię sprzedaży produktu w konkretnym sklepie, konkretnego dnia i na konkretnej fakturze.
```

To znaczy:

- nie jeden miesiąc,
- nie jeden sklep,
- nie jedna kategoria,
- nie jedna cała faktura,
- tylko jedna linia faktury / sprzedaży.

Dlaczego to dobre ziarno?

Bo jest szczegółowe. A szczegółowe dane można agregować:

- do miesiąca,
- do kwartału,
- do roku,
- do sklepu,
- do miasta,
- do county,
- do kategorii,
- do vendora.

Gdybyśmy od razu zapisali dane miesięcznie, stracilibyśmy szczegół.

Jak powiedzieć:

```text
Wybraliśmy ziarno na poziomie linii sprzedaży, bo daje największą elastyczność analityczną.
```

---

## 14. Tabela faktów

Tabela faktów:

```text
dw.fact_sales
```

Przechowuje zdarzenia sprzedażowe i miary.

Ma klucze obce:

- `date_key`,
- `store_key`,
- `product_key`,
- `category_key`,
- `vendor_key`,
- `packaging_key`.

Ma też miary:

- `sales_line_count`,
- `bottles_sold`,
- `sale_dollars`,
- `volume_sold_liters`,
- `volume_sold_gallons`,
- `state_bottle_cost`,
- `state_bottle_retail`,
- `margin_amount`.

Ma też:

- `invoice_number`,
- `source_row_hash`,
- `load_timestamp`.

`invoice_number` to wymiar zdegenerowany. To znaczy, że jest identyfikatorem biznesowym trzymanym w fakcie, ale bez osobnej tabeli wymiaru.

Dlaczego nie ma `dim_invoice`?

Bo faktura nie ma tutaj rozbudowanych atrybutów opisowych. Numer faktury wystarczy trzymać w fakcie, żeby liczyć np. liczbę unikalnych faktur.

---

## 15. Wymiary

### `dw.dim_date`

Opisuje czas:

- dzień,
- miesiąc,
- kwartał,
- rok,
- nazwa dnia,
- nazwa miesiąca,
- weekend / dzień roboczy.

Dlaczego osobny wymiar czasu?

Bo czas jest jednym z najważniejszych przekrojów analizy. Dzięki `dim_date` można odpowiedzieć na pytania o miesiące, kwartały, lata i weekendy.

### `dw.dim_store`

Opisuje sklep:

- numer sklepu,
- nazwa sklepu,
- adres,
- miasto,
- county,
- stan,
- współrzędne.

Dlaczego geografia jest tutaj?

Bo lokalizacja jest cechą sklepu. Sklep ma miasto, county i współrzędne. Osobna `dim_geography` byłaby możliwa, ale niepotrzebnie komplikowałaby projekt.

### `dw.dim_product`

Opisuje produkt:

- numer produktu,
- opis produktu.

Po co?

Żeby analizować konkretne produkty i rankingi produktów.

### `dw.dim_category`

Opisuje kategorię produktu:

- numer kategorii,
- nazwa kategorii.

Po co osobno od produktu?

Bo kategoria jest poziomem agregacji. Możemy analizować szczegółowy produkt albo całą kategorię.

### `dw.dim_vendor`

Opisuje vendora / dostawcę:

- numer vendora,
- nazwa vendora.

Po co?

Bo jedno z pytań biznesowych dotyczy udziału vendorów w sprzedaży i marży.

### `dw.dim_packaging`

Opisuje opakowanie:

- `pack`,
- `bottle_volume_ml`,
- `volume_group`.

Dlaczego osobny wymiar?

Bo opakowanie jest samodzielną perspektywą analizy. Chcemy wiedzieć, które pojemności i grupy opakowań generują sprzedaż, wolumen i marżę.

---

## 16. Miary addytywne i nieaddytywne

Miary addytywne można sumować.

W projekcie addytywne są:

- `sale_dollars`,
- `bottles_sold`,
- `volume_sold_liters`,
- `volume_sold_gallons`,
- `margin_amount`,
- `sales_line_count`.

Przykład:

Sprzedaż ze sklepów A i B można dodać. Sprzedaż ze stycznia, lutego i marca można dodać. Wolumen można sumować. Marżę można sumować.

Miary nieaddytywne nie powinny być sumowane.

W projekcie nieaddytywne są:

- `state_bottle_cost`,
- `state_bottle_retail`.

Dlaczego?

Bo to ceny jednostkowe. Suma cen jednostkowych nie ma sensu biznesowego.

Zamiast sumy używa się:

- średniej,
- średniej ważonej,
- różnicy jednostkowej,
- marży wyliczonej.

Jak powiedzieć:

```text
Nie sumujemy cen jednostkowych. Sumujemy sprzedaż, wolumen, liczbę butelek i marżę.
```

---

## 17. Marża

Marża jest liczona tak:

```text
margin_amount = (state_bottle_retail - state_bottle_cost) * bottles_sold
```

Czyli:

1. bierzemy cenę detaliczną jednej butelki,
2. odejmujemy koszt jednej butelki,
3. dostajemy marżę jednostkową,
4. mnożymy przez liczbę sprzedanych butelek.

Dlaczego nie tylko `sale_dollars - cost`?

Bo dane źródłowe mają ceny jednostkowe i liczbę butelek. Wyliczenie przez jednostki jest zgodne z ziarnem linii sprzedaży.

Na obronie:

```text
Marża jest miarą wyliczoną na poziomie faktu, a potem może być agregowana po wymiarach.
```

---

## 18. Ujemne rekordy raw

W danych źródłowych mogą występować ujemne rekordy. To są realne korekty źródłowe.

Projekt robi z nimi coś rozsądnego:

- zostawia je widoczne jako fakt istnienia w raw/staging,
- pokazuje liczbę takich rekordów w quality checks,
- nie ładuje ich do faktu sprzedażowego.

Dlaczego?

Bo dashboard sprzedażowy nie powinien pokazywać ujemnej sprzedaży jako zwykłej sprzedaży. Ale jednocześnie nie wolno udawać, że takie rekordy nie istnieją.

Jak powiedzieć:

```text
Ujemne korekty są realnymi rekordami źródłowymi. Projekt pokazuje je informacyjnie, ale fakt sprzedażowy ładuje tylko rekordy kwalifikujące się do raportowania.
```

---

## 19. Warstwa semantyczna

Warstwa semantyczna to schemat:

```text
sem
```

Zawiera widoki SQL:

- `sem.vw_sales_overview`,
- `sem.vw_sales_by_month`,
- `sem.vw_sales_by_category`,
- `sem.vw_sales_by_store`,
- `sem.vw_sales_by_vendor`,
- `sem.vw_sales_by_packaging`,
- `sem.vw_sales_by_geography`,
- `sem.vw_sales_map_points`,
- `sem.vw_top_products`,
- `sem.vw_margin_analysis`,
- `sem.vw_volume_vs_revenue`,
- `sem.vw_category_sales_over_time`,
- `sem.vw_avg_sales_per_store_by_month_region`,
- `sem.vw_kpi_summary`,
- `sem.vw_etl_status`.

Po co warstwa semantyczna?

Bez niej dashboard musiałby:

- sam łączyć fakt z wymiarami,
- sam liczyć agregacje,
- sam liczyć KPI,
- sam znać szczegóły modelu,
- powtarzać logikę biznesową.

To byłoby ryzykowne i trudne w utrzymaniu.

Warstwa `sem` centralizuje logikę.

Jak powiedzieć:

```text
Dashboard korzysta z widoków `sem.*`, a nie bezpośrednio z tabel `dw`, bo warstwa semantyczna upraszcza raportowanie i daje jedno miejsce definicji KPI.
```

---

## 20. Dashboard Streamlit

Dashboard jest w:

```text
app/streamlit_app.py
```

Jest po polsku.

Ma 4 zakładki:

1. Przegląd zarządczy.
2. Produkty i kategorie.
3. Geografia.
4. Wyniki sklepów.

### Przegląd zarządczy

Pokazuje:

- sprzedaż łącznie,
- marżę łącznie,
- sprzedane butelki,
- wolumen,
- liczbę sklepów,
- liczbę produktów,
- sprzedaż w czasie,
- kwartalne i roczne rollupy,
- weekend vs dzień roboczy.

Odpowiada głównie na:

- Q1,
- Q11.

### Produkty i kategorie

Pokazuje:

- top kategorie,
- top produkty,
- marżę według kategorii,
- udział vendorów,
- analizę marży jednostkowej,
- strukturę kategorii w czasie,
- opakowania.

Odpowiada głównie na:

- Q2,
- Q5,
- Q6,
- Q7,
- Q8,
- Q12.

### Geografia

Pokazuje:

- sprzedaż według county,
- top miasta,
- wolumen vs sprzedaż,
- county z wysokim wolumenem i niższą sprzedażą na litr,
- mapy.

Odpowiada głównie na:

- Q4,
- Q9.

### Wyniki sklepów

Pokazuje:

- top sklepy,
- sklepy z wysokim wolumenem i niższą sprzedażą,
- średnią sprzedaż na sklep według county,
- rozkład sprzedaży sklepów.

Odpowiada głównie na:

- Q3,
- Q10.

---

## 21. Co jest po polsku, a co zostaje po angielsku

Po polsku są:

- interfejs dashboardu,
- zakładki,
- filtry,
- KPI,
- tytuły wykresów,
- komunikaty,
- narracja obrony,
- dokumenty prezentacyjne.

Po angielsku celowo zostają:

- nazwy technologii: Docker, Airflow, SQL Server, Streamlit, Plotly,
- nazwy schematów: `stg`, `dw`, `sem`,
- nazwy tabel: `dw.fact_sales`,
- nazwy widoków: `sem.vw_sales_overview`,
- nazwy kolumn: `sale_dollars`, `margin_amount`,
- nazwa zbioru: Iowa Liquor Sales,
- słowa domenowe ze źródła: vendor, county.

Dlaczego?

Bo tłumaczenie nazw technicznych mogłoby wprowadzić chaos. W kodzie i SQL te nazwy są po angielsku. Dashboard i opowieść są po polsku, ale obiekty techniczne zostają takie, jakie są w systemie.

Jak powiedzieć:

```text
Warstwa użytkownika jest po polsku, a nazwy techniczne pozostają po angielsku, bo są częścią bazy, kodu i oryginalnego źródła danych.
```

---

## 22. Live demo: jak uruchomić

Wejdź do folderu:

```powershell
cd D:\pjatk-idh\data-warehouse-iowa-liquor
```

Uruchom stack:

```powershell
docker compose up -d sqlserver airflow streamlit
```

Sprawdź:

```powershell
docker compose ps
```

Oczekiwane:

- SQL Server: healthy,
- Airflow: Up,
- Streamlit: Up.

Otwórz:

```text
Airflow: http://localhost:8080
Streamlit: http://localhost:8501
```

Uruchom live ETL:

```powershell
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
```

W logach szukaj:

```text
Loaded 10634 total rows into stg.iowa_liquor_sales_raw
Loaded 10624 rows into dw.fact_sales
Quality check eligible_staging_fact_row_count_difference = 0
Quality check null_foreign_keys = 0
Quality check fact_dimension_join_failures = 0
Quality check eligible_staging_vs_fact_sales_difference = 0.0000
Initial ETL finished
```

Jeśli Airflow UI nie odpowiada:

```powershell
docker compose up -d --force-recreate airflow
```

Poczekaj około minutę i sprawdź ponownie.

---

## 23. Jak opowiadać live demo

### Krok 1: Docker

Pokaż:

```powershell
docker compose ps
```

Powiedz:

```text
Tu widać trzy usługi: SQL Server jako hurtownię, Airflow jako orkiestrator ETL i Streamlit jako warstwę raportową.
```

### Krok 2: Airflow

Otwórz:

```text
http://localhost:8080
```

Pokaż DAG:

```text
iowa_liquor_etl
```

Powiedz:

```text
Ten DAG reprezentuje cały proces ETL: ekstrakcję, przygotowanie SQL, ładowanie staging, ładowanie wymiarów i faktu, widoki semantyczne oraz quality checks.
```

### Krok 3: ETL

Uruchom komendę demo.

Powiedz:

```text
Uruchamiam jednodniowy zakres demonstracyjny. To nie jest ograniczenie projektu, tylko sposób, żeby pokazać cały proces live bez długiego czekania.
```

### Krok 4: Quality checks

Pokaż w logach wartości:

- staging rows,
- fact rows,
- null foreign keys,
- fact dimension join failures,
- sales reconciliation.

Powiedz:

```text
Quality checks potwierdzają, że rekordy kwalifikujące się do faktu zgadzają się z faktem, klucze obce nie są puste, fakt łączy się z wymiarami, a sprzedaż po transformacji zgadza się ze stagingiem.
```

### Krok 5: Streamlit

Otwórz:

```text
http://localhost:8501
```

Pokaż:

- status danych,
- pokrycie warstwy semantycznej,
- KPI,
- 4 zakładki.

Powiedz:

```text
Dashboard korzysta z widoków semantycznych `sem.*`, czyli z warstwy Gold, a nie bezpośrednio z tabel technicznych.
```

---

## 24. Wersja prezentacji w 3 minuty

```text
Projekt przedstawia hurtownię danych dla publicznego zbioru Iowa Liquor Sales. Analizujemy sprzedaż detaliczną i dystrybucję, a nie konsumpcję alkoholu. Interesują nas przychody, wolumen, marża, sklepy, geografia, kategorie produktów, vendorzy i opakowania.

Dane są realne i niegenerowane. ETL próbuje pobrać dane z publicznego API, a jeśli endpoint jest niedostępny, korzysta z lokalnego cache realnych plików raw. To zabezpiecza demo, ale nie zmienia charakteru danych.

Architektura jest klasyczna dla hurtowni danych: Bronze to raw CSV, Silver to staging w SQL Server, a Gold to schemat gwiazdy, widoki semantyczne i dashboard. Orkiestrację wykonuje Airflow, hurtownia działa w SQL Server, a raportowanie jest zrobione w Streamlit.

Model danych to schemat gwiazdy. Centralna tabela faktów to `dw.fact_sales`. Wymiary to data, sklep, produkt, kategoria, vendor i opakowanie. Ziarno faktu oznacza jedną linię sprzedaży produktu w sklepie, w dniu i na fakturze.

Projekt odpowiada na 12 pytań biznesowych. Dashboard ma cztery zakładki: Przegląd zarządczy, Produkty i kategorie, Geografia oraz Wyniki sklepów. Pokazuje KPI, wykresy, mapy, tabele i eksport CSV.

Na końcu ETL uruchamia quality checks, które sprawdzają liczbę rekordów, klucze obce, połączenia z wymiarami i zgodność sprzedaży. Projekt spełnia wymagania, bo ma realne dane, ETL, hurtownię, schemat gwiazdy, warstwę semantyczną i dashboard.
```

---

## 25. Wersja prezentacji w 10-15 minut

1. Zacznij od tematu:

```text
Projekt dotyczy hurtowni danych dla Iowa Liquor Sales.
```

2. Wyjaśnij cel:

```text
Nie badamy konsumpcji, tylko sprzedaż, dystrybucję, wolumen i marżę.
```

3. Powiedz o danych:

```text
Dane są realne i niegenerowane. Są zapisane jako raw CSV, a ETL może je pobrać przez API albo użyć lokalnego cache.
```

4. Przejdź przez architekturę:

```text
Iowa Liquor Sales -> Airflow -> raw CSV -> staging -> dw -> sem -> Streamlit.
```

5. Wyjaśnij Bronze/Silver/Gold:

```text
Bronze to raw, Silver to staging, Gold to model gwiazdy i semantyka.
```

6. Omów model:

```text
Fakt sprzedaży i sześć wymiarów.
```

7. Powiedz ziarno:

```text
Jedna linia sprzedaży produktu w sklepie, w dniu i na fakturze.
```

8. Omów miary:

```text
Sumujemy sprzedaż, wolumen, butelki i marżę. Nie sumujemy cen jednostkowych.
```

9. Omów ETL:

```text
Extract, SQL objects, staging, dimensions, fact, semantic views, quality checks.
```

10. Omów semantykę:

```text
Widoki `sem.*` są warstwą raportową w SQL.
```

11. Pokaż dashboard:

```text
4 zakładki odpowiadają na 12 pytań biznesowych.
```

12. Zamknij:

```text
Projekt pokazuje pełną ścieżkę od realnych danych do raportów i spełnia wymagania.
```

---

## 26. Typowe pytania prowadzącej i odpowiedzi

### Czy dane są generowane?

Nie. Dane są realne. Fallback cache też korzysta z realnych plików raw, a nie z danych syntetycznych.

### Po co staging?

Staging oddziela źródło od hurtowni. Pozwala technicznie uporządkować dane przed modelem wymiarowym.

### Dlaczego Airflow?

Bo dobrze pokazuje proces ETL: taski, kolejność, logi i statusy.

### Dlaczego SQL Server?

Bo spełnia rolę relacyjnej hurtowni danych i pozwala tworzyć schematy, tabele oraz widoki.

### Dlaczego schemat gwiazdy?

Bo sprzedaż jest naturalnym faktem, a czas, sklep, produkt, kategoria, vendor i opakowanie są naturalnymi wymiarami analizy.

### Jakie jest ziarno faktu?

Jedna linia sprzedaży produktu w sklepie, w konkretnym dniu i na konkretnej fakturze.

### Dlaczego geografia jest w `dim_store`?

Bo lokalizacja jest atrybutem sklepu. Miasto, county, zip code i współrzędne opisują sklep.

### Dlaczego jest `dim_packaging`?

Bo opakowanie jest osobną perspektywą analizy i jedno z pytań biznesowych dotyczy pojemności oraz grup opakowań.

### Dlaczego nie incremental load?

Full refresh jest prostszy, stabilniejszy i lepszy do projektu dydaktycznego. Incremental load byłby możliwym rozwinięciem.

### Po co warstwa semantyczna?

Żeby dashboard korzystał z gotowych widoków i KPI, a nie samodzielnie łączył techniczne tabele.

### Co robią quality checks?

Sprawdzają, czy dane po transformacji są spójne: liczby rekordów, klucze obce, joiny z wymiarami, ujemne miary i zgodność sprzedaży.

### Co oznaczają ujemne rekordy raw?

To realne korekty źródłowe. Projekt pokazuje je informacyjnie, ale nie ładuje ich do faktu sprzedaży.

### Czy Streamlit jest hurtownią?

Nie. Streamlit jest tylko warstwą raportową. Hurtownią jest SQL Server.

### Jak dashboard odpowiada na pytania biznesowe?

Przez 4 zakładki:

- Przegląd zarządczy: czas i weekendy.
- Produkty i kategorie: produkty, kategorie, vendorzy, marża, opakowania.
- Geografia: county, miasta, mapy, wolumen vs sprzedaż.
- Wyniki sklepów: sklepy i średnia sprzedaż na sklep.

---

## 27. Czego nie mówić

Nie mów:

```text
Analizujemy konsumpcję alkoholu.
```

Mów:

```text
Analizujemy sprzedaż detaliczną i dystrybucję.
```

Nie mów:

```text
Dane są wygenerowane fallbackiem.
```

Mów:

```text
Fallback używa realnych plików raw.
```

Nie mów:

```text
Streamlit to hurtownia.
```

Mów:

```text
Streamlit to raportowanie. Hurtownia jest w SQL Server.
```

Nie mów:

```text
Jednodniowy zakres to cały projekt.
```

Mów:

```text
Jednodniowy zakres to szybki zakres demonstracyjny.
```

Nie mów:

```text
Sumujemy wszystkie miary.
```

Mów:

```text
Sumujemy miary addytywne. Cen jednostkowych nie sumujemy.
```

---

## 28. Najważniejsze zdania do zapamiętania

```text
Projekt nie jest tylko dashboardem, ale pełną hurtownią danych.
```

```text
Bronze to raw CSV, Silver to staging SQL, Gold to model gwiazdy, widoki semantyczne i dashboard.
```

```text
Ziarno faktu to jedna linia sprzedaży produktu w sklepie, w dniu i na fakturze.
```

```text
Dashboard korzysta z warstwy semantycznej `sem.*`, a nie bezpośrednio z tabel technicznych.
```

```text
Fallback cache nie generuje danych, tylko używa realnych plików raw.
```

```text
Ujemne rekordy raw są realnymi korektami źródłowymi, ale nie trafiają do faktu sprzedaży.
```

```text
Zakres jednodniowy jest zakresem demo, a nie ograniczeniem projektu.
```

```text
Projekt spełnia wymagania: realne dane, 12 pytań, schemat gwiazdy, ETL, SQL Server, semantyka i dashboard.
```

---

## 29. Szybka mapa plików

| Obszar | Plik / folder |
|---|---|
| Główne README | `README.md` |
| Opis projektu | `docs/project_description.md` |
| Pytania biznesowe | `docs/business_requirements.md` |
| Model wymiarowy | `docs/dimensional_model.md` |
| Uzasadnienie modelu | `docs/uzasadnienie_modelu.md` |
| ETL | `docs/etl_description.md` |
| Przepływ pipeline | `docs/pipeline_flow.md` |
| Warstwa semantyczna | `docs/warstwa_semantyczna.md` |
| Live demo | `docs/live_demo_checklista.md` |
| Pytania i odpowiedzi | `docs/pytania_i_odpowiedzi_techniczne.md` |
| Dashboard | `app/streamlit_app.py` |
| DAG Airflow | `dags/iowa_liquor_etl_dag.py` |
| SQL tabele DW | `sql/03_create_dw_tables.sql` |
| SQL widoki semantyczne | `sql/04_create_semantic_views.sql` |
| Quality checks | `sql/05_quality_checks.sql` |
| Ekstrakcja | `src/extract/socrata_extract.py` |
| Transformacja | `src/transform/warehouse_transform.py` |
| Ładowanie staging | `src/load/sqlserver_loader.py` |

---

## 30. Ostateczne podsumowanie

Ten projekt można obronić jako pełny projekt hurtowni danych, bo ma:

- realne dane,
- pytania biznesowe,
- model wielowymiarowy,
- ETL,
- SQL Server,
- staging,
- schemat gwiazdy,
- warstwę semantyczną,
- dashboard,
- quality checks,
- live demo.

Najważniejsza odpowiedź na pytanie "o co chodzi w tym projekcie":

```text
Chodzi o pokazanie pełnej architektury hurtowni danych: od realnych danych transakcyjnych Iowa Liquor Sales, przez ETL i model gwiazdy w SQL Server, do widoków semantycznych i polskiego dashboardu, który odpowiada na pytania biznesowe o sprzedaż, marżę, produkty, sklepy, geografię, vendorów i opakowania.
```
