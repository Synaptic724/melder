from types import SimpleNamespace
from unittest.mock import patch

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.spellbook.bind.spell_index import SpellIndex
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


def test_resolve_spell_contract_missing_contracted_map_raises() -> None:
    """
    Purpose:
        Validate missing contracted spell maps raise MeldExecutionError.
    Contract:
        - Contract lookup without contracted spell maps raises an error.
    Returns:
        None.
    Raises:
        AssertionError: If missing contracted maps do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_index = SpellIndex("provider")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={"peer": {contract_key: provider_index}},
        _contracted_spells=None,
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="Contracted spell map missing"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_missing_conduit_map_raises() -> None:
    """
    Purpose:
        Validate missing conduit contract maps raise MeldExecutionError.
    Contract:
        - Missing per-conduit map for a contract raises an error.
    Returns:
        None.
    Raises:
        AssertionError: If missing conduit maps do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_index = SpellIndex("provider")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={"peer": {contract_key: provider_index}},
        _contracted_spells={},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="Contracted spell map missing for conduit"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_missing_index_raises() -> None:
    """
    Purpose:
        Validate missing contracted spell indices raise MeldExecutionError.
    Contract:
        - Missing spell index in contracted map raises an error.
    Returns:
        None.
    Raises:
        AssertionError: If missing spell indices do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_index = SpellIndex("provider")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={"peer": {contract_key: provider_index}},
        _contracted_spells={"peer": {}},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="Contracted spell index missing"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_multiple_contracted_candidates_raises() -> None:
    """
    Purpose:
        Validate ambiguous contracted providers raise MeldExecutionError.
    Contract:
        - Multiple contracted candidates raise a disambiguation error.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguous contracted providers do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_a = SimpleNamespace(spell_index=SpellIndex("provider-a"))
    provider_b = SimpleNamespace(spell_index=SpellIndex("provider-b"))
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={
            "peer-a": {contract_key: provider_a.spell_index},
            "peer-b": {contract_key: provider_b.spell_index},
        },
        _contracted_spells={
            "peer-a": {provider_a.spell_index: provider_a},
            "peer-b": {provider_b.spell_index: provider_b},
        },
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="multiple contracted spells"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_prefers_contracted_over_local() -> None:
    """
    Purpose:
        Validate contracted providers take precedence over local providers.
    Contract:
        - Contracted candidates are preferred when present.
    Returns:
        None.
    Raises:
        AssertionError: If local providers are chosen over contracted ones.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    contracted = SimpleNamespace(spell_index=SpellIndex("contracted"))
    local = SimpleNamespace(spell_index=SpellIndex("local"))
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={"peer": {contract_key: contracted.spell_index}},
        _contracted_spells={"peer": {contracted.spell_index: contracted}},
        _lookup_spells={contract_key: local.spell_index},
        _spells={local.spell_index: local},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    resolved = engine._resolve_spell_contract_spell_id(
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
    )
    assert resolved == contracted.spell_index.current


def test_resolve_spell_contract_local_map_missing_raises() -> None:
    """
    Purpose:
        Validate missing local spell maps raise MeldExecutionError.
    Contract:
        - Local lookup without spell maps raises an error.
    Returns:
        None.
    Raises:
        AssertionError: If missing local maps do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_index = SpellIndex("provider")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={},
        _contracted_spells={},
        _lookup_spells={contract_key: provider_index},
        _spells=None,
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    with pytest.raises(MeldExecutionError, match="Local spell map missing"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_fallback_multiple_candidates_raises() -> None:
    """
    Purpose:
        Validate fallback resolution rejects multiple local candidates.
    Contract:
        - Multiple fallback candidates raise a disambiguation error.
    Returns:
        None.
    Raises:
        AssertionError: If multiple fallback candidates do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider_a = SimpleNamespace(spell_index=SpellIndex("provider-a"), key=contract_key)
    provider_b = SimpleNamespace(spell_index=SpellIndex("provider-b"), key=contract_key)
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={},
        _contracted_spells={},
        _lookup_spells={},
        _spells={},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    engine._spell_lookup = {
        provider_a.spell_index.current: provider_a,
        provider_b.spell_index.current: provider_b,
    }
    with pytest.raises(MeldExecutionError, match="multiple local spells"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_resolve_spell_contract_fallback_single_candidate_returns() -> None:
    """
    Purpose:
        Validate fallback resolution returns a single local candidate.
    Contract:
        - Single fallback candidate resolves to its spell id.
    Returns:
        None.
    Raises:
        AssertionError: If fallback candidate does not resolve.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    contract_key = contract.canonical_key
    provider = SimpleNamespace(spell_index=SpellIndex("provider"), key=contract_key)
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={},
        _contracted_spells={},
        _lookup_spells={},
        _spells={},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    engine._spell_lookup = {provider.spell_index.current: provider}
    resolved = engine._resolve_spell_contract_spell_id(
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
    )
    assert resolved == provider.spell_index.current


def test_resolve_spell_contract_missing_all_candidates_raises() -> None:
    """
    Purpose:
        Validate missing providers raise MeldExecutionError.
    Contract:
        - No contracted or local spell matches raise a resolution error.
    Returns:
        None.
    Raises:
        AssertionError: If missing candidates do not raise.
    """
    contract = SpellContract(spellframe=IService, binding_name="primary")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={},
        _contracted_spells={},
        _lookup_spells={},
        _spells={},
    )
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
        _spellbook=spellbook,
    )
    engine = object.__new__(MeldEngine)
    engine._spell_lookup = {}
    with pytest.raises(MeldExecutionError, match="could not be resolved"):
        engine._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
        )


