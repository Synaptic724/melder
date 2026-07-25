import copy
import enum
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, ClassVar

from melder.mutation_research.research_set.grouped_research_node import (
    GroupedResearchNode,
)
from melder.mutation_research.research_set.research_node import ResearchNode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


def node_identity(node: object) -> str:
    """
    Return one node's identity across BOTH node families.

    Purpose:
        The single dispatch point for heterogeneous lanes (owner ruling
        2026-07-11: GroupedResearchNode is its own type; the carrying code
        extends): spell nodes identify by binding-signature `spell_id`,
        composition nodes by content-addressed `group_id`. Both live in
        the same sha namespace, so lane indexing, residence, and journal
        endpoints carry either without shape changes.

    Args:
        node:
            ResearchNode or GroupedResearchNode.

    Returns:
        str:
            The node's identity sha.

    Raises:
        TypeError:
            If the object is neither node family (the error names both).
    """
    if isinstance(node, GroupedResearchNode):
        return node.group_id
    if isinstance(node, ResearchNode):
        return node.spell_id
    raise TypeError(
        "node must be a ResearchNode or a GroupedResearchNode; got "
        f"{type(node).__name__}."
    )


class LaneState(enum.Enum):
    """
    Lifecycle states for one research lane.

    Registration:
        VALUE VOCABULARY. An enum is a value a caller
        passes and compares, never an object Melder injects, so there is nothing
        to refuse at bind time.

    Subsystem Context:
        The lifecycle half of the lane vocabulary, beside `LaneType` (the policy
        half). State says whether a lane still accepts work; type says what kind
        of work it was for. They are deliberately orthogonal - an archived
        production lane and an open production lane differ in state, not type.

    Subsystem Context Note - both exits are terminal:
        `joined` and `archived` both end a lane's writable life, and neither is
        undone in place. Recovery runs through `NetworkVersioner`, which rebuilds
        containers wholesale rather than reopening them.

    System Context:
        Lane state is organization, not runtime. A lane changing state has ZERO
        effect on what is live - runtime residency is an orthogonal question
        answered by the frame, which is why archiving a lane never disturbs a
        running world.

    Contract:
        - `open`: the lane accepts registrations and organization.
        - `joined`: the lane finished into its parent; archived-equivalent,
          no further work happens FROM this container (its objects live on;
          new lanes may still anchor at any node that remains here).
        - `archived`: the lane left the active view as a dead end; the
          organization snapshot machinery can restore views that contained
          it, and residence stays permanent so rediscovery still points here.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Lifecycle state of one research lane. Read it from lane views; "
        "MutationResearch verbs move it."
    )

    open = "open"
    joined = "joined"
    archived = "archived"


class LaneType(enum.Enum):
    """
    Policy vocabulary for one research lane (salvaged May classification).

    Registration:
        VALUE VOCABULARY. Users pass this in directly
        (`research_create_lane(lane_type=...)`), so it is a value, not an
        injectable object.

    Subsystem Context:
        The policy half of the lane vocabulary, beside `LaneState` (the
        lifecycle half). Deliberately decoupled from lane NAMES: names stay
        freeform for humans, the type is the word policy reads.

    System Context:
        Note how little this gates. The type never restricts registration or
        reads - its ONLY hook is the join gate, and only when the set's
        `lane_type_enforcement` posture is on (off by default). That restraint
        is the point: this is a research tool, so classification exists to
        inform an agent rather than to block it, and even the one gate it does
        have yields to the same `force=True` supersede the divergence law uses.

    Contract:
        - The type is the POLICY word; lane names stay freeform.
        - Vocabulary: `development` (the trunk posture; the guaranteed
          default lane), `experiment` (the default for freeform lanes -
          this is a research tool), `production` (a lane whose tip is
          runtime-promotion-worthy), `test` (throwaway validation work).
        - The type never gates registration or reads; the ONLY policy hook
          is the join gate, and only while the set's lane-type enforcement
          posture is on (configuration `lane_type_enforcement`, default
          off) - a type-mixing join then requires the same force=True
          supersede the divergence law already uses.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Lane classification - development, experiment, production, test. Pass to "
        "create_lane(...). Cross-type joins require force=True when configuration "
        "lane_type_enforcement is on."
    )

    development = "development"
    experiment = "experiment"
    production = "production"
    test = "test"


