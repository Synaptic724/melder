"""Qualify an experimental creation-claim protocol over real native stores.

This is a protocol experiment, not a Melder runtime patch. All participating
writers must use the same per-entry locks; legacy scoped-root doors do not yet
do that. The probe deliberately selects real stores externally and gives them
no new scope policy. Store mutexes never remain held while waiting for claims
or invoking application constructors.
"""

import hashlib
import json
import sys
from _thread import RLock
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier, Event, Thread, current_thread
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Self

from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_lock_probe import (
    NativeLeaf,
    NativeParent,
    NativeRoot,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.spellbook.spell import Spell


class Entry:
    """Borrow one selected store/binding and retain its stable writer lock.

    Unique uses the existing Spell lock, so native unique purge participates.
    Other shared lifetimes use an experimental per-entry lock. Purging the value
    does not retire this lock; otherwise active waiters could split across locks.
    """

    def __init__(self, store: Creations, spell: Spell) -> None:
        """Initialize a trusted store selection; this object owns no scope authority."""
        self.store = store
        self.spell = spell
        self.lock = spell._lock if spell.existence is Existence.unique else RLock()


class ClaimBatch:
    """Own acquired writer locks and retain the selected values for one attempt."""

    def __init__(self, entries: list[Entry], values: dict[Entry, object]) -> None:
        """Take ownership of held locks after the whole attempt has succeeded."""
        self.entries = entries
        self.values = values

    def cleanup(self) -> None:
        """Release locks before dropping borrowed values, without disposing objects."""
        for entry in reversed(self.entries):
            entry.lock.release()
        self.entries.clear()
        self.values.clear()

    def __enter__(self) -> Self:
        """Return the already-admitted batch; no further acquisition happens here."""
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Release every claim when construction succeeds or raises."""
        self.cleanup()

    def get_or_create(self, entry: Entry, factory: Callable[[], object]) -> object:
        """Reuse the captured value or construct and publish under the held claim.

        Contract:
            Claims are complete before the first factory runs. There is no
            speculative retry after application construction has started.
            The native Creations store receives the actual object and existing
            disposal metadata. Its mutex covers publication only.
        """
        assert entry in self.entries
        if entry in self.values:
            return self.values[entry]
        value = factory()
        with entry.store._lock:
            entry.store.add_creation(
                entry.spell.spell_id, value,
                has_disposal_methods=entry.spell.has_disposal_methods,
                disposal_methods=entry.spell.disposal_method_names,
            )
        self.values[entry] = value
        return value


class ClaimCoordinator:
    """Own stable per-entry locks and retry only before user construction.

    A failed nonblocking acquisition releases every earlier claim before waiting
    for the contested entry. This avoids waiting on sibling B while retaining A
    when another batch holds B and requests A. It is a bounded scheduling proof;
    contention fairness and native compiler integration are not qualified here.
    """

    def __init__(self) -> None:
        """Initialize scope-lifetime lock records and optional scheduling probes."""
        self.entries: dict[tuple[int, str], Entry] = {}
        self.index_lock = RLock()
        self.waiting = Event()
        self.after_first: Optional[Callable[[], None]] = None
        self.attempts = 0

    def cleanup(self) -> None:
        """Release registry references after all workers and batches are quiescent."""
        self.entries.clear()
        self.after_first = None

    def entry(self, store: Creations, spell: Spell) -> Entry:
        """Get a stable claim identity without holding the registry lock during acquisition."""
        assert spell.existence is not Existence.many
        key = (id(store), spell.spell_id)
        with self.index_lock:
            entry = self.entries.get(key)
            if entry is None:
                entry = Entry(store, spell)
                self.entries[key] = entry
            return entry

    def claim(self, requested: Sequence[Entry]) -> ClaimBatch:
        """Acquire the complete known set or release all before waiting/retrying.

        Contract:
            A retry has no constructors or registrations to roll back. Reads
            happen after writer acquisition and are repeated on every attempt.
            No store lock is held when waiting for a writer. Duplicate entries
            are acquired once. This prototype uses a predeclared candidate set;
            compact-plan demand discovery still needs the corresponding adapter.
        """
        entries = tuple(dict.fromkeys(requested))
        for _attempt in range(32):
            with self.index_lock:
                self.attempts += 1
            held: list[Entry] = []
            values: dict[Entry, object] = {}
            contested = None
            try:
                for entry in entries:
                    if not entry.lock.acquire(False):
                        contested = entry
                        break
                    held.append(entry)
                    if len(held) == 1 and self.after_first is not None:
                        self.after_first()
                    with entry.store._lock:
                        if entry.spell.spell_id in entry.store._creations:
                            values[entry] = entry.store._creations[entry.spell.spell_id]
                if contested is None:
                    batch = ClaimBatch(held, values)
                    held = []
                    return batch
            finally:
                for entry in reversed(held):
                    entry.lock.release()
            self.waiting.set()
            # No held entry or store lock reaches this blocking operation.
            if not contested.lock.acquire(timeout=5):
                raise TimeoutError("Contested diagnostic entry did not become available.")
            contested.lock.release()
        raise RuntimeError("Diagnostic retry bound reached before any constructor ran.")

    def purge(self, entry: Entry) -> int:
        """Detach under the entry claim, then invoke native disposal helpers after release.

        Wrapping the whole native purge call would keep the added entry lock
        held during disposal. Separate its existing detachment/disposal stages
        so this experimental writer claim obeys the same cleanup boundary.
        """
        with entry.lock:
            count, retired, disposal = entry.store._detach_purge_entries(
                entry.spell, purge_all=True, creation=None,
            )
        errors: list[Exception] = []
        if isinstance(disposal, tuple):
            error = entry.store._attempt_cleanup(disposal)
            if error is not None:
                errors.append(error)
        elif isinstance(disposal, list):
            errors.extend(entry.store._dispose_many_creations(disposal))
        del retired
        if errors:
            raise ExceptionGroup("Errors occurred during diagnostic entry purge", errors)
        return count


class FirstRound:
    """Force opposite first claims once per worker without affecting retries."""

    def __init__(self) -> None:
        """Initialize a two-worker rendezvous and synchronized membership."""
        self.barrier = Barrier(2)
        self.seen: set[str] = set()
        self.lock = RLock()

    def meet(self) -> None:
        """Rendezvous on the first acquisition only; later attempts proceed normally."""
        name = current_thread().name
        with self.lock:
            if name in self.seen:
                return
            self.seen.add(name)
        self.barrier.wait(timeout=5)


def run_controls() -> list[dict[str, object]]:
    """Exercise claim contention, opposite order, failure release and native purge.

    Uses one real Book and creations store. The experiment publishes through
    native Creations and validates retrieval through the public reuse-only door.
    Compiler-generated execution, gate coverage and performance remain separate.
    """
    world = World()
    coordinator = ClaimCoordinator()
    rows: list[dict[str, object]] = []
    try:
        world.setup_model("entry-claim-controls", NativeRoot, (
            (NativeLeaf, Existence.unique), (NativeParent, Existence.unique_per_conduit),
        ))
        store = world.conduit._meld._conduit_creations
        leaf_spell = next(spell for spell in world.book._spell_id_pool.values() if spell.spell is NativeLeaf)
        parent_spell = next(spell for spell in world.book._spell_id_pool.values() if spell.spell is NativeParent)
        leaf = coordinator.entry(store, leaf_spell)
        parent = coordinator.entry(store, parent_spell)
        results: list[object] = []
        errors: list[Exception] = []

        def build(entries: tuple[Entry, ...]) -> None:
            """Run one complete claim attempt and surface expected diagnostic failures."""
            try:
                with coordinator.claim(entries) as claims:
                    child = claims.get_or_create(leaf, NativeLeaf)
                    result = claims.get_or_create(parent, lambda: NativeParent(child))
                    results.append(result)
            except (RuntimeError, ValueError, TypeError) as error:
                errors.append(error)

        # Mirror the native inversion control: child writer held, parent first.
        leaf.lock.acquire()
        worker = Thread(target=build, args=((parent, leaf),), name="claim-first", daemon=True)
        worker.start()
        try:
            assert coordinator.waiting.wait(5)
            assert parent.lock.acquire(False), "A waiter retained its earlier parent claim."
            parent.lock.release()
            assert store._lock.acquire(False), "A waiter retained the container store lock."
            store._lock.release()
            assert world.conduit.purge(NativeLeaf) == 0
        finally:
            leaf.lock.release()
            worker.join(5)
        assert not worker.is_alive() and not errors and len(results) == 1
        assert world.conduit.meld_existing_spell(spell=NativeParent) is results[0]
        rows.append({"case": "wait_releases_parent_and_store", "native_purge_completed": True,
                     "native_retrieval_identity": True, "attempts": coordinator.attempts})

        parent_lock = parent.lock
        assert coordinator.purge(parent) == 1 and coordinator.purge(leaf) == 1
        assert coordinator.entry(store, parent_spell).lock is parent_lock
        rows.append({"case": "purge_preserves_claim_identity", "removed": 2})

        # Opposite ordering cannot wait while retaining a sibling claim.
        results.clear()
        rendezvous = FirstRound()
        coordinator.after_first = rendezvous.meet
        first = Thread(target=build, args=((parent, leaf),), name="claim-left", daemon=True)
        second = Thread(target=build, args=((leaf, parent),), name="claim-right", daemon=True)
        first.start()
        second.start()
        first.join(5)
        second.join(5)
        assert not first.is_alive() and not second.is_alive() and not errors
        assert len(results) == 2 and results[0] is results[1]
        rows.append({"case": "opposite_order_batches", "same_parent": True,
                     "same_child": results[0].child is results[1].child})
        coordinator.after_first = None

        assert coordinator.purge(parent) == 1

        def fail() -> object:
            """Fail before publication to verify the batch releases its writer claims."""
            raise ValueError("expected construction failure")

        try:
            with coordinator.claim((parent,)) as claims:
                claims.get_or_create(parent, fail)
        except ValueError as error:
            assert str(error) == "expected construction failure"
        else:
            raise AssertionError("Expected construction failure was lost.")
        assert not world.conduit.has_live_creation(spell=NativeParent)
        with coordinator.claim((parent, leaf)) as claims:
            child = claims.get_or_create(leaf, NativeLeaf)
            rebuilt = claims.get_or_create(parent, lambda: NativeParent(child))
        assert world.conduit.meld_existing_spell(spell=NativeParent) is rebuilt
        rows.append({"case": "failure_releases_claims", "next_creation_succeeds": True})
        return rows
    finally:
        coordinator.cleanup()
        world.cleanup()


def main() -> None:
    """Persist bounded protocol evidence and confirm production source stayed unchanged."""
    directory = Path(__file__).resolve().parent
    before = _source_fingerprints(directory.parents[2])
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    cases = run_controls()
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "diagnostic_sha256": own_hash,
              "cases": cases, "limits": "Protocol-only over native stores; all writers must participate; no compiler/gate/timing qualification."}
    (directory / "entry_claim_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
