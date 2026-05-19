from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=True)
class InternalRegistrationError(RuntimeError):
    """
    Raised when code tries to register a Melder-owned object that is intentionally protected.

    Purpose:
        Provide one stable runtime error for "this object is reserved for the
        framework and cannot be registered through the public path."

    Contract:
        - Used by internal registration guards rather than by normal user-level
          validation paths.
        - Signals misuse of framework-owned sentinels, system objects, or other
          protected Melder surfaces.
        - Remains a `RuntimeError` so callers may either catch this specific
          guard failure or treat it as a broader runtime registration error.
    """

