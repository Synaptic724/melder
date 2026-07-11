
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
    """

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
