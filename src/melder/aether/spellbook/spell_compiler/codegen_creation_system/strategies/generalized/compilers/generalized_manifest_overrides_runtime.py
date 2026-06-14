"""
Family-owned override runtime for generalized, with process-wide
shape caches.

Replaces the bridged `GeneralizedFinalizeCreationContextStep._build_overrides_runtime`
with a family-owned implementation whose expensive layers are shared across
every spell in the process:

    shape source   : process-wide, keyed by (plan signature, shape aspects)
    code + exec    : process-wide, via the executor factory cache
    bound executor : per-spell memo (one factory call per shape per spell)

Previously each spell re-emitted, re-compiled (code objects were shared, but
exec was not), and re-exec'd every override shape it encountered. Now two
spells with the same plan shape and override socket shape share one emitted
source and one exec'd factory; specialization per spell is a function call.

The shape dispatch protocol (payload split, socket-shape precheck, last-state
fast path) is a faithful port of the generalized finalize-step runtime.
"""

import threading
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_library import (
    EMPTY_OVERRIDE_VALUES,
    MISSING,
    SpellGeneralizedCodegenPlanTargetKind,
    build_kwargs_with_overrides,
    build_overrides_codegen_creation_step_target_counts_from_rows,
    build_step_override_targets,
    build_step_override_values,
    construct_spell_instance_with_overrides,
    emit_overrides_codegen_creation_executor_shape_source,
    get_existing_creation,
    invoke_spell_with_kwargs,
    raise_override_on_existing_instance,
    register_spell_instance_prebound,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_rows import (
    CodegenStepRuntimeRow,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    build_executor_factory_source,
    get_or_build_executor_factory,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)

OVERRIDES_EXECUTOR_NAME = "_overrides_codegen_creation_executor"

_OVERRIDES_FACTORY_SOURCE_NAME = (
    "<melder_generalized_overrides_shape_factory>"
)

_OVERRIDES_STATIC_NAMESPACE = {
    "MeldExecutionError": MeldExecutionError,
    "Sequence": Sequence,
    "Existence": Existence,
    "SpellGeneralizedCodegenPlanTargetKind": SpellGeneralizedCodegenPlanTargetKind,
    "_MISSING": MISSING,
    "_EMPTY_OVERRIDE_VALUES": EMPTY_OVERRIDE_VALUES,
    "_construct_spell_instance_with_overrides": construct_spell_instance_with_overrides,
    "_build_step_override_values": build_step_override_values,
    "_build_kwargs_with_overrides": build_kwargs_with_overrides,
    "_invoke_spell_with_kwargs": invoke_spell_with_kwargs,
    "_get_existing_creation": get_existing_creation,
    "_register_spell_instance_prebound": register_spell_instance_prebound,
    "_raise_override_on_existing_instance": raise_override_on_existing_instance,
}

# Process-wide emitted-source memo for override shapes. Sources are pure
# functions of (plan rows shape, targeting aspects); the factory cache below
# this layer dedupes compile+exec by source hash, so this memo only avoids
# re-emitting source text. Bounded FIFO, correctness-neutral on eviction.
_SHAPE_SOURCE_CACHE_MAX_ENTRIES = 4096
_shape_source_cache_lock = threading.Lock()
_shape_source_cache: Dict[Tuple[Any, ...], str] = {}


def build_overrides_execute_runtime(
        *,
        plan_rows: Sequence[Dict[str, Any]],
        plan_signature: Tuple[Any, ...],
        empty_shape_key: Tuple[Any, ...],
        root_spell_id: str,
        root_instance_key: Tuple[str, Optional[int]],
        runtime_rows: Tuple[CodegenStepRuntimeRow, ...],
        spell_lookup: Dict[str, Any],
        root_spell: Any,
        override_targeting: Any,
        path_registry: Optional[Any],
) -> Callable[..., Any]:
    """
    Build the shape-dispatching `execute_with_overrides` runtime for one spell.

    Contract:
        - Output callable signature:
          `(caller_creations, overrides, caller_creations_lock_held) -> Any`.
        - Per-shape executors compile lazily at meld time; emitted source and
          exec'd factories are shared process-wide, bound executors are
          memoized per spell.
        - Faithful port of the generalized shape-dispatch semantics: payload
          split, prechecked socket-shape targeting, last-state fast path, and
          the baseline (no-target) executor for `overrides is None` calls.
    """
    identity_bindings = _build_identity_bindings(
        runtime_rows=runtime_rows,
        root_spell_id=root_spell_id,
        root_instance_key=root_instance_key,
    )

    bound_executor_cache: Dict[Tuple[Any, ...], Callable[..., Any]] = {}
    prefilter_step_targets_cache: Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]] = {}
    prefilter_path_metadata_cache: Dict[Any, Tuple[Any, Any]] = {}
    # Last-shape fast path uses one 3-slot list instead of a string-keyed
    # dict: indexed loads/stores beat hashed lookups on the per-meld path.
    # Slots: [socket_shape, root_positional_arity, executor].
    last_state: list = [None, -2, None]

    def _get_or_bind_executor(
            *,
            shape_key: Tuple[Any, ...],
            override_targets_by_spell_id: Dict[str, Tuple[Any, ...]],
            any_overrides_present: bool,
            prefilter_cache_key: Optional[Tuple[Any, ...]],
    ) -> Callable[..., Any]:
        executor = bound_executor_cache.get(shape_key)
        if executor is not None:
            return executor
        step_override_targets = build_step_override_targets(
            steps=runtime_rows,
            override_targets_by_spell_id=override_targets_by_spell_id,
            path_registry=path_registry,
            prefilter_step_targets_cache=prefilter_step_targets_cache,
            prefilter_cache_key=prefilter_cache_key,
            prefilter_path_metadata_cache=prefilter_path_metadata_cache,
        )
        target_counts_by_step = tuple(
            len(step_target_matches)
            for step_target_matches in step_override_targets
        )
        targeted_spell_ids = tuple(sorted(override_targets_by_spell_id.keys()))
        target_counts_by_spell_id = tuple(
            sorted(
                (
                    spell_id,
                    len(targets),
                )
                for spell_id, targets in override_targets_by_spell_id.items()
                if targets
            )
        )
        has_root_positional_override = shape_key[2] >= 0
        source = _get_or_emit_shape_source(
            plan_signature=plan_signature,
            plan_rows=plan_rows,
            root_spell_id=root_spell_id,
            spell_lookup=spell_lookup,
            targeted_spell_ids=targeted_spell_ids,
            target_counts_by_spell_id=target_counts_by_spell_id,
            target_counts_by_step=target_counts_by_step,
            has_root_positional_override=has_root_positional_override,
        )
        bindings = dict(identity_bindings)
        bindings["step_override_targets"] = step_override_targets
        bindings["step_has_targeted_overrides"] = tuple(
            bool(step_targets)
            for step_targets in step_override_targets
        )
        bindings["step_override_target_counts"] = target_counts_by_step
        bindings["any_overrides_present"] = any_overrides_present
        factory_source = build_executor_factory_source(
            inner_source=source,
            binding_names=tuple(bindings.keys()),
            executor_name=OVERRIDES_EXECUTOR_NAME,
        )
        factory = get_or_build_executor_factory(
            factory_source=factory_source,
            source_name=_OVERRIDES_FACTORY_SOURCE_NAME,
            static_namespace=_OVERRIDES_STATIC_NAMESPACE,
        )
        executor = factory(bindings)
        bound_executor_cache[shape_key] = executor
        return executor

    baseline_executor = _get_or_bind_executor(
        shape_key=empty_shape_key,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        prefilter_cache_key=(plan_signature, ()),
    )

    current_root_spell_id = (
        root_spell.spell_index.current or root_spell.spell_id
    )

    # Raw-key-shape cache: the user-facing override KEY SET fully determines
    # targeting, socket shape, and executor selection (values never affect
    # routing). Each entry resolves the target/path pipeline ONCE per key
    # shape and stores: [key_match_pairs, executors_by_arity, has_positional,
    # overlapping]. Overlapping shapes (one socket reachable from multiple
    # keys) keep the legacy per-call resolution because equal-specificity
    # conflict detection is value-dependent by contract.
    raw_shape_cache: Dict[Tuple[str, ...], list] = {}

    def _execute_resolved(
            caller_creations: Any,
            overrides: Optional[dict],
            caller_creations_lock_held: bool,
            owner_creations: Any,
    ) -> Any:
        """
        Legacy full-resolution path: per-call targeting and shape dispatch.
        """
        root_positional_override: Optional[Sequence[Any]] = None
        override_map: Dict[Any, Any] = {}
        socket_shape: Tuple[Tuple[Any, ...], ...] = ()

        target_payload, root_positional_override = _split_override_payload(
            spell=root_spell,
            override_payload=overrides,
        )
        if target_payload:
            try:
                override_map, socket_shape = (
                    override_targeting._apply_with_socket_shape_prechecked(
                        spell_override=target_payload,
                    )
                )
            except MeldExecutionError:
                raise
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=current_root_spell_id,
                    spell_name=root_spell.spell_name,
                    message="Failed to apply overrides.",
                    inner=exc,
                ) from exc

        if root_positional_override is None:
            root_positional_arity = -1
        else:
            root_positional_arity = len(root_positional_override)
        if (
                socket_shape is last_state[0]
                and root_positional_arity == last_state[1]
        ):
            executor = last_state[2]
        else:
            executor = None

        if executor is None:
            shape_key = (
                plan_signature,
                socket_shape,
                root_positional_arity,
            )
            if override_map:
                override_targets_by_spell_id = (
                    _collect_override_targets_from_socket_shape(
                        override_map=override_map,
                        socket_shape=socket_shape,
                    )
                )
            else:
                override_targets_by_spell_id = {}
            executor = _get_or_bind_executor(
                shape_key=shape_key,
                override_targets_by_spell_id=override_targets_by_spell_id,
                any_overrides_present=overrides is not None,
                prefilter_cache_key=(plan_signature, socket_shape),
            )
            last_state[0] = socket_shape
            last_state[1] = root_positional_arity
            last_state[2] = executor

        return executor(
            caller_creations,
            override_map,
            root_positional_override,
            owner_creations=owner_creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )

    def _prepare_raw_shape(
            raw_keys: Tuple[str, ...],
            overrides: dict,
    ) -> list:
        """
        Resolve targeting once for one raw key shape and freeze the routing.

        Contract:
            - Runs the exact legacy pipeline (split + targeting) to compute
              the socket shape and the per-key socket matches.
            - `executors_by_arity` memoizes the bound executor per root
              positional arity (-1 for none), because `__args__` length may
              vary per call within one key shape.
        """
        target_payload, root_positional_override = _split_override_payload(
            spell=root_spell,
            override_payload=overrides,
        )
        key_match_pairs: list = []
        socket_shape: Tuple[Tuple[Any, ...], ...] = ()
        overlapping = False
        if target_payload:
            try:
                override_map, socket_shape = (
                    override_targeting._apply_with_socket_shape_prechecked(
                        spell_override=target_payload,
                    )
                )
            except MeldExecutionError:
                raise
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=current_root_spell_id,
                    spell_name=root_spell.spell_name,
                    message="Failed to apply overrides.",
                    inner=exc,
                ) from exc
            seen_sockets: set = set()
            for raw_key in target_payload:
                matches, _, _ = override_targeting._resolve_targets_for_raw_key(
                    raw_key
                )
                key_match_pairs.append((raw_key, matches))
                for socket_ref in matches:
                    if socket_ref in seen_sockets:
                        overlapping = True
                    seen_sockets.add(socket_ref)

        if root_positional_override is None:
            root_positional_arity = -1
        else:
            root_positional_arity = len(root_positional_override)
        if socket_shape:
            override_targets_by_spell_id = (
                _collect_override_targets_from_socket_shape(
                    override_map={
                        socket_ref: None
                        for _raw_key, matches in key_match_pairs
                        for socket_ref in matches
                    },
                    socket_shape=socket_shape,
                )
            )
        else:
            override_targets_by_spell_id = {}
        executor = _get_or_bind_executor(
            shape_key=(plan_signature, socket_shape, root_positional_arity),
            override_targets_by_spell_id=override_targets_by_spell_id,
            any_overrides_present=True,
            prefilter_cache_key=(plan_signature, socket_shape),
        )
        prepared = [
            tuple(key_match_pairs),
            {root_positional_arity: executor},
            "__args__" in overrides,
            overlapping,
            socket_shape,
            override_targets_by_spell_id,
        ]
        raw_shape_cache[raw_keys] = prepared
        return prepared

    def execute_with_overrides(
            caller_creations: Any,
            overrides: Optional[dict],
            caller_creations_lock_held: bool,
            root_creations: Any = None,
    ) -> Any:
        # Lineage doors pass their lineage-root creations so the lineage OWNER step
        # stores there instead of the binding owner's `_owner_creations`.
        owner_creations = (
            root_creations
            if root_creations is not None
            else root_spell._owner_creations
        )

        if overrides is None:
            return baseline_executor(
                caller_creations,
                {},
                None,
                owner_creations=owner_creations,
                caller_creations_lock_held=caller_creations_lock_held,
            )

        if len(overrides) == 1:
            raw_keys = tuple(overrides)
        else:
            raw_keys = tuple(sorted(overrides))
        prepared = raw_shape_cache.get(raw_keys)
        if prepared is None:
            prepared = _prepare_raw_shape(raw_keys, overrides)
        if prepared[3]:
            # Overlapping targets: value-dependent conflict semantics, keep
            # the legacy per-call resolution path.
            return _execute_resolved(
                caller_creations,
                overrides,
                caller_creations_lock_held,
                owner_creations,
            )

        root_positional_override: Optional[Sequence[Any]] = None
        root_positional_arity = -1
        if prepared[2]:
            raw_args = overrides["__args__"]
            if isinstance(raw_args, tuple):
                root_positional_override = raw_args
            elif isinstance(raw_args, list):
                root_positional_override = tuple(raw_args)
            else:
                raise MeldExecutionError(
                    spell_id=current_root_spell_id,
                    spell_name=root_spell.spell_name,
                    message="__args__ override must be a list or tuple.",
                )
            root_positional_arity = len(root_positional_override)

        override_map: Dict[Any, Any] = {}
        for raw_key, matches in prepared[0]:
            value = overrides[raw_key]
            for socket_ref in matches:
                override_map[socket_ref] = value

        executors_by_arity = prepared[1]
        executor = executors_by_arity.get(root_positional_arity)
        if executor is None:
            executor = _get_or_bind_executor(
                shape_key=(plan_signature, prepared[4], root_positional_arity),
                override_targets_by_spell_id=prepared[5],
                any_overrides_present=True,
                prefilter_cache_key=(plan_signature, prepared[4]),
            )
            executors_by_arity[root_positional_arity] = executor

        return executor(
            caller_creations,
            override_map,
            root_positional_override,
            owner_creations=owner_creations,
            caller_creations_lock_held=caller_creations_lock_held,
        )

    return execute_with_overrides


