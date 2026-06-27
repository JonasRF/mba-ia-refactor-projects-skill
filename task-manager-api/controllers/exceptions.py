class ConflictError(ValueError):
    """Raised when a uniqueness constraint is violated (maps to HTTP 409)."""
    pass
