class DeadReferenceError(ReferenceError):
    """
    Raised when code tries to use a weak-reference target that no longer exists.

    Typical source:
        Weak-reference helper structures raise this when their referenced
        object has already been garbage collected and the caller requested a
        live target.
    """
    pass

