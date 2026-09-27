"""
Integration contracts for door-held first builds (0.2.73).

WHAT IS BEING CLAIMED
---------------------
Since 0.2.73 the normal site plan of a `unique_per_conduit` or
`unique_per_spell_space` root no longer re-takes the root's slot guard: the route
door holds that guard from its recheck until the plan returns. Nothing observable
may change. Through the public meld surface, with real doors and real stores:

    - concurrent first melds of one root on one conduit, or in one shared manual
      SpellSpace, construct the root and its dependency exactly once and hand
      every caller the same instance;
    - with an activation hook bound on the root (the hooks lane, whose door
      reports whether the call created the instance), the hook fires exactly once
      for that instance;
    - a same-thread nested override meld of the root, made from a dependency's
      constructor while the outer build is in flight, publishes the root, and the
      outer meld returns that instance instead of constructing a second one.

Timing is only used to widen race windows; every assertion is about identity and
counts, so a slow machine can make a test less sharp but never flaky.
"""

import threading
import time
from threading import Barrier, Thread
from typing import Any, Callable, Dict, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.spellbook import Spellbook

pytestmark = pytest.mark.integration


class ConstructionLog:
    """
    Thread-safe construction counter, bound as a `unique` class spell and injected into the test spells.

    Contract:
        - `record(name)` counts one construction of `name` under an internal lock.
        - `count(name)` reads the current count.
    """

    def __init__(self) -> None:
        """Start with no constructions recorded."""
        self._lock: threading.Lock = threading.Lock()
        self._counts: Dict[str, int] = {}

    def record(self, name: str) -> None:
        """
        Count one construction.

        Args:
            name: Class name of the constructed object.
        """
        with self._lock:
            self._counts[name] = self._counts.get(name, 0) + 1

    def count(self, name: str) -> int:
        """
        Return how many times `name` was constructed.

        Args:
            name: Class name to read.

        Returns:
            int: The construction count (0 when never constructed).
        """
        with self._lock:
            return self._counts.get(name, 0)


class ScopeDependency:
    """Shared dependency of the root; its Existence matches the root's scope in each test."""

    def __init__(self, log: ConstructionLog) -> None:
        """
        Record the construction.

        Args:
            log: The injected construction log.
        """
        log.record("ScopeDependency")
        self.log: ConstructionLog = log


class SlowScopeRoot:
    """Root whose constructor sleeps, so racing first melds overlap its build."""

    BUILD_SECONDS: float = 0.05

    def __init__(self, log: ConstructionLog, dependency: ScopeDependency) -> None:
        """
        Record the construction, then hold the build open for a moment.

        Args:
            log: The injected construction log.
            dependency: The shared scope dependency.
        """
        log.record("SlowScopeRoot")
        time.sleep(SlowScopeRoot.BUILD_SECONDS)
        self.dependency: ScopeDependency = dependency


class NestedDoorHolder:
    """`unique` singleton that arms `NestedMeldDependency` with the conduit to meld through."""

    def __init__(self) -> None:
        """Start unarmed."""
        self.conduit: Optional[Conduit] = None


class NestedMeldDependency:
    """
    `many` dependency of `NestedRoot` that, when armed, melds its own consumer with an override.

    Contract:
        - Unarmed (the default) it only records its construction.
        - Armed, it melds `NestedRoot` on the armed door with `{"marker": "nested"}` from inside its constructor,
          on the same thread as the outer meld whose build is in flight, and keeps what that meld returned.
    """

    def __init__(self, log: ConstructionLog, door: NestedDoorHolder) -> None:
        """
        Record the construction and run the nested meld when armed.

        Args:
            log: The injected construction log.
            door: The holder whose conduit, when set, arms the nested meld (None when unarmed).
        """
        log.record("NestedMeldDependency")
        self.nested_root: Optional[Any] = None
        conduit = door.conduit
        if conduit is not None:
            door.conduit = None
            self.nested_root = conduit.meld(spell=NestedRoot, override={"marker": "nested"})


