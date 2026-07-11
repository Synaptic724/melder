import threading
from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class ResidenceRegistry(Cleanable):
    """
    Single-residence partition map for one research set.

    Purpose:
        Enforce the hard invariant that one spell identity (binding-signature
        SHA256) resides in exactly ONE lane across the entire graph network,
        never duplicated. This makes the network a partition of identities
        and gives rediscovery detection for free: rebinding identical content
        produces the same SHA, and the collision points straight at the lane
        already holding it.

    Contract:
        - `claim()` is all-or-nothing: an already-resident SHA raises with the
          holding lane named (the rediscovery signal), even when the claimant
          is the holding lane itself (node dedup happens above this layer).
        - Residence is PERMANENT through archive (owner default): archived
          lanes keep their identities so rediscovery always points somewhere
          true. There is deliberately NO release verb.
        - `transfer()` repoints residencies during `join`; every transferred
          SHA must already be resident.
        - Network restore rebuilds the registry wholesale via
          `from_payload()`; it never edits entries in place.

    Threading:
        Instance `RLock` serializes claims, transfers, and reads.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` deletes owned fields;
        idempotent; lock released last.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lane_id_by_sha",
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty residence partition.
        """
        super().__init__()
        self._lane_id_by_sha: Dict[str, str] = {}
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the registry cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._lane_id_by_sha.clear()
            del self._lane_id_by_sha
        del self._lock

    def claim(self, spell_sha: str, lane_id: str) -> None:
        """
        Claim residence of one identity for one lane.

        Args:
            spell_sha:
                Binding-signature SHA256 to claim.
            lane_id:
                Lane taking residence.

        Raises:
            ValueError:
                If either argument is empty.
            RuntimeError:
                If the identity is already resident anywhere - the
                rediscovery signal, naming the holding lane.
        """
        self.check_cleaned()
        if not isinstance(spell_sha, str) or not spell_sha:
            raise ValueError("spell_sha must be a non-empty string.")
        if not isinstance(lane_id, str) or not lane_id:
            raise ValueError("lane_id must be a non-empty string.")
        with self._lock:
            holder = self._lane_id_by_sha.get(spell_sha)
            if holder is not None:
                raise RuntimeError(
                    f"Rediscovery: spell identity '{spell_sha}' already "
                    f"resides in lane '{holder}'. A spell identity lives in "
                    f"exactly one lane; identical content rebinds to the "
                    f"same SHA256."
                )
            self._lane_id_by_sha[spell_sha] = lane_id

    def transfer(self, spell_shas: List[str], to_lane_id: str) -> None:
        """
        Repoint residence of the given identities onto one lane.

        Purpose:
            The `join` mechanic: member identities move to the receiving lane
            in one all-or-nothing motion.

        Args:
            spell_shas:
                Identities to repoint; every one must already be resident.
            to_lane_id:
                Receiving lane id.

        Raises:
            ValueError:
                If to_lane_id is empty.
            KeyError:
                If any identity is not currently resident (nothing is
                repointed in that case).
        """
        self.check_cleaned()
        if not isinstance(to_lane_id, str) or not to_lane_id:
            raise ValueError("to_lane_id must be a non-empty string.")
        with self._lock:
            for spell_sha in spell_shas:
                if spell_sha not in self._lane_id_by_sha:
                    raise KeyError(
                        f"spell identity '{spell_sha}' has no residence to "
                        f"transfer."
                    )
            for spell_sha in spell_shas:
                self._lane_id_by_sha[spell_sha] = to_lane_id

    def residence_of(self, spell_sha: str) -> Optional[str]:
        """
        Return the lane holding one identity, when resident.

        Args:
            spell_sha:
                Identity to look up.

        Returns:
            Optional[str]:
                Holding lane id or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._lane_id_by_sha.get(spell_sha)

    def is_resident(self, spell_sha: str) -> bool:
        """
        Return whether one identity is resident anywhere.

        Args:
            spell_sha:
                Identity to test.

        Returns:
            bool:
                True when resident.
        """
        self.check_cleaned()
        with self._lock:
            return spell_sha in self._lane_id_by_sha

    @property
    def resident_count(self) -> int:
        """
        Return the number of resident identities.

        Returns:
            int:
                Current residence count.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._lane_id_by_sha)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready residence payload.

        Returns:
            Dict[str, object]:
                Plain-value payload with the sha -> lane mapping.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "lane_id_by_sha": dict(self._lane_id_by_sha),
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResidenceRegistry":
        """
        Rebuild one registry from a `describe()` payload.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            ResidenceRegistry:
                Reconstructed registry.

        Raises:
            ValueError:
                If the payload shape is invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        mapping = payload.get("lane_id_by_sha")
        if not isinstance(mapping, dict):
            raise ValueError(
                "payload is missing a valid 'lane_id_by_sha' mapping."
            )
        registry = cls()
        with registry._lock:
            for spell_sha, lane_id in mapping.items():
                registry._lane_id_by_sha[str(spell_sha)] = str(lane_id)
        return registry
