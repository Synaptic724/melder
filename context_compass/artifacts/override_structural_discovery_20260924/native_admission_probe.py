"""Check native admission placement and experimental disposal lock boundaries.

Public Conduit/SpellSpace calls remain native. A wrapped gate Event identifies
the exact parked point without a scheduling sleep. Disposal uses the separate
entry-claim experiment over a real bound object's Creations record.
"""

import hashlib
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread
from typing import Optional

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924.entry_claim_probe import (
    ClaimCoordinator,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_lock_probe import (
    NativeLeaf,
)
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)


class GateConsumer:
    """Observe admission tickets from inside a native application constructor."""

    def __init__(self, child: NativeLeaf, callback: Optional[Callable[[], None]] = None) -> None:
        """Borrow the child and invoke the optional diagnostic callback once."""
        self.child = child
        if callback is not None:
            callback()


class DisposableValue:
    """Expose the locks held when native disposal invokes an application's cleanup."""

    def __init__(self, on_cleanup: Optional[Callable[[], None]] = None) -> None:
        """Borrow a diagnostic callback and initialize idempotent disposal state."""
        self._on_cleanup = on_cleanup
        self._closed = False

    def cleanup(self) -> None:
        """Invoke the borrowed observer once, then release it without cleaning it."""
        if self._closed:
            return
        self._closed = True
        if self._on_cleanup is not None:
            self._on_cleanup()
        del self._on_cleanup


class DynamicWorld(World):
    """Use the established teardown with explicitly configured native dynamic binding."""

    def setup(self, name: str, target: type, existence: Existence,
              disposal: Optional[list[str]] = None) -> None:
        """Conjure one uncached dynamic Book with explicit disposal candidates."""
        self.graph, self.root_type = name, target
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        config = SpellbookConfiguration(name).with_defaults()
        config.with_phase_scheduler_workers(1)
        frame = configure_frame_posture_for_spellbook_configuration(config, dynamic=True)
        frame.with_system_caching_enabled(False)
        self.book = Spellbook(aetheric_frame=config._aether_frame, configuration=config)
        self.book.bind(spell=NativeLeaf, existence=Existence.unique, permissions="create")
        self.root_id = self.book.bind(spell=target, existence=existence, permissions="create",
                                      disposal_method_names=disposal)
        self.conduit = self.book.conjure(name="native-admission", dynamic=True)


