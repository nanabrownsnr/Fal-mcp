# Fal MCP API reference

Fal MCP exposes the fal.ai model API as an authenticated MCP tool. Each call
uses the encrypted API key configured for the request's verified Twynity user
and `Persona-Id` pair.

## Configure credentials

Send a bearer JWT and `Persona-Id` header to `POST /api/v1/configuration`:

```json
{
  "name": "fal.ai",
  "api_key": "<fal.ai API key>"
}
```

Credentials are encrypted at rest using `ENCRYPTION_KEY`. `GET
/api/v1/configuration` returns connection metadata only; it never returns the
stored API key.

## Invoke a model

Call the `invoke_fal_model` MCP tool with a fal.ai endpoint ID and the JSON
arguments documented for that model. For example:

```json
{
  "model_id": "fal-ai/flux/schnell",
  "arguments": {
    "prompt": "A red fox in a field of flowers",
    "image_size": "square"
  }
}
```

The tool returns the model ID and the provider's result. The key is selected
server-side from the verified user/persona connection and is never an MCP tool
argument.

## Other routes

- `GET /api/v1/.well-known/mcp.json` — public service manifest.
- `GET /api/v1/schema` — configuration schema.
- `GET /api/v1/external-connection/me` — authenticated connection status.
- `GET /api/v1/health` — public liveness check.

Twynity must forward the authenticated bearer token and `Persona-Id` header on
both HTTP configuration requests and MCP tool calls.
