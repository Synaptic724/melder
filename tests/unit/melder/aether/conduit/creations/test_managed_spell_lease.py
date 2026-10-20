"""
Unit tests of ManagedSpellLease, one leased object and the pool it goes back to (STORY-2026-10-15-release_managed_spell).

Scope:
    The lease on its own over a real pool: the object it carries, release once (later calls do nothing), the object
    refused after release, the `with` block (returns the object, releases on success and on error, never suppresses),
    and a release that raises (a failing reset, a torn-down pool) still ending the lease.
"""
from typing import List, Optional, Tuple

import pytest

from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode


class Leased:
    """A managed object whose resets and disposals write to a class-level log."""

    log: List[str] = []

    def __init__(self, label: str = "obj", *, fail_reset: bool = False) -> None:
        """
        Keep a label and the reset failure switch.

        Args:
            label: Name written to the log.
            fail_reset: Whether `reset` raises after logging.
        """
        self.label = label
        self.fail_reset = fail_reset

    def reset(self) -> None:
        """Log one reset, then fail when asked to."""
        Leased.log.append(f"reset:{self.label}")
        if self.fail_reset:
            raise ValueError(f"reset failed: {self.label}")

    def close(self) -> None:
        """Log one disposal."""
        Leased.log.append(f"close:{self.label}")


class _SpellStub:
    """The Spell fields a pool reads, for an elastic binding of `Leased`."""

    def __init__(self, resets: Tuple[str, ...] = ()) -> None:
        """
        Keep the identity and the options.

        Args:
            resets: The reset method names.
        """
        self.spell_id = "lease-sid"
        self.spell = Leased
        self.spell_name = "Leased"
        self.binding_name = None
        self.aetheric_frame = "default"
        self.existence = Existence.managed_spell_quantity
        self.disposal_method_names = ["close"]
        self.managed_spell_mode = ManagedSpellMode.elastic
        self.managed_spell_limit = 256
        self.managed_spell_timeout_seconds = None
        self.managed_spell_reset_methods = tuple(resets)
        self.spell_index = SpellIndex("lease-sid")

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """Return the index."""
        return self.spell_index


@pytest.fixture(autouse=True)
def empty_log() -> None:
    """An empty log per test."""
    Leased.log = []


def _leased(resets: Tuple[str, ...] = (), **object_options: object) -> Tuple[ManagedSpellQuantity, Leased]:
    """
    One pool and one object counted out of it.

    Args:
        resets: The pool's reset names.
        **object_options: `Leased` keywords.

    Returns:
        Tuple[ManagedSpellQuantity, Leased]: The pool and the object out.
    """
    pool = ManagedSpellQuantity(spell=_SpellStub(resets), owner_conduit_id="root-1")
    assert pool.reserve() is None
    return pool, Leased(**object_options)


def test_the_lease_carries_its_object_until_released() -> None:
    """`object` is the leased object; a fresh lease is not released."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    assert lease.object is obj
    assert lease.released is False


def test_release_puts_the_object_back_once() -> None:
    """The first release pools the object; the lease reports it."""
    pool, obj = _leased(("reset",))
    lease = ManagedSpellLease(obj, pool)
    lease.release()
    assert lease.released is True
    assert pool.idle_count == 1
    assert Leased.log == ["reset:obj"]


def test_a_second_release_does_nothing() -> None:
    """Releasing twice never pools the object twice."""
    pool, obj = _leased(("reset",))
    lease = ManagedSpellLease(obj, pool)
    lease.release()
    lease.release()
    assert pool.idle_count == 1
    assert Leased.log == ["reset:obj"]


def test_the_object_is_refused_after_release() -> None:
    """A released lease no longer hands out the pooled object."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    lease.release()
    with pytest.raises(RuntimeError) as caught:
        _ = lease.object
    assert str(caught.value) == "This ManagedSpellLease was released; its object went back to its pool."


def test_the_with_block_gets_the_object_and_releases_it_on_exit() -> None:
    """`__enter__` returns the object; leaving the block releases it."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    with lease as entered:
        assert entered is obj
        assert pool.idle_count == 0
    assert lease.released is True
    assert pool.idle_count == 1


def test_the_with_block_releases_when_it_raises_and_lets_the_error_through() -> None:
    """An error in the block still gives the object back, and is never suppressed."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    with pytest.raises(KeyError, match="boom"):
        with lease:
            raise KeyError("boom")
    assert lease.released is True
    assert pool.idle_count == 1


def test_exit_never_suppresses() -> None:
    """`__exit__` answers a falsy value even for an error."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    lease.__enter__()
    assert not lease.__exit__(KeyError, KeyError("boom"), None)
    assert lease.released is True


def test_a_release_whose_reset_raises_still_ends_the_lease() -> None:
    """The pool destroys the object and the error propagates; a second release does nothing."""
    pool, obj = _leased(("reset",), fail_reset=True)
    lease = ManagedSpellLease(obj, pool)
    with pytest.raises(ValueError, match="reset failed: obj"):
        lease.release()
    assert lease.released is True
    lease.release()
    assert (pool.idle_count, pool.count) == (0, 0)
    assert Leased.log == ["reset:obj", "close:obj"]


def test_a_release_into_a_torn_down_pool_ends_the_lease_and_raises() -> None:
    """The pool's torn-down error reaches the holder; the object stays the holder's."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    pool.cleanup()
    with pytest.raises(RuntimeError, match="was torn down with its root conduit"):
        lease.release()
    assert lease.released is True
    lease.release()


def test_a_with_block_over_an_already_released_lease_does_not_release_again() -> None:
    """Entering a released lease refuses, so nothing is pooled twice."""
    pool, obj = _leased()
    lease = ManagedSpellLease(obj, pool)
    lease.release()
    with pytest.raises(RuntimeError, match="was released"):
        with lease:
            pass
    assert pool.idle_count == 1
