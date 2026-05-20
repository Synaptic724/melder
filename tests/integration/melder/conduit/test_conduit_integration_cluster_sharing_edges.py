from __future__ import annotations

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Layer2A
from tests.mocks.spellbook.deep_layers import Depth3Layer2B
from tests.mocks.spellbook.deep_layers import Depth3LeafA
from tests.mocks.spellbook.deep_layers import Depth3LeafB
from tests.mocks.spellbook.deep_layers import Depth3Root


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
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


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for cluster sharing tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _inbound_spell_ids(spells_by_conduit: dict[str, list[tuple[str, Any]]] | None) -> list[str]:
    """
    Purpose:
        Extract inbound spell ids from a contract snapshot.
    Contract:
        - Returns spell ids from inbound entries only.
    Args:
        spells_by_conduit: Contract snapshot from get_spells_in_contract_by_conduit.
    Returns:
        list[str]: Inbound spell ids.
    """
    if not spells_by_conduit:
        return []
    inbound = spells_by_conduit.get("inbound", [])
    return [spell_id for spell_id, _spell in inbound]


def _bind_depth3_cluster_root(spellbook: Spellbook) -> dict[type, str]:
    """
    Purpose:
        Bind a depth-3 graph with a cluster-shareable root and local dependencies.
    Contract:
        - Dependencies use Existence.unique.
        - The root uses Existence.unique_per_conduit_cluster.
        - Returns class -> spell_id mapping.
    Args:
        spellbook: Target spellbook for bindings.
    Returns:
        dict[type, str]: Mapping of class to spell_id.
    """
    spell_ids: dict[type, str] = {}
    for cls in (Depth3LeafA, Depth3LeafB, Depth3Layer2A, Depth3Layer2B):
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.unique,
            permissions="create",
        )
    spell_ids[Depth3Root] = spellbook.bind(
        spell=Depth3Root,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    return spell_ids


def test_conduit_cluster_auto_link_dependencies_toggle() -> None:
    """
    Purpose:
        Validate cluster auto-link dependency toggle controls shared contracts.
    Contract:
        - With auto-link disabled, only roots are contracted.
        - Enabling auto-link and refreshing shares adds dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If cluster sharing does not respect dependency toggle.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    depth3_ids = _bind_depth3_cluster_root(owner_book)
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cluster = cloud._get_cluster("cluster-a")
        cluster.set_auto_link_dependencies(False)
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert inbound_ids == {depth3_ids[Depth3Root]}

        cluster.set_auto_link_dependencies(True)
        cloud.refresh_cluster_shares_for_conduit(owner)

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert inbound_ids == set(depth3_ids.values())
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_cluster_refresh_shares_after_new_bind() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares picks up new shareable roots.
    Contract:
        - Newly bound unique_per_conduit_cluster roots are shared after refresh.
    Returns:
        None.
    Raises:
        AssertionError: If refresh does not propagate new roots.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert inbound_ids == {service_id}

        with owner.binding_transaction():
            config_id = owner.bind(
                spell=BasicConfig,
                existence=Existence.unique_per_conduit_cluster,
                permissions="create",
            )
        cloud.refresh_cluster_shares_for_conduit(owner)

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert inbound_ids == {service_id, config_id}
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_cluster_leave_preserves_manual_contracts() -> None:
    """
    Purpose:
        Validate leaving a cluster removes only cluster-root sources.
    Contract:
        - Manual contract sources remain after cluster leave.
    Returns:
        None.
    Raises:
        AssertionError: If manual contracts are removed on leave.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            ) is True

        cloud.remove_conduit_from_cluster(borrower, "cluster-a")

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert inbound_ids == {service_id}
    finally:
        borrower.cleanup()
        owner.cleanup()
