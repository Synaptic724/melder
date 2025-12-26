from types import SimpleNamespace

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.mocks.spellbook.protocols import IService


def test_normalize_contract_override_payload_from_list() -> None:
    """
    Purpose:
        Validate list payloads normalize into __args__ overrides.
    Contract:
        - list payloads become {"__args__": list(payload)}.
    Returns:
        None.
    Raises:
        AssertionError: If list payloads are not normalized.
    """
    engine = object.__new__(MeldEngine)
    normalized = engine._normalize_contract_override_payload(
        payload=["alpha", "beta"],
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized == {"__args__": ["alpha", "beta"]}


def test_normalize_contract_override_payload_from_tuple() -> None:
    """
    Purpose:
        Validate tuple payloads normalize into __args__ overrides.
    Contract:
        - tuple payloads become {"__args__": list(payload)}.
    Returns:
        None.
    Raises:
        AssertionError: If tuple payloads are not normalized.
    """
    engine = object.__new__(MeldEngine)
    normalized = engine._normalize_contract_override_payload(
        payload=("alpha",),
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized == {"__args__": ["alpha"]}


def test_normalize_contract_override_payload_from_dict_preserves_args() -> None:
    """
    Purpose:
        Validate dict payloads preserve __args__ entries.
    Contract:
        - dict payloads are copied without mutation.
        - __args__ remains a list.
    Returns:
        None.
    Raises:
        AssertionError: If dict payloads are not preserved.
    """
    engine = object.__new__(MeldEngine)
    normalized = engine._normalize_contract_override_payload(
        payload={"marker": "alpha", "__args__": ["beta"]},
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized["marker"] == "alpha"
    assert normalized["__args__"] == ["beta"]


def test_normalize_contract_override_payload_rejects_invalid_args_type() -> None:
    """
    Purpose:
        Validate dict __args__ values must be list or tuple.
    Contract:
        - Invalid __args__ types raise MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid __args__ values do not raise.
    """
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="__args__"):
        engine._normalize_contract_override_payload(
            payload={"__args__": "bad"},
            consumer_spell_id="consumer",
            consumer_spell_name="Consumer",
            param_name="service",
        )


def test_normalize_contract_override_payload_rejects_invalid_type() -> None:
    """
    Purpose:
        Validate unsupported payload types raise errors.
    Contract:
        - Non dict/list/tuple payloads raise MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid payloads do not raise.
    """
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="spell_override must be a dict"):
        engine._normalize_contract_override_payload(
            payload={"bad"},
            consumer_spell_id="consumer",
            consumer_spell_name="Consumer",
            param_name="service",
        )


def test_iter_spell_contract_defaults_filters_non_contracts() -> None:
    """
    Purpose:
        Validate SpellContract defaults are detected while others are ignored.
    Contract:
        - Only SpellContract defaults are returned.
        - Varargs and kwargs are ignored.
    Returns:
        None.
    Raises:
        AssertionError: If non-contract defaults are returned.
    """
    class ContractHost:
        """
        Purpose:
            Provide a callable with a SpellContract default.
        Contract:
            - Declares one SpellContract parameter plus non-contract defaults.
        """
        def __init__(
            self,
            service: IService = SpellContract(spellframe=IService),
            marker: str = "marker",
            *args: object,
            **kwargs: object,
        ) -> None:
            """
            Purpose:
                Capture initializer arguments for signature inspection.
            Contract:
                Stores service and marker for completeness.
            Args:
                service: Contract service default.
                marker: Non-contract default.
                *args: Unused varargs.
                **kwargs: Unused kwargs.
            Returns:
                None.
            """
            self.service = service
            self.marker = marker

    engine = object.__new__(MeldEngine)
    spell = SimpleNamespace(spell=ContractHost)
    contracts = list(engine._iter_spell_contract_defaults(spell))
    assert len(contracts) == 1
    assert contracts[0][0] == "service"
    assert isinstance(contracts[0][1], SpellContract)


def test_get_contract_override_payload_for_occurrence() -> None:
    """
    Purpose:
        Validate contract overrides are returned for explicit occurrences.
    Contract:
        - Occurrence-scoped overrides are returned for non-shared instances.
    Returns:
        None.
    Raises:
        AssertionError: If occurrence overrides are not returned.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {
        ("spell-1", ("service",)): {"marker": "override"},
    }
    engine._contract_overrides_by_spell_id = {}
    result = engine._get_contract_override_payload_for_instance(
        instance_key=("spell-1", ("service",)),
        canonical_occurrences_by_spell_id={},
    )
    assert result == {"marker": "override"}


def test_get_contract_override_payload_for_shared_uses_canonical() -> None:
    """
    Purpose:
        Validate shared instances resolve contract overrides via canonical paths.
    Contract:
        - Shared instance overrides are looked up by canonical occurrence.
    Returns:
        None.
    Raises:
        AssertionError: If canonical overrides are not returned.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {
        ("spell-1", ("service",)): {"marker": "override"},
    }
    engine._contract_overrides_by_spell_id = {}
    result = engine._get_contract_override_payload_for_instance(
        instance_key=("spell-1", None),
        canonical_occurrences_by_spell_id={"spell-1": ("spell-1", ("service",))},
    )
    assert result == {"marker": "override"}
