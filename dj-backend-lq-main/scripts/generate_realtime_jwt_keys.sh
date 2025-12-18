#!/usr/bin/env bash

#
# Generate RSA key pair for realtime JWT tokens
#
# This script generates:
# 1. Private key (for Django backend)
# 2. Public key (for lq-realtime-service)
# 3. .env configuration example
#

set -e

echo "🔐 Realtime JWT Key Generator"
echo "================================"
echo ""

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo "❌ Error: openssl is not installed"
    echo "   Install it with: sudo apt-get install openssl (Ubuntu/Debian)"
    echo "                 or: brew install openssl (macOS)"
    exit 1
fi

# Create keys directory if it doesn't exist
KEYS_DIR="./keys"
mkdir -p "$KEYS_DIR"

# File paths
PRIVATE_KEY_FILE="$KEYS_DIR/realtime-jwt-private.pem"
PUBLIC_KEY_FILE="$KEYS_DIR/realtime-jwt-public.pem"

# Check if keys already exist
if [ -f "$PRIVATE_KEY_FILE" ] || [ -f "$PUBLIC_KEY_FILE" ]; then
    echo "⚠️  Warning: Key files already exist:"
    [ -f "$PRIVATE_KEY_FILE" ] && echo "   - $PRIVATE_KEY_FILE"
    [ -f "$PUBLIC_KEY_FILE" ] && echo "   - $PUBLIC_KEY_FILE"
    echo ""
    read -p "   Do you want to overwrite them? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Existing keys preserved."
        exit 0
    fi
fi

# Generate private key (2048-bit RSA)
echo "🔑 Generating RSA private key (2048-bit)..."
openssl genrsa -out "$PRIVATE_KEY_FILE" 2048 2>/dev/null

# Extract public key
echo "🔓 Extracting public key..."
openssl rsa -in "$PRIVATE_KEY_FILE" -pubout -out "$PUBLIC_KEY_FILE" 2>/dev/null

echo "✅ Keys generated successfully!"
echo ""

# Display keys
echo "📄 Private Key (for Django backend):"
echo "-----------------------------------"
cat "$PRIVATE_KEY_FILE"
echo ""

echo "📄 Public Key (for lq-realtime-service):"
echo "---------------------------------------"
cat "$PUBLIC_KEY_FILE"
echo ""

# Generate .env configuration
ENV_EXAMPLE_FILE="$KEYS_DIR/realtime-jwt.env.example"

echo "📝 Generating .env configuration..."

# Convert keys to single-line format with \n
PRIVATE_KEY_ONELINE=$(cat "$PRIVATE_KEY_FILE" | sed ':a;N;$!ba;s/\n/\\n/g')
PUBLIC_KEY_ONELINE=$(cat "$PUBLIC_KEY_FILE" | sed ':a;N;$!ba;s/\n/\\n/g')

cat > "$ENV_EXAMPLE_FILE" << EOF
# Realtime JWT Configuration
# Copy this to your .env file

# Private key for signing realtime JWT tokens (keep this SECRET!)
# Note: The key is in single-line format with \n for line breaks
REALTIME_JWT_PRIVATE_KEY="$PRIVATE_KEY_ONELINE"

# Public key for verification (optional - mainly for testing)
# Share this with lq-realtime-service for token verification
REALTIME_JWT_PUBLIC_KEY="$PUBLIC_KEY_ONELINE"

# JWT Algorithm (RS256 for RSA, ES256 for ECDSA)
REALTIME_JWT_ALGORITHM=RS256

# Token expiration in minutes (5-10 minutes recommended)
REALTIME_JWT_EXPIRATION_MINUTES=10
EOF

echo "✅ Configuration example created: $ENV_EXAMPLE_FILE"
echo ""

# Security warnings
echo "⚠️  SECURITY REMINDERS:"
echo "   1. ❌ NEVER commit the private key to version control"
echo "   2. ✅ Add $KEYS_DIR/*.pem to .gitignore"
echo "   3. ✅ Copy the private key to your .env file"
echo "   4. ✅ Share the public key with lq-realtime-service"
echo "   5. ✅ Keep the private key secure and backed up"
echo ""

# Check if .gitignore exists and update it
if [ -f ".gitignore" ]; then
    if ! grep -q "keys/" ".gitignore"; then
        echo "📝 Adding keys/ to .gitignore..."
        echo "" >> .gitignore
        echo "# Realtime JWT keys" >> .gitignore
        echo "keys/" >> .gitignore
        echo "*.pem" >> .gitignore
        echo "✅ .gitignore updated"
    else
        echo "✅ .gitignore already contains keys/"
    fi
else
    echo "⚠️  Warning: .gitignore not found. Please add 'keys/' manually."
fi
echo ""

# Next steps
echo "🚀 NEXT STEPS:"
echo "   1. Copy the private key from $ENV_EXAMPLE_FILE to your .env file"
echo "   2. Restart your Django server"
echo "   3. Share the public key ($PUBLIC_KEY_FILE) with lq-realtime-service"
echo "   4. Test the endpoint: POST /api/realtime/token"
echo ""
echo "📚 For more information, see: REALTIME_JWT_SETUP.md"
echo ""
echo "✨ Done!"
