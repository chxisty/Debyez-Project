# ==============================================================================
# Aegis Knowledge System - Backend Dockerfile
# ==============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code, knowledge database, and dataset
COPY backend /app/backend
COPY data /app/data
COPY aegis-dataset /app/aegis-dataset

EXPOSE 8000

ENV PYTHONPATH=/app
ENV AEGIS_BACKEND_HOST=0.0.0.0
ENV AEGIS_BACKEND_PORT=8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

