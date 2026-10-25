"""
Regression tests: a `many` dependency belongs to the scope that built it, never to the holder it was passed to.

The owner's decision (EPIC-2026-10-20-reassess_many_child_disposal_ownership, DECISION note of 2026-10-24; chat
2026-10-24: "it should behave like autofac not mysteriously cleanup transient objects"): a disposal-bearing `many`
dependency built for a slotted holder of any kind is recorded in, and disposed by, the meld's innermost scope - the
spellspace store, else the melding conduit's store - exactly as a `many` root is. Cleaning up the holder runs only the
holder's own disposal methods; what the holder holds is its own dispose rule's business.

The removed behaviour (0.2.8235-0.2.8265):
    The site plan registered the child in the store the holder was published to and, from 0.2.8238, moved it into
    the holder's disposal record. Ending the scope that built the child left it open, and the holder's owner disposed
    it with the holder - when that owner ended or purged the holder.

What these tests assert:
    - Placement: the child is recorded in the store of the scope that melded the holder; the holder's owner keeps no
      record of it.
    - Lifetime: ending the scope that built the child disposes it, once, while the holder's owner keeps serving the
      holder; the owner's end does not dispose it again.
    - The opt-in specializer still builds one child for a captured holder, and the scope that built it records it.
    - Controls (green before and after the change): holders built where they live keep their child until that
      scope ends.

The dynamic routes (a borrowing root, a cluster member) are covered by
`tests/integration/melder/conduit/test_conduit_integration_many_child_belongs_to_the_scope_that_built_it.py`.
"""

from collections.abc import Iterator
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Child:
    """
    Disposal-bearing `many` dependency.

    Contract:
        `close` is the disposal method declared at bind; `closes` counts how many times Melder ran it on this object
        and the class-level `built` counts constructions in the current test (reset by the fixture).
    """

    built: int = 0

    def __init__(self) -> None:
        """Count the construction and start undisposed."""
        Child.built += 1
        self.closes: int = 0

    def close(self) -> None:
        """Record one disposal."""
        self.closes += 1


class Extra:
    """`many` dependency without disposal methods; the override test supplies it."""

    def __init__(self) -> None:
        """Nothing to set up; identity is what the override test checks."""


class UniqueHolder:
    """Holder of one Child, bound `unique` (also the nested consumer's and the many root's dependency)."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class PerConduitHolder:
    """Holder of one Child, bound `unique_per_conduit`."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class LineageHolder:
    """Holder of one Child, bound `unique_per_conduit_lineage`."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class SpellSpaceHolder:
    """Holder of one Child, bound `unique_per_spell_space`."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class OverrideHolder:
    """`unique` holder of one Child and one Extra; the override test supplies the Extra."""

    def __init__(self, child: Child, extra: Extra) -> None:
        """Keep both dependencies."""
        self.child = child
        self.extra = extra


class PerConduitConsumer:
    """`unique_per_conduit` consumer of a `unique` UniqueHolder (nested route)."""

    def __init__(self, holder: UniqueHolder) -> None:
        """Keep the injected holder."""
        self.holder = holder


class ManyRoot:
    """`many` root over a `unique` UniqueHolder (the specializer test's shape)."""

    def __init__(self, holder: UniqueHolder) -> None:
        """Keep the injected holder."""
        self.holder = holder


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and a zeroed Child count; reset the Aether again afterwards."""
    _reset_aether()
    Child.built = 0
    yield
    _reset_aether()


def _book(specialize: bool = False) -> Tuple[Spellbook, str]:
    """
    Return an automatic Spellbook with Child bound as a disposal-bearing `many` spell.

    Args:
        specialize: Value of `generalized_singleton_specialization_enabled` (opt-in, default off).

    Returns:
        Tuple[Spellbook, str]: The book and Child's spell id; callers bind their holders and conjure.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("generalized_singleton_specialization_enabled", specialize)
    book = Spellbook(configuration=configuration)
    child_id = book.bind(spell=Child, existence=Existence.many, permissions="create", disposal_method_names=["close"])
    return book, child_id


def _bucket(store: Creations, child_id: str) -> List[Any]:
    """
    Return a copy of one store's live `many` bucket for Child's spell id (empty when it keeps none).

    Args:
        store: A conduit's or a spellspace's creations store.
        child_id: Child's spell id.

    Returns:
        List[Any]: A copy of the bucket - every Child this store recorded.
    """
    return list(store._creations.get(child_id) or [])


