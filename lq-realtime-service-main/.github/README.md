# GitHub Actions Workflows

This directory contains CI/CD pipelines for the LQ Real-time Service.

## Workflows

### [`ci.yml`](workflows/ci.yml)
**Continuous Integration Pipeline**

Runs on every push and pull request to validate code quality and functionality.

**Jobs:**
- `code-quality` - Linting (Black, Ruff) and type checking (mypy)
- `secret-scanning` - Scans for leaked secrets using TruffleHog
- `test` - Runs unit tests with coverage reporting
- `docker-build` - Builds Docker image to verify Dockerfile
- `ci-summary` - Summarizes all CI results

**Triggers:**
- Push to any branch
- Pull requests to `main` or `staging`
- Manual dispatch
- Called by other workflows

---

### [`pr-checks.yml`](workflows/pr-checks.yml)
**Pull Request Checks**

Additional checks specifically for pull requests.

**Jobs:**
- `pr-info` - Adds size labels to PRs (XS, S, M, L, XL)
- `lint-check` - Fast linting with PR comments on failure
- `test-coverage` - Generates coverage report and comments on PR

**Triggers:**
- Pull request opened, synchronized, or reopened

---

### [`deploy-staging.yml`](workflows/deploy-staging.yml)
**Deploy to Staging (QA) Environment**

Deploys the service to DigitalOcean App Platform staging environment.

**Jobs:**
- `ci-check` - Runs full CI pipeline
- `build-and-push` - Builds and pushes Docker image to DO registry
- `deploy` - Deploys to DigitalOcean with health checks

**Triggers:**
- Push to `staging` branch
- Manual dispatch

**Environment:** `qa`
- Requires `DO_APP_ID` secret
- Requires `APP_URL` variable

---

### [`deploy-production.yml`](workflows/deploy-production.yml)
**Deploy to Production Environment**

Deploys the service to DigitalOcean App Platform production environment.

**Jobs:**
- `ci-check` - Runs full CI pipeline
- `security-check` - Additional security validation
- `build-and-push` - Builds and pushes production Docker image
- `deploy` - Deploys to production with extended health checks

**Triggers:**
- Push to `main` branch
- Manual dispatch

**Environment:** `production`
- Requires `DO_APP_ID` secret
- Requires `APP_URL` variable
- Includes smoke tests

---

## Required Secrets

### Repository Secrets

Configure these in: `Settings > Secrets and variables > Actions`

| Secret | Description | How to Get |
|--------|-------------|------------|
| `DO_ACCESS_TOKEN` | DigitalOcean API token | [Create token](https://cloud.digitalocean.com/account/api/tokens) |
| `DO_REGISTRY_TOKEN` | Container registry token | Same as `DO_ACCESS_TOKEN` |
| `DO_REGISTRY_NAME` | Registry name | `doctl registry get` |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | Optional: Slack App settings |

### Environment Secrets

#### QA Environment

Configure in: `Settings > Environments > qa`

| Secret/Variable | Type | Description |
|----------------|------|-------------|
| `DO_APP_ID` | Secret | Staging app ID from DigitalOcean |
| `APP_URL` | Variable | Staging app URL |

#### Production Environment

Configure in: `Settings > Environments > production`

| Secret/Variable | Type | Description |
|----------------|------|-------------|
| `DO_APP_ID` | Secret | Production app ID from DigitalOcean |
| `APP_URL` | Variable | Production app URL |

---

## Dependabot

[`dependabot.yml`](dependabot.yml) configures automatic dependency updates.

**Updates:**
- Python dependencies (weekly, Mondays 9:00 AM)
- GitHub Actions (weekly)
- Docker base images (weekly)

**Features:**
- Groups minor/patch updates
- Ignores major version updates for critical packages (FastAPI, uvicorn, websockets, redis)
- Auto-assigns to `lingoquesto/owners`

---

## Usage

### Running CI Locally

```bash
# Install dependencies
make install

# Run linting
make lint

# Run formatting
make format

# Run tests
make test

# Build Docker image
make docker-build
```

### Deploying

**To Staging:**
```bash
git checkout staging
git merge develop
git push origin staging
```

**To Production:**
```bash
git checkout main
git merge staging
git push origin main
```

### Manual Deployment

Use workflow dispatch in GitHub Actions UI:
1. Go to Actions tab
2. Select workflow (deploy-staging or deploy-production)
3. Click "Run workflow"
4. Select branch and environment

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Developer                            │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────┐
    │  Push/PR      │
    └───────┬───────┘
            │
            ├─────────────────┬─────────────────┐
            ▼                 ▼                 ▼
    ┌───────────┐     ┌──────────┐     ┌──────────┐
    │    CI     │     │ PR Checks│     │ Deploy   │
    │ (all)     │     │  (PRs)   │     │(staging/ │
    │           │     │          │     │  prod)   │
    └─────┬─────┘     └────┬─────┘     └────┬─────┘
          │                │                │
          ▼                ▼                ▼
    ┌──────────────────────────────────────────┐
    │          Lint + Test + Build            │
    └──────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  DigitalOcean         │
            │  App Platform         │
            └───────────────────────┘
```

---

## Best Practices

### Branch Strategy

```
main (production)
  ↑
staging (QA)
  ↑
develop (development)
  ↑
feature/* (features)
```

### Commit Messages

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `deps:` - Dependency updates
- `ci:` - CI/CD changes

### Testing

- All tests must pass before merging
- Maintain > 80% code coverage
- Add tests for new features

### Deployment

- Always deploy to staging first
- Test in staging before production
- Use manual approval for production
- Monitor logs after deployment

---

## Troubleshooting

### CI Failing

**Linting errors:**
```bash
make format  # Auto-fix formatting
make lint    # Check for issues
```

**Test failures:**
```bash
# Run tests locally with Redis
docker run -d -p 6379:6379 redis:7-alpine
make test
```

**Docker build fails:**
```bash
# Test build locally
make docker-build
```

### Deployment Failing

**Check logs:**
```bash
# View workflow logs in GitHub Actions
# Or check DigitalOcean logs
doctl apps logs <app-id> --follow
```

**Verify secrets:**
- Check all required secrets are configured
- Verify DO_APP_ID matches the app

**Health check failing:**
```bash
# Test health endpoint
curl https://your-app-url/health
```

---

## Monitoring

### GitHub Actions

- View workflow runs: `Actions` tab
- Download artifacts: Build logs, coverage reports
- View deployment history

### DigitalOcean

```bash
# App status
doctl apps get <app-id>

# Logs
doctl apps logs <app-id> --follow

# Deployments
doctl apps list-deployments <app-id>
```

---

## Security

### Secret Scanning

- Automated scanning with TruffleHog
- Scans every commit for leaked secrets
- Fails CI if secrets detected

### Dependency Updates

- Dependabot creates PRs for updates
- Review and merge promptly
- Security updates are prioritized

### Production Safeguards

- Manual approval required (via environment)
- Extended health checks
- Rollback capability

---

For more information, see:
- [Main README](../README.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Architecture Documentation](../ARCHITECTURE.md)
