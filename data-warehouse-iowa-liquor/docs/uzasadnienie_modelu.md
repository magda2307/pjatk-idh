# Uzasadnienie doboru modelu i zrodla danych

## Cel dokumentu

Celem tego dokumentu jest wyjasnienie:

- dlaczego wybrano zbior Iowa Liquor Sales,
- dlaczego dane nadaja sie do budowy hurtowni danych,
- dlaczego zastosowano schemat gwiazdy,
- dlaczego tabela faktow i wymiary maja taka postac,
- jak model wspiera pytania biznesowe i raporty.

Dokument ma charakter uzasadnienia projektowego. Pokazuje nie tylko co zostalo zbudowane, ale tez dlaczego taki wybor jest poprawny z punktu widzenia architektury hurtowni danych.

## Dlaczego wybrano takie zrodlo danych

Wybranym zrodlem jest publiczny zbior:

```text
Iowa Liquor Sales
Socrata resource ID: m3tr-qhgy
https://data.iowa.gov/resource/m3tr-qhgy.csv
```

To zrodlo zostalo wybrane, poniewaz:

1. Jest to zbior rzeczywisty, publicznie dostepny i mozliwy do pobrania online.
2. Dane maja charakter historyczny i zawieraja wymiar czasu, co jest kluczowe w projektach hurtowni danych.
3. Dane opisuja transakcje sprzedazowe, a wiec naturalnie wspieraja analizy biznesowe.
4. Zbior zawiera jednoczesnie informacje o produkcie, kategorii, vendorze, sklepie, lokalizacji i wartosci sprzedazy.
5. Dane pochodza z API CSV, co pozwala pokazac realny proces ekstrakcji, a nie jedynie reczne ladowanie pliku.

## Dlaczego te dane nadaja sie do analiz biznesowych

Zbior pozwala odpowiadac na konkretne pytania analityczne, na przyklad:

- jak zmienia sie sprzedaz w czasie,
- ktore sklepy sprzedaja najwiecej,
- ktore produkty i kategorie generuja najwyzszy przychod,
- jacy vendorzy maja najwiekszy udzial w obrocie,
- ktore regiony generuja wysoki wolumen, ale nizsza wartosc sprzedazy,
- gdzie powstaje najwyzsza marza.

Oznacza to, ze dane nie zostaly wybrane przypadkowo. Zostaly dobrane tak, aby wspierac konkretne miary i raporty, a nie tylko dlatego, ze byly latwo dostepne.

## Jak rozumiemy podstawowe pojecia w projekcie

Aby model byl jednoznaczny, w projekcie przyjeto nastepujace definicje:

- `sprzedaz` - wartosc transakcji wyrazona miara `sale_dollars`,
- `fakt sprzedazy` - pojedyncza linia sprzedazy produktu w sklepie, w danym dniu i na danej fakturze,
- `produkt` - konkretny indeks towarowy z pola `item_number`,
- `kategoria` - grupa produktow opisana przez `category` i `category_name`,
- `vendor` - dostawca lub producent identyfikowany przez `vendor_number` i `vendor_name`,
- `sklep` - punkt detaliczny identyfikowany przez `store_number`,
- `opakowanie` - cechy fizyczne produktu, przede wszystkim `pack` i `bottle_volume_ml`.

Takie definicje sa potrzebne, aby pozniej poprawnie zbudowac ziarno faktu, wymiary i raporty.

## Dlaczego zastosowano schemat gwiazdy

W projekcie zastosowano schemat gwiazdy, poniewaz jest to najbardziej naturalny i najczytelniejszy model dla analizy sprzedazy.

Schemat gwiazdy zostal wybrany, bo:

1. Jest prosty do wyjasnienia podczas prezentacji projektu.
2. Dobrze wspiera agregacje i filtrowanie danych.
3. Jest standardowym rozwiazaniem w klasycznych hurtowniach danych typu ROLAP.
4. Oddziela zdarzenia biznesowe od kontekstu opisowego.
5. Ulatwia budowe warstwy semantycznej i dashboardu.

W centrum modelu znajduje sie tabela faktow, a wokol niej tabele wymiarow. Taki uklad odpowiada klasycznej logice analitycznej: najpierw mamy zdarzenie biznesowe, a potem perspektywy, wedlug ktorych to zdarzenie analizujemy.

## Dlaczego nie wybrano bardziej zlozonego modelu

Mozliwe byloby zastosowanie modelu platka sniegu albo bardziej rozbudowanej normalizacji, ale w tym projekcie nie byloby to najlepsze rozwiazanie.

Powody sa nastepujace:

- projekt ma byc czytelny i demonstracyjny,
- rozwiazanie ma byc mozliwe do uruchomienia na zwyklym laptopie,
- zbyt duza normalizacja utrudnilaby raportowanie i prezentacje,
- projekt studencki powinien pokazac poprawne podstawy hurtowni danych, a nie niepotrzebna zlozonosc.

Dlatego wybrano model prosty, ale poprawny architektonicznie.

## Dlaczego tabela faktow ma taka postac

Centralna tabela modelu to:

```text
dw.fact_sales
```

Zawiera ona:

- klucze obce do wymiarow,
- miary liczbowe,
- numer faktury jako wymiar zdegenerowany,
- techniczny hash rekordu,
- znacznik czasu ladowania.

### Ziarno tabeli faktow

Przyjete ziarno brzmi:

```text
Jeden rekord w dw.fact_sales reprezentuje jedna linie sprzedazy produktu
w konkretnym sklepie, w konkretnym dniu i na konkretnej fakturze,
zgodnie z ziarnistoscia danych zrodlowych Iowa Liquor Sales.
```

Takie ziarno zostalo wybrane, poniewaz:

1. Jest zgodne z charakterem danych zrodlowych.
2. Pozwala zachowac szczegolowosc potrzebna do agregacji w wielu przekrojach.
3. Umoliwia analizy po czasie, sklepie, produkcie, kategorii, vendorze i regionie.
4. Nie wymusza przedwczesnej agregacji podczas ETL.

To bardzo wazne, bo w hurtowni danych poziom szczegolowosci faktu powinien wynikac z potrzeb analitycznych, a nie z wygody implementacyjnej.

## Dlaczego miary zostaly wybrane w taki sposob

W tabeli faktow znajduja sie miary addytywne:

- `sales_line_count`
- `bottles_sold`
- `sale_dollars`
- `volume_sold_liters`
- `volume_sold_gallons`
- `margin_amount`

Sa one addytywne, czyli mozna je bezpiecznie sumowac po wymiarach i okresach czasu.

Dodatkowo w fakcie przechowywane sa:

- `state_bottle_cost`
- `state_bottle_retail`

Te dwie miary nie sa miarami addytywnymi. Sa to ceny jednostkowe, dlatego nie powinny byc analizowane przez zwykle sumowanie. Ich obecnoscia w fakcie jest uzasadniona, bo pozwalaja liczyc:

- sredni koszt jednostkowy,
- srednia cene detaliczna,
- srednia marze jednostkowa,
- miary wazone w warstwie semantycznej.

## Dlaczego wymiary zostaly zdefiniowane w taki sposob

Model zawiera nastepujace wymiary:

- `dw.dim_date`
- `dw.dim_store`
- `dw.dim_product`
- `dw.dim_category`
- `dw.dim_vendor`
- `dw.dim_packaging`

Kazdy z tych wymiarow opisuje inna perspektywe analizy.

### dim_date

Wymiar czasu jest niezbedny, bo praktycznie wszystkie raporty biznesowe porownuja wyniki w czasie.

Zawiera:

- dzien,
- miesiac,
- kwartal,
- rok,
- nazwy dni i miesiecy po angielsku i po polsku,
- pole `year_month`.

Pozwala to odpowiadac na pytania o trendy miesieczne, kwartalne i roczne.

### dim_store

Wymiar sklepu opisuje miejsce sprzedazy.

Zawiera:

- numer sklepu,
- nazwe sklepu,
- adres,
- miasto,
- county,
- kod pocztowy,
- stan,
- wspolrzedne geograficzne.

Geografia zostala utrzymana w `dim_store`, a nie w osobnym wymiarze geograficznym. To swiadoma decyzja projektowa.

Powod:

- dla tego projektu sklep i jego lokalizacja sa bardzo silnie powiazane,
- osobny wymiar geograficzny powodowalby czesciowe dublowanie atrybutow,
- model mial pozostac prosty i typowo gwiazdowy.

### dim_product

Wymiar produktu opisuje konkretny towar.

Zawiera:

- numer produktu,
- opis produktu.

Produkt pozostaje osobnym wymiarem, poniewaz raporty czesto schodza na poziom konkretnego indeksu towarowego.

### dim_category

Kategoria zostala wydzielona do osobnego wymiaru, mimo ze da sie ja logicznie powiazac z produktem.

To rozwiazanie jest uzasadnione, bo:

- raporty bardzo czesto agreguja dane na poziomie kategorii,
- upraszcza to budowe widokow i dashboardu,
- poprawia czytelnosc modelu,
- odpowiada praktyce hurtowni danych, gdzie kategorie biznesowe sa traktowane jako samodzielna os analizy.

### dim_vendor