def _holder_disposal_record(store: Creations, holder_id: str) -> Optional[Any]:
    """
    Return the disposal record one store keeps under a holder's spell id, or None.

    The holders in this module declare no disposal method, so a store that records only the holder keeps nothing
    here; a record means the store tied something else - the holder's child - to the holder.

    Args:
        store: The holder's owner store.
        holder_id: The holder's spell id.

    Returns:
        Optional[Any]: The record, or None when the store keeps none.
    """
    return store._disposable_creations.get(holder_id)


def _first_meld_through_lesser(root: Conduit, holder_id: str) -> Tuple[Any, Any, Optional[Conduit]]:
    """Meld the holder first through a lesser, return the lesser to its pool, read the holder at the root."""
    lesser = root.create_lesser_conduit()
    first = lesser.meld(spell_id=holder_id)
    lesser.cleanup()
    return first, root.meld(spell_id=holder_id), None


def _first_meld_in_root_spellspace(root: Conduit, holder_id: str) -> Tuple[Any, Any, Optional[Conduit]]:
    """Meld the holder first in a root spellspace, exit it, read the holder at the root."""
    with root.enter_spellspace() as space:
        first = space.meld(spell_id=holder_id)
    return first, root.meld(spell_id=holder_id), None


def _first_meld_in_lesser_spellspace(root: Conduit, holder_id: str) -> Tuple[Any, Any, Optional[Conduit]]:
    """Meld the holder first in a lesser's spellspace, exit it, read the holder at that lesser (left attached)."""
    lesser = root.create_lesser_conduit()
    with lesser.enter_spellspace() as space:
        first = space.meld(spell_id=holder_id)
    return first, lesser.meld(spell_id=holder_id), lesser


