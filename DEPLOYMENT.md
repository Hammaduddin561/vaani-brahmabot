# 🚀 Deployment Guide for VAANI - The BrahmaBot

This guide covers various deployment options for VAANI, from local development to production cloud deployment.

## 📋 Quick Deployment Checklist

- [ ] Environment variables configured
- [ ] Dependencies installed  
- [ ] Security settings reviewed
- [ ] Performance optimizations enabled
- [ ] Backup and monitoring setup

## 🖥️ Local Development

### Basic Setup
```bash
# Clone repository
git clone https://github.com/yourusername/vaani-brahmabot.git
cd vaani-brahmabot

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run VAANI
python enhanced_app.py
```

### Development with Auto-reload
```bash
# Install development dependencies
pip install uvicorn[standard]

# Run with auto-reload (development only)
uvicorn enhanced_app:app --reload --host 0.0.0.0 --port 8080
```

## 🐳 Docker Deployment

### Build Docker Image
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 vaani && chown -R vaani:vaani /app
USER vaani

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "enhanced_app.py"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  vaani:
    build: .
    ports:
      - "8080:8080"
    environment:
      - HOST=0.0.0.0
      - PORT=8080
      - NEO_URI=bolt://neo4j:7687
    env_file:
      - .env
    depends_on:
      - neo4j
    restart: unless-stopped
    
  neo4j:
    image: neo4j:5.15
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/your_password
      - NEO4J_dbms_default__database=vaani
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

volumes:
  neo4j_data:
```

### Run with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f vaani

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS EC2
```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Connect via SSH

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Clone and deploy
git clone https://github.com/yourusername/vaani-brahmabot.git
cd vaani-brahmabot
sudo docker-compose up -d

# Setup nginx reverse proxy
sudo apt install nginx
sudo nano /etc/nginx/sites-available/vaani
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 2: AWS ECS (Fargate)
```bash
# Install AWS CLI and ECS CLI
aws configure

# Create ECS cluster
ecs-cli configure --cluster vaani-cluster --default-launch-type FARGATE --region us-west-2
ecs-cli up --cluster-config vaani-cluster --ecs-profile default

# Deploy with docker-compose
ecs-cli compose --project-name vaani service up --cluster-config vaani-cluster --ecs-profile default
```

### Google Cloud Platform

#### Cloud Run Deployment
```bash
# Install gcloud CLI
gcloud auth login
gcloud config set project your-project-id

# Build and deploy
gcloud builds submit --tag gcr.io/your-project-id/vaani
gcloud run deploy vaani --image gcr.io/your-project-id/vaani --platform managed --region us-central1 --allow-unauthenticated
```

#### GKE Deployment
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vaani-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vaani
  template:
    metadata:
      labels:
        app: vaani
    spec:
      containers:
      - name: vaani
        image: gcr.io/your-project-id/vaani:latest
        ports:
        - containerPort: 8080
        env:
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8080"
---
apiVersion: v1
kind: Service
metadata:
  name: vaani-service
spec:
  selector:
    app: vaani
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Azure Deployment

#### Azure Container Instances
```bash
# Login to Azure
az login

# Create resource group
az group create --name vaani-rg --location eastus

# Deploy container
az container create \
  --resource-group vaani-rg \
  --name vaani-container \
  --image your-registry/vaani:latest \
  --dns-name-label vaani-unique \
  --ports 8080 \
  --environment-variables 'HOST'='0.0.0.0' 'PORT'='8080'
```

### Heroku Deployment

#### Setup Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-vaani-app

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set HOST=0.0.0.0
heroku config:set PORT=$PORT

# Deploy
git push heroku main
```

#### Procfile
```
web: python enhanced_app.py
```

## 🔒 Production Security

### Environment Variables
```bash
# Required production environment variables
export SECRET_KEY="your-super-secret-key-here"
export NEO_PASS="secure-neo4j-password"  
export TWILIO_AUTH_TOKEN="your-twilio-token"
export API_KEY="your-api-key"

# Optional security enhancements
export CORS_ORIGINS="https://yourdomain.com"
export RATE_LIMIT_PER_MINUTE=60
export MAX_REQUEST_SIZE=10MB
```

### SSL/TLS Setup
```bash
# Install certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Logging

### Basic Monitoring
```python
# Add to enhanced_app.py
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logging.basicConfig(
    handlers=[RotatingFileHandler('logs/vaani.log', maxBytes=100000, backupCount=10)],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
```

### Health Checks
```bash
# Setup health check monitoring
curl -f http://localhost:8080/health || exit 1

# Advanced health checks
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"text": "health check"}' \
  -w "%{http_code}\n"
```

### Performance Monitoring
```python
# Add performance metrics
import psutil
import time

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log performance metrics
    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
    logger.info(f"Request: {request.url} - Time: {process_time:.3f}s - Memory: {memory_mb:.1f}MB")
    
    return response
```

## 🚀 Production Optimization

### Performance Tuning
```python
# enhanced_app.py production settings
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_app:app",
        host="0.0.0.0",
        port=8080,
        reload=False,           # Disable in production
        workers=4,              # Adjust based on CPU cores
        log_level="warning",    # Reduce log verbosity
        access_log=False        # Disable access logs for performance
    )
```

### Database Optimization
```bash
# Neo4j production configuration
# Increase memory allocation
NEO4J_dbms_memory_heap_initial__size=2G
NEO4J_dbms_memory_heap_max__size=4G
NEO4J_dbms_memory_pagecache_size=2G

# Enable query logging
NEO4J_dbms_logs_query_enabled=true
NEO4J_dbms_logs_query_threshold=1s
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy VAANI

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying VAANI to production..."
```

## 📦 Backup & Recovery

### Database Backup
```bash
# Neo4j backup
neo4j-admin backup --from=localhost:6362 --to=/backups/vaani-$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/vaani"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
docker exec neo4j neo4j-admin backup --from=localhost:6362 --to=/var/lib/neo4j/backups/vaani-$DATE

# Compress backup
tar -czf $BACKUP_DIR/vaani-backup-$DATE.tar.gz /var/lib/neo4j/backups/vaani-$DATE

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "vaani-backup-*.tar.gz" -mtime +7 -delete
```

### Configuration Backup
```bash
# Backup environment and configuration
cp .env .env.backup.$(date +%Y%m%d)
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d)
```

## 🆘 Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats vaani_vaani_1

# Restart with memory limits
docker run --memory=1g --memory-swap=2g your-vaani-image
```

#### Database Connection Issues
```bash
# Check Neo4j status
docker logs vaani_neo4j_1

# Test connection
curl http://localhost:7474/browser/
```

#### Performance Issues
```bash
# Check system resources
htop
iotop
netstat -tuln

# Profile Python application
python -m cProfile -o profile.stats enhanced_app.py
```

## 📞 Production Support

### Monitoring Alerts
- Setup alerts for high memory usage (>500MB)
- Monitor response times (>5 seconds)
- Check disk space (>80% full)
- Database connection failures

### Emergency Contacts
- System Administrator: [Your Contact]
- Database Administrator: [Your Contact]  
- Application Developer: [Your Contact]

---

**Remember**: Always test deployments in a staging environment before production! 🚀