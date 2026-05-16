from __future__ import annotations

from typing import Any, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
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
        Create a dynamic configuration for dependency and cluster tests.
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


def _bind_graph(
    spellbook: Spellbook,
    classes: Iterable[type],
    *,
    existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind a dependency graph into the spellbook for integration tests.
    Contract:
        - Each class is bound with the requested Existence.
        - Returns a mapping of class -> spell_id.
    Args:
        spellbook: Target spellbook for bindings.
        classes: Classes to bind in dependency order.
        existence: Existence mode to apply to each binding.
    Returns:
        dict[type, str]: Mapping of class to spell_id.
    """
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


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


def test_conduit_add_spell_to_contract_with_dependencies_links_transitive_dependencies() -> None:
    """
    Purpose:
        Validate contract helper links transitive dependencies.
    Contract:
        - Root and dependency spell ids are all contracted.
        - Contract inspection returns the owner id for the root.
    Returns:
        None.
    Raises:
        AssertionError: If dependency linkage is incomplete.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
            )

        spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner.id)
        inbound_ids = set(_inbound_spell_ids(spells_by_conduit))
        assert inbound_ids == set(depth3_ids.values())

        root_entry = borrower.get_spell_in_contracts(depth3_ids[Depth3Root])
        assert root_entry is not None
        assert root_entry[0] == owner.id
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_refresh_cluster_shares_noop_when_no_clusters() -> None:
    """
    Purpose:
        Ensure refresh_cluster_shares is a no-op without cluster membership.
    Contract:
        - No exception is raised when no clusters exist.
        - list_clusters remains empty after refresh.
    Returns:
        None.
    Raises:
        AssertionError: If cluster state changes unexpectedly.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    conduit = spellbook.conjure(automatic=False, name="owner")
    try:
        assert conduit.list_clusters() == []
        conduit.refresh_cluster_shares()
        assert conduit.list_clusters() == []
    finally:
        conduit.cleanup()
