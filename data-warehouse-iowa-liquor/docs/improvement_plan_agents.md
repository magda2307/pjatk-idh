# Plan usprawnien: jasnosc, zgodnosc z celem i podzial agentow

## Cel zadania

Projekt ma pokazac kompletna hurtownie danych dla analizy sprzedazy detalicznej i dystrybucji na podstawie publicznych danych Iowa Liquor Sales. Ocena powinna jasno widziec:

- realne zrodlo danych i ekstrakcje przez API,
- warstwy `raw`, `stg`, `dw`, `sem`,
- model wymiarowy ze schematem gwiazdy,
- fakt, wymiary, ziarno i miary,
- ETL orkiestracyjny w Airflow,
- kontrole jakosci,
- dashboard Streamlit odpowiadajacy na pytania biznesowe,
- kompletna narracje do obrony projektu.

## Co juz pasuje do celu

- Projekt ma realne dane Iowa Liquor Sales z Socrata API.
- Dokumentacja opisuje cel biznesowy, model, ETL, warstwe semantyczna i dashboard.
- Model ma jedna tabele faktow i szesc wymiarow: czas, sklep, produkt, kategoria, vendor, opakowanie.
- Warstwa semantyczna ma widoki dla wszystkich glownych raportow.
- Dashboard korzysta z widokow `sem`, a nie bezposrednio z tabel technicznych.
- Airflow DAG pokazuje przeplyw od ekstrakcji do quality checks.
- README ma gotowa sciezke uruchomienia i obrony.

## Braki i ryzyka

| Priorytet | Obszar | Co brakuje / co jest niejasne | Dlaczego wazne | Efekt po poprawie |
|---|---|---|---|---|
| P1 | Spolnosc dokumentacji | `progress.md` nadal mowi o 10 pytaniach biznesowych, a README i `business_requirements.md` mowia o 12. | Niespojnosc moze wygladac jak nieukonczona zmiana zakresu. | Wszystkie dokumenty mowia jednym glosem o 12 pytaniach. |
| P1 | Dowod dzialania | Zweryfikowany stan demo opisuje tylko jednodniowy zakres `2023-01-03`. | Projekt ma domyslny zakres roczny, wiec warto miec mocniejszy dowod przynajmniej dla wiekszego wycinka. | Obrona ma silniejszy argument, ze pipeline skaluje sie ponad jeden dzien. |
| P1 | Kryteria ukonczenia | Brakuje jednej checklisty "gotowe do oddania". | Latwo przeoczyc wymaganie projektowe lub element prezentacji. | Ocena statusu projektu jest szybka i jednoznaczna. |
| P2 | Slownictwo | Dokumenty mieszaja polski opis z angielskimi nazwami raportow i polami technicznymi. | To jest akceptowalne technicznie, ale moze oslabic czytelnosc. | Nazwy sa konsekwentne: techniczne po angielsku, opis po polsku. |
| P2 | Mermaid/linki | README zawiera absolutne linki lokalne typu `/D:/...`. | Dziala lokalnie, ale gorzej wyglada na GitHub. | Linki relatywne dzialaja lokalnie i na GitHub. |
| P2 | Jakosc repo | Repo sledzi pliki `__pycache__/*.pyc`. | To szum w repo i ryzyko konfliktow po uruchomieniach. | `.gitignore` i repo bez binarnych cache Python. |
| P2 | Quality checks | README podaje wyniki, ale nie ma osobnego protokolu walidacji z data, zakresem i komendami. | Ocena moze zapytac "jak to sprawdzono?". | Jest powtarzalny raport walidacji. |
| P3 | Diagramy | Jest kilka diagramow, ale brakuje jednego "end-to-end lineage" z pytanie -> widok -> dashboard. | To ulatwia obrony ustne. | Jedna mapa pokazuje realizacje wymagan od pytan do raportow. |
| P3 | Prezentacja | `presentation_notes.md` jest dobre, ale nie ma wersji 5-minutowej i 10-minutowej. | Czas obrony bywa ograniczony. | Latwiej dopasowac narracje do czasu. |

## Podzial agentow

### Agent 1: Dokumentacja i jasnosc

Cel: usunac niespojnosci i poprawic czytelnosc narracji.

Zadania:

- Zmienic `progress.md`: "Business requirements with 10 questions" -> "12 questions".
- Przejrzec README, `project_description.md`, `business_requirements.md`, `etl_description.md` pod katem powtorzen i sprzecznosci.
- Ujednolicic nazwy: "county" zostaje jako termin danych Iowa, "hrabstwo" tylko w objasnieniach.
- Zamienic absolutne linki lokalne w dokumentacji na relatywne linki GitHub-friendly.
- Dodac sekcje "Status gotowosci do oddania" z lista kontrolna.

