# Fal MCP Deployment Guide

## Quick Deploy Options

### Option 1: Local Docker (Easiest)

```bash
# Build locally
docker build -t fal-mcp .

# Run with environment variables set
docker run --rm -p 8000:8000 \
  -e MONGODB_URI="mongodb://localhost:27017" \
  -e MONGODB_DATABASE="fal_mcp_keys" \
  -e ENCRYPTION_KEY="<your-fernet-key>" \
  fal-mcp:latest
```

### Option 2: Docker Compose (with MongoDB)

```bash
# Copy example env and generate encryption key
mv .env.example .env
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" >> .env

# Start with MongoDB included
docker-compose up -d

# Check logs
docker-compose logs -f fal-mcp-server
```

### Option 3: Render.com Deployment (with MongoDB Atlas)

#### Prerequisites:
1. Create MongoDB Atlas database at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/)
2. Get connection string from Atlas → Connect → Connect your application
3. Replace `<MONGODB_URI>` in `.env` with your Atlas connection string
4. Upload your `.env` to Render (with secrets configured)

#### Deploy Steps on Render:
1. Create new Web Service at [Render](https://render.com)
2. Connect GitHub repo `nanabrownsnr/Fal-mcp`
3. Set environment variables in Render dashboard:
   - `MONGODB_URI=your-atlas-connection-string`
   - `MONGODB_DATABASE=fal_mcp_keys`
   - `ENCRYPTION_KEY=<generate-new-key>`
   - `HOST=0.0.0.0`
   - `PORT=10000` (Render uses 10000 instead of 8000)

4. Build Command: `docker build -t fal-mcp .`
5. Start Command: `uvicorn app.main:mcp --host 0.0.0.0 --port $SERVER_PORT`

### Option 4: Cloud Provider (AWS ECS / GCP Cloud Run / Azure Container Apps)

For these platforms, you'll need to:
1. Build Docker image and push to container registry
2. Configure MongoDB connection as a database service
3. Set same environment variables listed above
4. Scale with zero-to-many instances depending on traffic

---

## Troubleshooting Exit Code 128

This occurs when:
- GitHub Actions tries to deploy without `.env` secrets
- MongoDB is missing from deployment environment
- API keys aren't properly encrypted in container

**Solutions:**
1. Use Render/Cloud provider (not raw Docker for production)
2. Generate encryption key using command in `.env.example`
3. Mount MongoDB volume or use managed database service
4. Don't commit `.env` to git - use platform secrets

---

## Environment Variables Reference

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://user:pass@host:27017/db` |
| `MONGODB_DATABASE` | Database name | `fal_mcp_keys` |
| `ENCRYPTION_KEY` | Fernet encryption key from CLI command | `<generated-key>` |
| `HOST` | Server bind address | `0.0.0.0` or `localhost` |
| `PORT` | Server port | `8000` or `10000` |
| `ALLOWED_ORIGINS` | CORS origins | `*` or specific domains |

---

## Production Recommendations

- ✅ Use environment variables managed by your hosting platform
- ✅ Enable health checks on all services
- ✅ Monitor logs via cloud provider dashboards
- ✅ Set proper resource limits (CPU/RAM)
- ✅ Use MongoDB Atlas for production-grade database
