# Plan materialu: nauka projektu od zera

## Cel

Stworzyc bardzo rozlegly plik `.md`, ktory uczy projektu od absolutnego poczatku:

- co to za projekt,
- po co powstal,
- jak wygladala praca,
- dlaczego wybrano takie decyzje,
- dlaczego nie inne,
- jak dziala architektura,
- jak dziala ETL,
- jak dziala model gwiazdy,
- jak dziala warstwa semantyczna,
- jak dziala dashboard,
- jak uruchomic projekt live,
- jak odpowiadac na pytania techniczne prowadzacej.

Docelowy plik:

```text
docs/nauka_projektu/01_projekt_od_zera_podrecznik.md
```

## Odbiorca

Osoba, ktora ma obronic projekt i musi rozumiec nie tylko "co kliknac", ale tez:

- co jest w kazdej warstwie,
- dlaczego kazda warstwa istnieje,
- jakie byly alternatywy,
- czemu ich nie wybrano,
- jak bronic decyzji technicznych,
- jak poprowadzic prowadzaca od danych do dashboardu.

## Styl

Material ma byc:

- po polsku,
- dydaktyczny,
- szczegolowy,
- spokojny i logiczny,
- pisany prostym jezykiem,
- gotowy do uczenia sie przed obrona,
- z sekcjami "co powiedziec", "dlaczego tak", "czemu nie inaczej", "pytania od prowadzacej".

## Zakres finalnego dokumentu

1. Start od zera: co to jest hurtownia danych i po co ten projekt.
2. Kontekst biznesowy Iowa Liquor Sales.
3. Co bylo wymagane w rubryce i jak projekt na to odpowiada.
4. Jak wygladala praca krok po kroku.
5. Dane zrodlowe: realne dane, raw CSV, API, fallback cache.
6. Bronze / Silver / Gold w tym projekcie.
7. Architektura: Airflow -> SQL Server -> sem -> Streamlit.
8. ETL: extract, load staging, dimensions, fact, semantic views, quality checks.
9. Model gwiazdy: fakt, wymiary, ziarno, miary addytywne i nieaddytywne.
10. Dlaczego taki model, a nie jeden plaski plik albo jedna tabela.
11. Dlaczego geografia jest w `dim_store`.
12. Dlaczego jest `dim_packaging`.
13. Warstwa semantyczna: po co widoki `sem.*`.
14. Dashboard: co pokazuje kazda zakladka i jakie pytania biznesowe pokrywa.
15. Live demo: dokladna kolejnosc komend i co mowic.
16. Quality checks: po co sa i jak interpretowac wyniki.
17. Co jest po polsku, co zostaje po angielsku i dlaczego.
18. Gotowe odpowiedzi na trudne pytania.
19. Krotka wersja do powiedzenia w 3 minuty.
20. Dluga wersja do powiedzenia w 10-15 minut.

## Podzial pracy na subagentow

### Subagent 1: architektura, dane, ETL

Zadanie:

- opisac przeplyw danych od zrodla do hurtowni,
- opisac Bronze/Silver/Gold,
- opisac ETL i fallback cache,
- wskazac decyzje "dlaczego tak, nie inaczej".

Zakres plikow do czytania:

- `README.md`
- `docs/project_description.md`
- `docs/etl_description.md`
- `docs/pipeline_flow.md`
- `src/extract/socrata_extract.py`
- `src/run_initial_etl.py`
- `dags/iowa_liquor_etl_dag.py`

### Subagent 2: model, semantyka, pytania biznesowe

Zadanie:

- opisac model gwiazdy,
- opisac fakt, wymiary i ziarno,
- opisac miary,
- opisac warstwe semantyczna,
- powiazac to z pytaniami biznesowymi.

Zakres plikow do czytania:

- `docs/business_requirements.md`
- `docs/dimensional_model.md`
- `docs/model_wielowymiarowy_etap2.md`
- `docs/uzasadnienie_modelu.md`
- `docs/warstwa_semantyczna.md`
- `sql/03_create_dw_tables.sql`
- `sql/04_create_semantic_views.sql`

### Subagent 3: narracja obrony, pytania i nauka

Zadanie:

- ulozyc material jak lekcje,
- dodac "co powiedziec prowadzacej",
- dodac pytania i odpowiedzi,
- dodac wersje krotka i dluga prezentacji,
- wskazac gdzie student moze sie pomylic.

Zakres plikow do czytania:

- `docs/scenariusz_obrony_od_a_do_z.md`
- `docs/pytania_i_odpowiedzi_techniczne.md`
- `docs/live_demo_checklista.md`
- `docs/prezentacja_od_a_do_z.md`
- `app/streamlit_app.py`

## Plan wykonania

1. Utworzyc ten plan.
2. Uruchomic 3 subagentow rownolegle.
3. W czasie pracy subagentow przygotowac szkielet finalnego dokumentu.
4. Odebrac wyniki subagentow.
5. Zintegrowac tresc w jeden duzy dokument.
6. Sprawdzic, czy dokument pokrywa wszystkie wymagania.
7. Sprawdzic, czy nie ma sprzecznosci z aktualnym projektem.
8. Zrobic finalne podsumowanie dla uzytkownika.

## Kryteria gotowosci

Dokument jest gotowy, jezeli:

- osoba bez wiedzy startowej rozumie projekt,
- mozna z niego nauczyc sie obrony,
- tlumaczy "czemu tak" i "czemu nie inaczej",
- zawiera Bronze/Silver/Gold,
- zawiera ETL live,
- zawiera model gwiazdy,
- zawiera semantyke,
- zawiera dashboard,
- zawiera gotowe odpowiedzi na pytania,
- jest spójny z aktualnymi plikami projektu.
