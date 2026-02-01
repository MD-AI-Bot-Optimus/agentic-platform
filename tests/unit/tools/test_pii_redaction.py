
import pytest
from agentic_platform.audit import audit_log
from agentic_platform.tools import PiiRedactor

PII_EXAMPLES = [
    ("My email is john.doe@example.com", "My email is <REDACTED:EMAIL>"),
    ("Call me at 555-123-4567.", "Call me at <REDACTED:PHONE>.")
]


def test_redact_pii_examples():
    redactor = PiiRedactor()
    for text, expected in PII_EXAMPLES:
        assert redactor.redact(text) == expected


def test_redact_pii_in_audit_event():
    redactor = PiiRedactor()
    event = {"message": "Contact: jane@company.com, 212-555-7890"}
    redacted = redactor.redact_event(event)
    assert redacted["message"] == "Contact: <REDACTED:EMAIL>, <REDACTED:PHONE>"
