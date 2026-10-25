"""
Component tests: a spell bound again while its removed definition's objects are still alive in a store.

Since 0.2.8257 a spell_id is the SHA256 of the object's code, and since 0.2.8258 the existence and the disposal names
are fields of the binding manifest, not of the spell_id. So `cleanup_spell` followed by a `bind` of the same class
under another existence or other disposal names keeps the spell_id, and the new definition registers its objects
under the key the removed one used. `cleanup_spell` disposes no creation (owner ruling, 2026-10-03): the removed
definition's objects stay alive in the stores that recorded them, and the new definition meets them there.

Two defects follow. TASK-2026-10-25-creations_many_disposal_docstrings measured both on 0.2.8267 with the GIL off
and on, and TASK-2026-10-25-rebind_while_old_objects_are_alive_tests wrote these tests for the owner, who asked to
see them proved ("prove it make tests to show me", chat 2026-10-25).

What these tests assert:
    - Wrong disposal methods, silently (strict xfail): a `many` spell bound with ["close"], melded, cleaned up and
      bound again with ["shutdown"] while the first object is still in the store. The new object must be disposed
      with `shutdown` when its scope ends - at the root's teardown and at a lesser's pool return. Today the store
      keeps the first registration's list for the key and runs `close` on it; nothing raises.
    - A meld that fails (strict xfail): a `unique` or `unique_per_conduit` spell melded, cleaned up and bound
      again as `many` while its object is still held in the store. The next meld must return a new object, which
      the scope disposes with its own list. Today that meld builds the object, then raises AttributeError
      ("'Svc' object has no attribute 'append'") from the store's registration, and the object is lost: never
      returned, never disposed.
    - Controls (green today), which bound each defect: the same disposal list both times; a first binding with no
      disposal names, or a second one with none; a slotted definition that was never melded.

Both defects are the gap STORY-2026-10-18-revalidate_on_binding_change (S3, parked by the owner) closes - "a
changed one retires the old entry" - so each defect test asserts the corrected contract under xfail(strict=True).
STRICT ON PURPOSE: when S3 closes a defect its test passes, strict turns that into a failure, and whoever closed
it deletes the marker. Each assertion names its symptom alone - the new object's disposal calls, the meld's outcome
- so a fix that handles the removed definition's objects another way still turns its test green. Do not loosen
them to make them pass.

Seeing the failures: a default run reports the two defect tests as XFAIL; `pytest -rxX` lists them with their
reasons; `pytest --runxfail` runs them as ordinary tests, and each fails on the values it observed.

The tests read the stores through behaviour only: every `Svc` records the disposal methods Melder runs on it, and
`Journal` records every construction, so an object a meld built but never returned can still be checked.
"""

from collections.abc import Iterator
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Journal:
    """
    The record of every `Svc` built in the current test, kept outside `Svc` on purpose.

    Contract:
        `built` lists each `Svc` in construction order; the fixture empties it before and after every test. It lives
        on this unbound helper, not on `Svc`, because a spell_id is the SHA256 of a class's code and of every
        class-level value (0.2.8257): a list on `Svc`, or one a closure captured, would change between the first and
        the second bind, give the rebind another spell_id and hide both defects. `Svc` names `Journal` in its code;
        a global it reads by name is not part of its digest.
    """

    built: List[Svc] = []


class Svc:
    """
    A service Melder can be told to dispose with `close` or with `shutdown`.

    Contract:
        Each disposal method appends its own name to the object's `calls`, so once the object's scope has ended
        `calls` lists exactly the disposal methods Melder ran on it, in order. The constructor reports the object to
        `Journal`. `Svc` keeps no class-level state (see `Journal`), so every bind of it in a test has one spell_id.
    """

    def __init__(self) -> None:
        """Start with no disposal calls and report the construction to the journal."""
        self.calls: List[str] = []
        Journal.built.append(self)

    def close(self) -> None:
        """Record that Melder disposed this object with `close`."""
        self.calls.append("close")

    def shutdown(self) -> None:
        """Record that Melder disposed this object with `shutdown`."""
        self.calls.append("shutdown")


