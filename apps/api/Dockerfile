FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY apps/api/pyproject.toml ./apps/api/
RUN pip install --no-cache-dir -e "./apps/api[dev]"

# Copy application code
COPY apps/api/ ./apps/api/
COPY database/ ./database/

WORKDIR /app/apps/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
