# api_client.py
# Kod: Engelska
# Kommentarer: Svenska
#
# Syfte: Enda lagret som vet om min backends existens och att HTTP finns.
# Inga streamlit importer här, varje funktion ska gå att köra i REPL vid behov utan att starta en sida.
# Samma tankeprocess som backend/data_processing.py har i backend.
#
from typing import Any
import httpx

from frontend.config import BACKEND_URL, REQUEST_TIMEOUT


# Privat funktion - FAAFO
def _get(path: str, params: dict[str, str] | None = None) -> Any:
    """
    The only place that performs an HTTP call.

    Base URL, timeout and status handling lives here and nowhere else.
    Function is private by convention, every endpoint function below this one goes through it.

    raise_for_status turns 400 and 500 responses into an error right here, IMMEDIATELY.
    Without it, the code proceeds with an error body as if it were data and the error
    only shows up later in pandas with a message about the wrong thing. FAIL LOUD, FAIL FAST logic.
    """
    response = httpx.get(f"{BACKEND_URL}{path}", params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


# Funktion för att bygga mina query strings(params).
def build_params(body: str | None = None) -> dict[str, str]:
    """
    Builds the entire query string from the Active filters ONLY.

    A filter that is None must NOT be sent AT ALL.
    httpx encodes None values as an empty value and
    '?body=' is NOT a valid enum member for the API (a 422 error).

    Every filter added later becomes one more if statement here and
    NOT a new argument at different call sites.
    """
    params: dict[str, str] = {}
    if body is not None:
        params["body"] = body
    return params


# ===== En funktion PER endpoint! =====
# Meningen: URL-strings finns på exakt EN plats i hela frontend
# Byter backend namn på en endpoint så ändras endast EN RAD, I _EN_ FIL!
# Hämtar min end health endpoint.
def get_health() -> dict[str, Any]:
    """
    Startup Returns {'status': str, 'rows': int}
    """
    return _get("/health")


# Hämtar min by-century endpoint
def get_by_century(params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """
    Ready made chart serie: [{'century': int, 'count': int}]
    """
    return _get("/stats/by-century", params)


# Hämtar min by-type endpoint
def get_by_type(params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """
    Ready made chart serie: [{'eclipse_type': str, 'count': int}]
    """
    return _get("/stats/by-type", params)
