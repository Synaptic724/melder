

import importlib
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class RestoreReport(Cleanable):
    """
    Detached outcome record for one restore run.

    Purpose:
        Carry everything the caller needs to judge a restore honestly: what
        was built (counts by kind), what could NOT be rebuilt and why
        (shortfall entries), and how recorded identities map onto the fresh
        identities the rebuilt world minted (the old->new translation map).

    Contract:
        - Value-only state: strings, ints, plain dicts/lists. No live twin or
          runtime references, no locks, no callables.
        - Shortfalls are the honesty surface: anything the engine skipped is
          entered here; nothing is silently under-built.
        - Recorded ULIDs appear ONLY inside the translation map; they never
          escape into the rebuilt world (never-rehydrate-ULIDs policy).

    Threading:
        Mutated by exactly one RestoreEngine on one thread during one restore
        call; readers consume `describe()` afterwards. No lock by contract.

    Lifecycle:
        Owned by the engine while the run is live; ownership passes to the
        caller with the return. `cleanup()` deletes owned fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_profile_name",
        "_checkpoint_ids",
        "_built_counts",
        "_shortfalls",
        "_identity_map",
        "_status",
        "_failed_stage",
        "_preflight",
    ]

    def __init__(self, profile_name: str, checkpoint_ids: List[str]) -> None:
        """
        Initialize an empty report for one restore run.

        Args:
            profile_name:
                Profile the restored chain was sealed from.
            checkpoint_ids:
                The folded chain's checkpoint ULIDs, oldest first.

        Returns:
            None.

        Raises:
            ValueError:
                If `profile_name` is empty or `checkpoint_ids` is empty.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("RestoreReport requires a non-empty profile_name.")
        if not checkpoint_ids:
            raise ValueError(
                "RestoreReport requires at least one checkpoint id."
            )
        self._profile_name: str = profile_name
        self._checkpoint_ids: List[str] = list(checkpoint_ids)
        self._built_counts: Dict[str, int] = {}
        self._shortfalls: List[Dict[str, str]] = []
        self._identity_map: Dict[str, str] = {}
        self._status: str = "pending"
        self._failed_stage: Optional[str] = None
        # Load-time strategy analysis (owner ruling: strategies run AS
        # we load); attached by the engine after the fold, before replay.
        self._preflight: Dict[str, object] = {}

    def cleanup(self) -> None:
        """
        Delete owned report fields and mark the report cleaned.

        Contract:
            - Idempotent; del posture (no tombstone fields retained).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._profile_name
        del self._checkpoint_ids
        del self._built_counts
        del self._shortfalls
        del self._identity_map
        del self._status
        del self._failed_stage
        del self._preflight

    def set_preflight(self, preflight_report: Dict[str, object]) -> None:
        """
        Attach the load-time strategy analysis to this report.

        Purpose:
            Owner ruling: analysis strategies run AS the world loads.
            The engine folds the chain, runs the PersistenceAnalyzer
            over the folded bundle, and files the result here so every
            restore report carries its own pre-flight.

        Args:
            preflight_report:
                The analyzer's detached {"findings", "counts",
                "verdict"} report.

        Returns:
            None.

        Raises:
            RuntimeError: If the report has been cleaned.
        """
        self.check_cleaned()
        self._preflight = dict(preflight_report)

    def record_built(self, kind: str) -> None:
        """
        Increment the built counter for one unit kind.

        Args:
            kind:
                Unit kind label ("spellbook", "conduit", "spell_active",
                "spell_staged", "link", "contract_detail", "cluster", ...).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        self._built_counts[kind] = self._built_counts.get(kind, 0) + 1

    def add_shortfall(self, kind: str, key: str, reason: str) -> None:
        """
        Append one honesty entry for a unit the engine did not rebuild.

        Args:
            kind:
                Recorded kind of the affected unit.
            key:
                Recorded identity key of the affected unit.
            reason:
                Teach-grade reason label plus context.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        self._shortfalls.append(
            {"kind": kind, "key": key, "reason": reason}
        )

    def map_identity(self, recorded_id: str, live_id: str) -> None:
        """
        Record one recorded-ULID -> fresh-live-identity translation.

        Args:
            recorded_id:
                Record-local identity from the checkpoint payloads.
            live_id:
                Identity the rebuilt world minted for the same unit.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        self._identity_map[recorded_id] = live_id

    def translate(self, recorded_id: str) -> Optional[str]:
        """
        Resolve one recorded identity to its fresh live identity.

        Args:
            recorded_id:
                Record-local identity to translate.

        Returns:
            Optional[str]:
                The live identity, or None when the unit was not rebuilt.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        return self._identity_map.get(recorded_id)

    def mark_complete(self) -> None:
        """
        Mark the run successful.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        self._status = "complete"

    def mark_failed(self, stage: str) -> None:
        """
        Mark the run failed at one named replay stage.

        Args:
            stage:
                The stage label that raised.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        self._status = "failed"
        self._failed_stage = stage

    def describe(self) -> Dict[str, object]:
        """
        Return the detached report payload.

        Returns:
            Dict[str, object]:
                Status, profile, chain ids, built counts, shortfall entries,
                and the identity translation map - fully detached copies.

        Raises:
            RuntimeError:
                If the report has been cleaned.
        """
        self.check_cleaned()
        return {
            "status": self._status,
            "failed_stage": self._failed_stage,
            "profile_name": self._profile_name,
            "checkpoint_ids": list(self._checkpoint_ids),
            "built_counts": dict(self._built_counts),
            "shortfalls": [dict(entry) for entry in self._shortfalls],
            "identity_map": dict(self._identity_map),
            "preflight": dict(self._preflight),
        }


class RestoreEngine(Cleanable):
    """
    Single-use driver that unfolds one folded checkpoint chain into the live
    runtime through the PUBLIC verbs (boot lane).

    Purpose:
        The B3 restore engine: fold the profile's checkpoint chain (later
        payloads win per (kind, key); tombstones delete), then replay the
        folded world in canon order - spellbook configs -> conjure -> binds
        by bind_order -> staged members onto their index anchors -> notch to
        recorded selections -> links -> clusters -> contracts LAST - minting
        fresh identities and REPORTING every shortfall.

    Contract:
        - Consumes DETACHED chain data only (replay_data dicts); never touches
          PersistenceSystem internals or holds its lock (replay re-enters the
          emit path, which must be free to record the rebuilt world).
        - All-or-nothing: a stage failure tears down every unit this run
          built (reverse build order), then raises RuntimeError chaining the
          stage error.
        - Re-emission is intended: the rebuilt world re-records itself into
          the ACTIVE profile under fresh identities.
        - Single-use: `restore()` raises on a second call.

    Threading:
        One engine, one thread, one call by contract (boot lane). No internal
        lock; the runtime verbs it drives take their own locks.

    Lifecycle:
        Constructed per restore call. `cleanup()` deletes owned fold state;
        the returned report's ownership passes to the caller; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_chain",
        "_report",
        "_consumed",
        "_refuse_on_blockers",
        "_skip_existing",
        "_aether_payload",
        "_crystallizer_payload",
        "_nexus_payload",
        "_nexus_state_name",
        "_mutation_research_payload",
        "_mutation_research_state_name",
        "_frames",
        "_postured_frames",
        "_books",
        "_conduits",
        "_indexes",
        "_contracts",
        "_clusters",
        "_custody_active",
        "_custody_inactive",
        "_live_books",
        "_live_conduits",
        "_built_stack",
    ]

    def __init__(
            self,
            profile_name: str,
            checkpoint_ids: List[str],
            chain: List[Dict[str, object]],
            refuse_on_blockers: bool = False,
            skip_existing: bool = False,
    ) -> None:
        """
        Initialize one engine over a detached, ordered checkpoint chain.

        Args:
            profile_name:
                Profile the chain was sealed from (report metadata).
            checkpoint_ids:
                Chain checkpoint ULIDs, oldest first (report metadata).
            chain:
                The chain's `replay_data()` payloads in the same order:
                each {"journal": [[sequence, kind, key], ...],
                      "payloads": {kind: {key: payload}}}.
            refuse_on_blockers:
                Admission gate (S4 verdict law): when True, a "blockers"
                preflight verdict over the FOLDED bundle refuses the load
                BEFORE any replay (nothing is built, so no teardown is
                needed). LoadAdmission always passes True; the default
                False preserves the legacy direct-engine behavior for
                existing unit suites.
            skip_existing:
                S1 skip lanes: when True, live-host name collisions met
                DURING replay skip instead of failing - a taken conduit
                name conjures UNNAMED with shortfall
                "conduit_name_taken_built_unnamed", and an existing
                cluster is REUSED (members join it) with shortfall
                "cluster_existed_members_joined". False preserves the
                fail-fast behavior (host preflight normally refused these
                rows already; mid-replay collisions then surface as
                stage failures).

        Returns:
            None.

        Raises:
            ValueError:
                If `chain` is empty or misaligned with `checkpoint_ids`.
        """
        super().__init__()
        if not chain:
            raise ValueError("RestoreEngine requires a non-empty chain.")
        if len(chain) != len(checkpoint_ids):
            raise ValueError(
                "chain and checkpoint_ids must align: got {0} windows for "
                "{1} ids.".format(len(chain), len(checkpoint_ids))
            )
        self._chain: List[Dict[str, object]] = chain
        self._report: RestoreReport = RestoreReport(
            profile_name, checkpoint_ids
        )
        self._consumed: bool = False
        self._refuse_on_blockers: bool = refuse_on_blockers
        self._skip_existing: bool = bool(skip_existing)
        # Folded stores: recorded truth after later-wins + tombstones.
        self._aether_payload: Optional[Dict[str, object]] = None
        self._crystallizer_payload: Optional[Dict[str, object]] = None
        self._nexus_payload: Optional[Dict[str, object]] = None
        # Latest folded nexus lifecycle state name (later-wins); None when
        # the window carries no state flip.
        self._nexus_state_name: Optional[str] = None
        # MR folds for ordered honest reporting (owner scope: too new to
        # restore); the stage reports, never silently.
        self._mutation_research_payload: Optional[Dict[str, object]] = None
        self._mutation_research_state_name: Optional[str] = None
        self._frames: Dict[str, Dict[str, object]] = {}
        # Frames whose live posture the frames stage (or the missing-twin
        # fallback) already applied; books refuse to build on an
        # unpostured frame (fresh boots default to automatic).
        self._postured_frames: Set[str] = set()
        self._books: Dict[str, Dict[str, object]] = {}
        self._conduits: Dict[str, Dict[str, object]] = {}
        self._indexes: Dict[str, Dict[str, object]] = {}
        self._contracts: Dict[str, Dict[str, object]] = {}
        self._clusters: Dict[str, Dict[str, object]] = {}
        self._custody_active: Dict[str, Dict[str, object]] = {}
        self._custody_inactive: Dict[str, Dict[str, object]] = {}
        # Live handles built during replay (for wiring + rollback).
        self._live_books: Dict[str, Any] = {}
        self._live_conduits: Dict[str, Any] = {}
        self._built_stack: List[Tuple[str, Any]] = []

    def cleanup(self) -> None:
        """
        Delete owned fold/replay state and mark the engine cleaned.

        Contract:
            - Idempotent; del posture.
            - Does NOT clean the report: its ownership passes to the caller
              when `restore()` returns (a never-run engine cleans it).
        """
        if self._cleaned:
            return
        self._cleaned = True
        if not self._consumed and not self._report.cleaned:
            self._report.cleanup()
        del self._chain
        del self._report
        del self._consumed
        del self._refuse_on_blockers
        del self._skip_existing
        del self._aether_payload
        del self._crystallizer_payload
        del self._nexus_payload
        del self._nexus_state_name
        del self._mutation_research_payload
        del self._mutation_research_state_name
        del self._frames
        del self._postured_frames
        del self._books
        del self._conduits
        del self._indexes
        del self._contracts
        del self._clusters
        del self._custody_active
        del self._custody_inactive
        del self._live_books
        del self._live_conduits
        del self._built_stack

    def restore(self) -> RestoreReport:
        """
        Fold the chain and replay it into the live runtime.

        Contract:
            - Single-use; a second call raises RuntimeError.
            - All-or-nothing: on stage failure every built unit is torn down
              in reverse order, then RuntimeError raises chaining the cause.

        Returns:
            RestoreReport:
                The detached outcome record (ownership passes to the caller).

        Raises:
            RuntimeError:
                If the engine was cleaned, already consumed, or a replay
                stage failed (after teardown; original error chained).
        """
        self.check_cleaned()
        if self._consumed:
            raise RuntimeError(
                "RestoreEngine is single-use; construct a fresh engine for "
                "another restore."
            )
        self._consumed = True
        self._fold_chain()
        # Owner ruling: analysis strategies run AS we load - the folded
        # bundle pre-flights before any replay, and the findings ride
        # the restore report ("preflight"). S4 verdict law: when the
        # admission knob is set (every mediated load), a "blockers"
        # verdict REFUSES the load here - the only seam owning
        # authoritative folded truth - before anything is built.
        preflight_report = self._run_preflight()
        self._report.set_preflight(preflight_report)
        if (
                self._refuse_on_blockers
                and str(preflight_report.get("verdict", "clean")) == "blockers"
        ):
            blocker_rows = [
                finding
                for finding in list(preflight_report.get("findings", []))
                if str(finding.get("severity", "")) == "blocker"
            ]
            self._report.mark_failed("admission")
            raise RuntimeError(
                "admission refused the load: the folded chain pre-flighted "
                "with {0} blocker finding(s) - {1}. Fix the recorded world "
                "(or its environment) and retry; nothing was built.".format(
                    len(blocker_rows),
                    "; ".join(
                        "{0}[{1}:{2}] {3}".format(
                            str(row.get("strategy", "?")),
                            str(row.get("kind", "?")),
                            str(row.get("key", "?")),
                            str(row.get("detail", "")),
                        )
                        for row in blocker_rows
                    ),
                )
            )
        stage = "fold"
        try:
            # Canonical configuration order (owner ruling):
            # Aether|AetherUtilitySystem -> Crystallizer -> MR -> Nexus ->
            # AethericFrame -> Spellbook -> Conduit|Ward.
            stage = "aether_configuration"
            self._replay_aether_configuration()
            stage = "crystallizer_policy"
            self._replay_crystallizer_policy()
            stage = "mutation_research"
            self._replay_mutation_research()
            stage = "nexus"
            self._replay_nexus()
            stage = "frames"
            self._replay_frames()
            stage = "books_and_binds"
            self._replay_books_and_binds()
            stage = "links"
            self._replay_links()
            stage = "clusters"
            self._replay_clusters()
            stage = "contracts"
            self._replay_contracts()
        except Exception as error:
            self._report.mark_failed(stage)
            self._teardown_built()
            raise RuntimeError(
                "restore failed at stage {0!r}; the partially built world "
                "was torn down (all-or-nothing). See the chained error for "
                "the cause.".format(stage)
            ) from error
        self._report.mark_complete()
        return self._report

    def _run_preflight(self) -> Dict[str, object]:
        """
        Run the analysis strategies over the FOLDED bundle (load-time).

        Contract:
            - The bundle is the folded recorded truth (chain-wide), so
              completeness findings are meaningful - unlike a single
              delta window.
            - Read-only: strategies never touch the folded stores or the
              live runtime.

        Returns:
            Dict[str, object]:
                The analyzer's {"findings", "counts", "verdict"} report.
        """
        # Lazy import mirrors the engine's runtime-surface import law.
        from melder.crystallizer.crystal_analysis.preflight.persistence_analyzer import (
            PersistenceAnalyzer,
        )

        bundle: Dict[str, Dict[str, Dict[str, object]]] = {
            "frame": dict(self._frames),
            "spellbook": dict(self._books),
            "conduit": dict(self._conduits),
            "spell_index": dict(self._indexes),
            "contract": dict(self._contracts),
            "cluster": dict(self._clusters),
            "spell_crystal": {
                **dict(self._custody_active),
                **dict(self._custody_inactive),
            },
        }
        if self._aether_payload is not None:
            bundle["aether"] = {"root": dict(self._aether_payload)}
        if self._crystallizer_payload is not None:
            bundle["crystallizer"] = {
                "root": dict(self._crystallizer_payload)
            }
        if self._nexus_payload is not None:
            bundle["nexus"] = {"root": dict(self._nexus_payload)}
        analyzer = PersistenceAnalyzer()
        try:
            return analyzer.analyze(bundle)
        finally:
            analyzer.cleanup()

    def _fold_chain(self) -> None:
        """
        Fold every chain window into the recorded-truth stores.

        Contract:
            - Windows apply oldest-first; entries apply in journal order.
            - Twin kinds replace per (kind, key) - later wins.
            - Tombstones delete their targets, applying the same match rules
              the live evictions used (spellbook parent-edge subtree sweep,
              frame-name sweep).
            - `spell_activity` moves custody between the active/inactive
              stores per the captured current-truth payload.

        Returns:
            None.
        """
        for window in self._chain:
            payloads = window["payloads"]
            for entry in window["journal"]:
                kind = str(entry[1])
                key = str(entry[2])
                payload = payloads.get(kind, {}).get(key)
                if payload is None:
                    # Honesty guard (triage #2 lesson): a journaled entry
                    # with no captured payload is a capture anomaly, not a
                    # normal shape - the SpellbookCrystal emission gap hid
                    # behind a silent skip here and restores reported
                    # "complete" over empty worlds. Report it, keep folding.
                    self._report.add_shortfall(
                        kind, key, "journal_entry_without_captured_payload"
                    )
                    continue
                self._fold_entry(kind, key, dict(payload))

    def _fold_entry(
            self,
            kind: str,
            key: str,
            payload: Dict[str, object],
    ) -> None:
        """
        Apply one journaled entry to the folded stores.

        Args:
            kind:
                Journal kind label.
            key:
                Identity key within the kind.
            payload:
                The captured payload for the entry's window.

        Returns:
            None.
        """
        if kind == "aether":
            self._aether_payload = payload
        elif kind == "nexus":
            self._nexus_payload = payload
        elif kind == "nexus_state":
            # Later-wins lifecycle truth: the journal key carries the
            # flipped state name; the payload confirms twin presence.
            self._nexus_state_name = key
        elif kind == "mutation_research":
            self._mutation_research_payload = payload
        elif kind == "mutation_research_state":
            self._mutation_research_state_name = key
        elif kind == "crystallizer":
            # The recorder's own policy twin: boot-time truth, never
            # replayed mid-restore (the live crystallizer driving this
            # restore already runs its own policy).
            self._crystallizer_payload = payload
        elif kind == "frame":
            self._frames[key] = payload
        elif kind == "spellbook":
            self._books[key] = payload
        elif kind == "conduit":
            self._conduits[key] = payload
        elif kind == "spell_index":
            self._indexes[key] = payload
        elif kind == "contract":
            self._contracts[key] = payload
        elif kind == "cluster":
            self._clusters[key] = payload
        elif kind == "spell_crystal":
            # The capture annotates WHICH location held custody at seal
            # time (staged members never flip, so spell_activity alone
            # cannot tell them apart). Pre-annotation payloads (old cached
            # checkpoints) default active, matching their era's behavior.
            location = str(payload.get("custody_location", "active"))
            self._custody_active.pop(key, None)
            self._custody_inactive.pop(key, None)
            if location == "inactive":
                self._custody_inactive[key] = payload
            else:
                self._custody_active[key] = payload
        elif kind == "spell_activity":
            self._fold_spell_activity(key, payload)
        elif kind == "spell_removed":
            self._custody_active.pop(key, None)
            self._custody_inactive.pop(key, None)
        elif kind == "spellbook_removed":
            self._fold_spellbook_removed(key)
        elif kind == "frame_removed":
            self._fold_frame_removed(key)
        elif kind == "spell_index_removed":
            self._indexes.pop(key, None)
        elif kind == "contract_removed":
            self._contracts.pop(key, None)
        elif kind == "cluster_removed":
            self._clusters.pop(key, None)
        elif kind in ("nexus_state", "mutation_research_state"):
            # State switches are reported, not replayed, in this cut.
            self._report.add_shortfall(
                kind, key, "recorded_state_switch_not_replayed_first_cut"
            )

    def _fold_spell_activity(
            self,
            spell_id: str,
            payload: Dict[str, object],
    ) -> None:
        """
        Move one spell's folded custody between locations.

        Args:
            spell_id:
                The flipped spell's SHA identity.
            payload:
                Captured current-truth ({"active": bool, ...}).

        Returns:
            None.
        """
        active = bool(payload.get("active"))
        source = (
            self._custody_inactive if active else self._custody_active
        )
        target = (
            self._custody_active if active else self._custody_inactive
        )
        crystal_payload = source.pop(spell_id, None)
        if crystal_payload is None and spell_id not in target:
            return
        if crystal_payload is not None:
            target[spell_id] = crystal_payload

    def _fold_spellbook_removed(self, spellbook_id: str) -> None:
        """
        Sweep one dead book's folded subtree (parent-edge match).

        Args:
            spellbook_id:
                The removed book's identity.

        Returns:
            None.
        """
        self._books.pop(spellbook_id, None)
        for store in (self._custody_active, self._custody_inactive):
            for spell_id in [
                key
                for key, payload in store.items()
                if payload.get("spellbook_id") == spellbook_id
            ]:
                store.pop(spell_id, None)
        for index_id in [
            key
            for key, payload in self._indexes.items()
            if payload.get("spellbook_id") == spellbook_id
        ]:
            self._indexes.pop(index_id, None)
        dead_conduits = [
            key
            for key, payload in self._conduits.items()
            if payload.get("spellbook_id") == spellbook_id
        ]
        for conduit_id in dead_conduits:
            self._conduits.pop(conduit_id, None)
            for contract_id in [
                key
                for key, payload in self._contracts.items()
                if conduit_id in (
                    payload.get("conduit_a_id"),
                    payload.get("conduit_b_id"),
                )
            ]:
                self._contracts.pop(contract_id, None)

    def _fold_frame_removed(self, frame_name: str) -> None:
        """
        Sweep one dead frame's folded subtree.

        Args:
            frame_name:
                The removed frame's canonical name.

        Returns:
            None.
        """
        self._frames.pop(frame_name, None)
        for spellbook_id in [
            key
            for key, payload in self._books.items()
            if payload.get("frame_name") == frame_name
        ]:
            self._fold_spellbook_removed(spellbook_id)
        for cluster_id in [
            key
            for key, payload in self._clusters.items()
            if payload.get("frame_name") == frame_name
        ]:
            self._clusters.pop(cluster_id, None)

    def _replay_aether_configuration(self) -> None:
        """
        Stage 1: apply the recorded root configuration when possible.

        Contract:
            - A live, already-configured Aether is respected: the recorded
              payload is reported as skipped, never force-applied.
            - Property failures degrade to shortfall entries (the root config
              is advisory for the world structure that follows).
        Returns:
            None.
        """
        if self._aether_payload is None:
            return
        from melder.aether.aether import Aether

        aether = Aether()
        payload = dict(
            self._aether_payload.get("configuration_payload", {})
        )
        if not payload:
            return
        if aether.configured:
            self._report.add_shortfall(
                "aether", "root",
                "live_aether_already_configured_recorded_payload_skipped",
            )
            return
        # RELOAD lane (owner ruling: sealed worlds rebuild from recorded
        # truth through dedicated reload verbs): the root configuration
        # rebuilds and seals from the recorded payload in one motion;
        # every deviation rides back for shortfall reporting. Its
        # callable-bearing entries (resolver/default logger) can never
        # round-trip through a record and are reported as such.
        from melder.aether.aether_configuration import AetherConfiguration

        configuration, reload_report = (
            AetherConfiguration.from_recorded_payload(payload)
        )
        for missing_key in reload_report["missing"]:
            self._report.add_shortfall(
                "aether", missing_key,
                "root_config_key_missing_defaulted_with_report",
            )
        for callable_key in reload_report["code_participation"]:
            self._report.add_shortfall(
                "aether", callable_key,
                "root_config_entry_requires_code_participation",
            )
        # Aether.activate requires an ACTIVATED configuration (activation
        # is the configuration's own act and its emission moment - the
        # rebuilt root re-records here); the reload verb only sealed it.
        configuration.activate()
        aether.activate(configuration)
        self._report.record_built("aether_configuration")

    def _replay_crystallizer_policy(self) -> None:
        """
        Stage 2: report the recorder's own recorded policy (boot-time
        truth).

        Contract:
            - The live crystallizer driving this restore already runs its
              policy; a mid-restore swap is never legal. The folded twin
              is reported so boot code knows to reload it via
              CrystallizerConfiguration.load_recorded_dictionary BEFORE
              activation on the next boot.

        Returns:
            None.
        """
        if self._crystallizer_payload is not None:
            self._report.add_shortfall(
                "crystallizer", "root",
                "crystallizer_policy_recorded_reload_is_boot_time_act",
            )

    def _replay_mutation_research(self) -> None:
        """
        Stage 3: report recorded MR truth (owner scope: not restored).

        Contract:
            - MR is too new to restore; the folded twin and lifecycle
              state report honestly in canonical order, never silently.

        Returns:
            None.
        """
        if self._mutation_research_payload is not None:
            self._report.add_shortfall(
                "mutation_research", "root",
                "mutation_research_recorded_not_restored_first_cut",
            )
        if self._mutation_research_state_name is not None:
            self._report.add_shortfall(
                "mutation_research", self._mutation_research_state_name,
                "mutation_research_state_recorded_not_restored_first_cut",
            )

    def _replay_nexus(self) -> None:
        """
        Stage 4: rebuild the recorded Nexus root (config + lifecycle).

        Contract:
            - No recorded nexus twin: NO-OP (a world without Nexus stays
              without one).
            - The configuration rebuilds through the RELOAD lane
              (NexusConfiguration.load_recorded_dictionary; per-key
              rejected/backfilled shortfalls) and enables through the
              public verb - Nexus.enable emits the twin for pre-frozen
              reloaded configurations, so the rebuilt root re-records.
            - The folded lifecycle state is later-wins truth: a final
              "disabled" replays enable-then-disable (both acts are the
              recorded history); a final "cleaned" skips the rebuild with
              an honest report (the world sealed AFTER its Nexus died).

        Returns:
            None.
        """
        if self._nexus_payload is None:
            return
        if self._nexus_state_name == "cleaned":
            self._report.add_shortfall(
                "nexus", "root",
                "nexus_recorded_but_cleaned_before_seal_not_rebuilt",
            )
            return
        from melder.nexus.configuration.nexus_configuration import (
            NexusConfiguration,
        )
        from melder.nexus.nexus import Nexus

        configuration = NexusConfiguration()
        reload_outcome = configuration.load_recorded_dictionary(
            dict(self._nexus_payload.get("configuration_payload", {}))
        )
        for rejected_entry in reload_outcome["rejected"]:
            self._report.add_shortfall(
                "nexus", "root",
                "config_property_not_replayable: {0}".format(
                    rejected_entry
                ),
            )
        for backfilled_key in reload_outcome["backfilled"]:
            self._report.add_shortfall(
                "nexus", "root",
                "config_property_backfilled_schema_default: {0}".format(
                    backfilled_key
                ),
            )
        nexus = Nexus()
        nexus.enable(configuration)
        if self._nexus_state_name == "disabled":
            # Recorded history: the world sealed with a disabled Nexus -
            # enable-then-disable replays both truthful acts.
            nexus.disable()
        self._built_stack.append(("nexus", nexus))
        self._report.record_built("nexus")

    def _replay_frames(self) -> None:
        """
        Stage 5: posture recorded frames BEFORE any book construction.

        Contract:
            - Frames are the posture owners in the runtime: conjure's
              check_system_state reads the FRAME configuration, so every
              recorded frame twin must land before its books build (a
              fresh-boot frame holds the automatic default posture and
              refuses the recorded lane's dynamic conjures).
            - Frame names are stable identities; no translation needed.

        Returns:
            None.
        """
        from melder.aether.aetheric_frame.aetheric_frame_configuration import (
            AethericFrameConfiguration,
        )

        for frame_name, payload in self._frames.items():
            # RELOAD lane: the sealed twin payload is the posture truth;
            # the verb reports every key that fell back to a schema
            # default so nothing substitutes silently.
            posture, backfilled_keys = (
                AethericFrameConfiguration.from_recorded_posture(
                    dict(payload)
                )
            )
            for backfilled_key in backfilled_keys:
                self._report.add_shortfall(
                    "frame", frame_name,
                    "posture_key_backfilled_schema_default: {0}".format(
                        backfilled_key
                    ),
                )
            self._posture_frame(frame_name, posture)
            self._report.record_built("frame")

    def _ensure_frame_postured(
            self,
            frame_name: str,
            book_payload: Dict[str, object],
    ) -> None:
        """
        Guarantee a book's frame carries a dynamic posture before building.

        Contract:
            - NO-OP when the frames stage already postured the frame.
            - Missing frame twin (windows sealed before the frame emission
              landed): the record's hard gate only ever seals dynamic
              worlds, so the frame postures dynamic with ai_native/rift
              hints pulled from the book's recorded configuration payload,
              and the tolerance is reported as a shortfall.

        Args:
            frame_name:
                The book's recorded frame edge.
            book_payload:
                The folded book twin payload (posture hint source).

        Returns:
            None.
        """
        if frame_name in self._postured_frames:
            return
        from melder.aether.aetheric_frame.aetheric_frame_configuration import (
            AethericFrameConfiguration,
        )
        from melder.aether.spellbook.configuration.system_state import (
            SystemState,
        )

        configuration_payload = dict(
            book_payload.get("configuration_payload", {})
        )
        # AUTHORING lane on purpose (not the reload verb): there is no
        # recorded posture to reload, so a fresh dynamic posture is built
        # from the book's recorded hints and the single shortfall below
        # carries the whole tolerance - per-key backfill noise would drown
        # the real signal.
        fallback_posture = AethericFrameConfiguration(
            origin_spellbook_id=None,
            system_state=SystemState.dynamic,
            ai_native_enabled=bool(
                configuration_payload.get("ai_native_enabled", False)
            ),
            rift_enabled=bool(
                configuration_payload.get("rift_enabled", False)
            ),
        )
        self._posture_frame(frame_name, fallback_posture)
        self._report.add_shortfall(
            "frame", frame_name,
            "frame_twin_missing_postured_dynamic_from_book_hints",
        )

    def _posture_frame(
            self,
            frame_name: str,
            posture: Any,
    ) -> None:
        """
        Bind one built posture object onto the live frame (then freeze).

        Contract:
            - Binds through AethericFrame.bind_frame_configuration: the
              frame copies the values into its own default unfrozen posture
              and freezes WITH origin identity, so the frame twin re-emits
              (the rebuilt world re-records its frames).
            - Idempotent against an already-frozen MATCHING posture; a
              frozen conflicting posture keeps the canonical frame truth
              (the frame logs the conflict).
            - Posture construction belongs to the callers: the frames
              stage RELOADS recorded twins via
              AethericFrameConfiguration.from_recorded_posture; the
              missing-twin fallback AUTHORS a fresh dynamic posture.

        Args:
            frame_name:
                Canonical frame name (twin anchor + live frame key).
            posture:
                The built, unfrozen AethericFrameConfiguration to bind
                (typed Any: the engine lazy-imports runtime surfaces).

        Returns:
            None.
        """
        from melder.aether.aether import Aether

        # Deliberate private seam (same class as frame._conduit_cloud in
        # the cluster stage): Aether exposes no public frame accessor yet;
        # the public-accessor follow-up is tracked in the story ticket.
        frame = Aether()._ensure_frame(frame_name)
        frame.bind_frame_configuration(posture)
        self._postured_frames.add(frame_name)

    def _replay_books_and_binds(self) -> None:
        """
        Stage 6 span (Spellbook -> Conduit|Ward): books, active binds,
        conjure, staged members, selections.

        Contract:
            - Per recorded book: build the SpellbookConfiguration from the
              recorded payload (lossy values -> shortfalls) and FINALIZE it
              BEFORE any bind - the conjure configuration-discipline guard
              refuses recorded-lane worlds whose binds ran against a mutable
              configuration.
            - The natural lane replays: actives bind PRE-conjure (bind
              self-admits its window), the recorded root conduit conjures,
              staged members bind_inactive onto their live anchors POST-
              conjure, then divergent selections notch.
            - Spell SHAs are content-derived and stay STABLE across restore;
              only index/conduit/contract/cluster ULIDs need translation.

        Returns:
            None.
        """
        from melder.aether.spellbook.configuration.spellbook_configuration import (
            SpellbookConfiguration,
        )
        from melder.aether.spellbook.spellbook import Spellbook

        for spellbook_id, book_payload in self._books.items():
            frame_name = str(book_payload.get("frame_name", "default"))
            self._ensure_frame_postured(frame_name, book_payload)
            configuration = SpellbookConfiguration(aether_frame=frame_name)
            # RELOAD lane, never the defaults lane: recorded values are the
            # configuration truth; the verb applies them first, backfills
            # only required keys the window does not carry, and reports
            # every deviation back so nothing defaults silently.
            reload_outcome = configuration.load_recorded_dictionary(
                dict(book_payload.get("configuration_payload", {}))
            )
            for rejected_entry in reload_outcome["rejected"]:
                self._report.add_shortfall(
                    "spellbook", spellbook_id,
                    "config_property_not_replayable: {0}".format(
                        rejected_entry
                    ),
                )
            for backfilled_key in reload_outcome["backfilled"]:
                self._report.add_shortfall(
                    "spellbook", spellbook_id,
                    "config_property_backfilled_schema_default: "
                    "{0}".format(backfilled_key),
                )
            for hook_name in list(book_payload.get("hook_names", [])):
                self._report.add_shortfall(
                    "spellbook", spellbook_id,
                    "hook_requires_code_participation: {0}".format(
                        hook_name
                    ),
                )
            # Frozen BEFORE binds: the reload verb loads and freezes in
            # one motion, so recorded worlds are never born
            # config-incoherent (the conjure guard enforces exactly this)
            # and no separate finalize call exists in the reload lane.
            spellbook = Spellbook(
                aetheric_frame=frame_name, configuration=configuration
            )
            self._built_stack.append(("spellbook", spellbook))
            self._live_books[spellbook_id] = spellbook
            self._report.record_built("spellbook")
            self._report.map_identity(spellbook_id, spellbook._id)
            bind_order = self._book_bind_order(spellbook_id)
            for spell_id in bind_order:
                if spell_id in self._custody_active:
                    self._bind_one_active(
                        spellbook, spell_id,
                        self._custody_active[spell_id],
                    )
            conduit = self._conjure_for_book(spellbook_id, spellbook)
            for spell_id in bind_order:
                if spell_id in self._custody_inactive:
                    self._bind_one_staged(
                        spellbook, conduit, spell_id,
                        self._custody_inactive[spell_id],
                    )
            self._enforce_selections(spellbook_id, spellbook, conduit)

    def _conjure_for_book(
            self,
            spellbook_id: str,
            spellbook: Any,
    ) -> Optional[Any]:
        """
        Conjure one recorded root conduit for a rebuilt book.

        Args:
            spellbook_id:
                Recorded book identity (conduit lookup edge).
            spellbook:
                The live rebuilt Spellbook.

        Returns:
            Optional[Any]:
                The live conduit, or None when the record holds no conduit
                twin for the book (pre-conjure world).
        """
        recorded = [
            (conduit_id, payload)
            for conduit_id, payload in self._conduits.items()
            if payload.get("spellbook_id") == spellbook_id
        ]
        if not recorded:
            return None
        conduit_id, payload = recorded[0]
        recorded_name = payload.get("conduit_name")
        if (
            self._skip_existing
            and recorded_name is not None
            and spellbook._aetheric_frame._conduit_cloud.has_conduit_name(
                str(recorded_name)
            )
        ):
            # S1 skip lane: the live world already owns this conduit name;
            # build UNNAMED so the replay completes, and report the dropped
            # identity honestly (names are never replay resolution keys -
            # links and contracts resolve through the identity map, so the
            # name drop is safe).
            recorded_name = None
            self._report.add_shortfall(
                "conduit", conduit_id, "conduit_name_taken_built_unnamed"
            )
        conduit = spellbook.conjure(
            policy=str(payload.get("policy_name", "default")),
            dynamic=bool(payload.get("dynamic", True)),
            name=recorded_name,
        )
        self._built_stack.append(("conduit", conduit))
        self._live_conduits[conduit_id] = conduit
        self._report.record_built("conduit")
        self._report.map_identity(conduit_id, conduit._id)
        return conduit

    def _book_bind_order(self, spellbook_id: str) -> List[str]:
        """
        Return one book's recorded bind order, custody-filtered.

        Args:
            spellbook_id:
                Recorded book identity.

        Returns:
            List[str]:
                Spell SHAs in recorded bind order that still hold folded
                custody under this book; custody without a bind_order slot
                appends afterwards (deterministic, sorted).
        """
        payload = self._books.get(spellbook_id, {})
        ordered = [str(entry) for entry in list(payload.get("bind_order", []))]
        owned = {
            spell_id
            for store in (self._custody_active, self._custody_inactive)
            for spell_id, crystal in store.items()
            if crystal.get("spellbook_id") == spellbook_id
        }
        sequence = [spell_id for spell_id in ordered if spell_id in owned]
        sequence.extend(sorted(owned.difference(sequence)))
        return sequence

    def _bind_one_active(
            self,
            spellbook: Any,
            spell_id: str,
            crystal: Dict[str, object],
    ) -> None:
        """
        Replay one ACTIVE bind from its custody payload.

        Args:
            spellbook:
                The live rebuilt Spellbook.
            spell_id:
                Recorded (content-stable) spell SHA.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        target = self._hydrate_target(spell_id, crystal)
        if target is None:
            return
        new_spell_id = spellbook.bind(
            spell=target,
            existence=str(crystal.get("existence_name", "unique")),
            permissions=str(crystal.get("permissions_name", "create")),
            spellframe=crystal.get("spellframe_name"),
            binding_name=crystal.get("binding_name"),
            disposal_method_names=list(
                crystal.get("disposal_method_names", [])
            ) or None,
            profile=str(crystal.get("profile_family", "general")),
        )
        self._report.record_built("spell_active")
        live_spell = spellbook.find_spell_by_id(new_spell_id)
        recorded_index_id = self._index_id_for_member(spell_id)
        if recorded_index_id is not None and live_spell is not None:
            self._report.map_identity(
                recorded_index_id, live_spell.spell_index.id
            )

    def _bind_one_staged(
            self,
            spellbook: Any,
            conduit: Optional[Any],
            spell_id: str,
            crystal: Dict[str, object],
    ) -> None:
        """
        Replay one STAGED member onto its live index anchor.

        Args:
            spellbook:
                The live rebuilt Spellbook.
            conduit:
                The live conduit hosting `bind_inactive`.
            spell_id:
                Recorded (content-stable) spell SHA.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        if conduit is None:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "staged_member_requires_conduit_none_recorded",
            )
            return
        recorded_index_id = self._index_id_for_member(spell_id)
        anchor = self._live_index_for(spellbook, recorded_index_id)
        if anchor is None:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "staged_member_anchor_index_not_rebuilt: {0}".format(
                    recorded_index_id
                ),
            )
            return
        target = self._hydrate_target(spell_id, crystal)
        if target is None:
            return
        conduit.bind_inactive(
            spell=target,
            spell_index=anchor,
            existence=str(crystal.get("existence_name", "unique")),
            permissions=str(crystal.get("permissions_name", "create")),
            spellframe=crystal.get("spellframe_name"),
            binding_name=crystal.get("binding_name"),
            profile=str(crystal.get("profile_family", "general")),
        )
        self._report.record_built("spell_staged")

    def _enforce_selections(
            self,
            spellbook_id: str,
            spellbook: Any,
            conduit: Optional[Any],
    ) -> None:
        """
        Notch rebuilt indexes whose live selection diverges from record.

        Args:
            spellbook_id:
                Recorded book identity (index owner edge).
            spellbook:
                The live rebuilt Spellbook.
            conduit:
                The live conduit hosting `notch_spell`.

        Returns:
            None.
        """
        for index_id, payload in self._indexes.items():
            if payload.get("spellbook_id") != spellbook_id:
                continue
            selected = payload.get("selected_spell_id")
            if selected is None:
                continue
            anchor = self._live_index_for(spellbook, index_id)
            if anchor is None or anchor.selected_spell_id == selected:
                continue
            if conduit is None:
                self._report.add_shortfall(
                    "spell_index", index_id,
                    "selection_requires_conduit_none_recorded",
                )
                continue
            live_spell = spellbook.find_spell_by_id(str(selected))
            if live_spell is None:
                self._report.add_shortfall(
                    "spell_index", index_id,
                    "recorded_selection_not_rebuilt: {0}".format(selected),
                )
                continue
            conduit.notch_spell(spell_index=anchor, spell=live_spell)
            self._report.record_built("selection_notch")

    def _index_id_for_member(self, spell_id: str) -> Optional[str]:
        """
        Find the recorded index holding one member SHA.

        Args:
            spell_id:
                Member spell SHA.

        Returns:
            Optional[str]:
                The recorded index ULID, or None when unrecorded.
        """
        for index_id, payload in self._indexes.items():
            if spell_id in list(payload.get("member_spell_ids", [])):
                return index_id
            if payload.get("selected_spell_id") == spell_id:
                return index_id
        return None

    def _live_index_for(
            self,
            spellbook: Any,
            recorded_index_id: Optional[str],
    ) -> Optional[Any]:
        """
        Resolve one recorded index to its live rebuilt SpellIndex.

        Args:
            spellbook:
                The live rebuilt Spellbook.
            recorded_index_id:
                Recorded index ULID (translated via the identity map).

        Returns:
            Optional[Any]:
                The live SpellIndex, or None when not rebuilt.
        """
        if recorded_index_id is None:
            return None
        live_index_id = self._report.translate(recorded_index_id)
        if live_index_id is None:
            return None
        recorded = self._indexes.get(recorded_index_id, {})
        selected = recorded.get("selected_spell_id")
        candidates = list(recorded.get("member_spell_ids", []))
        if selected is not None:
            candidates.insert(0, selected)
        for member_id in candidates:
            live_spell = spellbook.find_spell_by_id(str(member_id))
            if live_spell is not None:
                if live_spell.spell_index.id == live_index_id:
                    return live_spell.spell_index
        return None

    def _replay_links(self) -> None:
        """
        Stage 7: re-establish links from each initiator's outbound edges.

        Returns:
            None.
        """
        for conduit_id, payload in self._conduits.items():
            initiator = self._live_conduits.get(conduit_id)
            if initiator is None:
                continue
            for target_recorded_id in list(payload.get("link_targets", [])):
                target = self._live_conduits.get(str(target_recorded_id))
                if target is None:
                    self._report.add_shortfall(
                        "conduit", conduit_id,
                        "link_target_not_rebuilt: {0}".format(
                            target_recorded_id
                        ),
                    )
                    continue
                initiator.link(target)
                self._report.record_built("link")

    def _replay_clusters(self) -> None:
        """
        Stage 8: regroup recorded clusters (members; leader reported).

        Contract:
            - First cut restores cluster existence + membership through the
              frame ConduitCloud; recorded leaders and explicit share
              entries are REPORTED (auto-share on join covers the shareable
              lineages; leader election is a runtime act).

        Returns:
            None.
        """
        from melder.aether.aether import Aether

        for cluster_id, payload in self._clusters.items():
            cluster_name = payload.get("cluster_name")
            frame_name = str(payload.get("frame_name", "default"))
            if cluster_name is None:
                self._report.add_shortfall(
                    "cluster", cluster_id, "recorded_cluster_has_no_name"
                )
                continue
            frame = Aether()._ensure_frame(frame_name)
            # Cross-package seam: the cloud has no public frame accessor
            # yet; direct field access is deliberate (owned repo, visible
            # contract) - follow-up: public accessor on AethericFrame.
            cloud = frame._conduit_cloud
            if (
                self._skip_existing
                and str(cluster_name) in cloud._conduit_clusters
            ):
                # S1 skip lane: the live world already owns this cluster;
                # REUSE it - recorded members join the existing cluster
                # below, and the reuse is reported honestly (not counted
                # as built).
                self._report.add_shortfall(
                    "cluster", cluster_id, "cluster_existed_members_joined"
                )
            else:
                cloud.create_cluster(str(cluster_name))
                self._report.record_built("cluster")
            for member_recorded_id in list(
                    payload.get("member_conduit_ids", [])
            ):
                member = self._live_conduits.get(str(member_recorded_id))
                if member is None:
                    self._report.add_shortfall(
                        "cluster", cluster_id,
                        "member_not_rebuilt: {0}".format(
                            member_recorded_id
                        ),
                    )
                    continue
                cloud.add_conduit_to_cluster(member, str(cluster_name))
                self._report.record_built("cluster_member")
            if payload.get("leader_conduit_id") is not None:
                self._report.add_shortfall(
                    "cluster", cluster_id,
                    "leader_election_is_runtime_act_not_replayed",
                )
            shared_entries = list(payload.get("shared_spells", []))
            if shared_entries:
                # Auto-share on member join re-grants shareable lineages;
                # whether it reproduces EVERY recorded entry cannot be
                # verified at replay time - one honest signal per cluster.
                self._report.add_shortfall(
                    "cluster", cluster_id,
                    "shared_entries_recorded_auto_share_governs: "
                    "{0}".format(len(shared_entries)),
                )

    def _replay_contracts(self) -> None:
        """
        Stage 9 (LAST): re-grant recorded contract details.

        Contract:
            - Spell SHAs are content-stable, so detail spell ids replay
              as-recorded; conduit endpoints translate via the identity map.
            - Ward record truth: a plain detail lives in the map of the
              side that OWNS the lineage ("initiated" via the link-time
              bulk grant, "received" via the borrow verb, which files
              under the owner per the ward eligibility check). Either way
              the PEER is the borrower, and the live re-grant verb is
              borrower-called naming the owner - so EVERY detail replays
              as peer.add_spell_to_contract(conduit=owning_side) inside a
              borrower-opened link-transaction window.
            - Replayed details re-record as "received" regardless of the
              original label; the relationship is identical, the label
              drift is a documented first-cut tolerance.
            - Index subscriptions are REPORTED in this cut (their heads
              re-form when index links re-grant through the live notch
              fan-out; explicit index re-subscription lands with the
              chain-integrity lane).

        Returns:
            None.
        """
        for contract_id, payload in self._contracts.items():
            side_a = self._live_conduits.get(
                str(payload.get("conduit_a_id"))
            )
            side_b = self._live_conduits.get(
                str(payload.get("conduit_b_id"))
            )
            if side_a is None or side_b is None:
                self._report.add_shortfall(
                    "contract", contract_id,
                    "endpoint_not_rebuilt",
                )
                continue
            for granter, details_key in (
                    (side_a, "details_a"),
                    (side_b, "details_b"),
            ):
                for detail in list(payload.get(details_key, [])):
                    # The map holder OWNS the lineage (both detail labels);
                    # the peer borrowed it. The live verb is borrower-
                    # called naming the owner (the ward eligibility check
                    # demands the `conduit` argument own the spell).
                    borrower = side_b if granter is side_a else side_a
                    with borrower.transaction(
                            "link", conduits=[borrower, granter]
                    ):
                        borrower.add_spell_to_contract(
                            spell_id=str(detail.get("spell_id")),
                            conduit=granter,
                            permissions=str(
                                detail.get("permissions", "create")
                            ).lower(),
                        )
                    self._report.record_built("contract_detail")
            for subscriptions_key in ("index_details_a", "index_details_b"):
                for subscription in list(
                        payload.get(subscriptions_key, [])
                ):
                    self._report.add_shortfall(
                        "contract", contract_id,
                        "index_subscription_reported_not_replayed: "
                        "{0}".format(subscription.get("index_id")),
                    )

    def _hydrate_target(
            self,
            spell_id: str,
            crystal: Dict[str, object],
    ) -> Optional[Any]:
        """
        Rebuild one bind target from its recorded module coordinates.

        Contract:
            - Only "hydratable" custody (class/function roots) imports;
              replay_required and synthetic roots become shortfalls.
            - Import/attr failures become shortfalls, never partial binds.

        Args:
            spell_id:
                Recorded spell SHA (shortfall key).
            crystal:
                The folded custody payload.

        Returns:
            Optional[Any]:
                The live class/function target, or None (shortfall filed).
        """
        if str(crystal.get("rebindability")) != "hydratable":
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "replay_required_target_kind: {0}".format(
                    crystal.get("root_target_kind")
                ),
            )
            return None
        if str(crystal.get("root_module_kind")) == "synthetic_module":
            # Loader chain M3: rebuild the recorded synthetic module world
            # first, then hydrate through the normal import lane below.
            if not self._rebuild_synthetic_world(spell_id, crystal):
                return None
        module_name = str(crystal.get("root_module_name"))
        qualname = str(crystal.get("root_target_qualname"))
        try:
            module = importlib.import_module(module_name)
            target: Any = module
            for part in qualname.split("."):
                target = getattr(target, part)
        except Exception as error:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "hydration_failed ({0}.{1}): {2}".format(
                    module_name, qualname, error
                ),
            )
            return None
        return target

    def _rebuild_synthetic_world(
            self,
            spell_id: str,
            crystal: Dict[str, object],
    ) -> bool:
        """
        Rebuild one custody crystal's recorded synthetic modules (M3).

        Purpose:
            Synthetic modules have no files - their recorded source IS the
            truth. This lane reconstructs each recorded module through the
            SyntheticModule lifecycle (construct -> register in the import
            registry -> publish to sys.modules -> execute source) so the
            normal importlib hydration lane can then resolve the bind
            target exactly like a file-backed module.

        Contract:
            - Parents build before children (module-name dot depth order).
            - Modules already present in sys.modules are SKIPPED
              (idempotent across custody crystals sharing dependencies).
            - Every module this run builds rides _built_stack for the
              all-or-nothing teardown (SyntheticModule.cleanup unpublishes
              and unregisters).
            - Pre-M3 payloads (no synthetic_module_sources key) keep the
              historic honest shortfall.

        Args:
            spell_id:
                Custody identity (shortfall anchor).
            crystal:
                The folded custody payload.

        Returns:
            bool: True when the module world is ready for import.
        """
        from melder.crystallizer.synthetic_module import SyntheticModule

        sources = dict(crystal.get("synthetic_module_sources", {}))
        if not sources:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "synthetic_root_recorded_without_sources_pre_m3",
            )
            return False
        for module_name in sorted(
                sources.keys(), key=lambda name: (name.count("."), name)
        ):
            if module_name in sys.modules:
                continue
            payload = dict(sources[module_name])
            try:
                parent_name = payload.get("parent_name")
                module = SyntheticModule(
                    module_name=module_name,
                    spell_crystal_id=str(
                        payload.get("spell_crystal_id", spell_id)
                    ),
                    source_text=str(payload.get("source_text", "")),
                    source_sha256=str(payload.get("source_sha256", "")),
                    binding_signature=str(
                        payload.get("binding_signature", "")
                    ),
                    parent_name=(
                        str(parent_name) if parent_name else None
                    ),
                    is_package=bool(payload.get("is_package", False)),
                )
                module.register_in_import_registry()
                module.publish_to_sys_modules()
                module.execute_source()
            except Exception as error:
                self._report.add_shortfall(
                    "spell_crystal", spell_id,
                    "synthetic_module_rebuild_failed ({0}): {1}".format(
                        module_name, error
                    ),
                )
                return False
            self._built_stack.append(("synthetic_module", module))
            self._report.record_built("synthetic_module")
        return True

    def _teardown_built(self) -> None:
        """
        Tear down every unit this run built, newest first.

        Contract:
            - Best-effort per unit (teardown must reach the bottom of the
              stack even when one cleanup raises); the run's failure is the
              caller-visible error, not teardown noise.

        Returns:
            None.
        """
        while self._built_stack:
            _kind, unit = self._built_stack.pop()
            try:
                if not unit.cleaned:
                    unit.cleanup()
            except Exception:
                # Best-effort by contract: the original stage error is the
                # signal; teardown noise must not mask it.
                continue
        self._live_books.clear()
        self._live_conduits.clear()
