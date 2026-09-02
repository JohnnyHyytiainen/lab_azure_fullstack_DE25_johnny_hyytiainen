# api.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: Vara det enda lagret som vet om att HTTP finns.
# constants.py vet INGENTING om något.
# data_processing.py kan pandas.
# api.py kan HTTP och är den som delegerar allt annat downstream för att följa SoC principer.
#
# Scriptet innehåller 4 delar i ordningen: Uppstart, svarsmodell, beroenden och till slut endpoints.
#

# ===== IMPORTS =====
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI, Query, Request
from pydantic import BaseModel

from backend.constants import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MAX_YEAR,
    MIN_YEAR,
    Body,
    EclipseType,
)
from backend.data_processing import (
    count_by_century,
    count_by_type,
    filter_eclipses,
    load_dataset,
)


# ===== Uppstart och avstängning =====
# Decorator för lifespan med yield.
# Menat att köras EN GÅNG före requests och sen stängas av fint.
# Allt ovanför yield är start och allt under min yield är för shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async function - that requires contextmanager protocol.
    This function runs before upstart and any requests.
    """
    app.state.eclipses = load_dataset()  # Körs endast en gång före requests börjar
    yield
    app.state.eclipses = None  # körs vid shutdown.


# Själva appen
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)


# ===== Pydantic response models =====
# Använder pydantics Basemodels
class Health(BaseModel):
    """
    Health answer, class is also used to confirm that the datasets are loaded.
    """

    status: str
    rows: int


class Eclipse(BaseModel):
    """
    One row from NASAs catalogs.
    """

    catalog_number: int
    calendar_date: str
    year: int
    eclipse_type: EclipseType
    saros_number: int
    latitude: float
    longitude: float
    magnitude: float
    body: Body


class EclipsePage(BaseModel):
    """
    One page of Eclipse rows plus how many that matched in total.

    total = number of hits in the ENTIRE dataset.
    count = number of hits in this SPECIFIC response.

    The difference is what allows the serving layer(dashboard)
    to display '450 of 12 064'.
    """

    total: int
    count: int
    offset: int
    items: list[Eclipse]


class CenturyCount(BaseModel):
    """
    One bar in the eclipses per century chart
    """

    century: int
    count: int


class TypeCount(BaseModel):
    """
    One bar in the eclipses per type chart
    """

    eclipse_type: EclipseType
    count: int


# ===== BEROENDEN - Dependencies =====
# Funktion för att hämta lämna över DataFrame
def get_dataset(request: Request) -> pd.DataFrame:
    """
    Hands the endpoint the Dataframe that lifespan-function loaded at startup.
    """
    return request.app.state.eclipses


@dataclass
class EclipseFilters:
    """
    The four query params shared by EVERY data endpoint
    """

    body: Annotated[Body | None, Query(description="Which Catalog To Read")] = None
    eclipse_type: Annotated[EclipseType | None, Query(description="Eclipse Type")] = (
        None
    )
    year_from: Annotated[int | None, Query(ge=MIN_YEAR, le=MAX_YEAR)] = None
    year_to: Annotated[int | None, Query(ge=MIN_YEAR, le=MAX_YEAR)] = None


# ===== Shortcuts så att mina endpoint signaturer är LÄSBARA =====
DatasetDependency = Annotated[pd.DataFrame, Depends(get_dataset)]
FiltersDependency = Annotated[EclipseFilters, Depends()]


# ===== ENDPOINTS FÖR MITT API =====
# Root endpoint
@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """
    Root endpoint. Gives a basic, friendly greeting and points towards docs/.
    """
    return {
        "message": "Welcome to the eClipseBord API",
        "documentation": "/docs",
        "health_status": "/health",
    }


# Endpoint för att göra health checks
@app.get("/health", response_model=Health, tags=["meta"])
def health(df: DatasetDependency) -> Health:
    """
    Endpoint to report health status to make sure service is up and running + how many rows its serving.
    Rows are included by design. Responds and Have Data are two separate things.
    """
    return Health(status="ok", rows=len(df))


# Endpoint för att att lista eclipses
@app.get("/eclipses", response_model=EclipsePage, tags=["eclipses"])
def list_eclipses(
    df: DatasetDependency,
    filters: FiltersDependency,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EclipsePage:
    """
    Returns one page of eclipses matching the filters.

    asdict() breaks down the dataclass into keyword arguments so that
    filter_eclipses dont need to know that FastAPI even exists.
    """
    matches = filter_eclipses(df, **asdict(filters))
    page = matches.iloc[offset : offset + limit]

    return EclipsePage(
        total=len(matches),
        count=len(page),
        offset=offset,
        items=page.to_dict(orient="records"),
    )


# Endpoint för att räkna matchande förmörkelser per århundraden
@app.get("/stats/by-century", response_model=list[CenturyCount], tags=["stats"])
def stats_by_century(
    df: DatasetDependency, filters: FiltersDependency
) -> list[CenturyCount]:
    """
    Counts matching Eclipses per CENTURY in dataset.
    """
    matches = filter_eclipses(df, **asdict(filters))
    return count_by_century(matches).to_dict(orient="records")


# Endpoint för att räkna matchande förmörkelser per TYP
@app.get("/stats/by-type", response_model=list[TypeCount], tags=["stats"])
def stats_by_type(df: DatasetDependency, filters: FiltersDependency) -> list[TypeCount]:
    """
    Counts matching eclipses PER different eclipse type.
    """
    matches = filter_eclipses(df, **asdict(filters))
    return count_by_type(matches).to_dict(orient="records")