def test_record_contract_override_skips_empty_payload() -> None:
    """
    Purpose:
        Validate empty override payloads are not recorded.
    Contract:
        - Empty payloads produce no entries in override maps.
    Returns:
        None.
    Raises:
        AssertionError: If empty payloads are recorded.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {}
    engine._contract_overrides_by_spell_id = {}
    contract = SpellContract(spellframe=IService)
    contract.spell_override = {}
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    engine._record_contract_override(
        occurrence=("provider", ("service",)),
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
    )
    assert engine._contract_overrides_by_occurrence == {}
    assert engine._contract_overrides_by_spell_id == {}


def test_record_contract_override_stores_payload() -> None:
    """
    Purpose:
        Validate non-empty override payloads are recorded.
    Contract:
        - Overrides are stored by occurrence and spell id.
    Returns:
        None.
    Raises:
        AssertionError: If override payloads are not stored.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {}
    engine._contract_overrides_by_spell_id = {}
    contract = SpellContract(spellframe=IService)
    contract.spell_override = {"marker": "override"}
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    occurrence = ("provider", ("service",))
    engine._record_contract_override(
        occurrence=occurrence,
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
    )
    assert engine._contract_overrides_by_occurrence[occurrence]["marker"] == "override"
    assert engine._contract_overrides_by_spell_id["provider"]


def test_get_contract_override_payload_for_instance_uses_spell_id_fallback() -> None:
    """
    Purpose:
        Validate fallback to spell-id overrides when canonical overrides are absent.
    Contract:
        - When canonical occurrence lacks overrides, the first spell-id override is used.
    Returns:
        None.
    Raises:
        AssertionError: If spell-id fallback is not used.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {}
    engine._contract_overrides_by_spell_id = {
        "spell-1": [(("spell-1", ("path",)), {"marker": "first"})],
    }
    payload = engine._get_contract_override_payload_for_instance(
        instance_key=("spell-1", None),
        canonical_occurrences_by_spell_id={"spell-1": ("spell-1", ("canonical",))},
    )
    assert payload == {"marker": "first"}


def test_apply_spell_contract_dependencies_records_occurrence_and_override() -> None:
    """
    Purpose:
        Validate SpellContract dependencies are added and overrides recorded.
    Contract:
        - Contract socket adds a child occurrence.
        - Override payload is stored for the child occurrence.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies or overrides are not recorded.
    """
    engine = object.__new__(MeldEngine)
    engine._contract_overrides_by_occurrence = {}
    engine._contract_overrides_by_spell_id = {}
    engine._spell_lookup = {}
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    engine._spell_lookup["consumer"] = consumer_spell
    contract = SpellContract(spellframe=IService)
    contract.spell_override = {"marker": "override"}

    dependencies = {}
    with patch.object(
        MeldEngine,
        "_iter_spell_contract_defaults",
        return_value=[("service", contract)],
    ):
        with patch.object(
            MeldEngine,
            "_resolve_spell_contract_spell_id",
            return_value="provider",
        ):
            engine._apply_spell_contract_dependencies(
                dependencies=dependencies,
                occurrence=("consumer", ()),
            )

    assert dependencies["service"] == [("provider", ("service",))]
    assert ("provider", ("service",)) in engine._contract_overrides_by_occurrence