class NestedRoot:
    """`unique_per_conduit` root with a `many` dependency and a plain parameter the nested meld overrides."""

    def __init__(self, log: ConstructionLog, dependency: NestedMeldDependency, marker: str = "outer") -> None:
        """
        Record the construction and keep the marker.

        Args:
            log: The injected construction log.
            dependency: The (possibly nested-melding) dependency.
            marker: "outer" by default; the nested override meld passes "nested".
        """
        log.record("NestedRoot")
        self.dependency: NestedMeldDependency = dependency
        self.marker: str = marker


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> Any:
    """
    Give every test a fresh Aether singleton and restore a fresh one afterwards.

    Returns:
        Generator yielding once; rebinds `Spellbook._aether` and `Conduit._aether`.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _conjure_scope_world(
        existence: str,
        frame: str,
        activation_hook: Optional[Callable[..., None]] = None,
) -> Any:
    """
    Bind the log, the dependency and the slow root with one scope Existence and conjure a root conduit.

    Args:
        existence: "unique_per_conduit" or "unique_per_spell_space" for the dependency and the root.
        frame: Aetheric frame name for this world.
        activation_hook: Optional activation hook bound on the root; any spell hook routes its melds
            through the hooks lane, where the door reports whether it created the instance.

    Returns:
        Tuple[Conduit, ConstructionLog]: The conjured root conduit and the one ConstructionLog instance.
    """
    book = Spellbook(aetheric_frame=frame)
    book.bind(spell=ConstructionLog, existence="unique")
    book.bind(spell=ScopeDependency, existence=existence)
    if activation_hook is None:
        book.bind(spell=SlowScopeRoot, existence=existence)
    else:
        book.bind(spell=SlowScopeRoot, existence=existence, activation_hooks=[activation_hook])
    conduit = book.conjure(name=frame)
    return conduit, conduit.meld(spell=ConstructionLog)


def _race(meld_once: Callable[[], Any], threads: int) -> List[Any]:
    """
    Run `meld_once` on `threads` threads released together; return every result or raise the first error.

    Args:
        meld_once: The meld call each thread makes.
        threads: Number of racing threads.

    Returns:
        List[Any]: One result per thread.

    Raises:
        AssertionError: When a thread failed or did not finish within the timeout.
    """
    barrier = Barrier(threads)
    results: List[Any] = []
    errors: List[BaseException] = []
    guard = threading.Lock()

    def worker() -> None:
        try:
            barrier.wait(timeout=10)
            result = meld_once()
            with guard:
                results.append(result)
        except BaseException as exc:  # recorded and re-raised by the test thread
            with guard:
                errors.append(exc)

    workers = [Thread(target=worker, name=f"first-meld-{index}") for index in range(threads)]
    for worker_thread in workers:
        worker_thread.start()
    for worker_thread in workers:
        worker_thread.join(timeout=30)
    assert not any(worker_thread.is_alive() for worker_thread in workers), "a racing meld did not finish"
    assert errors == [], errors
    return results


def test_racing_first_melds_on_one_conduit_build_the_per_conduit_root_once() -> None:
    """Eight threads first-meld one unique_per_conduit root on one conduit: one construction, one instance."""
    conduit, log = _conjure_scope_world("unique_per_conduit", "door-held-conduit")
    try:
        results = _race(lambda: conduit.meld(spell=SlowScopeRoot), threads=8)
        assert len({id(result) for result in results}) == 1
        assert log.count("SlowScopeRoot") == 1
        assert log.count("ScopeDependency") == 1
        assert conduit.meld(spell=SlowScopeRoot) is results[0]
    finally:
        conduit.cleanup()


def test_racing_first_melds_in_one_shared_spellspace_build_the_space_root_once() -> None:
    """Eight threads first-meld one unique_per_spell_space root in one manual space: one construction."""
    conduit, log = _conjure_scope_world("unique_per_spell_space", "door-held-space")
    space: SpellSpace = conduit.create_spellspace()
    try:
        results = _race(lambda: space.meld(spell=SlowScopeRoot), threads=8)
        assert len({id(result) for result in results}) == 1
        assert log.count("SlowScopeRoot") == 1
        assert log.count("ScopeDependency") == 1
        assert space.meld(spell=SlowScopeRoot) is results[0]
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    ("existence", "door"),
    [
        pytest.param("unique_per_conduit", "conduit", id="per_conduit-conduit"),
        pytest.param("unique_per_spell_space", "space", id="spellspace-space"),
    ],
)
def test_activation_hook_fires_once_when_first_melds_race(existence: str, door: str) -> None:
    """With an activation hook on the root (hooks lane), racing first melds fire it exactly once, for the root."""
    activated: List[Any] = []
    activated_lock = threading.Lock()

    def on_activation(instance: Any, *args: Any) -> None:
        with activated_lock:
            activated.append(instance)

    conduit, log = _conjure_scope_world(existence, f"door-held-hook-{door}", on_activation)
    target: Any = conduit if door == "conduit" else conduit.create_spellspace()
    try:
        results = _race(lambda: target.meld(spell=SlowScopeRoot), threads=8)
        assert len({id(result) for result in results}) == 1
        assert log.count("SlowScopeRoot") == 1
        assert len(activated) == 1
        assert activated[0] is results[0]
    finally:
        conduit.cleanup()


def test_nested_same_thread_override_meld_of_the_root_is_returned_by_the_outer_meld() -> None:
    """
    A dependency's constructor melds its own consumer with an override while the consumer's first build is in
    flight on the same thread: the nested meld publishes the root, and the outer meld returns that instance.
    """
    book = Spellbook(aetheric_frame="door-held-nested")
    book.bind(spell=ConstructionLog, existence="unique")
    book.bind(spell=NestedDoorHolder, existence="unique")
    book.bind(spell=NestedMeldDependency, existence="many")
    book.bind(spell=NestedRoot, existence="unique_per_conduit")
    conduit = book.conjure(name="door-held-nested")
    try:
        log = conduit.meld(spell=ConstructionLog)
        conduit.meld(spell=NestedDoorHolder).conduit = conduit
        outer = conduit.meld(spell=NestedRoot)
        assert outer.marker == "nested"
        assert log.count("NestedRoot") == 1
        # The outer build's dependency ran the nested meld; the nested root built its own (unarmed) dependency.
        assert log.count("NestedMeldDependency") == 2
        assert outer.dependency.nested_root is None
        assert conduit.meld(spell=NestedRoot) is outer
    finally:
        conduit.cleanup()
