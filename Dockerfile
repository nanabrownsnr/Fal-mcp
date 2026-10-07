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

# Copy source code and dependencies
COPY pyproject.toml uv.lock* .[^.]* 2>*requirements.txt*.txt ./
COPY app/ tests/ docs/ .

# Install runtime dependencies only (no dev deps)
RUN pip install --no-deps -c "/app/pyproject.toml" -r requirements.txt 2>/dev/null || true

# Set environment configuration
ENV HOST=0.0.0.0 \
    PORT=8000 \
    MONGODB_URI=mongodb://mongo:27017 \
    DATABASE_NAME=fal_mcp_keys \
    ALLOWED_ORIGINS=*

# Copy UI assets (if any) - from template pattern
COPY app/ui/ frontend/assets/ 2>/dev/null || true

# Non-root user for security
RUN useradd --create-home --shell /bin/bash faluser && \
    chown -R faluser:faluser /app && \
    chmod -R 600 logs/ *.key 2>/dev/null || true

USER faluser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "0.0.0.0", "--port", "$PORT"]
