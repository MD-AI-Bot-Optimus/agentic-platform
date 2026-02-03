# Cloud Run Deployment Guide

This document explains how to deploy the Agentic Platform to Google Cloud Run.

## Overview

Cloud Run automatically deploys your application from GitHub:
- Every `git push` to `main` triggers a build
- Docker image is built and deployed via Cloud Build
- Public URL is generated instantly
- Pay only for what you use (serverless)

## Prerequisites

1. **Google Cloud Account** - https://cloud.google.com
2. **Google Cloud Project** - Create one in the console
3. **Google Cloud CLI** - `brew install google-cloud-sdk`
4. **GitHub Account** - Push to https://github.com/MD-AI-Bot-Optimous/agentic-platform

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

### 2. Build and Push Container (Manual)

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/agentic-platform:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/agentic-platform:latest
```

### 3. Cloud Build Trigger (Recommended)

The build trigger automatically deploys code on every push:
- Source: **GitHub** (`MD-AI-Bot-Optimus/agentic-platform`)
- Branch: `main`
- Configuration: `cloudbuild.yaml`

To verify the trigger:
```sh
gcloud builds triggers list
```

### 4. Configure Custom Domain (Optional)

```bash
gcloud run domain-mappings create \
  --service agentic-platform \
  --domain yourdomain.com \
  --region us-central1
```

## How It Works

1. **You push code to GitHub**
   ```sh
   git push origin main
   ```

2. **GitHub webhook triggers Cloud Build**
   - Webhook sends push event to Cloud Build
   - Cloud Build reads `cloudbuild.yaml`
   - Builds Docker image from `Dockerfile`
   - Uploads image to Container Registry (gcr.io)

3. **Cloud Run deploys automatically**
   - Cloud Build step deploys to Cloud Run
   - Creates new service revision
   - Routes 100% of traffic to new version

4. **You get a public URL**
   ```
   https://agentic-platform-api-xxxxx.run.app
   ```

## Environment Variables

Set these in Cloud Run environment:

- `ENVIRONMENT=production`
- `LOG_LEVEL=info`
- `PYTHONUNBUFFERED=1`

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

## Auto-scaling Configuration

Cloud Run automatically scales based on:
- Request rate
- Concurrent requests
- CPU utilization

Current settings: 10 max instances, 2 CPU cores, 2GB memory

## Security Best Practices

1. **Authentication**: Use Cloud Identity/IAM
2. **API Keys**: Store in Secret Manager
3. **CORS**: Restrict origins in production
4. **Input Validation**: Pydantic v2 for strict type checking

## Troubleshooting

1. **Service won't start**: Check logs with `gcloud run logs read`
2. **Memory issues**: Increase memory allocation
3. **Build Fails**: Check logs with `gcloud builds log`

## Rollback

```bash
# View deployment history
gcloud run revisions list --service agentic-platform

# Roll back to previous version
gcloud run services update-traffic agentic-platform-api \
  --to-revisions PREVIOUS_REVISION_ID=100 --region us-central1
```
