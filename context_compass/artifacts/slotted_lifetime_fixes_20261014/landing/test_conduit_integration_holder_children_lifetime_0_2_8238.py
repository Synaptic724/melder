"""
Regression tests: a slotted holder's `many` children are purged and moved with the holder.

EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D4 and D5 (proven by the lifetime audit on 0.2.8235; cases t4b, p5):
    Since 0.2.8235 a holder's disposal-bearing `many` children are registered in the holder's own store, but under
    their own spell id - in the child spell's `many` bucket - so a store verb keyed by the holder could not reach them:
    D5 - purging a holder disposed the holder only; its children stayed registered and undisposed until the store
         ended, one more for every purge-and-meld cycle, and a failing child disposal was never reported;
    D4 - moving a holder with `transfer_spell_ownership(..., move_creations=True)` carried the holder to the target and
         left its children in the source store, whose teardown disposed them while the target kept serving the holder.
    A `many` purge of the child spell, by contrast, reached the children and disposed them under their live holders.

Corrected behaviour asserted here - the owner's rule: a holder's `many` children belong to the holder; purging, moving
or disposing the holder does the same to its children, holder first. The children are recorded with the holder the
moment it is published, so a `many` purge of the child spell no longer reaches a child that a live holder owns.
"""

from collections.abc import Iterator
from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)

pytestmark = pytest.mark.integration


class Closable:
    """
    Base of the test objects that declare a disposal method.

    Contract:
        `close` is the disposal method declared at bind; `closes` counts how many times Melder ran it on this object,
        and the class-level `log` (reset by the fixture) records the class name of every close, in order.
    """

    log: List[str] = []

    def __init__(self) -> None:
        """Start undisposed."""
        self.closes: int = 0

    def close(self) -> None:
        """Record one disposal."""
        self.closes += 1
        Closable.log.append(type(self).__name__)


class Child(Closable):
    """Disposal-bearing `many` child of every holder below."""


class FailingChild(Closable):
    """Disposal-bearing `many` child whose disposal method records the call and then raises."""

    def close(self) -> None:
        """Record one disposal, then fail."""
        super().close()
        raise RuntimeError("child close failed")


class PerConduitHolder(Closable):
    """`unique_per_conduit` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        super().__init__()
        self.child = child


class PlainHolder:
    """`unique_per_conduit` holder of one Child that declares no disposal method of its own."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class SpaceHolder(Closable):
    """`unique_per_spell_space` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        super().__init__()
        self.child = child


class UniqueHolder(Closable):
    """`unique` holder of one Child: purged by its owner root, moved by an ownership transfer."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        super().__init__()
        self.child = child


class FailingChildHolder(Closable):
    """`unique_per_conduit` holder of one FailingChild."""

    def __init__(self, child: FailingChild) -> None:
        """Keep the injected child."""
        super().__init__()
        self.child = child


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and an empty close log; reset the Aether again afterwards."""
    _reset_aether()
    Closable.log = []
    yield
    _reset_aether()


def _bind(book: Spellbook, spell: type, existence: Existence, closable: bool = True) -> str:
    """
    Bind one test class, with its `close` disposal method unless told otherwise.

    Args:
        book: The Spellbook to bind into.
        spell: The class.
        existence: Its Existence.
        closable: Whether `close` is declared as the disposal method.

    Returns:
        str: The spell id.
    """
    if closable:
        return book.bind(spell=spell, existence=existence, permissions="create", disposal_method_names=["close"])
    return book.bind(spell=spell, existence=existence, permissions="create")


def _automatic_book(child: type = Child) -> Tuple[Spellbook, str]:
    """
    Return an automatic Spellbook with one disposal-bearing `many` child class bound.

    Args:
        child: The child class to bind (`Child` or `FailingChild`).

    Returns:
        Tuple[Spellbook, str]: The book and the child's spell id; callers bind their holder and conjure.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    return book, _bind(book, child, Existence.many)


def _dynamic_configuration(frame: str) -> SpellbookConfiguration:
    """
    Return a dynamic configuration for one frame with one phase worker.

    Args:
        frame: The aetheric frame the configuration belongs to.

    Returns:
        SpellbookConfiguration: The configuration.
    """
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bucket(scope: Any, spell_id: str) -> List[Any]:
    """
    Return a copy of the `many` bucket one scope's store keeps for a spell id (empty when it keeps none).

    Args:
        scope: A conduit or a spellspace.
        spell_id: The `many` spell id.

    Returns:
        List[Any]: The objects registered under the spell id itself.
    """
    return list(scope._creations._creations.get(spell_id) or [])


