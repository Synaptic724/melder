"""
Contract tests for conjure's owner wiring of the versions a Book parked before conjure
(STORY-2026-10-16-parked_versions_wired_at_conjure, 0.2.8248).

`SpellbookCreationSystem.define_conduit_into_spells` runs once, at the conjure tail. It wires every active version
of the Book as before - the owner stamp, `resolution_required` False, an existing object registered in the root's
store - and then every version in `_inactive_spells` with the same owner stamp a post-conjure `bind_inactive`
applies, and nothing else: a parked version is not live until a notch promotes it. These tests pin the stamp's
arguments, what a parked version does not get, the per-version failure policy and the lock the stamps run under.
"""

import threading
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem


class _StampCall:
    """One recorded `_add_owned_conduit` call: the arguments and whether the Book lock was held."""

    def __init__(
            self,
            conduit_id: str,
            conduit_name: Optional[str],
            creations: Any,
            dynamic_environment: bool,
            creation_gate_controller: Any,
            caching_enabled: bool,
            book_lock_held: bool,
    ) -> None:
        """
        Keep the call's arguments.

        Args:
            conduit_id: The owner root's id.
            conduit_name: The owner root's name.
            creations: The owner root's store.
            dynamic_environment: The root's dynamic flag.
            creation_gate_controller: The root's gate controller.
            caching_enabled: The Book's caching posture.
            book_lock_held: Whether another thread was kept out of the Book lock during the call.
        """
        self.conduit_id: str = conduit_id
        self.conduit_name: Optional[str] = conduit_name
        self.creations: Any = creations
        self.dynamic_environment: bool = dynamic_environment
        self.creation_gate_controller: Any = creation_gate_controller
        self.caching_enabled: bool = caching_enabled
        self.book_lock_held: bool = book_lock_held

    def arguments(self) -> Tuple[Any, ...]:
        """
        Return the stamp's arguments, without the lock observation.

        Returns:
            Tuple[Any, ...]: (conduit id, name, store, dynamic flag, gate controller, caching posture).
        """
        return (
            self.conduit_id,
            self.conduit_name,
            self.creations,
            self.dynamic_environment,
            self.creation_gate_controller,
            self.caching_enabled,
        )


class _SpellStub:
    """The Spell surface the owner wiring reads and writes."""

    def __init__(
            self,
            spell_id: str,
            book: "_BookStub",
            *,
            existing_object: Any = None,
            resolution_required: bool = False,
            raise_on_stamp: bool = False,
    ) -> None:
        """
        Build a spell stub.

        Args:
            spell_id: The spell's spell_id.
            book: The Book stub whose lock a stamp is expected to run under.
            existing_object: The bound existing object, or None for a class or function spell.
            resolution_required: The flag's starting value.
            raise_on_stamp: Whether `_add_owned_conduit` raises (after recording the call).
        """
        self.spell_id: str = spell_id
        self._book: "_BookStub" = book
        self.user_created_object: Any = existing_object
        self.resolution_required: bool = resolution_required
        self._owner_creations: Any = None
        self._raise_on_stamp: bool = raise_on_stamp
        self.stamps: List[_StampCall] = []

    def _add_owned_conduit(
            self,
            conduit_id: str,
            conduit_name: Optional[str] = None,
            creations: Any = None,
            *,
            dynamic_environment: bool,
            creation_gate_controller: Any,
            caching_enabled: bool,
    ) -> None:
        """
        Record the stamp, then raise when configured to, else take the store as the owner store.

        Raises:
            RuntimeError: When the stub was built with `raise_on_stamp=True`.
        """
        self.stamps.append(
            _StampCall(
                conduit_id,
                conduit_name,
                creations,
                dynamic_environment,
                creation_gate_controller,
                caching_enabled,
                self._book.lock_is_held_elsewhere(),
            )
        )
        if self._raise_on_stamp:
            raise RuntimeError(f"stamp of {self.spell_id} failed")
        self._owner_creations = creations


