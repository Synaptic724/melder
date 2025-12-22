from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_conduit_unique_reuses_across_lineage() -> None:
    """
    Purpose:
        Validate Existence.unique reuses instances across a conduit lineage.
    Contract:
        - Root and lesser conduits resolve the same instance.
        - Instance type matches the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not shared across the lineage.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        assert root_instance is lesser_instance
        assert isinstance(root_instance, BasicService)
    finally:
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_unique_per_conduit_isolated_per_conduit() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit isolates instances per conduit.
    Contract:
        - Root and lesser conduits receive different instances.
        - Each conduit reuses its own instance on repeated melds.
    Returns:
        None.
    Raises:
        AssertionError: If instances leak across conduits or are not reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        assert root_instance is not lesser_instance
        assert conduit.meld(spell=spell_id) is root_instance
        assert lesser.meld(spell=spell_id) is lesser_instance
    finally:
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_many_creates_new_each_time() -> None:
    """
    Purpose:
        Validate Existence.many creates a new instance per meld call.
    Contract:
        - Each meld call returns a distinct instance.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
    finally:
        conduit.cleanup()


def test_conduit_unique_per_conduit_lineage_reuses_across_lineage() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit_lineage reuses across a lineage.
    Contract:
        - Root and nested lesser conduits resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If lineage sharing fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    nested = lesser.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        nested_instance = nested.meld(spell=spell_id)
        assert root_instance is lesser_instance is nested_instance
    finally:
        nested.cleanup()
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_unique_per_spell_space_scopes_instances() -> None:
    """
    Purpose:
        Validate Existence.unique_per_spell_space scopes instances to a spellspace.
    Contract:
        - Reuses within the same spellspace.
        - Creates a new instance for a new spellspace.
        - Raises when no spellspace is active.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace scoping is incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld(spell=spell_id)
            second = space.meld(spell=spell_id)
            assert first is second
        with conduit.enter_spellspace() as space:
            third = space.meld(spell=spell_id)
            assert third is not first
        with pytest.raises(SpellSpaceScopeError, match="requires an active SpellSpace"):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_conduit_unique_per_conduit_cluster_shares_across_cluster() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit_cluster shares across a cluster.
    Contract:
        - Two conduits in the same cluster resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not shared across the cluster.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")

    borrower_book = Spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")

    owner.link(borrower)
    owner.create_cluster("cluster-a")
    owner.join_cluster("cluster-a")
    borrower.join_cluster("cluster-a")
    owner.refresh_cluster_shares()

    try:
        owner_instance = owner.meld(spell=spell_id)
        borrower_instance = borrower.meld(spell=spell_id)
        assert owner_instance is borrower_instance
    finally:
        borrower.cleanup()
        owner.cleanup()
