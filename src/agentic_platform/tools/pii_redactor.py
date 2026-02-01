"""
PII Redaction utility for audit logs and workflow artifacts.
"""
import re
from typing import Any, Dict

class PiiRedactor:
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_PATTERN = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")

    def redact(self, text: str) -> str:
        text = self.EMAIL_PATTERN.sub("<REDACTED:EMAIL>", text)
        text = self.PHONE_PATTERN.sub("<REDACTED:PHONE>", text)
        return text

    def redact_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        # Redact all string values in the event dict
        redacted = {}
        for k, v in event.items():
            if isinstance(v, str):
                redacted[k] = self.redact(v)
            else:
                redacted[k] = v
        return redacted
