from __future__ import annotations

from typing import Iterable

from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.strategies.contract_provider_presence_strategy import (
    ContractProviderPresenceStrategy,
)


class _ParamStub:
    """
    Purpose:
        Minimal parameter requirement stub for contract validation tests.
    Contract:
        Exposes name, di_shape, and default_value attributes.
    """

    def __init__(self, *, name: str, di_shape: ParameterDIShape, default_value: object) -> None:
        """
        Purpose:
            Initialize the parameter stub with DI metadata.
        Contract:
            Stores provided attributes without mutation.
        Args:
            name: Parameter name string.
            di_shape: Parameter DI shape.
            default_value: Default value representing the contract.
        Returns:
            None.
        """
        self.name = name
        self.di_shape = di_shape
        self.default_value = default_value


class _RequirementsStub:
    """
    Purpose:
        Provide a requirements stub with parameter list access.
    Contract:
        Returns parameters in the order provided.
    """

    def __init__(self, parameters: list[_ParamStub]) -> None:
        """
        Purpose:
            Initialize the requirements stub.
        Contract:
            Stores the provided parameter list.
        Args:
            parameters: List of parameter stubs.
        Returns:
            None.
        """
        self._parameters = list(parameters)

    @property
    def parameters(self) -> tuple[_ParamStub, ...]:
        """
        Purpose:
            Expose parameters as a stable tuple.
        Contract:
            Returns parameters in insertion order.
        Returns:
            tuple[_ParamStub, ...]: The stored parameters.
        """
        return tuple(self._parameters)


class _SpellIndexStub:
    """
    Purpose:
        Provide a spell index stub with a current id.
    Contract:
        Exposes current without validation.
    """

    def __init__(self, current: str) -> None:
        """
        Purpose:
            Initialize the index stub with a current id.
        Contract:
            Stores the provided id as current.
        Args:
            current: Spell id string.
        Returns:
            None.
        """
        self.current = current


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for contract validation.
    Contract:
        Exposes spell_name and spell_index.current.
    """

    def __init__(self, *, spell_id: str = "spell-id", spell_name: str = "spell-name") -> None:
        """
        Purpose:
            Initialize the spell stub with identifiers.
        Contract:
            Stores spell_name and spell_index.current.
        Args:
            spell_id: Spell id assigned to spell_index.current.
            spell_name: Spell name for diagnostics.
        Returns:
            None.
        """
        self.spell_name = spell_name
        self.spell_index = _SpellIndexStub(spell_id)


class _ProviderSpellStub:
    """
    Purpose:
        Provide a minimal provider spell for scanner iteration.
    Contract:
        Exposes spellframe, spell_name, and binding_name attributes.
    """

    def __init__(
        self,
        *,
        spellframe: object,
        spell_name: str,
        binding_name: str | None,
    ) -> None:
        """
        Purpose:
            Initialize the provider spell stub.
        Contract:
            Stores identifiers for contract key normalization.
        Args:
            spellframe: Frame/interface used for provider lookup.
            spell_name: Provider spell name.
            binding_name: Optional binding name.
        Returns:
            None.
        """
        self.spellframe = spellframe
        self.spell_name = spell_name
        self.binding_name = binding_name


class _ScannerStub:
    """
    Purpose:
        Provide a scanner stub yielding spell/index pairs.
    Contract:
        Iteration order matches the provided spell list.
    """

    def __init__(self, spells: list[tuple[_SpellIndexStub, _ProviderSpellStub]]) -> None:
        """
        Purpose:
            Initialize the scanner stub with spell/index pairs.
        Contract:
            Stores the provided pairs in order.
        Args:
            spells: List of (index, spell) tuples to yield.
        Returns:
            None.
        """
        self._spells = list(spells)

    def iter_spells(self) -> Iterable[tuple[_SpellIndexStub, _ProviderSpellStub]]:
        """
        Purpose:
            Yield stored spell/index pairs.
        Contract:
            Each yielded tuple matches the stored list.
        Returns:
            Iterable[tuple[_SpellIndexStub, _ProviderSpellStub]]: Spell/index pairs.
        """
        for pair in self._spells:
            yield pair


class _ConfigStub:
    """
    Purpose:
        Provide a configuration stub exposing system_state.
    Contract:
        Returns the stored SystemState for lookup.
    """

    def __init__(self, system_state: SystemState | None) -> None:
        """
        Purpose:
            Initialize the configuration stub with a SystemState.
        Contract:
            Stores the provided system_state.
        Args:
            system_state: SystemState value or None.
        Returns:
            None.
        """
        self._system_state = system_state

    def has_property(self, name: str) -> bool:
        """
        Purpose:
            Indicate whether the configuration exposes the requested property.
        Contract:
            Returns True only for "system_state".
        Args:
            name: Property name string.
        Returns:
            bool: True when the property is available.
        """
        return name == "system_state"

    def get_property(self, name: str) -> SystemState | None:
        """
        Purpose:
            Return the stored system_state when requested.
        Contract:
            Returns the stored value for "system_state", None otherwise.
        Args:
            name: Property name string.
        Returns:
            SystemState | None: Stored system state.
        """
        if name != "system_state":
            return None
        return self._system_state


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub that returns configuration.
    Contract:
        get_configuration returns the configured config object.
    """

    def __init__(self, config: _ConfigStub | None) -> None:
        """
        Purpose:
            Initialize the spellbook stub with a config.
        Contract:
            Stores the provided config for retrieval.
        Args:
            config: Configuration stub or None.
        Returns:
            None.
        """
        self._config = config

    def get_configuration(self) -> _ConfigStub | None:
        """
        Purpose:
            Return the stored configuration stub.
        Contract:
            Returns the configuration passed at construction.
        Returns:
            _ConfigStub | None: Stored configuration.
        """
        return self._config


