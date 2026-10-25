"""
Component tests: a Creations store files each binding's objects in its own slot, on one shelf per spell_id.

STORY-2026-10-25-creations_store_slots_by_binding (the owner's go, chat 2026-10-25). A spell_id is the SHA256 of the
object's code (0.2.8257), so `cleanup_spell` followed by a `bind` of the same class under another existence or other
disposal names keeps the spell_id, and `cleanup_spell` leaves the removed definition's objects alive where they are
(the owner's rulings, 2026-10-03 and 2026-10-14). A store files objects by `Spell.store_key`
(`<spell_id>:<binding_hash>`), so each binding of a class has its own slot, disposal record and shape, and it keeps one
shelf per spell_id, so purge and the live probes still act on every binding of the spell.

What these tests pin (the S-numbers are the store probe's cases, artifacts/rebind_live_store_tests_20261025/):
    - S3, S4: a `many` rebound as `unique` or `unique_per_conduit` melds a new object, never the old Python list.
    - S5: a `unique` rebound under other disposal names melds a new object, and each object is disposed with its own
      list; rebound under the same binding, it meets its slot (2026-10-03).
    - S2, its silent form: a slotted class with its own `append` rebound as `many` melds a new object, and Melder
      never calls the old object's `append`.
    - S6, S7: purge after a rebind retires every binding's objects, counts them all and disposes each with its own
      methods.
    - S8, S9: `has_live_creation` and `describe_live_creation_status` count every binding's objects in the store.
    - `meld_existing_spell` answers for the asking binding: the object a meld of it returns, else "not live".
    - An ownership transfer moves every binding's objects.
S1 and the failing-meld form of S2 are the two tests of `test_conduit_component_rebind_while_old_objects_are_alive.py`.

The tests read the store through behaviour only: every object records the disposal methods Melder runs on it, and
`Journal` records every construction.
"""

from collections.abc import Iterator
from typing import Any, Dict, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

SLOTTED = [Existence.unique, Existence.unique_per_conduit]
SLOTTED_IDS = ["unique", "unique-per-conduit"]


class Journal:
    """
    Every object built in the current test, kept outside the services on purpose.

    Contract:
        A spell_id digests every class-level value of a class (0.2.8257), so a list on a service class would change
        between two binds and give the rebind another spell_id; a global the services read by name is not digested.
    """

    built: List[Any] = []


class Svc:
    """
    A service Melder can be told to dispose with `close` or with `shutdown`.

    Contract:
        `calls` lists the disposal methods Melder ran on the object, in order. No class-level state.
    """

    def __init__(self) -> None:
        """Start with no disposal calls and report the construction."""
        self.calls: List[str] = []
        Journal.built.append(self)

    def close(self) -> None:
        """Record a disposal with `close`."""
        self.calls.append("close")

    def shutdown(self) -> None:
        """Record a disposal with `shutdown`."""
        self.calls.append("shutdown")


class Appender:
    """
    A service with its own `append`, the shape a `many` record's bucket is appended through.

    Contract:
        `appended` lists what was passed to `append`; `calls` lists the disposal methods Melder ran on the object.
    """

    def __init__(self) -> None:
        """Start empty and report the construction."""
        self.calls: List[str] = []
        self.appended: List[Any] = []
        Journal.built.append(self)

    def append(self, item: Any) -> None:
        """Record an append."""
        self.appended.append(item)

    def close(self) -> None:
        """Record a disposal with `close`."""
        self.calls.append("close")


class Anchor:
    """Something of its own for a second Book to conjure."""


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and an empty journal; reset both again afterwards."""
    _reset_aether()
    Journal.built.clear()
    yield
    _reset_aether()
    Journal.built.clear()


def _world(frame: str) -> Conduit:
    """
    Return a dynamic root on its own frame with creation caching off and no Book-level disposal names.

    Args:
        frame: The frame name.

    Returns:
        Conduit: The conjured root; the binds of each test go through it after conjure.
    """
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    return book.conjure(dynamic=True, name="root")


def _bind(root: Conduit, existence: Existence, disposal: Optional[List[str]], spell: type = Svc) -> str:
    """
    Bind a service at the module's one address (spellframe "svc", binding name "svc").

    Args:
        root: The root that owns the definition.
        existence: The existence to bind it under.
        disposal: The per-bind disposal method names, or None to declare none.
        spell: The class to bind.

    Returns:
        str: The spell_id `bind` returned.
    """
    options: Dict[str, Any] = {} if disposal is None else {"disposal_method_names": disposal}
    return root.bind(spell=spell, existence=existence, spellframe="svc", binding_name="svc", **options)


def _meld(door: Conduit) -> Any:
    """Meld the service by its address through one conduit."""
    return door.meld(spellframe="svc", binding_name="svc")


def _remove(root: Conduit, spell_id: str, frame: str) -> None:
    """Remove the definition with `cleanup_spell`; its objects stay alive in the stores that recorded them."""
    root.cleanup_spell(spell=root.get_spell_by_spell_id(spell_id, frame))


def _rebind(root: Conduit, frame: str, spell_id: str, existence: Existence, disposal: Optional[List[str]],
            spell: type = Svc) -> None:
    """Remove the definition and bind the same class again; the rebind keeps the spell_id (the precondition)."""
    _remove(root, spell_id, frame)
    assert _bind(root, existence, disposal, spell) == spell_id


def _count(root: Conduit, spell_id: str) -> int:
    """The live-creation count the root's probe reports for the spell."""
    status = root.describe_live_creation_status(spell=spell_id)
    assert status["is_live"] is (status["creation_count"] > 0)
    return int(status["creation_count"])