ScopeRoute = Callable[[Conduit], Tuple[Conduit, Callable[[], None]]]


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
        frame: The frame name; each test uses its own.

    Returns:
        Conduit: The conjured root. Late binds go through it, as in the defects' reports.
    """
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    return book.conjure(dynamic=True, name="root")


def _bind(root: Conduit, existence: Existence, disposal: Optional[List[str]]) -> str:
    """
    Bind `Svc` at the module's one address (spellframe "svc", binding name "svc").

    Args:
        root: The root that owns the definition.
        existence: The existence to bind it under.
        disposal: The per-bind disposal method names, or None to declare none.

    Returns:
        str: The spell_id `bind` returned.
    """
    options: Dict[str, Any] = {} if disposal is None else {"disposal_method_names": disposal}
    return root.bind(spell=Svc, existence=existence, spellframe="svc", binding_name="svc", **options)


def _meld(door: Conduit) -> Svc:
    """Meld `Svc` by its address through one conduit."""
    return door.meld(spellframe="svc", binding_name="svc")


def _remove(root: Conduit, spell_id: str, frame: str) -> None:
    """Remove the definition with `cleanup_spell`; its objects stay alive in the stores that recorded them."""
    root.cleanup_spell(spell=root.get_spell_by_spell_id(spell_id, frame))


def _root_teardown(root: Conduit) -> Tuple[Conduit, Callable[[], None]]:
    """Meld through the root itself; the root's teardown ends its store."""
    return root, root.cleanup


def _lesser_pool_return(root: Conduit) -> Tuple[Conduit, Callable[[], None]]:
    """Meld through a named lesser of the root; its pool return ends the lesser's store."""
    scope = root.create_lesser_conduit(name="scope")
    return scope, scope.cleanup


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "OPEN: a `many` key's disposal record keeps the list of the first definition that registered the key in a "
        "store, and Creations.register_many appends later objects under it without comparing lists, so a "
        "definition cleaned up and bound again under other disposal names (the same spell_id since 0.2.8257) has "
        "its objects disposed with the removed definition's methods while that definition's objects are still in "
        "the store. STORY-2026-10-18-revalidate_on_binding_change (S3, parked by the owner) closes it. STRICT ON "
        "PURPOSE: when the gap is closed this test passes, strict turns that into a failure, and whoever closed it "
        "deletes this marker."
    ),
)
@pytest.mark.parametrize(
    "scope",
    [
        pytest.param(_root_teardown, id="root-teardown"),
        pytest.param(_lesser_pool_return, id="lesser-pool-return"),
    ],
)
def test_rebind_with_other_disposal_methods_disposes_the_new_objects_with_their_own(scope: ScopeRoute) -> None:
    """
    DEFECT, wrong disposal methods: an object bound with ["shutdown"] is disposed with `shutdown`.

    The first definition is bound with ["close"] and melded, so the scope's store records the key with ["close"]
    and keeps the object; the definition is cleaned up and the class bound again with ["shutdown"] under the same
    spell_id; the next meld's object must be disposed with `shutdown` when the scope ends. Today it is disposed with
    `close`, the removed definition's method, and nothing raises.
    """
    frame = "rebind-other-disposal"
    root = _world(frame)
    try:
        door, end_scope = scope(root)
        identifier = _bind(root, Existence.many, ["close"])
        first = _meld(door)
        _remove(root, identifier, frame)
        _bind(root, Existence.many, ["shutdown"])
        second = _meld(door)
        end_scope()
        assert second.calls == ["shutdown"], (
            f"the second binding declares ['shutdown'], but its object was disposed with {second.calls}; the first "
            f"object, bound with ['close'] and still in the store at the rebind, was disposed with {first.calls}"
        )
    finally:
        root.cleanup()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "OPEN: Creations.register_many appends to whatever the key's live slot holds, so after a `unique` or "
        "`unique_per_conduit` definition whose object is still in the store is cleaned up and bound again as `many` "
        "(the same spell_id), the next meld builds its object and then raises AttributeError (\"'Svc' object has "
        "no attribute 'append'\"), and that object is neither returned nor recorded. "
        "STORY-2026-10-18-revalidate_on_binding_change (S3, parked by the owner) closes it. STRICT ON PURPOSE: "
        "when the gap is closed this test passes, strict turns that into a failure, and whoever closed it deletes "
        "this marker."
    ),
)
@pytest.mark.parametrize(
    "existence",
    [
        pytest.param(Existence.unique, id="unique"),
        pytest.param(Existence.unique_per_conduit, id="unique-per-conduit"),
    ],
)
def test_rebind_of_a_held_slotted_spell_as_many_returns_and_disposes_the_new_object(existence: Existence) -> None:
    """
    DEFECT, a meld that fails: after a slotted definition is bound again as `many`, the next meld returns a new object.

    The first definition is slotted and melded, so the root's store holds its object in the key's slot; the
    definition is cleaned up and the class bound again as `many` with ["close"] under the same spell_id. The next
    meld must return a new object - never the old one - and the root's teardown must dispose it with `close`. Today
    the meld builds the object, then raises AttributeError from the store's registration: the object is never
    returned and never disposed.
    """
    frame = "rebind-slotted-to-many"
    root = _world(frame)
    try:
        identifier = _bind(root, existence, ["close"])
        first = _meld(root)
        _remove(root, identifier, frame)
        _bind(root, Existence.many, ["close"])
        try:
            second = _meld(root)
            outcome = "returned the old object" if second is first else "returned a new object"
        except AttributeError as error:
            outcome = f"raised AttributeError: {error}"
        root.cleanup()
        built = list(Journal.built)
        new_calls = built[1].calls if len(built) > 1 else None
        assert (outcome, new_calls) == ("returned a new object", ["close"]), (
            f"after the rebind as `many` the next meld {outcome}; Svc objects built: {len(built)} (the first "
            f"definition's and the meld's); the meld's object was disposed with {new_calls} at the root's teardown; "
            f"the first definition's object was disposed with {first.calls}"
        )
    finally:
        root.cleanup()


