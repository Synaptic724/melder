"""
Experiment helper for persisting and reloading CreationContext-facing assets.

Purpose:
    Keep cache-playground logic out of runtime files while letting experiments
    snapshot the real emitted no-overrides executor artifact, save it, reload
    it, and rebuild a generic `CreationContext`.
"""

import base64
import json
import marshal
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    _compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache,
    compile_overrides_codegen_creation_executor_code_object,
    emit_overrides_codegen_creation_executor_shape_source,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_executor_namespace,
    _build_no_overrides_codegen_executor_source,
    _build_step_plan_executor_source,
    _build_step_executor_namespace,
    _hydrate_steps_from_rows,
    _normalize_transient_schema,
    _resolve_root_instance_key,
    _supports_transient_unrolled_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetSocketRef,
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers as SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    get_or_compile_executor_code,
)


_CACHE_KIND = "creation_context_cache_asset_playground"
_CACHE_VERSION = 1
_NO_OVERRIDES_EXECUTOR_NAME = "_no_overrides_codegen_creation_executor"
_NO_OVERRIDES_TRANSIENT_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_transient_executor>"
)
_NO_OVERRIDES_STEP_SOURCE_NAME = (
    "<melder_no_overrides_codegen_creation_step_executor>"
)


def build_creation_context_cache_asset(
        *,
        spell: Any,
) -> Dict[str, Any]:
    """
    Build one persisted cache asset from the live CreationContext-facing output.

    Contract:
        - Requires constructed-spell phase-11 output to already exist.
        - Snapshots only the no-overrides runtime artifact today.
        - Stores emitted source plus marshaled code object bytes so reload can
          skip `compile()` when desired.
    """
    artifact = spell._compiler_artifact
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError(
            "CreationContext cache export requires spell_codegen_creation."
        )
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_plan is None or spell_codegen_plan.no_overrides_plan is None:
        raise RuntimeError(
            "CreationContext cache export requires a no_overrides lane plan."
        )

    no_overrides_plan = spell_codegen_plan.no_overrides_plan
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
        root_instance_key=no_overrides_plan.root_instance_key,
        transient_schema=transient_schema,
    )
    compiled_code = get_or_compile_executor_code(
        source=emitted_source,
        source_name=source_name,
    )
    creation_metadata = spell_codegen_creation.metadata
    resolve_route_key = creation_metadata.get("resolve_route_key")
    if not isinstance(resolve_route_key, str):
        raise RuntimeError(
            "CreationContext cache export requires resolve_route_key."
        )

    return {
        "cache_kind": _CACHE_KIND,
        "cache_version": _CACHE_VERSION,
        "spell_id": spell.spell_id,
        "resolve_route_key": resolve_route_key,
        "fast_transient_no_overrides_enabled": bool(
            creation_metadata.get("fast_transient_no_overrides_enabled")
        ),
        "no_overrides": {
            "root_spell_id": no_overrides_plan.root_spell_id,
            "step_spell_ids": step_spell_ids,
            "steps_rows": steps_rows,
            "transient_schema": transient_schema,
            "source_name": source_name,
            "source": emitted_source,
            "code_object_base64": base64.b64encode(
                marshal.dumps(compiled_code)
            ).decode("ascii"),
        },
    }


