"""Call fal.ai models with the API key for the active project."""

import asyncio
from typing import Any

from fal_client import SyncClient


class FalApiClient:
    """Small async adapter over fal-client's synchronous API."""

    async def invoke(self, api_key: str, model_id: str, arguments: dict[str, Any]) -> Any:
        if not model_id or len(model_id) > 200:
            raise ValueError("model_id must be a non-empty model endpoint ID")
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be a JSON object")

        def call() -> Any:
            client = SyncClient(api_key)
            return client.subscribe(model_id, arguments)

        return await asyncio.to_thread(call)
