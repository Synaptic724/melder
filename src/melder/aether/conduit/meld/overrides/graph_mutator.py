from __future__ import annotations

from typing import Any, Dict

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagTargetingEngine
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec
from melder.utilities.general_base.cleanable import Cleanable


class GraphMutator(Cleanable):
    """
    Runtime helper for applying mutation_override to a root blueprint.

    This implementation validates targets against MutationContract sockets and
    currently returns the underlying blueprint unchanged. It is a scaffold for
    future graph rewiring logic.
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

    def apply(self, mutation_override: Dict[str, Any]) -> RootResolutionBlueprint:
        """
        Validate mutation targets and return a (currently unmodified) blueprint.

        Raises:
            RuntimeError if targets are invalid.
        """
        self.check_cleaned()
        if not mutation_override:
            return self._blueprint

        def _filter_mutation(socket_ref):
            return socket_ref.socket_kind is SocketKind.MUTATION_CONTRACT

        for raw_key in mutation_override.keys():
            spec = TargetSpec.parse(raw_key)
            # Validate that targets exist and are mutation sockets
            self._engine.resolve(spec, _filter_mutation)

        # TODO: apply structural rewiring once mutation contracts are defined.
        return self._blueprint
