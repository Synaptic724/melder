"""Regression: BUG-002 (2026-07-17 audit) - Aether initialization is once-only.

Symptom:
    Two threads racing the first ``Aether()`` construction both passed the
    unguarded ``_initialized`` test in ``__init__`` and built the subsystem
    graph twice on the same instance (audit repro: ``same_instance=True``,
    ``crystallizers_created=2``).

Contract under test:
    The ``_initialized`` check and the whole construction body run under
    ``Aether._lock``. Exactly one thread constructs the subsystem graph; a
    concurrent first caller blocks on the class lock until construction
    completes and then receives the same, fully initialized singleton.
"""

import threading
from typing import Dict, Iterator, List, Optional

import pytest

from melder.aether import aether as aether_module
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def fresh_singletons() -> Iterator[None]:
    """Reset the Aether/Nexus/utility singletons around each test.

    Contract:
        - Discards any pre-existing singleton state before the test body runs
          so the test exercises a true first construction.
        - Restores clean singleton state afterwards so later tests are not
          coupled to this module's raced instances.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()


def test_concurrent_first_construction_builds_subsystem_graph_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two threads racing the first ``Aether()`` must construct exactly once.

    Choreography (deterministic interleave, mirrors the audit probe):
        1. Thread A enters the construction body; the wrapped ``Crystallizer``
           constructor records the entry, signals ``entered``, and parks on
           ``release`` while still inside the body (holding ``Aether._lock``
           under the fixed contract).
        2. Thread B calls ``Aether()`` while A is parked mid-body. Under the
           fixed contract B blocks on ``Aether._lock`` and never enters the
           body; on the broken code B entered the body and bumped the
           construction count to 2.
        3. ``release`` opens; both threads finish and must hold the same,
           fully initialized singleton.

    Contract assertions:
        - The construction body ran exactly once.
        - Both threads received the identical singleton object.
        - The singleton the blocked caller received is fully constructed
          (lifecycle-safety: no partially built root escapes ``Aether()``).
    """
    construction_entries: List[int] = []
    entered = threading.Event()
    release = threading.Event()
    original_crystallizer = aether_module.Crystallizer

    def counting_crystallizer(*args: object, **kwargs: object) -> Crystallizer:
        """Record one construction-body entry, park, then delegate.

        Contract:
            - Appends one entry per call so the test can count how many
              threads entered the ``Aether.__init__`` construction body.
            - Signals ``entered`` and waits on ``release`` so the test
              controls the interleave deterministically.
            - Delegates to the real ``Crystallizer`` so the singleton the
              winning thread builds is fully functional.
        """
        construction_entries.append(1)
        entered.set()
        assert release.wait(timeout=10.0), "release event never opened"
        return original_crystallizer(*args, **kwargs)

    results: Dict[str, Optional[Aether]] = {"a": None, "b": None}
    errors: List[Exception] = []

    def build(slot: str) -> None:
        """Construct the singleton from one racing thread.

        Test-harness note: the broad ``except Exception`` exists only to
        surface cross-thread construction failures back into the main
        assertion flow; it re-raises nothing and hides nothing.
        """
        try:
            results[slot] = Aether()
        except Exception as exc:
            errors.append(exc)

    monkeypatch.setattr(aether_module, "Crystallizer", counting_crystallizer)
    thread_a = threading.Thread(target=build, args=("a",), name="aether-boot-a")
    thread_b = threading.Thread(target=build, args=("b",), name="aether-boot-b")
    try:
        thread_a.start()
        assert entered.wait(timeout=10.0), (
            "first builder never entered the construction body"
        )
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "second caller returned while the first build was still in flight; "
            "it must block on Aether._lock until construction completes"
        )
    finally:
        release.set()
    thread_a.join(timeout=10.0)
    thread_b.join(timeout=10.0)

    assert not thread_a.is_alive(), "thread A did not finish"
    assert not thread_b.is_alive(), "thread B did not finish"
    assert errors == [], f"racing construction raised: {errors!r}"
    assert len(construction_entries) == 1, (
        "the Aether construction body ran "
        f"{len(construction_entries)} times; the once-only contract requires 1"
    )
    assert results["a"] is results["b"], (
        "racing callers received different Aether objects"
    )
    assert Aether._initialized is True
    winner = results["a"]
    assert winner is not None
    assert isinstance(winner._crystallizer, Crystallizer)
    assert isinstance(winner._nexus, Nexus)


def test_sequential_reconstruction_reuses_singleton_without_rebuilding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A second sequential ``Aether()`` call must not re-enter the body.

    Contract assertions:
        - After the first boot completes, ``Aether()`` returns the same
          instance on the lock-free fast path without reconstructing any
          subsystem (the patched ``Crystallizer`` seam is never called).
    """
    first = Aether()

    def failing_crystallizer(*args: object, **kwargs: object) -> Crystallizer:
        """Fail loudly if the construction body runs a second time."""
        raise AssertionError(
            "Aether construction body re-ran for an already-initialized "
            "singleton"
        )

    monkeypatch.setattr(aether_module, "Crystallizer", failing_crystallizer)
    second = Aether()
    assert second is first
    assert Aether._initialized is True
