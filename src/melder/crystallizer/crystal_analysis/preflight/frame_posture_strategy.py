
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

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        One of the ten DEFAULT rows of the preflight set that
        `PersistenceAnalyzer` iterates polymorphically, emitting the
        shared finding shape {strategy, severity, kind, key, detail}.
        This row is SCOPE-BLIND by design, and it is the one row
        `LoadAdmission` adjudicates afterwards: on conduit-scoped and
        frame-scoped loads its warnings are reclassified as
        "expected_for_scope" in the additive "admission" view, because a
        partial-scope load is EXPECTED to omit frame twins. The raw
        finding is never rewritten - adjudication is additive, so the
        strategy stays honest and the reader still sees what it found.

    System Context:
        Frame posture is load-bearing because of boot order:
        Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch ->
        Nexus -> AethericFrame -> Spellbook -> Conduit|Ward. Frames come
        BEFORE books because the frame owns the dynamic gate that
        conjure's `check_system_state` reads. So the engine postures a
        book's frame from its recorded twin before the book builds; with
        no twin it guesses dynamic from the book's config hints. The
        world boots either way - which is why this warns rather than
        blocks - but the user is running on a fallback posture rather
        than recorded truth, and only this row tells them so.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Detect books whose frame posture is missing from the bundle. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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
