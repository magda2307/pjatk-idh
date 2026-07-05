[1mdiff --git a/data-warehouse-iowa-liquor/app/streamlit_app.py b/data-warehouse-iowa-liquor/app/streamlit_app.py[m
[1mindex 7ff7707..f978a86 100644[m
[1m--- a/data-warehouse-iowa-liquor/app/streamlit_app.py[m
[1m+++ b/data-warehouse-iowa-liquor/app/streamlit_app.py[m
[36m@@ -563,6 +563,13 @@[m [mdef render_q8():[m
 def render_q9():[m
     st.header("Q9: Które regiony miały wysoki wolumen, ale niższą wartość sprzedaży na litr?")[m
     show_semantic_sources(["vw_volume_vs_revenue"])[m
[32m+[m[32m    st.info([m
[32m+[m[32m        "**Jak interpretować tę analizę?**\n\n"[m
[32m+[m[32m        "Wartość sprzedaży na litr to stosunek `SUM(sale_dollars) / SUM(volume_sold_liters)` liczony dla każdego county. "[m
[32m+[m[32m        "Wysoki wolumen oznacza regiony znajdujące się w górnym kwartylu wolumenu, czyli od 75. percentyla wzwyż. "[m
[32m+[m[32m        "Tabela pokazuje więc county, które sprzedają dużo litrów, ale mają relatywnie niższą sprzedaż na 1 litr. "[m
[32m+[m[32m        "Może to oznaczać bardziej wolumenowy, tańszy lub mniej premium miks sprzedaży."[m
[32m+[m[32m    )[m
     df = read_view("vw_volume_vs_revenue")[m
     if df.empty:[m
         st.warning("Brak danych.")[m
