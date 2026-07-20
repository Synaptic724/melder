
import hashlib
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class SyntheticSourceIntegrityStrategy(PersistenceAnalysisStrategy):
    """
    Verify recorded synthetic module sources against their SHA256.

    Purpose:
        Synthetic sources ARE the record (loader chain M3): a corrupted
        or hand-altered cached payload would execute WRONG CODE at
        restore. This pass recomputes each recorded source's SHA256 and
        compares it to the recorded fingerprint before anything runs.

    Contract:
        - Severity "blocker" on mismatch: executing unverified source is
          worse than not booting.
        - Sources whose recorded sha is absent/empty are "info" (older
          test-authored payloads may carry sentinel fingerprints; the
          SyntheticModule constructor hashes canonically at runtime, so
          absence here is a documentation gap, not proven corruption).

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        One of two integrity rows in the ten-row DEFAULT preflight set,
        split by WHOSE code is under verification. This pass owns
        SYNTHETIC sources - code the record itself authored and carries
        (loader chain M3). `UserSourceIntegrityStrategy` owns retained
        USER text, and `SourceDriftStrategy` owns all disk-vs-seal
        comparison. Together with `HydrationStrategy` (can it rebuild?)
        these answer: is the material we would rebuild from trustworthy?

    System Context:
        This row carries the strongest severity posture in the package,
        and the reason is a genuine asymmetry: for synthetic modules the
        record is not a DESCRIPTION of code that lives elsewhere - it IS
        the code. There is no live file to fall back to and no other copy
        to compare against, so a corrupted payload does not fail loudly;
        it executes wrong code silently inside the user's process. That
        is why a mismatch blocks at the `RestoreEngine` fold->preflight
        seam before any replay: not booting is a recoverable outcome,
        while executing unverified source is not.
        Contrast `SourceDriftStrategy`, which only warns - there the live
        file wins at import, so divergence is a notice rather than a
        danger.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Verify recorded synthetic module sources against their SHA256. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "synthetic_source_integrity".
        """
        return "synthetic_source_integrity"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Recompute and compare every recorded synthetic source SHA256.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Blocker rows on mismatch; info rows
            for unverifiable fingerprints.
        """
        findings: List[Dict[str, object]] = []
        for spell_id, payload in dict(
                payload_bundle.get("spell_crystal", {})
        ).items():
            for module_name, source_payload in dict(
                    payload.get("synthetic_module_sources", {})
            ).items():
                recorded_sha = str(source_payload.get("source_sha256", ""))
                source_text = str(source_payload.get("source_text", ""))
                computed_sha = hashlib.sha256(
                    source_text.encode("utf-8")
                ).hexdigest()
                if not recorded_sha:
                    findings.append({
                        "strategy": self.name,
                        "severity": "info",
                        "kind": "spell_crystal",
                        "key": spell_id,
                        "detail": (
                            "synthetic module {0!r} carries no source "
                            "fingerprint; integrity cannot be "
                            "verified".format(module_name)
                        ),
                    })
                    continue
                if recorded_sha != computed_sha:
                    findings.append({
                        "strategy": self.name,
                        "severity": "blocker",
                        "kind": "spell_crystal",
                        "key": spell_id,
                        "detail": (
                            "synthetic module {0!r} source does not "
                            "match its recorded SHA256 (recorded "
                            "{1}..., computed {2}...); the payload was "
                            "corrupted or altered - do not execute "
                            "it".format(
                                module_name, recorded_sha[:12],
                                computed_sha[:12],
                            )
                        ),
                    })
        return findings