def test_purge_disposes_the_many_child_of_the_purged_holder_and_nothing_accumulates() -> None:
    """
    Purging a holder disposes its `many` child with it, and purge-and-meld cycles leave nothing registered.

    Symptom (0.2.8235, probe case p5): five purge-and-meld cycles of a per-conduit holder closed five holders and none
    of their children, which all stayed registered in the root's store until its teardown.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-purge")
    holders: List[PerConduitHolder] = []
    try:
        for _ in range(5):
            holder = root.meld(spell_id=holder_id)
            holders.append(holder)
            assert root.purge(spell_id=holder_id) == 1, "a holder purge counts the holder's own entry"
            assert holder.closes == 1
            assert holder.child.closes == 1, "purging the holder must dispose its many child with it"
        assert _bucket(root, child_id) == [], "no child of a purged holder may stay registered"
    finally:
        root.cleanup()
    assert [holder.child.closes for holder in holders] == [1] * 5, "each child must be disposed exactly once"


def test_single_instance_purge_disposes_the_holder_first_and_then_its_many_child() -> None:
    """
    A single-instance purge of a holder disposes the holder, then its child, and the next meld builds both anew.

    Symptom (0.2.8235): only the holder was closed; its child stayed open in the root's store.
    """
    book, _child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-single-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell=holder, purge_all=False) == 1
        assert Closable.log == ["PerConduitHolder", "Child"], "the holder is disposed first, then its child"
        again = root.meld(spell_id=holder_id)
        assert again is not holder and again.child is not holder.child
    finally:
        root.cleanup()
    assert (holder.closes, holder.child.closes) == (1, 1), "the purged holder and its child are disposed exactly once"


def test_purge_of_a_holder_without_disposal_methods_disposes_its_many_child() -> None:
    """
    A holder that declares no disposal method still takes its disposal-bearing child with it when purged.

    Symptom (0.2.8235): the purge removed the holder and left its child registered and open.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PlainHolder, Existence.unique_per_conduit, closable=False)
    root = book.conjure(name="holder-children-plain-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell_id=holder_id) == 1
        assert holder.child.closes == 1, "purging the holder must dispose its many child"
        assert _bucket(root, child_id) == [], "the purged holder's child must not stay registered"
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the child must be disposed exactly once"


def test_spellspace_purge_disposes_the_many_child_of_the_spellspace_holder() -> None:
    """
    Purging a spellspace holder inside its spellspace disposes the holder's child at once, not at the space's exit.

    Symptom (0.2.8235): the child stayed registered in the spellspace and was closed only when the space was released.
    """
    book, _child_id = _automatic_book()
    holder_id = _bind(book, SpaceHolder, Existence.unique_per_spell_space)
    root = book.conjure(name="holder-children-space-purge")
    try:
        with root.enter_spellspace() as space:
            holder = space.meld(spell_id=holder_id)
            assert space.purge(spell_id=holder_id) == 1
            assert holder.child.closes == 1, "purging the spellspace holder must dispose its many child"
            again = space.meld(spell_id=holder_id)
            assert again is not holder
        assert (again.closes, again.child.closes) == (1, 1), "the space's exit disposes the second holder and child"
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the purged holder's child must be disposed exactly once"


def test_owner_purge_of_a_unique_holder_disposes_its_many_child() -> None:
    """
    The owning root's purge of a `unique` holder disposes the holder's child too.

    Symptom (0.2.8235): the holder was closed and its child stayed in the owner's store until teardown.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, UniqueHolder, Existence.unique)
    root = book.conjure(name="holder-children-unique-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell_id=holder_id) == 1
        assert (holder.closes, holder.child.closes) == (1, 1), "the holder and its child are disposed together"
        assert _bucket(root, child_id) == []
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the child must be disposed exactly once"


def test_purge_raises_a_failing_child_disposal_after_retiring_the_holder() -> None:
    """
    A child whose disposal fails is reported by the holder's purge, after the holder has been retired.

    Symptom (0.2.8235): the purge returned without disposing the child, so its failure surfaced only at teardown.
    """
    book, _child_id = _automatic_book(child=FailingChild)
    holder_id = _bind(book, FailingChildHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-failing-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        with pytest.raises(ExceptionGroup) as raised:
            root.purge(spell_id=holder_id)
        failures = raised.value.exceptions
        assert len(failures) == 1 and str(failures[0].__cause__) == "child close failed"
        assert (holder.closes, holder.child.closes) == (1, 1), "every disposal method ran once"
        assert root.meld(spell_id=holder_id) is not holder, "the holder was retired before the failure was raised"
    finally:
        with pytest.raises(ExceptionGroup):
            root.cleanup()
    assert holder.child.closes == 1, "the purged holder's child must be disposed exactly once"


def test_many_purge_of_the_child_spell_leaves_a_live_holders_child_open() -> None:
    """
    A `many` purge of the child spell retires the spell's own objects, not the child a live holder owns.

    Symptom (0.2.8235): the purge counted the holder's child and closed it while the holder kept handing it out.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-many-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        free = root.meld(spell_id=child_id)
        assert root.purge(spell_id=child_id) == 1, "only the free-standing child is the many spell's own entry"
        assert free.closes == 1
        assert holder.child.closes == 0, "a many purge disposed the child of a live holder"
        assert root.meld(spell_id=holder_id) is holder
    finally:
        root.cleanup()
    assert (holder.closes, holder.child.closes, free.closes) == (1, 1, 1), "each object is disposed exactly once"


def test_transfer_move_carries_the_holders_many_child_to_the_target() -> None:
    """
    Moving a holder with `move_creations=True` moves its `many` child with it; the source's teardown leaves it open.

    Symptom (0.2.8235, probe case t4b): the holder moved and its child stayed in the source store; the source's
    teardown closed the child while the target kept serving the same holder.
    """
    frame = "holder-children-move"
    source_book = Spellbook(aetheric_frame=frame, configuration=_dynamic_configuration(frame))
    child_id = _bind(source_book, Child, Existence.many)
    holder_id = _bind(source_book, UniqueHolder, Existence.unique)
    source = source_book.conjure(dynamic=True, name="holder-children-move-source")
    target = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name="holder-children-move-target")
    try:
        holder = source.meld(spell_id=holder_id)
        child = holder.child
        source.transfer_spell_ownership(spell=holder_id, target_conduit=target, move_creations=True)
        assert target.meld(spell_id=holder_id) is holder, "precondition: the target serves the moved holder"
        left_in_source = _bucket(source, child_id)
        source.cleanup()
        assert child.closes == 0, "the source's teardown disposed the child of a holder the target still serves"
        assert child not in left_in_source, "the moved holder's child stayed in the source store"
        target.cleanup()
        assert (holder.closes, child.closes) == (1, 1), "the target's teardown disposes the holder and its child"
    finally:
        source.cleanup()
        target.cleanup()
    assert (holder.closes, child.closes) == (1, 1), "the holder and its child are disposed exactly once"