@pytest.mark.parametrize("existence", SLOTTED, ids=SLOTTED_IDS)
def test_many_rebound_as_a_slotted_spell_melds_a_new_object(existence: Existence) -> None:
    """
    S3, S4: the old `many` list is never served as the slotted spell's object.

    Contract: two `many` objects alive at the root; the class bound again as `existence`; the meld returns a new
        Svc, and the next meld the same one; the root's teardown closes all three.
    """
    frame = f"slots-many-to-{existence.name}"
    root = _world(frame)
    spell_id = _bind(root, Existence.many, ["close"])
    old = [_meld(root), _meld(root)]
    _rebind(root, frame, spell_id, existence, ["close"])
    new = _meld(root)
    assert isinstance(new, Svc), f"the meld returned {type(new).__name__}, not a Svc"
    assert all(new is not each for each in old)
    assert _meld(root) is new
    root.cleanup()
    assert [each.calls for each in old] == [["close"], ["close"]]
    assert new.calls == ["close"]


def test_unique_rebound_under_other_disposal_methods_melds_a_new_object() -> None:
    """
    S5: another binding starts with an empty slot; each object is disposed with its own list.

    Contract: a `unique` with ["close"] melded; the class bound again with ["shutdown"]; the meld by address and
        the meld by spell_id return one new object; the root's teardown closes the old object and shuts the new
        one down.
    """
    frame = "slots-unique-other-disposal"
    root = _world(frame)
    spell_id = _bind(root, Existence.unique, ["close"])
    old = _meld(root)
    _rebind(root, frame, spell_id, Existence.unique, ["shutdown"])
    new = _meld(root)
    assert new is not old
    assert root.meld(spell_id=spell_id) is new
    root.cleanup()
    assert old.calls == ["close"]
    assert new.calls == ["shutdown"]


@pytest.mark.parametrize("existence", SLOTTED, ids=SLOTTED_IDS)
def test_same_binding_rebind_meets_its_slot(existence: Existence) -> None:
    """
    The 2026-10-03 rule stands: the same binding gives the same store key, so the rebind meets its object.

    Contract: bound and melded; bound again the same way; the meld returns the surviving object, disposed once.
    """
    frame = f"slots-same-binding-{existence.name}"
    root = _world(frame)
    spell_id = _bind(root, existence, ["close"])
    old = _meld(root)
    _rebind(root, frame, spell_id, existence, ["close"])
    assert _meld(root) is old
    assert len(Journal.built) == 1
    root.cleanup()
    assert old.calls == ["close"]


@pytest.mark.parametrize("existence", SLOTTED, ids=SLOTTED_IDS)
def test_slotted_class_with_its_own_append_rebound_as_many_is_never_appended_to(existence: Existence) -> None:
    """
    S2, its silent form: the `many` registration never reaches the old slotted object.

    Contract: an Appender melded under `existence`; bound again as `many`; the meld returns a new object, the old
        object's `append` was never called, and the root's teardown closes both.
    """
    frame = f"slots-appender-{existence.name}"
    root = _world(frame)
    spell_id = _bind(root, existence, ["close"], Appender)
    old = _meld(root)
    _rebind(root, frame, spell_id, Existence.many, ["close"], Appender)
    new = _meld(root)
    assert new is not old
    assert old.appended == []
    root.cleanup()
    assert old.calls == ["close"]
    assert new.calls == ["close"]


