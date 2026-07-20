

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.dag.dag_index import SocketRef

from melder.aether.spellbook.spell_compiler.dag.dag_index import DagTargetingEngine
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


class _Specificity(IntEnum):
    """
    Precedence tiers for spell-override target specs.

    Contract:
        Higher values win when multiple override specs target the same socket.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded. Private precedence vocabulary for
        `SpellOverrider`; not part of any public surface.

    Subsystem Context:
        The tie-breaker behind `SpellOverrider`'s three targeting forms. It is
        an `IntEnum` rather than a plain `Enum` specifically so precedence is a
        numeric comparison rather than a lookup table.

    System Context:
        Precedence has to exist because the targeting forms deliberately
        OVERLAP: a `**param` broadcast and an exact `a>b>c` path can both name
        the same socket, and that overlap is a legitimate way to express
        "set all of these, except this one". Ordering the tiers so the more
        specific spec wins makes the general-plus-exception idiom work without
        the caller having to order their own dict, which would be fragile and
        silently order-dependent.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Precedence tiers for spell-override target specs. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__ = _mrg.sentinel
    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


class SpellOverrider(Cleanable):
    """
    Runtime helper that turns a raw spell_override dict into a socket-aware
    OverrideMap for a specific root blueprint.

    The targeting semantics are shared with mutation overrides:
      * PATH: a>b>c
      * UNIQUE: *param (exactly one match required)
      * BROADCAST: **param (one or more matches required)

    Contract:
        - Translates a raw override dict into a socket-aware `OverrideMap`
          bound to one specific root blueprint.
        - Match-count rules are ENFORCED, not advisory: `*param` requires
          exactly one match and `**param` requires at least one.
        - Precedence between competing specs is resolved by `_Specificity`.

    Owned State:
        `_blueprint` and `_engine`.

    Threading:
        Bound to one resolution call; not shared across threads.

    Lifecycle / Cleanup:
        Cleanable and single-use against the blueprint it was built for.

    Registration:
        MELDER KERNEL - guarded. Constructed inside the meld override lane;
        users supply the override PAYLOAD, never this object.

    Subsystem Context:
        The override half of resolution. `CreationContext` exposes a separate
        `overrides_executor` precisely because overrides cannot use the warm
        no-overrides fast lane, and this class is what makes that second lane
        necessary: the payload must be mapped onto real sockets before any
        executor can consume it.

    System Context:
        The three targeting forms exist because an override has to name a
        socket that may sit anywhere in a dependency graph the caller did not
        build. A PATH names it exactly; `*param` says "there is exactly one of
        these, find it"; `**param` says "hit every one". Enforcing the match
        counts is what keeps overrides honest - a `*param` that silently
        matched three sockets, or zero, would apply the caller's intent to the
        wrong object or to nothing at all, and both fail invisibly at runtime
        rather than at resolution. Failing loudly at map time is the whole
        point of resolving specs up front instead of during construction.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Runtime helper that turns a raw spell_override dict into a "
        "socket-aware OverrideMap for a specific root blueprint. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_blueprint", "_engine"]

    def __init__(self, blueprint: RootResolutionBlueprint) -> None:
        """
        Initialize the spell-override resolver for one root blueprint.

        Args:
            blueprint: Root blueprint whose DAG/index provides the override
                targeting surface.
        Contract:
            - Requires a prebuilt root blueprint.
            - Builds one targeting engine over the blueprint's DAG index.
            - Does not mutate the source blueprint during construction.

        Returns:
            None.
        """
        super().__init__()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._blueprint: RootResolutionBlueprint = blueprint
        self._blueprint.ensure_dag_index_built()
        self._engine: DagTargetingEngine = DagTargetingEngine(blueprint.dag_index)

    def cleanup(self) -> None:
        """
        Idempotently clear the overrider and its targeting engine.

        Contract:
            - Safe to call more than once.
            - Best-effort cleans the owned targeting engine.
            - Drops only overrider-owned references; it does not clean the
              source blueprint.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._engine is not None:
            try:
                self._engine.cleanup()
            except Exception:
                pass
        del self._engine
        del self._blueprint

    def apply(self, spell_override: Dict[str, Any]) -> Dict[SocketRef, Any]:
        """
        Compute the final socket->value mapping with specificity precedence.

        Contract:
            - Returns an empty mapping when no overrides are supplied.
            - Resolves raw target specs into concrete socket references using
              the shared targeting semantics.
            - Higher-specificity overrides win over lower-specificity ones.
            - Equal-specificity conflicting overrides raise instead of being
              resolved arbitrarily.

        Raises:
            RuntimeError on conflicting overrides or invalid targets.
        """
        self.check_cleaned()
        if spell_override is None:
            return {}

        per_socket: Dict[SocketRef, tuple[_Specificity, Any]] = {}

        for key, value in spell_override.items():
            spec = TargetSpec.parse(key)
            matches = self._engine.resolve(spec, lambda _: True)
            level = self._specificity_for_spec(spec)

            for socket_ref in matches:
                existing = per_socket.get(socket_ref)
                if existing is None:
                    per_socket[socket_ref] = (level, value)
                    continue

                existing_level, existing_value = existing
                if level > existing_level:
                    per_socket[socket_ref] = (level, value)
                elif level == existing_level and existing_value != value:
                    raise RuntimeError(
                        f"Conflicting overrides for socket {socket_ref}: multiple rules "
                        f"with the same specificity."
                    )
                # lower specificity is ignored

        return {socket: val for socket, (spec_level, val) in per_socket.items()}

    @staticmethod
    def _specificity_for_spec(spec: TargetSpec) -> _Specificity:
        """
        Map one parsed target spec to its override-specificity tier.

        Contract:
            PATH > UNIQUE > BROADCAST.
        """
        if spec.kind is TargetSpecKind.PATH:
            return _Specificity.PATH
        if spec.kind is TargetSpecKind.UNIQUE:
            return _Specificity.UNIQUE
        if spec.kind is TargetSpecKind.BROADCAST:
            return _Specificity.BROADCAST
        raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind}")
