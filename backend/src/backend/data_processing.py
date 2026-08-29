# data_processing.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: Processera data, DataFramen laddas EN GÅNG och delas sen av varje request.
# Ren pandas logik, ingen FastAPI import här, allting i scriptet ska gå att köra i REPL utan att starta en server.
#
# Regel att hålla mig efter: Ingen funktion här får ÄNDRA i DataFramen den fick in.
#
# DRY i den meningen att jag skiljer på filtrering och aggregat.
# Aggregat tar emot ett redan filtrerat resultat.

from pathlib import Path
import pandas as pd
from backend.constants import EXPECTED_COLS, PARQUET_FILES, Body, EclipseType

# ===== Läsning, körs EN gång vid uppstart =====


# priv funktion - FAAFO
def _read_catalog(path: Path) -> pd.DataFrame:
    """
    Read one .parquet catalog and verifies that it matches the expected schema.

    A missing file is a startup error and not an empty search result.
    Preferring to raise an Exception here so the process dies LOUD and DIRECTLY rather
    than returning empty DataFrame that looks like 'no hits' to every visitor.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing Data File: {path}")

    df = pd.read_parquet(path)

    # Kontroll mot EXPECTED_COLS är billig att köra en gång.
    # Hellre högljudd och direkt krasch än tyst och ingen krasch!
    missing = [column for column in EXPECTED_COLS if column not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing the expected columns: {missing}")

    # Returnerar de förväntade columns(9x) i redan förbestämd ordning via constants.py.
    # Smyger en extra column in senare följer den INTE med ut i API't av misstag
    return df[list(EXPECTED_COLS)]


# Funktion för att ladda datasettet och min data
def load_dataset() -> pd.DataFrame:
    """
    Function which only purpose is:

    To loads every catalog into a single DataFrame, nothing more, nothing less.

    ignore_index=True produces a continual index across entire dataset.
    The catalogs own catalog_number values restart at 1 in each file and are not considered unique.

    This way when the files are merged the catalog_number acts as a reference and NOT a KEY.
    """
    frame = [_read_catalog(path) for path in PARQUET_FILES.values()]
    return pd.concat(frame, ignore_index=True)


# ===== FILTRERING =====


# Funktion för att filtrera mina eclipses
def filter_eclipses(
    df: pd.DataFrame,
    body: Body | None = None,
    eclipse_type: EclipseType | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> pd.DataFrame:
    """
    Function to return the rows matching the given filters, each filter is OPTIONAL.

    Purpose of function:
    A boolean mask that starts as 'all true' and is narrowed down by each active filter.
    Rewriting 'df=df[]' at each step makes the every filter depending on the order.
    Using a bolean mask will let it be the filtering be independent and a new filter will
    just become one more line of code.
    """
    mask = pd.Series(True, index=df.index)
    # &= jämför position för position där båda är True blir resultatet True
    # &= används istället för att t.ex skriva mask = mask & new_mask
    if body is not None:
        mask &= df["body"] == body.value
    if eclipse_type is not None:
        mask &= df["eclipse_type"] == eclipse_type.value
    if year_from is not None:
        mask &= df["year"] >= year_from
    if year_to is not None:
        mask &= df["year"] <= year_to

    # Tack vare masken skapar jag en lång lista med True/False som df.loc[mask] enkelt kan
    # applicera EN ENDA GÅNG i i slutet då .loc bara returnerar bara ett urval som aldrig gör ändringar i originalet.
    # Genom .loc[] undviker jag SettingWithCopyWarning i pandas då jag inte modifierar originalet öht.
    return df.loc[mask]


# ===== Aggregeringar för frontend =====


# Funktion för att räkna antal förmörkelser per århundraden
def count_by_century(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to Count eclipses per century.

    Using integer division by 100 yields the first year
    of the century: 1987 -> 1900.

    For negative years rounds downwards which is the correct direction,
    -1999 becomes -2000

    .rename() sets the column name in the final result,
    without it the column would be named 'year' and that would be misleading.
    """
    centuries = ((df["year"] // 100) * 100).rename("century")
    return centuries.value_counts().sort_index().reset_index()


# Funktion för att räkna per förmörkelse TYP
def count_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Counts eclipses per eclipse TYPE.
    """
    return df["eclipse_type"].value_counts().sort_index().reset_index()
