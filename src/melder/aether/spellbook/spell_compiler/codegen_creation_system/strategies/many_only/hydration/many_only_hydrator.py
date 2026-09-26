"""
Single executor hydrator for the many_only codegen-creation family.

`hydrate_many_only_creation_executors(manifest, spell)` is the one assembly
program for this family. The live phase-11 step publishes lazy doors over it;
the cache codec publishes lazy doors over it. Both produce identical hot
doors at first meld.

Both lanes run on `SitePlanOverrideRuntime` over the manifest's no-overrides
rows (the Codegen IR the manifest stores verbatim): its normal plan (the empty
key set) is the inner no-overrides executor since S2b-2 (2026-09-26), and it
compiles one plan per override key set at first use, as in the generalized
family.
"""

import threading
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
    compile_creation_context_instance_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows,
    _resolve_root_instance_key,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.manifest.many_only_manifest import (
    validate_many_only_manifest,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable


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

        Contract:
            Pure store of the many-only hydration outputs; every field is
            retained verbatim. Executors are plain callables; code objects are
            shared via the process-wide caches and referenced, not owned.

        Args:
            route_key:
                Runtime route key the doors were compiled for.
            no_overrides_executor:
                Final route-keyed no-overrides CreationContext door.
            no_overrides_instance_executor:
                Instance-only no-hooks twin of the no-overrides door.
            overrides_executor:
                Final route-keyed overrides CreationContext door.
            no_overrides_code_object:
                Compiled code object backing the no-overrides door.
            overrides_code_object:
                Compiled code object backing the overrides door.

        Returns:
            None.
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
    # One runtime serves both lanes (S2b-2, 2026-09-26): its normal plan is the
    # inner no-overrides executor; override key sets compile on it.
    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell=spell,
        spell_lookup=spell_lookup,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
    execute_with_overrides = site_plan_runtime.execute_with_overrides

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


def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell: Any,
        spell_lookup: Dict[str, Any],
) -> SitePlanOverrideRuntime:
    """
    Build the many_only site-plan runtime: the normal plan now, override plans per key set later.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's own
          row hydration, so normal and override plans see the same steps
          (design v2 S3a, S2b-2). The manifest's overrides payload is not read.
        - The runtime builds its site graph and normal plan at construction
          (first meld); it lives as long as the executors it hands out.

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell:
            Live root spell.
        spell_lookup:
            Live spell per step spell id.

    Raises:
        RuntimeError:
            When no step carries the root instance key, or the site graph
            cannot be built.

    Returns:
        SitePlanOverrideRuntime: The runtime.
    """
    rows = _hydrate_steps_from_rows(
        steps_rows=no_overrides_payload["steps_rows"],
        spell_lookup=spell_lookup,
    )
    root_instance_key = _resolve_root_instance_key(
        steps=rows,
        root_spell_id=no_overrides_payload["root_spell_id"],
    )
    if root_instance_key is None:
        raise RuntimeError(
            "many_only override runtime could not resolve the root instance key."
        )
    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(row) for row in rows),
        root_spell=spell,
        root_instance_key=root_instance_key,
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
