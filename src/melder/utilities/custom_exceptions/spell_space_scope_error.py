
from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=True)
class SpellSpaceScopeError(RuntimeError):
    """
    Raised when SpellSpace scoping rules are violated.

    Contract:
        - Indicates a SpellSpace lifecycle or ownership violation rather than a
          generic runtime failure.
        - Keeps the message payload flexible so callers can describe the exact
          scope rule that failed.

    Examples:
    - Using a spell that requires an active SpellSpace when none is active.
    - Attempting to reuse a SpellSpace across different conduits.
    - Using a SpellSpace after it has been closed.
    """

    def __init__(self, message: str) -> None:
        """
        Build a SpellSpace scope violation error.

        Args:
            message (str): Human-readable description of the violated scoping
                rule.
        """
        super().__init__(message)
