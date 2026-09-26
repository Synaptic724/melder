"""Exercise compact generated calls with demanded claims and real native stores.

This is an integration experiment outside the normal Meld implementation. It
does not qualify unsupported signatures, hooks, transfer, full validation or
all disposal lifetimes. Native public lookup checks the actual published values.
"""

import hashlib
import json
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from threading import Thread
from types import FrameType
from typing import TYPE_CHECKING, Optional

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
    CompactGraph,
    CompactPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_claim_prelude import (
    CompactClaimPrelude,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    FiveRoot,
    Leaf,
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924.entry_claim_probe import (
    ClaimCoordinator,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_admission_probe import (
    DynamicWorld,
    GateConsumer,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_compact_adapter import (
    NativeCompactAdapter,
)
from context_compass.artifacts.override_structural_discovery_20260924.native_lock_probe import (
    NativeLeaf,
    NativeParent,
)
from context_compass.artifacts.override_structural_discovery_20260924.review_alias_demand import (
    CachedParent,
    FreshParent,
    ReuseAliasRoot,
    SharedService,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)

if TYPE_CHECKING:
    from melder.aether.conduit.spell_space.spell_space import SpellSpace


class NativeConsumer:
    """A many root over a reusable parent, with independent caller input."""

    def __init__(self, parent: NativeParent, value: int = 0) -> None:
        """Borrow the resolved parent and retain this call's plain value."""
        self.parent = parent
        self.value = value


class FailingConsumer:
    """Expose constructor failure after its dependencies have been published."""

    def __init__(self, parent: NativeParent, fail: bool = False) -> None:
        """Raise on request to prove that application construction is never replayed."""
        if fail:
            raise ValueError("expected root construction failure")
        self.parent = parent


@contextmanager
def prepared(world: World, raw: dict[str, object], *, space: Optional[SpellSpace] = None) -> Iterator[NativeCompactAdapter]:
    """Own one compact program, prelude and native adapter; preserve the native world."""
    graph = CompactGraph.from_world(world)
    plan = CompactPlan(graph, tuple(raw))
    prelude = CompactClaimPrelude(plan)
    coordinator = ClaimCoordinator()
    adapter = NativeCompactAdapter(world, plan, prelude.prepare, coordinator,
                                   world.conduit._meld if space is None else space._meld,
                                   explicit_space=space is not None)
    try:
        yield adapter
    finally:
        adapter.cleanup()
        coordinator.cleanup()
        prelude.cleanup()
        plan.cleanup()
        graph.cleanup()


def observe(call: Callable[[], object], error: Optional[type[Exception]] = None) -> tuple[object, list[str]]:
    """Record application constructors only and restore the calling thread's profiler."""
    calls: list[str] = []

    def trace(frame: FrameType, event: str, arg: object) -> None:
        """Exclude compilation, admission and artifact helper construction from the count."""
        if (event == "call" and frame.f_code.co_name == "__init__"
                and frame.f_code.co_filename.endswith(("native_compact_probe.py", "native_lock_probe.py",
                                                      "review_alias_demand.py", "graph_slice_probe.py"))):
            calls.append(type(frame.f_locals["self"]).__qualname__)

    previous = sys.getprofile()
    sys.setprofile(trace)
    try:
        if error is None:
            result = call()
        else:
            with pytest.raises(error):
                call()
            result = None
    finally:
        sys.setprofile(previous)
    return result, calls


def many_control() -> dict[str, object]:
    """Run the five-dependency reduction with zero shared-store callbacks."""
    world = World()
    try:
        world.setup_model("native-compact-many", FiveRoot, ((Leaf, Existence.many),))
        raw = {"a": None, "b": False, "c": object()}
        with prepared(world, raw) as adapter:
            (result, selected, attempts), calls = observe(partial(adapter.execute, raw))
            assert isinstance(result, FiveRoot)
            assert result.a is None and result.b is False and result.c is raw["c"]
            assert calls == ["Leaf", "Leaf", "FiveRoot"] and selected == () and attempts == 1
            return {"case": "five_many", "constructors": calls, "shared_claims": 0}
    finally:
        world.cleanup()


def reuse_and_purge_control() -> dict[str, object]:
    """Skip an absent child under a live parent, then recreate after parent purge."""
    world = World()
    try:
        world.setup_model("native-compact-reuse", NativeConsumer, (
            (NativeLeaf, Existence.unique), (NativeParent, Existence.unique_per_conduit),
        ))
        with prepared(world, {"value": 1}) as adapter:
            (first, cold_selected, _), cold_calls = observe(partial(adapter.execute, {"value": 1}))
            parent_index = next(index for index, spell in enumerate(adapter.spells) if spell.spell is NativeParent)
            leaf_index = next(index for index, spell in enumerate(adapter.spells) if spell.spell is NativeLeaf)
            assert world.conduit.meld_existing_spell(spell=NativeParent) is first.parent
            assert world.conduit.meld_existing_spell(spell=NativeLeaf) is first.parent.child
            assert adapter.coordinator.purge(adapter.entries[leaf_index]) == 1
            (warm, warm_selected, _), warm_calls = observe(partial(adapter.execute, {"value": 2}))
            assert warm.parent is first.parent and warm.value == 2
            assert warm_selected == (parent_index,) and warm_calls == ["NativeConsumer"]
            assert not world.conduit.has_live_creation(spell=NativeLeaf)
            assert adapter.coordinator.purge(adapter.entries[parent_index]) == 1
            (fresh, fresh_selected, _), fresh_calls = observe(partial(adapter.execute, {"value": 3}))
            assert fresh.parent is not first.parent and fresh.parent.child is not first.parent.child
            assert len(cold_calls) == len(fresh_calls) == 3
            assert cold_selected == fresh_selected == (parent_index, leaf_index)
            return {"case": "reuse_then_purge", "cold_constructors": cold_calls,
                    "warm_constructors": warm_calls, "fresh_constructors": fresh_calls,
                    "unused_child_claimed": False, "native_store_identity": True}
    finally:
        world.cleanup()


def alias_control() -> dict[str, object]:
    """Resolve the earlier alias counterexample with a native retained parent/store."""
    world = World()
    try:
        world.setup_model("native-compact-alias", ReuseAliasRoot, (
            (SharedService, Existence.unique_per_conduit),
            (CachedParent, Existence.unique_per_conduit), (FreshParent, Existence.many),
        ))
        external = SharedService(77)
        parent = world.conduit.meld(spell=CachedParent, override={"service": external})
        assert world.conduit.purge(SharedService) == 1
        raw = {"cached>service>value": 21, "fresh>service>value": 91}
        with prepared(world, raw) as adapter:
            (result, selected, _), calls = observe(partial(adapter.execute, raw))
            assert result.cached is parent and result.cached.service is external
            assert result.fresh.service.value == 91
            assert world.conduit.meld_existing_spell(spell=SharedService) is result.fresh.service
            assert calls == ["SharedService", "FreshParent", "ReuseAliasRoot"]
            return {"case": "native_reused_alias", "constructors": calls, "active_value": 91,
                    "selected_count": len(selected), "native_store_identity": True}
    finally:
        world.cleanup()


def contention_control() -> dict[str, object]:
    """Retry a blocked prelude and observe another call's publication without rebuilding it."""
    world = World()
    try:
        world.setup_model("native-compact-contention", NativeConsumer, (
            (NativeLeaf, Existence.unique), (NativeParent, Existence.unique_per_conduit),
        ))
        with prepared(world, {"value": 1}) as adapter:
            parent_index = next(index for index, spell in enumerate(adapter.spells) if spell.spell is NativeParent)
            entry = adapter.entries[parent_index]
            outcomes: list[tuple[object, tuple[int, ...], int]] = []

            def worker() -> None:
                """Request the same shared parent while its claim is deliberately held."""
                outcomes.append(adapter.execute({"value": 9}))

            entry.lock.acquire()
            thread = Thread(target=worker, name="native-compact-contender", daemon=True)
            thread.start()
            try:
                assert adapter.retry_waiting.wait(5)
                published, _selected, _attempts = adapter.execute({"value": 8})
            finally:
                entry.lock.release()
                thread.join(5)
            assert not thread.is_alive() and len(outcomes) == 1
            resumed, selected, attempts = outcomes[0]
            assert resumed.parent is published.parent and resumed.value == 9 and published.value == 8
            assert selected == (parent_index,) and attempts >= 2
            return {"case": "competing_publication", "same_parent": True, "attempts": attempts,
                    "unused_child_claimed_after_retry": False}
    finally:
        world.cleanup()


def failure_control() -> dict[str, object]:
    """Prove no constructor replay and release claims for a succeeding second thread."""
    world = World()
    try:
        world.setup_model("native-compact-failure", FailingConsumer, (
            (NativeLeaf, Existence.unique), (NativeParent, Existence.unique_per_conduit),
        ))
        with prepared(world, {"fail": True}) as adapter:
            _, calls = observe(partial(adapter.execute, {"fail": True}), ValueError)
            assert calls == ["NativeLeaf", "NativeParent", "FailingConsumer"]
            outcomes: list[tuple[object, tuple[int, ...], int]] = []
            thread = Thread(target=lambda: outcomes.append(adapter.execute({"fail": False})), daemon=True)
            thread.start()
            thread.join(5)
            assert not thread.is_alive() and len(outcomes) == 1
            result, _selected, attempts = outcomes[0]
            assert result.parent is world.conduit.meld_existing_spell(spell=NativeParent) and attempts == 1
            return {"case": "constructor_failure", "constructors_before_error": calls,
                    "constructor_replayed": False, "second_thread_succeeded": True}
    finally:
        world.cleanup()


def dynamic_control(explicit_space: bool) -> dict[str, object]:
    """Keep native Conduit/index admission across integrated selection and construction."""
    world = DynamicWorld()
    try:
        world.setup(f"compact-dynamic-{explicit_space}", GateConsumer, Existence.many)
        world.conduit.meld(spell=GateConsumer)
        assert world.conduit.purge(NativeLeaf) == 1
        space = world.conduit.create_spellspace() if explicit_space else None
        snapshots: list[tuple[int, int]] = []
        root = world.book._spell_id_pool[world.root_id]
        gate = root._creation_context._creation_gate

        def observe_gates() -> None:
            """Read the real ticket counts from inside the generated application call."""
            snapshots.append((world.conduit._creation_gate.active_ticket_count(), gate.active_ticket_count()))

        raw = {"callback": observe_gates}
        with prepared(world, raw, space=space) as adapter:
            result, selected, attempts = adapter.execute(raw)
            assert isinstance(result, GateConsumer) and attempts == 1 and len(selected) == 1
            assert snapshots == [(0 if explicit_space else 1, 1)]
            assert world.conduit.meld_existing_spell(spell=NativeLeaf) is result.child
            gate.close_and_wait_until_free(timeout=1, interval=0.001)
            with pytest.raises(RuntimeError, match="CreationGate is closed"):
                adapter.execute(raw)
            assert len(snapshots) == 1
            assert gate.active_ticket_count() == world.conduit._creation_gate.active_ticket_count() == 0
            return {"case": "dynamic_space" if explicit_space else "dynamic_conduit",
                    "constructor_tickets": snapshots[0], "terminal_refused": True, "tickets_after": 0}
    finally:
        world.cleanup()


def main() -> None:
    """Write integration observations and assert production/artifact source stability."""
    directory = Path(__file__).resolve().parent
    peer = directory.parent / "override_occurrence_discovery_20260924"
    scripts = (Path(__file__), directory / "native_compact_adapter.py", directory / "entry_claim_probe.py",
               peer / "compact_claim_prelude.py", peer / "compact_alias_plan.py", peer / "compact_alias_emitter.py")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in scripts}
    before = _source_fingerprints(directory.parents[2])
    cases = [many_control(), reuse_and_purge_control(), alias_control(), contention_control(),
             failure_control(), dynamic_control(False), dynamic_control(True)]
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed and all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name] for path in scripts)
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "scripts_sha256": hashes,
              "cases": cases, "limits": "Experimental adapter/protocol; prevalidated class fixtures and native gates; full validation/transfer/hook integration and production throughput remain unqualified."}
    (directory / "native_compact_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
