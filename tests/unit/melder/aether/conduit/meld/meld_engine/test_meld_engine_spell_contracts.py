from types import SimpleNamespace
from typing import Any

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def _make_builder(spellbook: Any) -> OccurrencePlanBuilder:
    builder = object.__new__(OccurrencePlanBuilder)
    builder._root_spell = SimpleNamespace(
        _spellbook=spellbook,
        spell_index=SpellIndex("root"),
        spell_name="Root",
    )
    return builder


def test_normalize_contract_override_payload_accepts_supported_types() -> None:
    payload = {"marker": "ok"}
    normalized = OccurrencePlanBuilder._normalize_contract_override_payload(
        payload=payload,
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized is payload

    normalized = OccurrencePlanBuilder._normalize_contract_override_payload(
        payload=["alpha", "beta"],
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized == {"__args__": ["alpha", "beta"]}

    normalized = OccurrencePlanBuilder._normalize_contract_override_payload(
        payload=("alpha",),
        consumer_spell_id="consumer",
        consumer_spell_name="Consumer",
        param_name="service",
    )
    assert normalized == {"__args__": ("alpha",)}


def test_normalize_contract_override_payload_rejects_invalid_type() -> None:
    with pytest.raises(MeldExecutionError, match="spell_override must be a dict"):
        OccurrencePlanBuilder._normalize_contract_override_payload(
            payload={"bad"},
            consumer_spell_id="consumer",
            consumer_spell_name="Consumer",
            param_name="service",
        )


def test_iter_spell_contract_defaults_filters_non_contracts() -> None:
    class ContractHost:
        def __init__(
            self,
            service: Any = SpellContract(spellframe="Service", binding_name="primary"),
            marker: str = "marker",
            *args: object,
            **kwargs: object,
        ) -> None:
            self.service = service
            self.marker = marker

    builder = object.__new__(OccurrencePlanBuilder)
    spell = SimpleNamespace(spell=ContractHost)
    contracts = list(builder._iter_spell_contract_defaults(spell))
    assert len(contracts) == 1
    assert contracts[0][0] == "service"
    assert isinstance(contracts[0][1], SpellContract)


def test_resolve_spell_contract_spell_id_prefers_contracted() -> None:
    contract = SpellContract(spellframe="Service", binding_name="primary")
    contract_key = contract.canonical_key
    provider_index = SpellIndex("provider")
    provider_spell = SimpleNamespace(spell_index=provider_index)
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={"peer": {contract_key: provider_index}},
        _contracted_spells={"peer": {provider_index: provider_spell}},
    )
    builder = _make_builder(spellbook)
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    resolved = builder._resolve_spell_contract_spell_id(
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
        allow_missing=False,
    )
    assert resolved == "provider"


def test_resolve_spell_contract_spell_id_missing_respects_allow_missing() -> None:
    contract = SpellContract(spellframe="Service", binding_name="primary")
    spellbook = SimpleNamespace(
        _lookup_contracted_spells={},
        _contracted_spells={},
    )
    builder = _make_builder(spellbook)
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    assert builder._resolve_spell_contract_spell_id(
        contract=contract,
        consumer_spell=consumer_spell,
        param_name="service",
        allow_missing=True,
    ) is None
    with pytest.raises(MeldExecutionError, match="SpellContract could not be resolved"):
        builder._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
            allow_missing=False,
        )


def test_resolve_spell_contract_spell_id_raises_on_multiple_candidates() -> None:
    contract = SpellContract(spellframe="Service", binding_name="primary")
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
    builder = _make_builder(spellbook)
    consumer_spell = SimpleNamespace(
        spell_index=SpellIndex("consumer"),
        spell_name="Consumer",
    )
    with pytest.raises(MeldExecutionError, match="multiple contracted spells"):
        builder._resolve_spell_contract_spell_id(
            contract=contract,
            consumer_spell=consumer_spell,
            param_name="service",
            allow_missing=False,
        )


def test_record_contract_override_stores_payload() -> None:
    overrides_by_occurrence: dict[Any, dict[str, Any]] = {}
    overrides_by_spell_id: dict[str, list[tuple[Any, dict[str, Any]]]] = {}
    occurrence = ("spell-1", ("service",))
    payload = {"marker": "override"}
    OccurrencePlanBuilder._record_contract_override(
        occurrence=occurrence,
        spell_id="spell-1",
        overrides_by_occurrence=overrides_by_occurrence,
        overrides_by_spell_id=overrides_by_spell_id,
        normalized_payload=payload,
    )
    assert overrides_by_occurrence[occurrence] == payload
    assert overrides_by_spell_id["spell-1"] == [(occurrence, payload)]
