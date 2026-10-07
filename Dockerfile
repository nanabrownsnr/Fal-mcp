# Stage 1: Build dependencies with uv
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_FOR_BUILD=true
UV_LINK_MODE=copy

# Copy lock file and pyproject.toml
COPY pyproject.toml uv.lock* ./

# Install dependencies into base Python installation (no venv for runtime)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e . --break-system-packages 2>&1 || true

# Stage 2: Runtime image
FROM python:3.12-slim as runtime

WORKDIR /app

# Install production dependencies into /usr/local/lib/python* (not virtualenv)
RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages 2>/dev/null || true
COPY pyproject.toml .
RUN pip install --no-cache-dir uvicorn[standard] fal pymongo cryptography fastmcp \
        httpx starlette pydantic-settings python-dotenv \
        && rm -rf /root/.cache

# Copy application source code
COPY app/ ./app/
COPY tests/ ./tests/ 2>/dev/null || true
COPY docs/ ./docs/ 2>/dev/null || true
COPY .env.example ./.env.example

# Create app directory and copy UI if exists
RUN mkdir -p /app/frontend/assets && \
    if [ -d "app/ui" ]; then cp -r app/ui/* /app/frontend/assets/ 2>/dev/null || true; fi

# Copy UI component Vue file (not the whole ui folder)
COPY app/ui/*.vue /app/frontend/assets/ 2>/dev/null || true

# Create virtual environment for optional local development or fallback
RUN python -m venv /app/venv

# Set up logging directory
RUN mkdir -p /app/logs && \
    chown -R "$(whoami)" /app

# Configure environment variables (no shell commands or complex expressions)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build-time args (can be overridden at build/runtime)
ARG HOST=0.0.0.0 PORT=8000 ENVIRONMENT=development \
PUBLIC_URL=http://localhost:8000 MONGODB_URI=mongodb://localhost:27017/dummy DATABASE_NAME=fal_mcp_keys ALLOWED_ORIGINS=*

# Set runtime environment from args or build-time env vars  
ENV HOST=${HOST:-0.0.0.0} \
    PORT=${PORT:-8000} \
    ENVIRONMENT=${ENVIRONMENT:-development} \
    PUBLIC_URL=${PUBLIC_URL:-http://localhost:8000} \
    MONGODB_URI=${MONGODB_URI:-mongodb://localhost:27017/mcp_storage} \
    DATABASE_NAME=${DATABASE_NAME:-fal_mcp_keys} \
    ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}

# Set health check (works with /api/v1/health and /api/v1/status endpoints)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health', timeout=5)" || exit 1

# Run as non-root user for security
RUN useradd --create-home --shell /bin/bash faluser && \
    chown -R faluser:faluser /app

USER faluser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "${HOST:-0.0.0.0}", "--port", "$PORT"]
