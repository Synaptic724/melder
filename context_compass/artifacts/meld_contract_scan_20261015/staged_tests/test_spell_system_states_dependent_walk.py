"""Unit coverage for the registry's downstream walk (contract_recheck_on_notch_2026_10_16, D2).

A notch flags for revalidation every lineage that depends on the notched one: the registry records each lineage's
binding key (`register_index(binding_key=...)`) and `mark_dependents_for_revalidation` walks from the given lineages
over the reverse dependency edges (`direct_dependents`) and over the contract keys (a SpellContract consumer, in any
Book, of the binding key of a lineage already reached). An edge-reached lineage is marked
`impacted_by_dependency` and transitively dirty; a contract-reached one gets rule 2's contract mark (`gated` +
`contract_unvalidated`, not transitively dirty); both, when reached both ways. Every contract-consumer mark
(`mark_contract_dependents_dirty`) walks on from the consumers it marks. Mark only: states change, nothing else.
"""

import time
from collections.abc import Iterator
from typing import Iterable, List, Optional, Sequence, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)


class _PublicationSpy:
    """
    Risk-manager double that records every structural publication.

    Purpose:
        Prove that a mark publishes once per changed validity and that a repeated mark publishes nothing, the
        contract `SpellSystemState.set_validity` gives every registry mark.
    """

    def __init__(self, states: SpellSystemStates) -> None:
        """Bind the registry whose lock the callbacks check, with no recorded events."""
        self.states: SpellSystemStates = states
        self.published: List[Tuple[str, Optional[SpellValidity], bool]] = []

    def on_structural_validity_change(self, lineage_id: str, validity: Optional[SpellValidity]) -> None:
        """Record the event and whether the registry lock is held while it runs."""
        self.published.append((lineage_id, validity, self.states._lock._is_owned()))

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """Resolution events are not part of these cases."""


