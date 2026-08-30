from __future__ import annotations

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


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
        Create a dynamic configuration suitable for link/contract tests.
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

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
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

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
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

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)

        with borrower.transaction("link", conduits=[borrower, owner]):
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

        with borrower.transaction("link", conduits=[borrower, owner]):
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

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
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


def test_conduit_spell_contract_resolves_after_dynamic_link() -> None:
    """
    Purpose:
        Validate SpellContract sockets resolve after dynamic conduit linking.
    Contract:
        - A linked provider conduit can satisfy a SpellContract dependency.
        - The resolved dependency is an instance of the contracted spell.
    Returns:
        None.
    Raises:
        AssertionError: If SpellContract sockets do not resolve after linking.
    """
    class ContractConsumer:
        """
        Purpose:
            Provide a consumer that declares a SpellContract dependency.
        Contract:
            - Declares a SpellContract socket for IService.
            - Stores the resolved service for assertions.
        """
        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the resolved contract service dependency.
            Contract:
                Stores the resolved service instance on the consumer.
            Args:
                service: Resolved service instance for this consumer.
            Returns:
                None.
            """
            self.service = service

    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumer,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell_id=consumer_id)

        assert isinstance(instance, ContractConsumer)
        assert isinstance(instance.service, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_spell_contract_missing_provider_raises() -> None:
    """
    Purpose:
        Validate SpellContract raises when no contracted provider exists.
    Contract:
        - Missing contracted providers gate validation during meld.
    Returns:
        None.
    Raises:
        AssertionError: If missing contracts do not raise.
    """
    class LocalService:
        """
        Purpose:
            Provide a local IService implementation for fallback resolution.
        Contract:
            - Stores a marker for assertions.
        """

        def __init__(self, marker: str = "local") -> None:
            """
            Purpose:
                Initialize the local marker.
            Contract:
                Stores the provided marker on the instance.
            Args:
                marker: Marker for assertions.
            Returns:
                None.
            """
            self.marker = marker

    class ContractConsumer:
        """
        Purpose:
            Provide a consumer with a SpellContract dependency.
        Contract:
            - Declares a SpellContract socket for IService.
            - Stores the resolved service for assertions.
        """

        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the resolved service dependency.
            Contract:
                Stores the service instance on the consumer.
            Args:
                service: Resolved service instance.
            Returns:
                None.
            """
            self.service = service

    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=LocalService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_id = spellbook.bind(
        spell=ContractConsumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="local")
    try:
        assert conduit.validate_contracts_and_define() == {}
        with pytest.raises(SpellbookValidationError, match="Spellbook validation failed"):
            conduit.meld(spell_id=consumer_id)
    finally:
        conduit.cleanup()


def test_conduit_spell_contract_prefers_contracted_spell() -> None:
    """
    Purpose:
        Validate SpellContract prefers contracted spells when available.
    Contract:
        - Contracted spells are used when available.
        - Local providers do not override contracted resolution.
    Returns:
        None.
    Raises:
        AssertionError: If the contracted spell is not selected.
    """
    class LocalService:
        """
        Purpose:
            Provide a local IService implementation for fallback comparison.
        Contract:
            - Stores a marker for assertions.
        """

        def __init__(self, marker: str = "local") -> None:
            """
            Purpose:
                Initialize the local marker.
            Contract:
                Stores the marker on the instance.
            Args:
                marker: Marker for assertions.
            Returns:
                None.
            """
            self.marker = marker

    class ContractConsumer:
        """
        Purpose:
            Provide a consumer with a SpellContract dependency.
        Contract:
            - Declares a SpellContract socket for IService.
            - Stores the resolved service for assertions.
        """

        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the resolved service dependency.
            Contract:
                Stores the service instance on the consumer.
            Args:
                service: Resolved service instance.
            Returns:
                None.
            """
            self.service = service

    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )

    borrower_book = Spellbook(configuration=configuration)
    borrower_book.bind(
        spell=LocalService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="local",
    )
    consumer_id = borrower_book.bind(
        spell=ContractConsumer,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell_id=consumer_id)

        assert isinstance(instance, ContractConsumer)
        assert isinstance(instance.service, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_spell_contract_applies_override_payload() -> None:
    """
    Purpose:
        Validate SpellContract spell_override applies to provider construction.
    Contract:
        - spell_override payload is passed to the provider constructor.
    Returns:
        None.
    Raises:
        AssertionError: If the override is not applied.
    """
    class ContractConsumer:
        """
        Purpose:
            Provide a consumer that supplies a SpellContract override.
        Contract:
            - Declares a SpellContract socket with a spell_override payload.
            - Stores the resolved service for assertions.
        """

        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
                spell_override={"marker": "override"},
            ),
        ) -> None:
            """
            Purpose:
                Capture the resolved service dependency.
            Contract:
                Stores the service instance on the consumer.
            Args:
                service: Resolved service instance.
            Returns:
                None.
            """
            self.service = service

    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumer,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell_id=consumer_id)

        assert isinstance(instance, ContractConsumer)
        assert isinstance(instance.service, BasicService)
        assert instance.service.marker == "override"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_spell_contract_ambiguous_contracted_raises() -> None:
    """
    Purpose:
        Validate a duplicate provider for a signature is rejected at bind time.
    Contract:
        - Binding a second provider for an active signature raises (framewide).
    Returns:
        None.
    Raises:
        AssertionError: If duplicate contracts are not rejected.
    """
    class AltService:
        """
        Purpose:
            Provide an alternate IService implementation for ambiguity tests.
        Contract:
            - Stores a marker for assertions.
        """

        def __init__(self, marker: str = "alt") -> None:
            """
            Purpose:
                Initialize the alternate marker.
            Contract:
                Stores the marker on the instance.
            Args:
                marker: Marker for assertions.
            Returns:
                None.
            """
            self.marker = marker

    class ContractConsumer:
        """
        Purpose:
            Provide a consumer with a SpellContract dependency.
        Contract:
            - Declares a SpellContract socket for IService.
            - Stores the resolved service for assertions.
        """

        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the resolved service dependency.
            Contract:
                Stores the service instance on the consumer.
            Args:
                service: Resolved service instance.
            Returns:
                None.
            """
            self.service = service

    configuration = _make_dynamic_configuration()
    owner_a_book = Spellbook(configuration=configuration)
    owner_a_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    owner_b_book = Spellbook(configuration=configuration)
    try:
        # Framewide one-active-signature-per-frame: the ambiguous second provider
        # for (IService, primary) is rejected at bind on the shared frame, before
        # any contract can be formed.
        with pytest.raises(RuntimeError, match="already active in this frame"):
            owner_b_book.bind(
                spell=AltService,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="primary",
            )
    finally:
        owner_b_book.cleanup()
        owner_a_book.cleanup()