class ResearchLane(Cleanable):
    """
    Governance (single-residence law, BUG-048):
        Lanes are handed out LIVE as read surfaces. Every mutator on this
        class is set-internal (underscore-prefixed): residence claims, the
        journal, snapshots, and persistence emission all live on the owning
        `ResearchSet`, so public state change flows through set verbs ONLY.
        Public callers read; the owning set writes.

    One object's line of versions inside the research network.

    Purpose:
        Hold the ordered, full-object version records that describe how one
        conceptual object moved through candidate futures. A lane is a graph
        container, not a runtime surface: lane membership has ZERO runtime
        footprint (versions live in crystallizer custody; runtime residency
        is an orthogonal, on-demand act).

    Contract:
        - Nodes are full-object records keyed by binding-signature SHA256;
          diffs are a derived read feature, never storage.
        - One node per SHA per lane; the set-level `ResidenceRegistry`
          guarantees one lane per SHA network-wide.
        - The anchor (`anchor_lane_id` + `anchor_spell_id`) organizes ancestry
          onto another lane's node; it never moves content.
        - State machine: open -> joined | archived; both exits are terminal
          for this container (recovery happens via network restore, which
          rebuilds containers wholesale).

    Registration:
        MELDER KERNEL - guarded. Lanes are handed out live as READ surfaces and
        written only by their owning set; a user never constructs or registers
        one.

    Subsystem Context:
        The container tier of the ResearchSet package: `ResearchSet` owns lanes,
        lanes hold nodes, and nodes reference custody. It accepts BOTH node
        families - `ResearchNode` (one object's versions) and
        `GroupedResearchNode` (one subsystem's compositions) - dispatching
        through the module-level identity helper, so a lane of group nodes is a
        subsystem's timeline exactly as a lane of spell nodes is an object's.

    System Context:
        A lane is a graph container with ZERO runtime footprint. Membership does
        not make anything live, and promotion does not move anything between
        lanes - "which lane holds this version" and "which version is currently
        selected" are deliberately independent questions. That separation is
        what lets research organization be reorganized freely without ever
        disturbing a running world.
        - Mutating verbs require the open state and raise otherwise.
        - `describe()` / `from_payload()` are exact inverses (nodes ride
          nested payloads).

    Threading:
        Instance `RLock` serializes node/anchor/state mutation and reads.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` cleans owned nodes
        then deletes owned fields; idempotent; lock released last.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Governance (single-residence law, BUG-048): Lanes are handed out LIVE "
        "as read surfaces. Every mutator on this class is set-internal (underscore-prefixed): "
        "residence claims, the journal, snapshots, and persistence emission all live on the "
        "owning `ResearchSet`, so public state change flows through set verbs ONLY. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_lane_id",
        "_name",
        "_lane_type",
        "_anchor_lane_id",
        "_anchor_spell_id",
        "_nodes_by_spell_id",
        "_node_order",
        "_tip_spell_id",
        "_state",
        "_joined_into_lane_id",
        "_created_at",
        "_metadata",
        "_lock",
    ]

    def __init__(
            self,
            name: str,
            *,
            lane_type: Optional[str] = None,
            lane_id: Optional[str] = None,
            created_at: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one open, empty research lane.

        Contract:
            - BORN OPEN AND EMPTY, with no tip and no anchor. State advances
              open -> joined | archived one-way and never returns to open.
            - `lane_type` defaults to `experiment`, NOT to the owning set's
              default-lane type of `development`. A freshly created lane is an
              experiment until the caller says otherwise; the set passes
              `development` explicitly only for its guaranteed default lane.
            - An UNKNOWN `lane_type` raises `ValueError` naming the valid
              vocabulary, so a typo cannot silently create an untyped lane.
            - `lane_id` is minted as a fresh ULID unless one is supplied. A
              supplied id is the RESTORE path - `from_payload` passes the
              recorded id so a rebuilt lane keeps its identity - and is trusted
              without a uniqueness check here, because uniqueness is the owning
              set's responsibility.
            - `metadata` is deep-copied in, so the caller's dict cannot mutate
              the lane afterwards. `created_at` is minted now only when omitted.
            - Name UNIQUENESS is not enforced here; the owning set indexes lanes
              by name and owns that guarantee. This constructor only rejects an
              empty name.

        Threading:
            Creates the lane's own `RLock`; construction is otherwise
            unsynchronized because the object is not yet shared.

        Args:
            name:
                Human-facing lane name (uniqueness is enforced by the owning
                set, which indexes lanes by name).
            lane_type:
                Optional policy vocabulary word (`LaneType` value). Defaults
                to `experiment` (this is a research tool); the owning set
                passes `development` for the guaranteed default lane.
            lane_id:
                Optional stable id (restore path); a fresh ULID is minted
                when omitted.
            created_at:
                Optional ISO-8601 UTC stamp; minted now when omitted.
            metadata:
                Optional value-typed annotations (detached copy is stored).

        Raises:
            ValueError:
                If name is empty, or lane_type is not a `LaneType` value
                (the error names the vocabulary).

        Returns:
            None.
        """
        super().__init__()
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string.")
        self._lane_id: str = lane_id if lane_id else IDBuilder.create_id()
        self._name: str = name
        if lane_type is None:
            self._lane_type: LaneType = LaneType.experiment
        else:
            try:
                self._lane_type = LaneType(lane_type)
            except ValueError:
                known = [member.value for member in LaneType]
                raise ValueError(
                    f"Unknown lane_type '{lane_type}'. Known types: "
                    f"{known}."
                ) from None
        self._anchor_lane_id: Optional[str] = None
        self._anchor_spell_id: Optional[str] = None
        self._nodes_by_spell_id: Dict[str, ResearchNode] = {}
        self._node_order: List[str] = []
        self._tip_spell_id: Optional[str] = None
        self._state: LaneState = LaneState.open
        self._joined_into_lane_id: Optional[str] = None
        self._created_at: str = (
            created_at
            if created_at
            else datetime.now(timezone.utc).isoformat()
        )
        self._metadata: Dict[str, object] = copy.deepcopy(metadata) if metadata else {}
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Clean owned nodes, release fields, and mark the lane cleaned.

        Contract:
            - IDEMPOTENT under double-checked locking: `_cleaned` is tested
              before and inside the lock.
            - OWNS ITS NODES: every held `ResearchNode` is cleaned (best-effort,
              so one failing node cannot strand the rest) before the lane's own
              fields are dropped. A node's single-residence lane is the thing
              that cleans it.
            - DELETE-NOT-NULL posture, no tombstones; post-cleanup access raises
              `AttributeError` via `check_cleaned()`.
            - The lock is deleted LAST, outside the guarded block.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for node in self._nodes_by_spell_id.values():
                try:
                    node.cleanup()
                except Exception:
                    pass
            self._nodes_by_spell_id.clear()
            self._node_order.clear()
            del self._nodes_by_spell_id
            del self._node_order
            del self._tip_spell_id
            del self._anchor_lane_id
            del self._anchor_spell_id
            del self._state
            del self._joined_into_lane_id
            del self._metadata
            del self._created_at
            del self._lane_type
            del self._name
            del self._lane_id
        del self._lock

    def _require_open(self) -> None:
        """
        Raise unless the lane is in the open state.

        Raises:
            RuntimeError:
                If the lane is joined or archived.
        """
        if self._state is not LaneState.open:
            raise RuntimeError(
                f"Lane '{self._name}' ({self._lane_id}) is "
                f"{self._state.value}; no further work happens from this "
                f"container."
            )

    @property
    def lane_id(self) -> str:
        """
        Return the stable lane id (ULID).

        Contract:
            - Machine identity, fixed at construction and unchanged for the
              lane's life; distinct from `name`, which is the human-facing key.
              Survives a describe/from_payload round trip.

        Returns:
            str:
                Lane id.
        """
        self.check_cleaned()
        return self._lane_id

    @property
    def name(self) -> str:
        """
        Return the human-facing lane name.

        Contract:
            - The lookup key the owning set indexes by; unique within that set.
              Distinct from `lane_id`, which is the stable machine identity.

        Returns:
            str:
                Lane name.
        """
        self.check_cleaned()
        return self._name

    @property
    def lane_type(self) -> LaneType:
        """
        Return the policy vocabulary word for this lane.

        Contract:
            - The TYPE is the policy word; the name is freeform. The only place
              type is enforced is the set's join gate (`lane_type_enforcement`),
              where a type-mixing join needs `force=True`. Reading it here is
              always allowed and never gated.

        Returns:
            LaneType:
                development, experiment, production, or test.
        """
        self.check_cleaned()
        return self._lane_type

    @property
    def state(self) -> LaneState:
        """
        Return the current lifecycle state.

        Contract:
            - ONE-WAY STATE MACHINE: `open -> joined` or `open -> archived`, and
              never back. Only an `open` lane accepts new work; `joined` and
              `archived` are terminal read-only containers.
            - `joined` and `archived` are distinct terminals: `joined` means the
              lane's line was folded into a receiver (see `joined_into_lane_id`);
              `archived` means it was retired in place. Neither loses its held
              nodes - the records stay readable.

        Returns:
            LaneState:
                open, joined, or archived.
        """
        self.check_cleaned()
        with self._lock:
            return self._state

    @property
    def tip_spell_id(self) -> Optional[str]:
        """
        Return the newest registered identity in this lane, when any.

        Contract:
            - The tip is the LAST entry in registration order, so it tracks the
              node line, not ancestry. It is `None` only while the lane is empty.
            - It MOVES BACKWARD on detach: when a join transfers the tail nodes
              out, the tip becomes the last remaining node (or `None` if all
              were taken), so it is not a monotonic high-water mark.

        Returns:
            Optional[str]:
                Tip SHA256 or None while empty.
        """
        self.check_cleaned()
        with self._lock:
            return self._tip_spell_id

    @property
    def anchor_lane_id(self) -> Optional[str]:
        """
        Return the lane this lane anchors onto, when attached.

        Contract:
            - Ancestry is a SINGLE pointer, not a list: a lane anchors onto at
              most one node in one other lane. `None` means this lane is a root
              of its own line.
            - Always moves in lockstep with `anchor_spell_id` - they are set
              together and cleared together, so one being `None` implies the
              other is too.

        Returns:
            Optional[str]:
                Anchor lane id or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._anchor_lane_id

    @property
    def anchor_spell_id(self) -> Optional[str]:
        """
        Return the node identity this lane anchors at, when attached.

        Contract:
            - The specific node within `anchor_lane_id` this lane hangs from.
              `None` exactly when `anchor_lane_id` is `None`; the pair is set and
              cleared atomically.
            - Names a node in the OTHER lane, not in this one - it is the
              ancestry attach point, not one of this lane's own members.

        Returns:
            Optional[str]:
                Anchor SHA256 or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._anchor_spell_id

    @property
    def joined_into_lane_id(self) -> Optional[str]:
        """
        Return the receiving lane id after a join, when joined.

        Contract:
            - `None` UNTIL A JOIN, and set exactly once when the lane transitions
              to `joined`. It is the forwarding pointer that says where this
              lane's line went.
            - Independent of the ANCHOR pointer: anchoring is ancestry
              organization on an open lane, joining is a terminal handoff. A lane
              can be anchored without being joined and vice versa.

        Returns:
            Optional[str]:
                Receiving lane id or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._joined_into_lane_id

    @property
    def node_count(self) -> int:
        """
        Return the number of version records held by this lane.

        Contract:
            - Counts nodes CURRENTLY held, so it drops when a join detaches the
              tail out. It is not a lifetime total of everything ever registered
              here - the journal holds that history.

        Returns:
            int:
                Node count.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._node_order)

    @property
    def created_at(self) -> str:
        """
        Return the ISO-8601 UTC creation stamp.

        Contract:
            - Always present. On a rebuilt lane it is the ORIGINAL recorded time,
              not the rebuild time, because `from_payload` passes the stored
              stamp through.

        Returns:
            str:
                Creation timestamp.
        """
        self.check_cleaned()
        return self._created_at

    def _add_node(self, node: object) -> None:
        """
        Append one record (either node family) and advance the tip.

        Args:
            node:
                Immutable ResearchNode (version record) or
                GroupedResearchNode (composition record) to hold.

        Raises:
            RuntimeError:
                If the lane is not open.
            TypeError:
                If the object is neither node family.
            ValueError:
                If the identity is already held by this lane (full-object
                records dedup by content SHA - for compositions, an
                identical member set IS the same identity).
        """
        self.check_cleaned()
        identity = node_identity(node)
        with self._lock:
            self._require_open()
            if identity in self._nodes_by_spell_id:
                raise ValueError(
                    f"Lane '{self._name}' already holds identity "
                    f"'{identity}'."
                )
            self._nodes_by_spell_id[identity] = node
            self._node_order.append(identity)
            self._tip_spell_id = identity

    def get_node(self, spell_id: str) -> ResearchNode:
        """
        Return the version record for one held identity.

        Contract:
            - Returns the LIVE node object, not a copy. The node is immutable, so
              sharing it is safe, but it is the same object the lane holds.
            - A non-held identity raises `KeyError` naming the lane, so the
              return is never `None` and needs no null check. Use `has_node` to
              test membership without catching.

        Threading:
            Lookup runs under `self._lock`.

        Args:
            spell_id:
                Identity to fetch.

        Returns:
            ResearchNode:
                Held version record.

        Raises:
            KeyError:
                If the identity is not held here.
        """
        self.check_cleaned()
        with self._lock:
            node = self._nodes_by_spell_id.get(spell_id)
            if node is None:
                raise KeyError(
                    f"Lane '{self._name}' holds no identity '{spell_id}'."
                )
            return node

    def has_node(self, spell_id: str) -> bool:
        """
        Return whether this lane holds one identity.

        Contract:
            - Tests CURRENT membership of THIS lane only. It says nothing about
              whether the identity resides elsewhere in the network - that is the
              set's residence registry. False here plus a residence answer
              elsewhere is normal after a join moved the node.

        Threading:
            Membership test runs under `self._lock`.

        Args:
            spell_id:
                Identity to test.

        Returns:
            bool:
                True when held.
        """
        self.check_cleaned()
        with self._lock:
            return spell_id in self._nodes_by_spell_id

    def node_spell_ids(self) -> List[str]:
        """
        Return the held identities in registration order.

        Contract:
            - A FRESH list, so mutating it cannot alter the lane's order.
            - REGISTRATION ORDER, oldest first; the last element is the tip.
            - Ids only. Use `nodes()` when the records are needed - it reads the
              same order without a second lookup.

        Threading:
            Materialized under `self._lock`; a coherent snapshot.

        Returns:
            List[str]:
                Detached ordered identity list.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._node_order)

    def nodes(self) -> List[ResearchNode]:
        """
        Return the held version records in registration order.

        Contract:
            - A FRESH list of the LIVE node objects, registration order, oldest
              first. The list is detached (safe to mutate); the nodes inside it
              are immutable and shared.
            - Positionally aligned with `node_spell_ids()` for the same lane
              state, since both walk the same order.

        Threading:
            Built under `self._lock`; a coherent snapshot of the current line.

        Returns:
            List[ResearchNode]:
                Detached ordered node list (nodes are immutable).
        """
        self.check_cleaned()
        with self._lock:
            return [self._nodes_by_spell_id[sha] for sha in self._node_order]

    def _detach_nodes(self, spell_ids: List[str]) -> List[ResearchNode]:
        """
        Remove and return the given records in registration order.

        Purpose:
            The join transfer mechanic: the receiving lane absorbs these
            records; this container stops holding them.

        Args:
            spell_ids:
                Identities to detach; every one must be held here.

        Returns:
            List[ResearchNode]:
                Detached records in this lane's registration order.

        Raises:
            RuntimeError:
                If the lane is not open.
            KeyError:
                If any identity is not held (nothing is detached then).
        """
        self.check_cleaned()
        with self._lock:
            self._require_open()
            requested = set(spell_ids)
            for spell_id in requested:
                if spell_id not in self._nodes_by_spell_id:
                    raise KeyError(
                        f"Lane '{self._name}' holds no identity "
                        f"'{spell_id}'."
                    )
            detached: List[ResearchNode] = []
            remaining_order: List[str] = []
            for spell_id in self._node_order:
                if spell_id in requested:
                    detached.append(self._nodes_by_spell_id.pop(spell_id))
                else:
                    remaining_order.append(spell_id)
            self._node_order = remaining_order
            self._tip_spell_id = remaining_order[-1] if remaining_order else None
            return detached

    def _set_anchor(self, anchor_lane_id: str, anchor_spell_id: str) -> None:
        """
        Attach this lane's ancestry onto another lane's node.

        Args:
            anchor_lane_id:
                Lane being anchored onto.
            anchor_spell_id:
                Node identity within that lane to anchor at.

        Raises:
            RuntimeError:
                If the lane is not open.
            ValueError:
                If either argument is empty.
        """
        self.check_cleaned()
        if not isinstance(anchor_lane_id, str) or not anchor_lane_id:
            raise ValueError("anchor_lane_id must be a non-empty string.")
        if not isinstance(anchor_spell_id, str) or not anchor_spell_id:
            raise ValueError("anchor_spell_id must be a non-empty string.")
        with self._lock:
            self._require_open()
            self._anchor_lane_id = anchor_lane_id
            self._anchor_spell_id = anchor_spell_id

    def clear_anchor(self) -> None:
        """
        Detach this lane's ancestry anchor.

        Contract:
            - OPEN LANES ONLY. A joined or archived lane raises, because ancestry
              is not reorganized on a terminal container.
            - NOT IDEMPOTENT: clearing a lane that holds no anchor raises rather
              than returning quietly, so a redundant clear is a caller error.
            - Clears BOTH anchor fields together, restoring the lane to a root of
              its own line. Content is untouched - only the ancestry pointer
              goes.
            - This is a set-internal effect at the lane level; the public
              `ResearchSet.detach` verb is the journalled path. Clearing here
              alone does not write a journal entry.

        Threading:
            The open-check and the clear run under `self._lock`.

        Raises:
            RuntimeError:
                If the lane is not open, or when no anchor exists.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._require_open()
            if self._anchor_lane_id is None:
                raise RuntimeError(
                    f"Lane '{self._name}' has no anchor to detach."
                )
            self._anchor_lane_id = None
            self._anchor_spell_id = None

    def _mark_joined(self, into_lane_id: str) -> None:
        """
        Finish this lane into a receiving lane (terminal).

        Args:
            into_lane_id:
                Receiving lane id.

        Raises:
            RuntimeError:
                If the lane is not open.
            ValueError:
                If into_lane_id is empty.
        """
        self.check_cleaned()
        if not isinstance(into_lane_id, str) or not into_lane_id:
            raise ValueError("into_lane_id must be a non-empty string.")
        with self._lock:
            self._require_open()
            self._state = LaneState.joined
            self._joined_into_lane_id = into_lane_id

    def _mark_archived(self) -> None:
        """
        Archive this lane as a dead end (terminal for this container).

        Raises:
            RuntimeError:
                If the lane is not open.
        """
        self.check_cleaned()
        with self._lock:
            self._require_open()
            self._state = LaneState.archived

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this lane.

        Contract:
            - THE EXACT INVERSE of `from_payload()`, capturing the FULL lifecycle
              state - state, both anchor fields, tip, joined-into pointer - not
              just contents, so a joined or archived lane round-trips as joined
              or archived rather than reviving open.
            - NODES RIDE NESTED describe() PAYLOADS in registration order, so the
              whole node line is embedded; the lane's order and tip are
              reconstructible from `nodes` alone.
            - Enum fields are emitted as their `.value` strings and `metadata` is
              deep-copied, so the payload is JSON-safe and fully detached.

        Threading:
            Assembled under `self._lock`, so lifecycle fields and the node line
            are mutually consistent.

        Returns:
            Dict[str, object]:
                Plain-value payload (exact `from_payload()` inverse; nodes
                ride nested `describe()` payloads in registration order).
        """
        self.check_cleaned()
        with self._lock:
            return {
                "lane_id": self._lane_id,
                "name": self._name,
                "lane_type": self._lane_type.value,
                "state": self._state.value,
                "anchor_lane_id": self._anchor_lane_id,
                "anchor_spell_id": self._anchor_spell_id,
                "tip_spell_id": self._tip_spell_id,
                "joined_into_lane_id": self._joined_into_lane_id,
                "created_at": self._created_at,
                "metadata": copy.deepcopy(self._metadata),
                "nodes": [
                    self._nodes_by_spell_id[sha].describe()
                    for sha in self._node_order
                ],
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResearchLane":
        """
        Rebuild one lane from a `describe()` payload.

        Contract:
            - `name`, `lane_id`, and a `nodes` LIST are the hard requirements;
              their absence or wrong type raises `ValueError`. Everything else
              degrades to a default.
            - NODE-FAMILY DISPATCH per entry: a payload tagged with the grouped
              node type hydrates as a `GroupedResearchNode`, an untagged one as a
              `ResearchNode`. Back-compat is by ABSENCE - pre-grouping payloads
              have no tag and correctly rebuild as spell nodes.
            - LANE-TYPE BACK-COMPAT: a payload sealed before the type vocabulary
              carries no `lane_type`, and hydrates as `development` when its name
              is `default`, `experiment` otherwise - mirroring how a fresh lane
              of each kind is typed.
            - PRESERVES recorded identity and time: the stored `lane_id` and
              `created_at` are passed through, so a rebuilt lane is the same
              identity it was sealed as.
            - The tip is recomputed as the last node in the rebuilt order rather
              than trusted from the payload, so order and tip cannot disagree.
            - Runs each node's own `from_payload`, so a corrupt node payload is
              rejected by that node's constructor - the lane cannot rebuild a
              node its own type would refuse.

        Threading:
            The rebuilt lane is not shared until this returns; nodes are loaded
            under the new lane's lock.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            ResearchLane:
                Reconstructed lane (state, anchor, order, and tip restored).

        Raises:
            ValueError:
                If the payload shape is invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        name = payload.get("name")
        lane_id = payload.get("lane_id")
        if not isinstance(name, str) or not isinstance(lane_id, str):
            raise ValueError("payload is missing 'name'/'lane_id' values.")
        metadata = payload.get("metadata")
        lane_type = payload.get("lane_type")
        if not isinstance(lane_type, str):
            # Back-compat: payloads sealed before the type vocabulary carry
            # no lane_type. The guaranteed default lane hydrates as the
            # trunk posture; every other lane hydrates as research work.
            lane_type = (
                LaneType.development.value
                if name == "default"
                else LaneType.experiment.value
            )
        lane = cls(
            name,
            lane_type=lane_type,
            lane_id=lane_id,
            created_at=payload.get("created_at"),
            metadata=metadata if isinstance(metadata, dict) else None,
        )
        node_payloads = payload.get("nodes")
        if not isinstance(node_payloads, list):
            raise ValueError("payload is missing a valid 'nodes' list.")
        with lane._lock:
            for node_payload in node_payloads:
                # Node-family dispatch (owner ruling 2026-07-11): tagged
                # payloads hydrate as compositions; untagged payloads are
                # spell nodes - back-compat by absence.
                if (
                        isinstance(node_payload, dict)
                        and node_payload.get("node_type")
                        == GroupedResearchNode.NODE_TYPE
                ):
                    node = GroupedResearchNode.from_payload(node_payload)
                else:
                    node = ResearchNode.from_payload(node_payload)
                identity = node_identity(node)
                lane._nodes_by_spell_id[identity] = node
                lane._node_order.append(identity)
            lane._tip_spell_id = (
                lane._node_order[-1] if lane._node_order else None
            )
            anchor_lane_id = payload.get("anchor_lane_id")
            anchor_spell_id = payload.get("anchor_spell_id")
            if isinstance(anchor_lane_id, str) and isinstance(anchor_spell_id, str):
                lane._anchor_lane_id = anchor_lane_id
                lane._anchor_spell_id = anchor_spell_id
            state_value = payload.get("state")
            if isinstance(state_value, str):
                lane._state = LaneState(state_value)
            joined_into = payload.get("joined_into_lane_id")
            if isinstance(joined_into, str):
                lane._joined_into_lane_id = joined_into
        return lane
