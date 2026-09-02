# Frontend - eClipseBord Dashboard

Streamlit dashboard. Owns no data - it reads everything from the backend over HTTP.

- `config.py` - env vars, labels, page metadata

- `api_client.py` - HTTP to the backend

- `charts.py` - the charts (Plotly)

- `dashboard.py` - wires the widgets together


> Backend location comes from `BACKEND_URL` (fallback `http://localhost:8000`)

> Run from the repo root: `uv run streamlit run frontend/src/frontend/dashboard.py`

See the [root README](../README.md) for the full picture.