@pytest.mark.parametrize(
    "scope",
    [
        pytest.param(_root_teardown, id="root-teardown"),
        pytest.param(_lesser_pool_return, id="lesser-pool-return"),
    ],
)
def test_rebind_with_the_same_disposal_methods_disposes_both_objects_with_them(scope: ScopeRoute) -> None:
    """
    CONTROL (green today): when the second binding declares the same list, the record it joins is right for it.

    Also pins the precondition both defects need: the rebind keeps the spell_id.
    """
    frame = "rebind-same-disposal"
    root = _world(frame)
    try:
        door, end_scope = scope(root)
        identifier = _bind(root, Existence.many, ["close"])
        first = _meld(door)
        _remove(root, identifier, frame)
        assert _bind(root, Existence.many, ["close"]) == identifier
        second = _meld(door)
        end_scope()
        assert (first.calls, second.calls) == (["close"], ["close"])
    finally:
        root.cleanup()


def test_rebind_after_a_binding_without_disposal_methods_disposes_the_new_objects_with_their_own() -> None:
    """
    CONTROL (green today): a `many` without disposal methods is recorded nowhere, so the store holds no record for
    the key at the rebind and the new definition writes it with its own list.
    """
    frame = "rebind-from-no-disposal"
    root = _world(frame)
    try:
        identifier = _bind(root, Existence.many, None)
        first = _meld(root)
        _remove(root, identifier, frame)
        assert _bind(root, Existence.many, ["shutdown"]) == identifier
        second = _meld(root)
        root.cleanup()
        assert (first.calls, second.calls) == ([], ["shutdown"])
    finally:
        root.cleanup()


def test_rebind_without_disposal_methods_leaves_the_new_objects_undisposed() -> None:
    """
    CONTROL (green today): an object whose binding declares no disposal methods is recorded nowhere and never
    disposed, even though the removed definition's record for the key is still in the store; the first object is
    disposed with its own list.
    """
    frame = "rebind-to-no-disposal"
    root = _world(frame)
    try:
        identifier = _bind(root, Existence.many, ["close"])
        first = _meld(root)
        _remove(root, identifier, frame)
        assert _bind(root, Existence.many, None) == identifier
        second = _meld(root)
        root.cleanup()
        assert (first.calls, second.calls) == (["close"], [])
    finally:
        root.cleanup()


@pytest.mark.parametrize(
    "existence",
    [
        pytest.param(Existence.unique, id="unique"),
        pytest.param(Existence.unique_per_conduit, id="unique-per-conduit"),
    ],
)
def test_rebind_of_a_slotted_spell_never_melded_as_many_builds_and_disposes_new_objects(existence: Existence) -> None:
    """
    CONTROL (green today): a slotted definition that was never melded left nothing in the store, so its key has no
    slot when the class is bound again as `many`; each meld returns a new object, and the root's teardown disposes
    each with its list. The meld fails only when the old object is still held.
    """
    frame = "rebind-unmelded-slotted"
    root = _world(frame)
    try:
        identifier = _bind(root, existence, ["close"])
        _remove(root, identifier, frame)
        assert _bind(root, Existence.many, ["close"]) == identifier
        first = _meld(root)
        second = _meld(root)
        assert second is not first
        root.cleanup()
        assert (first.calls, second.calls) == (["close"], ["close"])
    finally:
        root.cleanup()
