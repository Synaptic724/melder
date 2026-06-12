"""
Single executor hydrator for the generalized_cache codegen-creation family.

`hydrate_creation_executors(manifest, resolver)` is the one assembly program
for this family. The live phase-11 step calls it with a `PlanBindingResolver`;
the cache codec calls it with a `SpellbookBindingResolver`. Both receive the
identical final runtime doors, so cache loads can never drift from live builds.

Hydration shape:
    1. Resolve live identity (spells, path registry) through the resolver.
    2. Rebuild lane step adapters from manifest rows.
    3. Build the inner no-overrides executor through the process-wide
       executor *factory* cache: one compile + one exec per source shape,
       one factory call per spell.
    4. Rebuild the shape-dispatching override runtime from manifest rows.
    5. Wrap both lanes in the shared route-keyed CreationContext doors.

Bridging note:
    This module deliberately reuses the generalized family's emitters,
    namespace builders, row hydration, and override-runtime builder. The
    generalized_cache family shares the generalized lane shape by definition.
    When this family is promoted, those helpers should be lifted into
    `shared_assets/` and the private imports below removed.
"""

from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler import (
    compile_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_finalize_creation_context_step import (
    GeneralizedFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.manifest.generalized_cache_manifest import (
    coerce_manifest_sequences,
    validate_generalized_cache_manifest,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    build_executor_factory_source,
    get_or_build_executor_factory,
    split_namespace_for_factory,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)

_EXECUTOR_NAME = "_no_overrides_codegen_creation_executor"
_TRANSIENT_FACTORY_SOURCE_NAME = (
    "<melder_generalized_cache_no_overrides_transient_factory>"
)
_STEP_FACTORY_SOURCE_NAME = (
    "<melder_generalized_cache_no_overrides_step_factory>"
)

# Process-constant names in the step-plan executor namespace. Everything else
# the namespace builder emits is per-spell identity and travels as bindings.
_STEP_LANE_STATIC_KEYS = (
    "MeldExecutionError",
    "SpellSpaceScopeError",
    "SpellGeneralizedCodegenPlanTargetKind",
    "_construct_spell_instance",
    "_raise_meld_construction_error",
    "_get_existing_creation",
    "_register_spell_instance_prebound",
    "_register_spell_instance",
)

# The transient executor namespace is almost entirely per-spell identity
# (unrolled dependency arrays plus live call targets); only the exception type
# is process-constant.
_TRANSIENT_LANE_STATIC_KEYS = (
    "MeldExecutionError",
)

# Null model stand-in for the bridged override-runtime builder: it only reads
# `graph_shape` when no explicit path registry is supplied.
_NULL_MODEL = SimpleNamespace(graph_shape=None)


class GeneralizedCacheHydratedExecutors:
    """
    Hydration result container for one spell.

    Contract:
        - `no_overrides_executor` and `overrides_executor` are the final
          route-keyed CreationContext doors, identical in shape to the
          generalized family's published executors.
        - `inner_no_overrides_executor` is exposed for diagnostics and reuse
          by override-runtime construction only.
    """

    __slots__ = (
        "route_key",
        "fast_transient_no_overrides",
        "inner_no_overrides_executor",
        "no_overrides_executor",
        "overrides_executor",
        "no_overrides_code_object",
        "overrides_code_object",
    )

    def __init__(
            self,
            *,
            route_key: str,
            fast_transient_no_overrides: bool,
            inner_no_overrides_executor: Callable[..., Any],
            no_overrides_executor: Callable[..., Any],
            overrides_executor: Callable[..., Any],
            no_overrides_code_object: Any,
            overrides_code_object: Any,
    ) -> None:
        """
        Build one hydration result container.
        """
        self.route_key = route_key
        self.fast_transient_no_overrides = fast_transient_no_overrides
        self.inner_no_overrides_executor = inner_no_overrides_executor
        self.no_overrides_executor = no_overrides_executor
        self.overrides_executor = overrides_executor
        self.no_overrides_code_object = no_overrides_code_object
        self.overrides_code_object = overrides_code_object


def hydrate_creation_executors(
        *,
        manifest: Dict[str, Any],
        resolver: Any,
) -> GeneralizedCacheHydratedExecutors:
    """
    Hydrate both final runtime doors from one manifest plus one resolver.

    Purpose:
        Provide the single assembly program for this family. Live phase-11
        builds and cache loads both call exactly this function.

    Args:
        manifest:
            Marshal-safe family manifest from
            `build_generalized_cache_manifest` (or a decoded cache package).
        resolver:
            Binding resolver exposing `resolve_spell(spell_id)` and
            `resolve_path_registry()`.

    Returns:
        GeneralizedCacheHydratedExecutors:
            Final doors plus diagnostics for one spell.

    Raises:
        RuntimeError:
            When the manifest is invalid or required identity cannot be
            resolved.
    """
    validate_generalized_cache_manifest(manifest)
    route_key = manifest["route_key"]
    root_spell = resolver.resolve_spell(manifest["root_spell_id"])

    no_overrides_payload = manifest["no_overrides"]
    inner_no_overrides_executor = _hydrate_inner_no_overrides_executor(
        no_overrides_payload=no_overrides_payload,
        resolver=resolver,
    )
    fast_transient_no_overrides = (
        no_overrides_payload["transient_schema"] is not None
    )

    execute_with_overrides = _hydrate_overrides_runtime(
        overrides_payload=manifest["overrides"],
        resolver=resolver,
        root_spell=root_spell,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )

    no_overrides_door = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides,
        spell=root_spell,
        spell_id=root_spell.spell_id,
        owner_creations=root_spell._owner_creations,
        no_overrides_executor=inner_no_overrides_executor,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )
    overrides_door = compile_creation_context_hooks_overrides_only_executor(
        resolve_route_key=route_key,
        spell=root_spell,
        spell_id=root_spell.spell_id,
        owner_creations=root_spell._owner_creations,
        no_overrides_executor=inner_no_overrides_executor,
        execute_with_overrides=execute_with_overrides,
        meld_execution_error_type=MeldExecutionError,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )

    return GeneralizedCacheHydratedExecutors(
        route_key=route_key,
        fast_transient_no_overrides=fast_transient_no_overrides,
        inner_no_overrides_executor=inner_no_overrides_executor,
        no_overrides_executor=no_overrides_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=overrides_door.__code__,
    )


def _hydrate_inner_no_overrides_executor(
        *,
        no_overrides_payload: Dict[str, Any],
        resolver: Any,
) -> Callable[..., Any]:
    """
    Hydrate the inner no-overrides executor through the factory cache.

    Contract:
        - Mirrors the generalized transient-vs-step-plan emission rule exactly.
        - One compile + one exec per emitted source shape per process; one
          factory call per spell.
    """
    spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    steps = _hydrate_steps_from_rows(
        steps_rows=no_overrides_payload["steps_rows"],
        spell_lookup=spell_lookup,
    )

    transient_schema = no_overrides_payload["transient_schema"]
    if transient_schema is not None and _supports_transient_unrolled_plan(steps):
        normalized_transient_schema = _normalize_transient_schema(
            transient_schema=transient_schema,
        )
        transient_source = _build_no_overrides_codegen_executor_source(
            transient_schema=normalized_transient_schema,
        )
        if transient_source is not None:
            transient_namespace = _build_executor_namespace(
                transient_schema=normalized_transient_schema,
                steps=steps,
            )
            return _hydrate_via_factory(
                inner_source=transient_source,
                namespace=transient_namespace,
                static_keys=_TRANSIENT_LANE_STATIC_KEYS,
                source_name=_TRANSIENT_FACTORY_SOURCE_NAME,
            )

    root_instance_key = no_overrides_payload["root_instance_key"]
    if root_instance_key is not None:
        root_instance_key = (root_instance_key[0], root_instance_key[1])
    else:
        root_instance_key = _resolve_root_instance_key(
            steps=steps,
            root_spell_id=no_overrides_payload["root_spell_id"],
        )
    if root_instance_key is None:
        raise RuntimeError(
            "generalized_cache manifest could not resolve a root instance key."
        )
    step_source = _build_step_plan_executor_source(
        steps=steps,
    )
    step_namespace = _build_step_executor_namespace(
        steps=steps,
        root_instance_key=root_instance_key,
    )
    return _hydrate_via_factory(
        inner_source=step_source,
        namespace=step_namespace,
        static_keys=_STEP_LANE_STATIC_KEYS,
        source_name=_STEP_FACTORY_SOURCE_NAME,
    )


def _hydrate_via_factory(
        *,
        inner_source: str,
        namespace: Dict[str, Any],
        static_keys: Tuple[str, ...],
        source_name: str,
) -> Callable[..., Any]:
    """
    Build one executor from emitted source through the shared factory cache.
    """
    static_namespace, bindings = split_namespace_for_factory(
        namespace=namespace,
        static_keys=static_keys,
    )
    factory_source = build_executor_factory_source(
        inner_source=inner_source,
        binding_names=tuple(bindings.keys()),
        executor_name=_EXECUTOR_NAME,
    )
    factory = get_or_build_executor_factory(
        factory_source=factory_source,
        source_name=source_name,
        static_namespace=static_namespace,
    )
    return factory(bindings)


def _hydrate_overrides_runtime(
        *,
        overrides_payload: Dict[str, Any],
        resolver: Any,
        root_spell: Any,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Hydrate the shape-dispatching override runtime from manifest rows.

    Contract:
        - Per-shape override executors still compile lazily at meld time,
          exactly as in the generalized family.
        - The bridged builder receives a null model stand-in plus an explicit
          path registry, so it never reads live plan/model truth here.
    """
    spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=overrides_payload["step_spell_ids"],
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    path_registry = resolver.resolve_path_registry()
    plan_rows = list(overrides_payload["plan_rows"])
    plan_signature = coerce_manifest_sequences(
        overrides_payload["plan_signature"]
    )
    empty_shape_key = coerce_manifest_sequences(
        overrides_payload["empty_shape_key"]
    )

    baseline_executor = compile_overrides_codegen_creation_executor(
        execution_plan=None,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=path_registry,
        plan_rows=plan_rows,
        root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
    )

    finalize_step = GeneralizedFinalizeCreationContextStep()
    return finalize_step._build_overrides_runtime(
        spell_codegen_model=_NULL_MODEL,
        overrides_plan=None,
        root_spell=root_spell,
        base_no_overrides_executor=inner_no_overrides_executor,
        override_targeting=override_targeting,
        plan_signature=plan_signature,
        path_registry=path_registry,
        plan_rows=plan_rows,
        override_root_spell_id=overrides_payload["root_spell_id"],
        spell_lookup=spell_lookup,
        empty_shape_key=empty_shape_key,
        baseline_executor=baseline_executor,
    )


def _resolve_spell_lookup(
        *,
        resolver: Any,
        step_spell_ids: Any,
) -> Dict[str, Any]:
    """
    Resolve one stable spell-id -> Spell map through the binding resolver.
    """
    spell_lookup: Dict[str, Any] = {}
    for spell_id in step_spell_ids:
        if spell_id in spell_lookup:
            continue
        spell_lookup[spell_id] = resolver.resolve_spell(spell_id)
    return spell_lookup


def _deserialize_targets_by_spec(
        serialized_targets_by_spec: Dict[str, Any],
) -> Dict[str, Tuple[SpellOverrideTargetRef, ...]]:
    """
    Rebuild processor override-target rows from serialized tuples.
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
