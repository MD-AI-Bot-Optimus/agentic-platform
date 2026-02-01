# Cloud Run Deployment Guide

This document explains how to deploy the Agentic Platform to Google Cloud Run.

## Overview

Cloud Run automatically deploys your application from GitLab:
- Every `git push` to main triggers a build
- Docker image is built and deployed
- Public URL is generated instantly
- Pay only for what you use (serverless)

## Prerequisites

1. **Google Cloud Account** - https://cloud.google.com
2. **Google Cloud Project** - Create one in the console
3. **Google Cloud CLI** - `brew install google-cloud-sdk`
4. **GitLab Account** - Already have this ✓

## Setup Instructions

### Step 1: Authenticate with Google Cloud

```sh
gcloud auth login
gcloud config set project YOUR-PROJECT-ID
gcloud auth application-default login
```

Replace `YOUR-PROJECT-ID` with your actual Google Cloud project ID.

### Step 2: Enable Required APIs

```sh
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 3: Connect GitLab to Google Cloud Build

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Build** → **Triggers**
3. Click **Create Trigger**
4. **Connect Repository:**
   - Source: Select **GitLab**
   - Authorize (follow OAuth flow)
   - Select `MD-AI-Bot-Optimus/agentic-platform`
5. **Trigger Settings:**
   - Trigger type: **Push to a branch**
   - Branch: `^main$`
   - Configuration: **Cloud Build configuration file (yaml)**
   - Location: `cloudbuild.yaml`
6. Click **Create**

### Step 4: Manual First Deploy (Optional)

If you want to deploy immediately without waiting for a Git push:

```sh
# Deploy from local repo
gcloud builds submit \
  --config=cloudbuild.yaml \
  --region=us-central1

# Or deploy directly
gcloud run deploy agentic-platform-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 2 \
  --timeout 3600
```

### Step 5: Get Your Public URL

```sh
gcloud run services describe agentic-platform-api --region us-central1 --format='value(status.url)'
```

Or find it in [Cloud Run Console](https://console.cloud.google.com/run)

## How It Works

1. **You push code to GitLab**
   ```sh
   git push origin main
   ```

2. **Cloud Build detects the push**
   - Reads `cloudbuild.yaml`
   - Builds Docker image from `Dockerfile`
   - Uploads image to Container Registry

3. **Cloud Run deploys automatically**
   - Creates new service revision
   - Routes traffic to new version
   - Old versions kept for rollback

4. **You get a public URL**
   ```
   https://agentic-platform-api-xxxxx.run.app
   ```

## Environment Variables

Set environment variables in Cloud Run:

```sh
gcloud run services update agentic-platform-api \
  --region us-central1 \
  --set-env-vars PYTHONUNBUFFERED=1,LOG_LEVEL=INFO
```

## Monitoring & Logs

View logs:
```sh
gcloud run services logs read agentic-platform-api --region us-central1
```

Real-time logs:
```sh
gcloud run services logs read agentic-platform-api --region us-central1 --follow
```

View in console:
- [Cloud Run Services](https://console.cloud.google.com/run)
- [Cloud Logging](https://console.cloud.google.com/logs)

## Cost Estimation

Cloud Run pricing (as of 2024):
- **Compute:** $0.24 per vCPU-hour
- **Memory:** $0.0025 per GiB-hour
- **Requests:** $0.40 per 1M requests

**Typical usage:** ~$5-20/month for a demo

## Troubleshooting

### Build Fails
Check logs:
```sh
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

### Service Won't Start
Check Cloud Run logs for errors

### CORS Issues
Add to `src/agentic_platform/api.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## CI/CD Pipeline

Your pipeline:
```
git push → GitLab → Cloud Build → Docker Build → Container Registry → Cloud Run Deploy → Public URL
```

Every commit to main automatically deploys!

## Rollback

If something breaks:

```sh
# View previous revisions
gcloud run revisions list --region us-central1

# Roll back to previous version
gcloud run services update-traffic agentic-platform-api \
  --to-revisions PREVIOUS_REVISION_ID=100 \
  --region us-central1
```

## Next Steps

1. Complete Setup Instructions above
2. Make a test commit: `git push origin main`
3. Watch Cloud Build in console
4. Access your live demo URL!

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

---

**Ready to deploy?** Start with Step 1! 🚀
