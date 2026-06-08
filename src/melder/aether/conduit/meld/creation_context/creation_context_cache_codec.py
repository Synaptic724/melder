"""
Reloadable codec for CreationContext-facing phase-11 assets.

Purpose:
    Build and reload the durable, conduit-agnostic cache payload for one
    spell's runtime lanes (no_overrides + overrides). The cached unit is
    schema-only data:
      - the *inner* no_overrides codegen executor (emitted source compiled to a
        `CodeType`) plus the rows needed to rebuild its execution namespace, and
      - the override lane's plan rows + targeting rows + plan signature, which
        rebuild the shape-dispatching override runtime against a live phase-5
        `PathRegistry`.
    The owner-dependent outer route wrappers are rebuilt at load time, so no
    per-conduit runtime object is ever frozen into the cache.

Contract:
    - `build_package(spell)` returns a marshal-safe dict (primitives, tuples,
      dicts, and one `CodeType`) covering both lanes.
    - `load_creation_context(spell, package, publish=...)` rebuilds both inner
      executors against the live Spellbook + live phase-5 path registry, wraps
      each with the final hook-aware doors phase 11 would emit for the live
      spell, and returns a published-or-detached `CreationContext`.
    - The payload excludes any per-conduit runtime object, so a cached package
      is reusable across conduits/runs (subject to the Python-version stamp
      owned by `CachingSystem`).

Reload invariants:
    - The override runtime is rebuilt by reusing
      `GeneralizedFinalizeCreationContextStep._build_overrides_runtime` (the
      step has empty slots / self-free helpers), fed cached rows and the live
      phase-5 `PathRegistry` from `artifact._root_blueprint_phase5`.
    - Per-shape override executors still compile lazily at meld time, exactly
      as in the non-cached runtime; the cache only skips phases 8-10 analysis.
"""

from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_executor_namespace,
    _build_no_overrides_codegen_executor_source,
    _build_step_executor_namespace,
    _build_step_plan_executor_source,
    _hydrate_steps_from_rows,
    _normalize_transient_schema,
    _resolve_root_instance_key,
    _supports_transient_unrolled_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_finalize_creation_context_step import (
    GeneralizedFinalizeCreationContextStep,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)


PACKAGE_VERSION: int = 1
_NO_OVERRIDES_EXECUTOR_NAME = "_no_overrides_codegen_creation_executor"
_NO_OVERRIDES_TRANSIENT_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_transient_executor>"
)
_NO_OVERRIDES_STEP_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_step_executor>"
)


# ---------------------------------------------------------------------------
# Build (emit)
# ---------------------------------------------------------------------------

def build_package(spell: Any) -> Dict[str, Any]:
    """
    Build the marshal-safe both-lane cache package for one constructed spell.

    Contract:
        - Requires constructed-spell phase-11 output (creation + plan + model).
        - Returns a dict of primitives/tuples/dicts plus the inner no_overrides
          `CodeType`. The override lane is row-only (no code object).

    Raises:
        RuntimeError:
            When phase-11 creation/plan/model output is missing.
    """
    artifact = spell._compiler_artifact
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError("cache export requires spell_codegen_creation.")
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_plan is None or spell_codegen_plan.no_overrides_plan is None:
        raise RuntimeError("cache export requires a no_overrides lane plan.")
    spell_codegen_model = artifact._spell_codegen_model
    if spell_codegen_model is None:
        raise RuntimeError("cache export requires a spell_codegen_model.")

    package = {
        "package_version": PACKAGE_VERSION,
        "spell_id": spell.spell_id,
        "no_overrides": _build_no_overrides_subpackage(
            no_overrides_plan=spell_codegen_plan.no_overrides_plan,
        ),
        "overrides": _build_overrides_subpackage(
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_model=spell_codegen_model,
        ),
    }
    return package