Rezultat:

- Dokumentacja czyta sie jak jeden spojny projekt, nie zlepek etapow.

### Agent 2: Walidacja i dowody dzialania

Cel: przygotowac twardy dowod, ze pipeline i raporty dzialaja.

Zadania:

- Uruchomic szybki demo run dla jednego dnia i zapisac wynik.
- Jesli zasoby pozwola, uruchomic wiekszy zakres, np. tydzien lub miesiac.
- Zapisac liczby: staging rows, fact rows, null foreign keys, negative measures, liczba widokow `sem` z danymi.
- Utworzyc `docs/validation_report.md` z data uruchomienia, zakresem danych, komendami i wynikami.
- Dopisac w README link do raportu walidacji.

Rezultat:

- Projekt ma powtarzalny dowod dzialania, gotowy do pokazania prowadzacemu.

### Agent 3: Model i warstwa semantyczna

Cel: sprawdzic, czy model odpowiada na wszystkie pytania biznesowe.

Zadania:

- Porownac 12 pytan z `business_requirements.md` z widokami w `sql/04_create_semantic_views.sql`.
- Sprawdzic, czy kazde pytanie ma minimum jeden widok i jedna sekcje dashboardu.
- Dodac brakujace komentarze SQL tylko tam, gdzie logika miar nie jest oczywista.
- Sprawdzic, czy `margin_amount`, `sales_per_liter`, `avg_invoice_value` i `avg_margin_percent` sa liczone konsekwentnie.
- Dodac mala tabele "pytanie -> widok -> dashboard" do `warstwa_semantyczna.md`, jesli obecna wersja nie wystarcza.

Rezultat:

- Warstwa semantyczna jest jasnie powiazana z wymaganiami biznesowymi.

### Agent 4: Dashboard i UX raportow

Cel: upewnic sie, ze dashboard odpowiada na pytania bez tlumaczenia tabel technicznych.

Zadania:

- Sprawdzic cztery strony dashboardu: Executive overview, Product and category analysis, Geography analysis, Store performance.
- Zweryfikowac, czy kazda strona ma KPI, wykres i tabele tam, gdzie ma to sens.
- Dodac krotkie biznesowe tytuly sekcji zamiast technicznych opisow.
- Upewnic sie, ze eksport CSV dziala dla glownych tabel.
- Sprawdzic puste stany: brak danych, brak polaczenia SQL, blad widoku.

Rezultat:

- Dashboard broni projekt biznesowo, nie tylko technicznie.

### Agent 5: Repo hygiene i oddanie

Cel: ograniczyc szum techniczny i przygotowac repo do oddania.

Zadania:

- Dodac lub poprawic `.gitignore` dla `__pycache__/`, `*.pyc`, lokalnych plikow tymczasowych i sekretow.
- Usunac sledzone pliki cache Python z repo po potwierdzeniu, ze nie sa wymagane.
- Sprawdzic, czy `requirements.txt`, `docker-compose.yml` i instrukcje uruchomienia sa zgodne.
- Sprawdzic `git status` przed finalnym commitem.
- Uzyc komunikatu commita w stylu:

```text
docs(project): add improvement plan
```

Rezultat:

- Repo jest czystsze i latwiejsze do ocenienia.

## Kolejnosc prac

1. Agent 1 usuwa niespojnosci w dokumentacji.
2. Agent 3 sprawdza mapowanie pytan na widoki i raporty.
3. Agent 4 robi szybki przeglad dashboardu.
4. Agent 2 uruchamia walidacje i zapisuje wyniki.
5. Agent 5 sprzata repo i przygotowuje finalny commit.

## Definicja gotowosci

Projekt jest gotowy, gdy:

- wszystkie dokumenty mowia o tym samym celu i tych samych 12 pytaniach,
- pipeline ma zapisany raport walidacji,
- kazde pytanie biznesowe ma widok semantyczny i miejsce w dashboardzie,
- README pozwala uruchomic projekt od zera,
- prezentacja ma jasna narracje od zrodla danych do raportu,
- repo nie zawiera nowych plikow cache ani lokalnego szumu,
- ostatni `git status` jest czysty po commicie.

## Najkrotsza narracja dla obrony

Projekt pobiera realne dane Iowa Liquor Sales z publicznego API, zapisuje je jako raw CSV, laduje do SQL Server staging, przeksztalca do modelu gwiazdy w schemacie `dw`, publikuje biznesowe widoki w schemacie `sem`, a dashboard Streamlit odpowiada na 12 pytan biznesowych dotyczacych sprzedazy, marzy, produktow, sklepow, regionow, vendorow i opakowan.
