"""MCP tool for invoking a fal.ai model with the active project's credentials."""

from typing import Any

from fastmcp import FastMCP

from app.config import settings
from app.tools.connection import get_current_connection
from app.tweenit import FalApiClient


def register_tool(mcp: FastMCP) -> None:
    @mcp.tool()
    async def invoke_fal_model(
        model_id: str = settings.DEFAULT_FAL_MODEL,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a fal.ai model using the API key configured for this project.

        Use the model's exact fal.ai endpoint ID and pass its documented input
        fields in arguments. Configure credentials through Twynity first.
        """
        connection = await get_current_connection()
        api_key = connection.get("api_key", "")
        if not api_key:
            raise ValueError("The configured fal.ai connection has no API key")
        result = await FalApiClient().invoke(api_key, model_id, arguments or {})
        return {"model_id": model_id, "result": result}
