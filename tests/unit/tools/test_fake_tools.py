import pytest
from platform.tools import fake_tools

def test_fake_tool_client_returns_fixture():
    client = fake_tools.FakeToolClient()
    result = client.call("ocr_page", {"page": 1})
    assert result == {"text": "This is page 1", "confidence": 0.92}
    result2 = client.call("ocr_page", {"page": 2})
    assert result2 == {"text": "This is page 2", "confidence": 0.92}
    # Unknown tool returns error
    with pytest.raises(Exception):
        client.call("unknown_tool", {})
