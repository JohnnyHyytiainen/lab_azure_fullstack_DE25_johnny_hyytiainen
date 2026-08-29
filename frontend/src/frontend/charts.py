# charts.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: Klar data ska komma in, diagram ska ritas ut. Scriptet vet att streamlit och pandas existerar,
# vet ingenting om HTTPX, URLs eller vart datan kommer ifrån.
# Funktionernas enda syfte är att rita diagram, de returnerar ingenting öht därför -> None.

import pandas as pd
import streamlit as st

from frontend.config import ECLIPSE_TYPE_NAMES


# Funktion för en bartchart över århundraden.
def century_chart(rows: list[dict]) -> None:
    """
    Bar chart of eclipses per century.

    'century' is the FIRST year of the century.

    Example: 1676 -> 1670, -1996 -> -2000.
    Negative labels are correct and not a bug to be fixed.
    Tracking of eclipses goes to B.CE and are assigned as -YEAR.

    set_index puts the century to X-axis
    Without it Streamlit draws BOTH columns as bars, century included.
    """
    df = pd.DataFrame(rows)
    st.bar_chart(df.set_index("century")["count"])


# funktion för barchart av förmörkelse per TYP.
def type_chart(rows: list[dict]) -> None:
    """
    Bar chart of eclipses PER ECLIPSE TYPE with the single letter code translated.

    .map() replaces the code with a readable name without altering any numbers.
    .assign() returns a new DataFrame, the original remains UNCHANGED.
    Following the same logic and principles as data_processing.py in the backend.
    """
    df = pd.DataFrame(rows)
    readable = df.assign(eclipse_type=df["eclipse_type"].map(ECLIPSE_TYPE_NAMES))
    st.bar_chart(readable.set_index("eclipse_type")["count"])
