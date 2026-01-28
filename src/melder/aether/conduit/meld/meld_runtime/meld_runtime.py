from typing import Any, Dict
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
    ExecutionPlanBuilder,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef


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
                 - Phase 8 occurrence plan (if available)
            4. Create a `ResolutionFrame` initialized with the normalized
               overrides from the context.
            5. Instantiate `MeldEngine` and delegate to `engine.run()`.
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
        if context is None:
            raise ValueError("context cannot be None.")

        spell_obj = context.root_spell
        if spell_obj is None:
            raise ValueError("context.root_spell cannot be None.")

        # Work with the concrete Spell facade type when available.
        spell: ISpell = spell_obj

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

        # Phase 5 artifacts may be present for root spells.
        root_blueprint: RootResolutionBlueprint = None
        occurrence_plan = None
        injection_plan = None
        override_patch_map = None
        mutation_patch_map = None
        execution_plan = None
        crafter = spell._crafter
        if crafter is not None:
            root_blueprint = crafter.root_blueprint_phase5
            occurrence_plan = crafter.occurrence_plan_phase8
            injection_plan = crafter.injection_plan_phase9
            override_patch_map = crafter.override_patch_map_phase10
            mutation_patch_map = crafter.mutation_patch_map_phase10
            execution_plan = crafter.execution_plan_phase11

        mutation_override_payload = {}
        try:
            mutation_override_payload = spell.mutation_override
        except Exception:
            mutation_override_payload = {}

        if mutation_override_payload and root_blueprint is None:
            occurrence_plan = None
            injection_plan = None

        # Apply mutation overrides (graph-level) and spell overrides (value-level)
        # if we have a deep blueprint. Fallback to simple overrides otherwise.
        execution_blueprint = root_blueprint
        override_map = {}
        use_phase11 = False
        execution_plan_to_run = execution_plan
        if root_blueprint is not None:
            try:
                if mutation_override_payload:
                    execution_blueprint = apply_phase10_mutation_overrides(
                        blueprint=root_blueprint,
                        mutation_patch_map=mutation_patch_map,
                        mutation_override=mutation_override_payload,
                    )
                    occurrence_plan = None
                    injection_plan = None
                    execution_plan = None
                else:
                    if occurrence_plan is None or injection_plan is None:
                        raise RuntimeError(
                            "Phase 8/9 artifacts are required for meld execution."
                        )

                override_map = apply_phase10_override_payload(
                    override_patch_map=override_patch_map,
                    override_payload=context.overrides,
                )
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=f"Failed to apply overrides for root '{spell.spell_name}': {exc}",
                    inner=exc,
                ) from exc

            use_phase11 = self._phase11_allowed(
                spell=spell,
                context=context,
                execution_plan=execution_plan,
                occurrence_plan=occurrence_plan,
                injection_plan=injection_plan,
                mutation_override_payload=mutation_override_payload,
                override_map=override_map,
            )

            if use_phase11 and execution_plan is None:
                try:
                    builder = ExecutionPlanBuilder(
                        occurrence_plan=occurrence_plan,
                        injection_plan=injection_plan,
                        spell_lookup=spell._spellbook._spell_id_pool,
                    )
                    execution_plan_to_run = builder.build()
                except Exception:
                    use_phase11 = False
                    execution_plan_to_run = None

        # Per-execution ResolutionFrame seeded with per-call overrides.
        frame_overrides = self._build_frame_overrides(
            context_overrides=context.overrides,
            override_map=override_map,
            root_spell_id=spell.spell_index.current,
        )
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
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
        )

        result = None
        try:
            if use_phase11 and execution_plan_to_run is not None:
                result = engine.run_execution_plan(execution_plan_to_run)
            else:
                result = engine.run()
        finally:
            # Always tear down engine + frame to avoid leaks.
            try:
                engine.cleanup()
            except Exception:
                pass

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
    def _build_frame_overrides(
            self,
            *,
            context_overrides,
            override_map,
            root_spell_id: str,
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
            for socket_ref, value in override_map.items():
                if socket_ref.node_id == root_spell_id and len(socket_ref.param_path) == 1:
                    merged[socket_ref.param_name] = value
        return merged

    def _phase11_allowed(
            self,
            *,
            spell: ISpell,
            context: "MeldContext",
            execution_plan,
            occurrence_plan,
            injection_plan,
            mutation_override_payload,
            override_map: Dict[SocketRef, Any],
    ) -> bool:
        """
        Determine whether Phase 11 execution is eligible for this call.
        """
        if occurrence_plan is None or injection_plan is None:
            return False
        if execution_plan is not None:
            if execution_plan.root_spell_id != spell.spell_index.current:
                return False
        elif occurrence_plan.root_spell_id != spell.spell_index.current:
            return False
        if mutation_override_payload:
            return False
        if context.overrides:
            return False
        if override_map:
            return False
        if getattr(spell, "_hooks_enabled", False):
            return False
        if occurrence_plan.contract_overrides_by_occurrence:
            return False
        if occurrence_plan.contract_overrides_by_spell_id:
            return False
        return True
