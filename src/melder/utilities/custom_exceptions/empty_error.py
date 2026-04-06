class Empty(Exception):
    """
    Raised when an operation requires at least one item but the container is empty.

    This exception is intentionally broad and lightweight. Callers should use
    it when "empty container/state" is the contract failure and a more specific
    domain exception would not add useful context.
    """
    pass
