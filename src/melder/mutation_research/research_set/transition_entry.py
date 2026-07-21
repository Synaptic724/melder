import copy
import enum
from datetime import datetime, timezone
from typing import Dict, List, Optional, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class TransitionAct(enum.Enum):
    """
    World-entry act vocabulary for the mutation-research journal.

    Purpose:
        Name the only events the research record acknowledges. The stream is
        forward-only and additive: history exists for understanding, never for
        time travel, so there are deliberately NO checkout/rollback acts.
        Returning to an old version is a NEW registration, not a rewind.

    Registration:
        VALUE VOCABULARY - deliberately unguarded. An enum is compared and
        passed, never injected.

    Subsystem Context:
        The act vocabulary stamped onto every `TransitionEntry` in a
        `ResearchJournal`. The vocabulary is drawn from version control but is
        deliberately NOT git: there is no merge, no rebase, and no checkout,
        because those verbs all imply rewriting or relocating history that this
        model treats as permanent.

    System Context:
        The absent acts say more than the present ones. `promoted` changes what
        is LIVE without changing which lane holds a version, and `restored`
        rebuilds organization while itself being journalled - so even a rewind
        of structure appears in history as a forward event. There is no act in
        this enum that removes anything.

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
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. World-entry act vocabulary for the mutation-research journal. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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

    Registration:
        MELDER KERNEL - guarded. Journal entries are minted by the record;
        a user reads them rather than constructing them.

    Subsystem Context:
        The event value carried by `ResearchJournal`, stamped with a
        `TransitionAct` from this same module. Its immutability is what lets the
        journal promise append-only history: an entry that could be edited would
        make "how did the network come to look like this" a mutable answer.

    System Context:
        The `campaign` stamp is the cross-cutting dimension here - it is applied
        ambiently by the root, so every runtime auto-record made while a
        campaign is active carries it. That is what makes a campaign view a
        WHERE-by-WHEN join across lanes rather than another container: the
        grouping lives on the events, not on the structure.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. One immutable forward-only journal event in a research set. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel

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

        Contract:
            - IMMUTABLE AFTER THIS RETURNS: no setters, no lock. An event that
              could be edited would make the journal's append-only history a
              mutable answer, so immutability is the whole point of the type.
            - THREE HARD REQUIREMENTS validated up front: `act` must be a real
              `TransitionAct` member, `sequence` an int >= 1, and `lane_id`
              non-empty. Everything else is optional annotation.
            - THE ENDPOINTS ARE ACT-DEPENDENT, not fixed columns. `from_spell_id`
              / `to_spell_id` carry spell SHAs for spell-scope acts, the anchor
              node for organization acts, and for `restored` the `to_spell_id`
              carries a NETWORK SNAPSHOT sha rather than a spell identity. The
              constructor does not police which act uses which endpoint - the
              minting verb owns that.
            - `metadata` is deep-copied in, so a caller's dict cannot mutate the
              entry. `created_at` is minted now only when omitted, so a rebuilt
              entry keeps its original time.

        Threading:
            Construction is unsynchronized; the entry is immutable and safe to
            share once the journal holds it.

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

        Returns:
            None.
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
        self._metadata: Dict[str, object] = copy.deepcopy(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Release owned fields and mark the entry cleaned.

        Contract:
            - IDEMPOTENT on the `_cleaned` flag. No lock - the entry is immutable
              and single-owned by its journal, so cleanup is never concurrent.
            - DELETE-NOT-NULL, no tombstones; post-cleanup access raises
              `AttributeError` via `check_cleaned()`.
            - Owns no children and no external resources; it drops its own value
              fields only.

        Returns:
            None.
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

        Contract:
            - Journal-minted, strictly increasing, starts at 1. Ordering by
              sequence IS chronological order within one journal, and it never
              repeats even across a rebuild - `from_payload` continues minting
              beyond the recorded high-water mark.

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

        Contract:
            - The act determines how the other fields read - especially which
              endpoint carries a spell sha versus a snapshot sha (see
              `to_spell_id`). Every act in the vocabulary is additive; none
              removes anything.

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

        Contract:
            - USUALLY A LANE ID, but for the network-scope `restored` act it is
              the owning SET id instead, because a restore has no single subject
              lane. Always non-empty. Read it together with `act` before
              assuming it names a lane.

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

        Contract:
            - MEANING IS ACT-DEPENDENT: a previous tip on a join, the vacated
              anchor node on a detach, or pre-restore context - not a fixed
              "source spell". `None` when the act has no origin end.

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

        Contract:
            - MEANING IS ACT-DEPENDENT and this is the endpoint that carries the
              cross-scope values: a registered/staged version sha, a composition
              content-sha for the group acts, or - for `restored` - a NETWORK
              SNAPSHOT sha rather than a spell identity. `campaign_view` and
              `group_history` key off this field, so read `act` before treating
              the value as a spell id.

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

        Contract:
            - `None` means the minting verb supplied no actor; optional
              annotation, never inferred.

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

        Contract:
            - `None` means the event was recorded outside any campaign. This is
              the field `campaign_view` filters on to gather one effort's story
              across lanes.

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

        Contract:
            - `None` when no reason was supplied; free-text annotation only,
              never parsed.

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

        Contract:
            - Always present. On a rebuilt entry it is the ORIGINAL recorded
              time, since `from_payload` passes the stored stamp through - the
              journal's timeline survives a round trip.

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

        Contract:
            - DEEP-COPIED out, mirroring the deep copy in, so neither the
              caller's original nor the returned dict can mutate the entry.
            - This is where act-specific structured detail rides - a group act's
              member roster and composition ancestry, a restore's snapshot
              address - so the payload varies by act.
            - Empty dict (never None) when no annotations were recorded.

        Returns:
            Dict[str, object]:
                Detached metadata mapping.
        """
        self.check_cleaned()
        return copy.deepcopy(self._metadata)

    def touches_spell_id(self, spell_id: str) -> bool:
        """
        Return whether this event references the given identity on either end.

        Contract:
            - Tests BOTH endpoints (`from_spell_id` and `to_spell_id`), so it
              catches an identity whether it was the origin or the destination of
              the act. This is what `history(...)` and `group_history(...)` use to
              gather every event touching an identity.
            - Endpoint-only. It does NOT look inside `metadata`, so an identity
              that appears only in a group act's member roster is not matched
              here - the group-history reads widen the search deliberately.

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

        Contract:
            - THE EXACT INVERSE of `from_payload()`: the ten keys it emits are
              precisely the ones `from_payload` reads, so an entry round-trips
              losslessly including its sequence and original time.
            - `act` is emitted as its `.value` string and `metadata` is
              deep-copied, so the payload is JSON-safe and fully detached.

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
            "metadata": copy.deepcopy(self._metadata),
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "TransitionEntry":
        """
        Rebuild one entry from a `describe()` payload.

        Contract:
            - HARD REQUIREMENTS: a string `act` that names a real `TransitionAct`
              value, an int `sequence`, and a string `lane_id`. Missing or
              wrong-typed values among these raise `ValueError`; an unknown act
              string raises from the `TransitionAct(...)` lookup.
            - TOLERANT OF WRONG-TYPED OPTIONALS: a non-dict `metadata` is treated
              as absent rather than raising, so a partially-corrupt payload still
              yields a valid entry.
            - PRESERVES sequence and `created_at`, so a rebuilt entry keeps its
              journal position and original time - the timeline is faithful.
            - Runs the constructor's full validation, so it cannot produce an
              entry the constructor would refuse.

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