def _build_identity_bindings(
        *,
        runtime_rows: Tuple[CodegenStepRuntimeRow, ...],
        root_spell_id: str,
        root_instance_key: Tuple[str, Optional[int]],
) -> Dict[str, Any]:
    """
    Build the per-spell identity half of the override executor bindings.

    Shape-dependent keys (`step_override_targets`,
    `step_has_targeted_overrides`, `step_override_target_counts`,
    `any_overrides_present`) are merged per shape by the caller.
    """
    return {
        "steps": runtime_rows,
        "step_spells": tuple(
            runtime_row.spell
            for runtime_row in runtime_rows
        ),
        "step_spell_ids": tuple(
            runtime_row.spell.spell_id
            for runtime_row in runtime_rows
        ),
        "step_has_disposal_methods": tuple(
            runtime_row.spell.has_disposal_methods
            for runtime_row in runtime_rows
        ),
        "step_disposal_methods": tuple(
            runtime_row.spell.disposal_method_names
            for runtime_row in runtime_rows
        ),
        "step_existences": tuple(
            runtime_row.existence
            for runtime_row in runtime_rows
        ),
        "step_creations_target_kinds": tuple(
            runtime_row.creations_target_kind
            for runtime_row in runtime_rows
        ),
        "step_is_root": tuple(
            runtime_row.spell.spell_index.current == root_spell_id
            for runtime_row in runtime_rows
        ),
        "step_is_existing_unique_creation": tuple(
            (
                    runtime_row.spell.existence is Existence.unique
                    and runtime_row.spell.is_existing_creation
            )
            for runtime_row in runtime_rows
        ),
        "step_is_callable_spell": tuple(
            (
                    runtime_row.spell.is_class_spell
                    or runtime_row.spell.is_method_spell
                    or runtime_row.spell.is_lambda_spell
            )
            for runtime_row in runtime_rows
        ),
        "step_instance_keys": tuple(
            runtime_row.instance_key
            for runtime_row in runtime_rows
        ),
        "step_use_spell_lock_hints": tuple(
            runtime_row.use_spell_lock_hint
            for runtime_row in runtime_rows
        ),
        "step_must_register_flags": tuple(
            runtime_row.must_register
            for runtime_row in runtime_rows
        ),
        "root_instance_key": root_instance_key,
        "root_spell_id": root_spell_id,
    }


