# Builds the MCP App and production Python runtime using Vite for frontend
FROM node:22-alpine AS ui-builder

WORKDIR /ui

# Install Node dependencies and build UI with Vite
COPY app/ui/package.json app/ui/package-lock.json ./ 2>/dev/null || true
RUN npm ci --no-audit --no-fund 2>/dev/null || echo "No node modules to install"

COPY app/ui/index.html \
     app/ui/vite.config.ts \
     app/ui/tsconfig.json \
     app/ui/*.vue \
     app/ui/src/ ./src/ 2>/dev/null || true

RUN npm run build \
  && cp -r app/ui/dist/* /ui/


FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./ 2>/dev/null || true

RUN uv sync --locked --no-dev 2>&1 || pip install -e . && pip install fal pymongo cryptography fastmcp uvicorn[standard] httpx starlette pydantic-settings python-dotenv

# Copy application source code
COPY app/ ./app/
COPY tests/ ./tests/ 2>/dev/null || true
COPY docs/ ./docs/ 2>/dev/null || true

# Copy built UI assets
COPY --from=ui-builder /ui/dist /app/frontend/assets

# Create and use non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