def _build_no_overrides_subpackage(*, no_overrides_plan: Any) -> Dict[str, Any]:
    """Build the row-only + inner-code no_overrides subpackage."""
    steps = tuple(no_overrides_plan.steps)
    steps_rows = tuple(
        SharedCompilerExecutions.build_phase11_step_ir_row(
            step,
            include_override_metadata=False,
        )
        for step in steps
    )
    step_spell_ids = tuple(
        step.spell.spell_index.current
        for step in steps
    )
    transient_schema = SharedCompilerExecutions.build_fast_transient_schema(
        no_overrides_plan.fast_transient_plan,
    )
    emitted_source, source_name = _build_no_overrides_source_package(
        steps=steps,
        transient_schema=transient_schema,
    )
    return {
        "root_spell_id": no_overrides_plan.root_spell_id,
        "step_spell_ids": step_spell_ids,
        "steps_rows": steps_rows,
        "transient_schema": transient_schema,
        "source_name": source_name,
        "code_object": compile(emitted_source, source_name, "exec"),
    }


def _build_overrides_subpackage(
        *,
        spell_codegen_plan: Any,
        spell_codegen_model: Any,
) -> Optional[Dict[str, Any]]:
    """
    Build the row-only overrides subpackage, or None when no override lane.

    The override lane is rebuilt at load against the live phase-5 path
    registry, so no compiled code object is persisted here.
    """
    overrides_plan = spell_codegen_plan.overrides_plan
    override_targeting_shape = spell_codegen_model.override_targeting_shape
    if overrides_plan is None or override_targeting_shape is None:
        return None

    plan_rows = tuple(
        SharedCompilerExecutions.build_phase11_step_ir_row(
            step,
            include_override_metadata=True,
        )
        for step in overrides_plan.steps
    )
    step_spell_ids = tuple(
        step.spell.spell_index.current
        for step in overrides_plan.steps
    )
    plan_signature = GeneralizedFinalizeCreationContextStep._build_override_plan_signature(
        overrides_plan=overrides_plan,
        plan_rows=plan_rows,
    )
    empty_shape_key = (plan_signature, (), -1)
    return {
        "root_spell_id": overrides_plan.root_spell_id,
        "step_spell_ids": step_spell_ids,
        "plan_rows": plan_rows,
        "plan_signature": plan_signature,
        "empty_shape_key": empty_shape_key,
        "targets_by_spec": _serialize_targets_by_spec(
            override_targeting_shape.targets_by_spec,
        ),
        "specificity_by_spec": dict(override_targeting_shape.specificity_by_spec),
    }


# ---------------------------------------------------------------------------
# Load (reload)
# ---------------------------------------------------------------------------

def load_creation_context(
        spell: Any,
        package: Dict[str, Any],
        *,
        publish: bool = True,
) -> CreationContext:
    """
    Rebuild one spell-bound `CreationContext` from a cache package.

    Contract:
        - Rebuilds both runtime lanes against the live Spellbook and the live
          phase-5 path registry, then wraps each with the final hook-aware
          phase-11 doors for the live spell.
        - Requires phases 1-7 to have already run for `spell` (so the phase-5
          blueprint + path registry are live) and ownership to be wired (so
          `spell._owner_creations` is set).
    """
    resolve_route_key = _resolve_route_key_for_spell(spell)
    fast_transient_no_overrides_enabled = _has_fast_transient_no_overrides(
        package
    )
    inner_no_overrides = _build_inner_no_overrides_executor(spell, package)
    outer_no_overrides = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=resolve_route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides_enabled,
        spell=spell,
        spell_id=spell.spell_id,
        owner_creations=spell._owner_creations,
        no_overrides_executor=inner_no_overrides,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )

    overrides_payload = package.get("overrides")
    if overrides_payload is None:
        outer_overrides = _build_missing_overrides_executor(spell)
    else:
        inner_overrides = _build_inner_overrides_runtime(
            spell=spell,
            overrides_payload=overrides_payload,
            base_no_overrides_executor=inner_no_overrides,
        )
        outer_overrides = compile_creation_context_hooks_overrides_only_executor(
            resolve_route_key=resolve_route_key,
            spell=spell,
            spell_id=spell.spell_id,
            owner_creations=spell._owner_creations,
            no_overrides_executor=inner_no_overrides,
            execute_with_overrides=inner_overrides,
            meld_execution_error_type=MeldExecutionError,
            spell_space_scope_error_type=SpellSpaceScopeError,
        )

    creation_context_factory = spell._creation_context_factory
    if creation_context_factory is None:
        raise RuntimeError("Spell has no CreationContextFactory.")
    creation_gate, creation_gate_index_id = (
        creation_context_factory._resolve_runtime_gate_for_spell(spell)
    )
    return CreationContext.load_cached(
        spell=spell,
        dynamic_environment=spell._dynamic_environment,
        creation_gate=creation_gate,
        creation_gate_index_id=creation_gate_index_id,
        no_overrides_executor=outer_no_overrides,
        overrides_executor=outer_overrides,
        publish=publish,
    )


