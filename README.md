# Fal MCP — AI Model API Caller

A FastMCP server for calling AI models via the [fal.ai](https://fal.ai) API.

## What this server does

- Stores encrypted API keys per user/persona in MongoDB
- Provides tools to call fal.ai's model endpoints
- Simple UI for viewing tool responses
- Twynity-compatible authentication model

## Quick Start

1. Copy `.env.example` to `.env` and fill in:
   - `MONGODB_URI`: Your database connection string
   - `MONGODB_DATABASE`: Database name (e.g., `fal_mcp_keys`)
   - `ENCRYPTION_KEY`: Run the Python command below

2. Generate a Fernet encryption key:
   ```bash
   uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. Install dependencies and run:
   ```bash
   uv sync --locked
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Keys Storage

Store your fal.ai (and other services) API keys securely in MongoDB, encrypted per `(user_id, persona_id)` pair.

### Store a Key

```bash
curl -X POST http://localhost:8000/api/v1/keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Persona-Id: your-persona-id" \
  -d '{
    "name": "GitHub-PAT",
    "key": "ghp_xxxxxxxxxxx"
  }'
```

### Use the Tool

Call fal.ai via the MCP tool (from VS Code extension or other client). Your API key is resolved automatically.

## fal.ai Model API Reference

- [fal.ai Model API](https://fal.ai/docs/model-api-reference)
- [fal.ai Playground](https://fal.ai/playground) for testing

## Project Structure

```
FalMCP/
├── app/
│   ├── auth.py              # JWT verification
│   ├── config.py            # Settings and logging
│   ├── connection_store.py  # Encrypt storage per (user, persona)
│   ├── twynity.py          # HTTP routes for key management
│   ├── main.py             # Server entry point
│   └── say_hello.py        # Example tool
├── tests/                   # Pytest test suite
├── app/ui/                  # MCP App UI resources
├── pyproject.toml          # Dependencies and tool config
├── README.md               # This file
└── .env.example            # Environment template
```

## License

MIT — See LICENSE file if added later.
