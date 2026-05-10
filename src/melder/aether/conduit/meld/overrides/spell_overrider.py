from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from enum import IntEnum
from typing import Any, Dict, List

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagTargetingEngine, SocketRef
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


class _Specificity(IntEnum):
    """
    Precedence tiers for spell-override target specs.

    Contract:
        Higher values win when multiple override specs target the same socket.
    """
    __melder_internal__ = _mrg.sentinel
    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


class SpellOverrider(Cleanable):
    """
    Runtime helper that turns a raw spell_override dict into a socket-aware
    OverrideMap for a specific root blueprint.

    The targeting semantics are shared with mutation overrides:
      * PATH:       a>b>c
      * UNIQUE:     *param  (exactly one match required)
      * BROADCAST:  ``**param`` (one or more matches required)
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_blueprint", "_engine"]

    def __init__(self, blueprint: RootResolutionBlueprint) -> None:
        """
        Initialize the spell-override resolver for one root blueprint.

        Args:
            blueprint: Root blueprint whose DAG/index provide the override
                targeting surface.
        Contract:
            - Requires a prebuilt root blueprint.
            - Builds one targeting engine over the blueprint's DAG index.
            - Does not mutate the source blueprint during construction.
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
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._engine is not None:
            try:
                self._engine.cleanup()
            except Exception:
                pass
        self._engine = None
        self._blueprint = None

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