@pytest.mark.parametrize(
    ("holder", "existence", "route"),
    [
        pytest.param(UniqueHolder, Existence.unique, _first_meld_through_lesser, id="unique-through-lesser"),
        pytest.param(UniqueHolder, Existence.unique, _first_meld_in_root_spellspace, id="unique-in-root-spellspace"),
        pytest.param(
            UniqueHolder, Existence.unique, _first_meld_in_lesser_spellspace, id="unique-in-lesser-spellspace",
        ),
        pytest.param(
            PerConduitHolder,
            Existence.unique_per_conduit,
            _first_meld_in_root_spellspace,
            id="per-conduit-in-root-spellspace",
        ),
        pytest.param(
            PerConduitHolder,
            Existence.unique_per_conduit,
            _first_meld_in_lesser_spellspace,
            id="per-conduit-in-lesser-spellspace",
        ),
        pytest.param(
            LineageHolder,
            Existence.unique_per_conduit_lineage,
            _first_meld_through_lesser,
            id="lineage-through-lesser",
        ),
        pytest.param(
            LineageHolder,
            Existence.unique_per_conduit_lineage,
            _first_meld_in_root_spellspace,
            id="lineage-in-root-spellspace",
        ),
    ],
)
def test_scope_end_disposes_the_many_child_it_built_for_a_holder_that_outlives_it(
        holder: type,
        existence: Existence,
        route: Any,
) -> None:
    """
    The scope that first melded a longer-lived holder built its `many` child, so that scope's end disposes the
    child, once, while the holder's owner keeps serving the holder; the owner's end does not dispose it again.

    Symptom (0.2.8235-0.2.8265): after the route's scope ended the child was still open - recorded with the holder -
    and the holder's owner closed it at its own end, Melder disposing a transient because of the holder it was
    passed to.
    """
    book, _child_id = _book()
    holder_id = book.bind(spell=holder, existence=existence, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        first, again, lesser = route(root, holder_id)
        assert again is first, "precondition: the holder outlives the scope that first melded it"
        assert first.child.closes == 1, "the scope that built the many child must dispose it when it ends"
        if lesser is not None:
            lesser.cleanup()
    finally:
        root.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, by the scope that built it"


@pytest.mark.parametrize(
    ("holder", "existence", "route_kind"),
    [
        pytest.param(UniqueHolder, Existence.unique, "lesser", id="unique-through-lesser"),
        pytest.param(UniqueHolder, Existence.unique, "root_spellspace", id="unique-in-root-spellspace"),
        pytest.param(UniqueHolder, Existence.unique, "lesser_spellspace", id="unique-in-lesser-spellspace"),
        pytest.param(
            PerConduitHolder, Existence.unique_per_conduit, "root_spellspace", id="per-conduit-in-root-spellspace",
        ),
        pytest.param(
            PerConduitHolder,
            Existence.unique_per_conduit,
            "lesser_spellspace",
            id="per-conduit-in-lesser-spellspace",
        ),
        pytest.param(PerConduitHolder, Existence.unique_per_conduit, "lesser", id="per-conduit-at-lesser"),
        pytest.param(LineageHolder, Existence.unique_per_conduit_lineage, "lesser", id="lineage-through-lesser"),
        pytest.param(
            LineageHolder, Existence.unique_per_conduit_lineage, "root_spellspace", id="lineage-in-root-spellspace",
        ),
        pytest.param(
            SpellSpaceHolder,
            Existence.unique_per_spell_space,
            "root_spellspace",
            id="spellspace-holder-in-root-spellspace",
        ),
    ],
)
def test_many_child_is_recorded_in_the_store_of_the_scope_that_melded_its_holder(
        holder: type,
        existence: Existence,
        route_kind: str,
) -> None:
    """
    The first build of a holder records its `many` child in the store of the scope that melded it - the
    spellspace, else the melding conduit - and the store that owns the holder keeps no record of the child.

    Owners of the holder: the root for `unique` and lineage; the conduit a per-conduit holder is cached in; the
    spellspace for a spellspace holder. Symptom (0.2.8235-0.2.8265): the child was recorded in the owner's store and,
    from 0.2.8238, inside the holder's own disposal record, out of its spell's bucket.
    """
    book, child_id = _book()
    holder_id = book.bind(spell=holder, existence=existence, permissions="create")
    root = book.conjure(name="many_child_root")
    owned_by_root = existence in (Existence.unique, Existence.unique_per_conduit_lineage)
    try:
        if route_kind == "lesser":
            lesser = root.create_lesser_conduit()
            child = lesser.meld(spell_id=holder_id).child
            owner_store = root._creations if owned_by_root else lesser._creations
            melding_store = lesser._creations
            assert child in _bucket(melding_store, child_id), "the melding lesser must record the child it built"
            assert _holder_disposal_record(owner_store, holder_id) is None, (
                "the holder's owner must not tie the child to the holder"
            )
            if owner_store is not melding_store:
                assert child not in _bucket(owner_store, child_id), "the holder's owner must not record the child"
            lesser.cleanup()
        else:
            conduit = root if route_kind == "root_spellspace" else root.create_lesser_conduit()
            with conduit.enter_spellspace() as space:
                child = space.meld(spell_id=holder_id).child
                if existence is Existence.unique_per_spell_space:
                    owner_store = space._creations
                elif owned_by_root:
                    owner_store = root._creations
                else:
                    owner_store = conduit._creations
                melding_store = space._creations
                assert child in _bucket(melding_store, child_id), (
                    "the melding spellspace must record the child it built"
                )
                assert _holder_disposal_record(owner_store, holder_id) is None, (
                    "the holder's owner must not tie the child to the holder"
                )
                if owner_store is not melding_store:
                    assert child not in _bucket(owner_store, child_id), (
                        "the holder's owner must not record the child"
                    )
    finally:
        root.cleanup()
    assert child.closes == 1, "the child must be disposed exactly once"


def test_lesser_end_disposes_the_many_child_it_built_for_a_unique_under_a_per_conduit_consumer() -> None:
    """
    A per-conduit consumer melded in a lesser builds its `unique` holder (published in the root) and the holder's
    `many` child; the lesser built the child, so the lesser records it and its pool return disposes it.

    Symptom (0.2.8235-0.2.8265): the root recorded the child with its unique holder, so the lesser's pool return left
    it open and the root closed it at teardown.
    """
    book, child_id = _book()
    holder_id = book.bind(spell=UniqueHolder, existence=Existence.unique, permissions="create")
    consumer_id = book.bind(spell=PerConduitConsumer, existence=Existence.unique_per_conduit, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        lesser = root.create_lesser_conduit()
        held = lesser.meld(spell_id=consumer_id).holder
        assert held.child in _bucket(lesser._creations, child_id), "the lesser built the child and records it"
        assert held.child not in _bucket(root._creations, child_id), "the root must not record the child"
        assert _holder_disposal_record(root._creations, holder_id) is None, "the root must not tie it to the holder"
        lesser.cleanup()
        assert root.meld(spell_id=holder_id) is held, "precondition: the unique holder outlives the lesser"
        assert held.child.closes == 1, "the lesser's pool return must dispose the many child it built"
    finally:
        root.cleanup()
    assert held.child.closes == 1, "the child must be disposed exactly once"


def test_lesser_end_disposes_the_many_child_an_override_meld_built_for_a_unique() -> None:
    """
    An override meld through a lesser first builds a `unique` holder with the supplied Extra and a new Child; the
    lesser's key-set plan built the child, so the lesser records it and its pool return disposes it.

    Symptom (0.2.8235-0.2.8265): the root recorded the child with its unique holder and closed it at teardown.
    """
    book, child_id = _book()
    book.bind(spell=Extra, existence=Existence.many, permissions="create")
    holder_id = book.bind(spell=OverrideHolder, existence=Existence.unique, permissions="create")
    root = book.conjure(name="many_child_root")
    supplied = Extra()
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id, override={"extra": supplied})
        assert first.extra is supplied, "precondition: the override supplied the Extra"
        assert first.child in _bucket(lesser._creations, child_id), "the lesser built the child and records it"
        assert _holder_disposal_record(root._creations, holder_id) is None, "the root must not tie it to the holder"
        lesser.cleanup()
        assert root.meld(spell_id=holder_id) is first, "precondition: the unique holder outlives the lesser"
        assert first.child.closes == 1, "the lesser's pool return must dispose the many child it built"
    finally:
        root.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once"


def test_specializer_records_the_one_many_child_of_a_captured_unique_in_the_scope_that_built_it() -> None:
    """
    With the opt-in singleton specializer on, warm melds of a `many` root over a captured `unique` holder build no
    further child (the specializer still declines a graph that feeds a `many` step into a holder); the one child is
    recorded by the scope that built it - the root - and disposed once, when the root ends.

    Symptom (0.2.8235-0.2.8265): the child was recorded with the holder, out of its spell's bucket.
    """
    book, child_id = _book(specialize=True)
    holder_id = book.bind(spell=UniqueHolder, existence=Existence.unique, permissions="create")
    root_id = book.bind(spell=ManyRoot, existence=Existence.many, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        melded = [root.meld(spell_id=root_id) for _ in range(6)]
        with root.enter_spellspace() as space:
            melded.append(space.meld(spell_id=root_id))
        held = melded[0].holder
        assert all(each.holder is held for each in melded), "precondition: every meld reuses the one unique holder"
        assert Child.built == 1, "warm melds built a many child the captured unique holder does not need"
        assert _bucket(root._creations, child_id) == [held.child], "the root, which built the child, records it once"
        assert _holder_disposal_record(root._creations, holder_id) is None, "the root must not tie it to the holder"
        assert held.child.closes == 0
    finally:
        root.cleanup()
    assert held.child.closes == 1, "the child must be disposed exactly once"


@pytest.mark.parametrize(
    ("holder", "existence"),
    [
        pytest.param(UniqueHolder, Existence.unique, id="unique"),
        pytest.param(PerConduitHolder, Existence.unique_per_conduit, id="per-conduit"),
        pytest.param(LineageHolder, Existence.unique_per_conduit_lineage, id="lineage"),
    ],
)
def test_control_holder_built_at_its_owner_keeps_its_many_child_through_scope_cycles(
        holder: type,
        existence: Existence,
) -> None:
    """
    Control (green before and after the change): a holder first built at the root has its child built by the root,
    so lesser and spellspace cycles that meld it again leave the child open; the root's teardown closes it once.
    """
    book, _child_id = _book()
    holder_id = book.bind(spell=holder, existence=existence, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        first = root.meld(spell_id=holder_id)
        lesser = root.create_lesser_conduit()
        lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        with root.enter_spellspace() as space:
            space.meld(spell_id=holder_id)
        assert root.meld(spell_id=holder_id) is first
        assert first.child.closes == 0
    finally:
        root.cleanup()
    assert first.child.closes == 1


def test_control_per_conduit_holder_at_a_lesser_takes_its_many_child_with_it() -> None:
    """
    Control (green before and after the change): a per-conduit holder built at a lesser and its child both live in
    the lesser's store, so the lesser's pool return disposes the child once.
    """
    book, _child_id = _book()
    holder_id = book.bind(spell=PerConduitHolder, existence=Existence.unique_per_conduit, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id)
        assert lesser.meld(spell_id=holder_id) is first
        assert first.child.closes == 0
        lesser.cleanup()
        assert first.child.closes == 1
    finally:
        root.cleanup()
    assert first.child.closes == 1


def test_control_spellspace_holder_takes_its_many_child_with_it() -> None:
    """
    Control (green before and after the change): a `unique_per_spell_space` holder and its child live and die with
    the spellspace, so its exit disposes the child once.
    """
    book, _child_id = _book()
    holder_id = book.bind(spell=SpellSpaceHolder, existence=Existence.unique_per_spell_space, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        with root.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
            assert space.meld(spell_id=holder_id) is first
            assert first.child.closes == 0
        assert first.child.closes == 1
    finally:
        root.cleanup()
    assert first.child.closes == 1
