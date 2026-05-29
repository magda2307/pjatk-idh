# Wymagania biznesowe

## Kontekst projektu

Celem projektu jest zbudowanie hurtowni danych wspierajacej analize sprzedazy detalicznej i dystrybucji regulowanych produktow na podstawie publicznego zbioru Iowa Liquor Sales. Organizacja chce analizowac sprzedaz wedlug czasu, sklepow, geografii, kategorii, vendorow, produktow i opakowan.

Projekt nie koncentruje sie na konsumpcji alkoholu. Perspektywa biznesowa to analiza sprzedazy, dystrybucji, przychodow, wolumenu i marzy w sieci detalicznej.

## Pytania biznesowe

| Nr | Pytanie biznesowe | Widok semantyczny / raport |
|---:|---|---|
| 1 | Jak zmieniala sie calkowita wartosc sprzedazy w kolejnych miesiacach i kwartalach? | `sem.vw_sales_by_month`, raport Executive overview |
| 2 | Ktore kategorie produktow generowaly najwyzszy przychod? | `sem.vw_sales_by_category`, raport Product and category analysis |
| 3 | Ktore sklepy osiagaly najwyzsza sprzedaz wartosciowa? | `sem.vw_sales_by_store`, raport Store performance |
| 4 | Ktore miasta i hrabstwa generowaly najwiekszy obrot? | `sem.vw_sales_by_geography`, raport Geography analysis |
| 5 | Ktorzy vendorzy mieli najwiekszy udzial w sprzedazy? | `sem.vw_sales_by_vendor`, raport Product and category analysis |
| 6 | Ktore produkty sprzedawaly sie najlepiej ilosciowo? | `sem.vw_top_products`, raport Product and category analysis |
| 7 | Ktore produkty lub kategorie generowaly najwyzsza marze jednostkowa i calkowita? | `sem.vw_margin_analysis`, `sem.vw_sales_by_category`, raport Product and category analysis |
| 8 | Jak zmieniala sie struktura sprzedazy wedlug kategorii produktow w czasie? | `sem.vw_category_sales_over_time`, raport Product and category analysis |
| 9 | Ktore regiony mialy wysoka sprzedaz wolumenowa, ale nizsza wartosc sprzedazy? | `sem.vw_volume_vs_revenue`, raport Geography analysis |
| 10 | Jaka byla srednia wartosc sprzedazy na sklep w podziale na miesiace i regiony? | `sem.vw_avg_sales_per_store_by_month_region`, raport Store performance |

## Miary biznesowe

- Wartosc sprzedazy: `sale_dollars`
- Liczba sprzedanych butelek: `bottles_sold`
- Wolumen w litrach: `volume_sold_liters`
- Wolumen w galonach: `volume_sold_gallons`
- Marza: `(state_bottle_retail - state_bottle_cost) * bottles_sold`
- Liczba linii sprzedazy: `sales_line_count`
- Koszt jednostkowy: `state_bottle_cost`, miara nieaddytywna
- Cena detaliczna jednostkowa: `state_bottle_retail`, miara nieaddytywna

## Wymiary analizy

- Czas: dzien, miesiac, kwartal, rok
- Sklep: numer sklepu, nazwa, adres, miasto, hrabstwo
- Produkt: numer produktu, opis
- Kategoria: numer i nazwa kategorii
- Vendor: numer i nazwa vendora
- Geografia: miasto, hrabstwo, kod pocztowy, stan
- Opakowanie: pack, pojemnosc butelki, grupa pojemnosci

## Minimalny zestaw raportow

Projekt powinien dostarczyc co najmniej nastepujace raporty:

1. Sprzedaz w czasie
   - miesiac / kwartal / rok
   - `sale_dollars`
   - `bottles_sold`
   - `volume_sold_liters`

2. Sprzedaz wedlug sklepow
   - top sklepy
   - suma sprzedazy
   - liczba butelek
   - marza

3. Sprzedaz wedlug produktow i kategorii
   - top produkty
   - top kategorie
   - porownanie ilosci i wartosci

4. Sprzedaz geograficzna
   - city / county
   - tabela albo mapa

5. Analiza marzy
   - marza wedlug produktu, kategorii, sklepu
   - marza jednostkowa i calkowita

6. Vendor analysis
   - sprzedaz wedlug vendora
   - marza wedlug vendora

7. Struktura kategorii w czasie
   - udzial kategorii w kolejnych miesiacach
   - trend sprzedazy wedlug kategorii

8. Srednia sprzedaz na sklep wedlug miesiaca i regionu
   - srednia wartosc sprzedazy na sklep
   - porownanie county w czasie

## Wymagania raportowe

Raporty powinny zawierac:

- agregacje,
- filtrowanie,
- sortowanie,
- wykresy,
- kilka perspektyw analizy,
- czytelne biznesowe nazwy,
- mozliwosc odpowiedzi na pytania biznesowe bez odwolania do tabel technicznych.
