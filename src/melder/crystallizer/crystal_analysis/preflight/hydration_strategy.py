
import importlib.util
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class HydrationStrategy(PersistenceAnalysisStrategy):
    """
    Detect custody that cannot rebuild its bind target.

    Purpose:
        The bootloader's hardest failures are hydration failures. This
        pass pre-flights every custody payload: replay-required target
        kinds, synthetic roots sealed BEFORE the M3 source capture,
        unresolvable importable roots, and custody whose owning book is
        absent from the bundle.

    Contract:
        - "blocker": the anchor will NOT rebuild (missing book, pre-M3
          synthetic root, unfindable module).
        - "warning": the restore completes but this custody shortfalls
          (replay_required target kinds).
        - Module probing uses importlib.util.find_spec (spec lookup
          only; nothing imports during analysis).

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        The heaviest of the ten DEFAULT preflight rows and the only one
        that emits blockers for the CUSTODY family. It reads the
        `SpellCrystal` payload - `rebindability`, `root_module_kind`,
        `synthetic_module_sources`, `user_module_sources` - which the
        crystal derives at bind from the shared `crystal_analysis`
        service. It divides labour with the two integrity rows cleanly:
        this pass asks "can the anchor rebuild AT ALL", while
        `SyntheticSourceIntegrityStrategy` and
        `UserSourceIntegrityStrategy` ask "is the material we would
        rebuild FROM trustworthy".

    System Context:
        Hydration failures are the bootloader's hardest failures, which
        is why this row is allowed to refuse. At the `RestoreEngine`
        fold->preflight seam a "blocker" verdict raises a teach-grade
        error naming the offending rows BEFORE any replay begins - and
        that ordering matters because the restore is ALL-OR-NOTHING: a
        failure mid-replay tears down every unit built so far in reverse
        order. Refusing early is therefore strictly cheaper than
        discovering an unimportable root halfway through.
        The find_spec probe never imports, honouring the rule that a
        probe must not cause the effect it is checking for.
        The S2 downgrade encodes opt-in physical custody: an absent
        module whose source text was RETAINED drops from blocker to
        info, because the engine's rebuild lane can reconstruct it
        through the synthetic-module path with an honest shortfall.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "hydration".
        """
        return "hydration"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Pre-flight every custody payload's rebuild path.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Blocker/warning rows per custody.
        """
        books = dict(payload_bundle.get("spellbook", {}))
        findings: List[Dict[str, object]] = []
        for spell_id, payload in dict(
                payload_bundle.get("spell_crystal", {})
        ).items():
            book_id = str(payload.get("spellbook_id"))
            if book_id not in books:
                findings.append(self._finding(
                    "blocker", spell_id,
                    "owning spellbook {0!r} is not in this bundle; the "
                    "custody cannot bind".format(book_id),
                ))
                continue
            if str(payload.get("rebindability")) != "hydratable":
                findings.append(self._finding(
                    "warning", spell_id,
                    "target kind {0!r} is replay_required; the restore "
                    "will shortfall this custody".format(
                        payload.get("root_target_kind")
                    ),
                ))
                continue
            module_name = str(payload.get("root_module_name"))
            if str(payload.get("root_module_kind")) == "synthetic_module":
                if not dict(payload.get("synthetic_module_sources", {})):
                    findings.append(self._finding(
                        "blocker", spell_id,
                        "synthetic root {0!r} was sealed before the M3 "
                        "source capture; it cannot rebuild".format(
                            module_name
                        ),
                    ))
                continue
            try:
                spec = importlib.util.find_spec(module_name)
            except (ImportError, ValueError):
                spec = None
            if spec is None:
                # S2 physical custody: retained source text downgrades
                # the absent-module blocker - the engine's rebuild lane
                # reconstructs it through the synthetic module path with
                # an honest shortfall, so the load can proceed.
                if module_name in dict(
                        payload.get("user_module_sources", {})
                ):
                    findings.append(self._finding(
                        "info", spell_id,
                        "root module {0!r} is absent but its source is "
                        "RETAINED (opt-in physical custody); the engine "
                        "rebuilds it through the synthetic lane".format(
                            module_name
                        ),
                    ))
                    continue
                findings.append(self._finding(
                    "blocker", spell_id,
                    "root module {0!r} is not importable in this "
                    "environment; hydration will fail".format(
                        module_name
                    ),
                ))
        return findings

    def _finding(
            self,
            severity: str,
            spell_id: str,
            detail: str,
    ) -> Dict[str, object]:
        """
        Build one custody finding row.

        Args:
            severity:
                "blocker" or "warning" per the class contract.
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