def _make_context(
    *,
    requirements: _RequirementsStub,
    scanner: _ScannerStub | None,
    system_state: SystemState | None,
) -> tuple[SpellValidationContext, list]:
    """
    Purpose:
        Build a SpellValidationContext for contract provider tests.
    Contract:
        Returns the context and the shared issues list.
    Args:
        requirements: Requirements stub for the spell.
        scanner: Scanner stub or None.
        system_state: SystemState to expose via spellbook config.
    Returns:
        tuple[SpellValidationContext, list]: Context and issues list.
    """
    issues: list = []
    spellbook = None
    if system_state is not None:
        spellbook = _SpellbookStub(_ConfigStub(system_state))
    context = SpellValidationContext(
        spell=_SpellStub(),
        spellbook=spellbook,
        requirements=requirements,
        symbolic_graph=None,
        resolution_frame=None,
        scanner=scanner,
        cancel_event=None,
        issues=issues,
    )
    return context, issues


def test_contract_provider_presence_missing_spell_contract_warns() -> None:
    """
    Purpose:
        Verify missing SpellContract providers emit warnings in dynamic mode.
    Contract:
        Emits SPELL_CONTRACT_MISSING_PROVIDER with warning severity.
    Returns:
        None.
    Raises:
        AssertionError: If the warning is missing.
    """
    class IService:
        """
        Purpose:
            Dummy interface for contract key generation.
        Contract:
            Acts as a stable spellframe identifier.
        """

    contract = SpellContract(spellframe=IService, binding_name="primary")
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="service",
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=contract,
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        scanner=_ScannerStub([]),
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].code == "SPELL_CONTRACT_MISSING_PROVIDER"


def test_contract_provider_presence_automatic_mode_warns() -> None:
    """
    Purpose:
        Verify contract sockets emit warnings in automatic system state.
    Contract:
        Emits CONTRACT_IN_AUTOMATIC_MODE warning.
    Returns:
        None.
    Raises:
        AssertionError: If the warning is missing.
    """
    class IService:
        """
        Purpose:
            Dummy interface for contract key generation.
        Contract:
            Acts as a stable spellframe identifier.
        """

    contract = SpellContract(spellframe=IService, binding_name="primary")
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="service",
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=contract,
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        scanner=_ScannerStub([]),
        system_state=SystemState.automatic,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].code == "CONTRACT_IN_AUTOMATIC_MODE"


def test_contract_provider_presence_ambiguous_spell_contract_errors() -> None:
    """
    Purpose:
        Verify ambiguous SpellContract providers emit errors.
    Contract:
        Emits SPELL_CONTRACT_AMBIGUOUS when multiple providers match.
    Returns:
        None.
    Raises:
        AssertionError: If the error is missing.
    """
    class IService:
        """
        Purpose:
            Dummy interface for contract key generation.
        Contract:
            Acts as a stable spellframe identifier.
        """

    contract = SpellContract(spellframe=IService, binding_name="primary")
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="service",
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=contract,
            )
        ]
    )
    scanner = _ScannerStub(
        [
            (_SpellIndexStub("prov-a"), _ProviderSpellStub(spellframe=IService, spell_name="A", binding_name="primary")),
            (_SpellIndexStub("prov-b"), _ProviderSpellStub(spellframe=IService, spell_name="B", binding_name="primary")),
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        scanner=scanner,
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].code == "SPELL_CONTRACT_AMBIGUOUS"
    assert len(issues[0].details.get("provider_spell_ids", [])) == 2


def test_contract_provider_presence_missing_mutation_early_errors() -> None:
    """
    Purpose:
        Verify early-bound MutationContract missing providers emits errors.
    Contract:
        Emits MUTATION_CONTRACT_MISSING_PROVIDER_EARLY.
    Returns:
        None.
    Raises:
        AssertionError: If the error is missing.
    """
    class IService:
        """
        Purpose:
            Dummy interface for mutation key generation.
        Contract:
            Acts as a stable spellframe identifier.
        """

    contract = MutationContract(spellframe=IService, binding_name="primary", late_binding=False)
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="mutation",
                di_shape=ParameterDIShape.MUTATION_CONTRACT,
                default_value=contract,
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        scanner=_ScannerStub([]),
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].code == "MUTATION_CONTRACT_MISSING_PROVIDER_EARLY"


def test_contract_provider_presence_missing_mutation_late_warns() -> None:
    """
    Purpose:
        Verify late-bound MutationContract missing providers emits warnings.
    Contract:
        Emits MUTATION_CONTRACT_MISSING_PROVIDER with warning severity.
    Returns:
        None.
    Raises:
        AssertionError: If the warning is missing.
    """
    class IService:
        """
        Purpose:
            Dummy interface for mutation key generation.
        Contract:
            Acts as a stable spellframe identifier.
        """

    contract = MutationContract(spellframe=IService, binding_name="primary", late_binding=True)
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="mutation",
                di_shape=ParameterDIShape.MUTATION_CONTRACT,
                default_value=contract,
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        scanner=_ScannerStub([]),
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].code == "MUTATION_CONTRACT_MISSING_PROVIDER"
