import enum
from datetime import datetime, timezone
from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class TransitionAct(enum.Enum):
    """
    World-entry act vocabulary for the mutation-research journal.

    Purpose:
        Name the only events the research record acknowledges. The stream is
        forward-only and additive: history exists for understanding, never for
        time travel, so there are deliberately NO checkout/rollback acts.
        Returning to an old version is a NEW registration, not a rewind.

    Contract:
        - `lane_created`: a research lane entered the network (optionally
          anchored onto another lane's node).
        - `registered`: a bound version was formally declared research and
          landed in a lane (the world-entry moment; active bind-side).
        - `staged`: a version entered the world PARKED (`bind_inactive`);
          same declaration mechanics as `registered`, different runtime
          posture at entry.
        - `promoted`: the runtime selection moved (a notch repointed the
          SpellIndex active member); journal-only - promotion changes what
          is live, never which lane holds the version.
        - `attached` / `detached`: a lane's ancestry anchor was organized onto
          or off another lane's node (organization only, never content).
        - `joined`: a lane finished into its parent (divergence-aware; the
          source lane archives).
        - `archived`: a dead-end lane left the active view (restorable via
          network snapshots; objects are indestructible).
        - `restored`: the network organization was rebuilt from a
          content-addressed snapshot (network-scope act).
        - `group_registered` / `group_recomposed`: a subsystem COMPOSITION
          (GroupedResearchNode) entered a lane - first composition vs an
          evolution of a previous one (2026-07-11 owner ruling). Group-
          scope acts carry the composition's content-addressed sha in
          `to_spell_id` (the same sha namespace as spell identities); the
          member roster and composition ancestry ride `metadata`.
    """

    lane_created = "lane_created"
    registered = "registered"
    staged = "staged"
    promoted = "promoted"
    attached = "attached"
    detached = "detached"
    joined = "joined"
    archived = "archived"
    restored = "restored"
    group_registered = "group_registered"
    group_recomposed = "group_recomposed"


