# VulnPatch AI Deployment Guide

## Prerequisites

- Docker and Docker Compose
- 4GB+ RAM
- 10GB+ disk space
- OpenAI API key (for LLM features)

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd vulnpatch-ai
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Configure Environment**
   ```bash
   # Edit backend/.env with your API keys
   nano backend/.env
   
   # Required settings:
   OPENAI_API_KEY=your-openai-api-key-here
   SECRET_KEY=your-secure-secret-key
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Start PostgreSQL
   docker run -d --name vulnpatch_postgres \
     -e POSTGRES_DB=vulnpatch_db \
     -e POSTGRES_USER=vulnpatch \
     -e POSTGRES_PASSWORD=vulnpatch \
     -p 5432:5432 postgres:15

   # Run migrations
   alembic upgrade head
   ```

3. **Start Backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend**
   ```bash
   npm start
   ```

## Production Deployment

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-openai-api-key
NVD_API_KEY=your-nvd-api-key
DEBUG=false
ALLOWED_HOSTS=["https://yourdomain.com"]

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
```

### Docker Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: vulnpatch_db
      POSTGRES_USER: vulnpatch
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://vulnpatch:${DB_PASSWORD}@postgres:5432/vulnpatch_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=${API_URL}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
docker-compose exec backend python -c "from app.core.database import engine; print('DB OK' if engine.connect() else 'DB Error')"
```

### Logs

```bash
# View all logs
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Database logs
docker-compose logs -f postgres
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U vulnpatch vulnpatch_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U vulnpatch vulnpatch_db < backup.sql
```

### File Backup

```bash
# Backup uploads
tar -czf uploads-backup.tar.gz backend/uploads/

# Restore uploads
tar -xzf uploads-backup.tar.gz -C backend/
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   ```

2. **OpenAI API Errors**
   ```bash
   # Verify API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

3. **File Upload Issues**
   ```bash
   # Check permissions
   ls -la backend/uploads/
   
   # Fix permissions
   chmod 755 backend/uploads/
   ```

4. **Frontend Build Errors**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
   CREATE INDEX idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
   CREATE INDEX idx_scans_user_id ON scans(user_id);
   ```

2. **Redis Configuration**
   ```bash
   # Increase memory limit
   docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
   ```

3. **Backend Scaling**
   ```yaml
   # Scale backend instances
   backend:
     deploy:
       replicas: 3
   ```

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Database**: Use strong passwords and restrict access
3. **HTTPS**: Always use SSL/TLS in production
4. **File Uploads**: Validate and sanitize all uploads
5. **Rate Limiting**: Implement API rate limiting
6. **Monitoring**: Set up security monitoring and alerts