"""Regression: BUG-003 (2026-07-17 audit) - Nexus initialization is once-only.

Symptom:
    Two threads racing the first ``Nexus()`` construction both passed the
    unguarded ``_initialized`` test in ``__init__`` and built the manager
    graph twice on the same instance (audit repro: ``same_instance=True``,
    ``gate_controllers_created=2``).

Contract under test:
    The ``_initialized`` check and the whole manager-graph construction run
    under ``Nexus._lock``. Exactly one thread constructs the singleton state;
    a concurrent first caller blocks on the class lock until construction
    completes and then receives the same, fully initialized singleton.
"""

import threading
from typing import Dict, Iterator, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus import nexus as nexus_module
from melder.nexus.nexus import Nexus
from melder.nexus.rift.rift_gate_controller.rift_gate_controller import (
    RiftGateController,
)


@pytest.fixture(autouse=True)
def fresh_singletons() -> Iterator[None]:
    """Reset the Aether/Nexus/utility singletons around each test.

    Contract:
        - Discards any pre-existing singleton state before the test body runs.
        - Restores clean singleton state afterwards so the raced Nexus and its
          hosting Aether never leak into later tests.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def test_concurrent_first_construction_builds_manager_graph_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two threads racing the first ``Nexus()`` must construct exactly once.

    Setup:
        A real ``Aether`` boots first (which eagerly builds the hosted Nexus),
        then ``Nexus._reset_singleton_for_tests()`` clears the Nexus singleton
        so the test can stage a true concurrent first construction against a
        live substrate.

    Choreography (deterministic interleave, mirrors the audit probe):
        1. Thread A enters the construction body; the wrapped
           ``RiftGateController`` constructor records the entry, signals
           ``entered``, and parks on ``release`` while still inside the body
           (holding ``Nexus._lock`` under the fixed contract).
        2. Thread B calls ``Nexus(aether=...)`` while A is parked mid-body.
           Under the fixed contract B blocks on ``Nexus._lock`` and never
           enters the body; on the broken code B entered the body and bumped
           the construction count to 2.
        3. ``release`` opens; both threads finish and must hold the same,
           fully initialized singleton.
    """
    aether = Aether()
    Nexus._reset_singleton_for_tests()

    construction_entries: List[int] = []
    entered = threading.Event()
    release = threading.Event()

    def counting_gate_controller(
        *args: object, **kwargs: object
    ) -> RiftGateController:
        """Record one construction-body entry, park, then delegate.

        Contract:
            - Appends one entry per call so the test can count how many
              threads entered the ``Nexus.__init__`` construction body.
            - Signals ``entered`` and waits on ``release`` so the test
              controls the interleave deterministically.
            - Delegates to the real ``RiftGateController`` so the winning
              thread builds a fully functional singleton.
        """
        construction_entries.append(1)
        entered.set()
        assert release.wait(timeout=10.0), "release event never opened"
        return RiftGateController(*args, **kwargs)

    results: Dict[str, Optional[Nexus]] = {"a": None, "b": None}
    errors: List[Exception] = []

    def build(slot: str) -> None:
        """Construct the singleton from one racing thread.

        Test-harness note: the broad ``except Exception`` exists only to
        surface cross-thread construction failures back into the main
        assertion flow; it re-raises nothing and hides nothing.
        """
        try:
            results[slot] = Nexus(aether=aether)
        except Exception as exc:
            errors.append(exc)

    monkeypatch.setattr(
        nexus_module, "RiftGateController", counting_gate_controller
    )
    thread_a = threading.Thread(target=build, args=("a",), name="nexus-boot-a")
    thread_b = threading.Thread(target=build, args=("b",), name="nexus-boot-b")
    try:
        thread_a.start()
        assert entered.wait(timeout=10.0), (
            "first builder never entered the construction body"
        )
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "second caller returned while the first build was still in flight; "
            "it must block on Nexus._lock until construction completes"
        )
    finally:
        release.set()
    thread_a.join(timeout=10.0)
    thread_b.join(timeout=10.0)

    assert not thread_a.is_alive(), "thread A did not finish"
    assert not thread_b.is_alive(), "thread B did not finish"
    assert errors == [], f"racing construction raised: {errors!r}"
    assert len(construction_entries) == 1, (
        "the Nexus construction body ran "
        f"{len(construction_entries)} times; the once-only contract requires 1"
    )
    assert results["a"] is results["b"], (
        "racing callers received different Nexus objects"
    )
    assert Nexus._initialized is True
    winner = results["a"]
    assert winner is not None
    assert isinstance(winner._rift_gate_controller, RiftGateController)
    assert winner._frame_manager is not None


def test_missing_aether_on_first_init_resets_bookkeeping_under_lock() -> None:
    """First construction without an ``Aether`` must fail and reset cleanly.

    Contract assertions:
        - ``Nexus()`` with no substrate raises ``ValueError``.
        - Singleton bookkeeping is reset so a later, properly formed first
          construction succeeds and initializes fully.
    """
    aether = Aether()
    Nexus._reset_singleton_for_tests()

    with pytest.raises(ValueError):
        Nexus()
    assert Nexus._instance is None
    assert Nexus._initialized is False

    rebuilt = Nexus(aether=aether)
    assert Nexus._initialized is True
    assert rebuilt._frame_manager is not None
