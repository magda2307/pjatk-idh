# Warstwa semantyczna

## Cel warstwy semantycznej

Warstwa semantyczna w projekcie pelni role posrednia pomiedzy modelem hurtowni danych `dw` a raportami w Streamlit.

Jej zadaniem jest:

- ukrycie technicznych szczegolow modelu gwiazdy,
- udostepnienie biznesowych nazw i gotowych agregacji,
- przygotowanie danych pod raporty i wykresy,
- centralizacja logiki obliczen,
- zapewnienie spojnosc wynikow w calym projekcie.

W projekcie warstwa semantyczna zostala zrealizowana jako widoki SQL w schemacie:

```text
sem
```

## Dlaczego potrzebna jest warstwa semantyczna

Model `dw` jest poprawny analitycznie, ale zawiera:

- surrogate keys,
- relacje miedzy faktami i wymiarami,
- pola techniczne,
- szczegolowosc na poziomie pojedynczej linii sprzedazy.

Bez warstwy semantycznej kazdy raport musialby samodzielnie:

- laczyc tabele,
- pilnowac agregacji,
- powtarzac logike KPI,
- rozstrzygac, ktore pola sumowac, a ktorych nie.

Warstwa `sem` rozwiazuje ten problem. Uzytkownik raportu korzysta z gotowych struktur biznesowych, a nie z surowego modelu technicznego.

## Zrodlo danych dla warstwy semantycznej

Warstwa semantyczna korzysta z:

- `dw.fact_sales`
- `dw.dim_date`
- `dw.dim_store`
- `dw.dim_product`
- `dw.dim_category`
- `dw.dim_vendor`
- `dw.dim_packaging`

Widok bazowy:

```text
sem.vw_sales_overview
```

To glowny widok laczacy fakt z wymiarami. Pozostale widoki semantyczne buduja nad nim agregacje i pola raportowe.

## Wymiary analityczne w warstwie semantycznej

Warstwa semantyczna udostepnia nastepujace wymiary analizy:

### 1. Wymiar czasu

Zrodlo:

- `dw.dim_date`

Atrybuty:

- `date`
- `day`
- `month`
- `month_name_en`
- `month_name_pl`
- `quarter`
- `year`
- `year_month`
- `day_name_en`
- `day_name_pl`
- `is_weekend`

Zastosowanie:

- analiza trendow miesiecznych, kwartalnych i rocznych,
- porownania sprzedazy w czasie,
- analiza sezonowosci.

### 2. Wymiar sklepu

Zrodlo:

- `dw.dim_store`

Atrybuty:

- `store_number`
- `store_name`
- `address`
- `city`
- `county`
- `zip_code`
- `state_name`
- `latitude`
- `longitude`

Zastosowanie:

- analiza najlepszych sklepow,
- analiza sprzedazy na sklep,
- analizy geograficzne na poziomie punktow sprzedazy.

### 3. Wymiar produktu

Zrodlo:

- `dw.dim_product`

Atrybuty:

- `item_number`
- `item_description`

Zastosowanie:

- analiza top produktow,
- analiza ilosciowa i wartosciowa,
- analiza rentownosci pojedynczych produktow.

### 4. Wymiar kategorii

Zrodlo:

- `dw.dim_category`

Atrybuty:

- `category_number`
- `category_name`

Zastosowanie:

- agregacja sprzedazy wedlug grup produktowych,
- analiza struktury sprzedazy,
- analiza marzy na poziomie kategorii.

### 5. Wymiar vendora

Zrodlo:

- `dw.dim_vendor`

Atrybuty:

- `vendor_number`
- `vendor_name`

Zastosowanie:

- analiza sprzedazy wedlug dostawcy,
- analiza udzialu vendorow w przychodach,
- porownanie marzy pomiedzy vendorami.

### 6. Wymiar opakowania

Zrodlo:

- `dw.dim_packaging`

Atrybuty:

- `pack`
- `bottle_volume_ml`
- `volume_group`

