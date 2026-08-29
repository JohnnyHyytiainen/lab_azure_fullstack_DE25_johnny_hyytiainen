# config.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: likadant som backend/constants.py så hör INGEN logik, INGEN I/O hemma här. Inga importer från projektet i helhet.
# Menat att ligga längst ner i importkedjan och vara basen för frontend, så högt upstream det bara går.
# Basen är grunden, allt ovanför basen importerar härifrån.
#

import os

# ===== Backend =====
# Environment variables(miljövariabler) allra först, lokal fallback FÖRST.
# Exakt samma mönster som ECLIPSE_DATA_DIR har i backend av samma skäl.
# Flödet är menat att vara local -> localhost, compose -> azure -> Public URL.
#
# r.strip("/") ska göra att både http://....:8000 och http://....:8000/ ska fungera,

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# Lägg till en request timeout inom "rimlig gräns"
REQUEST_TIMEOUT = 25.0

# ===== Presentation =====
# Backend står för kod och logik bakom
# Vad ECLIPSE_TYPE_NAMES heter för människor ska göra läsbart för människor också.
ECLIPSE_TYPE_NAMES = {
    "A": "Annular",
    "H": "Hybrid",
    "N": "Penumbral",
    "P": "Partial",
    "T": "Total",
}

# Katalogfiltret - Alla val i ALL_CATALOGS är en SENTINEL.
# Sentinel innebär 'skicka inget body-filter alls', dvs det är inte ett värde som backend känner till.
ALL_CATALOGS = "All"
CATALOG_CHOICES = (ALL_CATALOGS, "solar", "lunar")

# ===== Metadata för sidan =====
PAGE_TITLE = "eClipseBord"
PAGE_LAYOUT = "wide"
