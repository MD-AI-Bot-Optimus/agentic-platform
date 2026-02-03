# Google Cloud Deployment Guide

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed locally
- Appropriate IAM permissions (Cloud Run, Container Registry)

## Deployment Steps

### 1. Configure Google Cloud

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Build and Push Container

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/agentic-platform:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/agentic-platform:latest
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy agentic-platform \
  --image gcr.io/$PROJECT_ID/agentic-platform:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production"
```

### 4. Configure Custom Domain (Optional)

```bash
gcloud run domain-mappings create \
  --service agentic-platform \
  --domain yourdomain.com \
  --region us-central1
```

## Environment Variables

Set these in Cloud Run environment:

- `ENVIRONMENT=production`
- `LOG_LEVEL=info`
- `GOOGLE_CLOUD_CREDENTIALS` (if using actual Google Vision)

## Monitoring

View logs and metrics:

```bash
gcloud run logs read agentic-platform --region us-central1 --limit 50

# View metrics
gcloud monitoring dashboards list
```

## Auto-scaling Configuration

Cloud Run automatically scales based on:
- Request rate
- Concurrent requests
- CPU utilization

Current settings: 10 max instances, 2 CPU cores, 2GB memory

## Database/Persistence

Currently uses in-memory storage. For production:
- Add Cloud SQL for audit logs
- Use Cloud Storage for artifacts
- Configure VPC for security

## Security Best Practices

1. **Authentication**: Use Cloud Identity/IAM
2. **API Keys**: Store in Secret Manager
3. **CORS**: Restrict origins in production
4. **Rate Limiting**: Implement in Cloud Armor
5. **DDoS Protection**: Enable Cloud Armor

## Cost Optimization

- Use Cloud Run pay-per-use pricing
- Configure idle timeout (default 5 min)
- Monitor invocations and adjust max-instances
- Use preemptible instances if applicable

## Rollback

```bash
# View deployment history
gcloud run revisions list --service agentic-platform

# Deploy previous version
gcloud run deploy agentic-platform \
  --image gcr.io/$PROJECT_ID/agentic-platform:previous-tag \
  --region us-central1
```

## Health Check

```bash
# Test deployed service
curl https://agentic-platform-service-url.run.app/

# Check API docs
curl https://agentic-platform-service-url.run.app/docs
```

## Troubleshooting

1. **Service won't start**: Check logs with `gcloud run logs read`
2. **Memory issues**: Increase memory allocation
3. **Timeout errors**: Increase timeout from 3600s
4. **Cold starts**: Enable min instances or use warmup requests

## CI/CD Integration

For automated deployments via GitHub:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v0
      - run: gcloud run deploy agentic-platform --image gcr.io/...
```
