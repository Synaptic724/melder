"""
Regression tests: a slotted holder's disposal-bearing `many` child belongs to whatever owns the holder.

The owner's rule (EPIC-2026-10-14-many_child_follows_holder, Decision Log 2026-10-14): "if a root makes a unique its
many should be owned by the root, corresponding to all the unique types ... make sure the corresponding object owns
it". So a holder's `many` child is recorded in, and disposed with, the store that owns the holder: the spell-owning
root for `unique`, that conduit for `unique_per_conduit`, that spellspace for `unique_per_spell_space`, the lineage
root for `unique_per_conduit_lineage` (and the elected leader for cluster - the integration module).

The defect (TASK-2026-10-14-prove_many_child_registration_bug, measured on 0.2.8234):
    The child is built inside the holder's first build and the site plan registered it in the meld's innermost scope
    - the spellspace store, else the melding conduit's store. When that scope ends before the holder's owner, the
    scope's end runs the child's disposal while the holder keeps handing the child out:
        - `unique` first melded through a lesser, in a root spellspace or in a lesser's spellspace;
        - `unique_per_conduit` first melded in a spellspace;
        - `unique_per_conduit_lineage` first melded through a lesser or in a root spellspace;
        - `unique` built as the dependency of a per-conduit consumer melded in a lesser;
        - `unique` first built by an override meld (a key-set plan) through a lesser.
    The opt-in singleton specializer also built and recorded an unused child on every warm meld of a `many` root over
    a captured `unique` holder.

What these tests assert:
    - Ownership: the child is recorded in the store of the holder's owner, not in the melding scope's store. Since
      0.2.8238 it is recorded with the holder itself (its `HolderDisposalEntry`) and leaves its spell's `many` bucket.
    - Lifetime: ending the scope that first melded the holder leaves the child open; ending the holder's owner disposes
      it, exactly once.
    - The specializer builds and records no child its holder does not need.
    - Controls (green on 0.2.8234 too): holders built where they live keep their child through scope cycles; a
      per-conduit holder at a lesser and a spellspace holder take their child with them when their scope ends.

The dynamic routes (a borrowing root, a cluster member) are covered by
`tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py`.
"""

