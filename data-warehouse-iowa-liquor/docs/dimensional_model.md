# Model wymiarowy

## Ziarno tabeli faktow

Jeden rekord w `dw.fact_sales` reprezentuje jedna linie sprzedazy produktu w konkretnym sklepie, w konkretnym dniu i na konkretnej fakturze, zgodnie z ziarnistoscia danych zrodlowych Iowa Liquor Sales.

Jezeli w zrodle istnieja duplikaty dla tego samego numeru faktury, produktu, sklepu i daty, rekordy sa zachowywane w stagingu. Agregacja odbywa sie w widokach semantycznych, a nie przez ukryte usuwanie rekordow.

## Tabela faktow

`dw.fact_sales`

Klucze obce:

- `date_key`
- `store_key`
- `product_key`
- `category_key`
- `vendor_key`
- `packaging_key`

Wymiar zdegenerowany:

- `invoice_number`

Miary addytywne:

- `sales_line_count`
- `bottles_sold`
- `sale_dollars`
- `volume_sold_liters`
- `volume_sold_gallons`
- `margin_amount`

Miary jednostkowe / nieaddytywne:

- `state_bottle_cost`
- `state_bottle_retail`

`state_bottle_cost` i `state_bottle_retail` sa cenami jednostkowymi. Nie powinny byc sumowane w raportach. Nalezy analizowac je przez `AVG` albo srednia wazona.

## Wymiary

- `dw.dim_date`: dzien, miesiac, kwartal, rok, etykiety polskie i angielskie.
- `dw.dim_store`: sklep, adres, miasto, kod pocztowy, hrabstwo, stan, wspolrzedne.
- `dw.dim_product`: produkt i opis produktu.
- `dw.dim_category`: kategoria produktu.
- `dw.dim_vendor`: vendor / dostawca.
- `dw.dim_packaging`: pack, pojemnosc butelki i grupa pojemnosci.

## Hierarchie

Data:

```text
day -> month -> quarter -> year
```

Geografia:

```text
store -> city -> county -> state
```

Produkt:

```text
product -> category
```

Vendor analysis:

```text
product -> vendor
```

Packaging analysis:

```text
product -> packaging
```

## Diagram schematu gwiazdy

```mermaid
erDiagram
    FACT_SALES {
        int sales_key PK
        int date_key FK
        int store_key FK
        int product_key FK
        int category_key FK
        int vendor_key FK
        int packaging_key FK
        string invoice_number
        int sales_line_count
        decimal bottles_sold
        decimal sale_dollars
        decimal volume_sold_liters
        decimal volume_sold_gallons
        decimal state_bottle_cost
        decimal state_bottle_retail
        decimal margin_amount
    }

    DIM_DATE {
        int date_key PK
        date date
        int day
        int month
        int quarter
        int year
        string year_month
        string day_name_en
        string day_name_pl
        string month_name_en
        string month_name_pl
        bit is_weekend
    }

    DIM_STORE {
        int store_key PK
        string store_number
        string store_name
        string address
        string city
        string zip_code
        string county
        string state_name
        decimal latitude
        decimal longitude
    }

    DIM_PRODUCT {
        int product_key PK
        string item_number
        string item_description
    }

    DIM_CATEGORY {
        int category_key PK
        string category_number
        string category_name
    }

    DIM_VENDOR {
        int vendor_key PK
        string vendor_number
        string vendor_name
    }

    DIM_PACKAGING {
        int packaging_key PK
        int pack
        int bottle_volume_ml
        string volume_group
    }

    FACT_SALES }o--|| DIM_DATE : date_key
    FACT_SALES }o--|| DIM_STORE : store_key
    FACT_SALES }o--|| DIM_PRODUCT : product_key
    FACT_SALES }o--|| DIM_CATEGORY : category_key
    FACT_SALES }o--|| DIM_VENDOR : vendor_key
    FACT_SALES }o--|| DIM_PACKAGING : packaging_key
```