def test_purge_after_a_unique_was_rebound_as_many_retires_each_binding_with_its_own_methods() -> None:
    """
    S6: purge reads each slot's own shape - no TypeError - and disposes it with its own record.

    Contract: a `unique` with ["close"] melded; bound again as `many` with ["shutdown"]; purge by spell_id retires
        the old object (1, closed); two new objects melded; purge retires both (2, shut down); a third purge
        returns 0.
    """
    frame = "slots-purge-unique-to-many"
    root = _world(frame)
    spell_id = _bind(root, Existence.unique, ["close"])
    old = _meld(root)
    _rebind(root, frame, spell_id, Existence.many, ["shutdown"])
    assert root.purge(spell_id=spell_id) == 1
    assert old.calls == ["close"]
    new = [_meld(root), _meld(root)]
    assert root.purge(spell_id=spell_id) == 2
    assert [each.calls for each in new] == [["shutdown"], ["shutdown"]]
    assert root.purge(spell_id=spell_id) == 0
    root.cleanup()
    assert old.calls == ["close"]


def test_purge_after_a_many_was_rebound_as_unique_counts_every_object() -> None:
    """
    S7: purge counts what is stored on every binding of the spell, not the asking spell's shape.

    Contract: two `many` objects with ["close"]; bound again as `unique` with ["shutdown"] and melded; purge by
        spell_id returns 3, closes the two old objects and shuts the new one down; the next meld builds anew.
    """
    frame = "slots-purge-many-to-unique"
    root = _world(frame)
    spell_id = _bind(root, Existence.many, ["close"])
    old = [_meld(root), _meld(root)]
    _rebind(root, frame, spell_id, Existence.unique, ["shutdown"])
    new = _meld(root)
    assert root.purge(spell_id=spell_id) == 3
    assert [each.calls for each in old] == [["close"], ["close"]]
    assert new.calls == ["shutdown"]
    assert _meld(root) is not new
    root.cleanup()


@pytest.mark.parametrize(
    ("first", "first_melds", "second", "before", "after"),
    [
        (Existence.unique, 1, Existence.many, 1, 2),
        (Existence.many, 2, Existence.unique, 2, 3),
        (Existence.many, 1, Existence.many, 1, 2),
    ],
    ids=["S9-unique-to-many", "many-to-unique", "S8-many-to-many"],
)
def test_probes_count_every_binding_of_the_spell(
        first: Existence, first_melds: int, second: Existence, before: int, after: int) -> None:
    """
    S8, S9: the probes count every binding's objects in the store, from what each slot holds.

    Contract: `first_melds` objects of the first binding alive; the class bound again (`second`, other disposal
        names); the probes report `before` objects and live before the new binding builds, and `after` once it has
        built one.
    """
    frame = f"slots-probe-{first.name}-{second.name}-{first_melds}"
    root = _world(frame)
    spell_id = _bind(root, first, ["close"])
    for _ in range(first_melds):
        _meld(root)
    _rebind(root, frame, spell_id, second, ["shutdown"])
    assert _count(root, spell_id) == before
    assert root.has_live_creation(spell=spell_id) is True
    _meld(root)
    assert _count(root, spell_id) == after
    root.cleanup()


def test_meld_existing_spell_answers_for_the_asking_binding() -> None:
    """
    `meld_existing_spell` returns what a meld of the asking binding returns, never another binding's object.

    Contract: a `unique` with ["close"] melded; bound again with ["shutdown"]; before the new binding builds,
        meld_existing_spell raises "not live" while the probe counts the old object; after a meld it returns the
        new object and the probe counts both.
    """
    frame = "slots-meld-existing"
    root = _world(frame)
    spell_id = _bind(root, Existence.unique, ["close"])
    _meld(root)
    _rebind(root, frame, spell_id, Existence.unique, ["shutdown"])
    with pytest.raises(ValueError, match="is not live"):
        root.meld_existing_spell(spell=spell_id)
    assert _count(root, spell_id) == 1
    new = _meld(root)
    assert root.meld_existing_spell(spell=spell_id) is new
    assert _count(root, spell_id) == 2
    root.cleanup()


def test_ownership_transfer_moves_every_binding_of_the_spell() -> None:
    """
    An ownership transfer moves the whole shelf: every binding's objects, each with its own record.

    Contract: a `unique` with ["close"] melded, bound again with ["shutdown"] and melded; the spell transferred to a
        second Book's root; the target counts both objects, purges both, and each is disposed with its own list.
    """
    frame = "slots-transfer"
    root = _world(frame)
    target_book = Spellbook(aetheric_frame=frame)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        spell_id = _bind(root, Existence.unique, ["close"])
        old = _meld(root)
        _rebind(root, frame, spell_id, Existence.unique, ["shutdown"])
        new = _meld(root)
        root.transfer_spell_ownership(spell=spell_id, target_conduit=target)
        assert _count(target, spell_id) == 2
        assert target.purge(spell_id=spell_id) == 2
        assert old.calls == ["close"]
        assert new.calls == ["shutdown"]
    finally:
        target.cleanup()
        root.cleanup()
