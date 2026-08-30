# frontend.dockerfile
# Kod: Engelska
# Kommentarer: Svenska
#
# Byggs ALLTID med repos root som kontext precis som backend.dockerfile.
# . <-- Punkten i slutet är kontexten. Sökvägarna under är RELATIVA TILL PUNKTEN
# och inte till den här filen.
# docker build -f dockerfiles/frontend.dockerfile -t eclipsebord-frontend:dev .
#

# Officiell uv image med python 3.13 inbyggd, slipper installera uv för hand i imagen helt.
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# working directory
WORKDIR /app

# Samma lockfil som backend. EN lockfil för HELA workspace. Det garanterar att båda images får EXAKT samma pandas version
COPY pyproject.toml uv.lock ./



# ===== KOD  =====
COPY frontend/pyproject.toml frontend/README.md ./frontend/
COPY frontend/src ./frontend/src

# ===== INSTALLATION AV DEPS =====
# Tack vare valet av officiell image behöver jag ej skriva in "RUN pip install --no-cache-dir uv"
#
# --frozen = vägrar om uv.lock INTE MATCHAR pyproject filerna
# --no-dev = hoppar över roots dev-group (ipykernel, ruff, pandas för min EDA)
# --package frontend = streamlit, plotly, httpx, pandas. INGEN fastapi, INGEN uvicorn.
RUN uv sync --package frontend --frozen --no-dev

# Lägger VENVs bin-folder först i PATH, så uvicorn hittas direkt utan att behöva köra "uv run" framför.
ENV PATH="/app/.venv/bin:$PATH"


# Ingen data för frontend, frontend hämtar allt över HTTP requests.
# INGEN BACKEND_URL sätts heller, för jag in den i min image blir imagen docker-compose.yml specifik och
# oanvändbar i Azure. Värdet SKA komma UTIFRÅN. Varje gång.
EXPOSE 8501

# --server.address=0.0.0.0 gör att den lyssnar på all nätverks interface i containern, samma skäl som backends uvicorn --host
# --Server.headless=true stänger av försök att öppna browser och email frågan vid första start. 
# (Det finns ingen browser ELLER tangentbord i en container lol.)
CMD ["streamlit", "run", "frontend/src/frontend/dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]