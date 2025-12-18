#!/bin/bash

# Script to switch between local and QA backend

case "$1" in
  local)
    echo "🔄 Switching to LOCAL backend (HTTP)"
    cat > .env << 'EOF'
# API Configuration
# Local Backend (HTTP to HTTP works perfectly)
VITE_API_BASE_URL=http://localhost:8000
VITE_GRAPHQL_ENDPOINT=http://localhost:8000/graphql/
VITE_GRAPHQL_WS_ENDPOINT=ws://localhost:8000/graphql/

# QA Backend (HTTPS - requires HTTPS frontend via ngrok/cloudflared)
# VITE_API_BASE_URL=https://api-qa.lingoquesto.com
# VITE_GRAPHQL_ENDPOINT=https://api-qa.lingoquesto.com/graphql/
# VITE_GRAPHQL_WS_ENDPOINT=wss://lq-backend-qa-lkbq4.ondigitalocean.app/graphql/

# Sentry Configuration
VITE_SENTRY_DSN=
VITE_ENVIRONMENT=development

# App Configuration
NODE_ENV=development
EOF
    echo "✅ Switched to LOCAL backend"
    echo "ℹ️  Make sure Django is running on http://localhost:8000"
    ;;

  qa)
    echo "🔄 Switching to QA backend (HTTPS)"
    cat > .env << 'EOF'
# API Configuration
# QA Backend (HTTPS - requires HTTPS frontend via ngrok/cloudflared)
VITE_API_BASE_URL=https://api-qa.lingoquesto.com
VITE_GRAPHQL_ENDPOINT=https://api-qa.lingoquesto.com/graphql/
VITE_GRAPHQL_WS_ENDPOINT=wss://lq-backend-qa-lkbq4.ondigitalocean.app/graphql/

# Local Backend (HTTP to HTTP works perfectly)
# VITE_API_BASE_URL=http://localhost:8000
# VITE_GRAPHQL_ENDPOINT=http://localhost:8000/graphql/
# VITE_GRAPHQL_WS_ENDPOINT=ws://localhost:8000/graphql/

# Sentry Configuration
VITE_SENTRY_DSN=
VITE_ENVIRONMENT=qa

# App Configuration
NODE_ENV=development
EOF
    echo "✅ Switched to QA backend"
    echo "⚠️  IMPORTANT: You need HTTPS frontend for QA backend to work!"
    echo "   Run one of these:"
    echo "   - cloudflared tunnel --url http://localhost:3002"
    echo "   - ngrok http 3002"
    ;;

  *)
    echo "Usage: $0 {local|qa}"
    echo ""
    echo "Examples:"
    echo "  $0 local  - Switch to local backend (http://localhost:8000)"
    echo "  $0 qa     - Switch to QA backend (requires HTTPS tunnel)"
    exit 1
    ;;
esac
