"""
Contract tests for RefcountDeferral (deferred reference counting for Melder-owned objects).

Purpose:
    On free-threaded CPython 3.14, `RefcountDeferral.defer_graph` moves the Melder-owned part
    of an object graph to deferred reference counting so that other threads load those objects
    without atomic reference-count traffic. These tests pin the selection rules: which objects
    are deferred, which are only searched, which are never entered, when the walk descends, and
    that the whole feature is a no-op where the interpreter does not support it.

Oracle:
    The interpreter's own `PyUnstable_Object_EnableDeferredRefcount` returns 0 for an object
    that is already deferred and 1 when it defers it now. `_is_deferred` asks it once per object
    as the final observation (asking defers an object that was not, so each object is asked at
    most once and last).
"""

import sys
import sysconfig
import threading
from typing import Any, Callable, Dict, List

import pytest

from melder.aether.conduit.creations.creations import Creations
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.refcount_deferral import RefcountDeferral

requires_deferral = pytest.mark.skipif(
    not RefcountDeferral.available(),
    reason="deferred reference counting needs a free-threaded CPython 3.14 build",
)


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


def _store() -> Creations:
    """Return a fresh, empty Melder creations store (a slotted Melder class holding three dicts)."""
    return Creations(owner_conduit_id="conduit-under-test", id="scope-under-test")


class UserService:
    """An application object: never deferred, never entered."""

    def __init__(self, payload: object = None) -> None:
        """Keep an optional payload so tests can hide Melder objects behind a user object."""
        self.payload = payload


class UserCleanable(Cleanable):
    """A user subclass of a Melder base class: it belongs to the user, not to Melder."""

    __slots__ = ["store"]

    def __init__(self, store: Creations) -> None:
        """Hold a Melder store."""
        super().__init__()
        self.store = store

    def cleanup(self) -> None:
        """Satisfy the Cleanable contract."""
        self._cleaned = True


class RaisingDict(dict):
    """A dict whose keys cannot be read, standing in for one that changes size during the walk."""

    def keys(self) -> Any:
        """Fail the way a dict mutated during iteration fails."""
        raise RuntimeError("dictionary changed size during iteration")


def test_available_matches_free_threaded_cpython() -> None:
    """Deferral is offered exactly on free-threaded CPython builds."""
    expected = sys.implementation.name == "cpython" and bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    assert RefcountDeferral.available() is expected


def test_unavailable_interpreter_makes_every_walk_a_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without the C function every walk returns 0 and defers nothing."""
    store = _store()
    enable = RefcountDeferral._ENABLE
    monkeypatch.setattr(RefcountDeferral, "_ENABLE", None)
    assert RefcountDeferral.available() is False
    assert RefcountDeferral.defer_graph(store, {"k": store}, [store]) == 0
    monkeypatch.setattr(RefcountDeferral, "_ENABLE", enable)
    if enable is not None:
        assert not _is_deferred(store)


@requires_deferral
def test_melder_instance_and_its_empty_stores_are_deferred() -> None:
    """A Melder instance is deferred together with the containers it owns."""
    store = _store()
    assert RefcountDeferral.defer_graph(store) >= 4
    assert _is_deferred(store)
    assert _is_deferred(store._creations)
    assert _is_deferred(store._disposable_creations)
    assert _is_deferred(store._slot_guards)


@requires_deferral
def test_second_walk_defers_nothing_new() -> None:
    """Walking an already deferred graph again is a no-op."""
    store = _store()
    RefcountDeferral.defer_graph(store)
    assert RefcountDeferral.defer_graph(store) == 0


@requires_deferral
def test_user_instance_root_is_neither_deferred_nor_entered() -> None:
    """A user object is skipped, so a Melder object reachable only through it is not reached."""
    store = _store()
    service = UserService(payload=store)
    assert RefcountDeferral.defer_graph(service) == 0
    assert not _is_deferred(store)
    assert not _is_deferred(service)


@requires_deferral
def test_user_subclass_of_a_melder_base_is_a_user_object() -> None:
    """Ownership follows the concrete class: a user subclass of Cleanable is not Melder's."""
    store = _store()
    holder = UserCleanable(store)
    assert RefcountDeferral.defer_graph(holder) == 0
    assert not _is_deferred(store)
    assert not _is_deferred(holder)


