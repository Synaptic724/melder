
import hashlib
from pathlib import Path
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
        record. Two truths need guarding before anything executes:
        the retained text itself (a corrupted/altered payload must never
        rebuild - same law as the synthetic integrity pass), and the
        relationship to the LIVE tree (when the file still exists, the
        live file wins; a silent difference from the sealed world is the
        user's business to know about, not a refusal).

    Contract:
        - TAMPER (retained text vs its own recorded sha): "blocker" -
          executing unverified source is worse than not booting.
        - DRIFT (live file vs the bind-time fingerprint in
          physical_module_fingerprints): "warning"
          ("user_source_drifted_since_seal") - the live file is imported
          as-is; the row is teach-grade notice, never an override.
        - Unreadable live files and absent fingerprints are "info"
          (unverifiable, not proven corruption).
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
        Check every retained user source for tamper and disk drift.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Blocker rows on tamper; warning rows
            on live-file drift; info rows for unverifiable cases.
        """
        findings: List[Dict[str, object]] = []
        for spell_id, payload in dict(
                payload_bundle.get("spell_crystal", {})
        ).items():
            fingerprints = dict(
                payload.get("physical_module_fingerprints", {})
            )
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
                    continue
                recorded_path = source_payload.get("module_path")
                if recorded_path is None:
                    continue
                live_path = Path(str(recorded_path))
                if not live_path.exists():
                    continue
                sealed_sha = str(fingerprints.get(module_name, ""))
                if not sealed_sha:
                    findings.append(self._row(
                        "info", spell_id,
                        "user module {0!r} exists on disk but carries no "
                        "bind-time fingerprint; drift cannot be "
                        "verified".format(module_name),
                    ))
                    continue
                try:
                    # read_text mirrors the custody read that produced
                    # the sealed fingerprint (universal newlines
                    # normalize CRLF -> LF); hashing raw bytes would
                    # false-drift every CRLF-authored file.
                    disk_sha = hashlib.sha256(
                        live_path.read_text(
                            encoding="utf-8"
                        ).encode("utf-8")
                    ).hexdigest()
                except Exception as error:
                    findings.append(self._row(
                        "info", spell_id,
                        "user module {0!r} exists on disk but could not "
                        "be read for drift verification: {1}".format(
                            module_name, error
                        ),
                    ))
                    continue
                if disk_sha != sealed_sha:
                    findings.append(self._row(
                        "warning", spell_id,
                        "user_source_drifted_since_seal: module {0!r} on "
                        "disk differs from the sealed world (the LIVE "
                        "file wins and will be imported as-is; retained "
                        "text is only a fallback for absent "
                        "files)".format(module_name),
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
