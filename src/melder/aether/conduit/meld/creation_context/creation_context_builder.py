from typing import Optional, Any, Callable

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell


class CreationContextBuilder(Cleanable):
    """
    Build spell-shaped `CreationContext` instances.

    Purpose:
        Encapsulate the build-time policy for creation contexts so Meld can
        request a context without embedding shape logic in front-door flow.

    Contract:
        - Builder only consumes spell-static data.
        - No caller-conduit transients are accepted by this builder.
        - Output context is deterministic for the same spell state.
    """

    __slots__ = []

    def __init__(self) -> None:
        """
        Initialize one stateless builder.

        Contract:
            - Builder owns no runtime caches.
            - Cleanup only marks the builder as unusable.
        """
        super().__init__()

    def cleanup(self) -> None:
        """
        Mark this builder as cleaned.

        Contract:
            - Idempotent cleanup.
            - No child resources are owned by this builder.
        """
        if self._cleaned:
            return
        self._cleaned = True

    def build(self, spell: ISpell) -> CreationContext:
        """
        Build one `CreationContext` bound to the provided spell.

        Args:
            spell:
                Spell to bind to the created runtime context.

        Returns:
            CreationContext:
                A new spell-bound runtime context.

        Raises:
            RuntimeError:
                If the spell is not in a runnable state for context creation.
        """
        self.check_cleaned()
        spell.check_cleaned()
        if not spell.is_existing_creation and spell._crafter is None:
            raise RuntimeError(
                "Cannot build CreationContext before spell crafter artifacts "
                "exist. Run conjure phases first."
            )
        resolve_route_key = self._resolve_route_key(spell)
        fast_transient_no_overrides_enabled = (
            self._resolve_fast_transient_no_overrides_enabled(spell)
        )
        no_overrides_executor = self._resolve_no_overrides_executor(spell)
        override_patch_map_phase10 = self._resolve_override_patch_map_phase10(spell)
        override_route_config_no_mutation = self._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides",
        )
        override_route_config_mutation = self._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides_with_mutations",
        )
        runtime_flags = self._build_runtime_flags(
            fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            override_route_config_no_mutation=override_route_config_no_mutation,
            override_route_config_mutation=override_route_config_mutation,
        )

        return CreationContext(
            spell=spell,
            resolve_route_key=resolve_route_key,
            runtime_flags=runtime_flags,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            no_overrides_executor=no_overrides_executor,
            override_patch_map_phase10=override_patch_map_phase10,
            override_route_config_no_mutation=override_route_config_no_mutation,
            override_route_config_mutation=override_route_config_mutation,
        )

    @staticmethod
    def _resolve_route_key(spell: ISpell) -> str:
        """
        Resolve one deterministic resolve-route key for the target spell.
        """
        if spell.is_existing_creation:
            return CreationContext.ROUTE_EXISTING_CREATION

        existence = spell.existence
        if existence is Existence.unique_per_spell_space:
            return CreationContext.ROUTE_SPELLSPACE
        if existence is Existence.unique_per_conduit:
            return CreationContext.ROUTE_UNIQUE_PER_CONDUIT
        if existence is Existence.many:
            return CreationContext.ROUTE_MANY
        return CreationContext.ROUTE_SHARED

    @staticmethod
    def _resolve_fast_transient_no_overrides_enabled(spell: ISpell) -> bool:
        """
        Resolve whether no-overrides calls can use fast transient dispatch.
        """
        if spell.is_existing_creation:
            return False

        crafter = spell._crafter
        dispatch_route = spell.execution_plan_dispatch_route
        if dispatch_route and dispatch_route.startswith("FAST_TRANSIENT"):
            return True

        plan = crafter.execution_plan_phase11_no_overrides
        if plan is None:
            return False
        return plan.fast_transient_plan is not None

    @staticmethod
    def _resolve_no_overrides_executor(
            spell: ISpell,
    ) -> Optional[Callable[..., Any]]:
        """
        Resolve the compiled no-overrides phase 12 executor for this spell.
        """
        if spell.is_existing_creation:
            return None
        crafter = spell._crafter
        return crafter.phase12_no_overrides_executor

    @staticmethod
    def _resolve_override_patch_map_phase10(spell: ISpell) -> Optional[Any]:
        """
        Resolve the compiled Phase 10 override patch map for this spell.
        """
        if spell.is_existing_creation:
            return None
        crafter = spell._crafter
        return crafter.override_patch_map_phase10

    @staticmethod
    def _build_runtime_flags(
            *,
            fast_transient_no_overrides_enabled: bool,
            override_route_config_no_mutation: Optional[OverrideRouteConfig],
            override_route_config_mutation: Optional[OverrideRouteConfig],
    ) -> int:
        """
        Build spell-static runtime flag bits for one CreationContext.

        Contract:
            - Flags only represent spell-static lane availability.
            - Per-call transients are not encoded in these flags.
        """
        runtime_flags = 0
        if fast_transient_no_overrides_enabled:
            runtime_flags |= CreationContext.FLAG_FAST_TRANSIENT_NO_OVERRIDES
        if override_route_config_no_mutation is not None:
            runtime_flags |= CreationContext.FLAG_OVERRIDE_ROUTE_NO_MUTATION
        if override_route_config_mutation is not None:
            runtime_flags |= CreationContext.FLAG_OVERRIDE_ROUTE_MUTATION
        return runtime_flags

    @staticmethod
    def _build_override_route_config(
            *,
            spell: ISpell,
            execution_ir_key: str,
    ) -> Optional[OverrideRouteConfig]:
        """
        Build one static override route configuration payload.

        Contract:
            - Returns None when the spell has no crafter/codegen payload.
            - Returns None when the requested execution variant is unavailable.
        """
        if spell.is_existing_creation:
            return None

        crafter = spell._crafter
        codegen_ir = crafter.codegen_ir
        if codegen_ir is None:
            return None

        phase8_11_payload = codegen_ir["phase8_11"]
        execution_payload = phase8_11_payload["execution"]
        override_execution_ir_payload = execution_payload.get(execution_ir_key)
        if override_execution_ir_payload is None:
            return None

        variant_signature = override_execution_ir_payload["signature"]
        plan_signature = (
            "phase11_overrides_ir",
            variant_signature,
            override_execution_ir_payload.get("steps_rows_signature"),
        )

        root_blueprint_phase5 = crafter.root_blueprint_phase5
        path_registry = None
        if root_blueprint_phase5 is not None:
            path_registry = root_blueprint_phase5.path_registry

        spellbook = spell._spellbook
        spell_lookup = None
        if spellbook is not None:
            spell_lookup = spellbook._spell_id_pool

        plan_rows = override_execution_ir_payload.get("steps_rows")
        root_spell_id = override_execution_ir_payload.get("root_spell_id")

        return OverrideRouteConfig(
            plan_signature=plan_signature,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            empty_shape_key=None,
            baseline_executor=None,
        )
