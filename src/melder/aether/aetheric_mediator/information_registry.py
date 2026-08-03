"""
The reporting surface for the mediator plane.

Dependency rule: standard library plus `melder.utilities` only.

Mirrors the reporting half of `DevopsInformationRegistry`, which is two
mechanisms rather than one:
  1. FACT BASELINES - what changed, when, and who reported it, so a reader can
     check a baseline instead of re-deriving state that has not moved.
  2. LIVE ACTIVITY INDEXES - what is in flight right now, along one axis.

Deliberately NOT ported: the DevOps relational mirrors (spellbook<->conduit
ownership, conduit links, cluster membership). Relational truth belongs to each
subsystem; duplicating it here would create a second place to be wrong.
"""

import threading
import time
from collections.abc import Mapping
from typing import Dict, List, Optional, Tuple

from melder.aether.aetheric_mediator.participation import ParticipationState
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.utilities.general_base.cleanable import Cleanable


class FactRecord(Cleanable):
    """
    One "this region was last changed by this reporter at this time" baseline.

    Contract:
        Immutable. Replaced wholesale on each report rather than mutated, so a
        reader holding one never observes it change underneath.

    Lifecycle / Cleanup:
        `Cleanable`, with TWO owner-is-finished moments, both inside the
        registry that owns it:

        REPLACE-ON-EMIT. `report_fact` REPLACES the baseline for a region, and
        the displaced record is cleaned by the thread doing the replacing. This
        is the crystallizer's own recorded rule - "replace-on-emit: a displaced
        twin is CLEANED; runtime holders must fetch fresh per use" - applied to
        the one place in this plane with the same shape. A region that is
        written on every commit would otherwise leave one dead baseline per
        commit for a collector to find later.

        TEARDOWN. `InformationRegistry.cleanup` walks the remaining baselines
        and cleans them before dropping the map.

        Readers are never handed the record itself - `get_fact` and `describe`
        return detached dicts - so cleaning a displaced baseline cannot pull
        state out from under a caller.

    Threading:
        Immutable after construction; no lock. Every mutation of the map that
        holds these, and every cleanup of one, happens under the registry's
        `RLock`.

    Registration:
        MELDER KERNEL - guarded. Built by the registry; never user-built.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable freshness baseline for one region.
        Cleanable; cleaned when displaced or at registry teardown.
    """

    __slots__ = Cleanable.__slots__ + [
        "fact_family", "region", "reporter", "reported_at",
    ]

    def __init__(
            self,
            *,
            fact_family: str,
            region: str,
            reporter: str,
            reported_at: float,
    ) -> None:
        """
        Build one immutable fact baseline.

        Args:
            fact_family: The transaction type that produced the change.
            region: The scope key the change applies to.
            reporter: The request id that reported it.
            reported_at: Unix timestamp of the report.

        Returns:
            None.
        """
        super().__init__()
        self.fact_family: str = fact_family
        self.region: str = region
        self.reporter: str = reporter
        self.reported_at: float = reported_at

    def cleanup(self) -> None:
        """
        Idempotently drop this baseline's fields.

        Contract:
            Called by the owning `InformationRegistry` - when this record is
            displaced by a newer baseline for the same region, and at registry
            teardown. Idempotent, so the teardown sweep may call it without
            first checking whether a replace already did.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.fact_family
        del self.region
        del self.reporter
        del self.reported_at

    def age_seconds(self, now: Optional[float] = None) -> float:
        """
        Return how long ago this baseline was stamped.

        Args:
            now: Optional current time; defaults to the wall clock.

        Returns:
            float: Age in seconds, never negative.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        current = time.time() if now is None else now
        return max(0.0, current - self.reported_at)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached value-only view of this baseline.

        Returns:
            Dict[str, object]: Family, region, reporter, timestamp, age.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return {
            "fact_family": self.fact_family,
            "region": self.region,
            "reporter": self.reporter,
            "reported_at": self.reported_at,
            "age_seconds": self.age_seconds(),
        }


