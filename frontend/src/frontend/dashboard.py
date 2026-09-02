# dashboard.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: INGÅNGEN. Den enda filen som kör streamlit direkt.
# Läser widgets, ber api_client om data, lämnar över till charts.
# Ritar ingenting, känner inte till någon URL
#
# HELA filen körs vid VARJE interaktion. Tänk scriptet som en typ av "orchestrator".

import httpx
import streamlit as st

from frontend.api_client import build_params, get_by_century, get_by_type, get_health
from frontend.charts import century_chart, type_chart
from frontend.config import (
    ALL_CATALOGS,
    BACKEND_URL,
    CATALOG_CHOICES,
    PAGE_LAYOUT,
    PAGE_TITLE,
)

# set_page_config måste vara det första streamlit anropet i hela scriptet.
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
st.title(PAGE_TITLE)
st.caption(f"Backend: {BACKEND_URL}")

# ===== Kontroll av uppstart =====
# Om backend inte svarar är resten av sidan useless.
try:
    health = get_health()
except httpx.HTTPError as error:
    st.error(f"Backend is not reachable at: {BACKEND_URL}  {error}")
    st.stop()  # HELA körningen avbryts här och INGENTING under ritas


# ===== Filtrering =====
# selectbox ska returnera det valda värdet på just DEN HÄR körningen och BARA den här körningen.
# Ingen callback ska behövas då själva klicket ÄR HELA omkörningen.
catalog = st.sidebar.selectbox("Catalog", CATALOG_CHOICES)
body = None if catalog == ALL_CATALOGS else catalog
params = build_params(body=body)

st.sidebar.metric("Rows Loaded By Backend", health["rows"])

# ===== Innehåll =====
left, right = st.columns(2)

with left:
    st.subheader("Eclipses Per Century")
    century_chart(get_by_century(params))

with right:
    st.subheader("Eclipses Per Type")
    type_chart(get_by_type(params))