class _ConduitStub:
    """The Conduit surface the owner wiring reads, and its existing-object registrations."""

    def __init__(self, *, dynamic: bool) -> None:
        """
        Build a root stub.

        Args:
            dynamic: The root's dynamic flag.
        """
        self._id: str = "root-id"
        self._name: str = "root"
        self._creations: object = object()
        self.__dynamic_environment__: bool = dynamic
        self._creation_gate_controller: object = object()
        self.registered: List[Tuple[str, Any]] = []

    def _register_to_creations(self, spell: _SpellStub, instance: Any) -> None:
        """
        Record an existing-object registration.

        Args:
            spell: The registered version.
            instance: Its existing object.
        """
        self.registered.append((spell.spell_id, instance))


class _LoggerStub:
    """Collects error calls as (message, method tag, exc_info)."""

    def __init__(self) -> None:
        """Start with no errors."""
        self.errors: List[Tuple[str, str, bool]] = []

    def error(self, message: str, method_name: str, exc_info: bool = False) -> None:
        """
        Record one error call.

        Args:
            message: The message.
            method_name: The method tag.
            exc_info: Whether the traceback was requested.
        """
        self.errors.append((message, method_name, exc_info))


class _BookStub:
    """The Spellbook surface the owner wiring reads: the lock, both version maps, the caching posture, the logger."""

    def __init__(self, *, caching_enabled: bool) -> None:
        """
        Build an empty Book stub.

        Args:
            caching_enabled: What `_resolve_system_caching_enabled` answers.
        """
        self._lock: threading.RLock = threading.RLock()
        self._spells: Dict[object, _SpellStub] = {}
        self._inactive_spells: Dict[str, _SpellStub] = {}
        self._logger: _LoggerStub = _LoggerStub()
        self._caching_enabled: bool = caching_enabled

    def _resolve_system_caching_enabled(self) -> bool:
        """
        Return the Book's caching posture.

        Returns:
            bool: The configured posture.
        """
        return self._caching_enabled

    def add_active(self, spell: _SpellStub) -> None:
        """
        Publish an active version under a fresh index key.

        Args:
            spell: The active version.
        """
        self._spells[object()] = spell

    def add_parked(self, spell: _SpellStub) -> None:
        """
        Park a version, as `bind_inactive` does.

        Args:
            spell: The parked version.
        """
        self._inactive_spells[spell.spell_id] = spell

    def lock_is_held_elsewhere(self) -> bool:
        """
        Report whether another thread is kept out of the Book lock right now.

        Returns:
            bool: True when a non-blocking acquire from another thread fails.
        """
        acquired: List[bool] = []

        def try_acquire() -> None:
            """Try the lock once without blocking; release it again when taken."""
            taken = self._lock.acquire(blocking=False)
            acquired.append(taken)
            if taken:
                self._lock.release()

        prober = threading.Thread(target=try_acquire)
        prober.start()
        prober.join()
        return not acquired[0]


@pytest.mark.parametrize(("caching_enabled", "dynamic"), [(True, True), (False, True), (True, False)])
def test_every_parked_version_gets_the_stamp_the_active_versions_get(caching_enabled: bool, dynamic: bool) -> None:
    """
    Every parked version is stamped once, with the arguments of the active loop: the root's id, name and store, its
    dynamic flag and gate controller, and the Book's caching posture.
    """
    book = _BookStub(caching_enabled=caching_enabled)
    active = _SpellStub("active", book)
    parked = [_SpellStub("parked-1", book), _SpellStub("parked-2", book)]
    book.add_active(active)
    for spell in parked:
        book.add_parked(spell)
    conduit = _ConduitStub(dynamic=dynamic)

    SpellbookCreationSystem.define_conduit_into_spells(book, conduit)

    expected = (
        conduit._id,
        conduit._name,
        conduit._creations,
        dynamic,
        conduit._creation_gate_controller,
        caching_enabled,
    )
    assert [call.arguments() for call in active.stamps] == [expected]
    for spell in parked:
        assert [call.arguments() for call in spell.stamps] == [expected]
        assert spell._owner_creations is conduit._creations
    assert book._logger.errors == []