@pytest.fixture
def information_registry() -> Iterator[DevopsInformationRegistry]:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("dependent-walk-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(information_registry: DevopsInformationRegistry) -> Iterator[SpellSystemStates]:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test."""
    frame = MagicMock()
    frame.name = "dependent-walk-frame"
    registry = SpellSystemStates(frame, information_registry)
    yield registry
    if not registry._cleaned:
        registry.cleanup()


@pytest.fixture
def spy(states: SpellSystemStates) -> _PublicationSpy:
    """A publication spy wired into the registry."""
    manager = _PublicationSpy(states)
    states.set_risk_manager(manager)
    return manager


def _contract_topology(version_id: str, keys: Sequence[Tuple[str, str]]) -> SpellLocalTopology:
    """A local topology with one SPELL_CONTRACT socket per key, as Phase 3 records a consumer's contracts."""
    return SpellLocalTopology(
        spell_id=version_id,
        sockets=tuple(
            SpellSocketDescriptor(
                spell_id=version_id,
                param_name=f"contract_{position}",
                position=position,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=key,
            )
            for position, key in enumerate(keys)
        ),
    )


def _lineage(
        states: SpellSystemStates,
        version_id: str,
        book_id: str,
        *,
        key: Optional[Tuple[str, str]] = None,
        depends_on: Iterable[SpellIndex] = (),
        consumes: Sequence[Tuple[str, str]] = (),
) -> SpellIndex:
    """
    Register one lineage as bind and Phase 3 would, and leave it `valid`.

    Contract:
        - `register_index` with the owner Book and the binding key.
        - `update_dependencies` with the dependencies' current version ids (the reverse edges).
        - `register_local_topology` with one SPELL_CONTRACT socket per consumed key (the contract index).
        - `clear_dirty`, so a later mark is observable as a change.
    """
    index = SpellIndex(version_id)
    states.register_index(index, owner_spellbook_id=book_id, binding_key=key)
    dependencies = [dependency.selected_spell_id for dependency in depends_on]
    if dependencies:
        states.update_dependencies(index, dependencies)
    if consumes:
        states.register_local_topology(index, _contract_topology(version_id, consumes))
    _state(states, index).clear_dirty(time.time())
    return index


def _state(states: SpellSystemStates, index: SpellIndex) -> SpellSystemState:
    """The lineage's registered state."""
    state = states.get_by_index_id(index.id)
    assert state is not None
    return state


def _assert_valid(states: SpellSystemStates, *indexes: SpellIndex) -> None:
    """Every given lineage is still `valid`, untouched by a walk."""
    for index in indexes:
        assert _state(states, index).validity is SpellValidity.valid


def _assert_edge_marked(states: SpellSystemStates, index: SpellIndex) -> None:
    """The lineage carries the edge mark: gated, impacted_by_dependency, transitively dirty."""
    state = _state(states, index)
    assert state.validity is SpellValidity.gated
    assert state.has_flag(SpellState.impacted_by_dependency)
    assert state.transitively_dirty is True


def _assert_contract_marked(states: SpellSystemStates, index: SpellIndex) -> None:
    """The lineage carries rule 2's contract mark: gated, contract_unvalidated, not transitively dirty."""
    state = _state(states, index)
    assert state.validity is SpellValidity.gated
    assert state.has_flag(SpellState.contract_unvalidated)
    assert state.change_reason is SpellStateChangeReason.contract_unvalidated
    assert state.transitively_dirty is False


KEY_D = ("idep", "dep")
KEY_P = ("iservice", "svc")


def test_walk_marks_a_chain_downstream_of_the_seed_and_leaves_the_seed(states: SpellSystemStates) -> None:
    """Q -> P -> D: a walk from D marks P and Q by edge, returns them, and leaves D as it was."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    p = _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    q = _lineage(states, "q-v1", "book-1", key=("q", "q"), depends_on=[p])

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {p.id, q.id}
    _assert_edge_marked(states, p)
    _assert_edge_marked(states, q)
    _assert_valid(states, d)


def test_walk_marks_contract_consumers_in_every_book_by_the_binding_key(states: SpellSystemStates) -> None:
    """A consumer of the notched lineage's key in another Book gets the contract mark; its dependent the edge mark."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_D])
    user = _lineage(states, "u-v1", "borrower", key=("user", "u"), depends_on=[consumer])

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {consumer.id, user.id}
    _assert_contract_marked(states, consumer)
    _assert_edge_marked(states, user)
    _assert_valid(states, d)


def test_walk_marks_consumers_of_a_lineage_reached_by_edge(states: SpellSystemStates) -> None:
    """D -> P by edge, and a consumer of P's key in another Book: the walk goes edge, then key (probe X1's shape)."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    p = _lineage(states, "p-v1", "lender", key=KEY_P, depends_on=[d])
    consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_P])

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {p.id, consumer.id}
    _assert_edge_marked(states, p)
    _assert_contract_marked(states, consumer)


def test_walk_gives_a_lineage_reached_both_ways_both_marks(states: SpellSystemStates) -> None:
    """A lineage that depends on D by edge and consumes D's key carries both flags and is transitively dirty."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    both = _lineage(states, "x-v1", "book-2", key=("x", "x"), depends_on=[d], consumes=[KEY_D])

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {both.id}
    state = _state(states, both)
    assert state.validity is SpellValidity.gated
    assert state.has_flag(SpellState.contract_unvalidated)
    assert state.has_flag(SpellState.impacted_by_dependency)
    assert state.transitively_dirty is True


def test_walk_follows_edges_only_for_a_lineage_without_a_recorded_key(states: SpellSystemStates) -> None:
    """With no binding key recorded for D, a consumer of D's would-be key is not reached; D's edge dependent is."""
    d = _lineage(states, "d-v1", "book-1", key=None)
    p = _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    consumer = _lineage(states, "c-v1", "book-2", key=("consumer", "c"), consumes=[KEY_D])

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {p.id}
    _assert_edge_marked(states, p)
    _assert_valid(states, consumer)


def test_walk_terminates_on_a_contract_cycle_across_books_and_never_marks_a_seed(states: SpellSystemStates) -> None:
    """A consumes B's key and B consumes A's key, in two Books: the walk from A marks B once and leaves A."""
    key_a, key_b = ("a", "a"), ("b", "b")
    a = _lineage(states, "a-v1", "book-1", key=key_a, consumes=[key_b])
    b = _lineage(states, "b-v1", "book-2", key=key_b, consumes=[key_a])

    marked = states.mark_dependents_for_revalidation([a.id])

    assert marked == {b.id}
    _assert_contract_marked(states, b)
    _assert_valid(states, a)


def test_walk_skips_a_dependent_with_no_registered_state(states: SpellSystemStates) -> None:
    """A reverse edge naming no registered lineage is passed over, neither marked nor returned."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    p = _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    _state(states, d).add_dependent("ghost-lineage")

    marked = states.mark_dependents_for_revalidation([d.id])

    assert marked == {p.id}


def test_walk_with_no_seed_marks_nothing(states: SpellSystemStates, spy: _PublicationSpy) -> None:
    """Empty and blank seeds mark and publish nothing."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    spy.published.clear()

    assert states.mark_dependents_for_revalidation([]) == set()
    assert states.mark_dependents_for_revalidation(["", None]) == set()
    assert spy.published == []


def test_walk_publishes_once_per_changed_validity_under_the_registry_lock(
        states: SpellSystemStates,
        spy: _PublicationSpy,
) -> None:
    """The first walk publishes `gated` once per marked lineage; a second walk publishes nothing (idempotent)."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    p = _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    consumer = _lineage(states, "c-v1", "book-2", key=("consumer", "c"), consumes=[KEY_P])
    spy.published.clear()

    first = states.mark_dependents_for_revalidation([d.id])
    published_first = list(spy.published)
    second = states.mark_dependents_for_revalidation([d.id])

    assert first == second == {p.id, consumer.id}
    expected = [(p.id, SpellValidity.gated, True), (consumer.id, SpellValidity.gated, True)]
    assert sorted(published_first) == sorted(expected)
    assert spy.published == published_first


def test_walk_adds_every_marked_lineage_to_the_dirty_set(states: SpellSystemStates) -> None:
    """The marked lineages join the dirty worklist; the seed is not added by the walk."""
    d = _lineage(states, "d-v1", "book-1", key=KEY_D)
    p = _lineage(states, "p-v1", "book-1", key=KEY_P, depends_on=[d])
    states.consume_dirty_indexes()

    states.mark_dependents_for_revalidation([d.id])

    assert states.consume_dirty_indexes() == [p.id]


def test_register_index_with_no_key_keeps_the_recorded_key(states: SpellSystemStates) -> None:
    """A registration that states no key (the transfer's calls) keeps the key bind recorded."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_D])
    states.register_index(d, owner_spellbook_id="lender")

    assert states.mark_dependents_for_revalidation([d.id]) == {consumer.id}


def test_register_index_with_a_key_replaces_the_recorded_key(states: SpellSystemStates) -> None:
    """A notch to a version with another binding key moves the walk to the new key's consumers."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    old_consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_D])
    new_key = ("idep", "renamed")
    new_consumer = _lineage(states, "n-v1", "borrower", key=("new", "n"), consumes=[new_key])
    states.register_index(d, owner_spellbook_id="lender", binding_key=new_key)

    assert states.mark_dependents_for_revalidation([d.id]) == {new_consumer.id}
    _assert_valid(states, old_consumer)


def test_unregister_index_forgets_the_binding_key(states: SpellSystemStates) -> None:
    """Once a lineage is unregistered, registering the same index again without a key follows no contract key."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_D])
    states.unregister_index(d)
    _state(states, consumer).clear_dirty(time.time())
    states.register_index(d, owner_spellbook_id="lender")

    assert states.mark_dependents_for_revalidation([d.id]) == set()
    _assert_valid(states, consumer)


def test_mark_contract_dependents_dirty_walks_on_and_returns_its_consumers_only(states: SpellSystemStates) -> None:
    """A contract mark gates the Book's consumers, marks their dependents too, and returns only the consumers."""
    consumer = _lineage(states, "c-v1", "borrower", key=("consumer", "c"), consumes=[KEY_P])
    user = _lineage(states, "u-v1", "borrower", key=("user", "u"), depends_on=[consumer])
    elsewhere = _lineage(states, "e-v1", "other-book", key=("e", "e"), consumes=[("consumer", "c")])

    impacted = states.mark_contract_dependents_dirty(spellbook_id="borrower", contract_keys=[KEY_P])

    assert impacted == {consumer.id}
    _assert_contract_marked(states, consumer)
    _assert_edge_marked(states, user)
    _assert_contract_marked(states, elsewhere)


def test_mark_contract_dependents_dirty_with_no_consumer_walks_nowhere(states: SpellSystemStates) -> None:
    """No consumer of the key in the Book: nothing is marked, and no walk starts."""
    d = _lineage(states, "d-v1", "lender", key=KEY_D)
    p = _lineage(states, "p-v1", "lender", key=KEY_P, depends_on=[d])

    assert states.mark_contract_dependents_dirty(spellbook_id="borrower", contract_keys=[KEY_P]) == set()
    _assert_valid(states, d, p)


def test_walk_on_a_cleaned_registry_raises(states: SpellSystemStates) -> None:
    """A walk on a cleaned registry raises the standard use-after-clean error."""
    states.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        states.mark_dependents_for_revalidation(["lineage"])


def test_cleanup_drops_the_binding_key_map(states: SpellSystemStates) -> None:
    """Registry cleanup removes the binding-key map with the other indices."""
    _lineage(states, "d-v1", "lender", key=KEY_D)

    states.cleanup()

    assert not hasattr(states, "_binding_key_by_index")
