"""
Regression tests: cleaning up a slotted holder runs only the holder's own disposal; its `many` children stay with
the store that built them.

The owner's decision (EPIC-2026-10-20-reassess_many_child_disposal_ownership, DECISION note of 2026-10-24; chat
2026-10-24: "it should behave like autofac not mysteriously cleanup transient objects"): a holder's `many` children
are not the holder's to dispose. Purging, moving or disposing a holder does exactly that to the holder; each child is
an ordinary entry of its own spell's `many` bucket in the store that built it, which disposes it when it ends - or
when its spell is purged there. What a holder does with the objects it holds is its own dispose rule's business.

Removed behaviour (0.2.8238-0.2.8265, `slotted_lifetime_ownership`): a just-published holder adopted the children
built for it into its disposal record, so purging the holder disposed its children after it and raised their
failures with its own, an ownership move carried them to the target, and a `many` purge of the child spell skipped
every child a live holder held.
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


def _leaf_errors(group: BaseException) -> List[BaseException]:
    """
    Return the non-group exceptions inside an exception group, depth first.

    A root's teardown raises its own group around each store's group, so a disposal failure is a leaf two levels
    down.

    Args:
        group: An exception, usually an ExceptionGroup.

    Returns:
        List[BaseException]: Every leaf exception (the argument itself when it is not a group).
    """
    if isinstance(group, BaseExceptionGroup):
        leaves: List[BaseException] = []
        for inner in group.exceptions:
            leaves.extend(_leaf_errors(inner))
        return leaves
    return [group]


def test_holder_purge_disposes_only_the_holder_and_its_children_wait_for_their_store() -> None:
    """
    Purging a holder disposes the holder alone; each purged holder's child stays in its spell's bucket and is
    disposed once, when the store that built it ends.

    Symptom (0.2.8238-0.2.8265): each purge disposed the holder's child with it.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-purge")
    holders: List[PerConduitHolder] = []
    try:
        for _ in range(3):
            holder = root.meld(spell_id=holder_id)
            holders.append(holder)
            assert root.purge(spell_id=holder_id) == 1, "a holder purge counts the holder's own entry"
            assert holder.closes == 1
            assert holder.child.closes == 0, "purging the holder must not dispose the many child it holds"
        assert _bucket(root, child_id) == [holder.child for holder in holders], (
            "every child stays an entry of its spell's bucket in the store that built it"
        )
    finally:
        root.cleanup()
    assert [holder.child.closes for holder in holders] == [1] * 3, "each child is disposed once, at its store's end"


def test_single_instance_purge_of_a_holder_disposes_only_the_holder() -> None:
    """
    A single-instance purge of a holder runs the holder's disposal and nothing else; the next meld builds a new
    holder and a new child, and the root's teardown disposes the two children it built.

    Symptom (0.2.8238-0.2.8265): the purge disposed the holder, then its child.
    """
    book, _child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-single-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell=holder, purge_all=False) == 1
        assert Closable.log == ["PerConduitHolder"], "only the holder's own disposal runs"
        again = root.meld(spell_id=holder_id)
        assert again is not holder and again.child is not holder.child
    finally:
        root.cleanup()
    assert (holder.closes, holder.child.closes) == (1, 1), "the purged holder and its child are disposed once each"


