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


class SoloCodegenCreationState:
    """
    Family-local mutable state for the solo creation strategy.

    Purpose:
        Carry only the solo-family intermediate compiler data across ordered
        solo steps so the final `SpellCodegenCreation` artifact stays narrow
        and runtime-facing.
    """

    __slots__ = [
        "spell_codegen_model",
        "spell_codegen_plan",
        "spell_codegen_creation",
        "root_spell",
        "root_spell_id",
        "resolve_route_key",
        "solo_emit_key",
        "fast_transient_no_overrides_enabled",
        "no_overrides_executor",
        "overrides_executor",
    ]

    def __init__(
            self,
            *,
            spell_codegen_model: "SpellCodegenModel",
            spell_codegen_plan: "SpellCodegenPlan",
            spell_codegen_creation: "SpellCodegenCreation",
    ) -> None:
        """
        Build one solo family state object.

        Contract:
            Stores the three phase inputs (model, plan, creation) by reference
            and initializes every solo intermediate (root spell + id, route key,
            solo emit key, fast-transient flag, and the two executors) to its
            empty default; the ordered steps populate them in place.

        Args:
            spell_codegen_model:
                Fitted spell model for the current compile.
            spell_codegen_plan:
                Chosen solo plan.
            spell_codegen_creation:
                Artifact-owned creation sink the steps populate.

        Returns:
            None.
        """
        self.spell_codegen_model = spell_codegen_model
        self.spell_codegen_plan = spell_codegen_plan
        self.spell_codegen_creation = spell_codegen_creation
        self.root_spell: Optional[Any] = None
        self.root_spell_id: Optional[str] = None
        self.resolve_route_key: Optional[str] = None
        self.solo_emit_key: Optional[str] = None
        self.fast_transient_no_overrides_enabled: bool = False
        self.no_overrides_executor: Optional[Callable[..., Any]] = None
        self.overrides_executor: Optional[Callable[..., Any]] = None
