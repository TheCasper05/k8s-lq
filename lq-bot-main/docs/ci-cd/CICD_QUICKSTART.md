# CI/CD Quick Start Guide

Get your CI/CD pipeline up and running in 15 minutes.

## Prerequisites

- GitHub Enterprise account
- DigitalOcean account
- `doctl` CLI installed and authenticated
- `gh` CLI installed (optional, but recommended)

## Quick Setup (5 Steps)

### Step 1: Install Tools (2 minutes)

```bash
# macOS
brew install doctl gh

# Linux
snap install doctl
# For gh: https://cli.github.com/

# Authenticate doctl
doctl auth init

# Authenticate gh (optional)
gh auth login
```

### Step 2: Run Setup Script (5 minutes)

```bash
# Make script executable (if not already)
chmod +x scripts/setup-cicd.sh

# Run setup
./scripts/setup-cicd.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Update app specs with your GitHub org
- ✅ Create DigitalOcean apps (staging & production)
- ✅ Optionally set GitHub secrets

### Step 3: Configure GitHub Secrets (3 minutes)

Go to your repository → `Settings` → `Secrets and variables` → `Actions`

Add these secrets (if not done by script):

```
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxxxxxxxxxx
DO_APP_ID_STAGING=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DO_APP_ID_PRODUCTION=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Step 4: Configure DigitalOcean Environment Variables (3 minutes)

For each app (staging and production), add these **encrypted** environment variables:

1. Go to https://cloud.digitalocean.com/apps
2. Select app → Settings → Environment Variables
3. Add secrets (mark as "Encrypt"):

```bash
LQBOT_OPENAI_API_KEY=sk-xxxxx
LQBOT_GROK_API_KEY=xai-xxxxx  # if using Grok
LQBOT_ELEVENLABS_API_KEY=xxxxx  # if using Eleven Labs
```

### Step 5: Enable GitHub Features (2 minutes)

Go to `Settings` → `Code security and analysis`

Enable:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ CodeQL analysis
- ✅ Secret scanning

## Test Your Setup

### Test Staging Deployment

```bash
# Create a test change
git checkout staging
echo "# Test" >> README.md
git add README.md
git commit -m "test: CI/CD staging deployment"
git push origin staging
```

Watch the deployment:
1. Go to `Actions` tab in GitHub
2. See workflow `Deploy to Staging (QA)` running
3. Wait for completion (~5 minutes)
4. Visit your staging URL

### Test Production Deployment

```bash
# Merge staging to main
git checkout main
git merge staging
git push origin main
```

Watch the deployment:
1. Go to `Actions` tab
2. See workflow `Deploy to Production` running
3. Wait for completion (~5 minutes)
4. Visit your production URL

## Verify Everything Works

### 1. Check CI Pipeline

Create a test PR:

```bash
git checkout -b test/ci-check
echo "# CI Test" >> README.md
git add README.md
git commit -m "test: CI pipeline"
git push origin test/ci-check
```

Create PR on GitHub → Check that all CI jobs pass:
- ✅ Code Quality & Security
- ✅ CodeQL Security Analysis
- ✅ Dependency Review
- ✅ Secret Scanning
- ✅ Tests (Python 3.11, 3.12)
- ✅ Docker Build Test

### 2. Check Deployments

Visit your apps:

```bash
# Get URLs
doctl apps list

# Or check in GitHub Actions workflow output
```

Expected URLs:
- Staging: `https://lq-bot-staging-xxxxx.ondigitalocean.app`
- Production: `https://lq-bot-production-xxxxx.ondigitalocean.app`

Test endpoints:

```bash
# Health check
curl https://your-app-url/health

# API docs
curl https://your-app-url/docs
```

### 3. Check Monitoring

**GitHub:**
- Actions → Workflows → See all workflows
- Environments → See deployment history

**DigitalOcean:**
```bash
# View logs
doctl apps logs <app-id> --follow

# View app status
doctl apps get <app-id>
```

## Common First-Time Issues

### Issue: "GitHub secrets not found"

**Solution:**
```bash
# Set via gh CLI
echo "your-token" | gh secret set DIGITALOCEAN_ACCESS_TOKEN

# Or manually in GitHub UI:
# Settings → Secrets and variables → Actions → New secret
```

### Issue: "doctl auth failed"

**Solution:**
```bash
# Re-authenticate
doctl auth init

# Verify
doctl auth list
```

### Issue: "Docker image not found"

**Solution:**
- Make sure you pushed to the correct branch (staging or main)
- Check GitHub Container Registry permissions
- Verify image tag in app spec matches workflow output

### Issue: "Health check fails"

**Solution:**
```bash
# Check app logs
doctl apps logs <app-id>

# Common causes:
# - Missing environment variables
# - Wrong PORT configuration (should be 8081)
# - App not starting correctly
```

## Next Steps

✅ Your CI/CD is now set up! Here's what happens automatically:

### On Pull Requests:
1. Runs linting and formatting checks
2. Runs security scanning (CodeQL, secrets)
3. Runs all tests with coverage report
4. Builds Docker image
5. Posts coverage report as PR comment

### On Push to `staging`:
1. Runs full CI pipeline
2. Builds and pushes Docker image
3. Deploys to DigitalOcean staging
4. Runs health checks
5. Posts deployment notification

### On Push to `main`:
1. Runs full CI pipeline
2. Builds and pushes Docker image
3. Deploys to DigitalOcean production
4. Runs health checks and smoke tests
5. Posts deployment notification

## Customization

### Change Instance Size

Edit `.do/app-staging.yaml` or `.do/app-production.yaml`:

```yaml
instance_size_slug: basic-xxs  # $5/month - 512MB RAM
# or
instance_size_slug: basic-xs   # $12/month - 1GB RAM
# or
instance_size_slug: basic-s    # $24/month - 2GB RAM
```

### Add Custom Domain

```bash
# Via doctl
doctl apps create-domain <app-id> --domain yourdomain.com

# Or in DigitalOcean UI:
# Apps → Select App → Settings → Domains
```

### Configure Auto-scaling

Edit `.do/app-production.yaml`:

```yaml
autoscaling:
  min_instance_count: 2
  max_instance_count: 5
  metrics:
    cpu:
      percent: 70  # Scale up when CPU > 70%
```

### Add Slack Notifications

Add to workflow files:

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Deployment completed: ${{ job.status }}"
      }
```

## Resources

- **Full Documentation**: [CICD_SETUP.md](CICD_SETUP.md)
- **GitHub Actions**: https://docs.github.com/en/actions
- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/

## Support

If you run into issues:

1. Check [CICD_SETUP.md](CICD_SETUP.md) troubleshooting section
2. Review GitHub Actions logs
3. Check DigitalOcean app logs: `doctl apps logs <app-id>`
4. Create GitHub issue with error details

---

**That's it! Your CI/CD pipeline is ready.** 🚀

Every push to `staging` or `main` will now automatically deploy to DigitalOcean.
