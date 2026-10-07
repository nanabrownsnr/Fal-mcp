# fal.ai Model API Reference — Integration Guide

## Overview

This section documents how to use the `fal_mcp` server with [fal.ai](https://fal.ai)'s Model API.

### Example Call

```python
from fal import Client

client = Client()
result = client.invoke(
    model="fal-ai/llama3",  # Choose any supported model
    input={
        "prompt": "Write a haiku about AI",
        "num_samples": 1,
    },
)
return result["output"]
```

### Supported Models

Visit [fal.ai Models](https://fal.ai/models) to see available models. All require API key authentication via fal's `/api/v1/keys` endpoint.

## Storage Contract

API keys are stored per `(user_id, persona_id)` pair in an encrypted MongoDB collection. Each user gets their own secure key for each service they register.

### Storing a Key

**POST /api/v1/keys**

```json
{
  "name": "GitHub-PAT",
  "key": "ghp_xxxxxxxxxxxxxxxxxxxxxx"
}
```

### Retrieving a Key

The server decrypts and returns the key for use in tool calls via `fal.call()` or direct Python import.

## Twynity Deployment Notes

- The server verifies JWT bearer tokens using account-service JWKS
- Keys are stored encrypted with Fernet (use `.env` to generate)  
- Always forward `Persona-Id` header when calling from UI apps

---

See [fal.ai Playground](https://fal.ai/playground) for quick model test examples.
