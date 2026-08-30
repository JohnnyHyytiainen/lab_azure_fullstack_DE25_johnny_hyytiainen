# backend.dockerfile
# Kod: Engelska
# Kommentarer: Svenska
#
# Byggs ALLTID med repos root som kontext.
# . <-- Punkten i slutet är kontexten. Sökvägarna under är RELATIVA TILL PUNKTEN
# och inte till den här filen.
# docker build -f dockerfiles/backend.dockerfile -t eclipsebord-backend:dev .

# Officiell uv image med python 3.13 inbyggd, slipper installera uv för hand i imagen helt.
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# working directory
WORKDIR /app

# Det uv behöver för att kunna lösa sina beroenden
# lockfilen ligger i root och gäller för HELA workspacet, därför måste kontext vara root
COPY pyproject.toml uv.lock ./

# Saknas README.md i backend failar hela bygget. backend/pyproject.toml declares readme = "README.md"
# och build motorn läser från den filen. Saknas README.md dör hela bygget och orsakar "failed to open file" errors
COPY backend/pyproject.toml backend/README.md ./backend/

# ===== KOD OCH DATA =====
COPY backend/src ./backend/src
COPY backend/data/processed ./backend/data/processed

# ===== INSTALLATION AV DEPS =====
# Tack vare valet av officiell image behöver jag ej skriva in "RUN pip install --no-cache-dir uv"
# --package backend = bygg BARA den här medlemmen, utan den installeras hela mitt workspace och image får onödiga deps
#
# --frozen = vägrar om uv.lock INTE MATCHAR pyproject filerna
#
# --no-dev = hoppar över roots dev-group (ipykernel, ruff, pandas för min EDA)
RUN uv sync --package backend --frozen --no-dev

# Lägger VENVs bin-folder först i PATH, så uvicorn hittas direkt utan att behöva köra "uv run" framför.
ENV PATH="/app/.venv/bin:$PATH"

# Data ska följa med i image, variabeln gör så att koden inte behöver veta vart datan hamnade
ENV ECLIPSE_DATA_DIR=/app/backend/data/processed

# Dokumentation bara, öppnar ingen port, mappning av portar görs vid körning
EXPOSE 8000

# --host 0.0.0.0 gör att den lyssnar på all nätverks interface i containern
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]