import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.mocks.spellbook.contract_classes import ContractConfigPrimary
from tests.mocks.spellbook.contract_classes import ContractConsumerConfigPrimary
from tests.mocks.spellbook.contract_classes import ContractConsumerDual
from tests.mocks.spellbook.contract_classes import ContractConsumerExplicitSpellUpper
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideArgsDict
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideList
from tests.mocks.spellbook.contract_classes import ContractConsumerOverrideTuple
from tests.mocks.spellbook.contract_classes import ContractConsumerPrimary
from tests.mocks.spellbook.contract_classes import ContractConsumerSecondary
from tests.mocks.spellbook.contract_classes import ContractConsumerStringFrame
from tests.mocks.spellbook.contract_classes import ContractServiceLocal
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.contract_classes import ContractServiceRemote
from tests.mocks.spellbook.contract_classes import ContractServiceSecondary
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_spell_contracts() -> None:
    """
    Purpose:
        Ensure spell contract integration tests start with a clean Aether singleton.
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
        Create a dynamic configuration suitable for SpellContract tests.
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


def _inbound_spell_ids(spells_by_conduit: dict[str, list[tuple[str, object]]] | None) -> list[str]:
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


def test_spell_contract_resolves_by_explicit_spell_class_binding_normalized() -> None:
    """
    Purpose:
        Validate SpellContract resolves using explicit spell and normalized binding.
    Contract:
        - Explicit spell contracts resolve to the contracted provider.
        - Binding names are matched case-insensitively.
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not select the contracted spell.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerExplicitSpellUpper,
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

        assert isinstance(instance.service, ContractServicePrimary)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_string_frame_missing_provider_raises() -> None:
    """
    Purpose:
        Validate SpellContract raises when no contracted provider exists.
    Contract:
        - Missing contracted providers raise during meld.
    Returns:
        None.
    Raises:
        AssertionError: If missing contracts do not raise.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe="service_frame",
        binding_name="primary",
    )
    consumer_id = spellbook.bind(
        spell=ContractConsumerStringFrame,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="local")
    try:
        assert conduit.validate_contracts_and_define() == {}
        with pytest.raises(MeldExecutionError, match="SpellContract could not be resolved"):
            conduit.meld(spell=consumer_id)
    finally:
        conduit.cleanup()


def test_spell_contract_dual_occurrence_many_providers_distinct() -> None:
    """
    Purpose:
        Validate SpellContract sockets create distinct providers for Existence.many.
    Contract:
        - Each contract socket receives a distinct provider instance.
    Returns:
        None.
    Raises:
        AssertionError: If per-socket providers are not distinct.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.many,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerDual,
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

        assert isinstance(instance.left, ContractServicePrimary)
        assert isinstance(instance.right, ContractServicePrimary)
        assert instance.left is not instance.right
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_dual_occurrence_unique_providers_shared() -> None:
    """
    Purpose:
        Validate SpellContract sockets share providers for unique existences.
    Contract:
        - Unique providers are reused across contract sockets.
    Returns:
        None.
    Raises:
        AssertionError: If unique providers are not shared.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerDual,
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

        assert isinstance(instance.left, ContractServicePrimary)
        assert instance.left is instance.right
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_override_list_payload_applies() -> None:
    """
    Purpose:
        Validate list-style SpellContract overrides apply to provider construction.
    Contract:
        - The provider marker reflects the list override payload.
    Returns:
        None.
    Raises:
        AssertionError: If the override payload is not applied.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
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


def test_spell_contract_override_tuple_payload_applies() -> None:
    """
    Purpose:
        Validate tuple-style SpellContract overrides apply to provider construction.
    Contract:
        - The provider marker reflects the tuple override payload.
    Returns:
        None.
    Raises:
        AssertionError: If the override payload is not applied.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
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


def test_spell_contract_override_dict_args_payload_applies() -> None:
    """
    Purpose:
        Validate dict SpellContract overrides with __args__ apply to providers.
    Contract:
        - The provider marker reflects the __args__ override payload.
    Returns:
        None.
    Raises:
        AssertionError: If the override payload is not applied.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
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


