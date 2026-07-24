FROM python:3.11-slim

# System deps needed for psycopg2 build + Playwright's browser runtime
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installs the Chromium binary + its OS-level dependencies (fonts, libs, etc.)
RUN playwright install --with-deps chromium

COPY . .

# Render sets $PORT at runtime; default to 8000 for local runs
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]