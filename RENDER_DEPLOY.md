# Deploy Fal MCP on Render

Create a Render **Web Service** using the repository's Dockerfile. Leave the
Build Command and Start Command empty so Render builds the image and uses its
Docker `CMD`. The container binds to `0.0.0.0` and reads Render's `PORT`
environment variable (Render's default is `10000`).

## Required environment variables

Set these in the Render dashboard. Do not commit actual credentials.

| Variable | Purpose |
| --- | --- |
| `MONGODB_URI` | MongoDB connection URI, including Atlas credentials if applicable |
| `DATABASE_NAME` | Database name, for example `fal_mcp` |
| `ENCRYPTION_KEY` | Stable Fernet key used to encrypt stored fal.ai keys |
| `ACCOUNT_SERVICE_URL` | Twynity account service base URL |
| `SERVICE_ID` | JWT audience configured for this MCP, default `fal_mcp` |
| `PUBLIC_URL` | Public Render URL used in the MCP manifest |

`ACCOUNT_SERVICE_JWKS_ENDPOINT` defaults to `/.well-known/jwks.json`. The
service also accepts `ACCOUNT_SERVICE_JWKS_CACHE_TTL`, `PERSONA_ID_HEADER`,
`ALLOWED_ORIGINS`, `DEFAULT_FAL_MODEL`, and an optional full URL for
`USAGE_REPORT_ENDPOINT`. Optional license enforcement is disabled by default;
to enable it, set `LICENSE_ENFORCEMENT_ENABLED=true`, `LICENSE_KEY`, and
`LICENSE_SERVER_BASE_URL` (the JWKS and activation paths have defaults).

Generate the encryption key locally with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep that key stable after deployment. Replacing it makes previously stored
fal.ai credentials unreadable. Configure Render's health check path as
`/api/v1/health`.

## Configure fal.ai

Twynity must send a valid account-service bearer JWT and the active
`Persona-Id` header. Configure each project's fal.ai credentials with an
authenticated `POST /api/v1/configuration` request:

```json
{"name":"fal.ai","api_key":"<project fal.ai key>"}
```

The API key is encrypted in MongoDB and is never returned by configuration GET
routes. The `invoke_fal_model` MCP tool uses the credentials belonging to the
verified user/persona pair.
