from typing import TYPE_CHECKING, Any, Dict, Optional

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


class GeneralizedCacheCodegenCreationState:
    """
    Family-local mutable state for the generalized_cache creation strategy.

    Purpose:
        Carry the manifest and hydration result across ordered internal steps
        so the final `SpellCodegenCreation` artifact stays narrow and
        runtime-facing.

    Contract:
        - Owns this family's intermediate build data only.
        - `manifest` is the serialization-shaped truth produced by the
          manifest step; the hydrate step consumes it untouched.
        - Does not own external runtime lifecycle or cleanup.
    """

    __slots__ = [
        "spell_codegen_model",
        "spell_codegen_plan",
        "spell_codegen_creation",
        "manifest",
        "hydrated_executors",
    ]

    def __init__(
            self,
            *,
            spell_codegen_model: "SpellCodegenModel",
            spell_codegen_plan: "SpellCodegenPlan",
            spell_codegen_creation: "SpellCodegenCreation",
    ) -> None:
        """
        Build one generalized_cache family state object.

        Args:
            spell_codegen_model:
                Processor-owned model truth from phase 9.
            spell_codegen_plan:
                Planner-owned plan truth from phase 10.
            spell_codegen_creation:
                Final phase-11 output object being populated.
        """
        self.spell_codegen_model = spell_codegen_model
        self.spell_codegen_plan = spell_codegen_plan
        self.spell_codegen_creation = spell_codegen_creation
        self.manifest: Optional[Dict[str, Any]] = None
        self.hydrated_executors: Optional[Any] = None
