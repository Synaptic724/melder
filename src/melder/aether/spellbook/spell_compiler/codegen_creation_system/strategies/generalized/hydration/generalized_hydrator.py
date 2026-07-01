"""
Single executor hydrator for the generalized codegen-creation family.

`hydrate_creation_executors(manifest, resolver)` is the one assembly program
for this family. The live phase-11 step publishes lazy doors over it; the
cache codec publishes lazy doors over it. Both produce identical hot doors at
first meld, so cache loads can never drift from live builds.

Hydration shape:
    1. Resolve live identity (spells, path registry) through the resolver.
    2. Build slotted runtime rows from manifest rows.
    3. Hydrate the inner no-overrides executor through the family compiler
       (row-driven emission, process-wide factory cache).
    4. Build the family override runtime (process-wide shape source +
       factory caches; per-spell bound-executor memo).
    5. Wrap both lanes in the shared route-keyed CreationContext doors.
"""

import threading
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_library import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    build_specialized_no_overrides_executor,
    hydrate_no_overrides_executor,
    resolve_root_instance_key_from_rows,
    select_specializable_step_indexes,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_overrides_runtime import (
    build_overrides_execute_runtime,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_runtime_rows import (
    build_runtime_rows,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest.generalized_manifest import (
    coerce_manifest_sequences,
    validate_generalized_manifest,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable


class GeneralizedHydratedExecutors(Cleanable):
    """
    Hydration result container for one spell.

    Contract:
        - `no_overrides_executor` and `overrides_executor` are the final
          route-keyed CreationContext doors.
        - `inner_no_overrides_executor` is exposed for diagnostics only.

    Lifecycle / Cleanup:
        - Owned by the lazy-door closure that hydrated it; lives for the
          executor lifetime so cold doors can delegate before the hot swap.
        - `cleanup()` is idempotent and deletes every field. Executors are
          plain callables (no child cleanup); code objects are shared via the
          process-wide caches and are referenced, never owned.
    """

    __slots__ = Cleanable.__slots__ + [
        "route_key",
        "fast_transient_no_overrides",
        "inner_no_overrides_executor",
        "no_overrides_executor",
        "overrides_executor",
        "no_overrides_code_object",
        "overrides_code_object",
    ]

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
        super().__init__()
        self.route_key = route_key
        self.fast_transient_no_overrides = fast_transient_no_overrides
        self.inner_no_overrides_executor = inner_no_overrides_executor
        self.no_overrides_executor = no_overrides_executor
        self.overrides_executor = overrides_executor
        self.no_overrides_code_object = no_overrides_code_object
        self.overrides_code_object = overrides_code_object

    def cleanup(self) -> None:
        """
        Deterministically release the hydration container surface.

        Contract:
            - Idempotent. Every field is deleted; no child cleanup runs
              because executors and code objects are referenced callables and
              cache-shared code, not owned resources.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.route_key
        del self.fast_transient_no_overrides
        del self.inner_no_overrides_executor
        del self.no_overrides_executor
        del self.overrides_executor
        del self.no_overrides_code_object
        del self.overrides_code_object


def build_lazy_creation_executors(
        *,
        manifest: Dict[str, Any],
        spell: Any,
) -> Tuple[Callable[..., Any], Callable[..., Any]]:
    """
    Build cold runtime doors that hydrate on first call, not at build time.

    Purpose:
        Make door construction free at conjure/cache-load time. The returned
        doors close over (manifest, spell) only. The first meld call through
        either door runs `hydrate_creation_executors` exactly once (leader
        hydrates under the lock, followers wait), swaps the hot doors into the
        spell's currently published `CreationContext` executor slots, then
        delegates. Every later meld runs the unwrapped hot path because meld
        re-reads the context slots per call.

    Contract:
        - Zero hydration work at build time: validation plus closure
          construction only.
        - Hydration always resolves through `SpellbookBindingResolver`, so the
          live phase-11 path and the cache-load path execute one identical
          assembly program at one identical time (first meld).
        - Requires phases 1-7 live and ownership wiring at first meld, which
          meld's structural gates already guarantee.
        - If no context is published when hydration completes (publish=False
          loads), the cold doors keep delegating correctly; only the
          swap-to-hot optimization is skipped.
    """
    validate_generalized_manifest(manifest)
    hydration_lock = threading.Lock()
    hydrated_cell: list = [None]

    def _hydrate_once() -> GeneralizedHydratedExecutors:
        hydrated = hydrated_cell[0]
        if hydrated is not None:
            return hydrated
        with hydration_lock:
            hydrated = hydrated_cell[0]
            if hydrated is not None:
                return hydrated
            resolver = SpellbookBindingResolver(spell=spell)
            hydrated = hydrate_creation_executors(
                manifest=manifest,
                resolver=resolver,
            )
            resolver.cleanup()
            hydrated_cell[0] = hydrated
            published_context = spell._creation_context
            if published_context is not None:
                published_context._no_overrides_executor = (
                    hydrated.no_overrides_executor
                )
                published_context._overrides_executor = (
                    hydrated.overrides_executor
                )
            return hydrated

    def _swap_hot_doors(hydrated: GeneralizedHydratedExecutors) -> None:
        published_context = spell._creation_context
        if published_context is not None:
            published_context._no_overrides_executor = (
                hydrated.no_overrides_executor
            )
            published_context._overrides_executor = (
                hydrated.overrides_executor
            )

    def _cold_no_overrides_door(caller_creations: Any) -> Any:
        # Self-healing swap: every cold-path call re-targets the CURRENT
        # published context. A rebuilt context starts with cold doors copied
        # from the creation artifact; its first call lands here and gets the
        # hot doors installed, so cold indirection never persists per meld.
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.no_overrides_executor(caller_creations)

    def _cold_overrides_door(
            caller_creations: Any,
            overrides: Optional[dict],
    ) -> Any:
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.overrides_executor(caller_creations, overrides)

    return _cold_no_overrides_door, _cold_overrides_door


def hydrate_creation_executors(
        *,
        manifest: Dict[str, Any],
        resolver: Any,
) -> GeneralizedHydratedExecutors:
    """
    Hydrate both final runtime doors from one manifest plus one resolver.

    Raises:
        RuntimeError:
            When the manifest is invalid or required identity cannot be
            resolved.
    """
    validate_generalized_manifest(manifest)
    route_key = manifest["route_key"]
    root_spell = resolver.resolve_spell(manifest["root_spell_id"])

    no_overrides_payload = manifest["no_overrides"]
    no_overrides_spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    inner_no_overrides_executor = hydrate_no_overrides_executor(
        rows=no_overrides_payload["steps_rows"],
        transient_schema=no_overrides_payload["transient_schema"],
        root_instance_key=no_overrides_payload["root_instance_key"],
        root_spell_id=no_overrides_payload["root_spell_id"],
        spell_lookup=no_overrides_spell_lookup,
    )
    fast_transient_no_overrides = (
        no_overrides_payload["transient_schema"] is not None
    )

    no_overrides_door = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides,
        spell=root_spell,
        spell_id=root_spell.spell_id,
        no_overrides_executor=inner_no_overrides_executor,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )
    overrides_door = _build_lazy_overrides_door(
        manifest=manifest,
        root_spell=root_spell,
        route_key=route_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )

    final_no_overrides_door = no_overrides_door
    if _specialization_enabled_for_spell(root_spell):
        final_no_overrides_door = _install_specializing_door(
            plain_door=no_overrides_door,
            rows=no_overrides_payload["steps_rows"],
            root_instance_key=no_overrides_payload["root_instance_key"],
            root_spell_id=no_overrides_payload["root_spell_id"],
            spell_lookup=no_overrides_spell_lookup,
            inner_no_overrides_executor=inner_no_overrides_executor,
            route_key=route_key,
            fast_transient_no_overrides=fast_transient_no_overrides,
            root_spell=root_spell,
        )

    return GeneralizedHydratedExecutors(
        route_key=route_key,
        fast_transient_no_overrides=fast_transient_no_overrides,
        inner_no_overrides_executor=inner_no_overrides_executor,
        no_overrides_executor=final_no_overrides_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=None,
    )


def _hydrate_overrides_runtime(
        *,
        overrides_payload: Dict[str, Any],
        resolver: Any,
        root_spell: Any,
) -> Callable[..., Any]:
    """
    Hydrate the family override runtime from manifest rows.
    """
    plan_rows = list(overrides_payload["plan_rows"])
    spell_lookup = _resolve_spell_lookup(
        resolver=resolver,
        step_spell_ids=overrides_payload["step_spell_ids"],
    )
    runtime_rows = build_runtime_rows(
        rows=plan_rows,
        spell_lookup=spell_lookup,
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    root_instance_key = resolve_root_instance_key_from_rows(
        rows=plan_rows,
        explicit_root_instance_key=None,
        root_spell_id=overrides_payload["root_spell_id"],
    )
    return build_overrides_execute_runtime(
        plan_rows=plan_rows,
        plan_signature=coerce_manifest_sequences(
            overrides_payload["plan_signature"]
        ),
        empty_shape_key=coerce_manifest_sequences(
            overrides_payload["empty_shape_key"]
        ),
        root_spell_id=overrides_payload["root_spell_id"],
        root_instance_key=root_instance_key,
        runtime_rows=runtime_rows,
        spell_lookup=spell_lookup,
        root_spell=root_spell,
        override_targeting=override_targeting,
        path_registry=resolver.resolve_path_registry(),
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


def _build_lazy_overrides_door(
        *,
        manifest: Dict[str, Any],
        root_spell: Any,
        route_key: str,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build a cold overrides door that hydrates the overrides runtime lazily.

    Purpose:
        Defer the overrides-lane hydration cost (runtime rows, override
        targeting deserialization, root-instance-key resolution, and the
        override execute-runtime build) from FIRST MELD to FIRST OVERRIDE
        MELD, so override-free workloads never pay for the lane at all.

    Contract:
        - Zero hydration work at build time: closure construction only.
        - The first override call hydrates exactly once (leader under the
          lock, followers wait), builds the real route-keyed overrides door
          through the same door compiler the eager path used, then swaps it
          into the spell's currently published `CreationContext`
          `_overrides_executor` slot (self-replacing slot contract), so the
          shim vanishes from later override melds.
        - Hydration resolves through a fresh `SpellbookBindingResolver` at
          first override call, mirroring `_hydrate_once`; phases 1-7 liveness
          is guaranteed by meld's structural gates on every path that can
          reach an executor.
        - When no context is published (publish=False cache loads), the shim
          keeps delegating correctly; only the swap optimization is skipped.
        - Behavior delta vs the eager path is TIMING ONLY: overrides-lane
          hydration errors surface at the first override meld instead of the
          first meld. Result values, error types, and the no-overrides lane
          are unchanged.

    Args:
        manifest:
            Validated family manifest carrying the overrides lane payload.
        root_spell:
            Live root spell whose published context receives the hot swap.
        route_key:
            Family route key for the door compiler.
        inner_no_overrides_executor:
            Already-hydrated inner no-overrides executor the overrides door
            falls back to for empty payloads.

    Returns:
        Callable[..., Any]: Cold overrides door with the same
        `(caller_creations, overrides)` call shape as the real door.
    """
    hydration_lock = threading.Lock()
    door_cell: list = [None]

    def _hydrate_overrides_door() -> Callable[..., Any]:
        real_door = door_cell[0]
        if real_door is not None:
            return real_door
        with hydration_lock:
            real_door = door_cell[0]
            if real_door is not None:
                return real_door
            resolver = SpellbookBindingResolver(spell=root_spell)
            execute_with_overrides = _hydrate_overrides_runtime(
                overrides_payload=manifest["overrides"],
                resolver=resolver,
                root_spell=root_spell,
            )
            resolver.cleanup()
            real_door = compile_creation_context_hooks_overrides_only_executor(
                resolve_route_key=route_key,
                spell=root_spell,
                spell_id=root_spell.spell_id,
                no_overrides_executor=inner_no_overrides_executor,
                execute_with_overrides=execute_with_overrides,
                meld_execution_error_type=MeldExecutionError,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
            door_cell[0] = real_door
            return real_door

    def _cold_overrides_lane_door(
            caller_creations: Any,
            overrides: Optional[dict],
    ) -> Any:
        real_door = _hydrate_overrides_door()
        # Self-healing swap mirroring the family cold doors: re-target the
        # CURRENT published context so later override melds skip this shim.
        published_context = root_spell._creation_context
        if published_context is not None:
            published_context._overrides_executor = real_door
        return real_door(caller_creations, overrides)

    return _cold_overrides_lane_door


def _specialization_enabled_for_spell(root_spell: Any) -> bool:
    """
    Read the singleton-specialization config flag once at hydration time.

    Contract:
        - Reads `generalized_singleton_specialization_enabled` from the
          spell-owning Spellbook's configuration exactly once per hydration;
          the meld hot path never re-reads it (construction-time selection,
          per the patch lane's zero-overhead-when-off rule).
        - Any unavailable surface (no spellbook, no configuration, cleaned
          configuration, unregistered property on a legacy config object)
          resolves to False - specialization is strictly opt-in and a
          missing flag must behave exactly like OFF. This is a documented
          best-effort boundary read on a hydration-only path, not a hot-path
          defensive guard.
    """
    spellbook = root_spell._spellbook
    if spellbook is None:
        return False
    try:
        configuration = spellbook.get_configuration()
        if configuration is None:
            return False
        if not configuration.has_property(
                "generalized_singleton_specialization_enabled"
        ):
            return False
        return bool(
            configuration.get_property(
                "generalized_singleton_specialization_enabled"
            )
        )
    except (RuntimeError, KeyError, AttributeError):
        return False


def _install_specializing_door(
        *,
        plain_door: Callable[..., Any],
        rows: Any,
        root_instance_key: Any,
        root_spell_id: Any,
        spell_lookup: Dict[str, Any],
        inner_no_overrides_executor: Callable[..., Any],
        route_key: str,
        fast_transient_no_overrides: bool,
        root_spell: Any,
) -> Callable[..., Any]:
    """
    Wrap the hot no-overrides door in a one-shot warm-tail specializer.

    Purpose:
        After the first successful hot execution, build the specialized
        no-overrides body (captured `unique` singletons behind per-dep door
        epoch guards), wrap it with the same route-keyed door compiler, and
        self-swap it into the published context slot - the third stage of the
        family's cold -> hot -> specialized door progression.

    Contract:
        - Zero-capture graphs never install the wrapper: this function
          returns `plain_door` unchanged when no `unique` step exists.
        - The wrapper's steady state is one closure call + one cell read:
          once a final door is resolved (specialized or declined-to-plain),
          every wrapper call delegates directly, and the context-slot swap
          removes the wrapper from later melds entirely.
        - Specialization runs post-success on the leader thread under a
          NON-BLOCKING lock acquire: concurrent melds never wait on the
          specialization build; they return their already-computed result.
        - Attempt failures and not-yet-live capture targets decline softly;
          after three declined attempts the plain hot door is pinned so the
          wrapper cost cannot persist on graphs that never warm up.
        - Wrong speculation is impossible by construction here: the emitted
          body's guards deopt to the generic inner (see emitter contract);
          this wrapper only decides WHEN a specialized door exists.

    Returns:
        Callable[..., Any]: The specializing wrapper door, or `plain_door`
        when the graph has no capturable steps.
    """
    captured_step_indexes = select_specializable_step_indexes(rows)
    if not captured_step_indexes:
        return plain_door
    if route_key != "many" and len(captured_step_indexes) == 1:
        captured_row = rows[captured_step_indexes[0]]
        if captured_row["spell_id"] == root_spell_id:
            # Root-only capture on a short-circuiting route is dead weight:
            # every non-"many" route door returns warm root hits from live
            # storage BEFORE calling the inner executor, so a specialized
            # inner that only captures the root can never execute on the
            # warm path. Decline instead of building a dead body.
            return plain_door

    state_lock = threading.Lock()
    resolved_cell: list = [None]
    attempts_cell: list = [0]

    def _try_specialize_once() -> None:
        # Leader-only: caller holds state_lock.
        specialized_inner = None
        try:
            specialized_inner = build_specialized_no_overrides_executor(
                rows=rows,
                root_instance_key=root_instance_key,
                root_spell_id=root_spell_id,
                spell_lookup=spell_lookup,
                generic_inner_executor=inner_no_overrides_executor,
            )
        except Exception:
            # Documented best-effort: a failed specialization ATTEMPT must
            # never poison the meld result path; the plain door remains
            # authoritative and the decline counter advances below.
            specialized_inner = None
        attempts_cell[0] += 1
        if specialized_inner is not None:
            resolved_cell[0] = (
                compile_creation_context_hooks_no_overrides_executor(
                    resolve_route_key=route_key,
                    fast_transient_no_overrides_enabled=(
                        fast_transient_no_overrides
                    ),
                    spell=root_spell,
                    spell_id=root_spell.spell_id,
                    no_overrides_executor=specialized_inner,
                    spell_space_scope_error_type=SpellSpaceScopeError,
                )
            )
        elif attempts_cell[0] >= 3:
            resolved_cell[0] = plain_door
        final_door = resolved_cell[0]
        if final_door is not None:
            # Self-replacing slot contract: later melds skip this wrapper.
            published_context = root_spell._creation_context
            if published_context is not None:
                published_context._no_overrides_executor = final_door

    def _specializing_no_overrides_door(caller_creations: Any) -> Any:
        resolved = resolved_cell[0]
        if resolved is not None:
            return resolved(caller_creations)
        result = plain_door(caller_creations)
        if resolved_cell[0] is None and state_lock.acquire(blocking=False):
            try:
                if resolved_cell[0] is None:
                    _try_specialize_once()
            finally:
                state_lock.release()
        return result

    return _specializing_no_overrides_door
