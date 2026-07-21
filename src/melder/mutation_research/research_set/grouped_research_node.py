import copy
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class GroupedResearchNode(Cleanable):
    """
    One immutable COMPOSITION record inside a research lane.

    Purpose:
        Formally declare that a set of registered versions form one
        subsystem composition (owner ruling 2026-07-11: "make a
        GroupedResearchNode and load it with multiple spells"). The node
        is PURELY INFORMATIONAL: it pins member identities by reference,
        owns no custody crystal, gates nothing, and never executes. A lane
        of these nodes is a subsystem's timeline, exactly as a lane of
        ResearchNodes is one object's timeline.

    Contract:
        - Its OWN node type: a sibling of ResearchNode, never a subclass
          or an optional-field variant of it (both families stay
          first-class; duplication between them is accepted by ruling).
        - Value object; immutable after construction (no setters, no
          lock).
        - `group_id` is CONTENT-ADDRESSED: sha256 over the canonical
          (deduped, sorted) member list - the NetworkVersioner identity
          discipline one rung up. Identical member sets ARE the same
          identity; recomposing an unchanged roster is a rediscovery, not
          a new fact.
        - `member_spell_ids` are references: members keep their own
          lanes, residence, and custody untouched.

    Registration:
        MELDER KERNEL - guarded. Compositions are declared through
        `ResearchSet.register_group()` / `recompose_group()`, never by
        constructing a node.

    Subsystem Context:
        The composition-grain node type, and a deliberate SIBLING of
        `ResearchNode` rather than a subclass or an optional field on it. Both
        families stay first-class and the duplication is accepted by ruling. A
        lane holds either kind. The practical difference: a spell node has
        custody behind it, a group node has none - which is why code-grain verbs
        refuse a composition id teach-grade rather than pretending.

    System Context:
        Content-addressing is what makes recomposition meaningful. The identity
        is a SHA256 over the canonical member list, so recomposing an unchanged
        roster reproduces the SAME identity and registers as a rediscovery
        rather than a new fact - the same discipline `NetworkVersioner` applies
        to organization snapshots, one rung up. Being purely informational is
        the counterpart: a composition can be declared freely because it gates
        nothing and cannot execute.
        - `parent_group_ids` is composition ancestry only (the previous
          composition(s) this one evolved from) - a namespace deliberately
          separate from spell ancestry.
        - `describe()` payloads carry `node_type: "group"`;
          `from_payload()` is the exact inverse and VERIFIES the recorded
          group_id against the recomputed content address (a mismatch is
          a corrupted or tampered record and refuses loudly). Untagged
          payloads belong to ResearchNode - back-compat by absence.

    Threading:
        Immutable-after-init; safe to share across threads without
        locking.

    Lifecycle:
        Owned by exactly one `ResearchLane` at a time (single-residence
        invariant applies to group identities exactly as to spell
        identities); `cleanup()` deletes owned fields; idempotent.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. One immutable COMPOSITION record inside a research lane. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel

    NODE_TYPE = "group"

    __slots__ = Cleanable.__slots__ + [
        "_group_id",
        "_member_spell_ids",
        "_parent_group_ids",
        "_author",
        "_reason",
        "_campaign",
        "_created_at",
        "_metadata",
    ]

    def __init__(
            self,
            member_spell_ids: List[str],
            *,
            parent_group_ids: Optional[List[str]] = None,
            author: Optional[str] = None,
            reason: Optional[str] = None,
            campaign: Optional[str] = None,
            created_at: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one immutable composition record.

        Contract:
            - IMMUTABLE AFTER THIS RETURNS: no setters, no lock.
            - IDENTITY IS THE CONTENT, NOT MINTED. `group_id` is derived from the
              sorted-deduped member set, so two compositions with the same
              members ARE the same identity (rediscovery). Members are stored as
              a canonical sorted tuple; order and duplicates in the input do not
              affect identity.
            - REQUIRES AT LEAST ONE MEMBER; an empty list raises. Every member
              and every parent group id must be non-empty, validated up front.
            - `group_id` IS NOT A CUSTODY ID. A composition is informational -
              no `SpellCrystal` exists or is expected for it, so this id reaches
              no crystallizer material (unlike a spell node's `spell_id`).
            - `parent_group_ids` is COMPOSITION ancestry in its own namespace
              (previous group ids), distinct from a spell node's spell ancestry.
            - `metadata` is deep-copied in; `created_at` is minted now only when
              omitted, so a rebuild preserves the original time.

        Threading:
            Construction is unsynchronized; the node is immutable once the lane
            holds it.

        Args:
            member_spell_ids:
                Non-empty member identities (binding-signature SHA256s).
                Deduped and stored sorted - a composition is a SET; the
                canonical order is what the content address seals.
            parent_group_ids:
                Optional composition ancestry (previous group ids).
            author:
                Optional registering agent name.
            reason:
                Optional human/agent reason line.
            campaign:
                Optional research-campaign stamp.
            created_at:
                Optional ISO-8601 UTC stamp; minted now when omitted.
            metadata:
                Optional value-typed annotations (detached copy stored).

        Raises:
            ValueError:
                If the member list is empty, any member is empty, or any
                parent group id is empty.

        Returns:
            None.
        """
        super().__init__()
        if not isinstance(member_spell_ids, list) or not member_spell_ids:
            raise ValueError(
                "member_spell_ids must be a non-empty list of identities."
            )
        for member in member_spell_ids:
            if not isinstance(member, str) or not member:
                raise ValueError(
                    "member_spell_ids must contain non-empty strings."
                )
        parents: List[str] = list(parent_group_ids) if parent_group_ids else []
        for parent in parents:
            if not isinstance(parent, str) or not parent:
                raise ValueError(
                    "parent_group_ids must contain non-empty strings."
                )
        members: Tuple[str, ...] = tuple(sorted(set(member_spell_ids)))
        self._member_spell_ids: Tuple[str, ...] = members
        self._group_id: str = GroupedResearchNode.compute_group_id(
            list(members),
        )
        self._parent_group_ids: Tuple[str, ...] = tuple(parents)
        self._author: Optional[str] = author
        self._reason: Optional[str] = reason
        self._campaign: Optional[str] = campaign
        self._created_at: str = (
            created_at
            if created_at
            else datetime.now(timezone.utc).isoformat()
        )
        self._metadata: Dict[str, object] = copy.deepcopy(metadata) if metadata else {}

    @staticmethod
    def compute_group_id(member_spell_ids: List[str]) -> str:
        """
        Return the content address for one member set.

        Contract:
            - PURE AND DETERMINISTIC: the same member set always yields the same
              digest, regardless of input order or duplicates, because it hashes
              the newline-joined SORTED, DEDUPED members. This is the identity
              function the whole grouped model rests on.
            - Static - it takes a raw member list and needs no instance, so it
              can predict a composition's identity before construction (e.g. to
              detect a would-be rediscovery).

        Args:
            member_spell_ids:
                Member identities (deduped/sorted internally).

        Returns:
            str:
                sha256 hex digest over the canonical member list.
        """
        canonical = "\n".join(sorted(set(member_spell_ids)))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the node cleaned.

        Contract:
            - IDEMPOTENT on the `_cleaned` flag; no lock, since the node is
              immutable and single-owned by its lane.
            - DELETE-NOT-NULL, no tombstones; post-cleanup access raises
              `AttributeError` via `check_cleaned()`.
            - Owns no children (members are referenced by id, not held), so there
              is no cascade - it drops its own value fields only.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._group_id
        del self._member_spell_ids
        del self._parent_group_ids
        del self._author
        del self._reason
        del self._campaign
        del self._created_at
        del self._metadata

    @property
    def group_id(self) -> str:
        """
        Return the composition identity (content-addressed; NOT a custody
        id - no crystal exists or is expected for a group identity).

        Contract:
            - CONTENT-ADDRESSED over the member set, so it is stable for the
              node's life and equal for any composition with the same members.
            - LIVES IN THE SAME sha NAMESPACE as spell ids (both hex sha256), so
              a group act's `to_spell_id` can carry it - but it reaches NO
              custody material, which is why the spell-grain custody reads refuse
              teach-grade when handed a composition id.

        Returns:
            str:
                sha256 hex digest over the canonical member list.
        """
        self.check_cleaned()
        return self._group_id

    @property
    def member_spell_ids(self) -> List[str]:
        """
        Return a detached copy of the pinned member identities.

        Contract:
            - A FRESH list in CANONICAL order (sorted, deduped) - the same order
              that seals `group_id`, so re-hashing it reproduces the identity.
            - Members are pinned BY REFERENCE (sha ids), not held: the
              composition points at spell versions, it does not own or copy them.

        Returns:
            List[str]:
                Canonical (sorted, deduped) member SHA256 identities.
        """
        self.check_cleaned()
        return list(self._member_spell_ids)

    @property
    def member_count(self) -> int:
        """
        Return the number of pinned members.

        Contract:
            - Counts DISTINCT members (the stored set is already deduped), so it
              equals `len(member_spell_ids)` and is always >= 1.

        Returns:
            int:
                Member count.
        """
        self.check_cleaned()
        return len(self._member_spell_ids)

    @property
    def parent_group_ids(self) -> List[str]:
        """
        Return a detached copy of the composition ancestry.

        Contract:
            - A FRESH list of GROUP ids (its OWN namespace), not spell ids -
              composition ancestry references previous compositions.
            - Empty means a FIRST composition; a single parent means an
              evolution (a `recompose_group` result). Declaration order preserved.

        Returns:
            List[str]:
                Previous composition identities in declaration order.
        """
        self.check_cleaned()
        return list(self._parent_group_ids)

    @property
    def author(self) -> Optional[str]:
        """
        Return the registering agent name, when recorded.

        Contract:
            - `None` means none was supplied; optional annotation, never
              inferred.

        Returns:
            Optional[str]:
                Author name or None.
        """
        self.check_cleaned()
        return self._author

    @property
    def reason(self) -> Optional[str]:
        """
        Return the recorded reason line, when one exists.

        Contract:
            - `None` when none was supplied; free-text annotation, never parsed.

        Returns:
            Optional[str]:
                Reason text or None.
        """
        self.check_cleaned()
        return self._reason

    @property
    def campaign(self) -> Optional[str]:
        """
        Return the research-campaign stamp, when recorded.

        Contract:
            - `None` when unstamped. Composition registration through the ROOT
              applies the ambient campaign (parity with runtime auto-records), so
              a stamped value here reflects that ambient stamp or an explicit one.

        Returns:
            Optional[str]:
                Campaign stamp or None.
        """
        self.check_cleaned()
        return self._campaign

    @property
    def created_at(self) -> str:
        """
        Return the ISO-8601 UTC creation stamp.

        Contract:
            - Always present. On a rebuilt node it is the ORIGINAL recorded time,
              since `from_payload` passes the stored stamp through.

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
            - DEEP-COPIED out, mirroring the deep copy in, so neither side can
              mutate the node's stored metadata. Empty dict (never None) when
              none was supplied.

        Returns:
            Dict[str, object]:
                Detached metadata mapping.
        """
        self.check_cleaned()
        return copy.deepcopy(self._metadata)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this node.

        Contract:
            - CARRIES `node_type: "group"`, which is the tag lane hydration
              dispatches on: tagged payloads rebuild as compositions, untagged
              ones as spell nodes (back-compat by absence). Never drop the tag.
            - THE EXACT INVERSE of `from_payload()`, fully detached (member and
              parent lists copied, metadata deep-copied), plain-value throughout.

        Returns:
            Dict[str, object]:
                Plain-value payload (exact `from_payload()` inverse;
                carries `node_type: "group"` so carrying code can
                dispatch - untagged payloads are spell nodes).
        """
        self.check_cleaned()
        return {
            "node_type": GroupedResearchNode.NODE_TYPE,
            "group_id": self._group_id,
            "member_spell_ids": list(self._member_spell_ids),
            "parent_group_ids": list(self._parent_group_ids),
            "author": self._author,
            "reason": self._reason,
            "campaign": self._campaign,
            "created_at": self._created_at,
            "metadata": copy.deepcopy(self._metadata),
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "GroupedResearchNode":
        """
        Rebuild one composition node from a `describe()` payload.

        Contract:
            - REQUIRES the `node_type` group tag; a payload without it is not a
              composition and is refused, which is the guard that stops a spell
              payload rehydrating as a group.
            - RE-VERIFIES IDENTITY. The recorded `group_id` is recomputed from the
              members and a mismatch raises - a tampered composition (members
              edited to disagree with the sealed id) cannot enter the record.
            - Runs the constructor's validation, so an empty member list or empty
              member/parent is rejected on rebuild exactly as on construction.
            - PRESERVES recorded `created_at`.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            GroupedResearchNode:
                Reconstructed immutable node.

        Raises:
            ValueError:
                If required keys are missing/invalid, or the recorded
                group_id does not match the recomputed content address
                (integrity refusal - the record never trusts a tampered
                composition).
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        if payload.get("node_type") != cls.NODE_TYPE:
            raise ValueError(
                "payload is not a grouped-research-node payload "
                "(node_type must be 'group')."
            )
        members = payload.get("member_spell_ids")
        if not isinstance(members, list) or not members:
            raise ValueError(
                "payload is missing a valid 'member_spell_ids' list."
            )
        parents = payload.get("parent_group_ids")
        metadata = payload.get("metadata")
        node = cls(
            list(members),
            parent_group_ids=(
                list(parents) if isinstance(parents, list) else None
            ),
            author=payload.get("author"),
            reason=payload.get("reason"),
            campaign=payload.get("campaign"),
            created_at=payload.get("created_at"),
            metadata=metadata if isinstance(metadata, dict) else None,
        )
        recorded_id = payload.get("group_id")
        if isinstance(recorded_id, str) and recorded_id != node.group_id:
            raise ValueError(
                f"Recorded group_id '{recorded_id[:12]}...' does not match "
                f"the recomputed content address "
                f"'{node.group_id[:12]}...'; the composition record is "
                f"corrupted or tampered."
            )
        return node
