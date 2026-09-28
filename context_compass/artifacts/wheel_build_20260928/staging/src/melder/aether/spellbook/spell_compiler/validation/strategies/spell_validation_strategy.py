from typing import TYPE_CHECKING, ClassVar



from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext

class SpellValidationStrategy(Cleanable):
    """
    Base class for all spell validation strategies.

    Strategies are small, composable units of logic that inspect a single
    spell (plus its environment) and append: class:`SpellValidationIssue`
    instances to the shared context.

    Contract
    --------
    * Implement: meth: 'validate` and **never** mutate the spell or spellbook.
    * Prefer appending issues instead of raising; raising is reserved for
      truly unrecoverable situations.

    Registration:
        MELDER KERNEL. A user-extensible strategy base. Strategies register into
        `SpellValidationSystem` via `register_strategy` and are NEVER passed to
        `Spellbook.bind`, so refusal cannot fire on a strategy at all.

    Subsystem Context:
        The base of the `validation/strategies` family: every built-in strategy
        subclasses it, and `SpellValidationSystem` registers instances by `name`.

    System Context:
        Phase 4 (validation) of the conjure pipeline. Strategies run in registry
        order over one `SpellValidationContext` per spell; an emitted error makes
        the spell broken.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Base class for Phase-4 validation strategies: implement
        validate(context) to inspect one spell and append SpellValidationIssue; name/description
        identify it in the registry. Never mutate the spell/spellbook; prefer appending issues
        to raising.
    """
    __slots__ = Cleanable.__slots__ + [
        "_name",
        "_description",
    ]

    def __init__(self, name: str, description: str = "") -> None:
        """
        Initialize one validation strategy base object.

        Args:
            name: Stable machine-readable strategy identifier.
            description: Optional human-readable strategy description.
        Contract:
            - Strategy names must be non-empty.
            - Stores only lightweight identifier/description metadata on the
              base object.
        """
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

    def validate(self, context: SpellValidationContext) -> None:
        """
        Execute this validation strategy against a single spell.

        Implementations should inspect the context and append: class:`SpellValidationIssue` instances to "context.issues".

        Contract:
            Read-only over the spell/spellbook (see the class Contract); prefer
            appending issues to `context.issues` over raising.

        Args:
            context:
                Per-spell validation context to inspect and append issues to.

        Returns:
            None.
        """
        raise NotImplementedError("SpellValidationStrategy.validate must be overridden.")

