import hashlib
import json
import threading
from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class NetworkVersioner(Cleanable):
    """
    Content-addressed version control for the graph network itself.

    Purpose:
        Objects in the research network are indestructible; the thing that
        can actually be damaged by a mistake is the ORGANIZATION (which lane
        holds what, what anchors where, what is archived). This object
        versions that organization the same way the network versions spells:
        full snapshots, content-addressed by SHA256, restorable at any point.

    Contract:
        - `snapshot()` canonicalizes the payload (sorted keys, compact
          separators) and addresses it by the SHA256 of that canonical form;
          identical organization states dedup to the same address and are
          stored once.
        - Snapshots exclude the journal by design: history is append-only
          and survives restore.
        - Retention is a bounded FIFO ring (`max_snapshots`); the newest
          snapshot is never dropped by an insert that follows it.
        - `get()` returns a fresh deep value copy decoded from the stored
          canonical form; callers can never mutate the store.

    Threading:
        Instance `RLock` serializes snapshot minting, retention, and reads.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` deletes owned fields;
        idempotent; lock released last.
    """

    __slots__ = Cleanable.__slots__ + [
        "_canonical_by_sha",
        "_order",
        "_max_snapshots",
        "_lock",
    ]

    def __init__(self, *, max_snapshots: int = 64) -> None:
        """
        Initialize one empty snapshot ring.

        Args:
            max_snapshots:
                FIFO retention bound (>= 1).

        Raises:
            ValueError:
                If max_snapshots < 1.
        """
        super().__init__()
        if not isinstance(max_snapshots, int) or max_snapshots < 1:
            raise ValueError("max_snapshots must be an int >= 1.")
        self._canonical_by_sha: Dict[str, str] = {}
        self._order: List[str] = []
        self._max_snapshots: int = max_snapshots
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the versioner cleaned.

        Contract:
            - Idempotent; del posture (no tombstones); lock last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._canonical_by_sha.clear()
            self._order.clear()
            del self._canonical_by_sha
            del self._order
            del self._max_snapshots
        del self._lock

    def snapshot(self, payload: Dict[str, object]) -> str:
        """
        Store one organization snapshot and return its content address.

        Args:
            payload:
                Detached, JSON-serializable organization payload.

        Returns:
            str:
                SHA256 hex address of the canonical payload form. Identical
                payloads return the existing address without duplication,
                MOVED to the newest retention position - recency follows
                the operation order, not first insertion.
        """
        self.check_cleaned()
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )
        snapshot_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        with self._lock:
            if snapshot_sha in self._canonical_by_sha:
                # Dedupe stores the canonical once but recency is the
                # OPERATION's (BUG-261): a re-snapshot (for example a
                # restore's closing snapshot) moves the address to the
                # newest position so latest_sha identifies the restored
                # organization and bounded retention keeps it as the next
                # mutation's immediate predecessor - the undo ring holds.
                self._order.remove(snapshot_sha)
                self._order.append(snapshot_sha)
                return snapshot_sha
            self._canonical_by_sha[snapshot_sha] = canonical
            self._order.append(snapshot_sha)
            while len(self._order) > self._max_snapshots:
                oldest = self._order.pop(0)
                del self._canonical_by_sha[oldest]
            return snapshot_sha

    def get(self, snapshot_sha: str) -> Dict[str, object]:
        """
        Return a fresh value copy of one stored snapshot.

        Args:
            snapshot_sha:
                Content address to fetch.

        Returns:
            Dict[str, object]:
                Decoded organization payload.

        Raises:
            KeyError:
                If the address is unknown (possibly retired by retention).
        """
        self.check_cleaned()
        with self._lock:
            canonical = self._canonical_by_sha.get(snapshot_sha)
        if canonical is None:
            raise KeyError(
                f"Unknown network snapshot '{snapshot_sha}' (it may have "
                f"aged out of the retention ring)."
            )
        return json.loads(canonical)

    def has(self, snapshot_sha: str) -> bool:
        """
        Return whether one content address is currently retained.

        Args:
            snapshot_sha:
                Content address to test.

        Returns:
            bool:
                True when retained.
        """
        self.check_cleaned()
        with self._lock:
            return snapshot_sha in self._canonical_by_sha

    def snapshot_shas(self) -> List[str]:
        """
        Return the retained content addresses, oldest first.

        Returns:
            List[str]:
                Detached ordered address list.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._order)

    @property
    def latest_sha(self) -> Optional[str]:
        """
        Return the newest retained content address, when any.

        Returns:
            Optional[str]:
                Newest address or None while empty.
        """
        self.check_cleaned()
        with self._lock:
            return self._order[-1] if self._order else None

    @property
    def snapshot_count(self) -> int:
        """
        Return the number of retained snapshots.

        Returns:
            int:
                Retained snapshot count.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._order)

    @property
    def max_snapshots(self) -> int:
        """
        Return the FIFO retention bound.

        Returns:
            int:
                Maximum retained snapshots.
        """
        self.check_cleaned()
        return self._max_snapshots

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready versioner payload.

        Returns:
            Dict[str, object]:
                Plain-value payload with canonical snapshots, order, and the
                retention bound.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "canonical_by_sha": dict(self._canonical_by_sha),
                "order": list(self._order),
                "max_snapshots": self._max_snapshots,
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "NetworkVersioner":
        """
        Rebuild one versioner from a `describe()` payload.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            NetworkVersioner:
                Reconstructed versioner.

        Raises:
            ValueError:
                If the payload shape is invalid, or a retained entry's
                claimed content address does not match the recomputed
                digest of its canonical text (corrupt/forged payload).
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        canonical_by_sha = payload.get("canonical_by_sha")
        order = payload.get("order")
        max_snapshots = payload.get("max_snapshots")
        if not isinstance(canonical_by_sha, dict) or not isinstance(order, list):
            raise ValueError(
                "payload is missing 'canonical_by_sha'/'order' values."
            )
        versioner = cls(
            max_snapshots=(
                max_snapshots
                if isinstance(max_snapshots, int) and max_snapshots >= 1
                else 64
            ),
        )
        with versioner._lock:
            for snapshot_sha in order:
                canonical = canonical_by_sha.get(snapshot_sha)
                if isinstance(canonical, str):
                    # Content-address integrity: the key IS the digest.
                    # Recompute it so a forged/corrupt claimed SHA can never
                    # enter the store as if it were content-verified.
                    actual_sha = hashlib.sha256(
                        canonical.encode("utf-8")
                    ).hexdigest()
                    if actual_sha != str(snapshot_sha):
                        raise ValueError(
                            f"Snapshot content address mismatch during "
                            f"hydration: claimed '{snapshot_sha}' but the "
                            f"canonical text digests to '{actual_sha}'. "
                            f"The payload is corrupt or forged; refusing "
                            f"to install a false content address."
                        )
                    versioner._canonical_by_sha[str(snapshot_sha)] = canonical
                    versioner._order.append(str(snapshot_sha))
        return versioner
