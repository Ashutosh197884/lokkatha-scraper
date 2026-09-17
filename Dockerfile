FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ app/
COPY config.yaml .

# Non-root user; data dirs are created on demand by the storage layer.
RUN useradd --create-home crawler && chown -R crawler:crawler /app
USER crawler

ENV PYTHONUNBUFFERED=1

# Fly injects $PORT (default 8080).
CMD ["sh", "-c", "python -m app.api.run_server --host 0.0.0.0 --port ${PORT:-8080}"]
