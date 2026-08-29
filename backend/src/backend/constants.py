# constants.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: Ingen logik och ingen I/O. Menat att ligga längst ner i importkedjan och vara basen.
# Basen är grunden, allt ovanför basen importerar härifrån.

import os
from enum import StrEnum
from pathlib import Path

# ===== Pathing =====
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA_DIR = _PACKAGE_ROOT / "data" / "processed"

# Env variabel först, lokal folder som fallback. Frontend kommer använda samma mönster för backends URL.
# Koden ändras ALDRIG mellan lokalt, compose eller Azure, endast VARIABELN.
# test av att använda mig av 12 factor app methodology, ska göra så att kod lokalt hämtar från
# min folder struktur utan att behöva ändra EN ENDA RAD i när det är dags för docker och Azure
DATA_DIR = Path(os.getenv("ECLIPSE_DATA_DIR", str(_DEFAULT_DATA_DIR)))
# Ren data
PARQUET_FILES = {
    "solar": DATA_DIR / "solar.parquet",
    "lunar": DATA_DIR / "lunar.parquet",
}

# ===== Datamodellen ======
# Mina 9x cols som renskrevs och skapades ur EDA i ordning.
# Används vid uppstart för att kontrollera att fil på disk
# är den rätta filen.
EXPECTED_COLS = (
    "catalog_number",
    "calendar_date",
    "year",
    "eclipse_type",
    "saros_number",
    "latitude",
    "longitude",
    "magnitude",
    "body",
)


# Data enum för vilken katalog raden kommer ifrån
# LIKT data classes men här bygger jag ingen instans
# En enum används för att definiera en strikt och hardcoded lista med constants
class Body(StrEnum):
    """
    Enumeration for celestial bodies.

    Purpose:
    Restricts the allowed values to strictly 'solar' or 'lunar'
    to indicate which catalog rows originates from.
    """

    SOLAR = "solar"
    LUNAR = "lunar"


# Data enum för att kunna särskilja på vilken förmörkelsetyp det är
# LIKT data classes men här bygger jag ingen instans
# En enum används för att definiera en strikt och hardcoded lista med constants
class EclipseType(StrEnum):
    """
    Enumeration for different Eclipse types.

    Purpose of this Enum is to:
    Represent the first character of the 'Eclipse Type'
    column from NASAs catalogs, standardizing the event type
    """

    ANNULAR = "A"
    # Ringformig solförmörkelse, finns endast i solar katalogen
    HYBRID = "H"
    # Hybrid solförmörkelse, finns endast i solar katalogen
    PENUMBRAL = "N"
    # penumbral månförmörkelse(halvskugga), finns bara i lunar katalogen
    PARTIAL = "P"
    # Partiell förmörkelse(båda), finns i båda katalogerna
    TOTAL = "T"
    # Total förmörkelse(båda), finns i båda katalogerna


# ===== Hårda gränser =====
# MIN och MAX värden.
MIN_YEAR = -1999
MAX_YEAR = 3000

# Request limits(Rate limits(?))
# Skydd för om någon vill ha ut ALLA rader från båda datasetten PÅ EN GÅNG.
DEFAULT_LIMIT = 500
MAX_LIMIT = 5_000


# ===== METADATA för mitt API =====
API_TITLE = "eClipseBord - FastlyDep API"
API_DESCRIPTION = "Solar and Lunar eclipse data from NASAs five millenium catalogs."
API_VERSION = "0.1.0"