def _get_or_emit_shape_source(
        *,
        plan_signature: Tuple[Any, ...],
        plan_rows: Sequence[Dict[str, Any]],
        root_spell_id: str,
        spell_lookup: Dict[str, Any],
        targeted_spell_ids: Tuple[str, ...],
        target_counts_by_spell_id: Tuple[Tuple[str, int], ...],
        target_counts_by_step: Tuple[int, ...],
        has_root_positional_override: bool,
) -> str:
    """
    Return emitted shape source from the process-wide memo, emitting on miss.
    """
    source_key = (
        plan_signature,
        targeted_spell_ids,
        target_counts_by_spell_id,
        target_counts_by_step,
        has_root_positional_override,
    )
    source = _shape_source_cache.get(source_key)
    if source is not None:
        return source
    source = emit_overrides_codegen_creation_executor_shape_source(
        plan_rows=plan_rows,
        root_spell_id=root_spell_id,
        spell_lookup=spell_lookup,
        override_targeted_spell_ids=targeted_spell_ids,
        override_target_counts_by_spell_id=target_counts_by_spell_id,
        override_target_counts_by_step=target_counts_by_step,
        has_root_positional_override=has_root_positional_override,
    )
    with _shape_source_cache_lock:
        existing_source = _shape_source_cache.get(source_key)
        if existing_source is not None:
            return existing_source
        while len(_shape_source_cache) >= _SHAPE_SOURCE_CACHE_MAX_ENTRIES:
            oldest_key = next(iter(_shape_source_cache))
            del _shape_source_cache[oldest_key]
        _shape_source_cache[source_key] = source
    return source