def test_purge_of_a_holder_without_disposal_methods_disposes_nothing() -> None:
    """
    A holder that declares no disposal method has nothing to run when purged; its child is not its to dispose.

    Symptom (0.2.8238-0.2.8265): the purge disposed the holder's child.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PlainHolder, Existence.unique_per_conduit, closable=False)
    root = book.conjure(name="holder-children-plain-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell_id=holder_id) == 1
        assert holder.child.closes == 0, "purging the holder must not dispose its many child"
        assert _bucket(root, child_id) == [holder.child], "the child stays recorded in the store that built it"
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the child must be disposed exactly once, at its store's end"


def test_spellspace_holder_purge_leaves_its_child_for_the_space_exit() -> None:
    """
    Purging a spellspace holder disposes the holder; the space built the child and disposes it at its exit.

    Symptom (0.2.8238-0.2.8265): the purge disposed the child with the holder.
    """
    book, _child_id = _automatic_book()
    holder_id = _bind(book, SpaceHolder, Existence.unique_per_spell_space)
    root = book.conjure(name="holder-children-space-purge")
    try:
        with root.enter_spellspace() as space:
            holder = space.meld(spell_id=holder_id)
            assert space.purge(spell_id=holder_id) == 1
            assert (holder.closes, holder.child.closes) == (1, 0), "only the holder's own disposal runs"
            again = space.meld(spell_id=holder_id)
            assert again is not holder
        assert holder.child.closes == 1, "the space's exit disposes the child it built"
        assert (again.closes, again.child.closes) == (1, 1), "the space's exit disposes the second holder and child"
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the purged holder's child must be disposed exactly once"


def test_owner_purge_of_a_unique_holder_leaves_its_many_child_open() -> None:
    """
    The owning root's purge of a `unique` holder disposes the holder; the child stays recorded in the root, which
    built it, until the root ends.

    Symptom (0.2.8238-0.2.8265): the holder's purge disposed its child too.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, UniqueHolder, Existence.unique)
    root = book.conjure(name="holder-children-unique-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell_id=holder_id) == 1
        assert (holder.closes, holder.child.closes) == (1, 0), "only the holder's own disposal runs"
        assert _bucket(root, child_id) == [holder.child]
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the child must be disposed exactly once"


def test_a_failing_child_disposal_surfaces_at_its_store_end_not_at_the_holder_purge() -> None:
    """
    A child whose disposal fails is not touched by its holder's purge; the failure is raised when the store that
    built the child ends.

    Symptom (0.2.8238-0.2.8265): the holder's purge disposed the child and raised its failure.
    """
    book, _child_id = _automatic_book(child=FailingChild)
    holder_id = _bind(book, FailingChildHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-failing-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        assert root.purge(spell_id=holder_id) == 1, "the holder's purge raises nothing: its own disposal succeeds"
        assert (holder.closes, holder.child.closes) == (1, 0)
        with pytest.raises(ExceptionGroup) as raised:
            root.cleanup()
        failures = _leaf_errors(raised.value)
        assert len(failures) == 1 and str(failures[0].__cause__) == "child close failed"
    finally:
        root.cleanup()
    assert holder.child.closes == 1, "the child must be disposed exactly once"


def test_many_purge_of_the_child_spell_disposes_every_child_its_store_recorded() -> None:
    """
    A `many` purge of the child spell retires every child the store recorded, the one a live holder holds
    included: the child is not the holder's, and the holder keeps a reference the application owns.

    Symptom (0.2.8238-0.2.8265): the purge skipped the child a live holder held.
    """
    book, child_id = _automatic_book()
    holder_id = _bind(book, PerConduitHolder, Existence.unique_per_conduit)
    root = book.conjure(name="holder-children-many-purge")
    try:
        holder = root.meld(spell_id=holder_id)
        free = root.meld(spell_id=child_id)
        assert root.purge(spell_id=child_id) == 2, "the bucket holds the holder's child and the free one"
        assert (free.closes, holder.child.closes) == (1, 1)
        assert root.meld(spell_id=holder_id) is holder, "the holder itself is untouched"
    finally:
        root.cleanup()
    assert (holder.closes, holder.child.closes, free.closes) == (1, 1, 1), "each object is disposed exactly once"


def test_transfer_move_leaves_the_holders_many_child_in_the_store_that_built_it() -> None:
    """
    Moving a holder with `move_creations=True` moves the holder; its child stays in the source store, which built
    it and disposes it when it ends, while the target serves the holder and disposes only the holder.

    Symptom (0.2.8238-0.2.8265): the move carried the child to the target with the holder.
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
        assert child in _bucket(source, child_id), "the child stays in the store that built it"
        source.cleanup()
        assert (holder.closes, child.closes) == (0, 1), "the source's teardown disposes the child it built"
        target.cleanup()
        assert (holder.closes, child.closes) == (1, 1), "the target's teardown disposes only the holder"
    finally:
        source.cleanup()
        target.cleanup()
    assert (holder.closes, child.closes) == (1, 1), "the holder and its child are disposed exactly once"


def test_control_transfer_move_with_dependencies_disposes_the_child_once_at_the_target() -> None:
    """
    Control (green before and after the change): moving the holder with its dependencies moves the child's spell,
    and its bucket, as well; the source's teardown leaves the child open and the target's disposes holder and child
    once each.
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
    Control (green before and after the change): within one store, teardown runs newest first, and a holder is
    published after the child built for it, so a holder's own disposal can still use its child.
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
