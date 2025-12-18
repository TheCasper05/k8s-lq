#!/bin/bash
#
# Quick setup script for CI/CD configuration
# This script helps you configure GitHub and DigitalOcean for deployment
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
print_header "Checking Prerequisites"

# Check if doctl is installed
if command -v doctl &> /dev/null; then
    print_success "doctl is installed"
else
    print_error "doctl is not installed"
    print_info "Install with: brew install doctl (macOS) or snap install doctl (Linux)"
    exit 1
fi

# Check if doctl is authenticated
if doctl auth list &> /dev/null; then
    print_success "doctl is authenticated"
else
    print_error "doctl is not authenticated"
    print_info "Run: doctl auth init"
    exit 1
fi

# Check if gh CLI is installed (optional)
if command -v gh &> /dev/null; then
    print_success "GitHub CLI is installed"
    GH_CLI=true
else
    print_warning "GitHub CLI not installed (optional)"
    print_info "Install with: brew install gh (macOS) or visit: https://cli.github.com/"
    GH_CLI=false
fi

# Get GitHub organization/username
print_header "GitHub Configuration"
read -p "Enter your GitHub username or organization: " GITHUB_ORG

if [ -z "$GITHUB_ORG" ]; then
    print_error "GitHub org/username is required"
    exit 1
fi

print_info "GitHub org/username: $GITHUB_ORG"

# Update app spec files
print_header "Updating App Spec Files"

# Update staging app spec
sed -i.bak "s|YOUR_GITHUB_ORG|$GITHUB_ORG|g" .do/app-staging.yaml
print_success "Updated .do/app-staging.yaml"

# Update production app spec
sed -i.bak "s|YOUR_GITHUB_ORG|$GITHUB_ORG|g" .do/app-production.yaml
print_success "Updated .do/app-production.yaml"

# Remove backup files
rm -f .do/app-staging.yaml.bak .do/app-production.yaml.bak

# Create DigitalOcean apps
print_header "Creating DigitalOcean Apps"

read -p "Create DigitalOcean apps? (y/n): " CREATE_APPS

if [ "$CREATE_APPS" = "y" ]; then
    # Create staging app
    print_info "Creating staging app..."
    STAGING_OUTPUT=$(doctl apps create --spec .do/app-staging.yaml --format ID --no-header 2>&1)

    if [ $? -eq 0 ]; then
        STAGING_APP_ID=$STAGING_OUTPUT
        print_success "Staging app created: $STAGING_APP_ID"
    else
        print_error "Failed to create staging app"
        print_info "$STAGING_OUTPUT"
        exit 1
    fi

    # Create production app
    print_info "Creating production app..."
    PROD_OUTPUT=$(doctl apps create --spec .do/app-production.yaml --format ID --no-header 2>&1)

    if [ $? -eq 0 ]; then
        PROD_APP_ID=$PROD_OUTPUT
        print_success "Production app created: $PROD_APP_ID"
    else
        print_error "Failed to create production app"
        print_info "$PROD_OUTPUT"
        exit 1
    fi
else
    print_warning "Skipping app creation"
    print_info "List existing apps with: doctl apps list"
    read -p "Enter staging app ID (or press Enter to skip): " STAGING_APP_ID
    read -p "Enter production app ID (or press Enter to skip): " PROD_APP_ID
fi

# Display next steps
print_header "Setup Complete!"

echo ""
print_success "CI/CD configuration is ready!"
echo ""

print_info "Next steps:"
echo ""
echo "1. Add GitHub Secrets:"
echo "   Go to: Settings → Secrets and variables → Actions"
echo ""
echo "   Required secrets:"
echo "   - DIGITALOCEAN_ACCESS_TOKEN"

if [ ! -z "$STAGING_APP_ID" ]; then
    echo "   - DO_APP_ID_STAGING=$STAGING_APP_ID"
fi

if [ ! -z "$PROD_APP_ID" ]; then
    echo "   - DO_APP_ID_PRODUCTION=$PROD_APP_ID"
fi

echo ""
echo "2. Configure DigitalOcean App Environment Variables:"
echo "   - LQBOT_OPENAI_API_KEY (mark as secret)"
echo "   - LQBOT_GROK_API_KEY (mark as secret, if using)"
echo "   - LQBOT_ELEVENLABS_API_KEY (mark as secret, if using)"
echo ""

if [ ! -z "$STAGING_APP_ID" ]; then
    echo "   Staging: https://cloud.digitalocean.com/apps/$STAGING_APP_ID/settings"
fi

if [ ! -z "$PROD_APP_ID" ]; then
    echo "   Production: https://cloud.digitalocean.com/apps/$PROD_APP_ID/settings"
fi

echo ""
echo "3. Update Dependabot configuration:"
echo "   Edit .github/dependabot.yml and replace 'YOUR_GITHUB_USERNAME'"
echo ""
echo "4. Enable GitHub security features:"
echo "   Go to: Settings → Code security and analysis"
echo "   Enable: CodeQL, Dependabot, Secret scanning"
echo ""
echo "5. Create GitHub Environments:"
echo "   Go to: Settings → Environments"
echo "   Create: 'staging' and 'production'"
echo ""
echo "6. Test deployment:"
echo "   git checkout staging"
echo "   git push origin staging"
echo ""

print_info "For detailed instructions, see: docs/CICD_SETUP.md"
echo ""

# Optional: Set GitHub secrets via CLI
if [ "$GH_CLI" = true ]; then
    read -p "Do you want to set GitHub secrets now via gh CLI? (y/n): " SET_SECRETS

    if [ "$SET_SECRETS" = "y" ]; then
        print_header "Setting GitHub Secrets"

        read -sp "Enter your DigitalOcean access token: " DO_TOKEN
        echo ""

        if [ ! -z "$DO_TOKEN" ]; then
            echo "$DO_TOKEN" | gh secret set DIGITALOCEAN_ACCESS_TOKEN
            print_success "Set DIGITALOCEAN_ACCESS_TOKEN"
        fi

        if [ ! -z "$STAGING_APP_ID" ]; then
            echo "$STAGING_APP_ID" | gh secret set DO_APP_ID_STAGING
            print_success "Set DO_APP_ID_STAGING"
        fi

        if [ ! -z "$PROD_APP_ID" ]; then
            echo "$PROD_APP_ID" | gh secret set DO_APP_ID_PRODUCTION
            print_success "Set DO_APP_ID_PRODUCTION"
        fi

        print_success "GitHub secrets configured!"
    fi
fi

print_success "Setup complete! 🎉"
