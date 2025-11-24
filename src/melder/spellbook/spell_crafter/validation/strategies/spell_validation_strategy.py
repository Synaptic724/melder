from melder.utilities.general_base.cleanable import Cleanable


class SpellValidationStrategy(Cleanable):
    """
    Base class for all spell validation strategies.

    Strategies are small, composable units of logic that inspect a single
    spell (plus its environment) and append :class:`SpellValidationIssue`
    instances to the shared context.

    Contract
    --------
    * Implement :meth:`validate` and **never** mutate the spell or spellbook.
    * Prefer appending issues instead of raising; raising is reserved for
      truly unrecoverable situations.
    """

    __slots__ = Cleanable.__slots__ + [
        "_name",
        "_description",
    ]

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__()
        if not name:
            raise ValueError("strategy name cannot be empty.")
        self._name: str = name
        self._description: str = description

    @property
    def name(self) -> str:
        """Short, stable identifier for this strategy."""
        return self._name

    @property
    def description(self) -> str:
        """Optional human-readable description of what this strategy checks."""
        return self._description

    def cleanup(self) -> None:
        """
        Idempotent cleanup.

        Most strategies are stateless, so this simply flips the cleaned flag.
        """
        if self._cleaned:
            return
        self._cleaned = True

    # ------------------------------------------------------------------ #
    # Overridables
    # ------------------------------------------------------------------ #

    def validate(self, context: 'SpellValidationContext') -> None:
        """
        Execute this validation strategy against a single spell.

        Implementations should inspect the context and append
        :class:`SpellValidationIssue` instances to ``context.issues``.
        """
        raise NotImplementedError("SpellValidationStrategy.validate must be overridden.")

