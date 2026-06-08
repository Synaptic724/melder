from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Tuple

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
        "override_targeting",
        "override_plan_signature",
        "override_path_registry",
        "override_plan_rows",
        "override_root_spell_id",
        "override_spell_lookup",
        "override_empty_shape_key",
        "override_baseline_executor",
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
        Build one many-only family state object.
        """
        self.spell_codegen_model = spell_codegen_model
        self.spell_codegen_plan = spell_codegen_plan
        self.spell_codegen_creation = spell_codegen_creation
        self.root_spell: Optional[Any] = None
        self.base_no_overrides_executor: Optional[Callable[..., Any]] = None
        self.override_targeting: Optional[Any] = None
        self.override_plan_signature: Optional[Tuple[Any, ...]] = None
        self.override_path_registry: Optional[Any] = None
        self.override_plan_rows: Optional[Sequence[Dict[str, Any]]] = None
        self.override_root_spell_id: Optional[str] = None
        self.override_spell_lookup: Optional[Dict[str, Any]] = None
        self.override_empty_shape_key: Optional[Tuple[Any, ...]] = None
        self.override_baseline_executor: Optional[Callable[..., Any]] = None
        self.overrides_executor: Optional[Callable[..., Any]] = None