Zastosowanie:

- analiza wolumenu wedlug pojemnosci,
- porownanie wynikow sprzedazowych dla roznych opakowan,
- analiza relacji wartosc sprzedazy vs wielkosc opakowania.

## Hierarchie analityczne

Warstwa semantyczna wspiera nastepujace hierarchie:

### Hierarchia czasu

```text
dzien -> miesiac -> kwartal -> rok
```

Realizacja:

- `date`
- `month`
- `quarter`
- `year`
- `year_month`

### Hierarchia geograficzna

```text
sklep -> miasto -> county -> stan
```

Realizacja:

- `store_name`
- `city`
- `county`
- `state_name`

### Hierarchia produktowa

```text
produkt -> kategoria
```

Realizacja:

- `item_description`
- `category_name`

### Perspektywa dostawcy

To nie jest klasyczna hierarchia nad kategoria, lecz dodatkowy przekroj analityczny:

```text
produkt -> vendor
```

Realizacja:

- `item_description`
- `vendor_name`

### Hierarchia opakowania

```text
produkt -> bottle_volume_ml -> volume_group
```

Realizacja:

- `item_description`
- `bottle_volume_ml`
- `volume_group`

## Miary i pola wyliczane

Warstwa semantyczna udostepnia miary bezposrednie oraz pola obliczane.

### Miary podstawowe

Pochodzace z faktu:

- `sale_dollars`
- `bottles_sold`
- `volume_sold_liters`
- `volume_sold_gallons`
- `margin_amount`
- `sales_line_count`

### Miary nieaddytywne

- `state_bottle_cost`
- `state_bottle_retail`

Sa to ceny jednostkowe. Nie powinny byc sumowane. W warstwie semantycznej sa wykorzystywane przez:

- `AVG`
- analize marzy jednostkowej

### Pola wyliczane i kalkulacje

Warstwa semantyczna wykorzystuje miedzy innymi:

1. `avg_margin_per_bottle`

```text
SUM(margin_amount) / SUM(bottles_sold)
```

2. `sales_share_percent`

```text
100 * suma sprzedazy wybranej grupy / suma sprzedazy ogolem
```

3. `avg_unit_margin`

```text
AVG(state_bottle_retail - state_bottle_cost)
```

4. `sales_per_liter`

```text
SUM(sale_dollars) / SUM(volume_sold_liters)
```

5. `avg_sales_per_store`

```text
AVG(store_month_sales)
```

6. `avg_bottles_per_store`

```text
AVG(store_month_bottles)
```

7. `avg_volume_liters_per_store`

```text
AVG(store_month_volume_liters)
```

8. `avg_margin_per_store`

```text
AVG(store_month_margin)
```

### Kalkulacja marzy

Najwazniejsza kalkulacja biznesowa:

```text
margin_amount = (state_bottle_retail - state_bottle_cost) * bottles_sold
```

Jest ona obliczana juz na poziomie faktu, a nastepnie agregowana w warstwie semantycznej.

## KPI

Warstwa semantyczna zawiera zestaw KPI wykorzystywanych w dashboardzie.

Glowny widok KPI:

```text
sem.vw_kpi_summary
```

Zawiera:

- `total_sales`
- `total_margin`
- `sales_line_count`
- `total_bottles_sold`
- `total_volume_liters`
- `invoice_count`
- `store_count`
- `product_count`
- `category_count`
- `vendor_count`

### Interpretacja KPI

1. `total_sales`
   - calkowita wartosc sprzedazy w analizowanym zakresie

2. `total_margin`
   - laczna marza uzyskana ze sprzedazy

3. `sales_line_count`
   - liczba linii sprzedazy w fakcie

4. `total_bottles_sold`
   - laczna liczba sprzedanych butelek

5. `total_volume_liters`
   - laczny wolumen sprzedazy w litrach

6. `invoice_count`
   - liczba unikalnych dokumentow sprzedazy

