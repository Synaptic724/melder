from typing import TYPE_CHECKING, List



# Melder imports
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import SpellValidationStrategy
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext


class SelfDependencyStrategy(SpellValidationStrategy):
    """
    Detect trivial self-dependencies (a spell depending on itself).

    This is always a configuration bug and is treated as an error.

    Contract:
    - Checks only for direct self-dependency, not longer dependency cycles.
    - Emits validation issues into the supplied context; it does not mutate the
      dependency graph.

    Registration:
        MELDER KERNEL. A built-in strategy; registered, never bound.

    Subsystem Context:
        One built-in of the `validation/strategies` family, registered into
        `SpellValidationSystem`. Sibling to `CircularDependencyStrategy`, which
        catches the multi-hop cycles this one deliberately does not.

    System Context:
        Phase 4 (validation) of the conjure pipeline. Its error marks the spell
        broken and aborts conjure.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-4 strategy: emits one SELF_DEPENDENCY error if a spell's "
        "dependency list contains its own selected_spell_id. Direct self-dependency only, not "
        "longer cycles."
    )
    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the self-dependency strategy.

        Contract:
            Seeds the stable strategy name/description published through the
            validation pipeline.
        """
        super().__init__(
            name="self_dependency",
            description="Detects spells that directly depend on themselves.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Detect whether the current spell directly depends on itself.

        Contract:
        - Stops early if the validation context has been cancelled.
        - Emits one `SELF_DEPENDENCY` error when the current spell id is found
          in its own dependency list.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = context.spell
        deps: List[str] = spell.dependencies
        if not deps:
            return

        root_id = spell.spell_index.selected_spell_id
        if root_id is None:
            return
        if root_id in deps:
            context.issues.append(
                SpellValidationIssue(
                    severity="error",
                    code="SELF_DEPENDENCY",
                    message=(
                        f"Spell {spell.spell_name!r} declares a dependency on itself "
                        f"(spell_id={root_id}). This indicates a configuration bug."
                    ),
                    details={"spell_id": root_id},
                )
            )
