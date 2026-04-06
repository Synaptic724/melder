class InternalRegistrationError(RuntimeError):
    """
    Raised when code tries to register a Melder object that is intentionally protected.

    Typical source:
        Internal registration guards raise this when user or plugin code tries
        to register framework-owned sentinels, system objects, or otherwise
        reserved Melder surfaces.
    """

