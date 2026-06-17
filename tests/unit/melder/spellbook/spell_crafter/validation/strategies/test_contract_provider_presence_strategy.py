from typing import Dict, List, Optional, Tuple

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.contract_provider_presence_strategy import (
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
        self.selected_spell_id = current


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for contract validation.
    Contract:
        Exposes spell_name and spell_index.selected_spell_id.
    """

    def __init__(
            self,
            *,
            spell_id: str = "spell-id",
            spell_name: str = "spell-name",
            mutation_override: Optional[dict] = None,
    ) -> None:
        """
        Purpose:
            Initialize the spell stub with identifiers.
        Contract:
            Stores spell_name and spell_index.selected_spell_id.
        Args:
            spell_id: Spell id assigned to spell_index.selected_spell_id.
            spell_name: Spell name for diagnostics.
        Returns:
            None.
        """
        self.spell_name = spell_name
        self.spell_index = _SpellIndexStub(spell_id)
        self._mutation_override = (
            dict(mutation_override) if mutation_override is not None else {}
        )

    @property
    def has_mutation_override(self) -> bool:
        """
        Purpose:
            Mirror the real spell convenience flag used by the validation strategy.
        Contract:
            Returns True when the stored mutation payload is non-empty.
        Returns:
            bool: Whether a mutation binding is currently present.
        """
        return bool(self._mutation_override)


class _ProviderSpellStub:
    """
    Purpose:
        Provide a minimal provider spell for contracted provider lookup.
    Contract:
        Exposes spellframe, spell_name, and binding_name attributes.
    """

    def __init__(
        self,
        *,
        spellframe: object,
        spell_name: str,
        binding_name: Optional[str],
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


class _ConfigStub:
    """
    Purpose:
        Provide a configuration stub exposing system_state.
    Contract:
        Returns the stored SystemState for lookup.
    """

    def __init__(self, system_state: Optional[SystemState]) -> None:
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

    def get_property(self, name: str) -> Optional[SystemState]:
        """
        Purpose:
            Return the stored system_state when requested.
        Contract:
            Returns the stored value for "system_state", None otherwise.
        Args:
            name: Property name string.
        Returns:
            Optional[SystemState]: Stored system state.
        """
        if name != "system_state":
            return None
        return self._system_state


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub that returns configuration and contracted spells.
    Contract:
        get_configuration returns the configured config object.
        _contracted_spells exposes provider spell mappings.
    """

    def __init__(
        self,
        *,
        config: Optional[_ConfigStub],
        contracted_spells: Optional[List[Tuple[_SpellIndexStub, _ProviderSpellStub]]] = None,
    ) -> None:
        """
        Purpose:
            Initialize the spellbook stub with a config and contracted spells.
        Contract:
            Stores the provided config and contracted spell mappings.
        Args:
            config: Configuration stub or None.
            contracted_spells: Optional contracted provider spells.
        Returns:
            None.
        """
        self._config = config
        class _FrameConfigurationStub:
            @property
            def system_state(_self):
                if config is None:
                    return None
                return config.get_property("system_state")

        self._aetheric_frame_configuration = _FrameConfigurationStub()
        self._contracted_spells: Dict[str, Dict[_SpellIndexStub, _ProviderSpellStub]] = {}
        if contracted_spells:
            self._contracted_spells["contracted"] = {
                index: spell for index, spell in contracted_spells
            }

    def get_configuration(self) -> Optional[_ConfigStub]:
        """
        Purpose:
            Return the stored configuration stub.
        Contract:
            Returns the configuration passed at construction.
        Returns:
            Optional[_ConfigStub]: Stored configuration.
        """
        return self._config


class _RaisingConfigStub(_ConfigStub):
    def get_property(self, name: str) -> Optional[SystemState]:
        raise RuntimeError("config failed")


class _CancelAfter:
    def __init__(self, threshold: int) -> None:
        self._checks = 0
        self._threshold = threshold

    @property
    def is_set(self):
        self._checks += 1
        return self._checks > self._threshold

    def throw_if_set(self):
        raise RuntimeError("cancelled")


def _make_context(
    *,
    requirements: _RequirementsStub,
    contracted_spells: Optional[List[Tuple[_SpellIndexStub, _ProviderSpellStub]]],
    system_state: Optional[SystemState],
    mutation_override: Optional[dict] = None,
) -> tuple[SpellValidationContext, list]:
    """
    Purpose:
        Build a SpellValidationContext for contract provider tests.
    Contract:
        Returns the context and the shared issues list.
    Args:
        requirements: Requirements stub for the spell.
        contracted_spells: Contracted provider spells to expose.
        system_state: SystemState to expose via spellbook config.
    Returns:
        tuple[SpellValidationContext, list]: Context and issues list.
    """
    issues: list = []
    config = _ConfigStub(system_state) if system_state is not None else None
    spellbook = _SpellbookStub(
        config=config,
        contracted_spells=contracted_spells,
    )
    context = SpellValidationContext(
        spell=_SpellStub(mutation_override=mutation_override),
        spellbook=spellbook,
        requirements=requirements,
        symbolic_graph=None,
        resolution_frame=None,
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
        contracted_spells=[],
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].code == "SPELL_CONTRACT_MISSING_PROVIDER"


def test_contract_provider_presence_automatic_mode_errors() -> None:
    """
    Purpose:
        Verify contract sockets emit errors in automatic system state.
    Contract:
        Emits CONTRACT_IN_AUTOMATIC_MODE error.
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
    context, issues = _make_context(
        requirements=requirements,
        contracted_spells=[],
        system_state=SystemState.automatic,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "error"
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
    contracted_spells = [
        (_SpellIndexStub("prov-a"), _ProviderSpellStub(spellframe=IService, spell_name="A", binding_name="primary")),
        (_SpellIndexStub("prov-b"), _ProviderSpellStub(spellframe=IService, spell_name="B", binding_name="primary")),
    ]
    context, issues = _make_context(
        requirements=requirements,
        contracted_spells=contracted_spells,
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].code == "SPELL_CONTRACT_AMBIGUOUS"
    assert len(issues[0].details.get("provider_spell_ids", [])) == 2


def test_contract_provider_presence_honors_cancellation_before_scan() -> None:
    requirements = _RequirementsStub([])
    context, _ = _make_context(
        requirements=requirements,
        contracted_spells=[],
        system_state=None,
    )
    context.cancel_event = _CancelAfter(0)

    with pytest.raises(RuntimeError, match="cancelled"):
        ContractProviderPresenceStrategy().validate(context)


def test_contract_provider_presence_returns_when_requirements_missing() -> None:
    issues: list = []
    context = SpellValidationContext(
        spell=_SpellStub(),
        spellbook=_SpellbookStub(config=None, contracted_spells=None),
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=issues,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert issues == []


def test_contract_provider_presence_swallows_configuration_errors() -> None:
    class IService:
        pass

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
    issues: list = []
    context = SpellValidationContext(
        spell=_SpellStub(),
        spellbook=_SpellbookStub(config=_RaisingConfigStub(SystemState.dynamic), contracted_spells=None),
        requirements=requirements,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=issues,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].code == "SPELL_CONTRACT_MISSING_PROVIDER"


def test_contract_provider_presence_honors_cancellation_during_provider_scan() -> None:
    class IService:
        pass

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
    contracted_spells = [
        (_SpellIndexStub("prov-a"), _ProviderSpellStub(spellframe=IService, spell_name="A", binding_name="primary")),
    ]
    context, _ = _make_context(
        requirements=requirements,
        contracted_spells=contracted_spells,
        system_state=None,
    )
    context.cancel_event = _CancelAfter(1)

    with pytest.raises(RuntimeError, match="cancelled"):
        ContractProviderPresenceStrategy().validate(context)


def test_contract_provider_presence_skips_non_contract_parameters() -> None:
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="plain",
                di_shape=ParameterDIShape.PLAIN,
                default_value=None,
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        contracted_spells=[],
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert issues == []


def test_contract_provider_presence_invalid_spell_contract_errors() -> None:
    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="service",
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=object(),
            )
        ]
    )
    context, issues = _make_context(
        requirements=requirements,
        contracted_spells=[],
        system_state=None,
    )

    ContractProviderPresenceStrategy().validate(context)

    assert len(issues) == 1
    assert issues[0].code == "SPELL_CONTRACT_INVALID"


def test_contract_provider_presence_honors_cancellation_during_parameter_loop() -> None:
    class IService:
        pass

    requirements = _RequirementsStub(
        [
            _ParamStub(
                name="plain",
                di_shape=ParameterDIShape.PLAIN,
                default_value=None,
            ),
            _ParamStub(
                name="service",
                di_shape=ParameterDIShape.SPELL_CONTRACT,
                default_value=SpellContract(spellframe=IService, binding_name="primary"),
            ),
        ]
    )
    context, _ = _make_context(
        requirements=requirements,
        contracted_spells=[],
        system_state=None,
    )
    context.cancel_event = _CancelAfter(2)

    with pytest.raises(RuntimeError, match="cancelled"):
        ContractProviderPresenceStrategy().validate(context)
