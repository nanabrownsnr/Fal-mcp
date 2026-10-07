# Render Deployment Guide for Fal MCP

## ✅ Quick Start

```bash
# 1. Build using main Dockerfile (no separate Render file needed)
docker build -t fal-mcp-render .
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

### Optional (For twynity or custom URLs):
| Variable | Value |
|----------|-------|
| `ACCOUNT_SERVICE_URL` | `https://account-service.onrender.com` |
| `PUBLIC_URL` | `https://your-app.onrender.com` |
| `ALLOWED_ORIGINS` | `*` or your specific domains |

## How to Generate ENCRYPTION_KEY

```bash
# Run this command once (copy the output)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

⚠️ **Never commit `.env` files** - Render manages secrets via their dashboard!

## MongoDB Atlas Setup (Required for Production)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/)
2. Create free cluster (M0 tier)
3. Click "Connect" → "Connect your application"
4. Copy connection string and paste into: `MONGODB_URI`
5. Replace `<password>` with your database user password

## Render Settings Checklist

- [ ] **Build Command**: `docker build -t fal-mcp .` (uses main Dockerfile)
- [ ] **Start Command**: `uvicorn app.main:mcp --host 0.0.0.0 --port $PORT`
- [ ] Environment Variables configured (as table above)
- [ ] Health check enabled at `/api/v1/health` or `/api/v1/status`
- [ ] Git ignore includes `.env`, `__pycache__`, node_modules
- [ ] GitHub Actions workflows disabled (or skip the render.yml action)

## Debug Commands for Render Support Team

If deployment fails, send them these logs:

```bash
# Get container logs from Render API
curl -s https://api.render.com/v1/apps/YOUR_APP_ID/logs

# Or test locally with same env vars
docker build -t fal-mcp-test .
MONGODB_URI="your-connection-string" \
ENCRYPTION_KEY="cGFzc3dvcmQxMjM=" \
docker run --rm -p 8000:10000 fal-mcp-test:latest
```

## Testing Deployment Locally Before Render

```bash
# Build locally using main Dockerfile
docker build -t fal-mcp-render .

# Run with test environment (localhost MongoDB or Atlas)
MONGODB_URI="mongodb://localhost:27017/test" \
ENCRYPTION_KEY="cGFzc3dvcmQxMjM=" \
docker run --rm -p 8000:10000 fal-mcp-render:latest
```

## Troubleshooting Checklist

- [ ] Did you use MongoDB Atlas (managed), not local `mongodb://host`?
- [ ] Is `ENCRYPTION_KEY` properly generated (43 chars)?
- [ ] Are you using the **main Dockerfile** (not an old one with `|| true`)?
- [ ] Does MongoDB allow connections from Render's IP addresses?
- [ ] Have you whitelisted Render IPs in MongoDB Atlas Network Access list?

## Whitelisting Render IPs in MongoDB Atlas

Render connects from various IPs: `109.73.242.65/32` (and others)

1. Go to MongoDB Atlas → Network Access
2. Add new IP whitelist entry
3. Use Render's network range or allow all (0.0.0.0/0 for dev)

---

## Need Help?

- Render Docs: https://render.com/docs/troubleshooting-deploys
- Connection String Builder: https://mongodb.com/cloud/atlas/begin/setup-database/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
