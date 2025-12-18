#!/bin/bash

##############################################################################
# Droplet Setup Script for LQ Realtime Service
#
# This script prepares a fresh DigitalOcean Droplet for deploying the
# LQ Realtime Service using Docker and Docker Compose.
#
# Usage:
#   1. SSH into your droplet: ssh root@your-droplet-ip
#   2. Download this script: wget https://raw.githubusercontent.com/YOUR_ORG/lq-realtime-service/main/scripts/setup-droplet.sh
#   3. Make it executable: chmod +x setup-droplet.sh
#   4. Run it: ./setup-droplet.sh
##############################################################################

set -e

echo "=========================================="
echo "LQ Realtime Service - Droplet Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

# Update system
echo "[1/8] Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install required packages
echo "[2/8] Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    ufw \
    fail2ban

# Install Docker
echo "[3/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "[4/8] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed"
fi

# Configure firewall
echo "[5/8] Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8082/tcp  # WebSocket service port
echo "Firewall configured"

# Configure fail2ban
echo "[6/8] Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban
echo "Fail2ban configured"

# Create application directory
echo "[7/8] Creating application directory..."
mkdir -p /opt/lq-realtime-service
cd /opt/lq-realtime-service

# Download docker-compose.production.yml
echo "[8/8] Downloading docker-compose configuration..."
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  ws-service:
    image: ${DOCKER_IMAGE:-registry.digitalocean.com/lq-registry/lq-realtime-service:latest}
    container_name: lq-ws-service
    ports:
      - "8082:8082"
    environment:
      # Application
      - APP_NAME=lq-realtime-service
      - APP_VERSION=${APP_VERSION:-1.0.0}
      - DEBUG=false
      - ENVIRONMENT=${ENVIRONMENT:-production}

      # Server
      - HOST=0.0.0.0
      - PORT=8082
      - WORKERS=1

      # JWT Configuration
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

      # Redis Configuration
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT:-6379}
      - REDIS_DB=${REDIS_DB:-0}
      - REDIS_PASSWORD=${REDIS_PASSWORD:-}
      - REDIS_MAX_CONNECTIONS=200

      # WebSocket Configuration
      - WS_MAX_CONNECTIONS_PER_INSTANCE=10000
      - WS_HEARTBEAT_INTERVAL=30
      - WS_MESSAGE_MAX_SIZE=65536

      # Security
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - CORS_ENABLED=true

      # Logging
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json

      # Metrics
      - METRICS_ENABLED=true

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

    restart: unless-stopped

    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

    networks:
      - lq-network

    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  lq-network:
    driver: bridge
EOF

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Configure GitHub Secrets for your environment:"
echo "     - DROPLET_HOST (this droplet's IP)"
echo "     - DROPLET_USER (default: root)"
echo "     - SSH_PRIVATE_KEY (SSH private key with access to this droplet)"
echo "     - REDIS_HOST (your Redis instance)"
echo "     - REDIS_PORT (default: 6379)"
echo "     - REDIS_PASSWORD (if Redis has authentication)"
echo "     - JWT_SECRET_KEY (strong secret key, min 32 chars)"
echo "     - DO_REGISTRY_TOKEN (DigitalOcean Container Registry token)"
echo ""
echo "  2. Push code to trigger GitHub Actions deployment"
echo ""
echo "  3. Monitor deployment logs in GitHub Actions"
echo ""
echo "  4. Verify service health:"
echo "     curl http://$(hostname -I | awk '{print $1}'):8082/health"
echo ""
echo "Application directory: /opt/lq-realtime-service"
echo "Docker Compose file: /opt/lq-realtime-service/docker-compose.production.yml"
echo ""
