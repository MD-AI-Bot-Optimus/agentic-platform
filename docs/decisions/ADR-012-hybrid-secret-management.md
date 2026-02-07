# ADR-012: Hybrid Secret Management Strategy

## Context
As the Agentic Platform matures to support real LLM integrations (Gemini, GPT-4) and Enterprise deployments, we face conflicting requirements for managing sensitive API keys:

1.  **Local Development:** Developers need simplicity. Creating cloud resources for every local test is friction. The industry standard is `.env` files.
2.  **Enterprise Production:** Storing keys in plain text files or environment variables (which can be inspected via `ps aux` or Docker inspect) is a security risk. Enterprises require **Encryption at Rest**, **Audit Logging**, and **Key Rotation**.

We need a unified mechanism to access secrets that satisfies both needs without requiring code changes between environments.

## Decision
We will implement a **Hybrid Secret Manager** pattern found in `src/agentic_platform/core/secrets.py`.

### 1. The Hierarchy
The application will resolve secrets in the following order:
1.  **Local Environment (`.env`):**
    *   Using `python-dotenv`, we load variables from a local `.env` file (which is git-ignored) into `os.environ`.
    *   *Use Case:* Local development, rapid prototyping, CI/CD pipelines where secrets are injected as env vars.

2.  **Google Secret Manager (Cloud Fallback):**
    *   If a specific key (e.g., `GOOGLE_API_KEY`) is **missing** from the environment, and a `GCP_PROJECT_ID` is defined, the application will automatically attempt to fetch the secret from Google Secret Manager.
    *   *Path:* `projects/{GCP_PROJECT_ID}/secrets/{current_key_name}/versions/latest`
    *   *Use Case:* Production deployments on Cloud Run, GKE, or VM instances.

### 2. The Abstraction
All sensitive configuration must be accessed via the `SecretManager` class, not raw `os.getenv()`.

```python
# Bad
api_key = os.getenv("GOOGLE_API_KEY")

# Good
SecretManager.load_secrets(["GOOGLE_API_KEY"]) # Ensures it's loaded into env
api_key = os.getenv("GOOGLE_API_KEY")
```

## Consequences

### Positive
*   **Security by Default:** In production, secrets are never written to disk. They exist only in the application's memory process.
*   **Seamless Dev/Prod Parity:** Developers don't need to mock the Secret Manager locally; they just use `.env`. The code doesn't care where the secret came from.
*   **Audit Trail:** Operations teams can see exactly when production keys are accessed via Google Cloud Audit Logs.

### Negative
*   **Startup Latency:** Fetching secrets from GCP adds a small network overhead at application startup (milliseconds).
*   **Mocking Complexity:** Tests that verify secret handling now need to mock both `os.environ` and the `google.cloud.secretmanager` client.
*   **Dependency:** We introduce a hard dependency on `google-cloud-secret-manager` for the core platform.
