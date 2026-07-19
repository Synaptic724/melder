import threading
from typing import Dict, List, Optional, ClassVar

from melder.mutation_research.research_set.transition_entry import (
    TransitionAct,
    TransitionEntry,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ResearchJournal(Cleanable):
    """
    Set-level monotonic append-only log of world-entry events.

    Purpose:
        Own the single forward-only event stream for one `ResearchSet`. Every
        organizational or world-entry act across every lane lands here in
        strict sequence order, so "how did the network come to look like
        this" is always answerable without replaying lane internals.

    Contract:
        - Append-only: entries are never edited, reordered, or removed while
          the journal lives (cleanup releases them wholesale).
        - Sequences are minted monotonically starting at 1; there are no gaps
          and no reuse.
        - The journal SURVIVES network restore: organization snapshots exclude
          it by design, so history is never rewound by recovery.
        - Reads return detached lists; callers never receive the live store.

    Threading:
        Instance `RLock` serializes minting and reads; entries themselves are
        immutable and safe to share.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` cleans owned entries
        then deletes owned fields; idempotent; lock released last.

    THE JOURNAL IS NOT SNAPSHOTTED, AND THAT IS THE POINT:
        `NetworkVersioner` snapshots the ORGANIZATION - which lane holds what,
        what is anchored, what is archived - and deliberately excludes this log.
        So `restore_network` rewinds where things are, and never rewinds what
        happened.

        The result is a system where organization is recoverable but history is
        not editable. A restore is itself journalled, carrying the snapshot
        address it restored from, so the record shows the rewind rather than
        hiding it.

    Registration:
        MELDER KERNEL - guarded. The event stream belongs to the record; users
        read it through `ResearchSet` and room commands.

    Subsystem Context:
        One of the four bookkeeping structures a `ResearchSet` owns, beside
        `ResidenceRegistry` (where identities live), `NetworkVersioner` (past
        organization states), and the lanes. Journal entries are
        `TransitionEntry` values carrying a `TransitionAct` - and notably there
        are no rollback acts in that vocabulary, which is the same
        forward-only conviction expressed in the enum.

    System Context:
        Answers "how did the network come to look like this" without replaying
        lane internals. The twin that ships to the crystallizer carries a
        BOUNDED window of this journal rather than all of it - full history
        rides the checkpoint sequence instead - so a durable snapshot never
        grows without limit while the live log stays complete.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_entries",
        "_next_sequence",
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty journal with sequence minting at 1.
        """
        super().__init__()
        self._entries: List[TransitionEntry] = []
        self._next_sequence: int = 1
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Clean owned entries, release fields, and mark the journal cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for entry in self._entries:
                try:
                    entry.cleanup()
                except Exception:
                    pass
            self._entries.clear()
            del self._entries
            del self._next_sequence
        del self._lock

    def record(
            self,
            act: TransitionAct,
            lane_id: str,
            *,
            from_spell_id: Optional[str] = None,
            to_spell_id: Optional[str] = None,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> TransitionEntry:
        """
        Mint and append one forward-only journal event.

        Args:
            act:
                World-entry act to record.
            lane_id:
                Subject lane id (or set id for network-scope acts).
            from_spell_id:
                Optional origin identity.
            to_spell_id:
                Optional destination identity.
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp.
            reason:
                Optional reason line.
            metadata:
                Optional value-typed annotations.

        Returns:
            TransitionEntry:
                The appended immutable event.
        """
        self.check_cleaned()
        with self._lock:
            entry = TransitionEntry(
                self._next_sequence,
                act,
                lane_id,
                from_spell_id=from_spell_id,
                to_spell_id=to_spell_id,
                actor=actor,
                campaign=campaign,
                reason=reason,
                metadata=metadata,
            )
            self._next_sequence += 1
            self._entries.append(entry)
            return entry

    @property
    def entry_count(self) -> int:
        """
        Return the number of recorded events.

        Returns:
            int:
                Current entry count.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._entries)

    @property
    def latest_sequence(self) -> int:
        """
        Return the highest minted sequence (0 when empty).

        Returns:
            int:
                Last minted sequence or 0.
        """
        self.check_cleaned()
        with self._lock:
            return self._next_sequence - 1

    def entries(self) -> List[TransitionEntry]:
        """
        Return a detached list of every recorded event in order.

        Returns:
            List[TransitionEntry]:
                Detached entry list (entries themselves are immutable).
        """
        self.check_cleaned()
        with self._lock:
            return list(self._entries)

    def entries_for_lane(self, lane_id: str) -> List[TransitionEntry]:
        """
        Return every event whose subject is the given lane, in order.

        Args:
            lane_id:
                Subject lane id to filter on.

        Returns:
            List[TransitionEntry]:
                Detached filtered entry list.
        """
        self.check_cleaned()
        with self._lock:
            return [
                entry for entry in self._entries if entry.lane_id == lane_id
            ]

    def entries_for_spell_id(self, spell_id: str) -> List[TransitionEntry]:
        """
        Return every event touching the given identity on either end.

        Args:
            spell_id:
                Identity to filter on (`from_spell_id` or `to_spell_id`).

        Returns:
            List[TransitionEntry]:
                Detached filtered entry list.
        """
        self.check_cleaned()
        with self._lock:
            return [
                entry
                for entry in self._entries
                if entry.touches_spell_id(spell_id)
            ]

    def describe(
            self,
            *,
            recent: Optional[int] = None,
    ) -> Dict[str, object]:
        """
        Return a detached, serialization-ready journal payload.

        Args:
            recent:
                Optional bound: when given, only the newest `recent` entries
                are included (the persistence twin rides a bounded window;
                checkpoints capture the deltas over time).

        Returns:
            Dict[str, object]:
                Plain-value payload with `entries`, `entry_count`, and
                `next_sequence`.
        """
        self.check_cleaned()
        with self._lock:
            window = self._entries
            if recent is not None and recent >= 0:
                window = self._entries[len(self._entries) - recent:] \
                    if recent < len(self._entries) else self._entries
            return {
                "entries": [entry.describe() for entry in window],
                "entry_count": len(self._entries),
                "next_sequence": self._next_sequence,
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResearchJournal":
        """
        Rebuild one journal from a `describe()` payload.

        Contract:
            - Rebuilt sequences continue from the recorded `next_sequence`,
              so a bounded (recent-window) payload never re-mints identities
              that already exist in the durable record.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            ResearchJournal:
                Reconstructed journal.

        Raises:
            ValueError:
                If the payload shape is invalid, or restored entries are
                not strictly ascending by sequence (corrupt history).
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        entry_payloads = payload.get("entries")
        if not isinstance(entry_payloads, list):
            raise ValueError("payload is missing a valid 'entries' list.")
        journal = cls()
        rebuilt: List[TransitionEntry] = []
        for entry_payload in entry_payloads:
            rebuilt.append(TransitionEntry.from_payload(entry_payload))
        # Sequence integrity (BUG-041): restored journal order stays
        # monotonic and sequences are never reused, so entries must arrive
        # strictly ascending and the counter must clear every one of them.
        previous_sequence = 0
        for entry in rebuilt:
            if entry.sequence <= previous_sequence:
                raise ValueError(
                    f"Journal payload entries are not strictly ascending: "
                    f"sequence {entry.sequence} follows "
                    f"{previous_sequence}. The payload is corrupt; "
                    f"refusing to hydrate a reusable history."
                )
            previous_sequence = entry.sequence
        minimum_next = rebuilt[-1].sequence + 1 if rebuilt else 1
        next_sequence = payload.get("next_sequence")
        with journal._lock:
            journal._entries.extend(rebuilt)
            if (
                    isinstance(next_sequence, int)
                    and next_sequence >= minimum_next
            ):
                journal._next_sequence = next_sequence
            else:
                journal._next_sequence = minimum_next
        return journal