class ObservedEvent:
    """Borrow a real gate Event and signal when its native wait operation is reached."""

    def __init__(self, raw: Event) -> None:
        """Retain the real event; the probe owns only the arrival notification."""
        self.raw = raw
        self.waiting = Event()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Signal arrival before delegating to the genuine parking event."""
        self.waiting.set()
        return self.raw.wait(timeout)

    def set(self) -> None:
        """Preserve the native open/terminal-wake operation."""
        self.raw.set()

    def clear(self) -> None:
        """Preserve native temporary freezing."""
        self.raw.clear()


def admission_case(explicit_space: bool) -> list[dict[str, object]]:
    """Observe temporary parking, held tickets, construction and terminal refusal."""
    world = DynamicWorld()
    try:
        world.setup(f"native-gate-{explicit_space}", GateConsumer, Existence.many)
        world.conduit.meld(spell=GateConsumer)
        world.conduit.meld(spell=NativeLeaf)
        root = world.book._spell_id_pool[world.root_id]
        leaf = next(spell for spell in world.book._spell_id_pool.values() if spell.spell is NativeLeaf)
        root_gate = root._creation_context._creation_gate
        child_gate = leaf._creation_context._creation_gate
        conduit_gate = world.conduit._creation_gate
        door = world.conduit.create_spellspace() if explicit_space else world.conduit
        snapshots: list[dict[str, int]] = []
        results: list[object] = []
        errors: list[RuntimeError] = []

        def observe() -> None:
            """Capture exact gate cardinalities during native root construction."""
            snapshots.append({"conduit": conduit_gate.active_ticket_count(),
                              "root_index": root_gate.active_ticket_count(),
                              "child_index": child_gate.active_ticket_count()})

        def worker() -> None:
            """Use the public door and preserve runtime refusals for the coordinator."""
            try:
                results.append(door.meld(spell=GateConsumer, override={"callback": observe}))
            except RuntimeError as error:
                errors.append(error)

        root_gate.close_and_drain(timeout=1, interval=0.001)
        observed = ObservedEvent(root_gate._event)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(root_gate, "_event", observed)
            thread = Thread(target=worker, name="native-admission-worker", daemon=True)
            thread.start()
            try:
                assert observed.waiting.wait(5), errors
                parked = {"conduit": conduit_gate.active_ticket_count(),
                          "root_index": root_gate.active_ticket_count()}
                assert not snapshots
                assert parked == {"conduit": 0 if explicit_space else 1, "root_index": 0}
            finally:
                root_gate.open()
                thread.join(5)
            assert not thread.is_alive() and not errors and len(results) == 1
        assert snapshots == [{"conduit": 0 if explicit_space else 1, "root_index": 1, "child_index": 0}]
        assert conduit_gate.active_ticket_count() == root_gate.active_ticket_count() == 0
        rows = [{"case": "explicit_space" if explicit_space else "conduit", "parked": parked,
                 "during_constructor": snapshots[0], "tickets_after": 0}]
        root_gate.close_and_wait_until_free(timeout=1, interval=0.001)
        with pytest.raises(RuntimeError, match="CreationGate is closed"):
            door.meld(spell=GateConsumer, override={"callback": observe})
        assert len(snapshots) == 1 and conduit_gate.active_ticket_count() == root_gate.active_ticket_count() == 0
        rows.append({"case": "terminal_refusal", "explicit_space": explicit_space,
                     "new_constructors": 0, "tickets_after": 0})
        return rows
    finally:
        world.cleanup()


def disposal_case() -> dict[str, object]:
    """Prove the new claim is released before native disposal helpers run user code."""
    world = DynamicWorld()
    coordinator = ClaimCoordinator()
    try:
        world.setup("entry-disposal-locks", DisposableValue, Existence.unique_per_conduit, ["cleanup"])
        spell = world.book._spell_id_pool[world.root_id]
        store = world.conduit._meld._conduit_creations
        entry = coordinator.entry(store, spell)
        seen: list[tuple[bool, bool]] = []
        constructor_store_locks: list[bool] = []

        def disposed() -> None:
            """Use the real RLocks' ownership probes only as test instrumentation."""
            seen.append((entry.lock._is_owned(), store._lock._is_owned()))

        def create() -> DisposableValue:
            """Check that application construction also runs outside the container lock."""
            constructor_store_locks.append(store._lock._is_owned())
            return DisposableValue(disposed)

        assert spell.disposal_method_names == ["cleanup"]
        with coordinator.claim((entry,)) as claims:
            value = claims.get_or_create(entry, create)
        assert world.conduit.meld_existing_spell(spell=DisposableValue) is value
        assert coordinator.purge(entry) == 1
        assert seen == [(False, False)] and constructor_store_locks == [False]
        assert not world.conduit.has_live_creation(spell=DisposableValue)
        return {"case": "disposal_outside_claim_and_store", "disposal_calls": len(seen),
                "entry_lock_held": False, "store_lock_held": False, "constructor_store_lock_held": False}
    finally:
        coordinator.cleanup()
        world.cleanup()


def main() -> None:
    """Persist native admission and explicit disposal observations with source provenance."""
    directory = Path(__file__).resolve().parent
    before = _source_fingerprints(directory.parents[2])
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = admission_case(False) + admission_case(True) + [disposal_case()]
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "diagnostic_sha256": own_hash,
              "cases": rows, "limits": "Admission is native; disposal uses the experimental claim protocol; no full mutation drain or timing qualification."}
    (directory / "native_admission_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
