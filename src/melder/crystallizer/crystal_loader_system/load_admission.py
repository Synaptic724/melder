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
scope-blind frame-posture and mutation-research warnings into an
expected-for-scope admission view without ever rewriting the raw findings).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4;
rename: EPIC-2026-07-11-crystallizer-v3-horizon-iteration, story S1.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystal_loader_system.load_plan import LoadPlan
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.utilities.synchronization.phase_scheduler import (
        PhaseScheduler,
    )
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
        - The persistence record and optional `Aether` host are borrowed;
          admission never cleans either collaborator and never creates a frame
          merely to inspect host posture.

    Threading:
        Thread-confined to its owning CrystalLoaderSystem, which
        serializes load verbs under its own lock; no mediator lock.

    Lifecycle / Cleanup:
        Owned by exactly one CrystalLoaderSystem; cleanup dereferences the
        borrowed record (del posture); idempotent.

    Registration:
        MELDER KERNEL - guarded (`__melder_internal__` sentinel). The admission plane
        `CrystalLoaderSystem` constructs and owns; not user-held or bound. access=internal.

    Subsystem Context:
        The admission pipeline of THE UNFOLD: it turns a declarative `LoadPlan` into a gated
        engine run and a scope-adjudicated view (plan -> map -> verdict -> execute -> remember;
        renamed from BootMediator in S4). It mints formation windows in canonical kind order so
        folds see parents first, and borrows the record plus an optional `Aether` host without
        cleaning either.

    System Context:
        Crystallizer layer (position 2). The verdict law lives here: the engine always runs
        `refuse_on_blockers=True`, so blocker refusal is standard admission, not an opt-in; and
        adjudication is a VIEW - raw preflight findings are never rewritten, scope-expected
        warnings are only RECLASSIFIED into the additive "admission" payload. It never creates a
        frame merely to inspect host posture.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Plan, execute, and adjudicate admission-gated load transactions. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    # Canonical formation kind order: mirrors the engine's stage order so
    # folds see parents first (class-level constant per module-scope law).

    FORMATION_KIND_ORDER = (
        "frame", "spellbook", "conduit", "spell_index",
        "spell_crystal", "cluster", "contract",
    )

    __slots__ = Cleanable.__slots__ + [
        "_persistence_system",
        "_aether",
    ]

    def __init__(
            self,
            persistence_system: PersistenceSystem,
            aether: Optional["Aether"] = None,
    ) -> None:
        """
        Initialize the admission plane over one borrowed record.

        Args:
            persistence_system:
                The crystallizer's record (borrowed; used for chain
                detachment only, never cleaned here).
            aether:
                Optional borrowed Aether singleton (S1 load-scope
                maturity): when supplied, formation loads run the HOST
                preflight - live-world collision checks (frame presence/
                posture, conduit and cluster name collisions) - before
                any replay. None = bare-record posture: no host to check,
                host preflight reports empty (unit suites over records).

        Returns:
            None.

        Raises:
            TypeError: If `persistence_system` is None.
        """
        super().__init__()
        if persistence_system is None:
            raise TypeError("persistence_system cannot be None.")
        self._persistence_system: PersistenceSystem = persistence_system
        self._aether: Optional["Aether"] = aether

    def cleanup(self) -> None:
        """
        Idempotently dereference the borrowed record and host.

        Contract:
            Terminal for this admission object. Neither collaborator is owned,
            so cleanup does not clean the persistence record or `Aether`.

        Returns:
            None.

        Threading:
            Called by the owning loader after serialized load work has ended;
            it must not race with planning or execution.

        Lifecycle / Cleanup:
            `CrystalLoaderSystem` owns this object and cleans it before
            releasing its own borrowed record reference.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._persistence_system
        del self._aether

    # ------------------------------------------------------------------
    # PLAN
    # ------------------------------------------------------------------

    def plan_checkpoint_load(self, checkpoint_id: str) -> LoadPlan:
        """
        Build the declarative plan for one whole-world checkpoint load.

        Contract:
            Detaches the target checkpoint's same-profile chain through the
            record's public seam. The returned plan owns the detached windows
            and preserves checkpoint creation order; no replay or preflight
            runs during planning.

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
            target_frame_name: Optional[str] = None,
            skip_existing: bool = False,
    ) -> LoadPlan:
        """
        Build the declarative plan for one scoped formation load.

        Purpose:
            Manufacture the single synthetic chain window (journal minted
            in the canonical kind order - moved from the ledger in S4)
            and derive the plan's scope from the stored record. S1
            load-scope maturity: an optional RETARGET rewrites the
            window's frame identity so a formation captured on one frame
            composes into another.

        Contract:
            - The retarget rewrite happens in the DETACHED window ONLY:
              frame twins re-key, journal frame rows re-key, and book/
              cluster `frame_name` edges rewrite; the stored record dict
              the caller passed is never mutated (copy-on-write).
            - Formations are single-frame slices by capture design;
              retargeting a window carrying MORE than one frame twin
              refuses (teach-grade).

        Args:
            formation_record:
                A stored formation record (payloads + metadata) as
                captured by the ledger and loaded by the asset system.
            target_frame_name:
                Optional frame the load should aim at instead of the
                recorded identity. None = keep the recorded frame.
            skip_existing:
                When True, host name-collision blockers downgrade to
                "skipped_existing" and the engine runs its skip lanes.

        Returns:
            LoadPlan: Conduit- or frame-scoped plan with one window.

        Raises:
            RuntimeError: If the admission plane has been cleaned.
            KeyError: If the record lacks its required keys.
            ValueError: If a retarget hits a multi-frame window or a
                falsy/non-string target name.
        """
        self.check_cleaned()
        profile_name = str(formation_record["profile_name"])
        formation_name = str(formation_record["formation_name"])
        scope_record = dict(formation_record["scope"])
        plan_scope = "conduit" if "conduit_id" in scope_record else "frame"
        payloads = dict(formation_record["payloads"])
        if target_frame_name is not None:
            payloads = LoadAdmission._retarget_payloads(
                payloads, target_frame_name
            )

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
            target_frame_name=target_frame_name,
            skip_existing=skip_existing,
        )

    @staticmethod
    def _retarget_payloads(
            payloads: Dict[str, object],
            target_frame_name: str,
    ) -> Dict[str, object]:
        """
        Rewrite one detached payload map's frame identity (copy-on-write).

        Contract:
            - Frame twins re-key to the target (posture payloads carry no
              inner name field - the key IS the identity).
            - Every spellbook and cluster payload's `frame_name` edge
              rewrites to the target (formations are single-frame slices;
              the engine derives conduit frames from their books, so
              conduit payloads carry no frame edge of their own).
            - Inputs are never mutated: touched kinds are shallow-copied
              per payload before rewrite.

        Args:
            payloads:
                The record's kind -> {key -> payload} map (detached).
            target_frame_name:
                The frame the window should aim at.

        Returns:
            Dict[str, object]: A rewritten copy of the payload map.

        Raises:
            ValueError: If the target name is falsy/non-string or the
                window carries more than one frame twin.
        """
        if not isinstance(target_frame_name, str) or not target_frame_name:
            raise ValueError(
                "target_frame_name must be a non-empty string; got "
                "{0!r}.".format(target_frame_name)
            )
        rewritten = dict(payloads)
        frame_twins = dict(rewritten.get("frame", {}))
        if len(frame_twins) > 1:
            raise ValueError(
                "Retarget refused: the window carries {0} frame twins "
                "({1}); formations retarget single-frame slices only."
                .format(len(frame_twins), sorted(frame_twins.keys()))
            )
        if frame_twins:
            recorded_name, frame_payload = next(iter(frame_twins.items()))
            rewritten["frame"] = {target_frame_name: dict(frame_payload)}
        for kind in ("spellbook", "cluster"):
            kind_payloads = dict(rewritten.get(kind, {}))
            for key, payload in list(kind_payloads.items()):
                adjusted = dict(payload)
                if "frame_name" in adjusted:
                    adjusted["frame_name"] = target_frame_name
                kind_payloads[key] = adjusted
            if kind_payloads:
                rewritten[kind] = kind_payloads
        return rewritten

    # ------------------------------------------------------------------
    # EXECUTE + ADJUDICATE
    # ------------------------------------------------------------------

    def execute_plan(
            self,
            plan: LoadPlan,
            *,
            scheduler: Optional[PhaseScheduler] = None,
    ) -> Dict[str, object]:
        """
        Run one planned load through the gated engine and adjudicate.

        Contract:
            - The engine refuses "blockers" verdicts BEFORE any replay
              (standard admission; teach-grade error names the rows).
            - S1 HOST PREFLIGHT (conduit/frame scopes, live host wired):
              live-world collision findings are computed FIRST; host
              blockers refuse pre-replay unless the plan carries
              skip_existing (which downgrades them to "skipped_existing"
              and arms the engine's skip lanes).
            - The returned payload is the engine report's describe() plus
              the additive "admission" view (facade payloads stay
              byte-compatible superset); the admission view gains the
              additive "host" key.

        Args:
            plan:
                The declarative plan to execute (consumed by one engine).
            scheduler:
                Optional BORROWED PhaseScheduler (S4,
                parallel_restore_ulid_identity), passed through to the
                engine per load: present selects the graph-planned
                parallel driver; None selects the sequential driver. The
                loader owns the pool and its cohort span; this plane
                never stores or cleans it.

        Returns:
            Dict[str, object]:
                The detached report payload + {"admission": {"scope",
                "verdict", "reclassified", "host"}}.

        Raises:
            RuntimeError:
                If the admission plane was cleaned, admission refused the
                load (host-collision or preflight blockers), or a replay
                stage failed (after teardown; cause chained).
        """
        self.check_cleaned()
        host_findings = self._preflight_host(plan)
        host_blockers = [
            row for row in host_findings
            if row["severity"] == "blocker"
        ]
        if host_blockers and not plan.skip_existing:
            raise RuntimeError(
                "Load admission refused by host preflight ({0} blocker "
                "row(s)): {1}".format(
                    len(host_blockers),
                    "; ".join(
                        "{0} {1}={2}".format(
                            row["check"], row["kind"], row["key"]
                        )
                        for row in host_blockers
                    ),
                )
            )
        if plan.skip_existing:
            for row in host_findings:
                if row["severity"] == "blocker":
                    row["severity"] = "skipped_existing"

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
            skip_existing=plan.skip_existing,
            scheduler=scheduler,
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
        payload["admission"]["host"] = {
            "findings": host_findings,
            "checked": self._aether is not None,
        }
        return payload

    def _preflight_host(self, plan: LoadPlan) -> List[Dict[str, object]]:
        """
        Compute live-world collision findings for one formation plan.

        Contract:
            - Conduit/frame scopes only; world loads replay onto fresh
              boots and skip host checks entirely.
            - NEVER creates frames: frame presence reads the Aether
              registry directly (documented private seam - the
              crystallizer is Aether-owned; under lazy frames an
              _ensure_frame probe would BIRTH the frame it checks for).
            - Checks: frame missing -> "info" (replay creates it);
              recorded-vs-live posture conflict -> "warning"; conduit
              name collision -> "blocker"; cluster name collision ->
              "blocker". Both collision checks use the frame's public
              `conduit_cloud` accessor and public name probes.
            - No host wired (self._aether is None) -> empty findings.

        Args:
            plan:
                The plan whose single window is checked against the host.

        Returns:
            List[Dict[str, object]]:
                Rows of {"check", "severity", "kind", "key", "detail"}.
        """
        if self._aether is None or plan.scope == "world":
            return []
        findings: List[Dict[str, object]] = []
        window = plan.chain[0]
        payloads = dict(window.get("payloads", {}))
        frames = self._aether._aetheric_frames

        for frame_name, frame_payload in dict(
                payloads.get("frame", {})
        ).items():
            live_frame = frames.get(str(frame_name))
            if live_frame is None:
                findings.append({
                    "check": "frame_missing", "severity": "info",
                    "kind": "frame", "key": str(frame_name),
                    "detail": "replay postures it into existence",
                })
                continue
            recorded_state = dict(frame_payload).get("system_state")
            live_state = str(
                live_frame.frame_configuration.system_state.name
            )
            if (
                recorded_state is not None
                and str(recorded_state) != live_state
            ):
                findings.append({
                    "check": "frame_posture_conflict",
                    "severity": "warning",
                    "kind": "frame", "key": str(frame_name),
                    "detail": "recorded={0} live={1}".format(
                        recorded_state, live_state
                    ),
                })

        book_frames = {
            str(book_key): str(dict(book).get("frame_name", "default"))
            for book_key, book in dict(
                payloads.get("spellbook", {})
            ).items()
        }
        for conduit_key, conduit_payload in dict(
                payloads.get("conduit", {})
        ).items():
            recorded_name = dict(conduit_payload).get("conduit_name")
            if recorded_name is None:
                continue
            host_frame = frames.get(book_frames.get(
                str(dict(conduit_payload).get("spellbook_id")), "default"
            ))
            if host_frame is None:
                continue
            if host_frame.conduit_cloud.has_conduit_name(
                    str(recorded_name)
            ):
                findings.append({
                    "check": "conduit_name_taken", "severity": "blocker",
                    "kind": "conduit", "key": str(conduit_key),
                    "detail": "name={0}".format(recorded_name),
                })

        for cluster_key, cluster_payload in dict(
                payloads.get("cluster", {})
        ).items():
            cluster_name = dict(cluster_payload).get("cluster_name")
            if cluster_name is None:
                continue
            host_frame = frames.get(str(
                dict(cluster_payload).get("frame_name", "default")
            ))
            if host_frame is None:
                continue
            # NOTE (public_cloud_seams 2026-07-12): the documented
            # private seam retired - the cloud now exposes
            # has_cluster_name.
            if host_frame.conduit_cloud.has_cluster_name(
                    str(cluster_name)
            ):
                findings.append({
                    "check": "cluster_name_taken", "severity": "blocker",
                    "kind": "cluster", "key": str(cluster_key),
                    "detail": "name={0}".format(cluster_name),
                })
        return findings

    @staticmethod
    def _adjudicate_for_scope(
            preflight: Dict[str, object],
            scope: str,
    ) -> Dict[str, object]:
        """
        Derive the scope-aware admission view over one preflight report.

        Contract:
            - World scope: the admission verdict IS the raw verdict.
            - Conduit/frame scope: `frame_posture` warnings are expected
              because those scopes exclude or only partially carry frame
              twins. `mutation_research_composition` findings are also
              expected because MutationResearch is a world-scope root. Those
              rows reclassify to `expected_for_scope`, and the effective
              verdict is recomputed without them.
            - Raw findings are never mutated; reclassified rows are copies in
              the additive admission view.

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
            # frame_posture: conduit/frame slices deliberately exclude or
            # partially carry frame twins. mutation_research_composition:
            # MR is a WORLD-scope root - formation loads never rebuild it,
            # so its findings are expected context, not admission signal.
            if strategy in (
                "frame_posture",
                "mutation_research_composition",
            ):
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
