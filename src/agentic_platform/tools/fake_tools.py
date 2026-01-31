class FakeToolClient:
    def call(self, tool_name: str, args: dict) -> dict:
        if tool_name == "ocr_page":
            page = args.get("page", 1)
            return {"text": f"This is page {page}", "confidence": 0.92}
        raise Exception(f"Unknown tool: {tool_name}")
