FROM python:3.11-slim

# Install Pandoc for DOCX → Markdown conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
RUN pip uninstall -y torch nvidia-* 2>/dev/null; pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

COPY backend /app/backend
COPY rag_core /app/rag_core
COPY data /app/data
COPY .env.example /app/.env.example

# Install HTML renderer for OCR-first HTML flow (HTML -> PDF -> OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && (apt-get install -y --no-install-recommends wkhtmltopdf \
        || apt-get install -y --no-install-recommends chromium) \
    && rm -rf /var/lib/apt/lists/*

# Prefer chromium/chrome first, fallback to wkhtmltopdf
ENV OCR_RENDERER_HTML_PRIORITY=chrome,wkhtmltopdf
