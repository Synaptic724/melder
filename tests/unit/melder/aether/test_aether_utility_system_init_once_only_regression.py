"""Regression: BUG-146 (2026-07-17 audit) - utility-system init is once-only.

Symptom:
    ``AetherUtilitySystem.__new__`` published the singleton identity under the
    class lock, but ``__init__`` ran its whole body and the ``_initialized``
    latch outside it. Two constructors racing the first boot both entered the
    init body on the same object; the delayed second body reset every provider
    field, silently erasing a channel-logger resolver the first thread had
    already registered (audit repro: resolver presence flipped true -> false).

Contract under test:
    The ``_initialized`` check and the whole init body run under
    ``_singleton_lock`` (double-checked initialization). Exactly one thread
    initializes the provider surface; a completed provider registration can
    never be erased by another constructor of the same singleton.
"""

import threading
from typing import Any, Dict, Iterator, List, Optional

import pytest

from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.utilities.general_base.cleanable import Cleanable


@pytest.fixture(autouse=True)
def fresh_utility_singleton() -> Iterator[None]:
    """Reset the utility-system singleton around each test.

    Contract:
        - Discards any pre-existing singleton state before the test body runs
          so the test exercises a true first construction.
        - Restores clean singleton state afterwards so later tests are not
          coupled to this module's raced instances.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()


def test_concurrent_first_construction_cannot_erase_provider_registration() -> None:
    """A delayed second constructor must not re-run init and erase providers.

    Choreography (deterministic interleave, mirrors the audit probe):
        1. Thread A enters the init body; the gated ``Cleanable.__init__``
           wrapper records the entry, signals it, and parks on a per-entry
           release event while still inside the body (holding
           ``_singleton_lock`` under the fixed contract).
        2. Thread B calls ``AetherUtilitySystem()`` while A is parked
           mid-body. Under the fixed contract B blocks on the singleton lock
           and never enters the body; on the broken code B entered the body
           and parked as a second entrant.
        3. A's release opens; A finishes and the test registers a
           channel-logger resolver through the completed singleton.
        4. B's release opens; on the broken code B's delayed body now reset
           the provider fields and erased the registration. Under the fixed
           contract B re-checks the latch and touches nothing.

    Contract assertions:
        - The init body ran exactly once.
        - Both threads received the identical singleton object.
        - The resolver registered after the winning build is still present.
    """
    entries: List[int] = []
    entry_lock = threading.Lock()
    entered_events = [threading.Event(), threading.Event()]
    release_events = [threading.Event(), threading.Event()]
    original_cleanable_init = Cleanable.__init__

    def gated_cleanable_init(instance: Cleanable) -> None:
        """Record and gate utility-system init-body entries.

        Contract:
            - Only gates ``AetherUtilitySystem`` construction; every other
              ``Cleanable`` subclass initializes normally.
            - Assigns each entrant its own entered/release event pair so the
              test can release the first builder while holding the second
              (the audit's delayed-second-constructor interleave).
        """
        if isinstance(instance, AetherUtilitySystem):
            with entry_lock:
                index = len(entries)
                entries.append(index)
            if index < len(entered_events):
                entered_events[index].set()
                assert release_events[index].wait(timeout=10.0), (
                    f"release event {index} never opened"
                )
        original_cleanable_init(instance)

    results: Dict[str, Optional[AetherUtilitySystem]] = {"a": None, "b": None}
    errors: List[Exception] = []

    def build(slot: str) -> None:
        """Construct the singleton from one racing thread.

        Test-harness note: the broad ``except Exception`` exists only to
        surface cross-thread construction failures back into the main
        assertion flow; it hides nothing.
        """
        try:
            results[slot] = AetherUtilitySystem()
        except Exception as exc:
            errors.append(exc)

    Cleanable.__init__ = gated_cleanable_init
    thread_a = threading.Thread(target=build, args=("a",), name="utility-boot-a")
    thread_b = threading.Thread(target=build, args=("b",), name="utility-boot-b")
    try:
        thread_a.start()
        assert entered_events[0].wait(timeout=10.0), (
            "first builder never entered the init body"
        )
        thread_b.start()
        thread_b.join(timeout=0.5)
        assert thread_b.is_alive(), (
            "second caller returned while the first build was still in "
            "flight; it must block on _singleton_lock until init completes"
        )

        release_events[0].set()
        thread_a.join(timeout=10.0)
        assert not thread_a.is_alive(), "thread A did not finish"
        winner = results["a"]
        assert winner is not None

        def resolver(**kwargs: Any) -> None:
            """Minimal channel-logger resolver double for registration."""
            return None

        winner.register_channel_logger_resolver(resolver)
        assert winner.has_channel_logger_resolver() is True

        release_events[1].set()
        thread_b.join(timeout=10.0)
        assert not thread_b.is_alive(), "thread B did not finish"
    finally:
        for event in release_events:
            event.set()
        Cleanable.__init__ = original_cleanable_init

    assert errors == [], f"racing construction raised: {errors!r}"
    assert len(entries) == 1, (
        f"the init body ran {len(entries)} times; the once-only contract "
        "requires 1"
    )
    assert results["a"] is results["b"], (
        "racing callers received different utility-system objects"
    )
    assert winner.has_channel_logger_resolver() is True, (
        "a completed provider registration was erased by a delayed second "
        "constructor (the audited BUG-146 symptom)"
    )
    assert AetherUtilitySystem._initialized is True


def test_sequential_reconstruction_skips_init_body() -> None:
    """A second sequential constructor must fast-path without re-entering.

    Contract assertions:
        - After the first boot completes, ``AetherUtilitySystem()`` returns
          the same instance without re-running ``Cleanable.__init__`` (the
          init-body seam is never re-entered).
        - Provider registrations survive the second construction.
    """
    first = AetherUtilitySystem()

    def resolver(**kwargs: Any) -> None:
        """Minimal channel-logger resolver double for registration."""
        return None

    first.register_channel_logger_resolver(resolver)
    original_cleanable_init = Cleanable.__init__

    def failing_cleanable_init(instance: Cleanable) -> None:
        """Fail loudly if the init body runs a second time."""
        if isinstance(instance, AetherUtilitySystem):
            raise AssertionError(
                "AetherUtilitySystem init body re-ran for an "
                "already-initialized singleton"
            )
        original_cleanable_init(instance)

    Cleanable.__init__ = failing_cleanable_init
    try:
        second = AetherUtilitySystem()
    finally:
        Cleanable.__init__ = original_cleanable_init

    assert second is first
    assert first.has_channel_logger_resolver() is True
    assert AetherUtilitySystem._initialized is True
