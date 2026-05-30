from typing import Any, Dict, List, Optional, Sequence, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellArtifactProcessorState(Cleanable):
    """
    Phase 12 processor state assembled from spell-owned runtime facts and
    compiler-owned artifact facts.

    Purpose:
        Provide one canonical Phase 12 state object that exposes the full
        information surface the new processor and later plan-building
        strategies need to examine.

    Contract:
        - This object is compiler-owned and Phase 12-scoped.
        - It does not duplicate large graph/plan structures. It keeps direct
          references to the current `Spell` and `SpellCompilerArtifact`
          surfaces plus grouped dictionaries of borrowed facts.
        - The grouped dictionaries are intentionally split by meaning so Phase
          12 strategies can choose the shallowest useful read:
          - spell/runtime facts
          - structural artifacts
          - rooted artifacts
          - planning artifacts
          - compiler handoff artifacts
          - shape profiles
          - compiler metrics
        - `assessment` is the mutable Phase 12 scratch space where the
          processor records normalized findings before the codegen-plan layer
          runs.
        - `applied_strategy_ids` records which processor strategies actually
          executed for this state.
        - Cleanup is deterministic and drops all borrowed references so stale
          state objects cannot outlive a rerun.

    Ownership:
        - Compiler-owned and stored on `SpellCompilerArtifact` during Phase 12.
        - Borrows spell-owned runtime facts from `Spell`.
        - Borrows compiler/build artifacts from `SpellCompilerArtifact`.
        - Does not own the heavyweight graph/plan artifacts it references.

    Threading:
        - No internal lock is used here.
        - This object is intended to be built and consumed within one compiler
          pass rather than shared as a concurrent mutable runtime surface.

    Lifecycle:
        - Built fresh for one Phase 12 run.
        - Cleared when the owning compiler artifact clears later-phase state.
    """

    __slots__ = Cleanable.__slots__ + [
        "spell_id",
        "spell_name",
        "spell_facts",
        "compiler_structural_artifacts",
        "compiler_rooted_artifacts",
        "compiler_planning_artifacts",
        "compiler_handoff_artifacts",
        "shape_profiles",
        "compiler_metrics",
        "assessment",
        "applied_strategy_ids",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            spell_facts: Dict[str, Any],
            compiler_structural_artifacts: Dict[str, Any],
            compiler_rooted_artifacts: Dict[str, Any],
            compiler_planning_artifacts: Dict[str, Any],
            compiler_handoff_artifacts: Dict[str, Any],
            shape_profiles: Dict[str, Any],
            compiler_metrics: Dict[str, Any],
    ) -> None:
        """
        Build one Phase 12 processor state.

        Purpose:
            Materialize one grouped, strategy-friendly view over the current
            spell/runtime/compiler truth so Phase 12 logic can consume one
            coherent state object instead of reading `Spell` and
            `SpellCompilerArtifact` ad hoc.

        Contract:
            - Stores the grouped dictionaries by reference.
            - Does not deep-copy heavyweight graph/plan objects.
            - Starts with empty mutable assessment scratch state.
            - Starts with no applied strategy ids.

        Args:
            spell_id:
                Stable spell id for this Phase 12 run.
            spell_name:
                Human-facing spell name for diagnostics and later strategy
                reporting.
            spell_facts:
                Runtime-owned spell facts borrowed from `Spell`.
            compiler_structural_artifacts:
                Phase 1-4 artifact references borrowed from
                `SpellCompilerArtifact`.
            compiler_rooted_artifacts:
                Phase 5 rooted artifact references borrowed from
                `SpellCompilerArtifact`.
            compiler_planning_artifacts:
                Phase 8-11 planning artifact references borrowed from
                `SpellCompilerArtifact`.
            compiler_handoff_artifacts:
                Phase 11 -> 13 handoff and exported IR references borrowed from
                `SpellCompilerArtifact`.
            shape_profiles:
                Grouped shape/profile summaries already collected by earlier
                compiler phases.
            compiler_metrics:
                Grouped point-metrics already stored on the artifact.

        Returns:
            None.
        """
        super().__init__()
        self.spell_id: str = spell_id
        self.spell_name: str = spell_name
        self.spell_facts: Dict[str, Any] = spell_facts
        self.compiler_structural_artifacts: Dict[str, Any] = (
            compiler_structural_artifacts
        )
        self.compiler_rooted_artifacts: Dict[str, Any] = compiler_rooted_artifacts
        self.compiler_planning_artifacts: Dict[str, Any] = (
            compiler_planning_artifacts
        )
        self.compiler_handoff_artifacts: Dict[str, Any] = (
            compiler_handoff_artifacts
        )
        self.shape_profiles: Dict[str, Any] = shape_profiles
        self.compiler_metrics: Dict[str, Any] = compiler_metrics
        self.assessment: Dict[str, Any] = {}
        self.applied_strategy_ids: List[str] = []

    def cleanup(self) -> None:
        """
        Deterministically release the Phase 12 processor state.

        Contract:
            - Idempotent cleanup.
            - Clears mutable assessment and strategy-id collections.
            - Drops all borrowed reference groups so the state cannot be reused
              after the owning artifact reruns Phase 12.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self.assessment.clear()
        self.applied_strategy_ids.clear()

        del self.spell_id
        del self.spell_name
        del self.spell_facts
        del self.compiler_structural_artifacts
        del self.compiler_rooted_artifacts
        del self.compiler_planning_artifacts
        del self.compiler_handoff_artifacts
        del self.shape_profiles
        del self.compiler_metrics
        del self.assessment
        del self.applied_strategy_ids

    def snapshot_applied_strategy_ids(self) -> Tuple[str, ...]:
        """
        Return the currently applied processor strategy ids as an immutable row.

        Purpose:
            Provide one stable read surface for later plan-building,
            diagnostics, and tests without exposing the mutable backing list.

        Contract:
            - Preserves current strategy execution order.
            - Returns a detached tuple snapshot.

        Returns:
            Tuple[str, ...]:
                Ordered processor strategy identifiers recorded so far.
        """
        return tuple(self.applied_strategy_ids)

    def section_names(self) -> Tuple[str, ...]:
        """
        Return the stable top-level section names carried by this state.

        Purpose:
            Give later strategies and diagnostics a deterministic summary of
            the major grouped fact surfaces exposed by this state.

        Contract:
            - Ordering is stable.
            - The returned tuple is suitable for diagnostics, assertions, and
              low-cost metadata export.

        Returns:
            Tuple[str, ...]:
                Immutable section-name row for diagnostics and test assertions.
        """
        return (
            "spell_facts",
            "compiler_structural_artifacts",
            "compiler_rooted_artifacts",
            "compiler_planning_artifacts",
            "compiler_handoff_artifacts",
            "shape_profiles",
            "compiler_metrics",
            "assessment",
        )
