"""Compose Fal MCP, authenticated routes, middleware, and MongoDB lifespan."""

import asyncio
from contextlib import asynccontextmanager, suppress
import logging

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware as MCPMiddleware
from fastmcp.server.middleware import MiddlewareContext
from pymongo import AsyncMongoClient
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.auth import get_auth_provider
from app.config import settings
from app.connection_store import ConnectionStore, set_active_store
from app.license import license_watcher
from app.tools.fal_model import register_tool as register_fal_model
from app.twynity import register_routes
from app.usage import save_usage_report

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(server):
    mongo = AsyncMongoClient(settings.MONGODB_URI, tz_aware=True)
    license_task = None
    try:
        await mongo.admin.command("ping")
        store = ConnectionStore(
            mongo[settings.DATABASE_NAME]["project_connections"], settings.ENCRYPTION_KEY
        )
        await store.setup()
        set_active_store(store)
        if settings.LICENSE_ENFORCEMENT_ENABLED:
            license_task = asyncio.create_task(license_watcher())
        yield
    finally:
        if license_task is not None:
            license_task.cancel()
            with suppress(asyncio.CancelledError):
                await license_task
        set_active_store(None)
        await mongo.close()


mcp = FastMCP(
    settings.APP_TITLE,
    auth=get_auth_provider(),
    lifespan=app_lifespan,
)

register_fal_model(mcp)
register_routes(mcp)


class UsageTrackingMiddleware(MCPMiddleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        try:
            headers = get_http_headers()
            await save_usage_report(
                "TOOL_CALL",
                context.message.name,
                headers.get("authorization"),
            )
        except Exception:
            logger.exception("Usage tracking failed; continuing with tool call")
        return await call_next(context)


mcp.add_middleware(UsageTrackingMiddleware())

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
]

app = mcp.http_app(middleware=middleware)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
