# Builds the MCP App and production Python runtime. Update the UI COPY paths
# when renaming the example; generated dist/ files stay out of source control.
FROM node:22-alpine AS ui-builder

WORKDIR /ui

COPY app/ui/frappe_ui/package.json ./
RUN npm ci --no-audit --no-fund

COPY app/ui/frappe_ui/index.html \
     app/ui/frappe_ui/vite.config.ts \
     app/ui/frappe_ui/tsconfig.json \
     app/ui/frappe_ui/App.vue \
     app/ui/frappe_ui/*.css \
     ./

RUN npm run build


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

# Copy built UI assets from frappe_ui dist folder
COPY --from=ui-builder /ui/dist /app/ui/frappe_ui/dist

# Create and use non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:mcp", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
