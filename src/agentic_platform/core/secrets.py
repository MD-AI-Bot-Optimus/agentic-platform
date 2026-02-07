import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class SecretManager:
    """
    Hybrid Secret Manager.
    
    Priority:
    1. Local Environment Variables (.env) - Best for Local Dev
    2. Google Secret Manager (Cloud) - Best for Production
    """
    
    @staticmethod
    def load_secrets(secret_names: List[str]):
        """
        Ensure the given secrets are present in os.environ.
        If missing locally, attempt to fetch from Google Secret Manager.
        """
        project_id = os.getenv("GCP_PROJECT_ID")
        client = None

        # Check what's missing first
        missing_secrets = [name for name in secret_names if name not in os.environ]
        
        if not missing_secrets:
            # All present locally, no need to init cloud client
            logger.debug("All required secrets found in environment.")
            return

        if not project_id:
            logger.info("GCP_PROJECT_ID not set. Skipping Google Secret Manager lookup for: " + ", ".join(missing_secrets))
            return

        # Initialize Client
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
        except ImportError:
            logger.warning("google-cloud-secret-manager not installed. Skipping cloud lookup.")
            return
        except Exception as e:
            logger.warning(f"Failed to initialize Secret Manager client: {e}")
            return

        # Fetch missing secrets
        for name in missing_secrets:
            try:
                # Assumes secret name in GSM matches env var name exactly
                # Format: projects/{project_id}/secrets/{secret_name}/versions/latest
                name_path = f"projects/{project_id}/secrets/{name}/versions/latest"
                
                logger.debug(f"Attempting to fetch {name} from Secret Manager...")
                response = client.access_secret_version(request={"name": name_path})
                
                # Decode and set in environment
                payload = response.payload.data.decode("UTF-8")
                os.environ[name] = payload
                
                logger.info(f"Successfully loaded {name} from Google Secret Manager")
                
            except Exception as e:
                # It's okay if some are missing (optional keys), just log debug
                logger.debug(f"Could not fetch {name} from Secret Manager: {e}")
