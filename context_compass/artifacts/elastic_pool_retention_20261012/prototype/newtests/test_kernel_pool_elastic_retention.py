"""Kernel pools keep what a burst needed and let it go when quiet (0.2.8234).

Why component tests:
    The contracts run through a real root conduit, its ConduitPool and its SpellSpacePool - the pools the runtime
    takes every lesser conduit and every managed spellspace from - so they prove what a caller of
    `create_lesser_conduit()` and `enter_spellspace()` observes. The pool clock is swapped through `_time_func`, the
    seam the pool unit tests use, so 30-minute settle and 10-minute decay periods run instantly.

Contracts under test:
    - A burst of lessers past the 20 always kept is kept whole on return, and repeating it reuses every shell
      (through 0.2.8233 the pool kept 20 and rebuilt the rest on every repeat).
    - A burst of nested managed spellspaces past 20 is kept the same way.
    - A burst past `max_idle` (256) keeps 256 and destroys the rest.
    - With no miss for the settle time the root keeps fewer: one decay step per interval, back to the baseline
      after a long quiet, oldest shells first; a later burst is kept whole again.
    - `prewarm_lesser_conduits` and `prewarm_spellspaces` keep up to `max_idle`, not 20.
"""

from collections.abc import Iterator
from contextlib import ExitStack
import time
from typing import Any, List

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


class _Clock:
    """Hand-advanced monotonic clock that starts at the real monotonic time."""

    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = time.monotonic()

    def __call__(self) -> float:
        return self.value


def _make_root(frame: str = "kernel-pool-retention") -> Conduit:
    """
    Build a real empty automatic root with one phase worker and no runtime cache writes.

    Contract:
        The caller owns the returned root's cleanup.
    """
    configuration = SpellbookConfiguration(frame).with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    if not book._aetheric_frame_configuration._frozen:
        posture = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
        posture.with_system_caching_enabled(False)
    try:
        return book.conjure(name="kernel_pool_root")
    except Exception:
        book.cleanup()
        raise


@pytest.fixture
def root() -> Iterator[Conduit]:
    """Own one root and tear it down, with its pools, after each test."""
    conduit = _make_root()
    try:
        yield conduit
    finally:
        conduit.permanent_cleanup()


def _lesser_burst(root: Conduit, count: int) -> List[Any]:
    """Hold `count` lessers at once, return them all, and hand back the shells (kept referenced)."""
    held = [root.create_lesser_conduit() for _ in range(count)]
    for lesser in held:
        lesser.cleanup()
    return held


def _space_burst(root: Conduit, count: int) -> List[Any]:
    """Hold `count` nested managed spellspaces on one conduit, exit them all, and hand back the spaces."""
    with ExitStack() as stack:
        held = [stack.enter_context(root.enter_spellspace()) for _ in range(count)]
    return held


def _lesser_cycle(root: Conduit) -> None:
    """One ordinary scope cycle: take one lesser (a hit while any is idle) and return it."""
    root.create_lesser_conduit().cleanup()


def test_repeat_lesser_burst_past_twenty_reuses_every_shell(root: Conduit) -> None:
    """A burst of 30 lessers is kept whole and its repeat builds no new shell."""
    pool = root._conduit_pool
    first = _lesser_burst(root, 30)

    assert pool.idle_count == 30
    assert pool.target_idle == 30
    second = _lesser_burst(root, 30)
    assert {id(shell) for shell in second} == {id(shell) for shell in first}
    assert not any(shell._cleaned for shell in first)


def test_repeat_spellspace_burst_past_twenty_reuses_every_space(root: Conduit) -> None:
    """30 nested managed spellspaces are kept on exit and the next 30 reuse them all."""
    pool = root._spellspace_pool
    first = _space_burst(root, 30)

    assert pool.idle_count == 30
    assert pool.target_idle == 30
    second = _space_burst(root, 30)
    assert {id(space) for space in second} == {id(space) for space in first}


def test_lesser_burst_past_max_idle_keeps_max_idle(root: Conduit) -> None:
    """A burst past max_idle keeps max_idle shells and destroys exactly the rest."""
    pool = root._conduit_pool
    count = pool.max_idle + 20
    held = _lesser_burst(root, count)

    assert pool.max_idle == 256
    assert pool.idle_count == pool.max_idle
    assert pool.target_idle == pool.max_idle
    assert sum(1 for shell in held if shell._cleaned) == 20


def test_quiet_root_pool_decays_to_baseline_and_burst_restretches(root: Conduit) -> None:
    """Settle, one decay step per interval, catch-up after a long quiet, then a new burst kept whole."""
    pool = root._conduit_pool
    clock = _Clock()
    pool._time_func = clock
    held = _lesser_burst(root, 40)
    settle = pool.describe()["settle_time_seconds"]
    interval = pool.describe()["decay_interval_seconds"]

    clock.value += settle - 1.0
    _lesser_cycle(root)
    assert pool.target_idle == 40

    clock.value += 1.0
    _lesser_cycle(root)
    assert pool.target_idle == 36
    assert pool.idle_count == 36
    assert sum(1 for shell in held if shell._cleaned) == 4

    clock.value += interval
    _lesser_cycle(root)
    assert pool.target_idle == 32

    clock.value += 10 * 3600.0
    _lesser_cycle(root)
    assert pool.target_idle == pool.baseline_idle == 20
    for _ in range(4):
        _lesser_cycle(root)
    assert pool.idle_count == 20

    _lesser_burst(root, 40)
    assert pool.target_idle == 40
    assert pool.idle_count == 40


def test_prewarm_keeps_more_than_twenty_shells(root: Conduit) -> None:
    """Prewarming 40 lessers and 40 spellspaces leaves 40 of each idle."""
    assert root.prewarm_lesser_conduits(40) == 40
    assert root._conduit_pool.idle_count == 40
    assert root.prewarm_spellspaces(40) == 40
    assert root._spellspace_pool.idle_count == 40
