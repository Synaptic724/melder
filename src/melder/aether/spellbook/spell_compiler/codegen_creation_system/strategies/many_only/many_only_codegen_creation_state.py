from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
        SpellCodegenCreation,
    )
    from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
        SpellCodegenPlan,
    )


class ManyOnlyCodegenCreationState:
    """
    Family-local mutable state for the many-only creation strategy.

    Purpose:
        Carry only the many-only family intermediate compiler data across
        ordered many-only steps so the final `SpellCodegenCreation` artifact
        stays narrow and runtime-facing.
    """

    __slots__ = [
        "spell_codegen_model",
        "spell_codegen_plan",
        "spell_codegen_creation",
        "root_spell",
        "base_no_overrides_executor",
    ]

    def __init__(
            self,
            *,
            spell_codegen_model: "SpellCodegenModel",
            spell_codegen_plan: "SpellCodegenPlan",
            spell_codegen_creation: "SpellCodegenCreation",
    ) -> None:
        """
        Build one many-only family state object.

        Contract:
            Stores the three phase inputs (model, plan, creation) by reference
            and initializes the family-local intermediates (root spell and
            base no-overrides executor) to None; the ordered steps populate
            them in place. The override lane has no state here: override
            melds compile their plans at meld time (2026-09-26).

        Args:
            spell_codegen_model:
                Fitted spell model for the current compile.
            spell_codegen_plan:
                Chosen many-only plan.
            spell_codegen_creation:
                Artifact-owned creation sink the steps populate.

        Returns:
            None.
        """
        self.spell_codegen_model = spell_codegen_model
        self.spell_codegen_plan = spell_codegen_plan
        self.spell_codegen_creation = spell_codegen_creation
        self.root_spell: Optional[Any] = None
        self.base_no_overrides_executor: Optional[Callable[..., Any]] = None
