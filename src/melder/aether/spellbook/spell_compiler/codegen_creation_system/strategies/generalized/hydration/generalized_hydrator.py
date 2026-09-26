"""
Single executor hydrator for the generalized codegen-creation family.

`hydrate_creation_executors(manifest, resolver)` is the one assembly program
for this family. The live phase-11 step publishes lazy doors over it; the
cache codec publishes lazy doors over it. Both produce identical hot doors at
first meld, so cache loads can never drift from live builds.

Hydration shape:
    1. Resolve live identity (spells, path registry) through the resolver.
    2. Hydrate the manifest's no-overrides rows into site-plan steps.
    3. Build `SitePlanOverrideRuntime` over them (2026-09-26, S2b-2): its
       normal plan (the empty key set) is the inner no-overrides executor, and
       it compiles one plan per override key set at first use.
    4. Wrap both lanes in the shared route-keyed CreationContext doors (the
       override door is compiled at the first override meld).
    5. Optionally (configuration flag) install the singleton warm-tail
       specializer; its body comes from the family's old step emitter and it
       deopts to the normal plan.
"""

import threading
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
    compile_creation_context_instance_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    build_specialized_no_overrides_executor,
    resolve_root_instance_key_from_rows,
    select_specializable_step_indexes,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    SpellbookBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest.generalized_manifest import (
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
        - `no_overrides_executor`, `no_overrides_instance_executor`
          (the instance-only no-hooks twin), and `overrides_executor` are the
          final route-keyed CreationContext doors.
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
        "no_overrides_instance_executor",
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
            no_overrides_instance_executor: Callable[..., Any],
            overrides_executor: Callable[..., Any],
            no_overrides_code_object: Any,
            overrides_code_object: Any,
    ) -> None:
        """
        Build one hydration result container.

        Contract:
            Pure store of the hydration outputs; every field is retained
            verbatim. Executors are plain callables; code objects are shared via
            the process-wide caches and referenced, not owned.

        Args:
            route_key:
                Runtime route key the doors were compiled for.
            fast_transient_no_overrides:
                True when the no-overrides fast-transient lane is available.
            inner_no_overrides_executor:
                Underlying no-overrides executor (exposed for diagnostics only).
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
        self.fast_transient_no_overrides = fast_transient_no_overrides
        self.inner_no_overrides_executor = inner_no_overrides_executor
        self.no_overrides_executor = no_overrides_executor
        self.no_overrides_instance_executor = no_overrides_instance_executor
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
        del self.no_overrides_instance_executor
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
                published_context._no_overrides_instance_executor = (
                    hydrated.no_overrides_instance_executor
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
            published_context._no_overrides_instance_executor = (
                hydrated.no_overrides_instance_executor
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

    def _cold_no_overrides_instance_door(caller_creations: Any) -> Any:
        # Instance-only twin of the cold no-overrides door: same self-healing
        # hydrate+swap, bare-instance return contract.
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
    # One runtime per root serves both lanes (S2b-2, 2026-09-26): its normal
    # plan is the inner no-overrides executor; override key sets compile on it.
    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell_lookup=no_overrides_spell_lookup,
        root_spell=root_spell,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
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
    # Instance-only twin: same inner executor wrapped by the instance-variant
    # route template ((meld) -> instance); consumed by the no-hooks meld
    # lanes so warm melds never allocate the (instance, created) tuple.
    no_overrides_instance_door = (
        compile_creation_context_instance_no_overrides_executor(
            resolve_route_key=route_key,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides,
            spell=root_spell,
            spell_id=root_spell.spell_id,
            no_overrides_executor=inner_no_overrides_executor,
            spell_space_scope_error_type=SpellSpaceScopeError,
        )
    )
    overrides_door = _build_lazy_overrides_door(
        root_spell=root_spell,
        route_key=route_key,
        inner_no_overrides_executor=inner_no_overrides_executor,
        execute_with_overrides=site_plan_runtime.execute_with_overrides,
    )

    # The specializing wrapper rides the INSTANCE lane: the no-hooks meld
    # lanes only execute `_no_overrides_instance_executor`, so a wrapper on
    # the hooks slot would never run (regression caught by the component
    # specialization suite after the dual-door cut). On success it publishes
    # BOTH specialized doors; the hooks slot stays plain until then.
    final_no_overrides_instance_door = no_overrides_instance_door
    if _specialization_enabled_for_spell(root_spell):
        final_no_overrides_instance_door = _install_specializing_door(
            plain_instance_door=no_overrides_instance_door,
            plain_hooks_door=no_overrides_door,
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
        no_overrides_executor=no_overrides_door,
        no_overrides_instance_executor=final_no_overrides_instance_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=None,
    )


def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell_lookup: Dict[str, Any],
        root_spell: Any,
) -> SitePlanOverrideRuntime:
    """
    Build the root's site-plan runtime: the normal plan now, override plans per key set later.

    Contract:
        - Reads the manifest's no-overrides step rows through the family's
          step-row hydration (`_hydrate_steps_from_rows`), which also resolves
          contract payload references to live values where rows carry them, so
          normal and override plans see the same steps (design v2 S3a, S2b-2).
          The manifest's overrides payload is not read.
        - The runtime builds its site graph and normal plan at construction
          (first meld); requires phases 1-7 live, which meld's structural gates
          guarantee on every path that reaches hydration.

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell_lookup:
            Live spell per step spell id.
        root_spell:
            Live root spell.

    Raises:
        RuntimeError:
            When rows, the root instance key or the site graph cannot be
            resolved.

    Returns:
        SitePlanOverrideRuntime: The runtime (kept alive by the executors it
        hands out).
    """
    steps_rows = no_overrides_payload["steps_rows"]
    rows = _hydrate_steps_from_rows(
        steps_rows=steps_rows,
        spell_lookup=spell_lookup,
    )
    root_instance_key = resolve_root_instance_key_from_rows(
        rows=steps_rows,
        explicit_root_instance_key=no_overrides_payload["root_instance_key"],
        root_spell_id=no_overrides_payload["root_spell_id"],
    )
    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_generalized_row(row) for row in rows),
        root_spell=root_spell,
        root_instance_key=root_instance_key,
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


def _build_lazy_overrides_door(
        *,
        root_spell: Any,
        route_key: str,
        inner_no_overrides_executor: Callable[..., Any],
        execute_with_overrides: Callable[..., Any],
) -> Callable[..., Any]:
    """
    Build a cold overrides door that compiles the real overrides door lazily.

    Purpose:
        Defer the overrides door compile from FIRST MELD to FIRST OVERRIDE
        MELD. The site-plan runtime itself is built at hydration (its normal
        plan is the inner executor since S2b-2), so only the door is deferred.

    Contract:
        - Zero work at build time: closure construction only.
        - The first override call compiles exactly once (leader under the
          lock, followers wait) the real route-keyed overrides door through
          the same door compiler the eager path used, then swaps it into the
          spell's currently published `CreationContext` `_overrides_executor`
          slot (self-replacing slot contract), so the shim vanishes from later
          override melds.
        - When no context is published (publish=False cache loads), the shim
          keeps delegating correctly; only the swap optimization is skipped.

    Args:
        root_spell:
            Live root spell whose published context receives the hot swap.
        route_key:
            Family route key for the door compiler.
        inner_no_overrides_executor:
            The normal plan the overrides door falls back to for empty payloads.
        execute_with_overrides:
            The runtime's `(meld, overrides) -> instance` dispatcher.

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
        plain_instance_door: Callable[..., Any],
        plain_hooks_door: Callable[..., Any],
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
    Wrap the hot no-overrides INSTANCE door in a one-shot warm-tail
    specializer.

    Purpose:
        After the first successful hot execution, build the specialized
        no-overrides body (captured `unique` singletons behind per-dep door
        epoch guards), wrap it with BOTH route-keyed door compilers, and
        self-swap the pair into the published context slots - the third stage
        of the family's cold -> hot -> specialized door progression.

    Contract:
        - The wrapper rides the INSTANCE lane because the no-hooks meld lanes
          execute `_no_overrides_instance_executor`; a wrapper on the hooks
          slot would never run. Signature/return contract is the instance
          door's: `(meld) -> instance`.
        - Zero-capture graphs never install the wrapper: this function
          returns `plain_instance_door` unchanged when no `unique` step
          exists.
        - The wrapper's steady state is self-erasing: once a final door is
          resolved (specialized or declined-to-plain), every wrapper call
          re-publishes the final door(s) into the CURRENT published context
          before delegating, so any context still routing through the
          wrapper - including contexts REBUILT after resolution, which
          re-swap the container's wrapped instance door - sheds it after
          one call.
        - On successful specialization BOTH published slots swap together:
          `_no_overrides_instance_executor` gets the specialized instance
          door and `_no_overrides_executor` gets the specialized hooks door
          (CreationContext door contract). On decline only the instance slot
          re-pins the plain instance door; the hooks slot already holds the
          plain hooks door.
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
        Callable[..., Any]: The specializing wrapper door, or
        `plain_instance_door` when the graph has no capturable steps.
    """
    captured_step_indexes = select_specializable_step_indexes(rows)
    if not captured_step_indexes:
        return plain_instance_door
    if route_key != "many" and len(captured_step_indexes) == 1:
        captured_row = rows[captured_step_indexes[0]]
        if captured_row["spell_id"] == root_spell_id:
            # Root-only capture on a short-circuiting route is dead weight:
            # every non-"many" route door returns warm root hits from live
            # storage BEFORE calling the inner executor, so a specialized
            # inner that only captures the root can never execute on the
            # warm path. Decline instead of building a dead body.
            return plain_instance_door

    state_lock = threading.Lock()
    resolved_cell: list = [None]
    resolved_hooks_cell: list = [None]
    attempts_cell: list = [0]
    deopt_miss_cell: list = [0]

    def _deopt_notify(caller_creations: Any) -> Any:
        """
        Count one specialized-guard miss, re-pin plain doors at 3 strikes.

        Contract:
            - Deopt target bound into the specialized body (`_deopt_notify`):
              same `(meld) -> instance` contract as the generic inner, which
              it always delegates to (deopt is slower, never wrong).
            - After 3 misses the captured world is treated as permanently
              invalidated: BOTH published slots re-pin the plain doors and
              the wrapper cells resolve to plain, so the specialized body
              (and its per-call guard cost) leaves every lane instead of
              paying guard-miss + fallback forever (~13% over plain,
              measured by the efficacy probe's deopt lane).
            - Racy counting under nogil is acceptable: the re-pin publishes
              idempotent values, so late/duplicate strikes are benign.
        """
        deopt_miss_cell[0] += 1
        if deopt_miss_cell[0] >= 3:
            resolved_cell[0] = plain_instance_door
            resolved_hooks_cell[0] = plain_hooks_door
            published_context = root_spell._creation_context
            if published_context is not None:
                published_context._no_overrides_instance_executor = (
                    plain_instance_door
                )
                published_context._no_overrides_executor = plain_hooks_door
        return inner_no_overrides_executor(caller_creations)

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
                deopt_notify=_deopt_notify,
            )
        except Exception:
            # Documented best-effort: a failed specialization ATTEMPT must
            # never poison the meld result path; the plain door remains
            # authoritative and the decline counter advances below.
            specialized_inner = None
        attempts_cell[0] += 1
        specialized_hooks_door = None
        if specialized_inner is not None:
            resolved_cell[0] = (
                compile_creation_context_instance_no_overrides_executor(
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
            specialized_hooks_door = (
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
            # Kept beyond this attempt so the wrapper's resolved branch can
            # re-publish the pair into REBUILT contexts (see the self-heal
            # note in `_specializing_no_overrides_door`).
            resolved_hooks_cell[0] = specialized_hooks_door
        elif attempts_cell[0] >= 3:
            resolved_cell[0] = plain_instance_door
        final_door = resolved_cell[0]
        if final_door is not None:
            # Self-replacing slot contract: later melds skip the wrapper.
            # On success both no-overrides slots swap together
            # (CreationContext door contract); on decline only the instance
            # slot re-pins - the hooks slot already holds the plain hooks
            # door.
            published_context = root_spell._creation_context
            if published_context is not None:
                published_context._no_overrides_instance_executor = final_door
                if specialized_hooks_door is not None:
                    published_context._no_overrides_executor = (
                        specialized_hooks_door
                    )

    def _specializing_no_overrides_door(caller_creations: Any) -> Any:
        resolved = resolved_cell[0]
        if resolved is not None:
            # Rebuilt-context self-heal: a context rebuilt AFTER resolution
            # re-swaps the hydrated container doors, which re-installs this
            # wrapper in its instance slot. Without the re-publish below that
            # context would pay the wrapper indirection on every warm meld
            # forever; with it, the first call through the wrapper swaps the
            # final doors back in and later melds skip the wrapper again.
            # On decline-pin resolves the hooks cell is None and the hooks
            # slot is left untouched (it already holds the plain hooks door).
            published_context = root_spell._creation_context
            if published_context is not None:
                published_context._no_overrides_instance_executor = resolved
                resolved_hooks_door = resolved_hooks_cell[0]
                if resolved_hooks_door is not None:
                    published_context._no_overrides_executor = (
                        resolved_hooks_door
                    )
            return resolved(caller_creations)
        result = plain_instance_door(caller_creations)
        if resolved_cell[0] is None and state_lock.acquire(blocking=False):
            try:
                if resolved_cell[0] is None:
                    _try_specialize_once()
            finally:
                state_lock.release()
        return result

    return _specializing_no_overrides_door