class TransitionEntry(Cleanable):
    """
    One immutable forward-only journal event in a research set.

    Purpose:
        Record that one world-entry act happened, when, to which lane, and
        between which content identities. Entries are pure data: they carry no
        behavior, no live references, and are never edited after creation.

    Contract:
        - Value object; immutable after construction (no setters, no lock).
        - `sequence` is minted monotonically by the owning `ResearchJournal`.
        - `lane_id` names the subject lane, or the owning set id for
          network-scope acts (`restored`).
        - `from_spell_id` / `to_spell_id` carry binding-signature SHA256 identities for
          spell-scope acts; `restored` carries the network snapshot SHA in
          `to_spell_id`.
        - `campaign` is the cross-lane research-campaign stamp (owner default:
          always carried, may be None when uncampaigned).
        - `describe()` returns the detached serialization-ready payload;
          `from_payload()` is its exact inverse.

    Threading:
        Immutable-after-init; safe to share across threads without locking.

    Lifecycle:
        Owned by exactly one `ResearchJournal`; `cleanup()` deletes owned
        fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_sequence",
        "_act",
        "_lane_id",
        "_from_spell_id",
        "_to_spell_id",
        "_actor",
        "_campaign",
        "_reason",
        "_created_at",
        "_metadata",
    ]

    def __init__(
            self,
            sequence: int,
            act: TransitionAct,
            lane_id: str,
            *,
            from_spell_id: Optional[str] = None,
            to_spell_id: Optional[str] = None,
            actor: Optional[str] = None,
            campaign: Optional[str] = None,
            reason: Optional[str] = None,
            created_at: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one immutable journal event.

        Args:
            sequence:
                Monotonic position minted by the owning journal (>= 1).
            act:
                World-entry act this event records.
            lane_id:
                Subject lane id, or the owning set id for network-scope acts.
            from_spell_id:
                Optional origin identity (previous tip, anchor node, or
                pre-restore snapshot context depending on the act).
            to_spell_id:
                Optional destination identity (registered version SHA, join
                tip, or network snapshot SHA depending on the act).
            actor:
                Optional acting agent name.
            campaign:
                Optional research-campaign stamp shared across lanes.
            reason:
                Optional human/agent reason line.
            created_at:
                Optional ISO-8601 UTC stamp; minted now when omitted.
            metadata:
                Optional value-typed annotations (detached copy is stored).

        Raises:
            ValueError:
                If sequence < 1, lane_id is empty, or act is not a
                `TransitionAct`.
        """
        super().__init__()
        if not isinstance(act, TransitionAct):
            raise ValueError("act must be a TransitionAct member.")
        if not isinstance(sequence, int) or sequence < 1:
            raise ValueError("sequence must be an int >= 1.")
        if not isinstance(lane_id, str) or not lane_id:
            raise ValueError("lane_id must be a non-empty string.")
        self._sequence: int = sequence
        self._act: TransitionAct = act
        self._lane_id: str = lane_id
        self._from_spell_id: Optional[str] = from_spell_id
        self._to_spell_id: Optional[str] = to_spell_id
        self._actor: Optional[str] = actor
        self._campaign: Optional[str] = campaign
        self._reason: Optional[str] = reason
        self._created_at: str = (
            created_at
            if created_at
            else datetime.now(timezone.utc).isoformat()
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Release owned fields and mark the entry cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._sequence
        del self._act
        del self._lane_id
        del self._from_spell_id
        del self._to_spell_id
        del self._actor
        del self._campaign
        del self._reason
        del self._created_at
        del self._metadata

    @property
    def sequence(self) -> int:
        """
        Return the monotonic journal position of this event.

        Returns:
            int:
                Journal sequence (>= 1).
        """
        self.check_cleaned()
        return self._sequence

    @property
    def act(self) -> TransitionAct:
        """
        Return the recorded world-entry act.

        Returns:
            TransitionAct:
                Act vocabulary member.
        """
        self.check_cleaned()
        return self._act

    @property
    def lane_id(self) -> str:
        """
        Return the subject lane id (or set id for network-scope acts).

        Returns:
            str:
                Subject identity this event belongs to.
        """
        self.check_cleaned()
        return self._lane_id

    @property
    def from_spell_id(self) -> Optional[str]:
        """
        Return the origin identity of this event, when one exists.

        Returns:
            Optional[str]:
                Origin SHA256 (spell or snapshot scope) or None.
        """
        self.check_cleaned()
        return self._from_spell_id

    @property
    def to_spell_id(self) -> Optional[str]:
        """
        Return the destination identity of this event, when one exists.

        Returns:
            Optional[str]:
                Destination SHA256 (spell or snapshot scope) or None.
        """
        self.check_cleaned()
        return self._to_spell_id

    @property
    def actor(self) -> Optional[str]:
        """
        Return the acting agent name, when recorded.

        Returns:
            Optional[str]:
                Actor name or None.
        """
        self.check_cleaned()
        return self._actor

    @property
    def campaign(self) -> Optional[str]:
        """
        Return the research-campaign stamp, when recorded.

        Returns:
            Optional[str]:
                Campaign stamp or None.
        """
        self.check_cleaned()
        return self._campaign

    @property
    def reason(self) -> Optional[str]:
        """
        Return the recorded reason line, when one exists.

        Returns:
            Optional[str]:
                Reason text or None.
        """
        self.check_cleaned()
        return self._reason

    @property
    def created_at(self) -> str:
        """
        Return the ISO-8601 UTC creation stamp.

        Returns:
            str:
                Creation timestamp.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached copy of the value-typed annotations.

        Returns:
            Dict[str, object]:
                Detached metadata mapping.
        """
        self.check_cleaned()
        return dict(self._metadata)

    def touches_spell_id(self, spell_id: str) -> bool:
        """
        Return whether this event references the given identity on either end.

        Args:
            spell_id:
                Identity to test against `from_spell_id` and `to_spell_id`.

        Returns:
            bool:
                True when either endpoint matches.
        """
        self.check_cleaned()
        return spell_id == self._from_spell_id or spell_id == self._to_spell_id

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this event.

        Returns:
            Dict[str, object]:
                Plain-value payload (exact `from_payload()` inverse).
        """
        self.check_cleaned()
        return {
            "sequence": self._sequence,
            "act": self._act.value,
            "lane_id": self._lane_id,
            "from_spell_id": self._from_spell_id,
            "to_spell_id": self._to_spell_id,
            "actor": self._actor,
            "campaign": self._campaign,
            "reason": self._reason,
            "created_at": self._created_at,
            "metadata": dict(self._metadata),
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "TransitionEntry":
        """
        Rebuild one entry from a `describe()` payload.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            TransitionEntry:
                Reconstructed immutable entry.

        Raises:
            ValueError:
                If required keys are missing or invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        act_value = payload.get("act")
        if not isinstance(act_value, str):
            raise ValueError("payload is missing a valid 'act' value.")
        sequence = payload.get("sequence")
        lane_id = payload.get("lane_id")
        if not isinstance(sequence, int) or not isinstance(lane_id, str):
            raise ValueError("payload is missing 'sequence'/'lane_id' values.")
        metadata = payload.get("metadata")
        return cls(
            sequence,
            TransitionAct(act_value),
            lane_id,
            from_spell_id=payload.get("from_spell_id"),
            to_spell_id=payload.get("to_spell_id"),
            actor=payload.get("actor"),
            campaign=payload.get("campaign"),
            reason=payload.get("reason"),
            created_at=payload.get("created_at"),
            metadata=metadata if isinstance(metadata, dict) else None,
        )