def _build_inner_no_overrides_executor(
        spell: Any,
        package: Dict[str, Any],
) -> Any:
    """Rebuild the inner no_overrides executor from its cached package."""
    no_overrides_payload = package["no_overrides"]
    spell_lookup = _resolve_spell_lookup(
        spell=spell,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
        lane="no_overrides",
    )
    steps = _hydrate_steps_from_rows(
        steps_rows=no_overrides_payload["steps_rows"],
        spell_lookup=spell_lookup,
    )
    transient_schema = no_overrides_payload["transient_schema"]
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        namespace = _build_executor_namespace(
            transient_schema=_normalize_transient_schema(
                transient_schema=transient_schema,
            ),
            steps=steps,
        )
    else:
        root_instance_key = _resolve_root_instance_key(
            steps=steps,
            root_spell_id=no_overrides_payload["root_spell_id"],
        )
        if root_instance_key is None:
            raise RuntimeError(
                "Cached no_overrides payload could not resolve root_instance_key."
            )
        namespace = _build_step_executor_namespace(
            steps=steps,
            root_instance_key=root_instance_key,
        )

    local_namespace: Dict[str, Any] = {}
    exec(no_overrides_payload["code_object"], namespace, local_namespace)
    inner_executor = local_namespace.get(_NO_OVERRIDES_EXECUTOR_NAME)
    if not callable(inner_executor):
        raise RuntimeError(
            "Cached no_overrides payload did not define a callable "
            f"{_NO_OVERRIDES_EXECUTOR_NAME}."
        )
    return inner_executor


