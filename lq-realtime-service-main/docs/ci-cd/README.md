# Deployment Specifications

This directory contains DigitalOcean App Platform specifications for deploying the LQ Real-time Service.

## Files

- [`app-spec-staging.yaml`](app-spec-staging.yaml) - Staging/QA environment configuration
- [`app-spec-production.yaml`](app-spec-production.yaml) - Production environment configuration

## Prerequisites

1. **DigitalOcean Account** with App Platform access
2. **doctl CLI** installed and configured
   ```bash
   # Install doctl
   brew install doctl  # macOS
   # or download from https://docs.digitalocean.com/reference/doctl/how-to/install/

   # Authenticate
   doctl auth init
   ```

3. **Container Registry** created in DigitalOcean
   ```bash
   # Create registry
   doctl registry create lq-registry

   # Get registry name
   doctl registry get
   ```

4. **GitHub Secrets** configured:
   - `DO_ACCESS_TOKEN` - DigitalOcean API token
   - `DO_REGISTRY_TOKEN` - Container registry token
   - `DO_REGISTRY_NAME` - Registry name (e.g., `lq-registry`)
   - `DO_APP_ID` - App ID (after first deployment)

## Initial Setup

### 1. Update App Specifications

Edit both spec files and replace placeholders:

```yaml
# In both app-spec-staging.yaml and app-spec-production.yaml
image:
  registry: YOUR_REGISTRY_NAME  # Replace with your registry name

envs:
  - key: JWT_SECRET_KEY
    value: YOUR_JWT_SECRET_KEY  # Replace with actual secret
```

### 2. Create DigitalOcean Apps

**Staging:**
```bash
# Create staging app
doctl apps create --spec deploy/app-spec-staging.yaml

# Get app ID
doctl apps list
# Save the ID as DO_APP_ID in GitHub Environment secrets (qa)
```

**Production:**
```bash
# Create production app
doctl apps create --spec deploy/app-spec-production.yaml

# Get app ID
doctl apps list
# Save the ID as DO_APP_ID in GitHub Environment secrets (production)
```

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository:

**Repository Secrets:**
- `DO_ACCESS_TOKEN` - Your DigitalOcean API token
- `DO_REGISTRY_TOKEN` - Container registry token
- `DO_REGISTRY_NAME` - Your registry name

**Environment Secrets (qa):**
- `DO_APP_ID` - Staging app ID from step 2
- `APP_URL` - Staging app URL (e.g., `https://lq-realtime-staging-xxx.ondigitalocean.app`)

**Environment Secrets (production):**
- `DO_APP_ID` - Production app ID from step 2
- `APP_URL` - Production app URL (e.g., `https://lq-realtime-production-xxx.ondigitalocean.app`)

### 4. Configure Custom Domains (Optional)

```bash
# Add custom domain to app
doctl apps create-domain <app-id> --domain realtime.linguoquesto.com

# Get DNS configuration
doctl apps get-domain <app-id> realtime.linguoquesto.com
```

## Deployment Process

### Automated Deployment (Recommended)

Push to branches to trigger automatic deployments:

```bash
# Deploy to Staging
git push origin staging

# Deploy to Production
git push origin main
```

GitHub Actions will automatically:
1. Run CI tests
2. Build Docker image
3. Push to DigitalOcean Container Registry
4. Trigger app deployment
5. Run health checks
6. Notify on Slack (if configured)

### Manual Deployment

```bash
# Update staging
doctl apps update <staging-app-id> --spec deploy/app-spec-staging.yaml

# Update production
doctl apps update <production-app-id> --spec deploy/app-spec-production.yaml
```

## Scaling

### Manual Scaling

```bash
# Scale to 5 instances
doctl apps update <app-id> --spec deploy/app-spec-production.yaml
# Edit spec file first to set instance_count: 5
```

### Auto-scaling

Production spec includes auto-scaling configuration:
- Min: 3 instances
- Max: 10 instances
- Trigger: CPU > 70%

## Monitoring

### View Logs

```bash
# Real-time logs
doctl apps logs <app-id> --follow

# Specific component
doctl apps logs <app-id> --component ws-service --follow
```

### View Metrics

```bash
# App metrics
doctl apps get <app-id>

# Component metrics
doctl monitoring bandwidth list --format json
```

### Health Checks

```bash
# Check app health
curl https://your-app-url.ondigitalocean.app/health

# Check metrics
curl https://your-app-url.ondigitalocean.app/metrics
```

## Configuration

### Environment Variables

To update environment variables:

1. Edit the spec file
2. Run update command:
   ```bash
   doctl apps update <app-id> --spec deploy/app-spec-staging.yaml
   ```

### Resource Limits

**Staging:**
- Instance Size: `basic-xs` (512MB RAM, 1 vCPU)
- Instance Count: 2
- Cost: ~$10/month

**Production:**
- Instance Size: `professional-xs` (1GB RAM, 1 vCPU)
- Instance Count: 3-10 (auto-scaling)
- Cost: ~$36-120/month

## Troubleshooting

### Deployment Failed

```bash
# Check deployment logs
doctl apps logs <app-id> --type deploy

# Check app status
doctl apps get <app-id>
```

### App Not Responding

```bash
# Check health
curl https://your-app-url/health

# View logs
doctl apps logs <app-id> --follow

# Restart app
doctl apps create-deployment <app-id>
```

### Redis Connection Issues

```bash
# Check Redis status
doctl databases list

# Get Redis connection info
doctl databases connection <redis-id>
```

## Rollback

```bash
# List deployments
doctl apps list-deployments <app-id>

# Rollback to previous deployment
doctl apps create-deployment <app-id> --rollback-to <deployment-id>
```

## Cost Optimization

### Staging
- Use `basic-xs` instances
- 2 instances minimum
- ~$10/month

### Production
- Start with 3 instances
- Enable auto-scaling
- Monitor usage and adjust

### Tips
- Use alerts to monitor costs
- Scale down during off-peak hours (manual)
- Consider reserved pricing for predictable workloads

## Security Best Practices

1. **Use Secrets** - Never commit secrets to git
2. **Enable HTTPS** - Always use SSL/TLS
3. **Restrict CORS** - Whitelist specific origins only
4. **Rotate Secrets** - Rotate JWT secrets regularly
5. **Monitor Logs** - Set up log aggregation

## Support

For issues or questions:
- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- GitHub Issues: https://github.com/your-org/lq-realtime-service/issues
- Main README: [../README.md](../README.md)
