# CI/CD Setup Guide

Complete guide for setting up continuous integration and deployment for LingoBot using GitHub Actions and DigitalOcean App Platform.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [GitHub Configuration](#github-configuration)
4. [DigitalOcean Configuration](#digitalocean-configuration)
5. [Deployment Workflow](#deployment-workflow)
6. [Monitoring and Alerts](#monitoring-and-alerts)
7. [Troubleshooting](#troubleshooting)

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────────┐   │
│  │   main    │  │  staging  │  │  feature branches    │   │
│  └─────┬─────┘  └─────┬─────┘  └──────────┬───────────┘   │
└────────┼──────────────┼───────────────────┼───────────────┘
         │              │                   │
         │              │                   │
    ┌────▼────┐    ┌────▼────┐        ┌────▼────┐
    │ CI/CD   │    │ CI/CD   │        │   CI    │
    │ (Prod)  │    │ (Stage) │        │  Tests  │
    └────┬────┘    └────┬────┘        └─────────┘
         │              │
         │              │
    ┌────▼────────┐┌────▼────────┐
    │ Production  ││  Staging    │
    │    (DO)     ││    (DO)     │
    └─────────────┘└─────────────┘
```

### Environments

- **Production** (`main` branch) → https://lq-bot-production.ondigitalocean.app
- **Staging/QA** (`staging` branch) → https://lq-bot-staging.ondigitalocean.app

### CI/CD Features

✅ **Automated Testing**
- Unit tests with pytest
- Integration tests
- Code coverage reporting
- Multi-version Python testing (3.11, 3.12)

✅ **Code Quality**
- Ruff linting and formatting
- Type checking with mypy
- Code style enforcement

✅ **Security Scanning** (GitHub Enterprise)
- CodeQL analysis
- Secret scanning with TruffleHog
- Dependency review
- Container image signing
- SBOM generation

✅ **Automated Deployment**
- Docker containerization
- Multi-stage builds for optimization
- GitHub Container Registry (GHCR)
- DigitalOcean App Platform integration

✅ **Dependency Management**
- Dependabot for automated updates
- Grouped updates for efficiency
- Automatic PR creation

## Prerequisites

### Required Accounts

1. **GitHub Enterprise** account
2. **DigitalOcean** account
3. **GitHub Container Registry** access (included with GitHub Enterprise)

### Required Tools (for local development)

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate doctl
doctl auth init
```

## GitHub Configuration

### 1. Enable GitHub Enterprise Features

Go to your repository settings and enable:

1. **Security & Analysis**
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ CodeQL analysis
   - ✅ Secret scanning

2. **Code security and analysis**
   - Navigate to: `Settings` → `Code security and analysis`
   - Enable all available features

### 2. Configure GitHub Secrets

Add the following secrets in `Settings` → `Secrets and variables` → `Actions`:

#### Required Secrets

```bash
# DigitalOcean Access Token
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxx

# DigitalOcean App IDs (created in step 3)
DO_APP_ID_STAGING=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DO_APP_ID_PRODUCTION=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

To get your DigitalOcean access token:
1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Generate New Token
3. Name: `GitHub Actions - LingoBot`
4. Scopes: Read and Write
5. Copy the token (you'll only see it once!)

### 3. Configure GitHub Environments

Create two environments with protection rules:

#### Staging Environment

1. Go to `Settings` → `Environments` → `New environment`
2. Name: `staging`
3. Configure:
   - ✅ Required reviewers: (optional for staging)
   - ✅ Wait timer: 0 minutes
   - Environment secrets:
     ```
     (Secrets are inherited from repository secrets)
     ```

#### Production Environment

1. Go to `Settings` → `Environments` → `New environment`
2. Name: `production`
3. Configure:
   - ✅ Required reviewers: Add team/individuals
   - ✅ Wait timer: 5 minutes (optional cooldown)
   - ✅ Deployment branches: `main` only
   - Environment secrets:
     ```
     (Secrets are inherited from repository secrets)
     ```

### 4. Update Dependabot Configuration

Edit [.github/dependabot.yml](.github/dependabot.yml):

```yaml
reviewers:
  - "YOUR_GITHUB_USERNAME"  # Replace with your username
assignees:
  - "YOUR_GITHUB_USERNAME"  # Replace with your username
```

## DigitalOcean Configuration

### 1. Create Apps on DigitalOcean

#### Option A: Using doctl CLI (Recommended)

```bash
# Create staging app
doctl apps create --spec .do/app-staging.yaml

# Create production app
doctl apps create --spec .do/app-production.yaml

# Get app IDs
doctl apps list
```

#### Option B: Using DigitalOcean Web UI

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Choose "Docker Hub or a container registry"
4. Select "GitHub Container Registry (GHCR)"
5. Connect your GitHub account
6. Select repository: `YOUR_ORG/lq-bot`
7. Choose tag: `staging-latest` (for staging) or `production-latest` (for production)
8. Configure:
   - **App Name**: `lq-bot-staging` or `lq-bot-production`
   - **Region**: Choose closest to your users (e.g., `nyc`)
   - **Instance Size**:
     - Staging: Basic - 512MB RAM ($5/month)
     - Production: Basic - 1GB RAM ($12/month)
   - **Instance Count**:
     - Staging: 1
     - Production: 2 (for high availability)

9. Add environment variables (see section below)
10. Deploy!

### 2. Configure Environment Variables

For each app (staging and production), add these environment variables:

#### Required Variables

```bash
# App Configuration
LQBOT_APP_NAME=lq-bot-staging  # or lq-bot-production
LQBOT_ENVIRONMENT=staging      # or production
LQBOT_LOG_LEVEL=DEBUG          # or INFO for production
PYTHONPATH=/app/src

# LLM Provider
LQBOT_LLM_PROVIDER=openai
LQBOT_OPENAI_LLM_MODEL=gpt-4o-mini

# TTS Provider
LQBOT_TTS_PROVIDER=openai
LQBOT_OPENAI_TTS_MODEL=tts-1
LQBOT_OPENAI_TTS_VOICE=alloy

# STT Provider
LQBOT_STT_PROVIDER=openai
LQBOT_OPENAI_STT_MODEL=whisper-1
```

#### Encrypted Secrets (mark as secret in DO UI)

```bash
LQBOT_OPENAI_API_KEY=sk-xxxxx
LQBOT_GROK_API_KEY=xai-xxxxx  # if using Grok
LQBOT_ELEVENLABS_API_KEY=xxxxx  # if using Eleven Labs
```

### 3. Update App Specs

Edit [.do/app-staging.yaml](.do/app-staging.yaml) and [.do/app-production.yaml](.do/app-production.yaml):

```yaml
image:
  registry_type: GHCR
  registry: ghcr.io
  repository: YOUR_GITHUB_ORG/lq-bot  # Update this!
  tag: staging-latest
```

Replace `YOUR_GITHUB_ORG` with your GitHub organization or username.

### 4. Get App IDs and Add to GitHub Secrets

```bash
# List apps and get IDs
doctl apps list

# Output will show:
# ID                                    App Name            Region    Phase
# xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  lq-bot-staging      nyc       ACTIVE
# yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy  lq-bot-production   nyc       ACTIVE
```

Add these IDs to GitHub Secrets:
- `DO_APP_ID_STAGING`
- `DO_APP_ID_PRODUCTION`

## Deployment Workflow

### Development Flow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push and create PR
git push origin feature/new-feature
# Create PR to staging

# 4. CI runs automatically
# - Runs tests
# - Linting
# - Security scanning
# - CodeQL analysis

# 5. Merge to staging
# - Triggers deployment to QA environment
# - Runs health checks
# - Creates deployment notification

# 6. Test in QA
# Visit: https://lq-bot-staging.ondigitalocean.app

# 7. Create PR from staging to main
# - CI runs again
# - Requires approval (configured in GitHub)

# 8. Merge to main
# - Triggers production deployment
# - Runs smoke tests
# - Creates deployment notification
```

### Manual Deployment

You can also trigger deployments manually:

1. Go to `Actions` tab in GitHub
2. Select workflow:
   - `Deploy to Staging (QA)`
   - `Deploy to Production`
3. Click `Run workflow`
4. Select branch
5. Click `Run workflow`

### Rollback Procedure

If a deployment fails or has issues:

#### Option 1: Revert via GitHub

```bash
# Revert the commit
git revert <commit-sha>
git push origin main  # or staging

# This triggers a new deployment with the reverted changes
```

#### Option 2: Rollback via DigitalOcean

```bash
# List deployments
doctl apps deployment list <app-id>

# Rollback to previous deployment
doctl apps deployment rollback <app-id> <deployment-id>
```

## Monitoring and Alerts

### GitHub Actions Monitoring

1. **Actions Dashboard**
   - View: `Actions` tab in GitHub repository
   - Monitor workflow runs
   - Download logs and artifacts

2. **Deployment Status**
   - View: `Environments` section
   - Shows deployment history
   - Deployment URLs

### DigitalOcean Monitoring

1. **App Dashboard**
   - Go to https://cloud.digitalocean.com/apps
   - Select your app
   - View metrics:
     - CPU usage
     - Memory usage
     - Request rate
     - Response time

2. **Logs**
   ```bash
   # View logs via doctl
   doctl apps logs <app-id> --follow

   # Or in DigitalOcean UI
   # Apps → Select App → Runtime Logs
   ```

3. **Alerts**
   - Configured in `.do/app-*.yaml`
   - Email notifications for:
     - Deployment failures
     - High CPU/memory usage
     - Domain issues

### Health Checks

Both environments expose a health check endpoint:

```bash
# Staging
curl https://lq-bot-staging.ondigitalocean.app/health

# Production
curl https://lq-bot-production.ondigitalocean.app/health

# Expected response:
{
  "status": "healthy",
  "environment": "staging",
  "version": "0.1.0"
}
```

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

**Symptom**: `docker-build` job fails

**Solutions**:
```bash
# Test build locally
docker build -t lq-bot:test .

# Check for syntax errors in Dockerfile
cat Dockerfile

# Verify all dependencies are in pyproject.toml
uv sync --all-extras --group dev
```

#### 2. Tests Fail in CI

**Symptom**: `test` job fails

**Solutions**:
```bash
# Run tests locally first
make test

# Check for environment-specific issues
# Ensure tests don't depend on local .env file

# Check test logs in GitHub Actions
# Actions → Failed workflow → test job → Logs
```

#### 3. Deployment Fails

**Symptom**: `deploy-staging` or `deploy-production` job fails

**Solutions**:
```bash
# Check DigitalOcean status
doctl apps get <app-id>

# Check deployment logs
doctl apps logs <app-id> --deployment <deployment-id>

# Verify environment variables in DO
# Apps → Select App → Settings → Environment Variables

# Check GitHub secrets are set correctly
# Settings → Secrets and variables → Actions
```

#### 4. Health Check Fails

**Symptom**: Health check step fails after deployment

**Solutions**:
```bash
# Check if app is running
doctl apps get <app-id>

# Check logs for errors
doctl apps logs <app-id> --follow

# Verify port configuration (should be 8081)
# Check Dockerfile EXPOSE and app spec http_port

# Test health endpoint manually
curl -v https://your-app.ondigitalocean.app/health
```

#### 5. CodeQL Analysis Fails

**Symptom**: `codeql-analysis` job fails

**Solutions**:
- Ensure Python dependencies are correctly specified
- Check CodeQL configuration in workflow
- Review CodeQL logs in Actions tab
- May need to exclude certain files/directories

#### 6. Secret Scanning Alerts

**Symptom**: TruffleHog or GitHub finds secrets

**Solutions**:
```bash
# Never commit real secrets
# Use .env files (git ignored)
# Use .env.example for templates

# If secret was committed:
# 1. Revoke the secret immediately
# 2. Remove from git history (use git filter-repo)
# 3. Generate new secret
# 4. Update in GitHub Secrets and DigitalOcean
```

### Getting Help

1. **GitHub Actions Logs**
   - Most detailed information
   - Download logs for offline analysis

2. **DigitalOcean Support**
   - Community: https://www.digitalocean.com/community
   - Support tickets for platform issues

3. **Project Issues**
   - Create GitHub issue with:
     - Error message
     - Workflow run link
     - Steps to reproduce

## Security Best Practices

1. **Never commit secrets**
   - Use GitHub Secrets
   - Use DigitalOcean encrypted env vars
   - Keep `.env` in `.gitignore`

2. **Keep dependencies updated**
   - Review Dependabot PRs weekly
   - Test updates in staging first

3. **Monitor security alerts**
   - Enable GitHub security alerts
   - Review CodeQL findings
   - Address critical vulnerabilities immediately

4. **Use branch protection**
   - Require PR reviews
   - Require status checks to pass
   - Restrict who can push to main/staging

5. **Audit access**
   - Review who has access to:
     - GitHub repository
     - DigitalOcean apps
     - GitHub Secrets
   - Use teams for access management

## Cost Optimization

### Current Costs (estimated)

- **Staging**: $5/month (Basic - 512MB RAM)
- **Production**: $24/month (2x Basic - 1GB RAM)
- **GitHub Actions**: Free for private repos in Enterprise
- **Container Registry**: Free in GitHub Enterprise

**Total**: ~$29/month

### Optimization Tips

1. **Reduce staging instance size** if traffic is low
2. **Use autoscaling** in production to scale down during off-peak
3. **Monitor unused resources** in DigitalOcean
4. **Review logs retention** settings

## Next Steps

1. ✅ Complete this setup guide
2. ✅ Test staging deployment
3. ✅ Test production deployment
4. ⬜ Set up monitoring dashboards (optional)
5. ⬜ Configure custom domain (optional)
6. ⬜ Set up Slack/Discord notifications (optional)
7. ⬜ Implement blue-green deployments (advanced)

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
