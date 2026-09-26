"""
Component tests for deferred reference counting of Melder's runtime graph (free-threaded CPython).

Purpose:
    Conjure, executor hydration, pooled scope shells and fast meld door entries hand
    `RefcountDeferral` the long-lived objects every melding thread reads, so on a free-threaded
    CPython 3.14 those loads skip reference counting. These tests drive real bind -> conjure ->
    meld -> scope flows and pin both halves of the contract: the kernel objects are deferred, and
    application objects are not - they are still released the moment Melder lets go of them,
    without waiting for the garbage collector.

Oracle:
    `_is_deferred` asks the interpreter once per object, as the final observation (asking defers
    an object that was not deferred yet).
"""

import gc
import weakref
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.helpers.refcount_deferral import RefcountDeferral

requires_deferral = pytest.mark.skipif(
    not RefcountDeferral.available(),
    reason="deferred reference counting needs a free-threaded CPython 3.14 build",
)


def _reset_runtime() -> None:
    """Reset the Nexus and Aether singletons and rebind the class-level Aether references."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_runtime_for_refcount_deferral() -> Iterator[None]:
    """
    Reset singleton runtime state around every test.

    Yields:
        None.
    """
    _reset_runtime()
    yield
    _reset_runtime()


def _is_deferred(obj: object) -> bool:
    """
    Return whether `obj` already uses deferred reference counting (final observation only).

    Args:
        obj: A garbage-collected object.

    Returns:
        bool: True when the interpreter reports it was already deferred.
    """
    enable = RefcountDeferral._ENABLE
    assert enable is not None
    return enable(obj) == 0


class Settings:
    """Application singleton."""


class Session:
    """Application object scoped to one lesser conduit."""

    def __init__(self, settings: Settings) -> None:
        """Keep the singleton."""
        self.settings = settings


class Request:
    """Application object scoped to one spellspace."""

    def __init__(self, session: Session) -> None:
        """Keep the enclosing session."""
        self.session = session


def _world() -> tuple:
    """
    Bind three application classes, conjure, and return the pieces the tests inspect.

    Returns:
        tuple: (spellbook, conduit, settings_id, session_id, request_id).
    """
    book = Spellbook()
    settings_id = book.bind(spell=Settings, existence=Existence.unique)
    session_id = book.bind(spell=Session, existence=Existence.unique_per_conduit)
    request_id = book.bind(spell=Request, existence=Existence.unique_per_spell_space)
    conduit = book.conjure()
    return book, conduit, settings_id, session_id, request_id


@requires_deferral
def test_conjure_defers_the_spellbook_the_root_runtime_and_every_spell() -> None:
    """After conjure the kernel that every thread reads is deferred."""
    book, conduit, settings_id, session_id, request_id = _world()
    spells = [book._spells_by_id[spell_id] for spell_id in (settings_id, session_id, request_id)]
    assert _is_deferred(book)
    assert _is_deferred(conduit)
    assert _is_deferred(conduit._meld)
    assert _is_deferred(conduit._creations)
    assert all(_is_deferred(spell) for spell in spells)
    conduit.cleanup()
    book.cleanup()


@requires_deferral
def test_first_meld_defers_its_door_entry_and_hydrated_executor_but_not_the_object() -> None:
    """The memoized fast-door entry and the hot executor are deferred; the melded object is not."""
    book, conduit, settings_id, session_id, request_id = _world()
    settings = conduit.meld(spell_id=settings_id)
    entry = conduit._meld._fast_meld_doors[settings_id]
    executor = book._spells_by_id[settings_id]._creation_context._no_overrides_instance_executor
    assert _is_deferred(entry)
    assert _is_deferred(executor)
    assert not _is_deferred(settings)
    conduit.cleanup()
    book.cleanup()


@requires_deferral
def test_new_pooled_scope_shells_are_deferred() -> None:
    """A newly built lesser shell and spellspace shell are deferred before any other thread leases them."""
    book, conduit, settings_id, session_id, request_id = _world()
    lesser = conduit.create_lesser_conduit()
    space = lesser.enter_spellspace().__enter__()
    request = space.meld(spell_id=request_id)
    assert _is_deferred(lesser)
    assert _is_deferred(lesser._meld)
    assert _is_deferred(space)
    assert _is_deferred(space._meld)
    assert not _is_deferred(request)
    space.__exit__(None, None, None)
    lesser.cleanup()
    conduit.cleanup()
    book.cleanup()


def test_application_objects_are_released_without_a_collection() -> None:
    """Scope exit and cleanup still release application objects immediately (no garbage collection)."""
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        book, conduit, settings_id, session_id, request_id = _world()
        lesser = conduit.create_lesser_conduit()
        with lesser.enter_spellspace() as space:
            request = space.meld(spell_id=request_id)
            request_ref = weakref.ref(request)
            session_ref = weakref.ref(request.session)
            settings_ref = weakref.ref(request.session.settings)
            del request
        assert request_ref() is None
        lesser.cleanup()
        assert session_ref() is None
        conduit.cleanup()
        book.cleanup()
        assert settings_ref() is None
    finally:
        if was_enabled:
            gc.enable()
