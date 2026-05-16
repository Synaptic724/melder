from __future__ import annotations

from typing import Any, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Layer2A
from tests.mocks.spellbook.deep_layers import Depth3Layer2B
from tests.mocks.spellbook.deep_layers import Depth3LeafA
from tests.mocks.spellbook.deep_layers import Depth3LeafB
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


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
        Create a dynamic configuration suitable for contract/link edge tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    configuration.dynamic_defaults()
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


def test_conduit_remove_all_spells_from_contract_clears_inbound_keeps_link() -> None:
    """
    Purpose:
        Validate removing all spells clears contracted spells without severing the link.
    Contract:
        - remove_all_spells_from_contract clears inbound spell lists.
        - get_contracted_conduits still reports the linked conduit.
    Returns:
        None.
    Raises:
        AssertionError: If contract clearing or link retention fails.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spells_to_contract(
                spell_ids=[service_id, config_id],
                conduit=owner,
                permissions="create",
            ) == {service_id: True, config_id: True}

        assert borrower.get_spells_in_contract_by_conduit(owner.id) is not None
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower._remove_all_spells_from_contract(conduit=owner) is True
        assert borrower.get_spells_in_contract_by_conduit(owner.id) == {
            "inbound": [],
            "outbound": [],
        }

        contracted = borrower.get_contracted_conduits()
        assert contracted is not None
        assert any(conduit_id == owner.id for conduit_id, _conduit in contracted)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_describe_contract_reports_spell_count_and_permissions() -> None:
    """
    Purpose:
        Validate contract description reports spell count and permissions.
    Contract:
        - describe_contract reflects the provider's granted spell list.
        - permissions match the contract permissions for each spell.
    Returns:
        None.
    Raises:
        AssertionError: If contract descriptions are incorrect.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="read",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            ) is True
            assert borrower.add_spell_to_contract(
                spell_id=config_id,
                conduit=owner,
                permissions="read",
            ) is True

        description = owner._describe_contract(borrower.id)
        assert description["spell_count"] == 2
        spell_permissions = {
            (entry["spell_id"], entry["permissions"])
            for entry in description["spells"]
        }
        assert spell_permissions == {
            (service_id, "create"),
            (config_id, "read"),
        }
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_add_spell_to_contract_permission_mismatch_raises() -> None:
    """
    Purpose:
        Validate re-adding a spell with different permissions is rejected.
    Contract:
        - A second add with a different permission raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If permission mismatches are allowed.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            ) is True
            with pytest.raises(RuntimeError, match="different permissions"):
                borrower.add_spell_to_contract(
                    spell_id=service_id,
                    conduit=owner,
                    permissions="read",
                )
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_sever_link_raises_when_unlinked() -> None:
    """
    Purpose:
        Validate sever_link rejects unlinked conduits.
    Contract:
        - sever_link raises when no contract exists.
    Returns:
        None.
    Raises:
        AssertionError: If sever_link succeeds without a link.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        with pytest.raises(RuntimeError, match="No contract found"):
            owner.sever_link(borrower)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_remove_root_from_contracts_preserves_shared_dependencies() -> None:
    """
    Purpose:
        Validate root removal drops only the selected root and orphaned deps.
    Contract:
        - Removing a root removes its unique dependencies.
        - Dependencies shared by another root remain contracted.
    Returns:
        None.
    Raises:
        AssertionError: If root removal clears shared dependencies.
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
            assert borrower.add_spell_to_contract_with_dependencies(
                spell_id=depth3_ids[Depth3Layer2A],
                conduit=owner,
                permissions="create",
            )

            report = borrower.remove_root_from_contracts(
                root_spell_id=depth3_ids[Depth3Root],
                conduit=owner,
            )
        assert report["failed"] == {}

        inbound_ids = set(_inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)))
        assert depth3_ids[Depth3Root] not in inbound_ids
        assert depth3_ids[Depth3Layer2B] not in inbound_ids
        assert depth3_ids[Depth3Layer2A] in inbound_ids
        assert depth3_ids[Depth3LeafA] in inbound_ids
        assert depth3_ids[Depth3LeafB] in inbound_ids
    finally:
        borrower.cleanup()
        owner.cleanup()
