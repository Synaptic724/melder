import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.mocks.spellbook.contract_classes import ContractConsumerDualOverride
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideArgsDict
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideList
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideTuple
from tests.mocks.spellbook.contract_classes import ContractConsumerPrimary
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell_contracts() -> None:
    """
    Purpose:
        Ensure component spell contract tests start with a clean Aether singleton.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Build a dynamic spellbook for SpellContract component tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        Spellbook: Configured spellbook.
    """
    config = Configuration()
    config.dynamic_defaults()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


@contextlib.contextmanager
def _conjured(spellbook: Spellbook) -> Iterator[Conduit]:
    """
    Purpose:
        Conjure a conduit and ensure cleanup.
    Contract:
        - Yields a conduit for the provided spellbook.
        - Always cleans up the conduit.
    Args:
        spellbook: Spellbook used to conjure the conduit.
    Returns:
        Iterator[Conduit]: Context-managed conduit.
    """
    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        yield conduit
    finally:
        conduit.cleanup()


def test_component_spell_contract_path_override_targets_dependency() -> None:
    """
    Purpose:
        Validate PATH overrides target SpellContract dependencies.
    Contract:
        - PATH overrides replace the SpellContract socket value.
    Returns:
        None.
    Raises:
        AssertionError: If path overrides do not apply.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        override_instance = ContractServicePrimary(marker="path")
        instance = borrower.meld(
            spell=consumer_id,
            spell_override={"service": override_instance},
        )
        assert instance.service is override_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_broadcast_override_targets_dependency() -> None:
    """
    Purpose:
        Validate BROADCAST overrides target SpellContract dependencies.
    Contract:
        - Broadcast overrides replace the SpellContract socket value.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast overrides do not apply.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        override_instance = ContractServicePrimary(marker="broadcast")
        instance = borrower.meld(
            spell=consumer_id,
            spell_override={"**service": override_instance},
        )
        assert instance.service is override_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_unique_override_replaces_dependency() -> None:
    """
    Purpose:
        Validate UNIQUE overrides replace SpellContract dependencies.
    Contract:
        - Unique overrides replace the contracted provider instance.
    Returns:
        None.
    Raises:
        AssertionError: If unique overrides do not replace the dependency.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.unique,
        permissions="create",
    )
    override_instance = ContractServicePrimary(marker="override")
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(
            spell=consumer_id,
            spell_override={"*service": override_instance},
        )
        assert instance.service is override_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_path_override_beats_contract_override() -> None:
    """
    Purpose:
        Validate PATH overrides beat SpellContract override payloads.
    Contract:
        - PATH overrides replace the contracted provider instance.
    Returns:
        None.
    Raises:
        AssertionError: If PATH overrides do not win.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerOverrideList,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        override_instance = ContractServicePrimary(marker="meld")
        instance = borrower.meld(
            spell=consumer_id,
            spell_override={"service": override_instance},
        )
        assert instance.service is override_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_multiple_contract_overrides_on_many_allowed() -> None:
    """
    Purpose:
        Validate SpellContract overrides apply for Existence.many providers.
    Contract:
        - Multiple contract overrides apply to per-path provider instances.
    Returns:
        None.
    Raises:
        AssertionError: If overrides are not applied to per-path instances.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.many,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerDualOverride,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell=consumer_id)
        assert instance.left.marker == "override-left"
        assert instance.right.marker == "override-right"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_override_list_contracted() -> None:
    """
    Purpose:
        Validate list overrides apply to contracted SpellContract providers.
    Contract:
        - Contracted providers receive list override payloads.
    Returns:
        None.
    Raises:
        AssertionError: If list overrides do not apply.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerOverrideList,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell=consumer_id)
        assert instance.service.marker == "override-list"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_override_tuple_contracted() -> None:
    """
    Purpose:
        Validate tuple overrides apply to contracted SpellContract providers.
    Contract:
        - Contracted providers receive tuple override payloads.
    Returns:
        None.
    Raises:
        AssertionError: If tuple overrides do not apply.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerOverrideTuple,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell=consumer_id)
        assert instance.service.marker == "override-tuple"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_override_dict_args_contracted() -> None:
    """
    Purpose:
        Validate dict __args__ overrides apply to contracted providers.
    Contract:
        - Contracted providers receive __args__ override payloads.
    Returns:
        None.
    Raises:
        AssertionError: If __args__ overrides do not apply.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()
    consumer_id = borrower_book.bind(
        spell=ContractConsumerOverrideArgsDict,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell=consumer_id)
        assert instance.service.marker == "override-dict-args"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_spell_contract_broadcast_override_targets_dual_dependencies() -> None:
    """
    Purpose:
        Validate BROADCAST overrides apply to multiple SpellContract sockets.
    Contract:
        - Broadcast overrides apply to each contract socket with the same name.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast overrides do not apply to all sockets.
    """
    owner_book = _make_spellbook()
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.many,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = _make_spellbook()

    class ContractConsumerNested:
        """
        Purpose:
            Provide a consumer with multiple SpellContract "service" sockets.
        Contract:
            - Declares a SpellContract service socket.
            - Declares a child dependency that also declares a service contract.
        """
        def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
            child: ContractConsumerPrimary = None,
        ) -> None:
            """
            Purpose:
                Capture the resolved contract services.
            Contract:
                Stores the service and child for assertions.
            Args:
                service: Resolved service instance.
                child: Child dependency with its own contract socket.
            Returns:
                None.
            """
            self.service = service
            self.child = child

    borrower_book.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = borrower_book.bind(
        spell=ContractConsumerNested,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        override_instance = ContractServicePrimary(marker="broadcast")
        instance = borrower.meld(
            spell=consumer_id,
            spell_override={"**service": override_instance},
        )
        assert instance.service is override_instance
        assert instance.child.service is override_instance
    finally:
        borrower.cleanup()
        owner.cleanup()
