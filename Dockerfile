# Builds the MCP App and production Python runtime
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_COMPILE_FOR_BUILD=true \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy pyproject.toml and uv.lock for dependency resolution
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev --no-build-isolation 2>&1 || true

# Stage 2: Production runtime
FROM python:3.12-slim as runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python3.12/site-packages 2>/dev/null || true
COPY pyproject.toml ./
RUN pip install --no-cache-dir uvicorn[standard] fal pymongo cryptography fastmcp \
        httpx starlette pydantic-settings python-dotenv \
        && rm -rf /root/.cache

# Copy application source code
COPY app/ ./app/
COPY tests/ ./tests/ 2>/dev/null || true
COPY docs/ ./docs/ 2>/dev/null || true
COPY .env.example ./.env.example

# Create UI assets directory and copy Vue files if they exist
RUN mkdir -p /app/ui/dist && \
    if [ -d "app/ui" ]; then cp -r app/ui/*.vue /app/ui/dist/ 2>/dev/null || true; fi

# Set up logging directory
RUN mkdir -p /app/logs && \
    chown -R "$(whoami)" /app

# Configure environment variables
ENV HOST_HOST=${HOST:-0.0.0.0} \
    PORT_HOST=${PORT:-8000} \
    ENVIRONMENT=development \
    PUBLIC_URL=http://localhost:8000 \
    MONGODB_URI=mongodb://localhost:27017/mcp_storage \
    DATABASE_NAME=fal_mcp_keys \
    ALLOWED_ORIGINS=*

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health', timeout=5)" || exit 1

# Create and use non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "${HOST:-0.0.0.0}", "--port", "$PORT"]
