"""Observe native creation/purge lock ordering without leaving blocked threads.

Real public Meld and purge calls use their normal generated code and stores.
Lock wrappers delegate to the original RLocks. The coordinating thread's one
contended store acquisition raises a diagnostic exception instead of deadlocking;
all other acquisitions preserve normal behavior. No production files change.
"""

import hashlib
import json
import sys
from _thread import RLock
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread, current_thread
from types import TracebackType
from typing import Optional, Self

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    World,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)


class NativeLeaf:
    """Provide one frame-owned unique dependency with no external resources."""

    def __init__(self) -> None:
        """Create a value used to observe the native unique construction branch."""


class NativeParent:
    """Request a unique child while varying the parent's declared lifetime."""

    def __init__(self, child: NativeLeaf, value: int = 0) -> None:
        """Borrow the child and retain a plain input for the override lane."""
        self.child = child
        self.value = value


class NativeRoot:
    """Give the isolated World a harmless root independent of the probed binding."""

    def __init__(self) -> None:
        """Create no dependencies or owned resources."""


class ProbeWouldBlock(RuntimeError):
    """Record an acquisition that would complete the demonstrated wait cycle."""


class Trace:
    """Own a synchronized event list for diagnostic ordering only."""

    def __init__(self) -> None:
        """Initialize detached trace storage and its short-held writer lock."""
        self.rows: list[tuple[str, str, str]] = []
        self.lock = RLock()

    def add(self, label: str, event: str) -> None:
        """Append without holding the diagnostic lock during any native acquisition."""
        with self.lock:
            self.rows.append((current_thread().name, label, event))


class ObservedLock:
    """Borrow an RLock and expose two bounded scheduling controls for this probe.

    Contract:
        Normal acquisition/release delegates directly. A selected caller can
        pause before acquisition, or refuse a contended acquisition immediately.
        The refusal prevents a demonstrated cycle from becoming a stuck process.
        MonkeyPatch restores every original lock before World cleanup.
    """

    def __init__(self, raw: RLock, trace: Trace, label: str) -> None:
        """Retain the real lock and initialize disabled scheduling controls."""
        self.raw = raw
        self.trace = trace
        self.label = label
        self.attempted = Event()
        self.acquired = Event()
        self.paused = Event()
        self.resume = Event()
        self.pause_thread: Optional[str] = None
        self.refuse_thread: Optional[str] = None

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Delegate acquisition, recording when the named worker reaches each lock."""
        name = current_thread().name
        self.trace.add(self.label, "request")
        if name == "native-worker":
            self.attempted.set()
        if name == self.pause_thread:
            self.paused.set()
            if not self.resume.wait(5):
                raise TimeoutError("Diagnostic coordinator did not release the paused lock request.")
        if name == self.refuse_thread:
            result = self.raw.acquire(False)
            if not result:
                self.trace.add(self.label, "would_block")
                raise ProbeWouldBlock(self.label)
        else:
            result = self.raw.acquire(blocking, timeout)
        if result:
            self.trace.add(self.label, "acquired")
            if name == "native-worker":
                self.acquired.set()
        return result

    def release(self) -> None:
        """Release the real lock and record the completed operation."""
        self.raw.release()
        self.trace.add(self.label, "released")

    def __enter__(self) -> Self:
        """Acquire with ordinary context-manager behavior except the explicit probe refusal."""
        self.acquire()
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Release every successful context-manager acquisition, including on failure."""
        self.release()


