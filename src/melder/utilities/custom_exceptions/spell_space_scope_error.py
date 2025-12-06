class SpellSpaceScopeError(RuntimeError):
    """
    Raised when SpellSpace scoping rules are violated.

    Examples:
    - Using a spell that requires an active SpellSpace when none is active.
    - Attempting to reuse a SpellSpace across different conduits.
    - Using a SpellSpace after it has been closed.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
