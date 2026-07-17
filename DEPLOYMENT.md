# DocMind Deployment Guide

## Development Setup

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+
- **PostgreSQL** 16+
- **Docker & Docker Compose** (recommended)

### Quick Start (Local)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

**PostgreSQL:**
```bash
docker run -d \
  -e POSTGRES_DB=docmind \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

---

## Docker Compose (Recommended)

### Build

```bash
cd DocMind
docker compose build
```

### Start Services

```bash
docker compose up -d
```

### Monitor

```bash
# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Specific service
docker compose logs backend --tail=100
```

### Stop & Clean

```bash
# Stop services
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Rebuild and restart
docker compose down && docker compose build --no-cache && docker compose up -d
```

### Verify Services

```bash
# Frontend health
curl http://localhost/

# Backend health
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs

# Database connection
docker compose exec postgres pg_isready -U postgres

# Ollama health
curl http://localhost:11434/api/tags
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Use strong `JWT_SECRET` (min 32 random characters)
- [ ] Set `APP_ENV=production` and `DEBUG=false`
- [ ] Configure `DATABASE_URL` for production database
- [ ] Set up SSL/TLS certificates for HTTPS
- [ ] Configure `OPENAI_API_KEY` or ensure Ollama is available
- [ ] Set resource limits on containers
- [ ] Configure log forwarding
- [ ] Set up monitoring and alerting
- [ ] Configure database backups
- [ ] Test disaster recovery

### Environment Variables (Production)

**Backend (.env or secrets):**
```env
APP_NAME=DocMind
APP_VERSION=0.1.0
APP_ENV=production
DEBUG=false

DATABASE_URL=postgresql+psycopg2://user:password@prod-db.example.com:5432/docmind

JWT_SECRET=your-super-secret-key-min-32-chars-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

UPLOAD_DIR=/app/storage/uploads
MAX_UPLOAD_SIZE_MB=50
LOG_LEVEL=INFO

OPENAI_API_KEY=sk-your-production-key
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama2
EMBEDDING_MODEL=bge-small
OCR_LANGUAGE=en
```

### Docker Compose Production

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: docmind-postgres
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-docmind}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - docmind
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: docmind-backend
    restart: always
    environment:
      APP_ENV: production
      DEBUG: false
      DATABASE_URL: ${DATABASE_URL}
      JWT_SECRET: ${JWT_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OLLAMA_HOST: ${OLLAMA_HOST}
    volumes:
      - ./storage/uploads:/app/storage/uploads
      - ./storage/logs:/app/storage/logs
      - ./storage/vectorstore:/app/storage/vectorstore
    networks:
      - docmind
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: docmind-frontend
    restart: always
    environment:
      VITE_API_BASE_URL: https://api.docmind.example.com
    networks:
      - docmind
    depends_on:
      - backend
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  ollama:
    image: ollama/ollama:latest
    container_name: docmind-ollama
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - docmind
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

volumes:
  postgres_data:
  ollama_data:

networks:
  docmind:
    driver: bridge
```

**Start production:**
```bash
docker compose -f docker-compose.production.yml up -d
```

### Nginx Configuration

**File: `nginx.conf`**
```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    location = /index.html {
        root /usr/share/nginx/html;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Health checks
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### SSL/TLS Setup (Let's Encrypt)

```bash
# Using Certbot with Docker
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly --standalone \
  -d docmind.example.com

# Update nginx.conf
server {
    listen 443 ssl http2;
    server_name docmind.example.com;
    
    ssl_certificate /etc/letsencrypt/live/docmind.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docmind.example.com/privkey.pem;
    
    # Include remaining config...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name docmind.example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Kubernetes Deployment (Future)

**Namespace:**
```bash
kubectl create namespace docmind
```

**Database:**
```bash
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
```

**Backend:**
```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/backend-ingress.yaml
```

**Frontend:**
```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

**Monitoring:**
```bash
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
```

---

## Database Management

### Backups

**PostgreSQL Dump:**
```bash
# Full backup
docker compose exec postgres pg_dump -U postgres docmind > backup_$(date +%Y%m%d).sql

# Compressed backup
docker compose exec postgres pg_dump -U postgres docmind | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated daily backup
0 2 * * * /usr/local/bin/backup-docmind.sh >> /var/log/docmind-backup.log 2>&1
```

**Backup Script (`/usr/local/bin/backup-docmind.sh`):**
```bash
#!/bin/bash
BACKUP_DIR="/backups/docmind"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker compose exec -T postgres pg_dump -U postgres docmind | \
  gzip > $BACKUP_DIR/docmind_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

### Restore

```bash
# Restore from backup
gunzip < backup_20240717.sql.gz | docker compose exec -T postgres psql -U postgres -d docmind

# Or restore to new database
docker compose exec postgres createdb -U postgres docmind_restored
gunzip < backup_20240717.sql.gz | docker compose exec -T postgres psql -U postgres -d docmind_restored
```

### Database Migrations

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Revert migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Monitoring & Logging

### Container Logs

```bash
# Real-time logs
docker compose logs -f backend

# Last 100 lines
docker compose logs backend --tail=100

# With timestamps
docker compose logs -f --timestamps backend

# All services
docker compose logs -f
```

### Log Rotation

**Logrotate config (`/etc/logrotate.d/docmind`):**
```
/var/log/docmind/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 appuser appuser
    sharedscripts
    postrotate
        docker compose exec backend kill -SIGUSR1 1
    endscript
}
```

### Performance Monitoring

```bash
# CPU & Memory
docker stats

# Specific service
docker stats docmind-backend

# Database connections
docker compose exec postgres psql -U postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Health Checks

```bash
# Frontend
curl -f http://localhost/ || echo "Frontend DOWN"

# Backend
curl -f http://localhost:8000/health || echo "Backend DOWN"

# Database
docker compose exec postgres pg_isready -U postgres || echo "PostgreSQL DOWN"

# Ollama
curl -f http://localhost:11434/api/tags || echo "Ollama DOWN"
```

---

## Scaling

### Horizontal Scaling (Backend)

Use load balancer (nginx, HAProxy, Traefik):

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    least_conn;
}
```

### Vertical Scaling

**Increase resource limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '8'
      memory: 8G
    reservations:
      cpus: '4'
      memory: 4G
```

