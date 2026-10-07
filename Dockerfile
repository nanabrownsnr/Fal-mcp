# Stage 1: Build stage - install dependencies and copy source
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_COMPILE_FOR_BUILD=true \
    UV_LINK_MODE=copy

# Install Python dependencies with uv (or pip)
COPY pyproject.toml .
RUN if [ ! -f "venv" ]; then pip install uv; fi && \
    python -m venv /app/venv

# Stage 2: Final runtime image
FROM python:3.12-slim

WORKDIR /app

# Copy venv from builder or create new
COPY --from=builder /app/venv /app/venv

ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Copy source code and dependencies - copy everything except hidden files
RUN mkdir -p /app && cp -r app/ tests/ docs/ /app/. 2>&1 >/dev/null || true

# Install runtime dependencies only (no dev deps)
COPY pyproject.toml .
RUN pip install --prefix=/app --no-warn-script-location -e '.' 2>/dev/null || \
    pip install --prefix=/app --no-warn-script-location \
        "cryptography>=50.0.1" \
        "fastmcp==3.4.5" \
        "fal" \
        "httpx==0.28.1" \
        "pydantic-settings==2.14.2" \
        "python-dotenv==1.2.2" \
        "pymongo>=4.18.0" \
        "starlette==1.3.1" \
        "uvicorn==0.51.0" 2>/dev/null || true

# Set environment configuration from build args and env vars
ARG HOST=${HOST:-0.0.0.0} \
    PORT=${PORT:-8000} \
    DATABASE_NAME=${DATABASE_NAME:-fal_mcp_keys} \
    ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}

ENV HOST=${HOST} \
    PORT=${PORT} \
    MONGODB_URI=${MONGODB_URI:-mongodb://localhost:27017} \
    DATABASE_NAME=${DATABASE_NAME} \
    ALLOWED_ORIGINS=${ALLOWED_ORIGINS}

# Copy UI assets only if directory exists (ignore errors)
RUN mkdir -p /app/frontend/assets && cp -r app/ui/* /app/frontend/assets/ 2>/dev/null || true

# Non-root user for security
RUN useradd --create-home --shell /bin/bash faluser && \
    chown -R faluser:faluser /app

USER faluser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "0.0.0.0", "--port", "$PORT"]
