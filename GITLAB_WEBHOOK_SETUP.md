# GitLab Webhook to Cloud Build Setup

Since Cloud Build doesn't have native GitLab support, we use a Cloud Function as a webhook receiver.

## Step 1: Deploy Cloud Function

```sh
gcloud functions deploy gitlab-webhook \
  --runtime python312 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point gitlab_webhook \
  --region us-central1 \
  --set-env-vars GCP_PROJECT_ID=agentic-platfrom,GITLAB_SECRET=your-secret-token
```

This will output a webhook URL like:
```
https://us-central1-agentic-platfrom.cloudfunctions.net/gitlab-webhook
```

## Step 2: Add GitLab Webhook

1. Go to your GitLab repo:
   https://gitlab.com/MD-AI-Bot-Optimus/agentic-platform

2. Settings → Webhooks (or Integrations → Webhooks)

3. Add new webhook:
   - **URL:** `https://us-central1-agentic-platfrom.cloudfunctions.net/gitlab-webhook`
   - **Secret token:** `your-secret-token` (must match GITLAB_SECRET above)
   - **Trigger events:** ✓ Push events
   - **SSL verification:** ✓ Enabled

4. Click "Add webhook"

## Step 3: Test

Push a commit:
```sh
git push origin main
```

Watch build progress:
```sh
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

Or in console: https://console.cloud.google.com/cloud-build

## Monitoring

View function logs:
```sh
gcloud functions logs read gitlab-webhook --region us-central1 --limit 50
```

## Cleanup

Remove the webhook from GitLab settings if you want to disable auto-deploy.

Delete the Cloud Function:
```sh
gcloud functions delete gitlab-webhook --region us-central1
```