7. `store_count`
   - liczba sklepow aktywnych w analizowanym zakresie

8. `product_count`
   - liczba produktow obecnych w analizowanym zakresie

9. `category_count`
   - liczba kategorii obecnych w analizowanym zakresie

10. `vendor_count`
   - liczba vendorow obecnych w analizowanym zakresie

## Widoki semantyczne i ich rola

### 1. `sem.vw_sales_overview`

Rola:

- glowny widok laczacy wszystkie wymiary i miary,
- baza dla filtrowania i dashboardu,
- najbardziej szczegolowy widok semantyczny.

### 2. `sem.vw_sales_by_month`

Rola:

- analiza zmian sprzedazy w czasie,
- odpowiedz na pytania o miesiace i kwartaly,
- agregacja miesieczna.

### 3. `sem.vw_sales_by_category`

Rola:

- analiza kategorii produktowych,
- udzial kategorii w sprzedazy,
- marza i przychod wedlug kategorii.

### 4. `sem.vw_sales_by_store`

Rola:

- analiza sklepow,
- ranking sklepow,
- przychod i wolumen na poziomie sklepu.

### 5. `sem.vw_sales_by_vendor`

Rola:

- analiza dostawcow,
- udzial vendorow w przychodzie,
- porownanie marzy wedlug vendora.

### 6. `sem.vw_sales_by_geography`

Rola:

- analiza sprzedazy geograficznej,
- city / county / state,
- wsparcie dla tabel i map.

### 7. `sem.vw_top_products`

Rola:

- ranking produktow,
- analiza ilosciowa i wartosciowa produktow,
- identyfikacja bestsellerow.

### 8. `sem.vw_margin_analysis`

Rola:

- analiza rentownosci,
- marza jednostkowa i calkowita,
- porownanie produktow, kategorii i vendorow.

### 9. `sem.vw_volume_vs_revenue`

Rola:

- analiza zaleznosci miedzy wolumenem i przychodem,
- identyfikacja regionow o wysokim wolumenie i nizszej wartosci.

### 10. `sem.vw_category_sales_over_time`

Rola:

- analiza struktury sprzedazy kategorii w czasie,
- porownanie zmian udzialu kategorii miesiac do miesiaca.

### 11. `sem.vw_avg_sales_per_store_by_month_region`

Rola:

- analiza sredniej sprzedazy na sklep,
- porownanie county i miast w czasie,
- odpowiedz na pytanie o sprzedaz na sklep wedlug regionu i miesiaca.

### 12. `sem.vw_kpi_summary`

Rola:

- zestawienie najwazniejszych KPI dla dashboardu,
- szybki widok pod executive overview.

## Jak warstwa semantyczna realizuje wymagania projektu

Warstwa semantyczna realizuje wymagania pierwszej czesci projektu, poniewaz:

1. odwzorowuje glowne wymiary analizy,
2. udostepnia atrybuty potrzebne do filtrowania i grupowania,
3. zawiera hierarchie czasu, geografii i produktu,
4. dostarcza pola wyliczane potrzebne do raportow,
5. udostepnia KPI do raportu zarzadczego,
6. ukrywa techniczne szczegoly modelu `dw`,
7. pozwala budowac raporty bez bezposredniej pracy na tabelach faktow i wymiarow.

## Podsumowanie

Warstwa semantyczna w projekcie nie jest tylko zbiorem przypadkowych widokow. Jest uporzadkowana warstwa biznesowa nad hurtownia danych.

Jej funkcja polega na tym, ze:

- model `dw` przechowuje dane w strukturze analitycznej,
- warstwa `sem` nadaje im znaczenie raportowe,
- dashboard Streamlit korzysta juz z gotowych struktur biznesowych.

W praktyce oznacza to, ze wymagania dotyczace wymiarow, atrybutow, hierarchii, pol wyliczanych, kalkulacji i KPI zostaly zrealizowane w sposob spójny i zgodny z architektura calego projektu.
