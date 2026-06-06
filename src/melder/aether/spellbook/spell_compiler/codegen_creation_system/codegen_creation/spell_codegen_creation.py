from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Tuple

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_override_targeting_codegen_creation import (
        SpellOverrideTargetingCodegenCreation,
    )


class SpellCodegenCreation(Cleanable):
    """
    Artifact-owned codegen creation container.

    Purpose:
        Hold the compiler-owned post-plan creation artifact for one spell.

    Contract:
        - Lives on `SpellCompilerArtifact` as the output of the codegen
          creation layer.
        - Top-level route/setup fields capture the spell-static creation
          configuration that `CreationContextBuilder` currently derives
          directly.
        - `selected_strategy_ids` records the ordered strategy chain that
          produced this artifact.
        - No lane-specific payload wrapper classes are required here; the
          strategy layer writes the spell-static creation fields directly onto
          this artifact.
        - `metadata` is the mutable diagnostics/provenance bag.
    """

    __slots__ = Cleanable.__slots__ + [
        "selected_strategy_ids",
        "discovery_reason",
        "resolve_route_key",
        "fast_transient_no_overrides_enabled",
        "no_overrides_executor",
        "no_overrides_executor_signature",
        "override_targeting",
        "override_plan_signature",
        "override_path_registry",
        "override_plan_rows",
        "override_root_spell_id",
        "override_spell_lookup",
        "override_empty_shape_key",
        "override_baseline_executor",
        "metadata",
    ]

    def __init__(
            self,
            *,
            selected_strategy_ids: Tuple[str, ...],
            discovery_reason: Optional[str],
            resolve_route_key: Optional[str],
            fast_transient_no_overrides_enabled: bool,
            no_overrides_executor: Optional[Callable[..., Any]],
            no_overrides_executor_signature: Optional[str],
            override_targeting: Optional["SpellOverrideTargetingCodegenCreation"],
            override_plan_signature: Optional[Tuple[Any, ...]],
            override_path_registry: Optional[Any],
            override_plan_rows: Optional[Sequence[Dict[str, Any]]],
            override_root_spell_id: Optional[str],
            override_spell_lookup: Optional[Dict[str, Any]],
            override_empty_shape_key: Optional[Tuple[Any, ...]],
            override_baseline_executor: Optional[Callable[..., Any]],
            metadata: Dict[str, Any],
    ) -> None:
        """
        Build one codegen creation container.

        Contract:
            - Top-level fields describe the spell-static creation handoff.
            - Lane fields may be `None` until that lane's strategy is ported.
            - Override fields describe one normal override route only.
        """
        super().__init__()
        self.selected_strategy_ids = selected_strategy_ids
        self.discovery_reason = discovery_reason
        self.resolve_route_key = resolve_route_key
        self.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )
        self.no_overrides_executor = no_overrides_executor
        self.no_overrides_executor_signature = no_overrides_executor_signature
        self.override_targeting = override_targeting
        self.override_plan_signature = override_plan_signature
        self.override_path_registry = override_path_registry
        self.override_plan_rows = override_plan_rows
        self.override_root_spell_id = override_root_spell_id
        self.override_spell_lookup = override_spell_lookup
        self.override_empty_shape_key = override_empty_shape_key
        self.override_baseline_executor = override_baseline_executor
        self.metadata = metadata

    def cleanup(self) -> None:
        """
        Deterministically release the codegen creation container.
        """
        if self._cleaned:
            return

        self._cleaned = True
        override_targeting = self.override_targeting
        if override_targeting is not None:
            override_targeting.cleanup()
        self.metadata.clear()

        del self.selected_strategy_ids
        del self.discovery_reason
        del self.resolve_route_key
        del self.fast_transient_no_overrides_enabled
        del self.no_overrides_executor
        del self.no_overrides_executor_signature
        del self.override_targeting
        del self.override_plan_signature
        del self.override_path_registry
        del self.override_plan_rows
        del self.override_root_spell_id
        del self.override_spell_lookup
        del self.override_empty_shape_key
        del self.override_baseline_executor
        del self.metadata
