"""
Single executor hydrator for the many_only codegen-creation family.

`hydrate_many_only_creation_executors(manifest, spell)` is the one assembly
program for this family. The live phase-11 step publishes lazy doors over it;
the cache codec publishes lazy doors over it. Both produce identical hot
doors at first meld.

The no-overrides lane hydrates through the many_only compiler's public
Codegen IR entrypoint (the manifest stores that IR verbatim). The override
runtime is rebuilt through the bridged many_only finalize builder fed cached
rows plus the live phase-5 path registry, mirroring the generalized family's
hydration discipline.
"""

import threading
from types import SimpleNamespace
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
    compile_creation_context_instance_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    compile_no_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_overrides_codegen_creation_compiler import (
    compile_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.manifest.many_only_manifest import (
    coerce_manifest_sequences,
    validate_many_only_manifest,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step import (
    ManyOnlyFinalizeCreationContextStep,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable

# Null model stand-in for the bridged override-runtime builder: it only reads
# `graph_shape` when no explicit path registry is supplied.
_NULL_MODEL = SimpleNamespace(graph_shape=None)


class ManyOnlyHydratedExecutors(Cleanable):
    """
    Hydration result container for one many_only spell.

    Lifecycle / Cleanup:
        - Owned by the lazy-door closure that hydrated it; lives for the
          executor lifetime so cold doors can delegate before the hot swap.
        - `cleanup()` is idempotent and deletes every field. Executors are
          referenced callables, not owned resources.
    """

    __slots__ = Cleanable.__slots__ + [
        "route_key",
        "no_overrides_executor",
        "no_overrides_instance_executor",
        "overrides_executor",
        "no_overrides_code_object",
        "overrides_code_object",
    ]

    def __init__(
            self,
            *,
            route_key: str,
            no_overrides_executor: Callable[..., Any],
            no_overrides_instance_executor: Callable[..., Any],
            overrides_executor: Callable[..., Any],
            no_overrides_code_object: Any,
            overrides_code_object: Any,
    ) -> None:
        """
        Build one many_only hydration result container.
        """
        super().__init__()
        self.route_key = route_key
        self.no_overrides_executor = no_overrides_executor
        self.no_overrides_instance_executor = no_overrides_instance_executor
        self.overrides_executor = overrides_executor
        self.no_overrides_code_object = no_overrides_code_object
        self.overrides_code_object = overrides_code_object

    def cleanup(self) -> None:
        """
        Deterministically release the hydration container surface.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.route_key
        del self.no_overrides_executor
        del self.no_overrides_instance_executor
        del self.overrides_executor
        del self.no_overrides_code_object
        del self.overrides_code_object


def build_many_only_lazy_creation_executors(
        *,
        manifest: Dict[str, Any],
        spell: Any,
) -> Tuple[Callable[..., Any], Callable[..., Any]]:
    """
    Build cold many_only runtime doors that hydrate on first call.

    Contract:
        - Zero hydration work at build time: validation plus closure
          construction only.
        - First call hydrates once (leader under the lock, followers wait),
          swaps the hot doors into the spell's currently published
          `CreationContext`, then delegates. The swap re-runs on every
          cold-path call so rebuilt contexts self-heal.
    """
    validate_many_only_manifest(manifest)
    hydration_lock = threading.Lock()
    hydrated_cell: list = [None]

    def _hydrate_once() -> ManyOnlyHydratedExecutors:
        hydrated = hydrated_cell[0]
        if hydrated is not None:
            return hydrated
        with hydration_lock:
            hydrated = hydrated_cell[0]
            if hydrated is not None:
                return hydrated
            hydrated = hydrate_many_only_creation_executors(
                manifest=manifest,
                spell=spell,
            )
            hydrated_cell[0] = hydrated
            return hydrated

    def _swap_hot_doors(hydrated: ManyOnlyHydratedExecutors) -> None:
        published_context = spell._creation_context
        if published_context is not None:
            published_context._no_overrides_executor = (
                hydrated.no_overrides_executor
            )
            published_context._no_overrides_instance_executor = (
                hydrated.no_overrides_instance_executor
            )
            published_context._overrides_executor = (
                hydrated.overrides_executor
            )

    def _cold_no_overrides_door(caller_creations: Any) -> Any:
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.no_overrides_executor(caller_creations)

    def _cold_no_overrides_instance_door(caller_creations: Any) -> Any:
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.no_overrides_instance_executor(caller_creations)

    def _cold_overrides_door(
            caller_creations: Any,
            overrides: Optional[dict],
    ) -> Any:
        hydrated = _hydrate_once()
        _swap_hot_doors(hydrated)
        return hydrated.overrides_executor(caller_creations, overrides)

    return (
        _cold_no_overrides_door,
        _cold_no_overrides_instance_door,
        _cold_overrides_door,
    )


def hydrate_many_only_creation_executors(
        *,
        manifest: Dict[str, Any],
        spell: Any,
) -> ManyOnlyHydratedExecutors:
    """
    Hydrate both final many_only runtime doors from one manifest plus the
    root spell.

    Contract:
        - Requires phases 1-7 live (phase-5 path registry) and ownership
          wiring (`spell._owner_creations`), which first-meld gates guarantee.
        - The no-overrides door mirrors the legacy many_only finalize step:
          the door-level fast-transient flag stays False because transient
          unrolling is the inner executor's concern in this family.
    """
    validate_many_only_manifest(manifest)
    route_key = manifest["route_key"]

    no_overrides_payload = manifest["no_overrides"]
    spell_lookup = _resolve_spell_lookup(
        spell=spell,
        step_spell_ids=no_overrides_payload["step_spell_ids"],
    )
    inner_no_overrides_executor = compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": no_overrides_payload["steps_rows"],
            "root_spell_id": no_overrides_payload["root_spell_id"],
            "transient_schema": no_overrides_payload["transient_schema"],
        },
        spell_lookup=spell_lookup,
    )
    if inner_no_overrides_executor is None:
        raise RuntimeError(
            "many_only manifest hydration produced no no-overrides executor."
        )

    execute_with_overrides = _hydrate_overrides_runtime(
        overrides_payload=manifest["overrides"],
        spell=spell,
        inner_no_overrides_executor=inner_no_overrides_executor,
    )

    no_overrides_door = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=False,
        spell=spell,
        spell_id=spell.spell_id,
        no_overrides_executor=inner_no_overrides_executor,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )
    # Instance-only twin for the no-hooks meld lanes ((meld) -> instance).
    no_overrides_instance_door = (
        compile_creation_context_instance_no_overrides_executor(
            resolve_route_key=route_key,
            fast_transient_no_overrides_enabled=False,
            spell=spell,
            spell_id=spell.spell_id,
            no_overrides_executor=inner_no_overrides_executor,
            spell_space_scope_error_type=SpellSpaceScopeError,
        )
    )
    overrides_door = compile_creation_context_hooks_overrides_only_executor(
        resolve_route_key=route_key,
        spell=spell,
        spell_id=spell.spell_id,
        no_overrides_executor=inner_no_overrides_executor,
        execute_with_overrides=execute_with_overrides,
        meld_execution_error_type=MeldExecutionError,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )

    return ManyOnlyHydratedExecutors(
        route_key=route_key,
        no_overrides_executor=no_overrides_door,
        no_overrides_instance_executor=no_overrides_instance_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=overrides_door.__code__,
    )


def _hydrate_overrides_runtime(
        *,
        overrides_payload: Dict[str, Any],
        spell: Any,
        inner_no_overrides_executor: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Rebuild the many_only override runtime from manifest rows.

    Contract:
        - Reuses the bridged many_only finalize builder fed cached rows plus
          the live phase-5 path registry, so per-shape override executors
          still compile lazily at meld time.
    """
    spell_lookup = _resolve_spell_lookup(
        spell=spell,
        step_spell_ids=overrides_payload["step_spell_ids"],
    )
    override_targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
        root_spell_id=overrides_payload["root_spell_id"],
        targets_by_spec=_deserialize_targets_by_spec(
            overrides_payload["targets_by_spec"],
        ),
        specificity_by_spec=dict(overrides_payload["specificity_by_spec"]),
    )
    path_registry = _resolve_live_path_registry(spell)
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

    finalize_step = ManyOnlyFinalizeCreationContextStep()
    return finalize_step._build_overrides_runtime(
        spell_codegen_model=_NULL_MODEL,
        overrides_plan=None,
        root_spell=spell,
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
        spell: Any,
        step_spell_ids: Any,
) -> Dict[str, Any]:
    """
    Resolve one stable spell-id -> Spell map from the live Spellbook pool.
    """
    spellbook = spell._spellbook
    if spellbook is None:
        raise RuntimeError("Spell has no owning Spellbook surface.")
    spell_lookup: Dict[str, Any] = {}
    for spell_id in step_spell_ids:
        if spell_id in spell_lookup:
            continue
        resolved_spell = spellbook._spell_id_pool.get(spell_id)
        if resolved_spell is None:
            raise RuntimeError(
                "many_only manifest references unknown spell_id "
                f"'{spell_id}'."
            )
        spell_lookup[spell_id] = resolved_spell
    return spell_lookup


def _resolve_live_path_registry(spell: Any) -> Any:
    """
    Return the live phase-5 path registry for override specialization.
    """
    artifact = spell._compiler_artifact
    if artifact is None:
        raise RuntimeError(
            "Spell has no compiler artifact for manifest hydration."
        )
    root_blueprint = artifact._root_blueprint_phase5
    if root_blueprint is None:
        raise RuntimeError(
            "Manifest hydration requires a live phase-5 root blueprint "
            f"(spell_id={spell.spell_id})."
        )
    return root_blueprint.path_registry


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
