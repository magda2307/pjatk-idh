# Wymagania biznesowe

## Kontekst projektu

Celem projektu jest zbudowanie hurtowni danych wspierajacej analize sprzedazy detalicznej i dystrybucji regulowanych produktow na podstawie publicznego zbioru Iowa Liquor Sales. Organizacja chce analizowac sprzedaz wedlug czasu, sklepow, geografii, kategorii, vendorow, produktow i opakowan.

Projekt nie koncentruje sie na konsumpcji alkoholu. Perspektywa biznesowa to analiza sprzedazy, dystrybucji, przychodow, wolumenu i marzy w sieci detalicznej.

## Finalne pytania biznesowe

Ten zestaw pytan zostal ulozony tak, aby kazdy wymiar modelu mial jasne zastosowanie biznesowe.

| Nr | Pytanie biznesowe | Wykorzystywany wymiar / atrybut | Widok semantyczny / raport |
|---:|---|---|---|
| 1 | Jak zmienialy sie calkowita sprzedaz, marza i liczba faktur wedlug miesiaca, kwartalu i roku? | `dim_date` | `sem.vw_sales_by_month`, Przeglad zarzadczy |
| 2 | Ktore kategorie generowaly najwyzszy przychod i marze? | `dim_category` | `sem.vw_sales_by_category`, Produkty i kategorie |
| 3 | Ktore sklepy generowaly najwyzsza sprzedaz i marze? | `dim_store` | `sem.vw_sales_by_store`, Wyniki sklepow |
| 4 | Ktore miasta i county generowaly najwyzszy przychod i wolumen? | geografia w `dim_store` | `sem.vw_sales_by_geography`, Geografia |
| 5 | Ktorzy vendorzy mieli najwyzszy udzial w sprzedazy i wklad w marze? | `dim_vendor` | `sem.vw_sales_by_vendor`, Produkty i kategorie |
| 6 | Ktore produkty sprzedawaly sie najlepiej wedlug liczby butelek i wartosci sprzedazy? | `dim_product` | `sem.vw_top_products`, Produkty i kategorie |
| 7 | Ktore kategorie i produkty mialy najwyzsza marze jednostkowa i calkowita? | `dim_product`, `dim_category`, ceny jednostkowe | `sem.vw_margin_analysis`, Produkty i kategorie |
| 8 | Jak zmieniala sie struktura sprzedazy kategorii w czasie? | `dim_date`, `dim_category` | `sem.vw_category_sales_over_time`, Produkty i kategorie |
| 9 | Ktore regiony mialy wysoki wolumen, ale nizsza wartosc sprzedazy na litr? | geografia w `dim_store`, miary wolumenu | `sem.vw_volume_vs_revenue`, Geografia |
| 10 | Jak zmieniala sie srednia sprzedaz na sklep wedlug miesiaca i county? | `dim_date`, `dim_store` | `sem.vw_avg_sales_per_store_by_month_region`, Wyniki sklepow |
| 11 | Jak roznia sie sprzedaz, wolumen i liczba faktur w weekendy oraz dni robocze? | `dim_date.is_weekend` | `sem.vw_sales_by_day_type`, Przeglad zarzadczy |
| 12 | Ktore grupy opakowan i pojemnosci butelek generowaly najwyzsza sprzedaz, wolumen i marze? | `dim_packaging` | `sem.vw_sales_by_packaging`, Produkty i kategorie |

## Miary biznesowe

- Wartosc sprzedazy: `sale_dollars`
- Liczba sprzedanych butelek: `bottles_sold`
- Wolumen w litrach: `volume_sold_liters`
- Wolumen w galonach: `volume_sold_gallons`
- Marza: `(state_bottle_retail - state_bottle_cost) * bottles_sold`
- Liczba linii sprzedazy: `sales_line_count`
- Koszt jednostkowy: `state_bottle_cost`, miara nieaddytywna
- Cena detaliczna jednostkowa: `state_bottle_retail`, miara nieaddytywna

## KPI

Warstwa semantyczna udostepnia KPI w `sem.vw_kpi_summary`:

- `total_sales`
- `total_margin`
- `invoice_count`
- `store_count`
- `product_count`
- `avg_invoice_value`
- `avg_bottles_per_invoice`
- `avg_margin_percent`
- `sales_per_store`
- `sales_per_liter`

## Wymiary analizy

- Czas: dzien, miesiac, kwartal, rok, weekend / dzien roboczy
- Sklep: numer sklepu, nazwa, adres, miasto, county
- Produkt: numer produktu, opis
- Kategoria: numer i nazwa kategorii
- Vendor: numer i nazwa vendora
- Geografia: miasto, county, kod pocztowy, stan
- Opakowanie: pack, pojemnosc butelki, grupa pojemnosci

## Minimalny zestaw raportow

Projekt dostarcza raporty:

1. Sprzedaz w czasie
2. Sprzedaz wedlug sklepow
3. Sprzedaz wedlug produktow i kategorii
4. Sprzedaz geograficzna
5. Analiza marzy
6. Analiza vendorow
7. Struktura kategorii w czasie
8. Srednia sprzedaz na sklep wedlug miesiaca i regionu
9. Sprzedaz wedlug typu dnia
10. Sprzedaz wedlug opakowania

## Wymagania raportowe

Raporty zawieraja:

- agregacje,
- filtrowanie,
- sortowanie,
- wykresy,
- tabele,
- eksport CSV,
- kilka perspektyw analizy,
- czytelne biznesowe nazwy,
- mozliwosc odpowiedzi na pytania biznesowe bez odwolania do tabel technicznych.
