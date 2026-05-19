from typing import Optional, Any, Callable

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.synchronization.creation_gate import CreationGate


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

    __slots__: list[str] = []

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

    def build(
            self,
            spell: ISpell,
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional[CreationGate] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> CreationContext:
        """
        Build one `CreationContext` bound to the provided spell.

        Args:
            spell:
                Spell to bind to the created runtime context.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. This flag is
                carried into the CreationContext for runtime policy selection.
            creation_gate:
                Shared spell-index CreationGate used by the built context
                for dynamic-mode execution admission.
            creation_gate_index_id:
                Stable spell-index id used for gate diagnostics.

        Returns:
            CreationContext:
                A new spell-bound runtime context.

        Raises:
            RuntimeError:
                If the spell is not in a runnable state for context creation.
        """
        if not spell.is_existing_creation and spell._crafter is None:
            raise RuntimeError(
                "Cannot build CreationContext before spell crafter artifacts "
                "exist. Run conjure phases first."
            )
        resolve_route_key = self._resolve_route_key(spell)
        fast_transient_no_overrides_enabled = (
            self._resolve_fast_transient_no_overrides_enabled(spell)
        )
        fast_transient_no_overrides_enabled = (
            self._coerce_fast_transient_route_eligibility(
                resolve_route_key=resolve_route_key,
                fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            )
        )
        no_overrides_executor = self._resolve_no_overrides_executor(spell)
        override_patch_map_phase10 = self._resolve_override_patch_map_phase10(spell)
        override_route_config_no_mutation = self._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides",
        )
        override_route_config_mutation = (
            self._build_mutation_override_route_config(spell=spell)
        )

        return CreationContext(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            resolve_route_key=resolve_route_key,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            no_overrides_executor=no_overrides_executor,
            override_patch_map_phase10=override_patch_map_phase10,
            override_route_config_no_mutation=override_route_config_no_mutation,
            override_route_config_mutation=override_route_config_mutation,
        )

    @staticmethod
    def _resolve_route_key(spell: ISpell) -> str:
        """
        Select the runtime execution route for the spell's existence model.

        This is the builder's existence-policy switch. It collapses the spell's
        lifecycle semantics into one of the `CreationContext` route constants so
        the context can bind the correct hot-path executor family once at build
        time instead of branching repeatedly at runtime.
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
    def _coerce_fast_transient_route_eligibility(
            *,
            resolve_route_key: str,
            fast_transient_no_overrides_enabled: bool,
    ) -> bool:
        """
        Coerce fast-transient eligibility by resolve route.

        Contract:
            - Fast transient lane is valid only for `many` route contexts.
            - Other existence routes always use the standard runtime dispatch.
        """
        if not fast_transient_no_overrides_enabled:
            return False
        return resolve_route_key == CreationContext.ROUTE_MANY

    @staticmethod
    def _resolve_fast_transient_no_overrides_enabled(spell: ISpell) -> bool:
        """
        Decide whether no-override calls may use the fast transient lane.

        This helper inspects spell-static execution-plan data to determine
        whether the spell has a specialized transient path for plain no-override
        calls. Existing-creation spells are always excluded, because they do not
        participate in transient construction.
        """
        if spell.is_existing_creation:
            return False

        crafter = spell._crafter
        if crafter is None:
            return False
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
        Return the spell's precompiled no-overrides Phase 12 executor.

        The builder keeps this lookup separate so `CreationContext` can be
        seeded with the direct no-override execution lane only when the spell
        actually has one.
        """
        if spell.is_existing_creation:
            return None
        crafter = spell._crafter
        if crafter is None:
            return None
        return crafter.phase12_no_overrides_executor

    @staticmethod
    def _resolve_override_patch_map_phase10(spell: ISpell) -> Optional[Any]:
        """
        Return the spell's compiled Phase 10 override patch map artifact.

        This artifact is the bridge between frontdoor override payloads and the
        override-specialization runtime in `CreationContext`: it turns override
        input into socket-targeted patch data that the later executor pipeline
        can specialize against.
        """
        if spell.is_existing_creation:
            return None
        crafter = spell._crafter
        if crafter is None:
            return None
        return crafter.override_patch_map_phase10

    @staticmethod
    def _build_mutation_override_route_config(
            *,
            spell: ISpell,
    ) -> Optional[OverrideRouteConfig]:
        """
        Build mutation-lane route config only when mutation overlay is active.

        Contract:
            - Default spell contexts (no mutation overlay) omit mutation route
              config to keep builder output lean.
            - Applying or clearing mutation overlay cleans spell-owned context,
              so a rebuilt context can materialize the required lane.
        """
        if not spell.has_mutation_override:
            return None
        return CreationContextBuilder._build_override_route_config(
            spell=spell,
            execution_ir_key="overrides_with_mutations",
        )

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
        if crafter is None:
            return None
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
        if spellbook is None:
            return None
        spell_lookup = spellbook._spell_id_pool

        plan_rows = override_execution_ir_payload.get("steps_rows")
        root_spell_id = override_execution_ir_payload.get("root_spell_id")

        return OverrideRouteConfig(
            plan_signature=plan_signature,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            empty_shape_key=(
                plan_signature,
                (),
                -1,
            ),
            baseline_executor=None,
        )
