import hashlib
import json
import threading
from typing import Dict, List, Optional, ClassVar

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

    WHAT IT PROTECTS AGAINST:
        Version records are indestructible - a spell version, once declared,
        cannot be lost. The thing a mistake CAN damage is the organization
        around them: a bad `join` collapsing the wrong lane, an `archive` that
        should not have happened, an anchor pointed at the wrong node. This
        object exists so that class of mistake is recoverable, and only that
        class. It restores where things are; it never restores what happened.

    Registration:
        MELDER KERNEL - guarded. Organization snapshots are the record's own
        recovery mechanism, reached through `ResearchSet.snapshot_network()` /
        `restore_network()`.

    Subsystem Context:
        One of the four bookkeeping structures a `ResearchSet` owns, beside
        `ResearchJournal` (append-only history, deliberately excluded from these
        snapshots), `ResidenceRegistry` (the identity partition), and the lanes.
        It versions the ORGANIZATION using exactly the technique the network
        uses for spells: full snapshots, content-addressed, never diffs.

    System Context:
        Content-addressing is what makes the ring cheap - identical organization
        states dedup to one entry, so an idle network costs nothing to snapshot
        repeatedly. The undo ring rides the composition payload into the
        crystallizer twin, so `restore_network` can still reach pre-death
        organization states after a world has been reloaded from a checkpoint.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Content-addressed version control for the graph network itself. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
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

        Contract:
            - `max_snapshots` is the FIFO retention bound and must be >= 1; a
              smaller value raises `ValueError`. There is no unbounded mode - the
              ring always has a finite ceiling, so old organization snapshots age
              out by design.
            - Starts EMPTY: `latest_sha` is None and `snapshot_count` is 0 until
              the first `snapshot`.

        Threading:
            Creates the `RLock` that serializes every later mint, retention pass
            and read.

        Args:
            max_snapshots:
                FIFO retention bound (>= 1).

        Raises:
            ValueError:
                If max_snapshots < 1.

        Returns:
            None.
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
            - IDEMPOTENT under double-checked locking.
            - DELETE-NOT-NULL, no tombstones; the lock is deleted last, outside
              the guarded block.
            - Holds only canonical text and address strings, no owned objects, so
              there is no child cascade.

        Returns:
            None.
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

        Contract:
            - CONTENT-ADDRESSED: the address is the SHA256 of the CANONICAL form
              (sorted keys, compact separators), so two structurally identical
              organizations produce the same address and are stored ONCE.
            - RECENCY FOLLOWS THE OPERATION, not first insertion. Re-snapshotting
              an already-stored state does not duplicate it - it MOVES the
              address to the newest retention position. This is why a restore's
              closing snapshot makes `latest_sha` name the restored organization
              and keeps it as the next mutation's immediate predecessor (the undo
              ring holds).
            - FIFO EVICTION on insert: when the ring exceeds `max_snapshots` the
              OLDEST address is dropped and its canonical text deleted. A
              snapshot just added is never the one evicted by its own insert.
            - Payload must be JSON-serializable; canonicalization goes through
              `json.dumps`, so a non-serializable value raises there.

        Threading:
            The dedup/insert/evict sequence runs under `self._lock`.

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

        Contract:
            - DECODES FROM CANONICAL TEXT each call, so every result is a brand
              new object graph - callers can never reach into the store, and two
              gets of the same address return independent copies.
            - An unknown or AGED-OUT address raises `KeyError`. Because retention
              is bounded, an address observed earlier can legitimately be gone;
              the raise is the honest "no longer retained" signal, not
              corruption.
            - The decoded shape is whatever was snapshotted (an organization
              payload); this object does not interpret it.

        Threading:
            The canonical text is read under `self._lock`; JSON decoding happens
            outside the lock, on the local copy.

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

        Contract:
            - Tests CURRENT retention, not whether the address was ever minted -
              a snapshot evicted by the FIFO ring returns False here even though
              it once existed. Pair it with `snapshot_shas()` when you need the
              retained set rather than a single probe.

        Threading:
            Read under `self._lock`.

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

        Contract:
            - A FRESH list in retention order, oldest first, so the tail is the
              newest and `[-1]` equals `latest_sha`.
            - REFLECTS THE OPERATION ORDER, not mint order: a re-snapshot moves
              its address to the tail, so the position of an address tracks when
              it was last touched, not when it first appeared.
            - Detached; mutating it cannot affect the ring.

        Threading:
            Materialized under `self._lock`.

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

        Contract:
            - The tail of the retention order; `None` only while the ring is
              empty. Equals the last element of `snapshot_shas()`.
            - After a restore's closing snapshot this identifies the RESTORED
              organization, because a re-snapshot moves to the newest position -
              which is what lets `restore_network` chain correctly.
            - Content-addressed, so an organization that changes and reverts to a
              prior shape reports the SAME address again: this tracks the current
              SHAPE, not a monotonic operation count.

        Threading:
            Read under `self._lock`.

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

        Contract:
            - Counts CURRENTLY retained addresses, so it is capped at
              `max_snapshots` and never exceeds it. Dedup means it counts
              DISTINCT organization shapes, not the number of snapshot calls.

        Threading:
            Read under `self._lock`.

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

        Contract:
            - Fixed at construction and never changes; it is the ceiling
              `snapshot_count` can reach before FIFO eviction begins. Read
              WITHOUT the lock because the value is immutable.

        Returns:
            int:
                Maximum retained snapshots.
        """
        self.check_cleaned()
        return self._max_snapshots

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready versioner payload.

        Contract:
            - THE EXACT INVERSE of `from_payload()`: three keys - the
              sha -> canonical map, the retention order, and the bound - copied
              so mutating the result cannot alter the ring.
            - Carries the CANONICAL TEXT of each snapshot, not decoded objects,
              which is what lets `from_payload` re-verify each content address on
              hydration.
            - This is the undo ring that rides the composition payload into the
              crystallizer twin, so a restored world can still reach pre-death
              organization states.

        Threading:
            The three copies are taken together under `self._lock`.

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

        Contract:
            - RE-VERIFIES EVERY CONTENT ADDRESS. The map key IS the SHA256 of its
              canonical text, so hydration recomputes each digest and raises
              `ValueError` if a claimed address does not match. A corrupt or
              forged payload cannot install a false content address - the
              integrity guarantee survives the persistence round trip.
            - REBUILDS IN RETENTION ORDER, following `order`, so the restored ring
              keeps the same recency (and therefore the same `latest_sha`). An
              order entry with no matching canonical text is skipped rather than
              raising.
            - `max_snapshots` falls back to 64 when absent or invalid; a missing
              or wrong-typed `canonical_by_sha`/`order` raises `ValueError`.
            - Builds a fresh versioner; it never edits an existing one in place.

        Threading:
            Entries are loaded under the new versioner's own lock; the object is
            not shared until this returns.

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
