from typing import Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.phase12.spell_artifact_processor_state import (
    SpellArtifactProcessorState,
)
from melder.aether.spellbook.spell_compiler.phase12.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)


class SpellArtifactProcessor:
    """
    Phase 12 processor orchestrator over one spell's artifact-backed state.

    Purpose:
        Run the configured Phase 12 processor strategies against the assembled
        state and leave one assessed state object for the codegen-plan layer.

    Contract:
        - Owns no runtime/compiler artifacts itself; it only borrows the
          already assembled `SpellArtifactProcessorState`.
        - Strategy execution is ordered and deterministic.
        - The scaffold slice allows an empty strategy sequence and still
          produces a valid assessed state.
        - Assessment defaults are recorded even when no concrete strategies
          exist yet, so later plan building has a stable baseline surface.

    Ownership:
        - Borrows one processor state object.
        - Borrows a strategy sequence.
        - Does not own the heavyweight artifacts referenced by the state.
    """

    __slots__ = [
        "_state",
        "_strategies",
    ]

    def __init__(
            self,
            *,
            state: SpellArtifactProcessorState,
            strategies: Optional[Sequence[SpellArtifactProcessorStrategy]] = None,
    ) -> None:
        """
        Build one processor over one Phase 12 state object.

        Purpose:
            Bind one assembled state object and one optional ordered strategy
            sequence into the Phase 12 processor orchestrator.

        Contract:
            - `None` strategies become an empty deterministic sequence.
            - Strategy order is preserved exactly as supplied.

        Args:
            state:
                Assembled Phase 12 processor state.
            strategies:
                Ordered processor strategies to run. `None` means no concrete
                strategies are active yet.

        Returns:
            None.
        """
        self._state: SpellArtifactProcessorState = state
        if strategies is None:
            self._strategies: Tuple[SpellArtifactProcessorStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def process(self) -> SpellArtifactProcessorState:
        """
        Run the current processor strategy sequence and return the state.

        Purpose:
            Apply baseline assessment metadata and then run the ordered
            strategy sequence over the current processor state.

        Contract:
            - Clears prior mutable assessment/provenance before rerunning.
            - Always emits baseline metadata even when there are zero
              strategies.
            - Appends applied strategy ids in execution order.
            - Returns the same state object after mutation.

        Returns:
            SpellArtifactProcessorState:
                The same state object after baseline assessment and strategy
                processing.
        """
        state = self._state
        assessment = state.assessment
        state.applied_strategy_ids.clear()
        assessment.clear()
        assessment["processor_ready"] = True
        assessment["section_names"] = state.section_names()
        assessment["strategy_count"] = len(self._strategies)

        for strategy in self._strategies:
            strategy.process(state)
            state.applied_strategy_ids.append(strategy.strategy_id)

        assessment["applied_strategy_ids"] = state.snapshot_applied_strategy_ids()
        return state