def lock_order_case(mode: str, existence: Existence, with_overrides: bool) -> dict[str, object]:
    """Exercise a native parent resolution against the unique child's purge order.

    The coordinator first owns the child's real Spell lock. The worker reaches
    that lock through native Meld. Native purge then attempts its own normal
    Spell->store order; a contended store acquisition is refused rather than
    waited on. Releasing the child lock lets the worker finish and proves that
    the instrumentation leaves the live world recoverable.
    """
    world = World()
    trace = Trace()
    try:
        world.setup_model(f"native-order-{mode}-{with_overrides}", NativeRoot, (
            (NativeLeaf, Existence.unique), (NativeParent, existence),
        ))
        door = world.conduit
        if mode == "space":
            door = world.conduit.create_spellspace()
        elif mode == "lesser":
            door = world.conduit.create_lesser_conduit()
        raw = {"value": 7} if with_overrides else None
        # Warm native code and then remove creations, keeping its real compiled context.
        door.meld(spell=NativeParent, override=raw)
        door.purge(NativeParent)
        assert world.conduit.purge(NativeLeaf) == 1
        leaf = next(spell for spell in world.book._spell_id_pool.values() if spell.spell is NativeLeaf)
        owner = leaf._owner_creations
        local = door._meld._spellspace_creations if mode == "space" else door._meld._conduit_creations
        owner_lock = ObservedLock(owner._lock, trace, "owner_store")
        child_lock = ObservedLock(leaf._lock, trace, "child_spell")
        local_lock = owner_lock if local is owner else ObservedLock(local._lock, trace, "caller_store")
        outcomes: list[object] = []
        errors: list[Exception] = []

        def worker() -> None:
            """Invoke the public door; capture errors so the coordinator can always release locks."""
            try:
                outcomes.append(door.meld(spell=NativeParent, override=raw))
            except (MeldExecutionError, RuntimeError, ValueError, TypeError) as error:
                errors.append(error)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(owner, "_lock", owner_lock)
            if local is not owner:
                patch.setattr(local, "_lock", local_lock)
            patch.setattr(leaf, "_lock", child_lock)
            owner_lock.refuse_thread = current_thread().name
            thread = Thread(target=worker, name="native-worker", daemon=True)
            child_lock.raw.acquire()
            try:
                thread.start()
                reached_child = child_lock.attempted.wait(5)
                if not reached_child:
                    raise AssertionError(f"Worker did not reach child lock: {errors!r}; {trace.rows!r}")
                try:
                    purge_count = world.conduit.purge(NativeLeaf)
                except ProbeWouldBlock:
                    purge_blocked = True
                    purge_count = None
                else:
                    purge_blocked = False
                caller_lock_before_child = local_lock.acquired.is_set()
            finally:
                child_lock.raw.release()
                thread.join(5)
            assert not thread.is_alive(), "Native worker failed to finish after lock release."
            assert not errors, errors
            assert len(outcomes) == 1 and isinstance(outcomes[0], NativeParent)
        return {"case": mode, "existence": existence.name, "overrides": with_overrides,
                "caller_store_is_child_owner": local is owner,
                "caller_store_acquired_before_child": caller_lock_before_child,
                "native_purge_would_block": purge_blocked, "purge_count": purge_count,
                "worker_completed_after_release": True, "trace": trace.rows}
    finally:
        world.cleanup()


def competing_publication_case(with_overrides: bool) -> dict[str, object]:
    """Prove that an initial reuse miss can change before the native writer-lock recheck.

    A worker pauses immediately before its first store-lock acquisition. The
    coordinator publishes the same parent through public Meld, then releases
    the worker. Native no-override resolution must reuse that object; an
    override-bearing shared root must retain its existing refusal contract.
    """
    world = World()
    trace = Trace()
    try:
        world.setup_model(f"native-publication-{with_overrides}", NativeRoot, (
            (NativeLeaf, Existence.unique), (NativeParent, Existence.unique_per_conduit),
        ))
        world.conduit.meld(spell=NativeParent)
        assert world.conduit.purge(NativeParent) == 1
        store = world.conduit._meld._conduit_creations
        observed = ObservedLock(store._lock, trace, "caller_store")
        observed.pause_thread = "native-worker"
        outcomes: list[object] = []
        errors: list[Exception] = []

        def worker() -> None:
            """Pause after the initial miss and retain the eventual native outcome."""
            try:
                outcomes.append(world.conduit.meld(
                    spell=NativeParent, override={"value": 7} if with_overrides else None,
                ))
            except (MeldExecutionError, RuntimeError, ValueError, TypeError) as error:
                errors.append(error)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(store, "_lock", observed)
            thread = Thread(target=worker, name="native-worker", daemon=True)
            thread.start()
            try:
                assert observed.paused.wait(5), errors
                published = world.conduit.meld(spell=NativeParent)
            finally:
                observed.resume.set()
                thread.join(5)
            assert not thread.is_alive()
        if with_overrides:
            assert len(errors) == 1 and isinstance(errors[0], MeldExecutionError)
            assert not outcomes
            outcome = "existing_root_override_refused"
        else:
            assert not errors and outcomes == [published]
            assert outcomes[0] is published
            outcome = "concurrent_publication_reused"
        return {"case": "competing_publication", "overrides": with_overrides,
                "outcome": outcome, "trace": trace.rows}
    finally:
        world.cleanup()


def main() -> None:
    """Write native observations with source provenance and no performance claim."""
    directory = Path(__file__).resolve().parent
    before = _source_fingerprints(directory.parents[2])
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    modes = (("many", Existence.many), ("unique", Existence.unique),
             ("conduit", Existence.unique_per_conduit), ("lineage", Existence.unique_per_conduit_lineage),
             ("space", Existence.unique_per_spell_space), ("lesser", Existence.unique_per_conduit))
    for mode, existence in modes:
        for overrides in (False, True):
            rows.append(lock_order_case(mode, existence, overrides))
    for overrides in (False, True):
        rows.append(competing_publication_case(overrides))
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "diagnostic_sha256": own_hash,
              "cases": rows, "limits": "Scheduling instrumentation, not timings; contended purge is refused to avoid deadlock."}
    (directory / "native_lock_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