def _build_inner_overrides_runtime(
        *,
        spell: Any,
        overrides_payload: Dict[str, Any],
        base_no_overrides_executor: Any,
) -> Any:
    """
    Rebuild the inner shape-dispatching override runtime from cached rows.

    Reuses the phase-11 finalize builder fed cached rows plus the live phase-5
    path registry, so arbitrary override shapes still compile lazily at meld.
    """
    spell_lookup = _resolve_spell_lookup(
        spell=spell,
        step_spell_ids=overrides_payload["step_spell_ids"],
        lane="overrides",
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    path_registry = _resolve_live_path_registry(spell)
    plan_signature = _as_tuple(overrides_payload["plan_signature"])
    empty_shape_key = _as_tuple(overrides_payload["empty_shape_key"])
    plan_rows = list(overrides_payload["plan_rows"])

    finalize_step = GeneralizedFinalizeCreationContextStep()
    return finalize_step._build_overrides_runtime(
        spell_codegen_model=None,
        overrides_plan=None,
        root_spell=spell,
        base_no_overrides_executor=base_no_overrides_executor,
        override_targeting=override_targeting,
        plan_signature=plan_signature,
        path_registry=path_registry,
        plan_rows=plan_rows,
        override_root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
        empty_shape_key=empty_shape_key,
        baseline_executor=None,
    )


def _build_missing_overrides_executor(spell: Any) -> Any:
    """
    Build an outer overrides executor for a spell with no cached override lane.

    Raises on use, mirroring "no override lane" rather than silently degrading.
    """
    def execute_with_overrides(
            caller_creations: Any,
            overrides: Optional[dict],
            caller_creations_lock_held: bool,
    ) -> Any:
        _ = (caller_creations, overrides, caller_creations_lock_held)
        raise RuntimeError(
            "Cached spell has no override lane "
            f"(spell_id={spell.spell_id})."
        )

    return compile_creation_context_hooks_overrides_only_executor(
        resolve_route_key=_resolve_route_key_for_spell(spell),
        spell=spell,
        spell_id=spell.spell_id,
        owner_creations=spell._owner_creations,
        no_overrides_executor=None,
        execute_with_overrides=execute_with_overrides,
        meld_execution_error_type=MeldExecutionError,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_spell_lookup(
        *,
        spell: Any,
        step_spell_ids: Sequence[str],
        lane: str,
) -> Dict[str, Any]:
    """Resolve a stable spell-id -> Spell map from the live Spellbook pool."""
    spellbook = spell._spellbook
    if spellbook is None:
        raise RuntimeError("Spell has no owning Spellbook surface.")
    spell_lookup: Dict[str, Any] = {}
    for spell_id in step_spell_ids:
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                f"Cached {lane} payload references unknown spell_id "
                f"'{spell_id}'."
            )
        spell_lookup[spell_id] = resolved_spell
    return spell_lookup


def _resolve_live_path_registry(spell: Any) -> Any:
    """
    Return the live phase-5 path registry for the spell.

    The override runtime needs this to compile per-shape executors at meld
    time. Phase 5 (always run on conjure) builds it and `reset_phase_artifacts`
    preserves it, so it is live after conjure.
    """
    artifact = spell._compiler_artifact
    if artifact is None:
        raise RuntimeError("Spell has no compiler artifact for override reload.")
    root_blueprint = artifact._root_blueprint_phase5
    if root_blueprint is None:
        raise RuntimeError(
            "Override reload requires a live phase-5 root blueprint "
            f"(spell_id={spell.spell_id})."
        )
    return root_blueprint.path_registry


def _build_no_overrides_source_package(
        *,
        steps: Tuple[Any, ...],
        transient_schema: Optional[Dict[str, Any]],
) -> Tuple[str, str]:
    """Build emitted inner no_overrides source plus its synthetic source name."""
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        transient_source = _build_no_overrides_codegen_executor_source(
            transient_schema=normalized_transient_schema,
        )
        if transient_source is not None:
            return transient_source, _NO_OVERRIDES_TRANSIENT_SOURCE_NAME
    step_source = _build_step_plan_executor_source(
        steps=steps,
    )
    return step_source, _NO_OVERRIDES_STEP_SOURCE_NAME


def _resolve_route_key_for_spell(spell: Any) -> str:
    """Resolve the runtime route key directly from the live spell contract."""
    if spell.is_existing_creation:
        return "existing_creation"
    existence = spell.existence
    if existence is Existence.unique_per_spell_space:
        return "spellspace"
    if existence is Existence.unique_per_conduit:
        return "unique_per_conduit"
    if existence is Existence.many:
        return "many"
    if existence in (
            Existence.unique,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        return "shared"
    raise RuntimeError(
        f"Spell route is not cacheable for existence {existence!r}."
    )


def _has_fast_transient_no_overrides(package: Dict[str, Any]) -> bool:
    """Return whether the cached no-overrides lane used transient unrolling."""
    return package["no_overrides"]["transient_schema"] is not None


def _serialize_targets_by_spec(
        targets_by_spec: Dict[str, Tuple[Any, ...]],
) -> Dict[str, Tuple[Tuple[Any, ...], ...]]:
    """Serialize processor override-target rows to marshal-safe tuples."""
    return {
        spec_key: tuple(
            (
                target_ref.node_id,
                target_ref.param_path_id,
                target_ref.param_name,
                target_ref.socket_kind_value,
            )
            for target_ref in target_refs
        )
        for spec_key, target_refs in targets_by_spec.items()
    }


def _deserialize_targets_by_spec(
        serialized_targets_by_spec: Dict[str, Sequence[Sequence[Any]]],
) -> Dict[str, Tuple[SpellOverrideTargetRef, ...]]:
    """Rebuild processor override-target rows from serialized tuples."""
    rebuilt: Dict[str, Tuple[SpellOverrideTargetRef, ...]] = {}
    for spec_key, target_rows in serialized_targets_by_spec.items():
        rebuilt[spec_key] = tuple(
            SpellOverrideTargetRef(
                node_id=target_row[0],
                param_path_id=target_row[1],
                param_name=target_row[2],
                socket_kind_value=target_row[3],
            )
            for target_row in target_rows
        )
    return rebuilt


def _as_tuple(value: Any) -> Any:
    """
    Recursively coerce marshal-decoded sequences back into tuples.

    marshal preserves tuples, but be defensive so shape keys/signatures compare
    by value regardless of decoded list/tuple shape.
    """
    if isinstance(value, (list, tuple)):
        return tuple(_as_tuple(item) for item in value)
    return value
