# Fal MCP Server Deployment Guide

## Overview

This guide covers deploying the Fal.ai MCP Server for cloud hosting on Render, AWS, or self-hosted Kubernetes.

---

## Quick Start (Render Cloud)

### 1. Prerequisites

- GitHub account with `Fal-mcp` repository
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/) account (free tier OK)
- Python 3.12+ environment for key generation

### 2. Generate Encryption Key (One-Time Setup)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Copy the output** (43 characters). You will use this on Render Dashboard.

### 3. Configure MongoDB Atlas

1. Create free cluster → Get **connection string**
2. Network Access: Whitelist Render IPs or `0.0.0.0/0` for dev
3. Create database user with read/write access

### 4. Render Dashboard Setup

Go to your Render project settings:

**Environment Variables (all required):**

```bash
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/fal_mcp_keys?retryWrites=true&w=majority
DATABASE_NAME=fal_mcp_keys
ENCRYPTION_KEY=<paste-key-from-step-2>
HOST=0.0.0.0
PORT=10000
ENVIRONMENT=production
ALLOWED_ORIGINS=*
PUBLIC_URL=https://your-app.onrender.com
```

**Build Settings:**

- Build command: `docker build -t fal-mcp .`
- Start command: `uvicorn app.main:mcp --host 0.0.0.0 --port $PORT`
- Health check: `/api/v1/health` (Render auto-detects)

### 5. Deploy

```bash
# Commit & push after updating Dockerfile
git add -A && git commit -m "Deploy fixes: Dockerfile, twynity routes" && git push origin main
```

Render will automatically redeploy! ✅

---

## Deployment Checklist

- [ ] MongoDB Atlas cluster created and connected from Render IPs
- [ ] `ENCRYPTION_KEY` generated (43 base64 chars)  
- [ ] All environment variables set in Render Dashboard
- [ ] Dockerfile updated (check commit on GitHub)
- [ ] Main branch pushed to trigger deploy

---

## Alternative: Self-Hosted Kubernetes/AWS ECS

Use same `Dockerfile` with container orchestrators. Example docker-compose:

```yaml
version: '3.8'
services:
  fal-mcp:
    build: .
    ports:
      - "${HOST_IP}:10000:10000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/fal_mcp_keys
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - DATABASE_NAME=fal_mcp_keys
    depends_on:
      - mongo
  
  mongo:
    image: mongo:6.0

# Generate .env from .render-env.example before build!
```

---

## Support

- Render Docs: https://render.com/docs/troubleshooting-deploys  
- Fal Client: https://github.com/nanabrownsnr/fal-client  
- MongoDB Connection Strings: https://mongodb.com/cloud/atlas/begin/setup-database/  
