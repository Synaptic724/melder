"""
The small admission plane for load transactions (owner design, 2026-07-09;
renamed BootMediator -> LoadAdmission 2026-07-11 by owner ruling: the object
runs a linear admission pipeline, it does not mediate peers - the name now
matches the subsystem's established "admission" vocabulary and no longer
collides with the DevOps TransactionMediator).

Every load runs plan -> map -> verdict -> execute: LoadAdmission BUILDS the
declarative LoadPlan, the ENGINE maps it (authoritative folded preflight -
the only seam owning folded truth, so no fold logic is duplicated here) and
GATES it (blockers refuse before any replay), and LoadAdmission ADJUDICATES
the resulting report per scope (conduit/frame loads reclassify the
scope-blind frame_posture warnings into an expected-for-scope admission
view without ever rewriting the raw findings).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4;
rename: EPIC-2026-07-11-crystallizer-v3-horizon-iteration, story S1.
"""

from typing import Dict, List, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystal_loader_system.load_plan import LoadPlan

if TYPE_CHECKING:
    from melder.crystallizer.persistence.persistence_system import (
        PersistenceSystem,
    )


class LoadAdmission(Cleanable):
    """
    Plan, execute, and adjudicate admission-gated load transactions.

    Purpose:
        Give every load path (checkpoint chain, formation window) one
        admission pipeline: declarative plans in, gated engine runs
        through, scope-adjudicated admission views out.

    Contract:
        - Deliberately SMALL (owner ruling): no lock table, no claim
          modes - the admission plane plans, delegates, and interprets.
        - The engine runs with `refuse_on_blockers=True` ALWAYS: blocker
          refusal is standard admission, not an opt-in (verdict law).
        - Adjudication is a VIEW: raw preflight findings are never
          rewritten; scope-expected warnings are RECLASSIFIED into the
          additive "admission" payload only.
        - Formation windows are minted here in the canonical kind order
          (moved from the ledger in S4) so folds see parents first.

    Threading:
        Thread-confined to its owning CrystalLoaderSystem, which
        serializes load verbs under its own lock; no mediator lock.

    Lifecycle / Cleanup:
        Owned by exactly one CrystalLoaderSystem; cleanup dereferences the
        borrowed record (del posture); idempotent.
    """

    # Canonical formation kind order: mirrors the engine's stage order so
    # folds see parents first (class-level constant per module-scope law).
    FORMATION_KIND_ORDER = (
        "frame", "spellbook", "conduit", "spell_index",
        "spell_crystal", "cluster", "contract",
    )

    __slots__ = Cleanable.__slots__ + [
        "_persistence_system",
    ]

    def __init__(self, persistence_system: PersistenceSystem) -> None:
        """
        Initialize the admission plane over one borrowed record.

        Args:
            persistence_system:
                The crystallizer's record (borrowed; used for chain
                detachment only, never cleaned here).

        Returns:
            None.

        Raises:
            TypeError: If `persistence_system` is None.
        """
        super().__init__()
        if persistence_system is None:
            raise TypeError("persistence_system cannot be None.")
        self._persistence_system: PersistenceSystem = persistence_system

    def cleanup(self) -> None:
        """
        Idempotently dereference the borrowed record.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._persistence_system

    # ------------------------------------------------------------------
    # PLAN
    # ------------------------------------------------------------------

    def plan_checkpoint_load(self, checkpoint_id: str) -> LoadPlan:
        """
        Build the declarative plan for one whole-world checkpoint load.

        Args:
            checkpoint_id:
                ULID identity of the target checkpoint.

        Returns:
            LoadPlan: World-scoped plan carrying the detached chain.

        Raises:
            RuntimeError: If the admission plane has been cleaned.
            KeyError: If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        detached = self._persistence_system.detach_profile_chain(
            checkpoint_id
        )
        return LoadPlan(
            scope="world",
            profile_name=str(detached["profile_name"]),
            source_label=checkpoint_id,
            checkpoint_ids=list(detached["checkpoint_ids"]),
            chain=list(detached["chain"]),
        )

    def plan_formation_load(
            self,
            formation_record: Dict[str, object],
    ) -> LoadPlan:
        """
        Build the declarative plan for one scoped formation load.

        Purpose:
            Manufacture the single synthetic chain window (journal minted
            in the canonical kind order - moved from the ledger in S4)
            and derive the plan's scope from the stored record.

        Args:
            formation_record:
                A stored formation record (payloads + metadata) as
                captured by the ledger and loaded by the asset system.

        Returns:
            LoadPlan: Conduit- or frame-scoped plan with one window.

        Raises:
            RuntimeError: If the admission plane has been cleaned.
            KeyError: If the record lacks its required keys.
        """
        self.check_cleaned()
        profile_name = str(formation_record["profile_name"])
        formation_name = str(formation_record["formation_name"])
        scope_record = dict(formation_record["scope"])
        plan_scope = "conduit" if "conduit_id" in scope_record else "frame"
        payloads = dict(formation_record["payloads"])

        journal: List[List[object]] = []
        sequence = 0
        for kind in LoadAdmission.FORMATION_KIND_ORDER:
            for key in sorted(dict(payloads.get(kind, {})).keys()):
                sequence += 1
                journal.append([sequence, kind, key])
        window = {"journal": journal, "payloads": payloads}

        return LoadPlan(
            scope=plan_scope,
            profile_name=profile_name,
            source_label="formation-{0}".format(formation_name),
            checkpoint_ids=["formation-{0}".format(formation_name)],
            chain=[window],
        )

    # ------------------------------------------------------------------
    # EXECUTE + ADJUDICATE
    # ------------------------------------------------------------------

    def execute_plan(self, plan: LoadPlan) -> Dict[str, object]:
        """
        Run one planned load through the gated engine and adjudicate.

        Contract:
            - The engine refuses "blockers" verdicts BEFORE any replay
              (standard admission; teach-grade error names the rows).
            - The returned payload is the engine report's describe() plus
              the additive "admission" view (facade payloads stay
              byte-compatible superset).

        Args:
            plan:
                The declarative plan to execute (consumed by one engine).

        Returns:
            Dict[str, object]:
                The detached report payload + {"admission": {"scope",
                "verdict", "reclassified"}}.

        Raises:
            RuntimeError:
                If the admission plane was cleaned, admission refused the
                load (blockers), or a replay stage failed (after teardown;
                cause chained).
        """
        self.check_cleaned()
        # Lazy import: the engine drives runtime surfaces (3.14t-only
        # import chain) and must not burden plan-only usage.
        from melder.crystallizer.crystal_loader_system.restore_engine import (
            RestoreEngine,
        )

        engine = RestoreEngine(
            profile_name=plan.profile_name,
            checkpoint_ids=plan.checkpoint_ids,
            chain=plan.chain,
            refuse_on_blockers=True,
        )
        try:
            report = engine.restore()
            payload = report.describe()
            report.cleanup()
        finally:
            if not engine.cleaned:
                engine.cleanup()
        payload["admission"] = self._adjudicate_for_scope(
            dict(payload.get("preflight", {})),
            plan.scope,
        )
        return payload

    @staticmethod
    def _adjudicate_for_scope(
            preflight: Dict[str, object],
            scope: str,
    ) -> Dict[str, object]:
        """
        Derive the scope-aware admission view over one preflight report.

        Contract:
            - World scope: the admission verdict IS the raw verdict.
            - Conduit/frame scope: frame_posture warnings are EXPECTED
              (those scopes deliberately exclude/partially carry frame
              twins; the engine fallback-postures from book hints) - they
              reclassify to "expected_for_scope" rows and the admission
              verdict recomputes without them. Raw findings are never
              mutated.

        Args:
            preflight:
                The report's preflight section ({"findings", "counts",
                "verdict"}; possibly empty for legacy payloads).
            scope:
                The plan's load scope.

        Returns:
            Dict[str, object]:
                {"scope", "verdict", "reclassified": [rows]}.
        """
        raw_verdict = str(preflight.get("verdict", "clean"))
        findings = list(preflight.get("findings", []))
        if scope == "world":
            return {"scope": scope, "verdict": raw_verdict, "reclassified": []}

        reclassified: List[Dict[str, object]] = []
        effective_warning_count = 0
        effective_blocker_count = 0
        for finding in findings:
            severity = str(finding.get("severity", ""))
            strategy = str(finding.get("strategy", ""))
            if severity == "blocker":
                effective_blocker_count += 1
                continue
            if severity != "warning":
                continue
            if strategy == "frame_posture":
                adjusted_row = dict(finding)
                adjusted_row["severity"] = "expected_for_scope"
                reclassified.append(adjusted_row)
                continue
            effective_warning_count += 1

        if effective_blocker_count > 0:
            admission_verdict = "blockers"
        elif effective_warning_count > 0:
            admission_verdict = "warnings"
        else:
            admission_verdict = "clean"
        return {
            "scope": scope,
            "verdict": admission_verdict,
            "reclassified": reclassified,
        }
