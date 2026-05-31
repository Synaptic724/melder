from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.creation_gate import CreationGate



from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)


class CreationContextBuilder:
    """
    Build spell-shaped `CreationContext` instances.

    Purpose:
        Encapsulate the build-time policy for creation contexts so Meld can
        request a context without embedding shape logic in the front-door flow.

    Contract:
        - Builder only consumes spell-static data.
        - This builder accepts no caller-conduit transients.
        - Output context is deterministic for the same spell state.
    """

    __slots__ = ()

    @staticmethod
    def build(
            spell: Spell,
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
        artifact = spell._compiler_artifact
        spell_codegen_creation = artifact._spell_codegen_creation
        if not spell.is_existing_creation and spell_codegen_creation is None:
            raise RuntimeError(
                "Cannot build CreationContext before spell_codegen_creation "
                "exists. Run analyzer -> processor -> planner -> codegen "
                "creation first."
            )
        resolve_route_key = CreationContextBuilder._resolve_route_key(
            spell=spell,
            spell_codegen_creation=spell_codegen_creation,
        )
        fast_transient_no_overrides_enabled = (
            spell_codegen_creation.fast_transient_no_overrides_enabled
            if spell_codegen_creation is not None
            else False
        )
        no_overrides_executor = None
        override_targeting = None
        override_route_config_no_mutation = None
        override_route_config_mutation = None
        if spell_codegen_creation is not None:
            no_overrides_executor = spell_codegen_creation.no_overrides_executor
            override_targeting = spell_codegen_creation.override_targeting

            if (
                    spell_codegen_creation.override_no_mutation_plan_signature is not None
                    or spell_codegen_creation.override_no_mutation_plan_rows is not None
                    or spell_codegen_creation.override_no_mutation_baseline_executor is not None
            ):
                override_route_config_no_mutation = CreationContextBuilder._build_override_route_config_from_creation(
                    plan_signature=spell_codegen_creation.override_no_mutation_plan_signature,
                    path_registry=spell_codegen_creation.override_no_mutation_path_registry,
                    plan_rows=spell_codegen_creation.override_no_mutation_plan_rows,
                    root_spell_id=spell_codegen_creation.override_no_mutation_root_spell_id,
                    spell_lookup=spell_codegen_creation.override_no_mutation_spell_lookup,
                    empty_shape_key=spell_codegen_creation.override_no_mutation_empty_shape_key,
                    baseline_executor=spell_codegen_creation.override_no_mutation_baseline_executor,
                )

            if (
                    spell_codegen_creation.override_mutation_plan_signature is not None
                    or spell_codegen_creation.override_mutation_plan_rows is not None
                    or spell_codegen_creation.override_mutation_baseline_executor is not None
            ):
                override_route_config_mutation = CreationContextBuilder._build_override_route_config_from_creation(
                    plan_signature=spell_codegen_creation.override_mutation_plan_signature,
                    path_registry=spell_codegen_creation.override_mutation_path_registry,
                    plan_rows=spell_codegen_creation.override_mutation_plan_rows,
                    root_spell_id=spell_codegen_creation.override_mutation_root_spell_id,
                    spell_lookup=spell_codegen_creation.override_mutation_spell_lookup,
                    empty_shape_key=spell_codegen_creation.override_mutation_empty_shape_key,
                    baseline_executor=spell_codegen_creation.override_mutation_baseline_executor,
                )

        return CreationContext(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            resolve_route_key=resolve_route_key,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
            no_overrides_executor=no_overrides_executor,
            override_targeting=override_targeting,
            override_route_config_no_mutation=override_route_config_no_mutation,
            override_route_config_mutation=override_route_config_mutation,
        )

    @staticmethod
    def _resolve_route_key(
            *,
            spell: "Spell",
            spell_codegen_creation: Any,
    ) -> str:
        """
        Return the runtime execution route for the current spell.

        Contract:
            - Existing-creation spells still force the dedicated runtime route.
            - Constructed spells require `SpellCodegenCreation` to have already
              populated `resolve_route_key`.
        """
        if spell.is_existing_creation:
            return CreationContext.ROUTE_EXISTING_CREATION
        if spell_codegen_creation is None:
            raise RuntimeError(
                "CreationContextBuilder requires SpellCodegenCreation for "
                "constructed spell routes."
            )
        resolve_route_key = spell_codegen_creation.resolve_route_key
        if resolve_route_key is None:
            raise RuntimeError(
                "SpellCodegenCreation did not populate resolve_route_key."
            )
        return resolve_route_key

    @staticmethod
    def _build_override_route_config_from_creation(
            *,
            plan_signature: Optional[Tuple[Any, ...]],
            path_registry: Optional[Any],
            plan_rows: Optional[Sequence[Dict[str, Any]]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            empty_shape_key: Optional[Tuple[Any, ...]],
            baseline_executor: Optional[Callable[..., Any]],
    ) -> Optional[OverrideRouteConfig]:
        """
        Rehydrate one runtime `OverrideRouteConfig` from the flattened creation artifact.

        Contract:
            - Returns `None` only when all route-config fields are absent.
            - Recreates the runtime carrier directly from flattened
              `SpellCodegenCreation` fields.
        """
        if (
                plan_signature is None
                and path_registry is None
                and plan_rows is None
                and root_spell_id is None
                and spell_lookup is None
                and empty_shape_key is None
                and baseline_executor is None
        ):
            return None
        return OverrideRouteConfig(
            plan_signature=plan_signature,
            path_registry=path_registry,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            empty_shape_key=empty_shape_key,
            baseline_executor=baseline_executor,
        )

