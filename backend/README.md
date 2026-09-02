# Backend - eClipseBord API

FastAPI service. Reads the processed Parquet once at startup and serves the eclipse data over
HTTP, with automatic docs at `/docs`.

- `constants.py` - paths, columns, enums, limits

- `data_processing.py` - load + schema check, filtering, aggregates

- `api.py` - endpoints: `/health`, `/eclipses`, `/stats/by-century`, `/stats/by-type`

> Run from the repo root: `uv run uvicorn backend.api:app --reload`

See the [root README](../README.md) for the full picture.