from collections.abc import Iterator
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations, HolderDisposalEntry
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

    Since 0.2.8238 a child built for a holder leaves this bucket once the holder is published (the holder's record
    adopts it), so the bucket holds only children that no holder owns.

    Args:
        store: A conduit's or a spellspace's creations store.
        child_id: Child's spell id.

    Returns:
        List[Any]: A copy of the bucket.
    """
    return list(store._creations.get(child_id) or [])


def _adopted(store: Creations, holder_id: str) -> List[Any]:
    """
    Return the children one store records with a holder, in build order (0.2.8238).

    Args:
        store: A conduit's or a spellspace's creations store.
        holder_id: The holder's spell id.

    Returns:
        List[Any]: The children of the holder's `HolderDisposalEntry`; empty when the store keeps no such record.
    """
    record = store._disposable_creations.get(holder_id)
    if not isinstance(record, HolderDisposalEntry):
        return []
    return [child for child, _methods in record.children]


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
    ("holder", "existence", "route", "owner"),
    [
        pytest.param(
            UniqueHolder, Existence.unique, _first_meld_through_lesser, "root", id="unique-through-lesser",
        ),
        pytest.param(
            UniqueHolder, Existence.unique, _first_meld_in_root_spellspace, "root", id="unique-in-root-spellspace",
        ),
        pytest.param(
            UniqueHolder,
            Existence.unique,
            _first_meld_in_lesser_spellspace,
            "root",
            id="unique-in-lesser-spellspace",
        ),
        pytest.param(
            PerConduitHolder,
            Existence.unique_per_conduit,
            _first_meld_in_root_spellspace,
            "root",
            id="per-conduit-in-root-spellspace",
        ),
        pytest.param(
            PerConduitHolder,
            Existence.unique_per_conduit,
            _first_meld_in_lesser_spellspace,
            "lesser",
            id="per-conduit-in-lesser-spellspace",
        ),
        pytest.param(
            LineageHolder,
            Existence.unique_per_conduit_lineage,
            _first_meld_through_lesser,
            "root",
            id="lineage-through-lesser",
        ),
        pytest.param(
            LineageHolder,
            Existence.unique_per_conduit_lineage,
            _first_meld_in_root_spellspace,
            "root",
            id="lineage-in-root-spellspace",
        ),
    ],
)
def test_scope_end_disposes_the_many_child_of_a_holder_that_outlives_it(
        holder: type,
        existence: Existence,
        route: Any,
        owner: str,
) -> None:
    """
    The scope that first melded a longer-lived holder must not dispose the holder's `many` child; the holder's
    owner does, when it ends.

    Symptom (0.2.8234): after the route's scope ends, the owning scope still returns the same holder, but its
    child's `close()` has already run. Corrected: the child stays open while the holder lives and is closed exactly
    once when the holder's owner ends - root teardown for `unique`, lineage and a root's per-conduit holder; the
    lesser's pool return for a per-conduit holder first melded in that lesser's spellspace.
    """
    book, _child_id = _book()
    holder_id = book.bind(spell=holder, existence=existence, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        first, again, lesser = route(root, holder_id)
        assert again is first, "precondition: the holder outlives the scope that first melded it"
        assert first.child.closes == 0, (
            "the scope that first melded the holder disposed its many child while the holder is still handed out"
        )
        if owner == "lesser":
            assert lesser is not None
            lesser.cleanup()
        else:
            root.cleanup()
        assert first.child.closes == 1, "the child must be disposed when its holder's owner ends"
    finally:
        root.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once"


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
def test_many_child_is_recorded_in_the_store_of_its_holders_owner(
        holder: type,
        existence: Existence,
        route_kind: str,
) -> None:
    """
    The first build of a holder records its `many` child in the store that owns the holder, not in the store of the
    scope that melded it.

    Owners: the root for `unique` and lineage; the conduit a per-conduit holder is cached in (the root behind a root
    spellspace, the lesser behind a lesser's spellspace or a direct lesser meld); the spellspace for a spellspace
    holder. Where the owner is the melding scope itself (a per-conduit holder at a lesser, a spellspace holder) the
    case passes on 0.2.8234 too.
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
            assert _adopted(owner_store, holder_id) == [child], "the holder's owner must record its child"
            if owner_store is not melding_store:
                assert child not in _bucket(melding_store, child_id), "the melding lesser must not record the child"
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
                assert _adopted(owner_store, holder_id) == [child], "the holder's owner must record its child"
                if owner_store is not melding_store:
                    assert child not in _bucket(melding_store, child_id), (
                        "the melding spellspace must not record the child"
                    )
    finally:
        root.cleanup()
    assert child.closes == 1, "the child must be disposed exactly once"


def test_lesser_return_disposes_the_many_child_of_a_unique_built_for_a_per_conduit_consumer() -> None:
    """
    A `unique` holder built as a dependency inside a lesser keeps its `many` child after the lesser returns.

    Symptom (0.2.8234): a per-conduit consumer melded in a lesser builds the `unique` holder (published in the root's
    owner store) and the holder's child, which was recorded in the lesser; the lesser's pool return closed the child
    while the root kept returning the holder. Corrected: the root records the child and closes it once, at teardown.
    """
    book, child_id = _book()
    holder_id = book.bind(spell=UniqueHolder, existence=Existence.unique, permissions="create")
    consumer_id = book.bind(spell=PerConduitConsumer, existence=Existence.unique_per_conduit, permissions="create")
    root = book.conjure(name="many_child_root")
    try:
        lesser = root.create_lesser_conduit()
        held = lesser.meld(spell_id=consumer_id).holder
        assert _adopted(root._creations, holder_id) == [held.child], "the root owns the unique holder's child"
        assert held.child not in _bucket(lesser._creations, child_id), "the lesser must not record the child"
        lesser.cleanup()
        assert root.meld(spell_id=holder_id) is held, "precondition: the unique holder outlives the lesser"
        assert held.child.closes == 0, "the lesser's pool return disposed the many child of a live unique holder"
    finally:
        root.cleanup()
    assert held.child.closes == 1, "the child must be disposed exactly once, with its holder"


def test_lesser_return_disposes_the_many_child_of_a_unique_first_built_by_an_override_meld() -> None:
    """
    A `unique` holder first built by an override meld through a lesser keeps its `many` child after the lesser
    returns.

    Symptom (0.2.8234): the override meld's key-set plan builds the holder with the supplied Extra and a new Child,
    publishes the holder in the root's owner store and recorded the child in the lesser's store; the lesser's pool
    return closed the child. Corrected: the root records the child and closes it once, at teardown.
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
        assert _adopted(root._creations, holder_id) == [first.child], "the root owns the unique holder's child"
        lesser.cleanup()
        assert root.meld(spell_id=holder_id) is first, "precondition: the unique holder outlives the lesser"
        assert first.child.closes == 0, "the lesser's pool return disposed the many child of a live unique holder"
    finally:
        root.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, with its holder"


def test_specializer_builds_and_records_a_new_many_child_on_every_warm_meld_of_a_captured_unique() -> None:
    """
    With the opt-in singleton specializer on, warm melds of a `many` root over a captured `unique` holder must not
    build or record a `many` child for that holder: it already has one.

    Symptom (0.2.8234): the specialized straight-line body emitted every non-captured step, so each warm meld built
    a Child no holder used and recorded it for disposal (7 builds and 6 root records for 6 root melds and one
    spellspace meld). Corrected: one Child, recorded once by the root, closed once at teardown.
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
        assert _adopted(root._creations, holder_id) == [held.child], "the root records only the holder's own child"
        assert _bucket(root._creations, child_id) == [], "no stray child is recorded in the child spell's bucket"
        assert held.child.closes == 0
    finally:
        root.cleanup()
    assert held.child.closes == 1, "the child must be disposed exactly once, with its holder"


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
    Control (passes on 0.2.8234): a holder first built at the root keeps its child through a lesser cycle and a
    spellspace cycle that meld it again, and the child is closed once, at root teardown.
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
    Control (passes on 0.2.8234): a per-conduit holder built at a lesser lives in the lesser's store, so the
    lesser's pool return disposes the holder's child once.
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
    Control (passes on 0.2.8234): a `unique_per_spell_space` holder and its child live and die with the spellspace,
    so its exit disposes the child once.
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
