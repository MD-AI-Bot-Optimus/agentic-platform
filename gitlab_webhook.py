"""
Google Cloud Function to receive GitLab webhooks and trigger Cloud Build
Deploy this to Google Cloud Functions
"""
import functions_framework
import google.cloud.build_v1 as cloudbuild
import json
import hmac
import hashlib
import os

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "agentic-platfrom")
GITLAB_SECRET = os.environ.get("GITLAB_SECRET", "your-secret-token")


@functions_framework.http
def gitlab_webhook(request):
    """HTTP Cloud Function to receive GitLab webhooks"""
    
    # Verify GitLab signature
    if GITLAB_SECRET:
        gitlab_token = request.headers.get("X-Gitlab-Token")
        if gitlab_token != GITLAB_SECRET:
            return "Unauthorized", 401
    
    # Parse payload
    payload = request.get_json()
    
    # Only trigger on push to main branch
    if payload.get("ref") != "refs/heads/main":
        return "Ignoring non-main branch", 200
    
    # Trigger Cloud Build
    client = cloudbuild.CloudBuildClient()
    
    build = cloudbuild.Build(
        steps=[
            cloudbuild.BuildStep(
                name="gcr.io/cloud-builders/docker",
                args=[
                    "build",
                    "-t",
                    f"gcr.io/{PROJECT_ID}/agentic-platform-api:latest",
                    "-t",
                    f"gcr.io/{PROJECT_ID}/agentic-platform-api:$SHORT_SHA",
                    "."
                ]
            ),
            cloudbuild.BuildStep(
                name="gcr.io/cloud-builders/docker",
                args=["push", f"gcr.io/{PROJECT_ID}/agentic-platform-api"]
            ),
            cloudbuild.BuildStep(
                name="gcr.io/cloud-builders/run",
                args=[
                    "deploy",
                    "agentic-platform-api",
                    "--image",
                    f"gcr.io/{PROJECT_ID}/agentic-platform-api:$SHORT_SHA",
                    "--region",
                    "us-central1",
                    "--allow-unauthenticated",
                    "--memory",
                    "512Mi",
                    "--cpu",
                    "2",
                    "--timeout",
                    "3600"
                ]
            )
        ]
    )
    
    request = cloudbuild.CreateBuildRequest(
        parent=f"projects/{PROJECT_ID}",
        build=build
    )
    
    operation = client.create_build(request=request)
    
    return {
        "status": "Build triggered",
        "build_id": operation.name
    }, 202