def build_creation_context_override_cache_asset(
        *,
        spell: Any,
        override_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build one persisted override cache asset for a specific override shape.

    Contract:
        - Requires constructed-spell phase-11 output plus a live override
          targeting section.
        - Targets one concrete override payload shape for experimentation.
        - Stores precomputed step-target rows so reload avoids `path_registry`.
    """
    cache_asset = build_creation_context_cache_asset(
        spell=spell,
    )
    artifact = spell._compiler_artifact
    spell_codegen_model = artifact._spell_codegen_model
    spell_codegen_plan = artifact._spell_codegen_plan
    if spell_codegen_model is None or spell_codegen_plan is None:
        raise RuntimeError(
            "Override cache export requires live codegen model and plan."
        )
    overrides_plan = spell_codegen_plan.overrides_plan
    if overrides_plan is None:
        raise RuntimeError(
            "Override cache export requires an overrides lane plan."
        )
    override_targeting_shape = spell_codegen_model.override_targeting_shape
    if override_targeting_shape is None:
        raise RuntimeError(
            "Override cache export requires override_targeting_shape."
        )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_plan.root_spell_id,
        targets_by_spec=override_targeting_shape.targets_by_spec,
        specificity_by_spec=override_targeting_shape.specificity_by_spec,
    )
    override_map, socket_shape = override_targeting._apply_with_socket_shape_prechecked(
        spell_override=override_payload,
    )
    override_targets_by_spell_id = _collect_override_targets_by_spell_id(
        override_map=override_map,
        socket_shape=socket_shape,
    )
    plan_rows = tuple(
        SharedCompilerExecutions.build_phase11_step_ir_row(
            step,
            include_override_metadata=True,
        )
        for step in overrides_plan.steps
    )
    spell_lookup = _build_spell_lookup_from_steps(
        steps=tuple(overrides_plan.steps),
    )
    step_override_targets = _build_step_override_targets_rows(
        plan_rows=plan_rows,
        override_targets_by_spell_id=override_targets_by_spell_id,
    )
    override_targeted_spell_ids = tuple(sorted(override_targets_by_spell_id.keys()))
    override_target_counts_by_spell_id = tuple(
        sorted(
            (
                spell_id,
                len(targets),
            )
            for spell_id, targets in override_targets_by_spell_id.items()
        )
    )
    override_target_counts_by_step = tuple(
        len(targets)
        for targets in step_override_targets
    )
    emitted_source = emit_overrides_codegen_creation_executor_shape_source(
        plan_rows=plan_rows,
        root_spell_id=overrides_plan.root_spell_id,
        spell_lookup=spell_lookup,
        override_targeted_spell_ids=override_targeted_spell_ids,
        override_target_counts_by_spell_id=override_target_counts_by_spell_id,
        override_target_counts_by_step=override_target_counts_by_step,
        has_root_positional_override=False,
    )
    compiled_code = compile_overrides_codegen_creation_executor_code_object(
        source=emitted_source,
    )
    cache_asset["overrides"] = {
        "root_spell_id": overrides_plan.root_spell_id,
        "step_spell_ids": tuple(spell_lookup.keys()),
        "plan_rows": plan_rows,
        "targets_by_spec": _serialize_targets_by_spec(
            override_targeting_shape.targets_by_spec,
        ),
        "specificity_by_spec": dict(override_targeting_shape.specificity_by_spec),
        "override_targets_by_spell_id": _serialize_override_targets_by_spell_id(
            override_targets_by_spell_id,
        ),
        "socket_shape": socket_shape,
        "shape_key": (
            "creation_context_override_experiment",
            socket_shape,
            -1,
        ),
        "step_override_targets": _serialize_step_override_targets(
            step_override_targets,
        ),
        "source": emitted_source,
        "code_object_base64": base64.b64encode(
            marshal.dumps(compiled_code)
        ).decode("ascii"),
    }
    return cache_asset


def write_creation_context_cache_asset(
        *,
        cache_asset: Dict[str, Any],
        path: Path,
) -> None:
    """
    Persist one cache asset to disk as JSON.
    """
    path.write_text(
        json.dumps(cache_asset, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def read_creation_context_cache_asset(
        *,
        path: Path,
) -> Dict[str, Any]:
    """
    Load one cache asset from disk.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def load_creation_context_from_cache_asset(
        *,
        spell: Any,
        cache_asset: Dict[str, Any],
        publish: bool = True,
) -> CreationContext:
    """
    Rebuild one generic `CreationContext` from a persisted cache asset.

    Contract:
        - Rebuilds only the no-overrides runtime artifact today.
        - Uses a stub overrides executor that raises if the experiment drifts
          into override execution.
        - Can publish the rebuilt context back onto the spell for conduit use.
    """
    _validate_cache_asset(cache_asset)
    no_overrides_executor = _load_no_overrides_executor_from_asset(
        spell=spell,
        cache_asset=cache_asset,
    )
    overrides_executor = _build_overrides_stub()
    if "overrides" in cache_asset:
        overrides_executor = _load_overrides_executor_from_asset(
            spell=spell,
            cache_asset=cache_asset,
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
        resolve_route_key=cache_asset["resolve_route_key"],
        fast_transient_no_overrides_enabled=bool(
            cache_asset["fast_transient_no_overrides_enabled"]
        ),
        no_overrides_executor=no_overrides_executor,
        overrides_executor=overrides_executor,
        publish=publish,
    )


def _build_no_overrides_source_package(
        *,
        steps: Tuple[Any, ...],
        root_instance_key: Tuple[str, Optional[int]],
        transient_schema: Optional[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Build emitted no-overrides source and its synthetic source name.
    """
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
    _ = root_instance_key
    return step_source, _NO_OVERRIDES_STEP_SOURCE_NAME


def _load_no_overrides_executor_from_asset(
        *,
        spell: Any,
        cache_asset: Dict[str, Any],
) -> Any:
    """
    Rebuild the no-overrides executor from persisted source/code-object data.
    """
    no_overrides_payload = cache_asset["no_overrides"]
    spellbook = spell._spellbook
    if spellbook is None:
        raise RuntimeError("Spell has no owning Spellbook surface.")
    step_spell_ids = no_overrides_payload["step_spell_ids"]
    spell_lookup: Dict[str, Any] = {}
    for spell_id in step_spell_ids:
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                f"Cached no-overrides payload references unknown spell_id '{spell_id}'."
            )
        spell_lookup[spell_id] = resolved_spell

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
                "Cached no-overrides payload could not resolve root_instance_key."
            )
        namespace = _build_step_executor_namespace(
            steps=steps,
            root_instance_key=root_instance_key,
        )

    code_bytes = base64.b64decode(no_overrides_payload["code_object_base64"])
    code_object = marshal.loads(code_bytes)
    local_namespace: Dict[str, Any] = {}
    exec(
        code_object,
        namespace,
        local_namespace,
    )
    executor = local_namespace.get(_NO_OVERRIDES_EXECUTOR_NAME)
    if not callable(executor):
        raise RuntimeError(
            "Cached no-overrides payload did not define a callable "
            f"{_NO_OVERRIDES_EXECUTOR_NAME}."
        )
    return executor


def _validate_cache_asset(cache_asset: Dict[str, Any]) -> None:
    """
    Validate the outer cache asset envelope.
    """
    if not isinstance(cache_asset, dict):
        raise TypeError("cache_asset must be a dict.")
    if cache_asset.get("cache_kind") != _CACHE_KIND:
        raise RuntimeError("Unsupported creation-context cache asset kind.")
    if cache_asset.get("cache_version") != _CACHE_VERSION:
        raise RuntimeError("Unsupported creation-context cache asset version.")
    if not isinstance(cache_asset.get("resolve_route_key"), str):
        raise RuntimeError("Creation-context cache asset is missing resolve_route_key.")


def _build_spell_lookup_from_steps(
        *,
        steps: Tuple[Any, ...],
) -> Dict[str, Any]:
    """
    Build a stable spell-id lookup from lane-plan steps.
    """
    spell_lookup: Dict[str, Any] = {}
    for step in steps:
        spell_id = step.spell.spell_index.current
        if spell_id in spell_lookup:
            continue
        spell_lookup[spell_id] = step.spell
    return spell_lookup


def _collect_override_targets_by_spell_id(
        *,
        override_map: Dict[Any, Any],
        socket_shape: Tuple[Tuple[Any, ...], ...],
) -> Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]]:
    """
    Group override targets by spell id from one resolved socket shape.
    """
    shape_row_to_socket_ref: Dict[Tuple[Any, ...], SpellOverrideTargetSocketRef] = {}
    for socket_ref in override_map:
        shape_row_to_socket_ref[
            (
                socket_ref.node_id,
                socket_ref.param_path_id,
                socket_ref.param_name,
                socket_ref.socket_kind_value,
            )
        ] = socket_ref
    by_spell_id: Dict[str, list[SpellOverrideTargetSocketRef]] = {}
    for shape_row in socket_shape:
        node_id, _, _, _ = shape_row
        socket_ref = shape_row_to_socket_ref[shape_row]
        bucket = by_spell_id.setdefault(node_id, [])
        bucket.append(socket_ref)
    return {
        spell_id: tuple(refs)
        for spell_id, refs in by_spell_id.items()
    }


def _serialize_targets_by_spec(
        targets_by_spec: Dict[str, Tuple[SpellOverrideTargetRef, ...]],
) -> Dict[str, Tuple[Tuple[Any, ...], ...]]:
    """
    Serialize processor-owned override-target rows.
    """
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
    """
    Rebuild processor-style override-target rows from serialized tuples.
    """
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


def _serialize_override_targets_by_spell_id(
        override_targets_by_spell_id: Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]],
) -> Dict[str, Tuple[Tuple[Any, ...], ...]]:
    """
    Serialize grouped override targets keyed by spell id.
    """
    return {
        spell_id: tuple(
            (
                socket_ref.node_id,
                socket_ref.param_path_id,
                socket_ref.param_name,
                socket_ref.socket_kind_value,
            )
            for socket_ref in socket_refs
        )
        for spell_id, socket_refs in override_targets_by_spell_id.items()
    }


def _deserialize_override_targets_by_spell_id(
        serialized_override_targets: Dict[str, Sequence[Sequence[Any]]],
) -> Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]]:
    """
    Rebuild grouped override targets keyed by spell id.
    """
    rebuilt: Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]] = {}
    for spell_id, target_rows in serialized_override_targets.items():
        rebuilt[spell_id] = tuple(
            SpellOverrideTargetSocketRef(
                node_id=target_row[0],
                param_path_id=target_row[1],
                param_name=target_row[2],
                socket_kind_value=target_row[3],
            )
            for target_row in target_rows
        )
    return rebuilt


def _build_step_override_targets_rows(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        override_targets_by_spell_id: Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]],
) -> Tuple[Tuple[SpellOverrideTargetSocketRef, ...], ...]:
    """
    Build deterministic step-target rows without requiring a live path registry.

    Contract:
        - Supports the experiment's fixed override shape only.
        - Includes all shared-instance targets.
        - Includes all non-shared targets keyed to the step's spell id.
    """
    step_targets = []
    for row in plan_rows:
        spell_id = row["spell_id"]
        spell_targets = override_targets_by_spell_id.get(spell_id, ())
        step_targets.append(tuple(spell_targets))
    return tuple(step_targets)


def _serialize_step_override_targets(
        step_override_targets: Tuple[Tuple[SpellOverrideTargetSocketRef, ...], ...],
) -> Tuple[Tuple[Tuple[Any, ...], ...], ...]:
    """
    Serialize precomputed step-target tuples.
    """
    return tuple(
        tuple(
            (
                socket_ref.node_id,
                socket_ref.param_path_id,
                socket_ref.param_name,
                socket_ref.socket_kind_value,
            )
            for socket_ref in step_targets
        )
        for step_targets in step_override_targets
    )


def _deserialize_step_override_targets(
        serialized_step_targets: Sequence[Sequence[Sequence[Any]]],
) -> Tuple[Tuple[SpellOverrideTargetSocketRef, ...], ...]:
    """
    Rebuild precomputed step-target tuples.
    """
    return tuple(
        tuple(
            SpellOverrideTargetSocketRef(
                node_id=target_row[0],
                param_path_id=target_row[1],
                param_name=target_row[2],
                socket_kind_value=target_row[3],
            )
            for target_row in step_targets
        )
        for step_targets in serialized_step_targets
    )


def _load_overrides_executor_from_asset(
        *,
        spell: Any,
        cache_asset: Dict[str, Any],
) -> Any:
    """
    Rebuild an experiment-scoped overrides executor from persisted assets.

    Contract:
        - Supports the single cached override shape captured by the asset.
        - Uses a precomputed step-target cache to avoid needing `path_registry`.
        - Raises when a different override shape is attempted.
    """
    overrides_payload = cache_asset["overrides"]
    spellbook = spell._spellbook
    if spellbook is None:
        raise RuntimeError("Spell has no owning Spellbook surface.")

    step_spell_ids = overrides_payload["step_spell_ids"]
    spell_lookup: Dict[str, Any] = {}
    for spell_id in step_spell_ids:
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                f"Cached overrides payload references unknown spell_id '{spell_id}'."
            )
        spell_lookup[spell_id] = resolved_spell

    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=overrides_payload["specificity_by_spec"],
    )
    override_targets_by_spell_id = _deserialize_override_targets_by_spell_id(
        overrides_payload["override_targets_by_spell_id"],
    )
    cached_socket_shape = tuple(
        tuple(socket_shape_row)
        for socket_shape_row in overrides_payload["socket_shape"]
    )
    raw_shape_key = overrides_payload["shape_key"]
    shape_key = (
        raw_shape_key[0],
        tuple(
            tuple(shape_row)
            for shape_row in raw_shape_key[1]
        ),
        raw_shape_key[2],
    )
    precomputed_step_targets = _deserialize_step_override_targets(
        overrides_payload["step_override_targets"],
    )
    code_object = marshal.loads(
        base64.b64decode(overrides_payload["code_object_base64"])
    )
    compiled_executor = _compile_overrides_codegen_creation_executor_from_code_object_with_prefilter_cache(
        code_object=code_object,
        execution_plan=None,
        override_targets_by_spell_id=override_targets_by_spell_id,
        any_overrides_present=True,
        path_registry=None,
        plan_rows=overrides_payload["plan_rows"],
        root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
        prefilter_step_targets_cache={shape_key: precomputed_step_targets},
        prefilter_cache_key=shape_key,
        prefilter_path_metadata_cache={},
    )

    def execute_with_overrides(
            caller_creations: Any,
            overrides: Optional[dict[str, Any]],
            caller_creations_lock_held: bool,
    ) -> Any:
        if not overrides:
            raise RuntimeError(
                "Cached override experiment requires an override payload."
            )
        override_map, socket_shape = (
            override_targeting._apply_with_socket_shape_prechecked(
                spell_override=overrides,
            )
        )
        normalized_shape = tuple(
            tuple(shape_row)
            for shape_row in socket_shape
        )
        if normalized_shape != cached_socket_shape:
            raise RuntimeError(
                "Cached override experiment only supports the recorded override shape."
            )
        owner_creations = spell._owner_creations
        return compiled_executor(
            caller_creations,
            override_map,
            None,
            owner_creations=owner_creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )

    return execute_with_overrides


def _build_overrides_stub() -> Any:
    """
    Return the experimental override stub used by the cache-playground loader.
    """
    def execute_with_overrides(
            caller_creations: Any,
            overrides: Optional[dict[str, Any]],
            caller_creations_lock_held: bool,
    ) -> Any:
        _ = caller_creations
        _ = overrides
        _ = caller_creations_lock_held
        raise RuntimeError(
            "Creation-context cache asset experiment does not rebuild override executors."
        )

    return execute_with_overrides
