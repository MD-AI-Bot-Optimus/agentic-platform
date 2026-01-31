class PlatformError(Exception):
    """Base error for platform core."""
    pass

class ValidationError(PlatformError):
    pass

class NotFoundError(PlatformError):
    pass