def test_the_parked_stamps_run_under_the_book_lock() -> None:
    """Parked versions are stamped while the Book lock is held, as active versions are."""
    book = _BookStub(caching_enabled=True)
    active = _SpellStub("active", book)
    parked = _SpellStub("parked", book)
    book.add_active(active)
    book.add_parked(parked)

    SpellbookCreationSystem.define_conduit_into_spells(book, _ConduitStub(dynamic=True))

    assert [call.book_lock_held for call in active.stamps] == [True]
    assert [call.book_lock_held for call in parked.stamps] == [True]


def test_a_parked_existing_object_is_stamped_but_not_registered() -> None:
    """
    An active existing object is registered in the root's store; a parked one is stamped only - it is not live until
    a notch promotes it, exactly as when it is staged after conjure.
    """
    book = _BookStub(caching_enabled=True)
    active_object, parked_object = object(), object()
    active = _SpellStub("active", book, existing_object=active_object)
    parked = _SpellStub("parked", book, existing_object=parked_object)
    book.add_active(active)
    book.add_parked(parked)
    conduit = _ConduitStub(dynamic=True)

    SpellbookCreationSystem.define_conduit_into_spells(book, conduit)

    assert conduit.registered == [("active", active_object)]
    assert len(parked.stamps) == 1


@pytest.mark.parametrize("starting_flag", [True, False])
def test_a_parked_versions_resolution_flag_is_left_as_it_was(starting_flag: bool) -> None:
    """
    The active loop clears `resolution_required`; a parked version keeps whatever it had - the notch that promotes it
    sets the flag.
    """
    book = _BookStub(caching_enabled=True)
    active = _SpellStub("active", book, resolution_required=True)
    parked = _SpellStub("parked", book, resolution_required=starting_flag)
    book.add_active(active)
    book.add_parked(parked)

    SpellbookCreationSystem.define_conduit_into_spells(book, _ConduitStub(dynamic=True))

    assert active.resolution_required is False
    assert parked.resolution_required is starting_flag


def test_a_raising_parked_stamp_is_logged_and_every_other_version_is_still_wired() -> None:
    """
    One parked version whose stamp raises is logged with its id and the method tag, and the loop goes on: the other
    parked version and the active one are wired.
    """
    book = _BookStub(caching_enabled=True)
    active = _SpellStub("active", book)
    failing = _SpellStub("parked-failing", book, raise_on_stamp=True)
    other = _SpellStub("parked-other", book)
    book.add_active(active)
    book.add_parked(failing)
    book.add_parked(other)

    SpellbookCreationSystem.define_conduit_into_spells(book, _ConduitStub(dynamic=True))

    assert len(active.stamps) == 1 and len(other.stamps) == 1
    assert other._owner_creations is not None
    assert failing._owner_creations is None
    assert len(book._logger.errors) == 1
    message, method_name, exc_info = book._logger.errors[0]
    assert "parked-failing" in message and "stamp of parked-failing failed" in message
    assert method_name == "_define_conduit_into_spells"
    assert exc_info is True


def test_a_book_with_no_parked_versions_is_wired_as_before() -> None:
    """With nothing parked, conjure wires and registers the active versions exactly as before 0.2.8248."""
    book = _BookStub(caching_enabled=False)
    existing = object()
    plain = _SpellStub("plain", book, resolution_required=True)
    holder = _SpellStub("holder", book, existing_object=existing, resolution_required=True)
    book.add_active(plain)
    book.add_active(holder)
    conduit = _ConduitStub(dynamic=False)

    SpellbookCreationSystem.define_conduit_into_spells(book, conduit)

    assert len(plain.stamps) == 1 and len(holder.stamps) == 1
    assert (plain.resolution_required, holder.resolution_required) == (False, False)
    assert conduit.registered == [("holder", existing)]
    assert book._logger.errors == []
