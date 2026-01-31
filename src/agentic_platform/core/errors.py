class PlatformError(Exception):
    """Base error for agentic_platform core."""
    pass

class ValidationError(PlatformError):
    pass

class NotFoundError(PlatformError):
    pass
