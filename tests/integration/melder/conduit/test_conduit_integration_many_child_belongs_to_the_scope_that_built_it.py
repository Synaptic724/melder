"""
Regression tests (dynamic routes): a `many` dependency belongs to the root that built it, not to its holder's owner.

The owner's decision (EPIC-2026-10-20-reassess_many_child_disposal_ownership, DECISION note of 2026-10-24): a
disposal-bearing `many` dependency built for a slotted holder is recorded in, and disposed by, the meld's innermost
scope - here the store of the root that melds - exactly as a `many` root is. Two dynamic routes build a holder in one
store and its child through another root:
    - a borrowing root melds a `unique` holder contracted from its owner root: the holder lives in the owner's store;
      the borrower built the child, records it and disposes it at its teardown;
    - a non-leader cluster member melds a `unique_per_conduit_cluster` holder: the holder lives in the cluster's team
      store; the member built the child, records it and disposes it at its teardown.

Removed behaviour (0.2.8235-0.2.8265): the child was recorded with the holder - in the owner's store, in the
cluster's team store - and disposed only when that store ended. The automatic-world routes are covered by
`tests/component/melder/aether/conduit/test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py`.
"""

from collections.abc import Iterator
from typing import Any, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

pytestmark = pytest.mark.integration


class Child:
    """
    Disposal-bearing `many` dependency.

    Contract:
        `close` is the disposal method declared at bind; `closes` counts how many times Melder ran it.
    """

    def __init__(self) -> None:
        """Start undisposed."""
        self.closes: int = 0

    def close(self) -> None:
        """Record one disposal."""
        self.closes += 1


class ContractedHolder:
    """`unique` holder of one Child, contracted from its owner root to a borrowing root."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


class ClusterHolder:
    """`unique_per_conduit_cluster` holder of one Child, shared through a conduit cluster."""

    def __init__(self, child: Child) -> None:
        """Keep the injected child."""
        self.child = child


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give each test a fresh Aether and reset it again afterwards."""
    _reset_aether()
    yield
    _reset_aether()


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


def _bucket(store: Creations, child_id: str) -> List[Any]:
    """
    Return a copy of one store's live `many` bucket for Child's spell id (empty when it keeps none).

    Args:
        store: A creations store.
        child_id: Child's spell id.

    Returns:
        List[Any]: Every Child the store recorded.
    """
    return list(store._creations.get(child_id) or [])


def test_borrower_teardown_disposes_the_many_child_it_built_for_a_contracted_unique() -> None:
    """
    A borrowing root that first melds a contracted `unique` holder builds the holder's `many` child, so the borrower
    records the child and its teardown disposes it, once, while the owner keeps serving the holder.

    Symptom (0.2.8235-0.2.8265): the owner recorded the child with its unique holder, so the borrower's teardown left
    it open and the owner closed it at its own teardown.
    """
    configuration = _dynamic_configuration("default")
    owner_book = Spellbook(configuration=configuration)
    child_id = owner_book.bind(
        spell=Child, existence=Existence.many, permissions="create", disposal_method_names=["close"],
    )
    holder_id = owner_book.bind(spell=ContractedHolder, existence=Existence.unique, permissions="create")
    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="many_child_owner")
    borrower = borrower_book.conjure(dynamic=True, name="many_child_borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=holder_id, conduit=owner, permissions="create")
        assert borrower.validate_contracts_and_define()
        first = borrower.meld(spell_id=holder_id)
        assert first.child in _bucket(borrower._creations, child_id), (
            "the borrowing root built the child and must record it"
        )
        assert first.child not in _bucket(owner._creations, child_id), "the owner root must not record the child"
        assert owner._creations._disposable_creations.get(holder_id) is None, (
            "the owner must not tie the child to its holder"
        )
        borrower.cleanup()
        assert owner.meld(spell_id=holder_id) is first, "precondition: the holder outlives the borrower"
        assert first.child.closes == 1, "the borrower's teardown must dispose the many child it built"
    finally:
        borrower.cleanup()
        owner.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once"


def test_member_teardown_disposes_the_many_child_it_built_for_a_cluster_holder() -> None:
    """
    A non-leader cluster member that first melds the cluster's holder builds the holder's `many` child, so the
    member records the child and its teardown disposes it, once; neither the leader's teardown nor the cluster's
    deletion disposes it again.

    Symptom (0.2.8235-0.2.8265): the child was recorded with the holder - in the leader's store, from 0.2.8237 the
    cluster's team store - so the member's teardown left it open and the cluster's deletion closed it.
    """
    frame = "many-child-cluster"
    provider_book = Spellbook(aetheric_frame=frame, configuration=_dynamic_configuration(frame))
    child_id = provider_book.bind(
        spell=Child, existence=Existence.many, permissions="create", disposal_method_names=["close"],
    )
    holder_id = provider_book.bind(
        spell=ClusterHolder, existence=Existence.unique_per_conduit_cluster, permissions="create",
    )
    provider = provider_book.conjure(dynamic=True, name="many_child_provider")
    member_book = Spellbook(aetheric_frame=frame)
    member = member_book.conjure(dynamic=True, name="many_child_member")
    try:
        provider.link(member)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("many_child")
        for root in (provider, member):
            cloud.add_conduit_to_cluster(root, "many_child")
        for root in (provider, member):
            cloud.refresh_cluster_shares_for_conduit(root)
        cloud.get_cluster("many_child").elect_leader(provider.id)
        first = member.meld(spell_id=holder_id)
        team_store = cloud.get_cluster("many_child")._team_store
        assert first.child in _bucket(member._creations, child_id), "the member built the child and must record it"
        assert first.child not in _bucket(team_store, child_id), "the cluster's team store must not record the child"
        assert team_store._disposable_creations.get(holder_id) is None, (
            "the team store must not tie the child to the holder"
        )
        member.cleanup()
        assert provider.meld(spell_id=holder_id) is first, "precondition: the holder outlives the member"
        assert first.child.closes == 1, "the member's teardown must dispose the many child it built"
        provider.cleanup()
        cloud.delete_cluster("many_child")
        assert first.child.closes == 1, "neither the leader's teardown nor the cluster's deletion disposes it again"
    finally:
        member.cleanup()
        provider.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once"
