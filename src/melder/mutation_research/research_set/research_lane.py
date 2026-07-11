import enum
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

from melder.mutation_research.research_set.research_node import ResearchNode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class LaneState(enum.Enum):
    """
    Lifecycle states for one research lane.

    Contract:
        - `open`: the lane accepts registrations and organization.
        - `joined`: the lane finished into its parent; archived-equivalent,
          no further work happens FROM this container (its objects live on;
          new lanes may still anchor at any node that remains here).
        - `archived`: the lane left the active view as a dead end; the
          organization snapshot machinery can restore views that contained
          it, and residence stays permanent so rediscovery still points here.
    """

    open = "open"
    joined = "joined"
    archived = "archived"


class ResearchLane(Cleanable):
    """
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
        - Mutating verbs require the open state and raise otherwise.
        - `describe()` / `from_payload()` are exact inverses (nodes ride
          nested payloads).

    Threading:
        Instance `RLock` serializes node/anchor/state mutation and reads.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` cleans owned nodes
        then deletes owned fields; idempotent; lock released last.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lane_id",
        "_name",
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
            lane_id: Optional[str] = None,
            created_at: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one open, empty research lane.

        Args:
            name:
                Human-facing lane name (uniqueness is enforced by the owning
                set, which indexes lanes by name).
            lane_id:
                Optional stable id (restore path); a fresh ULID is minted
                when omitted.
            created_at:
                Optional ISO-8601 UTC stamp; minted now when omitted.
            metadata:
                Optional value-typed annotations (detached copy is stored).

        Raises:
            ValueError:
                If name is empty.
        """
        super().__init__()
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string.")
        self._lane_id: str = lane_id if lane_id else IDBuilder.create_id()
        self._name: str = name
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
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Clean owned nodes, release fields, and mark the lane cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
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

        Returns:
            str:
                Lane name.
        """
        self.check_cleaned()
        return self._name

    @property
    def state(self) -> LaneState:
        """
        Return the current lifecycle state.

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

        Returns:
            str:
                Creation timestamp.
        """
        self.check_cleaned()
        return self._created_at

    def add_node(self, node: ResearchNode) -> None:
        """
        Append one version record and advance the tip.

        Args:
            node:
                Immutable version record to hold.

        Raises:
            RuntimeError:
                If the lane is not open.
            ValueError:
                If the identity is already held by this lane (full-object
                records dedup by content SHA).
        """
        self.check_cleaned()
        with self._lock:
            self._require_open()
            spell_id = node.spell_id
            if spell_id in self._nodes_by_spell_id:
                raise ValueError(
                    f"Lane '{self._name}' already holds identity "
                    f"'{spell_id}'."
                )
            self._nodes_by_spell_id[spell_id] = node
            self._node_order.append(spell_id)
            self._tip_spell_id = spell_id

    def get_node(self, spell_id: str) -> ResearchNode:
        """
        Return the version record for one held identity.

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

        Returns:
            List[ResearchNode]:
                Detached ordered node list (nodes are immutable).
        """
        self.check_cleaned()
        with self._lock:
            return [self._nodes_by_spell_id[sha] for sha in self._node_order]

    def detach_nodes(self, spell_ids: List[str]) -> List[ResearchNode]:
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

    def set_anchor(self, anchor_lane_id: str, anchor_spell_id: str) -> None:
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

        Raises:
            RuntimeError:
                If the lane is not open, or when no anchor exists.
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

    def mark_joined(self, into_lane_id: str) -> None:
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

    def mark_archived(self) -> None:
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
                "state": self._state.value,
                "anchor_lane_id": self._anchor_lane_id,
                "anchor_spell_id": self._anchor_spell_id,
                "tip_spell_id": self._tip_spell_id,
                "joined_into_lane_id": self._joined_into_lane_id,
                "created_at": self._created_at,
                "metadata": dict(self._metadata),
                "nodes": [
                    self._nodes_by_spell_id[sha].describe()
                    for sha in self._node_order
                ],
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResearchLane":
        """
        Rebuild one lane from a `describe()` payload.

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
        lane = cls(
            name,
            lane_id=lane_id,
            created_at=payload.get("created_at"),
            metadata=metadata if isinstance(metadata, dict) else None,
        )
        node_payloads = payload.get("nodes")
        if not isinstance(node_payloads, list):
            raise ValueError("payload is missing a valid 'nodes' list.")
        with lane._lock:
            for node_payload in node_payloads:
                node = ResearchNode.from_payload(node_payload)
                lane._nodes_by_spell_id[node.spell_id] = node
                lane._node_order.append(node.spell_id)
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