def test_control_transfer_move_with_dependencies_disposes_the_child_once_at_the_target() -> None:
    """
    Control (passes on 0.2.8235 too, probe case t4): moving the holder with its dependencies moves the child's spell
    as well; the source's teardown leaves the child open and the target's disposes holder and child once each.
    """
    frame = "holder-children-move-deps"
    source_book = Spellbook(aetheric_frame=frame, configuration=_dynamic_configuration(frame))
    _bind(source_book, Child, Existence.many)
    holder_id = _bind(source_book, UniqueHolder, Existence.unique)
    source = source_book.conjure(dynamic=True, name="holder-children-move-deps-source")
    target = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name="holder-children-move-deps-target")
    try:
        holder = source.meld(spell_id=holder_id)
        child = holder.child
        source.transfer_spell_ownership(
            spell=holder_id, target_conduit=target, move_creations=True, include_dependencies=True,
        )
        source.cleanup()
        assert child.closes == 0
        assert target.meld(spell_id=holder_id) is holder
        target.cleanup()
    finally:
        source.cleanup()
        target.cleanup()
    assert (holder.closes, child.closes) == (1, 1), "the holder and its child are disposed exactly once"


def test_control_teardown_disposes_a_holder_before_its_many_child() -> None:
    """
    Control (passes on 0.2.8235 too): a root's teardown disposes a holder before the child it holds, so a holder's
    own disposal can still use its child.
    """
    book, _child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-teardown-order")
    try:
        holder = root.meld(spell_id=holder_id)
    finally:
        root.cleanup()
    assert Closable.log == ["PerConduitHolder", "Child"], "the holder is disposed first, then its child"
    assert (holder.closes, holder.child.closes) == (1, 1)
