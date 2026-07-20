
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
from melder.crystallizer.crystal_analysis.preflight.mutation_research_composition_strategy import (
    MutationResearchCompositionStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.source_drift_strategy import (
    SourceDriftStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.user_source_integrity_strategy import (
    UserSourceIntegrityStrategy,
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
        - The ten-strategy default set runs, in order: link integrity,
          contract peers, hydration, configuration loss, cluster membership,
          frame posture, synthetic source integrity, retained user-source
          integrity, mutation-research composition, and live source drift.
          Callers may replace the complete set with an explicit sequence of
          `PersistenceAnalysisStrategy` objects.
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
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Strategy-driven bootload pre-flight for persistence payload bundles. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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
                Optional explicit strategy sequence. None installs the ten
                default passes documented on the class. Supplying even one
                strategy replaces, rather than extends, that default set.

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
                UserSourceIntegrityStrategy(),
                MutationResearchCompositionStrategy(),
                SourceDriftStrategy(),
            ]
        )

    def cleanup(self) -> None:
        """
        Drop the strategy list and mark the analyzer cleaned.

        Contract:
            - Idempotent and terminal; later analysis is rejected.
            - Deletes only the owned strategy list. Default strategies are
              stateless and hold no teardown-sensitive collaborators.

        Threading:
            Must not race with `analyze()`; callers finish all reads before
            releasing the strategy list.

        Lifecycle / Cleanup:
            A facade or restore engine owns the analyzer for one preflight
            span and cleans it in `finally`.

        Returns:
            None.
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

        Contract:
            Strategies run in configured order over the same read-only bundle.
            Their rows retain that order. The aggregate verdict is `blockers`
            when any blocker exists, otherwise `warnings` when any warning
            exists, otherwise `clean`; informational rows do not escalate it.

        Args:
            payload_bundle:
                `{kind: {key: payload}}` for a formation slice, checkpoint
                window, or folded restore bundle. The analyzer does not mutate
                it or consult live runtime state directly.

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
