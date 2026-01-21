"""
Contract-specific test classes for SpellContract resolution scenarios.
"""
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import IService


class ContractServicePrimary:
    """
    Purpose:
        Provide a primary contract service implementation.
    Contract:
        - Stores a marker value for assertions.
    """
    def __init__(self, marker: str = "contract-primary") -> None:
        """
        Purpose:
            Initialize the primary service marker.
        Contract:
            Stores the marker on the instance.
        Args:
            marker: Identifier used in assertions.
        Returns:
            None.
        """
        self.marker = marker


class ContractServiceSecondary:
    """
    Purpose:
        Provide a secondary contract service implementation.
    Contract:
        - Stores a marker value for assertions.
    """
    def __init__(self, marker: str = "contract-secondary") -> None:
        """
        Purpose:
            Initialize the secondary service marker.
        Contract:
            Stores the marker on the instance.
        Args:
            marker: Identifier used in assertions.
        Returns:
            None.
        """
        self.marker = marker


class ContractServiceRemote:
    """
    Purpose:
        Provide a remote contract service implementation for link tests.
    Contract:
        - Stores a marker value for assertions.
    """
    def __init__(self, marker: str = "remote") -> None:
        """
        Purpose:
            Initialize the remote service marker.
        Contract:
            Stores the marker on the instance.
        Args:
            marker: Identifier used in assertions.
        Returns:
            None.
        """
        self.marker = marker


class ContractServiceLocal:
    """
    Purpose:
        Provide a local fallback service implementation for contract tests.
    Contract:
        - Stores a marker value for assertions.
    """
    def __init__(self, marker: str = "local") -> None:
        """
        Purpose:
            Initialize the local service marker.
        Contract:
            Stores the marker on the instance.
        Args:
            marker: Identifier used in assertions.
        Returns:
            None.
        """
        self.marker = marker


class ContractConfigPrimary:
    """
    Purpose:
        Provide a contract configuration implementation.
    Contract:
        - Stores a label value for assertions.
    """
    def __init__(self, label: str = "contract-config") -> None:
        """
        Purpose:
            Initialize the config label.
        Contract:
            Stores the label on the instance.
        Args:
            label: Identifier used in assertions.
        Returns:
            None.
        """
        self.label = label


class ContractConsumerPrimary:
    """
    Purpose:
        Provide a consumer that declares a primary SpellContract dependency.
    Contract:
        - Stores the resolved service instance.
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


class ContractConsumerSecondary:
    """
    Purpose:
        Provide a consumer that declares a secondary SpellContract dependency.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: IService = SpellContract(
            spellframe=IService,
            binding_name="secondary",
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


class ContractConsumerDual:
    """
    Purpose:
        Provide a consumer with two SpellContract service dependencies.
    Contract:
        - Stores both resolved services for assertions.
    """
    def __init__(
        self,
        left: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
        ),
        right: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
        ),
    ) -> None:
        """
        Purpose:
            Capture the resolved service dependencies.
        Contract:
            Stores both services on the consumer.
        Args:
            left: Resolved left service instance.
            right: Resolved right service instance.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class ContractConsumerDualOverride:
    """
    Purpose:
        Provide a consumer with two SpellContract overrides for the same service.
    Contract:
        - Stores both resolved services for assertions.
    """
    def __init__(
        self,
        left: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
            spell_override={"marker": "override-left"},
        ),
        right: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
            spell_override={"marker": "override-right"},
        ),
    ) -> None:
        """
        Purpose:
            Capture the resolved services with override payloads.
        Contract:
            Stores both services on the consumer.
        Args:
            left: Resolved left service instance.
            right: Resolved right service instance.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class ContractConsumerOverrideList:
    """
    Purpose:
        Provide a consumer with a list-style SpellContract override payload.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
            spell_override=["override-list"],
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


class ContractConsumerOverrideTuple:
    """
    Purpose:
        Provide a consumer with a tuple-style SpellContract override payload.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
            spell_override=("override-tuple",),
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


class ContractConsumerOverrideArgsDict:
    """
    Purpose:
        Provide a consumer with a dict override payload using __args__.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: IService = SpellContract(
            spellframe=IService,
            binding_name="primary",
            spell_override={"__args__": ["override-dict-args"]},
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


class ContractConsumerExplicitSpell:
    """
    Purpose:
        Provide a consumer that declares a SpellContract via explicit spell.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: ContractServicePrimary = SpellContract(
            spell=ContractServicePrimary,
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


class ContractConsumerExplicitSpellUpper:
    """
    Purpose:
        Provide a consumer with explicit spell and mixed-case binding name.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: ContractServicePrimary = SpellContract(
            spell=ContractServicePrimary,
            binding_name="Primary",
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


class ContractConsumerStringFrame:
    """
    Purpose:
        Provide a consumer that uses a string spellframe contract.
    Contract:
        - Stores the resolved service instance.
    """
    def __init__(
        self,
        service: IService = SpellContract(
            spellframe="service_frame",
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


class ContractConsumerConfigPrimary:
    """
    Purpose:
        Provide a consumer that declares a config SpellContract dependency.
    Contract:
        - Stores the resolved config instance.
    """
    def __init__(
        self,
        config: IConfig = SpellContract(
            spellframe=IConfig,
            binding_name="primary",
        ),
    ) -> None:
        """
        Purpose:
            Capture the resolved config dependency.
        Contract:
            Stores the config instance on the consumer.
        Args:
            config: Resolved config instance.
        Returns:
            None.
        """
        self.config = config
