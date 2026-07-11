

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class MutationResearchCrystal(Cleanable):
    """
    Pure-data digital twin of the MutationResearch root's configured surface.

    Purpose:
        Carry the persistable truth of the MR root for one profile. Phase A
        recorded configuration/activation state only; Phase B (the P5 seam,
        landed with the ResearchSet build) additionally rides the research
        COMPOSITION on this same twin: research sets with their lanes,
        full-object version records, residence partition, bounded
        recent-transition windows, and retained network-snapshot addresses,
        exactly as emitted by
        `MutationResearch.describe_research_composition()`.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - MR is codegen-lane-only at runtime, so this twin appears only in
          profiles emitted from dynamic-lane worlds.
        - `composition_payload` is optional so Phase-A emitters (the
          configuration activation seam) stay valid; None records as an
          empty composition.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle:
        Owned by exactly one PersistenceProfile; `cleanup()` deletes owned
        fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_activated",
        "_configuration_payload",
        "_composition_payload",
    ]

    def __init__(
            self,
            activated: bool,
            configuration_payload: Optional[Dict[str, object]] = None,
            composition_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the MR twin from emitted root state.

        Args:
            activated:
                Whether the MR root was activated at emission time.
            configuration_payload:
                Value-typed mapping of the installed MR configuration surface.
                None is treated as an empty payload.
            composition_payload:
                Value-typed research composition (set name ->
                `ResearchSet.describe_composition()` payload). None is
                treated as an empty composition (Phase-A emitters).

        Returns:
            None.
        """
        super().__init__()
        self._activated: bool = activated
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )
        self._composition_payload: Dict[str, object] = (
            dict(composition_payload) if composition_payload else {}
        )

    def cleanup(self) -> None:
        """
        Release owned fields and mark the twin cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._activated
        del self._configuration_payload
        del self._composition_payload

    @property
    def activated(self) -> bool:
        """
        Return whether the MR root was activated at emission.

        Returns:
            bool:
                Recorded activation flag.
        """
        self.check_cleaned()
        return self._activated

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded MR configuration surface.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    @property
    def composition_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded research composition.

        Returns:
            Dict[str, object]:
                Detached mapping of set name -> composition payload
                (organization + bounded journal window + snapshot addresses).
        """
        self.check_cleaned()
        return dict(self._composition_payload)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "mutation_research",
            "activated": self._activated,
            "configuration_payload": dict(self._configuration_payload),
            "composition_payload": dict(self._composition_payload),
        }
