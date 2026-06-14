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
    hydrate_no_overrides_executor,
    resolve_root_instance_key_from_rows,
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

    def _cold_no_overrides_door(
            caller_creations: Any,
            root_creations: Any = None,
    ) -> Any:
        # Self-healing swap: every cold-path call re-targets the CURRENT
        # published context. A rebuilt context starts with cold doors copied
        # from the creation artifact; its first call lands here and gets the
        # hot doors installed, so cold indirection never persists per meld.
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.no_overrides_executor(caller_creations, root_creations)

    def _cold_overrides_door(
            caller_creations: Any,
            overrides: Optional[dict],
            root_creations: Any = None,
    ) -> Any:
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.overrides_executor(caller_creations, overrides, root_creations)

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

    execute_with_overrides = _hydrate_overrides_runtime(
        overrides_payload=manifest["overrides"],
        resolver=resolver,
        root_spell=root_spell,
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

    return GeneralizedHydratedExecutors(
        route_key=route_key,
        fast_transient_no_overrides=fast_transient_no_overrides,
        inner_no_overrides_executor=inner_no_overrides_executor,
        no_overrides_executor=no_overrides_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=overrides_door.__code__,
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