### Database Scaling

- **Read Replicas:** Separate read traffic
- **Connection Pooling:** PgBouncer/Hikari
- **Partitioning:** Shard by user_id or document_id

### Vector Store Scaling

- **Distributed FAISS:** One index per document shard
- **Elasticsearch:** Full-text + vector search
- **Milvus:** Distributed vector database

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker compose logs backend

# Common issues:
# 1. Database not ready
docker compose exec postgres pg_isready

# 2. Migration failed
docker compose exec backend alembic current

# 3. Memory error
docker compose exec backend free -h
```

### High CPU Usage

```bash
# Check which process
docker stats

# Profile embeddings (CPU-intensive)
# Switch to bge-base for quality tradeoff
# Or use GPU: pip install faiss-gpu

# Profile LLM
curl http://ollama:11434/api/show?name=llama2
```

### Database Connection Issues

```bash
# Check connection
docker compose exec postgres psql -U postgres -c "SELECT 1"

# Check connection pool
docker compose exec backend python -c "
from app.database.engine import engine
with engine.connect() as conn:
    print(conn.info)
"

# Increase pool size in config
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
```

### Memory Leaks

```bash
# Monitor memory growth
while true; do
  docker stats --no-stream docmind-backend
  sleep 60
done

# Restart service
docker compose restart backend

# Or enable memory limit
docker compose down
# Edit docker-compose.yml, set memory limits
docker compose up -d
```

---

## Security Hardening

### Network

- [ ] Use private networks
- [ ] Restrict SSH to specific IPs
- [ ] Use VPN for remote access
- [ ] Enable WAF (ModSecurity, Cloudflare)

### Docker

- [ ] Use read-only root filesystem
- [ ] Disable privileged mode
- [ ] Use security scanning (Trivy)
- [ ] Sign images (Notary)

### Database

- [ ] Restrict access to PostgreSQL
- [ ] Use strong passwords
- [ ] Enable SSL connections
- [ ] Regular backups and restores

### Application

- [ ] Rotate JWT secrets regularly
- [ ] Enable HTTPS
- [ ] Set secure headers (HSTS, CSP)
- [ ] Rate limiting
- [ ] Input validation

---

## Continuous Integration/Deployment

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build images
        run: docker compose build
      
      - name: Test backend
        run: docker compose run backend pytest
      
      - name: Test frontend
        run: docker compose run frontend npm run lint
      
      - name: Deploy
        env:
          SERVER_IP: ${{ secrets.PRODUCTION_SERVER }}
        run: |
          echo "${{ secrets.DEPLOY_KEY }}" > deploy_key
          chmod 600 deploy_key
          ssh -i deploy_key ubuntu@$SERVER_IP \
            'cd /app/docmind && git pull && docker compose up -d'
```

---

## Disaster Recovery

### Recovery Time Objectives (RTO)

- Full infrastructure: 4 hours
- Database from backup: 30 minutes
- Application from image: 10 minutes

### Recovery Point Objectives (RPO)

- Database: Daily backup + transaction log
- Application code: Git repository (real-time)
- User data: Incremental backups (hourly)

### Restore Procedure

```bash
# 1. Provision new server/cluster
# 2. Install Docker & Docker Compose
# 3. Clone repository
git clone https://github.com/SwastikPandey1024/DocMind.git
cd DocMind

# 4. Restore database
gunzip < backup_20240717.sql.gz | docker compose exec -T postgres psql -U postgres -d docmind

# 5. Start services
docker compose up -d

# 6. Verify health
docker compose ps
curl http://localhost:8000/health
```

---

**For architecture details, see ARCHITECTURE.md**
**For API reference, see /docs endpoint**
**For troubleshooting, see README.md**
