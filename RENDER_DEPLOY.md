# Render Deployment Guide for Fal MCP

## ✅ Quick Start

```bash
# 1. Use the Render-specific Dockerfile
docker build -f Dockerfile.render -t fal-mcp-render .

# 2. Push to your own registry (or use Docker Hub)
docker push fal-mcp-render:latest

# 3. On Render dashboard:
#    - Build command: docker build -f Dockerfile.render .
#    - Start command: uvicorn app.main:mcp --host 0.0.0.0 --port $SERVER_PORT
#    - Add environment variables (see below)
```

## Environment Variables for Render

Add these to Render Dashboard **before deployment**:

### Required (Must configure in Render Dashboard):
| Variable | Value Example | Where to Get It |
|----------|---------------|-----------------|
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true&w=majority` | MongoDB Atlas connection string |
| `DATABASE_NAME` | `fal_mcp_keys` | Your Atlas database name |
| `ENCRYPTION_KEY` | `gAAAAAB...` (base64, 43 chars) | Generate with Python command below |
| `HOST` | `0.0.0.0` | Always 0.0.0.0 for public access |
| `PORT` | `10000` | Render uses port 10000, not 8000! |

### Optional (If using twynity):
| Variable | Value |
|----------|-------|
| `ACCOUNT_SERVICE_URL` | `https://account-service.onrender.com` |
| `PUBLIC_URL` | `https://your-app.onrender.com` |
| `ALLOWED_ORIGINS` | `*` or your specific domains |

## How to Generate ENCRYPTION_KEY

```bash
# Run this command once (copy the output)
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

⚠️ **Never commit `.env` files** - Render manages secrets via their dashboard!

## MongoDB Atlas Setup (Required for Production)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/)
2. Create free cluster (M0 tier)
3. Click "Connect" → "Connect your application"
4. Copy connection string and paste into: `MONGODB_URI`
5. Replace `<password>` with your database user password

## Common Render Errors & Solutions

### Error: "Exit code 128"

**Cause**: MongoDB connection failed or wrong environment variables

✅ **Solution**:
```bash
# Test locally first with proper env vars
docker run --rm -e MONGODB_URI="your-connection-string" \
    -e ENCRYPTION_KEY=<your-key> fal-mcp-render:latest
```

### Error: ImportError for fal module

**Cause**: fal package not installed in venv

✅ **Solution**: Edit Render → Settings → Build command:
```bash
docker build -f Dockerfile.render . && pip install fal>=1.60.0 || true
```

### Error: uvicorn not found

**Cause**: uvicorn missing from dependencies

✅ **Solution**: Ensure `uvicorn` is in pyproject.toml dependencies (it should be)

## Render Settings Checklist

- [ ] Build Command: `docker build -f Dockerfile.render .`
- [ ] Start Command: `uvicorn app.main:mcp --host 0.0.0.0 --port $SERVER_PORT`
- [ ] Environment Variables configured (as table above)
- [ ] Health check enabled (Render auto-detects at `/health`)
- [ ] Git ignore includes `.env`, `__pycache__`, node_modules
- [ ] GitHub Actions workflows disabled (or skip the render.yml action)

## Debug Commands for Render Support Team

If deployment fails, send them these logs:

```bash
# Get container logs from Render API
curl -s https://api.render.com/v1/apps/YOUR_APP_ID/logs

# Or test locally with same env vars
docker build -f Dockerfile.render -t fal-mcp-test .
docker run --rm \
  -p 8000:8000 \
  -e MONGODB_URI="${MONGODB_URI}" \
  -e ENCRYPTION_KEY="${ENCRYPTION_KEY}" \
  fal-mcp-test:latest
```

## Testing Deployment Locally Before Render

```bash
# Build locally
docker build -f Dockerfile.render -t fal-mcp-render .

# Run with test environment
MONGODB_URI="mongodb://localhost:27017/test" \
ENCRYPTION_KEY="cGFzc3dvcmQxMjM=" \
docker run --rm -p 8000:8000 fal-mcp-render:latest

# If MongoDB fails, this will fail fast with helpful errors
```

## Troubleshooting Checklist

- [ ] Did you use MongoDB Atlas (managed), not local `mongodb://host`?
- [ ] Is `ENCRYPTION_KEY` properly generated (43 chars)?
- [ ] Are you using `Dockerfile.render` (not the old one with `|| true`)?
- [ ] Does MongoDB allow connections from Render's IP addresses?
- [ ] Have you whitelisted Render IPs in MongoDB Atlas Network Access list?

## Whitelisting Render IPs in MongoDB Atlas

Render connects from: `109.73.242.65/32` (and others)

1. Go to MongoDB Atlas → Network Access
2. Add new IP whitelist entry
3. Use Render's network range or allow all (0.0.0.0/0 for dev)

---

## Need Help?

- Render Docs: https://render.com/docs/troubleshooting-deploys
- Connection String Builder: https://mongodb.com/cloud/atlas/begin/setup-database/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
