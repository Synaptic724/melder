from typing import Any, Dict, Optional
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    apply_phase10_mutation_overrides,
    apply_phase10_override_payload,
)
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanVariant,
)
from melder.spellbook.spell_crafter.dag.dag_index import PathRegistry, SocketRef


class MeldRuntime:
    """
    Orchestration façade for meld execution.

    `MeldRuntime` sits between the Conduit-level `Meld` façade and the
    low-level `MeldEngine`. It owns **no spell-specific state** and can
    be:

        * Constructed per-Conduit, or
        * Shared across multiple conduits (if desired later).

    Responsibilities
    ----------------

    * Perform **pre-flight checks** on the root spell:

        - Must not be broken (`spell.is_broken`).
        - Should be validated (`spell.validated`).
        - May have a dependency graph / resolution frame attached.

    * Create a **ResolutionFrame** per execution, initialized with
      per-call overrides from `MeldContext`.

    * Construct and invoke a **MeldEngine** to actually create the
      instance.

    * Ensure deterministic cleanup of the engine and frame after
      execution.

    This class deliberately does **not** know anything about Creations
    or Existence semantics; those remain in `Meld`. The runtime only
    focuses on "given this spell and this context, build me the object".
    """
    __melder_internal__ = _mrg.sentinel

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #

    def execute(self, context: "MeldContext") -> Any:
        """
        Execute a single meld call described by `context`.

        This method is the **primary entrypoint** that `Meld` should
        call when it needs to construct a new root instance.

        Flow:
            1. Validate the runtime and context.
            2. Perform basic spell invariants:
                 - not broken
                 - validated
            3. Snapshot build-time artifacts from the spell:
                 - dependency graph
                 - requirements
                 - resolution frame (if any)
            4. Create a `ResolutionFrame` initialized with the normalized
               overrides from the context when overrides or mutations apply.
            5. Instantiate `MeldEngine` and execute the Phase 11 execution plan.
               When no overrides or mutations are present, uses the no-overrides
               execution path and skips override preprocessing.
            6. Clean up engine and frame.
            7. Sanity-check the result for factory-style spells.

        Returns:
            The constructed root instance.

        Raises:
            MeldExecutionError:
                If the spell is broken or has not been validated, or if
                the engine fails with a DI-related error, or if a
                factory-style spell yields no instance.
            ValueError:
                If the context is None or missing a root spell.
        """
        spell: ISpell = context.root_spell

        # ------------------------------------------------------------------ #
        # System-level gating (Phase 6 / Change-control)                    #
        # ------------------------------------------------------------------ #
        if spell._spellbook._spellbook_validation_required:
            if spell.system_state is not None:
                validity = spell.system_state.validity
                if validity in (
                        SpellValidity.invalid,
                        SpellValidity.gated,
                        SpellValidity.disabled,
                ):
                    raise MeldExecutionError(
                        spell_id=spell.spell_index.current,
                        spell_name=spell.spell_name,
                        message=(
                            "Cannot execute meld runtime for a spell whose lineage is "
                            f"{validity.name}."
                        ),
                    )

            # Change-control dirty-root gating
            try:
                spellbook = spell._spellbook
                aether = spellbook._aether
                manager = aether._get_change_control_manager(spell.aetheric_frame)
                if manager is not None and manager.is_root_dirty(spell.spell_index.current):
                    raise MeldExecutionError(
                        spell_id=spell.spell_index.current,
                        spell_name=spell.spell_name,
                        message=(
                            "Cannot execute meld runtime while the root is marked dirty. "
                            "Revalidation is required."
                            ),
                        )
            except MeldExecutionError:
                raise
            except Exception:
                # Change-control is optional; if unavailable we proceed.
                pass

            # --- Invariants from the SpellCrafter / validation pipeline ----
            if spell.is_broken:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="Cannot execute meld runtime for a broken spell.",
                )

            if not spell.validated:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Spell has not been validated. Run the SpellCrafter "
                        "phases before attempting to meld this spell."
                    ),
                )

        # Snapshot build-time artifacts. These may be None depending on
        # how far the SpellCrafter pipeline has run; the engine can decide
        # how much it needs for the current MVP.
        dag = spell.dependency_graph
        requirements = spell.requirements
        resolution_frame = spell.resolution_frame
        crafter = spell._crafter
        root_blueprint = crafter.root_blueprint_phase5
        override_patch_map = crafter.override_patch_map_phase10
        mutation_patch_map = crafter.mutation_patch_map_phase10
        execution_plan_no_overrides = crafter.execution_plan_phase11_no_overrides
        execution_plan_overrides = crafter.execution_plan_phase11_overrides
        execution_plan_overrides_with_mutations = crafter.execution_plan_phase11_overrides_with_mutations
        mutation_override_payload = spell.mutation_override
        override_payload = context.overrides
        has_override_payload = bool(override_payload)
        has_mutation_overrides = bool(mutation_override_payload)
        has_overrides_or_mutations = has_override_payload or has_mutation_overrides


        # Apply mutation overrides (graph-level) and spell overrides (value-level)
        # if we have a deep blueprint. Fallback to simple overrides otherwise.
        execution_blueprint = root_blueprint
        override_map: Optional[Dict[SocketRef, Any]] = None
        if root_blueprint is not None and has_overrides_or_mutations:
            try:
                if has_mutation_overrides:
                    execution_blueprint = apply_phase10_mutation_overrides(
                        blueprint=root_blueprint,
                        mutation_patch_map=mutation_patch_map,
                        mutation_override=mutation_override_payload,
                    )

                if has_override_payload:
                    override_map = apply_phase10_override_payload(
                        override_patch_map=override_patch_map,
                        override_payload=override_payload,
                    )
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=f"Failed to apply overrides for root '{spell.spell_name}': {exc}",
                    inner=exc,
                ) from exc

        if has_overrides_or_mutations:
            execution_plan_to_run, _ = self._select_execution_plan_phase11(
                execution_plan_no_overrides=execution_plan_no_overrides,
                execution_plan_overrides=execution_plan_overrides,
                execution_plan_overrides_with_mutations=execution_plan_overrides_with_mutations,
                override_payload=override_payload,
                override_map=override_map,
                mutation_override_payload=mutation_override_payload,
            )
        else:
            execution_plan_to_run = execution_plan_no_overrides

        # Per-execution ResolutionFrame seeded with per-call overrides.
        frame_overrides: Optional[Dict[str, Any]] = None
        if override_payload or override_map:
            frame_overrides = self._build_frame_overrides(
                context_overrides=override_payload,
                override_map=override_map,
                root_spell_id=spell.spell_index.current,
                path_registry=execution_blueprint.path_registry if execution_blueprint else None,
            )

        frame: Optional[ResolutionFrame] = None
        if has_overrides_or_mutations:
            frame = ResolutionFrame(overrides=frame_overrides)
        else:
            if (
                    execution_plan_to_run is None
                    or execution_plan_to_run.fast_plan is None
            ):
                frame = ResolutionFrame(overrides=frame_overrides)
        engine = MeldEngine(
            context=context,
            root_spell=spell,
            dag=dag,
            resolution_frame=resolution_frame,
            requirements=requirements,
            frame=frame,
            blueprint=execution_blueprint,
            override_map=override_map,
            spell_lookup=spell._spellbook._spell_id_pool,
            system_states=spell._spell_system_states,
        )

        result = None
        try:
            if has_overrides_or_mutations:
                override_targets_by_spell_id = self._collect_override_targets(override_map)
                any_overrides_present = self._detect_any_overrides(
                    override_payload=override_payload,
                    override_map=override_map,
                    contract_overrides_by_spell_id={},
                )
                result = engine.run_execution_plan(
                    execution_plan_to_run,
                    override_targets_by_spell_id=override_targets_by_spell_id,
                    any_overrides_present=any_overrides_present,
                )
            else:
                result = engine.run_execution_plan_no_overrides(
                    execution_plan_to_run,
                )
        finally:
            # Always tear down engine + frame to avoid leaks.
            try:
                engine.cleanup()
            except Exception:
                pass

            if frame is not None:
                try:
                    frame.cleanup()
                except Exception:
                    pass

        # ------------------------------------------------------------------
        # Sanity check: factory-style spells must produce an instance.
        #
        # For EXISTING_CREATION spells, reuse is handled earlier in Meld
        # (via _get_existing_creation). For class/method/lambda spells,
        # a `None` result usually indicates a bug in the engine or the
        # callable, so we surface it as a deterministic MeldExecutionError.
        # ------------------------------------------------------------------
        if (
                result is None
                and (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell)
        ):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "MeldEngine returned None for a factory-style spell. "
                    "This usually indicates a bug in the DI pipeline or the "
                    "spell's constructor."
                ),
            )

        return result

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _select_execution_plan_phase11(
            self,
            *,
            execution_plan_no_overrides: Optional[ExecutionPlan],
            execution_plan_overrides: Optional[ExecutionPlan],
            execution_plan_overrides_with_mutations: Optional[ExecutionPlan],
            override_payload: Optional[Dict[str, Any]],
            override_map: Optional[Dict[SocketRef, Any]],
            mutation_override_payload: Optional[Dict[str, Any]],
    ) -> tuple[Optional[ExecutionPlan], Optional[str]]:
        """
        Select the Phase 11 execution plan variant for the current meld call.
        """
        has_override_payload = bool(override_payload) or bool(override_map)
        has_mutation_overrides = bool(mutation_override_payload)

        if has_mutation_overrides:
            return (
                execution_plan_overrides_with_mutations,
                ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
            )
        if has_override_payload:
            return (
                execution_plan_overrides,
                ExecutionPlanVariant.OVERRIDES,
            )
        return (
            execution_plan_no_overrides,
            ExecutionPlanVariant.NO_OVERRIDES_FAST,
        )

    @staticmethod
    def _collect_override_targets(
            override_map: Optional[Dict[SocketRef, Any]],
    ) -> Dict[str, list[SocketRef]]:
        """
        Group override targets by spell id for fast-path validation.

        Contract:
            - Keys are spell version ids.
            - Values are the SocketRef entries targeted by overrides.
        """
        if not override_map:
            return {}
        targets: Dict[str, list[SocketRef]] = {}
        for socket_ref in override_map:
            targets.setdefault(socket_ref.node_id, []).append(socket_ref)
        return targets

    @staticmethod
    def _detect_any_overrides(
            *,
            override_payload: Optional[Dict[str, Any]],
            override_map: Optional[Dict[SocketRef, Any]],
            contract_overrides_by_spell_id: Dict[str, Any],
    ) -> bool:
        """
        Determine whether any overrides apply to the current meld call.

        Contract:
            - Returns True when socket overrides, root overrides, or contract overrides are present.
            - Treats empty dictionaries as no overrides.
        """
        if override_map:
            return True
        if contract_overrides_by_spell_id:
            return True
        return bool(override_payload)

    def _build_frame_overrides(
            self,
            *,
            context_overrides,
            override_map,
            root_spell_id: str,
            path_registry: Optional[PathRegistry],
    ):
        """
        Merge plain context overrides with socket-level override_map.

        For the current MVP engine (single-node), we fold any SocketRef
        that targets the root node and has a single-segment path into
        keyword overrides.
        """
        merged = {}
        # Preserve positional args if supplied.
        if isinstance(context_overrides, dict):
            if "__args__" in context_overrides:
                merged["__args__"] = list(context_overrides["__args__"])
            # Also keep any direct kw overrides.
            for k, v in context_overrides.items():
                if k == "__args__":
                    continue
                merged[k] = v

        if override_map:
            if path_registry is None:
                raise RuntimeError("PathRegistry is required to interpret override paths.")
            for socket_ref, value in override_map.items():
                if (
                        socket_ref.node_id == root_spell_id
                        and path_registry.depth(socket_ref.param_path_id) == 1
                ):
                    merged[socket_ref.param_name] = value
        return merged
