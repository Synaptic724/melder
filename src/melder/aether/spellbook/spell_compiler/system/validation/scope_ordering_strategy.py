from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Set

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )
            


from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class ScopeOrderingStrategy(SpellSystemValidationStrategy):
    """
    Guard lifecycle-scope ordering across dependency edges.

    This strategy checks whether broader-lived nodes are depending on narrower-
    lived nodes in ways that would let per-conduit, per-spellspace, or per-call
    instances leak upward into shared contexts. It is a system-level lifetime
    sanity check layered on top of the existence metadata captured in the
    `SpellSystemIndex`.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, Spell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate dependency edges against scope ordering rules.

        Purpose:
            Detect broad-to-narrow dependencies that can corrupt lifecycle
            boundaries and caching semantics.
        Contract:
            - Only compares nodes with known existence metadata.
            - Emits one diagnostic per offending edge.
            - Cancellation is honored between nodes.
        Args:
            index: Spell system index being validated.
            blueprints: Root blueprints keyed by root spell id.
            phase4_results: Phase-4 validation artifacts keyed by spell id.
            broken_spell_ids: Set of broken spell ids.
            spell_system_states: SpellSystemStates registry for topology and lineage data.
            spell_lookup: Mapping of visible spell version ids to spell objects.
            diagnostics: Collection that receives diagnostics.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If cancel_event is set while iterating.
        """
        scope_rank = {
            Existence.unique: 0,
            Existence.unique_per_conduit_cluster: 1,
            Existence.unique_per_conduit_lineage: 2,
            Existence.unique_per_conduit: 3,
            Existence.unique_per_spell_space: 4,
            Existence.many: 5,
        }

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if node.existence is None:
                continue
            if node.existence is Existence.many:
                continue
            node_rank = scope_rank.get(node.existence)
            if node_rank is None:
                continue

            for dep_id in node.dependencies:
                dep_node = index.get_node(dep_id)
                if dep_node is None or dep_node.existence is None:
                    continue
                if dep_node.existence is Existence.many:
                    continue
                dep_rank = scope_rank.get(dep_node.existence)
                if dep_rank is None:
                    continue
                if node_rank >= dep_rank:
                    continue

                diagnostics.append(
                    SystemDiagnostic(
                        code="scope_ordering_violation",
                        message=(
                            f"Spell '{node.spell_id}' ({node.existence.name}) depends on "
                            f"'{dep_id}' ({dep_node.existence.name}), which is a narrower scope."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=node.spell_id,
                        root_id=None,
                        details={
                            "spell_id": node.spell_id,
                            "spell_existence": node.existence.name,
                            "dependency_id": dep_id,
                            "dependency_existence": dep_node.existence.name,
                        },
                    )
                )



