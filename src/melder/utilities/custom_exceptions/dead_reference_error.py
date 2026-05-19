from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class DeadReferenceError(ReferenceError):
    """
    Raised when code tries to use a weak-reference target that no longer exists.

    Typical source:
        Weak-reference helper structures raise this when their referenced
        object has already been garbage collected and the caller requested a
        live target.
    """
    pass

