"""Encrypted API key storage per (user_id, persona_id) pair."""

from datetime import UTC, datetime
from typing import Any, Optional
from cryptography.fernet import Fernet


class ConnectionStore:
    """MongoDB-backed encrypted API key storage."""

    def __init__(self, collection, encryption_key):
        self.collection = collection
        self.cipher = Fernet(encryption_key.encode("ascii"))

    async def setup(self) -> None:
        """Create compound unique index on (name, user_id) to prevent duplicate keys."""
        import pymongo
        await self.collection.create_index(
            [("name", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], 
            unique=True
        )

    async def save_api_key(self, name: str, key_value: str, user_id: str = None) -> dict[str, Any]:
        """Encrypt and store API key for (user_id, name) pair.
        
        Args:
            name: Source name (e.g., "GitHub PAT")
            key_value: The raw API key to encrypt
            user_id: Optional user identifier from auth
            
        Returns:
            {"status": "saved|updated"}
        """
        now = datetime.now(UTC)
        
        # Encrypt the key value before storage
        encrypted_api_key = self.cipher.encrypt(key_value.encode("utf-8")).decode("ascii")
        
        query = {"name": name}
        
        if user_id:
            # Update or insert for specific user
            result = await self.collection.update_one(
                query,
                {
                    "$setOnInsert": {
                        "user_id": str(user_id),
                        "persona_id": "_default_",
                        "created": now,
                    },
                    "$set": {"value": encrypted_api_key, "modified": now},
                },
                upsert=True
            )
        else:
            # Legacy behavior: just store by name (simplified)
            result = await self.collection.find_one_and_update(
                query,
                {
                    "$set": {
                        "user_id": str(__import__('bson').ObjectId()),
                        "persona_id": "_default_",
                        "value": encrypted_api_key,
                        "modified": now,
                    }
                },
                upsert=True
            )
        
        return {"status": "saved"}

    async def get_api_key(self, name: str) -> dict[str, Any] | None:
        """Retrieve and decrypt the stored API key.
        
        Args:
            name: Service name to look up
            
        Returns:
            {{"name": str, "key": str}} or None if not found
        """
        document = await self.collection.find_one({"name": name})
        
        if not document:
            return None
        
        try:
            # Decrypt and return clean result (without internal storage structure)
            api_key = self.cipher.decrypt(document.get("value", "").encode("ascii")).decode("utf-8")
            
            return {"name": name, "key": api_key}
        except Exception as exc:
            raise RuntimeError(f"Failed to decrypt key {name}") from exc
