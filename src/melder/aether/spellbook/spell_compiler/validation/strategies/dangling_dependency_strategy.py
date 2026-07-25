from typing import TYPE_CHECKING, List



from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class DanglingDependenciesStrategy(SpellValidationStrategy):
    """
    Verify that all dependency spell_ids attached to a spell actually exist.

    This runs at the **Spellbook** level using the Spellbook's live
    spell_id_pool map and ensures that every id in ``spell.dependencies``
    resolves to a visible spell in the owning Spellbook.

    Contract:
    - Validates dependency existence against the owning spellbook's current
      visible spell-id pool.
    - Emits validation issues into the supplied context; it does not attempt
      to repair or prune dependency lists.
    - Distinguishes between "cannot check because no spellbook exists" and
      "dependency is definitely dangling."

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        A built-in of the `validation/strategies` family; it pairs with
        `CircularDependencyStrategy`, which deliberately ignores dangling ids so
        this strategy owns reporting them.

    System Context:
        Phase 4 (validation) of the conjure pipeline, checking dependency existence
        against the owning Spellbook's live `_spell_id_pool`.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-4 strategy: checks every id in spell.dependencies exists in the "
        "owning Spellbook's _spell_id_pool. Emits DANGLING_DEPENDENCY (error) per missing id, or "
        "NO_SPELLBOOK_FOR_DEPENDENCY_CHECK (warning) when no spellbook is attached."
    )
    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the dangling-dependency strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="dangling_dependencies",
            description="Checks that all dependency spell_ids resolve to spells.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate that every declared dependency id resolves to a visible spell.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits `NO_SPELLBOOK_FOR_DEPENDENCY_CHECK` when dependency existence
          cannot be checked because no spellbook is attached.
        - Emits one `DANGLING_DEPENDENCY` issue per missing dependency id.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        deps: List[str] = spell.dependencies
        if not deps:
            return

        spellbook = context.spellbook
        if spellbook is None:
            # We can't validate existence without a Spellbook – warn and bail.
            context.issues.append(
                SpellValidationIssue(
                    severity="warning",
                    code="NO_SPELLBOOK_FOR_DEPENDENCY_CHECK",
                    message=(
                        f"Spell {spell.spell_name!r} has dependencies but no owning "
                        "Spellbook is attached; dependency existence cannot be verified."
                    ),
                    details={},
                )
            )
            return

        for dep_id in deps:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if dep_id not in spellbook._spell_id_pool:
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="DANGLING_DEPENDENCY",
                        message=(
                            f"Spell {spell.spell_name!r} depends on spell_id={dep_id!r}, "
                            "but no such spell is visible in the owning Spellbook."
                        ),
                        details={"missing_spell_id": dep_id},
                    )
                )
