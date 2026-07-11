
from typing import ClassVar, Dict, List, Optional, Sequence

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.cluster_membership_strategy import (
    ClusterMembershipStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.configuration_loss_strategy import (
    ConfigurationLossStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.contract_peer_strategy import (
    ContractPeerStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.frame_posture_strategy import (
    FramePostureStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.hydration_strategy import (
    HydrationStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.link_integrity_strategy import (
    LinkIntegrityStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.synthetic_source_integrity_strategy import (
    SyntheticSourceIntegrityStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable


class PersistenceAnalyzer(Cleanable):
    """
    Strategy-driven bootload pre-flight for persistence payload bundles.

    Purpose:
        Owner charter: BEFORE a user trusts a formation or checkpoint,
        run analysis strategies over its payloads and report exactly
        what their bootloader will hit - missing links, absent contract
        peers, unhydratable custody, code participation expectations.

    Contract:
        - Default strategy set: link integrity, contract peers,
          hydration, configuration loss, cluster membership, frame
          posture, synthetic source integrity; callers may supply their
          own sequence (each a PersistenceAnalysisStrategy).
        - This same default set runs AT LOAD TIME inside the
          RestoreEngine (owner ruling): every restore report carries a
          "preflight" section from the folded bundle.
        - analyze() is read-only over the bundle and touches no live
          runtime objects; it can run before ANY activation.
        - Verdict semantics: "blockers" when any blocker row exists,
          else "warnings" when any warning row exists, else "clean"
          (info rows never change the verdict).

    Threading:
        Strategies are stateless; the analyzer holds only its strategy
        list and may be shared for reads.

    Lifecycle:
        cleanup() drops the strategy list (strategies are stateless and
        need no teardown of their own); idempotent.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_strategies",
    ]

    def __init__(
            self,
            strategies: Optional[
                Sequence[PersistenceAnalysisStrategy]
            ] = None,
    ) -> None:
        """
        Initialize the analyzer with its strategy passes.

        Args:
            strategies:
                Optional explicit strategy sequence; None installs the
                default set (link integrity, contract peers, hydration,
                configuration loss, cluster membership, frame posture,
                synthetic source integrity).

        Returns:
            None.
        """
        super().__init__()
        self._strategies: List[PersistenceAnalysisStrategy] = (
            list(strategies)
            if strategies is not None
            else [
                LinkIntegrityStrategy(),
                ContractPeerStrategy(),
                HydrationStrategy(),
                ConfigurationLossStrategy(),
                ClusterMembershipStrategy(),
                FramePostureStrategy(),
                SyntheticSourceIntegrityStrategy(),
            ]
        )

    def cleanup(self) -> None:
        """
        Drop the strategy list and mark the analyzer cleaned.

        Contract:
            - Idempotent; del posture (strategies are stateless).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._strategies

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> Dict[str, object]:
        """
        Run every strategy over one bundle and aggregate the report.

        Args:
            payload_bundle:
                {kind: {key: payload}} - a formation's payload slice or
                a checkpoint's captured payloads.

        Returns:
            Dict[str, object]:
                {"findings": [rows...],
                 "counts": {"blocker": n, "warning": n, "info": n},
                 "verdict": "clean"|"warnings"|"blockers"}.

        Raises:
            RuntimeError: If the analyzer has been cleaned.
        """
        self.check_cleaned()
        findings: List[Dict[str, object]] = []
        for strategy in self._strategies:
            findings.extend(strategy.analyze(payload_bundle))
        counts = {"blocker": 0, "warning": 0, "info": 0}
        for row in findings:
            severity = str(row.get("severity"))
            if severity in counts:
                counts[severity] += 1
        if counts["blocker"] > 0:
            verdict = "blockers"
        elif counts["warning"] > 0:
            verdict = "warnings"
        else:
            verdict = "clean"
        return {
            "findings": findings,
            "counts": counts,
            "verdict": verdict,
        }
