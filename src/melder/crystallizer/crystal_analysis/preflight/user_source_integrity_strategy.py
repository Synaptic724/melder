
import hashlib
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class UserSourceIntegrityStrategy(PersistenceAnalysisStrategy):
    """
    Verify retained user-module sources and detect on-disk drift (S2).

    Purpose:
        Opt-in physical custody retains user source TEXT inside the
        record; a corrupted/altered payload must never rebuild - the
        same law as the synthetic integrity pass. This pass owns the
        record's SELF-CONSISTENCY half only; disk-vs-seal comparison
        moved to SourceDriftStrategy (source_drift_preflight
        2026-07-12), which covers EVERY fingerprinted module regardless
        of retention.

    Contract:
        - TAMPER (retained text vs its own recorded sha): "blocker" -
          executing unverified source is worse than not booting.
        - Scope: modules carried in user_module_sources (retention-on
          payloads); retention-off worlds have no rows here.

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        The second of two integrity rows in the ten-row DEFAULT preflight
        set: this pass owns retained USER text, its sibling
        `SyntheticSourceIntegrityStrategy` owns record-authored SYNTHETIC
        text. Its scope is gated by opt-in physical custody
        (`CrystallizerConfiguration.retain_user_sources`, default False),
        so a retention-off world produces zero rows here and is
        byte-identical to the pre-S2 record.

    System Context:
        The narrowing recorded in Purpose is the important fact, because
        this row used to do two jobs and now does one. Disk-vs-seal
        comparison moved wholesale to `SourceDriftStrategy` in the
        source_drift_preflight lane (2026-07-12), for a concrete reason:
        drift detection tied to retention meant retention-OFF worlds
        restored blind. Splitting it made drift RETENTION-AGNOSTIC and
        left this pass with the half only it can perform - checking the
        record against ITSELF.
        That split also explains the severity gap between the two. Drift
        is a warning because the live file wins at import; tamper is a
        blocker because retained text is used precisely when no live file
        exists, so altered material would rebuild unchallenged.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Verify retained user-module sources and detect on-disk drift (S2). "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "user_source_integrity".
        """
        return "user_source_integrity"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Check every retained user source for tamper (self-consistency).

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Blocker rows on tamper.
        """
        findings: List[Dict[str, object]] = []
        for spell_id, payload in dict(
                payload_bundle.get("spell_crystal", {})
        ).items():
            for module_name, source_payload in dict(
                    payload.get("user_module_sources", {})
            ).items():
                recorded_sha = str(source_payload.get("source_sha256", ""))
                source_text = str(source_payload.get("source_text", ""))
                computed_sha = hashlib.sha256(
                    source_text.encode("utf-8")
                ).hexdigest()
                if recorded_sha and recorded_sha != computed_sha:
                    findings.append(self._row(
                        "blocker", spell_id,
                        "retained user module {0!r} does not match its "
                        "recorded SHA256 (recorded {1}..., computed "
                        "{2}...); the payload was corrupted or altered - "
                        "do not rebuild from it".format(
                            module_name, recorded_sha[:12],
                            computed_sha[:12],
                        ),
                    ))
        return findings

    def _row(
            self,
            severity: str,
            spell_id: str,
            detail: str,
    ) -> Dict[str, object]:
        """
        Build one finding row in the shared preflight shape.

        Args:
            severity:
                "blocker" | "warning" | "info" per the class contract.
            spell_id:
                Custody anchor.
            detail:
                Human-facing explanation with remediation context.

        Returns:
            Dict[str, object]: The finding row.
        """
        return {
            "strategy": self.name,
            "severity": severity,
            "kind": "spell_crystal",
            "key": spell_id,
            "detail": detail,
        }