def test_spell_contract_missing_provider_raises() -> None:
    """
    Purpose:
        Validate SpellContract raises when no provider exists.
    Contract:
        - Missing contracted and local providers raise MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If missing providers do not raise.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    consumer_id = spellbook.bind(
        spell=ContractConsumerPrimary,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        with pytest.raises(MeldExecutionError, match="SpellContract could not be resolved"):
            conduit.meld(spell=consumer_id)
    finally:
        conduit.cleanup()


def test_spell_contract_missing_dependency_does_not_gate_provider_state() -> None:
    """
    Purpose:
        Validate missing contracted dependencies do not gate provider lineage state.
    Contract:
        - Borrower meld fails when provider dependencies are not contracted.
        - Provider SpellSystemState remains valid after the failure.
    Returns:
        None.
    Raises:
        AssertionError: If provider state is gated or borrower meld does not fail.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class _ProviderDependency:
        """
        Purpose:
            Provide a dependency that is only bound in the provider spellbook.
        Contract:
            - Acts as a required constructor dependency.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the provider-only dependency.
            Contract:
                - No side effects beyond construction.
            Returns:
                None.
            """
            return None

    class _ProviderService:
        """
        Purpose:
            Provide a contracted service that depends on a local-only dependency.
        Contract:
            - Requires the provider dependency at construction time.
        """

        def __init__(self, dep: _ProviderDependency) -> None:
            """
            Purpose:
                Capture the provider-only dependency.
            Contract:
                - Stores the dependency for completeness.
            Args:
                dep: Injected provider dependency.
            Returns:
                None.
            """
            self.dep = dep

    owner_book.bind(
        spell=_ProviderDependency,
        existence=Existence.unique,
        permissions="create",
    )
    service_id = owner_book.bind(
        spell=_ProviderService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
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

        provider_state = owner_book._spell_system_states.get_by_spell_id(service_id)
        assert provider_state is not None
        assert provider_state.validity is SpellValidity.valid

        with pytest.raises(MeldExecutionError):
            borrower.meld(spell=consumer_id)

        assert provider_state.validity is SpellValidity.valid
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_runtime_error_does_not_gate_provider_state() -> None:
    """
    Purpose:
        Validate provider runtime failures do not gate lineage validity.
    Contract:
        - Borrower meld raises when provider constructor fails.
        - Provider SpellSystemState remains valid after the failure.
    Returns:
        None.
    Raises:
        AssertionError: If provider state is gated or borrower meld does not fail.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class _ProviderService:
        """
        Purpose:
            Provide a contracted service that fails at construction time.
        Contract:
            - Raises a runtime error when instantiated.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Trigger a construction-time failure.
            Contract:
                - Always raises RuntimeError.
            Raises:
                RuntimeError: Always raised to simulate a runtime failure.
            """
            raise RuntimeError("boom")

    service_id = owner_book.bind(
        spell=_ProviderService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
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

        provider_state = owner_book._spell_system_states.get_by_spell_id(service_id)
        assert provider_state is not None
        assert provider_state.validity is SpellValidity.valid

        with pytest.raises(MeldExecutionError):
            borrower.meld(spell=consumer_id)

        assert provider_state.validity is SpellValidity.valid
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_contract_removed_raises_without_provider() -> None:
    """
    Purpose:
        Validate SpellContract raises after contract removal with no provider.
    Contract:
        - Contracted providers are used when present.
        - Missing contracted providers raise after removal.
    Returns:
        None.
    Raises:
        AssertionError: If missing contracts do not raise.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServiceRemote,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    borrower_book.bind(
        spell=ContractServiceLocal,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
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

        instance = borrower.meld(spell=consumer_id)
        assert isinstance(instance.service, ContractServiceRemote)

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner) is True
        assert borrower.validate_contracts_and_define() == {}

        with pytest.raises(MeldExecutionError, match="SpellContract could not be resolved"):
            borrower.meld(spell=consumer_id)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_secondary_binding_resolves() -> None:
    """
    Purpose:
        Validate SpellContract selects providers by binding name.
    Contract:
        - Contracted providers matching the binding are selected.
    Returns:
        None.
    Raises:
        AssertionError: If the bound provider is not selected.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServiceSecondary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="secondary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerSecondary,
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
        assert isinstance(instance.service, ContractServiceSecondary)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_config_frame_resolves() -> None:
    """
    Purpose:
        Validate SpellContract resolves providers for non-service frames.
    Contract:
        - Config SpellContracts resolve contracted providers.
    Returns:
        None.
    Raises:
        AssertionError: If the config provider is not selected.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    config_id = owner_book.bind(
        spell=ContractConfigPrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=ContractConsumerConfigPrimary,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=config_id,
                conduit=owner,
                permissions="create",
            )
        assert borrower.validate_contracts_and_define()

        instance = borrower.meld(spell=consumer_id)
        assert isinstance(instance.config, ContractConfigPrimary)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spell_contract_transfer_ownership_force_unshare_allows_local() -> None:
    """
    Purpose:
        Validate SpellContract resolves locally after ownership transfer.
    Contract:
        - Ownership transfer strips contracts when force_unshare is True.
        - The consumer still resolves the provider as a local spell.
    Returns:
        None.
    Raises:
        AssertionError: If the transferred spell no longer resolves.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
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

        instance = borrower.meld(spell=consumer_id)
        assert isinstance(instance.service, ContractServicePrimary)

        owner.transfer_spell_ownership(
            spell=service_id,
            target_conduit=borrower,
            force_unshare=True,
            invalidate_after_transfer=False,
        )

        spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner.id)
        assert _inbound_spell_ids(spells_by_conduit) == []

        transferred = borrower.meld(spell=consumer_id)
        assert isinstance(transferred.service, ContractServicePrimary)
    finally:
        borrower.cleanup()
        owner.cleanup()
