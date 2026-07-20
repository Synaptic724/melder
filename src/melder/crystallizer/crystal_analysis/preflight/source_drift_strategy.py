
from pathlib import Path
from typing import ClassVar, Dict, List, Set, Tuple

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.physical_source_cache import (
    PhysicalSourceCache,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class SourceDriftStrategy(PersistenceAnalysisStrategy):
    """
    Compare every bind-time fingerprint against the live disk at load.

    Purpose:
        A restore should TELL you your working tree diverged from the
        sealed world BEFORE it builds anything. Every custody crystal
        ships physical_module_fingerprints (bind-time sha256 of each
        physical module's text) regardless of retention - this pass owns
        ALL disk-vs-seal comparison (the integrity strategy owns only
        retained-text TAMPER, its record-self-consistency half).

    Contract:
        - WARNING on drift ("user_source_drifted_since_seal": the live
          file wins at import - this is notice, never a refusal) and on
          absent backing files (honest wording: the import may still
          resolve via sys.path; hydration owns the importability
          blocker for roots).
        - INFO on unreadable files (unverifiable, not proven divergence).
        - Silent on unchanged; per-(module, path) pairs deduplicate
          across crystals (shared modules report once).
        - Reads use read_text/utf-8 - the SAME read that sealed the
          fingerprints, so CRLF files never false-drift.

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls. The `PhysicalSourceCache` it consults is a process-wide
        class-level cache with its own internal discipline, not state
        owned by this strategy.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        The TENTH and newest row of the DEFAULT preflight set
        (source_drift_preflight lane, 2026-07-12), carved out of
        `UserSourceIntegrityStrategy` so drift detection stopped being
        tied to opt-in retention. It is the only preflight row that
        touches the live filesystem, and the only one that deduplicates
        across crystals: shared modules carried by many spells report
        once per (module, path) pair rather than once per carrier.

    System Context:
        This row answers a question no other part of a restore can:
        "has your working tree moved since you sealed this world?" It is
        deliberately the softest strong signal in the package - drift is
        NOTICE, never refusal - because the live file legitimately wins
        at import, so a drifted module is a normal state of affairs for
        anyone still developing. Blocking would make the record hostile
        to the workflow it is meant to support; staying silent would let
        a user restore a world they believe is sealed and get today's
        code instead.
        The read discipline is load-bearing rather than incidental: it
        re-hashes through the SAME read path that sealed the
        fingerprints, so line-ending differences can never manufacture
        phantom drift. That matters in this repo specifically, where
        mixed CRLF and LF endings are present in real source files.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Compare every bind-time fingerprint against the live disk at load. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "source_drift".
        """
        return "source_drift"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Re-hash every fingerprinted module and report divergence.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Warning rows for drifted/absent
            modules; info rows for unreadable ones.
        """
        findings: List[Dict[str, object]] = []
        seen: Set[Tuple[str, str]] = set()
        for spell_id, payload in dict(
                payload_bundle.get("spell_crystal", {})
        ).items():
            paths = dict(payload.get("module_to_path", {}))
            for module_name, sealed_sha in dict(
                    payload.get("physical_module_fingerprints", {})
            ).items():
                recorded_path = paths.get(str(module_name))
                if recorded_path is None:
                    continue
                dedupe_key = (str(module_name), str(recorded_path))
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                live_path = Path(str(recorded_path))
                if not live_path.exists():
                    findings.append(self._row(
                        "warning", spell_id,
                        "sealed module {0!r} has no backing file at its "
                        "recorded path (the import may still resolve via "
                        "sys.path; retained text rebuilds it when "
                        "custody carries one)".format(module_name),
                    ))
                    continue
                # IO-economy stat guard (2026-07-19): an unchanged stat
                # serves the cached sha without a read; a miss reads
                # THROUGH the cache so the next load pays a stat only.
                disk_sha = PhysicalSourceCache.fingerprint_if_unchanged(
                    live_path
                )
                if disk_sha is None:
                    read_text, read_sha, read_error = (
                        PhysicalSourceCache.read_text_and_fingerprint(
                            str(module_name),
                            live_path,
                        )
                    )
                    if read_error is not None or read_sha is None:
                        findings.append(self._row(
                            "info", spell_id,
                            "sealed module {0!r} could not be read for drift "
                            "verification: {1}".format(
                                module_name,
                                read_error
                                if read_error is not None
                                else "no readable source",
                            ),
                        ))
                        continue
                    disk_sha = read_sha
                if disk_sha != str(sealed_sha):
                    findings.append(self._row(
                        "warning", spell_id,
                        "user_source_drifted_since_seal: module {0!r} on "
                        "disk differs from the sealed world (the LIVE "
                        "file wins at import; reseal to modernize the "
                        "record)".format(module_name),
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
                "warning" | "info" per the class contract.
            spell_id:
                Custody anchor (first carrier of the deduplicated pair).
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
