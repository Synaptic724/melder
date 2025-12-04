from __future__ import annotations

from enum import IntEnum
from typing import Any, Dict, List

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagTargetingEngine, SocketRef
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


class _Specificity(IntEnum):
    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


class SpellOverrider(Cleanable):
    """
    Runtime helper that turns a raw ``spell_override`` dict into a socket-aware
    ``OverrideMap`` for a specific root blueprint.

    The targeting semantics are shared with mutation overrides:
      * PATH:       ``a>b>c``
      * UNIQUE:     ``*param``  (exactly one match required)
      * BROADCAST:  ``**param`` (one or more matches required)
    """

    __slots__ = Cleanable.__slots__ + ["_blueprint", "_engine"]

    def __init__(self, blueprint: RootResolutionBlueprint) -> None:
        super().__init__()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._blueprint: RootResolutionBlueprint = blueprint
        self._engine: DagTargetingEngine = DagTargetingEngine(blueprint.dag_index)

    def cleanup(self) -> None:
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
        if spec.kind is TargetSpecKind.PATH:
            return _Specificity.PATH
        if spec.kind is TargetSpecKind.UNIQUE:
            return _Specificity.UNIQUE
        if spec.kind is TargetSpecKind.BROADCAST:
            return _Specificity.BROADCAST
        raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind}")
