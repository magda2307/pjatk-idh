# Scenariusz obrony i prezentacji projektu od A do Z

Ten plik jest gotowym scenariuszem mówienia na prezentacji. Można iść punkt po punkcie i pokazywać projekt w tej samej kolejności.

## 0. Jednozdaniowy start

> Projekt przedstawia hurtownię danych dla publicznego zbioru Iowa Liquor Sales. Celem jest analiza sprzedaży detalicznej i dystrybucji według czasu, sklepów, geografii, kategorii, vendorów, produktów i opakowań.

**Ważne dopowiedzenie:**
Nie analizujemy konsumpcji alkoholu. Analizujemy sprzedaż, wolumen, marżę, efektywność sklepów i strukturę dystrybucji.

## 1. Problem biznesowy

**Co mówić:**
> Organizacja chce wiedzieć, gdzie i kiedy sprzedaż jest najwyższa, które kategorie i produkty generują największy przychód, którzy vendorzy mają największy udział, które sklepy i regiony są najmocniejsze oraz gdzie wolumen jest wysoki, ale wartość na litr jest niższa.

**Dlaczego to ma sens biznesowo:**
- pozwala porównywać sklepy i regiony,
- pomaga ocenić kategorie i vendorów,
- pokazuje trendy w czasie,
- pokazuje marżę, nie tylko przychód,
- daje podstawę do decyzji asortymentowych i dystrybucyjnych.

## 2. Dane źródłowe

**Co pokazać:**
- folder `data/raw`,
- pliki `iowa_liquor_sales_2023_part_000.csv` itd.,
- `data/processed/extract_manifest.json`.

**Co mówić:**
> Dane są realne i niegenerowane. Pochodzą z publicznego zbioru Iowa Liquor Sales. Opis katalogowy zbioru podaje zakres od 2012-01-01 do danych bieżących. W projekcie domyślnie analizujemy pełny rok 2023, czyli od 2023-01-01 do 2023-12-31.

**Co dopowiedzieć o API:**
> API filtruje dane po polu `date`. W Airflow podajemy `start_date` i `end_date` w formacie YYYY-MM-DD. Wybraliśmy rok 2023 jako konkretny wycinek do hurtowni i raportów, ale źródło jest szersze. ETL pobiera dane przez API albo, przy niedostępności endpointu, filtruje lokalny cache realnych plików raw.

**Jak odpowiedzieć, jeśli ktoś pyta "czy fallback to generowanie danych?":**
> Nie. Fallback nie generuje nowych danych. Bierze realne rekordy z lokalnych plików raw i filtruje je do wybranego zakresu dat.

## 3. Architektura projektu

**Główny przepływ:**
`Iowa Liquor Sales -> Airflow ETL -> raw CSV -> SQL Server staging -> SQL Server DW star schema -> SQL semantic views -> Streamlit dashboard`

**Co mówić:**
> Architektura jest klasyczna dla hurtowni danych: mamy warstwę surową (Bronze), staging (Silver), model wymiarowy (Gold), warstwę semantyczną i raportowanie. Orkiestracja jest w Airflow, baza hurtowni w SQL Server, raportowanie w Streamlit.

## 4. Bronze / Silver / Gold

**Bronze:**
- `data/raw/*.csv` - to kopia realnych danych źródłowych, pozwala powtórzyć ETL bez ponownego pobierania wszystkiego z internetu.

**Silver:**
- `stg.iowa_liquor_sales_raw` - warstwa technicznie oczyszczona i ujednolicona w SQL Server. Tu dane są już w bazie, mają techniczne typy.

**Gold:**
- `dw.fact_sales` i wymiary, oraz widoki `sem.*` - to model gwiazdy i widoki semantyczne. Z tej warstwy korzysta raportowanie.

## 5. Pytania biznesowe

**Co pokazać:**
- `docs/business_requirements.md`.

**Co mówić:**
> Projekt ma 12 pytań biznesowych, czyli mieści się w wymaganym zakresie 7-12. Pytania pokrywają czas, geografię, sklepy, produkty, kategorie, vendorów, marżę, weekendy i opakowania.

**Przykładowe pytania:**
- Jak zmieniała się sprzedaż według miesiąca, kwartału i roku?
- Które kategorie i produkty generują najwyższą sprzedaż i marżę?
- Które sklepy i regiony są najmocniejsze?
- Jak weekendy różnią się od dni roboczych?

