"""
Single executor hydrator for the solo codegen-creation family.

`hydrate_solo_creation_executors(manifest, resolver)` is the one assembly
program for this family. The live phase-11 step publishes lazy doors over it;
the cache codec publishes lazy doors over it. Both produce identical hot
doors at first meld.

Solo hydration is two compiler calls plus the shared door wrap: resolve the
root spell, compile the root-only no-overrides and overrides executors from
manifest facts, wrap both in the route-keyed CreationContext doors.
"""

import threading
from typing import Any, Callable, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler import (
    compile_solo_no_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler import (
    compile_solo_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.manifest.solo_manifest import (
    validate_solo_manifest,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable


class SoloHydratedExecutors(Cleanable):
    """
    Hydration result container for one solo spell.

    Lifecycle / Cleanup:
        - Owned by the lazy-door closure that hydrated it; lives for the
          executor lifetime so cold doors can delegate before the hot swap.
        - `cleanup()` is idempotent and deletes every field. Executors are
          referenced callables, not owned resources.
    """

    __slots__ = Cleanable.__slots__ + [
        "route_key",
        "fast_transient_no_overrides",
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
            no_overrides_executor: Callable[..., Any],
            overrides_executor: Callable[..., Any],
            no_overrides_code_object: Any,
            overrides_code_object: Any,
    ) -> None:
        """
        Build one solo hydration result container.
        """
        super().__init__()
        self.route_key = route_key
        self.fast_transient_no_overrides = fast_transient_no_overrides
        self.no_overrides_executor = no_overrides_executor
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
        del self.fast_transient_no_overrides
        del self.no_overrides_executor
        del self.overrides_executor
        del self.no_overrides_code_object
        del self.overrides_code_object


def build_solo_lazy_creation_executors(
        *,
        manifest: Dict[str, Any],
        spell: Any,
) -> Tuple[Callable[..., Any], Callable[..., Any]]:
    """
    Build cold solo runtime doors that hydrate on first call.

    Contract:
        - Zero hydration work at build time: validation plus closure
          construction only.
        - First call hydrates once (leader under the lock, followers wait),
          swaps the hot doors into the spell's currently published
          `CreationContext`, then delegates. The swap re-runs on every
          cold-path call so rebuilt contexts self-heal.
    """
    validate_solo_manifest(manifest)
    hydration_lock = threading.Lock()
    hydrated_cell: list = [None]

    def _hydrate_once() -> SoloHydratedExecutors:
        hydrated = hydrated_cell[0]
        if hydrated is not None:
            return hydrated
        with hydration_lock:
            hydrated = hydrated_cell[0]
            if hydrated is not None:
                return hydrated
            hydrated = hydrate_solo_creation_executors(
                manifest=manifest,
                spell=spell,
            )
            hydrated_cell[0] = hydrated
            return hydrated

    def _swap_hot_doors(hydrated: SoloHydratedExecutors) -> None:
        published_context = spell._creation_context
        if published_context is not None:
            published_context._no_overrides_executor = (
                hydrated.no_overrides_executor
            )
            published_context._overrides_executor = (
                hydrated.overrides_executor
            )

    def _cold_no_overrides_door(caller_creations: Any) -> Any:
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


def hydrate_solo_creation_executors(
        *,
        manifest: Dict[str, Any],
        spell: Any,
) -> SoloHydratedExecutors:
    """
    Hydrate both final solo runtime doors from one manifest plus the spell.

    Contract:
        - Runs the exact compiler calls the live solo steps run, fed by
          manifest facts instead of family state, then wraps both lanes in
          the shared route-keyed doors.
    """
    validate_solo_manifest(manifest)
    route_key = manifest["route_key"]
    solo_emit_key = manifest["solo_emit_key"]
    fast_transient_no_overrides = bool(
        manifest["fast_transient_no_overrides_enabled"]
    )

    inner_no_overrides_executor, _no_overrides_code_object = (
        compile_solo_no_overrides_codegen_creation_executor(
            spell=spell,
            solo_emit_key=solo_emit_key,
            fast_transient_no_overrides_enabled=fast_transient_no_overrides,
            return_compiled_code_object=True,
        )
    )
    inner_overrides_executor, _overrides_code_object = (
        compile_solo_overrides_codegen_creation_executor(
            spell=spell,
            solo_emit_key=solo_emit_key,
            return_compiled_code_object=True,
        )
    )

    no_overrides_door = compile_creation_context_hooks_no_overrides_executor(
        resolve_route_key=route_key,
        fast_transient_no_overrides_enabled=fast_transient_no_overrides,
        spell=spell,
        spell_id=spell.spell_id,
        owner_creations=spell._owner_creations,
        no_overrides_executor=inner_no_overrides_executor,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )
    overrides_door = compile_creation_context_hooks_overrides_only_executor(
        resolve_route_key=route_key,
        spell=spell,
        spell_id=spell.spell_id,
        owner_creations=spell._owner_creations,
        no_overrides_executor=inner_no_overrides_executor,
        execute_with_overrides=inner_overrides_executor,
        meld_execution_error_type=MeldExecutionError,
        spell_space_scope_error_type=SpellSpaceScopeError,
    )

    return SoloHydratedExecutors(
        route_key=route_key,
        fast_transient_no_overrides=fast_transient_no_overrides,
        no_overrides_executor=no_overrides_door,
        overrides_executor=overrides_door,
        no_overrides_code_object=no_overrides_door.__code__,
        overrides_code_object=overrides_door.__code__,
    )
