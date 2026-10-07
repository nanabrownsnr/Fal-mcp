"""Best-effort forwarding of authenticated MCP tool usage reports."""

from datetime import UTC, datetime
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def save_usage_report(method: str, endpoint: str, authorization: str | None) -> None:
    if not settings.USAGE_REPORT_ENDPOINT or not authorization:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                settings.USAGE_REPORT_ENDPOINT,
                json={
                    "service": settings.SERVICE_ID,
                    "method": method,
                    "endpoint": endpoint,
                    "timestamp": datetime.now(UTC).timestamp(),
                },
                headers={"Authorization": authorization},
            )
    except (httpx.HTTPError, ValueError):
        logger.warning("Usage report could not be sent", exc_info=True)