## 6. Model wielowymiarowy

**Co pokazać:**
- `docs/dimensional_model.md`
- `sql/03_create_dw_tables.sql`

**Co mówić:**
> Model jest schematem gwiazdy. W centrum jest tabela faktów `dw.fact_sales`, a dookoła są wymiary: data, sklep, produkt, kategoria, vendor i opakowanie.

**Ziarno faktu:**
> Jeden rekord w `dw.fact_sales` oznacza jedną linię sprzedaży produktu w konkretnym sklepie, w konkretnym dniu i na konkretnej fakturze.

**Ważna odpowiedź o geografii:**
> Nie robiliśmy osobnej `dim_geography`, bo w tym projekcie lokalizacja jest atrybutem sklepu. To ogranicza duplikacje i wystarcza do pytań biznesowych.

## 7. Miary

**Najważniejsze miary w fakcie:**
- `sale_dollars` - wartość sprzedaży,
- `bottles_sold` - liczba butelek,
- `volume_sold_liters` - wolumen,
- `margin_amount` - marża,
- `sales_line_count` - liczba linii sprzedaży.

**Ważne:**
`state_bottle_cost` i `state_bottle_retail` są miarami jednostkowymi, czyli nieaddytywnymi. Nie powinno się ich sumować. Do marży używamy wyliczonej miary `margin_amount`.

## 8. ETL

**Kroki ETL:**
1. Ekstrakcja danych (Extract).
2. Zapis raw CSV.
3. Tworzenie obiektów SQL.
4. Ładowanie staging.
5. Ładowanie wymiarów.
6. Ładowanie faktu.
7. Tworzenie widoków semantycznych.
8. Quality checks.

**Uruchomienie live przez Airflow UI:**
1. Wejdź na `http://localhost:8080` (admin / admin).
2. Otwórz DAG `iowa_liquor_etl`.
3. Kliknij `Trigger DAG` i sprawdź parametry (`start_date`, `end_date`, `limit`). Domyślny zakres to pełny rok 2023. Format dat to `YYYY-MM-DD`.

## 9. Quality checks

**Co sprawdzamy:**
- czy staging i fact mają dane,
- zgodność liczby wierszy kwalifikujących się do faktu,
- brak null foreign keys,
- czy fakt łączy się z wymiarami,
- czy sprzedaż w staging i fakcie się zgadza.

**Co powiedzieć o 10 ujemnych rekordach (jeśli wystąpią):**
> W raw są realne ujemne korekty źródłowe. Pokazujemy je jako informacyjną kontrolę, ale nie ładujemy ich do faktu sprzedaży, żeby raport nie miał ujemnej sprzedaży.

## 10. Warstwa semantyczna

**Co pokazać:**
- `sql/04_create_semantic_views.sql`

**Co mówić:**
> Warstwa semantyczna to widoki SQL w schemacie `sem`. Dashboard Streamlit nie odpytuje bezpośrednio tabel faktów i wymiarów, tylko korzysta z widoków `sem`. Upraszcza to raportowanie i ukrywa złożoność modelu.

## 11. Dashboard Streamlit

**Co pokazać:**
- `http://localhost:8501`

**Zakładki:**
1. Przegląd zarządczy
2. Produkty i kategorie
3. Geografia
4. Wyniki sklepów

**Co mówić:**
> Dashboard jest po polsku i odpowiada na pytania biznesowe przez KPI, wykresy, mapy, tabele i eksport CSV.

## 12. Co jest po polsku, a co po angielsku

**Po polsku:** Interfejs dashboardu, zakładki, filtry, KPI, tytuły wykresów, komunikaty, główne notatki do prezentacji.
**Celowo po angielsku:** Nazwy technologii (Docker, Airflow, Streamlit), nazwy obiektów technicznych (`dw.fact_sales`), nazwy kolumn, nazwa zbioru (Iowa Liquor Sales), słowa domenowe (vendor, county).

## 13. Jednozdaniowe zamknięcie

> Projekt spełnia wymagania: ma realne dane, 12 pytań biznesowych, schemat gwiazdy, działający ETL w Airflow, hurtownię w SQL Server, warstwę semantyczną w widokach SQL i polski dashboard z raportami odpowiadającymi na te pytania.
