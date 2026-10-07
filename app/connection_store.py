"""Encrypted MongoDB storage, strictly scoped to a user/persona pair."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from cryptography.fernet import Fernet, InvalidToken
from pymongo import ASCENDING


_active_store: "ConnectionStore | None" = None


def set_active_store(store: "ConnectionStore | None") -> None:
    global _active_store
    _active_store = store


def get_active_store() -> "ConnectionStore | None":
    return _active_store


class ConnectionStore:
    """Store encrypted connector values for exactly one Twynity project."""

    def __init__(self, collection: Any, encryption_key: str):
        self.collection = collection
        self.cipher = Fernet(encryption_key.encode("ascii"))

    async def setup(self) -> None:
        await self.collection.create_index(
            [("user_id", ASCENDING), ("persona_id", ASCENDING)], unique=True
        )

    async def save(self, user_id: str, persona_id: str, values: dict[str, str]) -> None:
        now = datetime.now(UTC)
        encrypted = {
            field: self.cipher.encrypt(value.encode("utf-8")).decode("ascii")
            for field, value in values.items()
        }
        await self.collection.update_one(
            {"user_id": user_id, "persona_id": persona_id},
            {
                "$set": {"values": encrypted, "modified": now},
                "$setOnInsert": {"created": now},
            },
            upsert=True,
        )

    async def get(self, user_id: str, persona_id: str) -> dict[str, str] | None:
        document = await self.collection.find_one(
            {"user_id": user_id, "persona_id": persona_id}
        )
        if not document:
            return None
        try:
            return {
                field: self.cipher.decrypt(value.encode("ascii")).decode("utf-8")
                for field, value in document.get("values", {}).items()
            }
        except (InvalidToken, KeyError, TypeError) as exc:
            raise RuntimeError("Stored credentials cannot be decrypted; check ENCRYPTION_KEY") from exc

    async def public_metadata(self, user_id: str, persona_id: str) -> dict[str, Any] | None:
        document = await self.collection.find_one(
            {"user_id": user_id, "persona_id": persona_id},
            {"values.name": 1, "created": 1, "modified": 1},
        )
        if not document:
            return None
        values = document.get("values", {})
        safe_values: dict[str, str] = {}
        for field in ("name",):
            encrypted = values.get(field)
            if encrypted:
                safe_values[field] = self.cipher.decrypt(encrypted.encode("ascii")).decode("utf-8")
        return {
            "id": str(document.get("_id", ObjectId())),
            **safe_values,
            "created": document.get("created").isoformat() if document.get("created") else None,
            "modified": document.get("modified").isoformat() if document.get("modified") else None,
        }
