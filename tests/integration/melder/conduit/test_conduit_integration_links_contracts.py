from __future__ import annotations

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
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


def _make_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Create a dynamic configuration suitable for link/contract tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        Configuration: Dynamic configuration instance.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
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


def test_conduit_link_and_sever_updates_links() -> None:
    """
    Purpose:
        Validate link/sever operations update link lists.
    Contract:
        - link returns True and links appear in get_links.
        - sever_link returns True and links are removed.
    Returns:
        None.
    Raises:
        AssertionError: If links are not updated.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower in owner.get_links()
        assert owner in borrower.get_links()

        assert owner.sever_link(borrower) is True
        assert borrower not in owner.get_links()
        assert owner not in borrower.get_links()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_initiated_and_provider_accessors() -> None:
    """
    Purpose:
        Validate initiated/provider accessors after linking.
    Contract:
        - Initiator sees the target in initiated accessors.
        - Provider sees the initiator in provider accessors.
    Returns:
        None.
    Raises:
        AssertionError: If initiated/provider accessors are incorrect.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)

        assert owner.get_initiated_conduit(borrower.id) is borrower
        assert borrower.get_provider_conduit(owner.id) is owner

        assert borrower in owner.get_initiated_conduits()
        assert owner in borrower.get_provider_conduits()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_contract_add_remove_and_lookup() -> None:
    """
    Purpose:
        Validate contract add/remove flows and lookups.
    Contract:
        - add_spells_to_contract contracts each spell.
        - lookups return inbound spell ids.
        - removal APIs remove contracted spells.
    Returns:
        None.
    Raises:
        AssertionError: If contract state is incorrect.
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
        owner.link(borrower)

        results = borrower.add_spells_to_contract(
            spell_ids=[service_id, config_id],
            conduit=owner,
            permissions="create",
        )
        assert results == {service_id: True, config_id: True}

        spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner.id)
        assert set(_inbound_spell_ids(spells_by_conduit)) == {service_id, config_id}

        spells_by_name = borrower.get_spells_in_contract_by_conduit_name("owner")
        assert set(_inbound_spell_ids(spells_by_name)) == {service_id, config_id}

        all_contracts = borrower.get_all_spells_in_contracts(validate=True)
        assert all_contracts is not None
        assert owner.id in all_contracts
        assert len(all_contracts[owner.id]) == 2

        spell_in_contract = borrower.get_spell_in_contracts(service_id)
        assert spell_in_contract is not None
        assert spell_in_contract[0] == owner.id

        contracted = borrower.get_contracted_conduits()
        assert contracted is not None
        assert any(conduit_id == owner.id for conduit_id, _conduit in contracted)

        validation = borrower.validate_contracts_and_define()
        assert validation
        assert all(isinstance(value, bool) for value in validation.values())
        assert borrower.validate_received_contracts() is True

        assert borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner) is True
        assert borrower.get_spell_in_contracts(service_id) is None

        remove_results = borrower.remove_spells_from_contract(
            spell_ids=[config_id],
            conduit=owner,
        )
        assert remove_results == {config_id: True}
        assert borrower.get_spell_in_contracts(config_id) is None
        assert _inbound_spell_ids(borrower.get_spells_in_contract_by_conduit(owner.id)) == []
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_remove_root_from_contracts_clears_root() -> None:
    """
    Purpose:
        Validate remove_root_from_contracts removes root spell entries.
    Contract:
        - add_spell_to_contract_with_dependencies adds the root.
        - remove_root_from_contracts clears the root spell.
    Returns:
        None.
    Raises:
        AssertionError: If root removal does not clear contracts.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        assert borrower.add_spell_to_contract_with_dependencies(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        report = borrower.remove_root_from_contracts(
            root_spell_id=spell_id,
            conduit=owner,
        )
        assert report["failed"] == {}
        assert borrower.get_spell_in_contracts(spell_id) is None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_set_new_policy_requires_dynamic() -> None:
    """
    Purpose:
        Validate set_new_policy rejects non-dynamic environments.
    Contract:
        - set_new_policy raises when dynamic mode is disabled.
    Returns:
        None.
    Raises:
        AssertionError: If policy changes succeed in automatic mode.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
            conduit.set_new_policy("whitelist_all")
    finally:
        conduit.cleanup()


def test_conduit_upgrade_to_normal_requires_dynamic() -> None:
    """
    Purpose:
        Validate upgrade_to_normal rejects non-dynamic environments.
    Contract:
        - upgrade_to_normal raises on a lesser conduit in automatic mode.
    Returns:
        None.
    Raises:
        AssertionError: If upgrade succeeds in automatic mode.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
            lesser.upgrade_to_normal(name="upgraded")
    finally:
        conduit.cleanup()
