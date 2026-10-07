# Fal MCP

A FastMCP server that invokes fal.ai models using credentials configured for
the active Twynity project. Credentials are encrypted in MongoDB and scoped to
the verified `(user_id, persona_id)` identity.

## Runtime configuration

Copy `.env.example` to `.env` and set the required MongoDB URI, Fernet
`ENCRYPTION_KEY`, and account service URL. Generate a Fernet key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Install dependencies and start the HTTP MCP app:

```bash
uv sync --locked
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The service verifies MCP bearer tokens against the configured account-service
JWKS. Custom configuration routes independently verify the token and require
the `Persona-Id` header. Twynity must forward both headers for MCP App calls.

## Configure a fal.ai connection

Send an authenticated request to `POST /api/v1/configuration`:

```json
{"name":"fal.ai","api_key":"<your fal.ai key>"}
```

The key is encrypted before storage. Configuration GET routes return metadata
only. The `invoke_fal_model` tool retrieves the key for the verified active
project and invokes the supplied model ID and JSON arguments. The default
model is `fal-ai/flux/schnell`; set `DEFAULT_FAL_MODEL` to override it.

## HTTP routes

- `GET /api/v1/.well-known/mcp.json` — public Twynity service manifest.
- `GET /api/v1/schema` — connection configuration schema.
- `POST /api/v1/configuration` — authenticated project-scoped credential upsert.
- `GET /api/v1/configuration` — authenticated safe metadata response.
- `GET /api/v1/external-connection/me` — authenticated connection status.
- `GET /api/v1/health` — public liveness check.

## Docker and Render

The Dockerfile installs the locked Python dependencies, copies the app source,
runs as a non-root user, and starts the exported ASGI app on `0.0.0.0:$PORT`.
For Render Web Services, configure the required variables and set the health
check path to `/api/v1/health`. See [RENDER_DEPLOY.md](RENDER_DEPLOY.md).