def _split_override_payload(
        *,
        spell: Any,
        override_payload: Dict[str, Any],
) -> Tuple[Dict[str, Any], Optional[Sequence[Any]]]:
    """
    Split root positional overrides from targeted socket overrides.
    """
    raw_args = override_payload.get("__args__")
    if raw_args is None:
        return override_payload, None
    if isinstance(raw_args, tuple):
        normalized_root_args = raw_args
    elif isinstance(raw_args, list):
        normalized_root_args = tuple(raw_args)
    else:
        raise MeldExecutionError(
            spell_id=spell.spell_index.current or spell.spell_id,
            spell_name=spell.spell_name,
            message="__args__ override must be a list or tuple.",
        )
    override_payload_size = len(override_payload)
    if override_payload_size == 1:
        return {}, normalized_root_args
    if override_payload_size == 2:
        for param_name, value in override_payload.items():
            if param_name != "__args__":
                return {param_name: value}, normalized_root_args
    normalized_payload: Dict[str, Any] = {}
    for param_name, value in override_payload.items():
        if param_name == "__args__":
            continue
        normalized_payload[param_name] = value
    return normalized_payload, normalized_root_args


def _collect_override_targets_from_socket_shape(
        *,
        override_map: Dict[Any, Any],
        socket_shape: Tuple[Tuple[Any, ...], ...],
) -> Dict[str, Tuple[Any, ...]]:
    """
    Group override targets by spell id from precomputed socket-shape rows.
    """
    if not socket_shape:
        return {}

    shape_row_to_socket_ref: Dict[Tuple[Any, ...], Any] = {}
    for socket_ref in override_map:
        shape_row_to_socket_ref[
            (
                socket_ref.node_id,
                socket_ref.param_path_id,
                socket_ref.param_name,
                _socket_kind_value(socket_ref),
            )
        ] = socket_ref

    by_spell_id: Dict[str, list] = {}
    current_spell_id: Optional[str] = None
    current_bucket: Optional[list] = None
    for shape_row in socket_shape:
        node_id, _, _, _ = shape_row
        socket_ref = shape_row_to_socket_ref[shape_row]
        if node_id != current_spell_id:
            current_spell_id = node_id
            current_bucket = [socket_ref]
            by_spell_id[node_id] = current_bucket
        else:
            if current_bucket is None:
                raise RuntimeError(
                    "Override target bucket was not initialized."
                )
            current_bucket.append(socket_ref)

    return {
        spell_id: tuple(refs)
        for spell_id, refs in by_spell_id.items()
    }


def _socket_kind_value(socket_ref: Any) -> int:
    """
    Return the stable socket-kind integer for one override target row.
    """
    try:
        return socket_ref.socket_kind_value
    except AttributeError:
        return socket_ref.socket_kind.value
