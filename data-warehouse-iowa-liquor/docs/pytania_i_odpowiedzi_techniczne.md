# Pytania i odpowiedzi techniczne do obrony

## 1. Dlaczego wybraliście taki temat?

Bo Iowa Liquor Sales to publiczny, realny i duży zbiór danych transakcyjnych. Nadaje się do hurtowni, bo ma czas, sklepy, produkty, kategorie, vendorów, geografię, wolumen, ceny i sprzedaż.

## 2. Czy dane są generowane?

Nie. Dane są realne. Pochodzą z publicznego zbioru Iowa Liquor Sales. Lokalny fallback używa realnych plików raw z `data/raw`, a nie danych syntetycznych.

## 3. Dlaczego jest fallback z cache?

Publiczny endpoint może być niedostępny albo zmieniony. Żeby demo było stabilne, ETL najpierw próbuje API, a gdy API zwraca błąd, bierze realne dane z lokalnego cache raw.

## 4. Czy fallback łamie wymaganie o danych niegenerowanych?

Nie, bo fallback nie tworzy danych. On filtruje realne rekordy z raw CSV.

## 5. Dlaczego jeden dzień w live demo?

Pełny rok jest cięższy i wolniejszy. Na prezentacji ważne jest pokazanie działającego procesu ETL. Jeden dzień używa tego samego kodu i tej samej architektury.

## 6. Jaki jest model danych?

Schemat gwiazdy:

- fakt: `dw.fact_sales`,
- wymiary: `dim_date`, `dim_store`, `dim_product`, `dim_category`, `dim_vendor`, `dim_packaging`.

## 7. Jakie jest ziarno faktu?

Jeden rekord w `dw.fact_sales` to jedna linia sprzedaży produktu w sklepie, w konkretnym dniu i na konkretnej fakturze.

## 8. Dlaczego geografia jest w `dim_store`, a nie w osobnym wymiarze?

Bo geografia w tym projekcie opisuje lokalizację sklepu. Miasto, county, zip code i współrzędne są atrybutami sklepu. Osobny wymiar geograficzny byłby możliwy, ale dla tych pytań biznesowych nie jest konieczny.

## 9. Dlaczego `dim_packaging` jest osobnym wymiarem?

Bo jedno z pytań biznesowych dotyczy grup opakowań i pojemności butelek. Osobny wymiar ułatwia analizę po `pack`, `bottle_volume_ml` i `volume_group`.

## 10. Co jest miarą addytywną?

Można sumować:

- `sale_dollars`,
- `bottles_sold`,
- `volume_sold_liters`,
- `volume_sold_gallons`,
- `margin_amount`,
- `sales_line_count`.

## 11. Co jest miarą nieaddytywną?

`state_bottle_cost` i `state_bottle_retail`, bo to ceny jednostkowe. Nie należy ich po prostu sumować.

## 12. Jak liczona jest marża?

```text
margin_amount = (state_bottle_retail - state_bottle_cost) * bottles_sold
```

## 13. Co oznacza Bronze/Silver/Gold?

- Bronze: raw CSV w `data/raw`.
- Silver: staging SQL `stg.iowa_liquor_sales_raw`.
- Gold: model gwiazdy `dw.*`, widoki `sem.*` i dashboard.

## 14. Co robi Airflow?

Airflow orkiestruje ETL:

1. extract,
2. create SQL objects,
3. load staging,
4. load dimensions,
5. load fact,
6. create semantic views,
7. run quality checks.

## 14a. Czy ETL lepiej uruchamiać z Airflow UI czy z Dockera?

Na prezentacji lepiej z Airflow UI. Wtedy widać DAG, kolejność zadań, statusy i logi. To bezpośrednio pokazuje wymagany element ETL/orchestracji.

Dockerowa komenda jest planem B. Jest dobra, gdy UI się zawiesi albo trzeba szybko sprawdzić pipeline bez klikania.

## 14b. Jak ustawić miesiąc w Airflow UI?

Przy ręcznym uruchomieniu DAG-a `iowa_liquor_etl` można podać konfigurację JSON:

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "limit": 50000
}
```

To ładuje styczeń. Dla jednego dnia demo:

```json
{
  "start_date": "2023-01-03",
  "end_date": "2023-01-03",
  "limit": 5000
}
```

## 15. Co jest hurtownią?

SQL Server. Schematy:

- `stg` - staging,
- `dw` - model wymiarowy,
- `sem` - warstwa semantyczna.

## 16. Co jest warstwą semantyczną?

Widoki SQL w schemacie `sem`, na przykład:

- `sem.vw_sales_overview`,
- `sem.vw_sales_by_month`,
- `sem.vw_margin_analysis`,
- `sem.vw_kpi_summary`.

## 17. Dlaczego nie raportujecie bezpośrednio z tabel faktów?

Bo warstwa semantyczna upraszcza raportowanie, centralizuje KPI i ukrywa techniczne szczegóły modelu.

## 18. Jak dashboard odpowiada na pytania biznesowe?

Dashboard ma 4 zakładki:

- Przegląd zarządczy: Q1, Q11.
- Produkty i kategorie: Q2, Q5, Q6, Q7, Q8, Q12.
- Geografia: Q4, Q9.
- Wyniki sklepów: Q3, Q10.

## 19. Co sprawdzają quality checks?

Sprawdzają:

- liczbę wierszy staging,
- liczbę wierszy faktu,
- zgodność eligible staging z fact,
- null foreign keys,
- ujemne miary w fakcie,
- duplikaty wymiarów,
- join faktu z wymiarami,
- zgodność sprzedaży staging vs fact.

## 20. Dlaczego są ujemne rekordy raw?

To realne korekty z danych źródłowych. Nie są ładowane do faktu sprzedaży, ale są pokazane informacyjnie jako `raw_negative_measure_rows_excluded_from_fact`.

## 21. Co zrobić, jeśli Airflow UI nie wstaje?

Najpierw sprawdzić:

```powershell
docker compose ps
```

Jeśli kontener jest up, ale UI nie odpowiada:

```powershell
docker compose up -d --force-recreate airflow
```

Po około minucie:

```powershell
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```

## 22. Co zrobić, jeśli API zwraca 404?

To jest obsłużone. ETL użyje lokalnego cache realnych raw CSV i dalej przejdzie.

## 23. Jak pokazać, że projekt działa?

Minimalny dowód:

```powershell
docker compose ps
docker compose run --rm -e IOWA_START_DATE=2023-01-03 -e IOWA_END_DATE=2023-01-03 -e SOCRATA_LIMIT=5000 airflow python -m src.run_initial_etl
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
```

## 24. Co jeśli padnie internet?

Projekt nadal może pokazać live ETL na lokalnym cache realnych raw data. Internet nie jest krytyczny dla demo.

## 25. Co jeśli Docker nie działa albo nie jest zainstalowany?

Jeśli Docker jest zainstalowany, ale nie działa, trzeba uruchomić Docker Desktop i poczekać, aż silnik będzie gotowy.

Jeśli Dockera w ogóle nie ma, nie ma prostej ścieżki startu jednym poleceniem. Trzeba ręcznie zainstalować SQL Server, ODBC Driver 18, Python 3.11, pakiety z `requirements.txt` i skonfigurować zmienne środowiskowe. Na prezentację rekomendowana jest wersja Docker Compose.

## 26. Czy projekt spełnia rubrykę?

Tak:

- pytania biznesowe: 12,
- schemat gwiazdy: tak,
- ETL live: tak,
- warstwa semantyczna: tak,
- raporty z wykresami: tak.

Formalnie trzeba tylko podać prawdziwy skład zespołu 2-4 osób.
