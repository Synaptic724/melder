"""
Regression: meld input-resolution cache id()-reuse aliasing
(owner finding, 2026-07-12).

Both meld doors used to fall back to raw
`(spell_name, id(spell), id(spellframe), binding_name)` cache keys for
unhashable inputs. id() values outlive their objects: after the original
object dies, CPython may hand its address to a DIFFERENT unhashable
object, whose meld would then HIT the dead entry and resolve the WRONG
spell. The fix makes unhashable inputs skip the cache entirely (resolve
every call, never store). These tests seed the exact poisoned id-shaped
entry the old fallback would have read and prove it can never be served,
and that hashable-input caching still works byte-identically.
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class AliasAlpha:
    """Bound resolution target; the poisoned cache entry points at it."""

    def __init__(self) -> None:
        """Mark liveness for assertions."""
        self.alive: bool = True


class _Unhashable:
    """A deliberately unhashable meld input (the fallback lane's trigger)."""

    __hash__ = None


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_alias_probe():
    """Isolate each test behind fresh world singletons."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _dynamic_conduit_with_alpha():
    """
    Build one dynamic conduit with AliasAlpha bound.

    Returns:
        tuple: (conduit, alpha_spell_id).
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    alpha_id = book.bind(
        spell=AliasAlpha, existence=Existence.unique, permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="alias-probe")
    return conduit, alpha_id


def test_poisoned_id_keyed_entry_is_never_served_for_unhashable_input():
    """
    Purpose:
        Reproduce the pre-fix poisoning: seed the cache with the exact
        id-shaped key the old fallback would build for this unhashable
        input, pointing at a real bound spell. On the fixed runtime the
        unhashable meld must NEVER serve that entry - it resolves
        uncached and refuses honestly.
    Contract:
        - meld(spell=<unhashable>) raises a resolution error; it must not
          return an AliasAlpha instance via the poisoned entry.
    """
    conduit, alpha_id = _dynamic_conduit_with_alpha()
    try:
        stale_input = _Unhashable()
        poisoned_key = (None, id(stale_input), id(None), None)
        # The exact entry the removed fallback would have read on a
        # cache hit (spell_name, id(spell), id(spellframe), binding_name).
        conduit._meld._input_resolution_cache[poisoned_key] = alpha_id

        with pytest.raises((KeyError, TypeError, ValueError, RuntimeError)) as refusal:
            result = conduit.meld(spell=stale_input)
            # Belt-and-braces: if some resolution lane ever accepts the
            # input, serving the poisoned target is still the failure.
            assert not isinstance(result, AliasAlpha), (
                "POISONED: the unhashable input was served the id-keyed "
                "cache entry - the aliasing fix regressed."
            )
        assert refusal is not None
    finally:
        conduit.cleanup()


def test_unhashable_input_never_writes_the_resolution_cache():
    """
    Purpose:
        Prove the skip-cache lane: a failed unhashable meld leaves the
        input-resolution cache without ANY id-shaped entry (pre-fix the
        fallback at least attempted id-keyed reads and successful
        resolutions would have stored id-keyed rows).
    Contract:
        - After the refusal, no cache key contains a raw int (the
          id-shape signature); hashable-input caching still stores.
    """
    conduit, _alpha_id = _dynamic_conduit_with_alpha()
    try:
        cache = conduit._meld._input_resolution_cache
        cache.clear()

        with pytest.raises((KeyError, TypeError, ValueError, RuntimeError)):
            conduit.meld(spell=_Unhashable())
        for key in cache:
            assert not any(isinstance(part, int) for part in key), (
                f"id-shaped cache key leaked past the fix: {key!r}"
            )

        # Hashable parity: a class input still caches exactly one entry.
        instance = conduit.meld(spell=AliasAlpha)
        assert isinstance(instance, AliasAlpha)
        assert any(
            isinstance(key, tuple) and AliasAlpha in key for key in cache
        )
    finally:
        conduit.cleanup()
