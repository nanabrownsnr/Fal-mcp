# Fal MCP — AI Model API Caller 🚀

A FastMCP server for calling AI models via the **fal.ai** API with encrypted credential storage per user.

## What This Server Does

- Stores encrypted API keys per `(user_id, persona_id)` in MongoDB  
- Provides tools to call fal.ai's model endpoints
- Simple UI for viewing tool outputs
- Twynity-compatible authentication model with JWT verification

## Quick Start

### 1. Environment Setup

```bash
# Copy this file and fill in actual values
mv .env.example .env

# Run these commands to generate encryption key:
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" >> .env
```

### 2. Install Dependencies

```bash
uv sync --locked
```

### 3. Run Development Server

```bash
uv run uvicorn app.main:mcp --host 0.0.0.0 --port 8000
```

## fal.ai Model API Reference

- [fal.ai Docs](https://fal.ai/docs/model-api-reference)
- Example call:
  ```python
  from fal import Client
  client = Client()
  result = client.invoke(
      model="fal-ai/llama3",
      input={"prompt": "Write a haiku about AI"},
  )
  print(result["output"])
  ```

## Docker Deployment

Build locally:

```bash
docker build -t fal-mcp .
docker run --rm -p 8000:8000 \
  -e MONGODB_URI=mongodb://host:port \
  -e ENCRYPTION_KEY=your-generated-fernet-key \
  fal-mcp
```

Deploy with Kubernetes compose pattern from template.

## Storage Contract

API keys are stored encrypted per user/persona in MongoDB for secure multi-tenant deployment.

### POST `/api/v1/keys`

```json
{
  "name": "GitHub-PAT",
  "key": "ghp_xxxxxxxxxxxxxx"
}
```

## Project Structure

```
FalMCP/
├── app/
│   ├── main.py              # FastMCP server entry point
│   ├── config.py            # Environment settings and logging
│   ├── auth.py              # JWT verification layer
│   ├── connection_store.py  # Encrypted credential storage
│   ├── twynity.py           # HTTP routes for /api/v1/keys
│   ├── tweenit.py           # fal.ai client helper
│   └── ui/
│       └── model_view.vue   # UI scaffold component
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_keys.py         # Key management tests
├── docs/
│   └── API_REFERENCE.md     # fal.ai Model API guide
├── .dockerignore            # Docker build exclusions
├── Dockerfile               # Multi-stage production image
├── pyproject.toml           # Dependencies and tool config
└── README.md                # This file
```

## License

MIT — See `LICENSE` if added later

---

**Status**: ✅ Ready for fal.ai integration and deployment  
**GitHub**: [nanabrownsnr/Fal-mcp](https://github.com/nanabrownsnr/Fal-mcp)
