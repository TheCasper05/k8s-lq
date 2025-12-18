# Deployment Guide

This guide covers production deployment strategies for the LQ Real-time Service.

## Current Deployment Platform

The service is currently deployed on **DigitalOcean Droplets** with automated CI/CD via GitHub Actions.

## Table of Contents

1. [DigitalOcean Droplets Setup (Current)](#digitalocean-droplets-setup)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [GitHub Actions Setup](#github-actions-setup)
5. [Alternative Deployment Platforms](#alternative-deployment-platforms)
6. [Load Balancing](#load-balancing)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Backup & Recovery](#backup--recovery)
9. [Security Hardening](#security-hardening)

---

## DigitalOcean Droplets Setup

### Quick Start

1. **Create a DigitalOcean Droplet**
   - OS: Ubuntu 22.04 LTS (recommended)
   - Size: Basic Plan - 2 GB / 2 vCPUs (minimum), 4 GB / 2 vCPUs (recommended for production)
   - Enable monitoring
   - Add your SSH key

2. **Run the Setup Script**

   SSH into your droplet and run:
   ```bash
   wget https://raw.githubusercontent.com/YOUR_ORG/lq-realtime-service/main/scripts/setup-droplet.sh
   chmod +x setup-droplet.sh
   ./setup-droplet.sh
   ```

   The script will:
   - Update system packages
   - Install Docker and Docker Compose
   - Configure firewall (UFW)
   - Set up fail2ban
   - Create application directory at `/opt/lq-realtime-service`

3. **Configure GitHub Secrets**

   Go to your GitHub repository settings and add these secrets for each environment (QA/Production):

   **For QA Environment:**
   - `QA_DROPLET_HOST` - Your QA droplet IP address
   - `QA_DROPLET_USER` - SSH user (usually `root`)
   - `QA_SSH_PRIVATE_KEY` - SSH private key for authentication
   - `QA_REDIS_HOST` - Redis host address
   - `QA_REDIS_PORT` - Redis port (default: 6379)
   - `QA_REDIS_PASSWORD` - Redis password (if required)
   - `JWT_SECRET_KEY` - JWT secret key (min 32 chars)
   - `DO_REGISTRY_TOKEN` - DigitalOcean Container Registry token
   - `DO_REGISTRY_NAME` - Your registry name (e.g., `lq-registry`)

   **For Production Environment:**
   - `PROD_DROPLET_HOST` - Your production droplet IP
   - `PROD_DROPLET_USER` - SSH user (usually `root`)
   - `PROD_SSH_PRIVATE_KEY` - SSH private key for authentication
   - `PROD_REDIS_HOST` - Redis host address
   - `PROD_REDIS_PORT` - Redis port (default: 6379)
   - `PROD_REDIS_PASSWORD` - Redis password (if required)
   - `JWT_SECRET_KEY` - JWT secret key (min 32 chars)
   - `DO_REGISTRY_TOKEN` - DigitalOcean Container Registry token
   - `DO_REGISTRY_NAME` - Your registry name (e.g., `lq-registry`)

   **Environment Variables (not secrets):**
   - `APP_URL` - Your application URL (e.g., `https://realtime-qa.linguoquesto.com`)
   - `ALLOWED_ORIGINS` - Comma-separated list of allowed origins

4. **Deploy**

   Push to your branch to trigger automatic deployment:
   - Push to `staging` branch → Deploys to QA environment
   - Push to `main` branch → Deploys to Production environment

### Manual Deployment

If you need to deploy manually to a droplet:

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Navigate to app directory
cd /opt/lq-realtime-service

# Login to DigitalOcean Container Registry
echo YOUR_DO_TOKEN | docker login registry.digitalocean.com -u YOUR_DO_TOKEN --password-stdin

# Pull latest image
docker pull registry.digitalocean.com/lq-registry/lq-realtime-service:prod-latest

# Create .env.production file
cat > .env.production << EOF
DOCKER_IMAGE=registry.digitalocean.com/lq-registry/lq-realtime-service:prod-latest
ENVIRONMENT=production
JWT_SECRET_KEY=your-secret-key
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
ALLOWED_ORIGINS=https://app.linguoquesto.com
EOF

# Deploy
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Check health
curl http://localhost:8082/health
```

### Troubleshooting

**Check service status:**
```bash
docker-compose -f docker-compose.production.yml ps
```

**View logs:**
```bash
docker-compose -f docker-compose.production.yml logs -f ws-service
```

**Restart service:**
```bash
docker-compose -f docker-compose.production.yml restart
```

**Complete cleanup and redeploy:**
```bash
docker-compose -f docker-compose.production.yml down
docker system prune -f
docker-compose -f docker-compose.production.yml --env-file .env.production up -d
```

---

## Prerequisites

Before deploying to production:

- [ ] Domain name configured
- [ ] SSL/TLS certificate obtained
- [ ] Redis instance provisioned (managed or self-hosted)
- [ ] Secrets manager configured (AWS Secrets Manager, Vault, etc.)
- [ ] Monitoring system set up (DataDog, Prometheus, etc.)
- [ ] CI/CD pipeline configured

---

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```bash
# Application
APP_NAME=lq-realtime-service
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8082
WORKERS=1

# JWT Configuration (USE SECRETS MANAGER!)
JWT_SECRET_KEY=${SECRET_JWT_KEY}  # From secrets manager
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# Redis Configuration (MANAGED REDIS RECOMMENDED)
REDIS_HOST=your-redis-host.cloud.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=${SECRET_REDIS_PASSWORD}
REDIS_MAX_CONNECTIONS=200

# WebSocket Configuration
WS_MAX_CONNECTIONS_PER_INSTANCE=10000
WS_HEARTBEAT_INTERVAL=30
WS_MESSAGE_MAX_SIZE=65536

# Security
ALLOWED_ORIGINS=https://app.linguoquesto.com,https://www.linguoquesto.com
CORS_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Metrics
METRICS_ENABLED=true
```

### Secret Management

**AWS Secrets Manager:**

```bash
# Store JWT secret
aws secretsmanager create-secret \
    --name lq-realtime/jwt-secret \
    --secret-string "your-super-secret-key-min-32-chars"

# Retrieve in application
export JWT_SECRET_KEY=$(aws secretsmanager get-secret-value \
    --secret-id lq-realtime/jwt-secret \
    --query SecretString --output text)
```

**HashiCorp Vault:**

```bash
# Store secret
vault kv put secret/lq-realtime jwt_secret="your-secret"

# Retrieve in application
export JWT_SECRET_KEY=$(vault kv get -field=jwt_secret secret/lq-realtime)
```

---

## GitHub Actions Setup

The repository includes automated deployment workflows:

- **Staging Deployment** ([.github/workflows/deploy-staging.yml](.github/workflows/deploy-staging.yml))
  - Triggers on push to `staging` branch
  - Runs CI checks before deployment
  - Builds and pushes Docker image with `qa-latest` tag
  - Deploys to QA droplet via SSH

- **Production Deployment** ([.github/workflows/deploy-production.yml](.github/workflows/deploy-production.yml))
  - Triggers on push to `main` branch
  - Runs security checks and CI before deployment
  - Builds and pushes Docker image with `prod-latest` tag
  - Deploys to production droplet via SSH

Both workflows:
1. Run pre-deployment CI checks
2. Build and push Docker image to DigitalOcean Container Registry
3. SSH into the droplet
4. Pull the latest image
5. Update environment configuration
6. Restart containers using docker-compose
7. Run health checks

---

## Alternative Deployment Platforms

While the service is currently deployed on DigitalOcean Droplets, it can be deployed to other platforms:

### 1. AWS ECS

#### Step 1: Create ECR Repository

```bash
aws ecr create-repository --repository-name lq-realtime-service
```

#### Step 2: Build and Push Image

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t lq-realtime-service:latest .
docker tag lq-realtime-service:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lq-realtime-service:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lq-realtime-service:latest
```

#### Step 3: Create ECS Task Definition

```json
{
  "family": "lq-realtime-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "ws-service",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/lq-realtime-service:latest",
      "portMappings": [
        {
          "containerPort": 8082,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "REDIS_HOST", "value": "your-redis-endpoint"}
      ],
      "secrets": [
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:lq-realtime/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/lq-realtime-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8082/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Step 4: Create ECS Service with ALB

```bash
aws ecs create-service \
    --cluster production \
    --service-name lq-realtime-service \
    --task-definition lq-realtime-service:1 \
    --desired-count 3 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=ws-service,containerPort=8082"
```

### 2. Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/lq-realtime-service

gcloud run deploy lq-realtime-service \
    --image gcr.io/PROJECT_ID/lq-realtime-service \
    --platform managed \
    --region us-central1 \
    --set-env-vars REDIS_HOST=REDIS_IP,ENVIRONMENT=production \
    --set-secrets JWT_SECRET_KEY=lq-jwt-secret:latest \
    --allow-unauthenticated \
    --cpu 2 \
    --memory 4Gi \
    --max-instances 10 \
    --min-instances 2
```

### 3. Kubernetes (GKE, EKS, AKS)

#### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lq-realtime-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lq-realtime-service
  template:
    metadata:
      labels:
        app: lq-realtime-service
    spec:
      containers:
      - name: ws-service
        image: lq-realtime-service:latest
        ports:
        - containerPort: 8082
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: lq-config
              key: redis_host
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: lq-secrets
              key: jwt_secret
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8082
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8082
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: lq-realtime-service
  namespace: production
spec:
  selector:
    app: lq-realtime-service
  ports:
  - port: 80
    targetPort: 8082
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lq-realtime-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lq-realtime-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Load Balancing

### Nginx Configuration

```nginx
upstream websocket_backend {
    # Use IP hash for sticky sessions (recommended for WebSocket)
    ip_hash;

    server ws-instance-1:8082 max_fails=3 fail_timeout=30s;
    server ws-instance-2:8082 max_fails=3 fail_timeout=30s;
    server ws-instance-3:8082 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name realtime.linguoquesto.com;

    ssl_certificate /etc/ssl/certs/linguoquesto.crt;
    ssl_certificate_key /etc/ssl/private/linguoquesto.key;

    # WebSocket endpoint
    location /ws {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeout (24 hours)
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # HTTP endpoints
    location / {
        proxy_pass http://websocket_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### AWS Application Load Balancer

- Enable WebSocket support (automatic with target group)
- Set idle timeout to 3600 seconds
- Use target group with health checks on `/health`
- Enable sticky sessions (optional)

---

## Monitoring & Alerts

### CloudWatch Alarms (AWS)

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name lq-realtime-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# High memory alarm
aws cloudwatch put-metric-alarm \
    --alarm-name lq-realtime-high-memory \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold
```

### DataDog Integration

```python
# Add to app/main.py
from datadog import initialize, statsd

initialize(statsd_host='localhost', statsd_port=8125)

# In connection_manager
statsd.gauge('websocket.connections', len(self.active_connections))
statsd.increment('websocket.messages.sent')
```

---

## Backup & Recovery

### Redis Persistence

```conf
# redis.conf
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec
```

### Automated Backups (AWS)

```bash
# ElastiCache Redis - Automatic backups enabled
aws elasticache create-cache-cluster \
    --cache-cluster-id lq-redis-prod \
    --cache-node-type cache.r6g.large \
    --engine redis \
    --num-cache-nodes 1 \
    --snapshot-retention-limit 7 \
    --preferred-snapshot-window "03:00-05:00"
```

---

## Security Hardening

### Network Security

1. **VPC Configuration**: Deploy in private subnets
2. **Security Groups**: Allow only necessary ports
3. **WAF**: Configure AWS WAF for webhook endpoints
4. **DDoS Protection**: Enable AWS Shield or Cloudflare

### Application Security

```python
# Rate limiting with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/webhooks/{provider}")
@limiter.limit("100/minute")
async def webhook_route(...):
    ...
```

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets stored in secrets manager
- [ ] SSL/TLS certificates installed
- [ ] Load balancer configured
- [ ] Auto-scaling configured
- [ ] Health checks enabled
- [ ] Monitoring and alerts set up
- [ ] Logging aggregation configured
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented
- [ ] Security hardening completed
- [ ] Performance testing completed
- [ ] Documentation updated

---

## Rollback Strategy

### ECS Rollback

```bash
# List task definitions
aws ecs list-task-definitions --family-prefix lq-realtime-service

# Update service to previous version
aws ecs update-service \
    --cluster production \
    --service lq-realtime-service \
    --task-definition lq-realtime-service:PREVIOUS_VERSION
```

### Kubernetes Rollback

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/lq-realtime-service -n production

# Rollback to specific revision
kubectl rollout undo deployment/lq-realtime-service --to-revision=2 -n production
```

---

For more information, see the main [README.md](README.md).
docker build . -t registry.digitalocean.com/lq-registry/lq-realtime-service:qa-latest
docker push registry.digitalocean.com/lq-registry/lq-realtime-service:qa-latest

<!-- doctl apps create-deployment de02d338-6db0-4c53-b0da-3077a62fd3ea -->