Vendor rowniez zostal wydzielony jako osobny wymiar.

To poprawne, poniewaz:

- vendor nie jest czescia hierarchii kategorii,
- vendor i kategoria opisują produkt z dwoch roznych perspektyw,
- organizacja chce analizowac sprzedaz i marze wedlug dostawcy.

Dlatego w projekcie przyjeto:

- analiza produktowa: produkt -> kategoria
- analiza dostawcow: produkt -> vendor

Nie nalezy traktowac `vendor` jako poziomu hierarchii nad `category`.

### dim_packaging

Szosty wymiar to `dim_packaging`.

Zostal dodany, poniewaz:

1. Pozwala analizowac sprzedaz wedlug cech opakowania.
2. Jest biznesowo sensowny, bo wielkosc opakowania ma wplyw na wolumen i wartosc sprzedazy.
3. Jest czystszy modelowo niz sztuczne wydzielanie zduplikowanej geografii.

Wymiar ten zawiera:

- `pack`
- `bottle_volume_ml`
- `volume_group`

## Jak model odpowiada na pytania biznesowe

Model zostal zbudowany od pytan biznesowych do tabel, a nie odwrotnie.

Na przyklad:

- pytania o trendy w czasie wykorzystuja `dim_date`,
- pytania o najlepsze sklepy wykorzystuja `dim_store`,
- pytania o top produkty wykorzystuja `dim_product`,
- pytania o kategorie wykorzystuja `dim_category`,
- pytania o vendorow wykorzystuja `dim_vendor`,
- pytania o wielkosc opakowania lub wolumen wykorzystuja `dim_packaging`,
- pytania o marze wykorzystuja miary `margin_amount`, `state_bottle_cost`, `state_bottle_retail`.

To pokazuje, ze model wielowymiarowy nie jest przypadkowym zestawem tabel. Kazdy jego element wspiera konkretne potrzeby analityczne.

## Jak model wspolpracuje z danymi zrodlowymi

Zrodlo nie jest ladowane bezposrednio do tabel docelowych `dw`. Najpierw dane trafiaja do warstwy `stg`.

Przeplyw jest nastepujacy:

```text
API CSV -> raw files -> staging -> dimensions -> fact -> semantic views -> dashboard
```

To podejscie jest poprawne, poniewaz:

- oddziela dane zrodlowe od docelowej hurtowni,
- pozwala wykonac czyszczenie i mapowanie,
- zachowuje surowosc danych w stagingu,
- daje mozliwosc kontroli jakosci przed zaladowaniem faktu.

## Dlaczego nie usuwamy duplikatow po cichu

W projekcie przyjeto zasade, ze rekordy zrodlowe sa zachowywane w stagingu. Jezeli w zrodle pojawiaja sie powtorzenia albo korekty, nie sa one automatycznie ukrywane.

To jest wazne, bo:

- staging powinien byc wierny wobec zrodla,
- ukryte usuwanie rekordow mogloby zafalszowac analizy,
- agregacja nalezy do warstwy semantycznej, a nie do niejawnego czyszczenia danych.

Wymiary sa deduplikowane tylko tam, gdzie budowane sa rekordy opisowe na podstawie kluczy naturalnych.

## Dlaczego warstwa semantyczna jest potrzebna

Sam schemat gwiazdy jest dobry dla hurtowni, ale nie zawsze jest najwygodniejszy dla raportowania bezposrednio przez uzytkownika koncowego.

Dlatego nad warstwa `dw` zbudowano warstwe `sem`, ktora:

- ukrywa techniczne klucze,
- upraszcza nazwy i agregacje,
- dostarcza gotowe miary biznesowe,
- przygotowuje dane bezposrednio pod dashboard.

To oznacza, ze model gwiazdy jest podstawa przechowywania i integracji danych, a warstwa semantyczna jest podstawa ich wygodnej interpretacji.

## Podsumowanie

Wybrany model jest uzasadniony, poniewaz:

1. Dane zrodlowe sa rzeczywiste, historyczne i bogate analitycznie.
2. Schemat gwiazdy dobrze pasuje do analizy sprzedazy.
3. Ziarno faktu odpowiada poziomowi danych zrodlowych.
4. Wymiary zostaly dobrane bezposrednio pod pytania biznesowe.
5. Miary zostaly rozdzielone na addytywne i nieaddytywne.
6. Model pozostaje prosty, czytelny i obronny na prezentacji.
7. Warstwa staging i warstwa semantyczna wzmacniaja poprawna architekture rozwiazania.

Z tego powodu przyjety projekt jest nie tylko dzialajacy technicznie, ale tez poprawny metodycznie jako studencka hurtownia danych.
