
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class FramePostureStrategy(PersistenceAnalysisStrategy):
    """
    Detect books whose frame posture is missing from the bundle.

    Purpose:
        Frames own the dynamic gate: the restore engine postures a
        book's frame from its recorded twin BEFORE the book builds.
        A book whose frame twin is absent falls back to a dynamic
        posture guessed from the book's config hints - it boots, but
        the user should know their posture is a fallback, not truth.

    Contract:
        - Severity "warning" once per (frame_name, spellbook) pair
          whose frame twin is absent.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "frame_posture".
        """
        return "frame_posture"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Flag every book building on an unrecorded frame posture.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: One warning row per uncovered book.
        """
        frames = dict(payload_bundle.get("frame", {}))
        findings: List[Dict[str, object]] = []
        for spellbook_id, payload in dict(
                payload_bundle.get("spellbook", {})
        ).items():
            frame_name = str(payload.get("frame_name", "default"))
            if frame_name in frames:
                continue
            findings.append({
                "strategy": self.name,
                "severity": "warning",
                "kind": "spellbook",
                "key": spellbook_id,
                "detail": (
                    "frame {0!r} has no posture twin in this bundle; "
                    "the restore postures it dynamic from the book's "
                    "config hints (fallback, not recorded truth)".format(
                        frame_name
                    )
                ),
            })
        return findings