class InformationRegistry(Cleanable):
    """
    Fact baselines and live activity indexes for the plane.

    Purpose:
        Answer two questions cheaply and without touching live subsystem
        state: "what is happening right now" and "has this region changed
        since I last looked".

    Contract:
        - CALLER-PAID BY DESIGN. Nothing in the runtime invokes reporting
          automatically. A reader asks; the plane answers. This matches the
          DevOps information layer and keeps the admission hot path free of
          reporting cost.
        - RESULTS ARE DETACHED. Every read returns values and strings, never
          live `StagedTransaction`, `Identity`, or session references. That is
          what makes a result safe to log, ship, or retain after the
          transaction it describes has ended.
        - ONE BASELINE PER REGION. `report_fact` REPLACES rather than appends.
          The registry answers "when did this last change", not "everything
          that ever happened" - an unbounded history here would be a memory
          leak on the commit path.
        - ACTIVITY IS INDEXED THREE WAYS - by scope, by submitter, and by
          transaction type - because those are the three axes someone
          diagnosing a stall actually asks along.
        - PARTICIPATION IS A STATE, NOT A PRESENCE. The participant store
          records a `ParticipationState` per subsystem, and exactly one member
          of that vocabulary means "emit". A bare set of live names could not
          distinguish a subsystem nobody wired in from one that was switched
          off deliberately, and those need different fixes.

    Owned State:
        `_facts` (region -> FactRecord), `_active` (request id -> staged),
        `_participants` (subsystem -> state row), and one lock. No subsystem
        references - names, states, values and timestamps only.

    Threading:
        One `RLock`. Reads copy under the lock and return detached values, so
        a caller never holds a reference into live registry state.

    Registration:
        MELDER KERNEL - guarded. Constructed by the plane; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Plane reporting - fact baselines plus live activity
        indexes by scope, submitter, and type. Caller-paid, detached results.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock", "_facts", "_active", "_participants",
    ]

    def __init__(self) -> None:
        """
        Build one empty registry.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._facts: Dict[str, FactRecord] = {}
        self._active: Dict[str, StagedTransaction] = {}
        # PARTICIPANT STORE. Owner constraint 6 gates participation on
        # activation: a subsystem takes part ONLY when enabled and active, and
        # emits its basic conditions at that edge. This is the ONE place that
        # is recorded - `Mediator`'s roster verbs delegate here rather than
        # keeping a second map, because two stores of the same fact is two
        # places to be wrong and the registry docstring above forbids exactly
        # that for relational truth.
        #
        # Each row carries a `ParticipationState` rather than mere presence, so
        # "never heard of it", "known but not started", "running", and "ran and
        # stopped" stay four distinct answers. Value-only by the same law the
        # rest of this registry follows - a live subsystem reference here would
        # defeat `describe()` and outlive the object it describes.
        self._participants: Dict[str, Dict[str, object]] = {}

    def cleanup(self) -> None:
        """
        Idempotently drop all baselines and activity.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            if self._cleaned:
                return
            self._cleaned = True
            # The registry OWNS its baselines, so it cleans them. It only
            # BORROWS the staged records in `_active` - those belong to the
            # sessions and are cleaned there - so `_active` is cleared, never
            # walked. Getting that asymmetry backwards would tear down another
            # owner's records mid-teardown.
            for record in self._facts.values():
                record.cleanup()
            self._facts.clear()
            self._active.clear()
            self._participants.clear()
        del self._facts
        del self._active
        del self._participants
        del self._lock

    def report_fact(
            self,
            *,
            fact_family: str,
            region: str,
            reporter: str,
    ) -> None:
        """
        Stamp the freshness baseline for one region.

        Contract:
            REPLACES any existing baseline for the region. Called from
            `apply_commit_delta` while claims are still held, which is what
            makes the stamp race-free against overlapping writers.

        Args:
            fact_family: The transaction type producing the change.
            region: The scope key that changed.
            reporter: The request id reporting it.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            # REPLACE-ON-EMIT: the displaced baseline is cleaned by the thread
            # that displaces it. A hot region is re-stamped on every commit, so
            # without this each commit would leave one dead record behind.
            # Safe under the lock, and safe against readers: nobody is ever
            # handed the record itself - `get_fact` and `describe` return
            # detached dicts built while this lock is held.
            displaced = self._facts.get(region)
            self._facts[region] = FactRecord(
                fact_family=fact_family,
                region=region,
                reporter=reporter,
                reported_at=time.time(),
            )
            if displaced is not None:
                displaced.cleanup()

    def get_fact(self, region: str) -> Optional[Dict[str, object]]:
        """
        Return the detached baseline for one region, if any.

        Args:
            region: The scope key to look up.

        Returns:
            Optional[Dict[str, object]]: Detached baseline, or None when the
                region has no baseline (never reported, or cold).

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            record = self._facts.get(region)
            return None if record is None else record.describe()

    def stale_regions(
            self,
            *,
            regions: Tuple[str, ...],
            max_age_seconds: float,
    ) -> Tuple[str, ...]:
        """
        Return which of `regions` are stale or have no baseline at all.

        Contract:
            This is the control-plane economy in one call: check the baseline
            first, re-derive only what is cold or stale. A region with NO
            baseline counts as stale - never-reported and long-ago-reported
            are equally untrustworthy to a reader, and treating an absent
            baseline as fresh would be the dangerous direction.

        Args:
            regions: The scope keys to test.
            max_age_seconds: Age beyond which a baseline is stale.

        Returns:
            Tuple[str, ...]: The stale or unknown regions, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        now = time.time()
        stale: List[str] = []
        with self._lock:
            for region in regions:
                record = self._facts.get(region)
                if record is None or record.age_seconds(now) > max_age_seconds:
                    stale.append(region)
        return tuple(sorted(stale))

    @staticmethod
    def _require_name(subsystem_name: str) -> None:
        """
        Internal

        Reject a subsystem name that could not match a scope key.

        Contract:
            Applied by EVERY participant verb, including the read verbs. A
            blank name silently reads as "not participating", which is the
            wrong answer to give a caller who is about to skip work on the
            strength of it.

        Args:
            subsystem_name: The name to validate.

        Returns:
            None.

        Raises:
            ValueError: If the name is not a non-empty, non-blank string.
        """
        if not isinstance(subsystem_name, str) or not subsystem_name.strip():
            raise ValueError(
                "subsystem_name must be a non-empty, non-blank string; it must "
                "match the name used for ScopeKey.subsystem(...)."
            )

    @staticmethod
    def _freeze_conditions(
            conditions: Mapping[str, object],
    ) -> Dict[str, object]:
        """
        Internal

        Copy and value-check one condition mapping.

        Contract:
            COPIES rather than aliases. The caller's mapping may be mutable and
            may outlive this call, so a stored reference would let a subsystem
            silently rewrite what the plane believes about it after the fact.

            Refuses non-value entries for the same reason `MetadataPolicy`
            does: a live object here would defeat `describe()` and would pin
            the subsystem it describes, which is exactly the reference the
            plane must never hold.

        Args:
            conditions: The announced conditions.

        Returns:
            Dict[str, object]: A detached, value-only copy.

        Raises:
            TypeError: If any key is not a string, or any value is not
                value-only.
        """
        frozen: Dict[str, object] = {}
        for key, value in dict(conditions).items():
            if not isinstance(key, str):
                raise TypeError("condition keys must be strings.")
            if value is not None and not isinstance(
                    value, (bool, int, float, str)
            ):
                raise TypeError(
                    "condition {0!r} is not value-only; the participant store "
                    "holds facts, not live objects.".format(key)
                )
            frozen[key] = value
        return frozen

    def announce_participant(self, subsystem_name: str) -> bool:
        """
        Record that one subsystem exists and may submit transactions.

        Purpose:
            The roster arrival. Let the plane answer "which subsystems exist"
            without ever importing, referencing, or reaching into any of them.

        Contract:
            - THE SUBSYSTEM ANNOUNCES ITSELF; THE PLANE NEVER REACHES OUT.
              This direction is what keeps epic constraint 4 intact. If the
              plane had to discover its subsystems it would need to import
              `melder.aether`, and the whole isolation property collapses.
            - LANDS AT `REGISTERED`, NOT `ENABLED`. Announcing is a roster
              arrival, not an activation - the subsystem has said it exists,
              not that it is running. Treating arrival as activation is the
              specific mistake this vocabulary exists to prevent: it would emit
              for a subsystem that has not started.
            - IDEMPOTENT, AND RE-ANNOUNCING NEVER MOVES THE STATE. Returns
              False on a repeat and leaves an existing row's state and
              conditions untouched. A subsystem that re-announces while ENABLED
              must not be knocked back to REGISTERED; that would silence a
              running subsystem.
            - THIS IS NOT ADMISSION. Announcing grants no claim and gates
              nothing. It is a roster, not a permission.

        Args:
            subsystem_name:
                Stable lowercase subsystem name, matching the name used to
                build its `ScopeKey.subsystem(...)` key.

        Returns:
            bool: True on first arrival, False when already known.

        Raises:
            RuntimeError: If the registry has been cleaned.
            ValueError: If `subsystem_name` is empty or whitespace-only.
        """
        self.check_cleaned()
        self._require_name(subsystem_name)
        now = time.time()
        with self._lock:
            existing = self._participants.get(subsystem_name)
            if existing is not None:
                existing["announced_at"] = now
                return False
            self._participants[subsystem_name] = {
                "subsystem_name": subsystem_name,
                "state": ParticipationState.REGISTERED,
                "conditions": {},
                "reporter": None,
                "announced_at": now,
                "state_changed_at": now,
            }
            return True

    def forget_participant(self, subsystem_name: str) -> bool:
        """
        Drop one subsystem from the roster entirely.

        Contract:
            - THIS IS NOT `SUBSYSTEM_DISABLE`, and the difference is the reason
              both exist. Disabling moves a subsystem to `DISABLED` and KEEPS
              its row, because "it ran and stopped" is a fact worth reporting.
              Forgetting removes the row, so the plane goes back to never
              having heard of it. Use this for teardown, not for deactivation.
            - Idempotent, so a teardown path may call it unconditionally.
            - Does NOT release any claims that subsystem holds. Claims belong
              to transactions and are released by finalising those, never by
              roster changes.

        Args:
            subsystem_name: The subsystem to forget.

        Returns:
            bool: True when a row was removed, False when none was present.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._participants.pop(subsystem_name, None) is not None

    def set_participation(
            self,
            *,
            subsystem_name: str,
            state: ParticipationState,
            reporter: str,
            conditions: Optional[Mapping[str, object]] = None,
    ) -> None:
        """
        Move one subsystem to a participation state, optionally with conditions.

        Purpose:
            Be the single write the subsystem lifecycle edges share, so enable,
            disable and configure differ in the VALUE they write rather than in
            the mechanics of writing it.

        Contract:
            - ATOMIC. State and conditions move together under one lock
              acquisition. Two verbs would leave a window in which a reader
              sees the new state beside the old conditions, and the whole point
              of gating emission on state is that the pair is trustworthy.
            - CREATES THE ROW IF ABSENT. An enable arriving for a subsystem
              that never announced itself is recorded rather than refused: the
              roster is not wired into the subsystems today, and making the
              activation edge depend on wiring that does not exist would mean
              silently losing the transition.
            - `conditions=None` MEANS "THIS EDGE ANNOUNCED NOTHING" and leaves
              existing conditions in place. An empty mapping means "this edge
              announced nothing IS the announcement" and clears them. That
              distinction is load-bearing: it is what lets a CONFIGURE record
              settings and a later ENABLE flip the state without wiping them.
            - CONDITIONS ON A NON-EMITTING ROW ARE LAST-KNOWN, NOT CURRENT.
              They are deliberately retained through a disable, because the
              state already tells a reader not to act on them and "what was it
              running with when it stopped" is the first question asked after a
              subsystem goes quiet. Retention is safe here ONLY because the
              state guards it; in a store that recorded presence alone, keeping
              them would invite acting on dead policy.
            - The plane NEVER calls this itself. A subsystem moves its own
              state through a transaction; the plane does not reach out and ask.

        Args:
            subsystem_name: The subsystem whose state is moving.
            state: The state to move to.
            reporter: The request id of the transaction moving it.
            conditions: Announced conditions, or None to keep existing ones.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
            ValueError: If `subsystem_name` or `reporter` is not a non-empty
                string.
            TypeError: If `state` is not a `ParticipationState`, or any
                condition value is not value-only.
        """
        self.check_cleaned()
        self._require_name(subsystem_name)
        if not isinstance(reporter, str) or not reporter:
            raise ValueError("reporter must be a non-empty string.")
        if not isinstance(state, ParticipationState):
            raise TypeError(
                "state must be a ParticipationState member; the participation "
                "vocabulary is closed. Got {0!r}.".format(state)
            )
        frozen = (
            None if conditions is None else self._freeze_conditions(conditions)
        )
        now = time.time()
        with self._lock:
            row = self._participants.get(subsystem_name)
            if row is None:
                row = {
                    "subsystem_name": subsystem_name,
                    "conditions": {},
                    "announced_at": now,
                }
                self._participants[subsystem_name] = row
            if frozen is not None:
                row["conditions"] = frozen
            row["state"] = state
            row["reporter"] = reporter
            row["state_changed_at"] = now

    def record_conditions(
            self,
            *,
            subsystem_name: str,
            conditions: Mapping[str, object],
            reporter: str,
    ) -> ParticipationState:
        """
        Record one subsystem's conditions without switching it on.

        Purpose:
            Serve the CONFIGURE edge, where a subsystem declares how it would
            run before - or independently of - actually running.

        Contract:
            - PROMOTES A NON-EMITTING ROW TO `CONFIGURED`. A subsystem that was
              REGISTERED, CONFIGURED or DISABLED lands on CONFIGURED, because
              declaring conditions is exactly the difference between "we know
              the name" and "we know how it would run".
            - LEAVES AN `ENABLED` ROW ENABLED. Reconfiguring a running
              subsystem updates what it is running with; it does not turn it
              off, and writing CONFIGURED over ENABLED would claim it did. That
              is the one transition this verb refuses to make, and it is
              enforced HERE rather than in the calling strategy so there is one
              place to be right about it.
            - Creates the row at `CONFIGURED` when the subsystem is unknown,
              for the same reason `set_participation` does.
            - Returns the RESULTING state, so a caller can see which of the two
              branches it took without a second read.

        Args:
            subsystem_name: The subsystem declaring conditions.
            conditions: Its basic conditions.
            reporter: The request id of the configuring transaction.

        Returns:
            ParticipationState: The state the row is in after the write.

        Raises:
            RuntimeError: If the registry has been cleaned.
            ValueError: If `subsystem_name` or `reporter` is not a non-empty
                string.
            TypeError: If any condition value is not value-only.
        """
        self.check_cleaned()
        self._require_name(subsystem_name)
        if not isinstance(reporter, str) or not reporter:
            raise ValueError("reporter must be a non-empty string.")
        frozen = self._freeze_conditions(conditions)
        now = time.time()
        with self._lock:
            row = self._participants.get(subsystem_name)
            if row is None:
                row = {
                    "subsystem_name": subsystem_name,
                    "announced_at": now,
                }
                self._participants[subsystem_name] = row
            current = row.get("state")
            resulting = (
                ParticipationState.ENABLED
                if current is ParticipationState.ENABLED
                else ParticipationState.CONFIGURED
            )
            row["conditions"] = frozen
            row["state"] = resulting
            row["reporter"] = reporter
            row["state_changed_at"] = now
            return resulting

    def participation_state(
            self,
            subsystem_name: str,
    ) -> Optional[ParticipationState]:
        """
        Return one subsystem's participation state, if the plane knows it.

        Contract:
            `None` means the plane has NEVER HEARD of this subsystem, which is
            a different fact from `DISABLED`. Collapsing the two would hide the
            most common real failure - a subsystem that was never wired in at
            all - behind one that looks deliberate.

        Args:
            subsystem_name: The subsystem being asked about.

        Returns:
            Optional[ParticipationState]: The current state, or None when
                unknown.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            row = self._participants.get(subsystem_name)
            if row is None:
                return None
            return row["state"]

    def is_participating(self, subsystem_name: str) -> bool:
        """
        Report whether one subsystem is enabled and active. THE EMISSION GATE.

        Contract:
            This is the question owner constraint 6 answers: emit for a
            subsystem ONLY when it is enabled and active, otherwise do not
            care. True for `ENABLED` alone - a REGISTERED, CONFIGURED,
            DISABLED, or unknown subsystem all read False, because none of them
            is running.

            Callers gating work on participation must use THIS rather than
            testing whether the plane knows the name. Knowing the name is
            `participation_state(...) is not None`, and the gap between the two
            is every subsystem that exists but is not running.

        Args:
            subsystem_name: The subsystem being asked about.

        Returns:
            bool: True only when the subsystem is enabled and active.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            row = self._participants.get(subsystem_name)
            if row is None:
                return False
            state = row["state"]
            return state.emits

    def participant_conditions(
            self,
            subsystem_name: str,
    ) -> Optional[Dict[str, object]]:
        """
        Return the basic conditions one subsystem last announced.

        Contract:
            - DETACHED. Returns a fresh copy, so a caller cannot edit what the
              plane believes about a subsystem by mutating the return.
            - LAST-KNOWN, NOT NECESSARILY CURRENT. A row that is not ENABLED
              still carries the conditions it announced, which is what makes
              "what was it running with when it stopped" answerable. Check
              `is_participating(...)` before acting on these as live settings.
            - `None` means the subsystem is unknown. A known subsystem that has
              announced nothing returns an EMPTY dict, and those are different
              answers.

        Args:
            subsystem_name: The subsystem being asked about.

        Returns:
            Optional[Dict[str, object]]: A copy of the conditions, or None when
                the subsystem is unknown.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            row = self._participants.get(subsystem_name)
            if row is None:
                return None
            return dict(row["conditions"])

    def known_subsystems(self) -> Tuple[str, ...]:
        """
        Return every subsystem the plane has heard of, sorted, in any state.

        Contract:
            This is the ROSTER, not the emission set. It includes REGISTERED,
            CONFIGURED and DISABLED subsystems. For "who is actually running",
            use `participants_in_state(ParticipationState.ENABLED)`.

        Returns:
            Tuple[str, ...]: Known subsystem names.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(self._participants))

    def participants_in_state(
            self,
            state: ParticipationState,
    ) -> Tuple[str, ...]:
        """
        Return every subsystem currently in one participation state, sorted.

        Purpose:
            Answer the diagnostic question directly - "which subsystems are
            sitting at CONFIGURED and never got switched on" is one call rather
            than a roster walk with a per-name lookup.

        Args:
            state: The state to filter by.

        Returns:
            Tuple[str, ...]: Subsystem names in that state.

        Raises:
            RuntimeError: If the registry has been cleaned.
            TypeError: If `state` is not a `ParticipationState`.
        """
        self.check_cleaned()
        if not isinstance(state, ParticipationState):
            raise TypeError(
                "state must be a ParticipationState member. Got {0!r}.".format(
                    state
                )
            )
        with self._lock:
            return tuple(sorted(
                name
                for name, row in self._participants.items()
                if row["state"] is state
            ))

    def _render_participant_locked(
            self,
            subsystem_name: str,
    ) -> Dict[str, object]:
        """
        Internal

        Render one participant row as detached values. CALLER HOLDS THE LOCK.

        Contract:
            Assumes `self._lock` is HELD and the name is present. Both
            `describe_participants` and `describe` render rows, and having two
            copies of the field list is how one of them ends up missing a field
            the other has.

            `state` is rendered as its string value rather than the member, so
            the result survives logging and serialisation without special
            casing. `emits` is rendered ALONGSIDE it rather than left for the
            reader to derive - a consumer reading a log line should not have to
            know which state is the emitting one.

        Args:
            subsystem_name: The row to render.

        Returns:
            Dict[str, object]: The detached row.
        """
        row = self._participants[subsystem_name]
        state = row["state"]
        return {
            "subsystem_name": subsystem_name,
            "state": state.value,
            "emits": state.emits,
            "conditions": dict(row["conditions"]),
            "reporter": row["reporter"],
            "announced_at": row["announced_at"],
            "state_changed_at": row["state_changed_at"],
        }

    def describe_participants(self) -> Tuple[Dict[str, object], ...]:
        """
        Return a detached row per known subsystem, sorted by name.

        Contract:
            DETACHED and value-only, like every other read here. Includes every
            state, not only the emitting ones - a roster that hid its silent
            members would be useless for the question it is usually asked to
            settle, which is why nothing is happening.

        Returns:
            Tuple[Dict[str, object], ...]: One row per known subsystem, each
                carrying name, state, whether it emits, its last-known
                conditions, the reporter that last moved it, and both
                timestamps.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(
                self._render_participant_locked(name)
                for name in sorted(self._participants)
            )

    def register_activity(self, staged: StagedTransaction) -> None:
        """
        Record one transaction as live.

        Args:
            staged: The admitted transaction.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._active[staged.request_id] = staged

    def unregister_activity(self, request_id: str) -> None:
        """
        Drop one transaction from the live set.

        Contract:
            Idempotent, so a `finally` may call it without checking.

        Args:
            request_id: The transaction to drop.

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._active.pop(request_id, None)

    def activity_by_scope(self, scope_key: str) -> Tuple[str, ...]:
        """
        Return live request ids touching one scope key.

        Args:
            scope_key: The scope to query.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if scope_key in staged.granted_scopes
            ))

    def activity_by_submitter(
            self,
            *,
            submitter_kind: str,
            submitter_id: str,
    ) -> Tuple[str, ...]:
        """
        Return live request ids submitted by one identity.

        Args:
            submitter_kind: The submitter's family.
            submitter_id: The submitter's id within that family.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if staged.submitter_kind == submitter_kind
                and staged.submitter_id == submitter_id
            ))

    def activity_by_type(self, transaction_type: str) -> Tuple[str, ...]:
        """
        Return live request ids of one transaction type.

        Args:
            transaction_type: The type value to query.

        Returns:
            Tuple[str, ...]: Live request ids, sorted.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(
                staged.request_id
                for staged in self._active.values()
                if staged.transaction_type.value == transaction_type
            ))

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of live activity, baselines, and the roster.

        Contract:
            Reports "who exists and in what state" beside "what is happening",
            because a stall is as often a subsystem that never reached ENABLED
            as it is a transaction that will not finish. `emitting_count` is
            broken out because it is the number an operator actually wants -
            the roster length includes subsystems that are doing nothing by
            design.

        Returns:
            Dict[str, object]: Counts plus rendered activity, baselines, and
                participant rows.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "active_count": len(self._active),
                "fact_count": len(self._facts),
                "participant_count": len(self._participants),
                "emitting_count": sum(
                    1
                    for row in self._participants.values()
                    if row["state"].emits
                ),
                "participants": [
                    self._render_participant_locked(name)
                    for name in sorted(self._participants)
                ],
                "active": [
                    staged.describe()
                    for staged in sorted(
                        self._active.values(),
                        key=lambda item: item.admitted_at,
                    )
                ],
                "facts": [
                    self._facts[region].describe()
                    for region in sorted(self._facts.keys())
                ],
            }