@requires_deferral
def test_container_holding_a_user_object_is_searched_but_not_deferred() -> None:
    """A container that holds a user object keeps normal counting; Melder objects in it are deferred."""
    store = _store()
    service = UserService()
    mixed: Dict[str, object] = {"service": service, "store": store}
    RefcountDeferral.defer_graph(mixed)
    assert _is_deferred(store)
    assert not _is_deferred(mixed)
    assert not _is_deferred(service)


@requires_deferral
def test_nested_userfree_containers_are_deferred() -> None:
    """Containers whose nested contents are all Melder-safe are deferred at every level."""
    store = _store()
    inner: List[object] = [store, "id", 3, None]
    outer: Dict[str, object] = {"inner": inner, "kind": int}
    RefcountDeferral.defer_graph(outer)
    assert _is_deferred(outer)
    assert _is_deferred(inner)
    assert _is_deferred(store)


@requires_deferral
def test_nested_container_with_a_user_object_blocks_its_parents() -> None:
    """One user object deep inside makes every enclosing container foreign."""
    service = UserService()
    inner: List[object] = [service]
    outer: Dict[str, object] = {"inner": inner}
    RefcountDeferral.defer_graph(outer)
    assert not _is_deferred(outer)
    assert not _is_deferred(inner)
    assert not _is_deferred(service)


@requires_deferral
def test_closure_is_deferred_and_module_globals_are_not_entered() -> None:
    """A closure, its cell and the Melder object it captured are deferred; its globals are left alone."""
    store = _store()

    def make_door(captured: Creations) -> Callable[[], Creations]:
        def door() -> Creations:
            return captured
        return door

    door = make_door(store)
    cell = door.__closure__[0]
    RefcountDeferral.defer_graph(door)
    assert _is_deferred(door)
    assert _is_deferred(cell)
    assert _is_deferred(store)
    assert not _is_deferred(UserService.__init__.__globals__["_GLOBAL_PROBE"])


@requires_deferral
def test_already_deferred_objects_are_not_descended_but_roots_are() -> None:
    """A later walk stops at deferred interior objects; naming the object as a root reaches new contents."""
    first = _store()
    members: List[object] = [first]

    def make_door(captured: List[object]) -> Callable[[], List[object]]:
        def door() -> List[object]:
            return captured
        return door

    door = make_door(members)
    RefcountDeferral.defer_graph(door)
    second = _store()
    members.append(second)
    RefcountDeferral.defer_graph(door)
    # The door is a root and is descended; its cell and the list were deferred by the first walk,
    # so the walk stops there and never reaches the store appended since.
    assert not _is_deferred(second)
    later = _store()
    members.append(later)
    RefcountDeferral.defer_graph(members)
    assert _is_deferred(later)
    assert _is_deferred(first)


@requires_deferral
def test_container_that_cannot_be_read_is_left_alone() -> None:
    """A container whose contents change while they are read is neither deferred nor searched."""
    store = _store()
    unreadable = RaisingDict(store=store)
    assert RefcountDeferral.defer_graph(unreadable) == 0
    assert not _is_deferred(unreadable)
    assert not _is_deferred(store)


@requires_deferral
def test_types_modules_code_and_thread_locals_are_skipped() -> None:
    """Classes, modules, code objects and thread-local objects are never deferred by the walk."""
    code = test_types_modules_code_and_thread_locals_are_skipped.__code__
    assert RefcountDeferral.defer_graph(Creations, sys, code, threading.local()) == 0


_GLOBAL_PROBE: Dict[str, object] = {"probe": UserService}
