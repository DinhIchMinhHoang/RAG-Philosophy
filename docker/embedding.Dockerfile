FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/app
ENV HF_HOME=/cache/huggingface
ENV TRANSFORMERS_CACHE=/cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/cache/huggingface

WORKDIR /app

ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

# Pre-install torch from an explicit index so the default image stays CPU-only,
# while docker-compose.gpu.yml can switch the embedding service to a CUDA wheel.
RUN pip install --upgrade pip \
    && pip install torch --index-url "${TORCH_INDEX_URL}" --no-cache-dir

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY embedding_service /app/embedding_service

WORKDIR /app/embedding_service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
