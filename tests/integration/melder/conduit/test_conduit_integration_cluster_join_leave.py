"""Integration tests: unique_per_conduit_cluster team-store facade across
cluster join / leave / leader-leave, exercised through the real meld front door.

Validation: Not run.
"""

from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """Reset the Aether singleton around each cluster join/leave integration test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_cluster_owner() -> tuple[Spellbook, Conduit, str]:
    """Bind a unique_per_conduit_cluster spell on a dynamic owner book and conjure."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    return owner_book, owner, spell_id


def test_cluster_join_into_live_cluster_shares_leader_instance() -> None:
    """A conduit that joins an already-elected cluster melds the leader's instance."""
    _owner_book, owner, spell_id = _make_cluster_owner()
    borrower = Spellbook().conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("cluster-a").elect_leader(owner.id)

        owner_instance = owner.meld(spell=spell_id)

        # Borrower joins the LIVE cluster: handle_join binds its facade to the
        # leader store and the refresh shares the cluster spell to it.
        cloud.add_conduit_to_cluster(borrower, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)

        borrower_instance = borrower.meld(spell=spell_id)
        assert borrower_instance is owner_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_cluster_non_leader_leave_keeps_leader_active() -> None:
    """A non-leader leaving leaves the leader and its shared instance intact."""
    _owner_book, owner, spell_id = _make_cluster_owner()
    borrower = Spellbook().conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("cluster-a").elect_leader(owner.id)

        owner_instance = owner.meld(spell=spell_id)
        assert borrower.meld(spell=spell_id) is owner_instance

        cloud.remove_conduit_from_cluster(borrower, "cluster-a")

        # The leader is untouched: it still resolves the same shared instance.
        assert owner.meld(spell=spell_id) is owner_instance
        # The leaver's team-store facade was dropped.
        assert borrower._cluster_creations.is_active() is False
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_cluster_leader_leave_dissolves_and_hard_errors() -> None:
    """The elected leader leaving dissolves the cluster; cluster melds hard-error."""
    _owner_book, owner, spell_id = _make_cluster_owner()
    borrower = Spellbook().conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("cluster-a").elect_leader(owner.id)

        owner_instance = owner.meld(spell=spell_id)
        assert borrower.meld(spell=spell_id) is owner_instance

        cloud.remove_conduit_from_cluster(owner, "cluster-a")

        # Dissolved to inert: the owner still owns the spell, so it resolves to a
        # Spell, but the team-store facade is now disabled and the meld door
        # hard-errors.
        with pytest.raises(RuntimeError, match="no elected cluster leader"):
            owner.meld(spell=spell_id)
        assert cloud.get_cluster("cluster-a").master_conduit_id is None
    finally:
        borrower.cleanup()
        owner.cleanup()
