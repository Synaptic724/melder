"""
Regression tests (dynamic routes): a disposal-bearing `many` child is disposed with the holder it was built for.

The defect (TASK-2026-10-14-prove_many_child_registration_bug, measured on 0.2.8234):
    The site plan registers a slotted holder's `many` child in the meld's innermost scope - the store of the
    conduit that melds - instead of the store the holder is published to. In a dynamic world two more routes
    reach it, both across normal roots:
        - a borrowing root melds a `unique` holder contracted from its owner root: the holder lives in the
          owner's store, the child in the borrower's, so tearing the borrower down closes the child of a holder
          the owner keeps returning;
        - a non-leader cluster member melds a `unique_per_conduit_cluster` holder: the holder lives in the elected
          leader's store (since 0.2.8237 the cluster's own team store), the child in the member's, so tearing the
          member down closes it the same way.
    The automatic-world routes are covered by
    `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py`.

Corrected behaviour asserted here - the owner's rule (EPIC-2026-10-14-many_child_follows_holder, Decision Log
2026-10-14): a holder's `many` child belongs to whatever owns the holder. The child is recorded in the owner's
(or the leader's) store, not the store of the root that melded it; tearing that root down does not dispose the
child while the holder lives; the child is disposed exactly once, when the holder's own store is.

Both tests fail on 0.2.8234 by design and pass once a child follows its holder.
"""

from collections.abc import Iterator
from typing import Any, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations, HolderDisposalEntry
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


def _adopted(store: Creations, holder_id: str) -> List[Any]:
    """
    Return the children one store records with a holder, in build order.

    Since 0.2.8238 a holder's `many` children leave their spell's bucket once the holder is published and live in
    the holder's disposal record (`HolderDisposalEntry`).

    Args:
        store: The creations store that holds the holder.
        holder_id: The holder's spell id.

    Returns:
        List[Any]: The adopted children; empty when the store keeps no record for the holder.
    """
    record = store._disposable_creations.get(holder_id)
    if not isinstance(record, HolderDisposalEntry):
        return []
    return [child for child, _methods in record.children]


def test_borrower_teardown_disposes_the_many_child_of_a_contracted_unique_it_first_melded() -> None:
    """
    A borrowing root's teardown must not dispose the `many` child of a contracted `unique` holder.

    Symptom (0.2.8234): the borrower melds the holder first through its contract; the holder is published in the
    owner's store and its child recorded in the borrower's. Tearing the borrower down closes the child while the
    owner keeps returning the same holder. Corrected: the child is closed once, at the owner's teardown.
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
        assert _adopted(owner._creations, holder_id) == [first.child], (
            "the owner root must record the child of the unique holder it owns"
        )
        assert first.child not in list(borrower._creations._creations.get(child_id) or []), (
            "the borrowing root must not record the child"
        )
        borrower.cleanup()
        assert owner.meld(spell_id=holder_id) is first, "precondition: the holder outlives the borrower"
        assert first.child.closes == 0, (
            "the borrower's teardown disposed the many child of a unique holder its owner still hands out"
        )
    finally:
        borrower.cleanup()
        owner.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, with its holder"


def test_member_teardown_disposes_the_many_child_of_a_cluster_holder_it_first_melded() -> None:
    """
    A non-leader cluster member's teardown must not dispose the `many` child of the cluster's holder.

    Symptom (0.2.8234): the member melds the cluster holder first; the holder is published in the elected
    leader's store and its child recorded in the member's. Tearing the member down closes the child while the
    leader keeps returning the same holder. Corrected (0.2.8235): the child is recorded with the holder's owner.
    Since 0.2.8237 that owner is the cluster (its team store, not the leader conduit's store), so neither the
    member's nor the leader's teardown disposes the child; deleting the cluster does, once.
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
        assert _adopted(team_store, holder_id) == [first.child], (
            "the cluster's team store must record the child of the cluster holder it stores"
        )
        assert first.child not in list(member._creations._creations.get(child_id) or []), (
            "the member root must not record the child"
        )
        assert first.child not in list(provider._creations._creations.get(child_id) or []), (
            "the leader conduit's own store must not record the child"
        )
        member.cleanup()
        assert provider.meld(spell_id=holder_id) is first, "precondition: the holder outlives the member"
        assert first.child.closes == 0, (
            "the member's teardown disposed the many child of a cluster holder the leader still hands out"
        )
        provider.cleanup()
        assert first.child.closes == 0, "the leader's teardown disposed a child the cluster owns"
        cloud.delete_cluster("many_child")
    finally:
        member.cleanup()
        provider.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, with the cluster that owns its holder"
