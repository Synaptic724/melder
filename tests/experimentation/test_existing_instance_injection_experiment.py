"""Characterize existing-object injection before selecting a production repair.

Known lookup/planning failures are printed as observations. Corrected-contract
regressions live in the integration tier and remain red until a repair lands.
"""

import json
from typing import Union

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    CollectionValueConsumer,
    ExistingValue,
    MappedValueConsumer,
    NestedValueConsumer,
    ValueConsumer,
    instance_book as instance_book,
)


class CallableFactory:
    """Characterize the current public callable-binding path separately from existing values."""

    def __init__(self) -> None:
        """Own one resource-free product and count actual factory calls."""
        self.product = ExistingValue("factory-product")
        self.calls = 0

    def __call__(self) -> ExistingValue:
        """Return the product and record execution, which must occur only during meld."""
        self.calls += 1
        return self.product


class FactoryConsumer:
    """Request a callable factory result through the existing explicit SpellMap contract."""

    def __init__(
            self,
            value: Union[ExistingValue, SpellMap] = SpellMap(
                spellframe="callable-providers", binding_name="factory",
            ),
    ) -> None:
        """Retain the factory-produced object for identity checks."""
        self.value = value


@pytest.mark.parametrize("mode", (
    "root", "root_typed", "root_named", "direct_unqualified", "direct_typed",
    "nested_typed", "collection_typed", "explicit_map", "late_bound_typed",
))
def test_characterize_existing_instance_injection(instance_book: Spellbook, mode: str) -> None:
    """Compare lookup metadata, real dependency planning and post-conjure binding.

    This is an observation test, not acceptance of the known failure. Successful
    outcomes must preserve object identity; only the two established failure
    categories are captured. Other exceptions still fail the experiment.
    """
    supplied = ExistingValue("supplied-before-bind")
    named = mode in ("root_named", "explicit_map")
    typed = mode.endswith("typed")
    spell_id = instance_book.bind(
        spell=supplied, existence="unique",
        spellframe="named-values" if named else ExistingValue if typed else None,
        binding_name="chosen" if named else None,
    )
    spell = instance_book._spell_id_pool[spell_id]
    assert spell.is_existing_creation
    assert not spell.profile.resolution_profile.requirements.parameters
    report: dict[str, object] = {"mode": mode, "existing_creation": True, "constructor_requirements": 0}
    stage = "conjure"
    try:
        root = instance_book.conjure(dynamic=True) if mode == "late_bound_typed" else None
        target_id = spell_id
        if not mode.startswith("root"):
            stage = "bind_consumer"
            consumer_type = ValueConsumer
            if mode == "nested_typed":
                instance_book.bind(spell=ValueConsumer, existence="many")
                consumer_type = NestedValueConsumer
            elif mode == "collection_typed":
                consumer_type = CollectionValueConsumer
            elif mode == "explicit_map":
                consumer_type = MappedValueConsumer
            target_id = instance_book.bind(spell=consumer_type, existence="many")
        stage = "conjure"
        if root is None:
            root = instance_book.conjure(dynamic=True)
        stage = "meld"
        result = root.meld(spell_id=target_id)
        if mode == "nested_typed":
            received = result.child.value
        elif mode == "collection_typed":
            assert len(result.values) == 1
            received = result.values[0]
        elif mode.startswith("root"):
            received = result
        else:
            received = result.value
        assert received is supplied
        report.update(outcome="same_instance", stage=stage)
    except (RuntimeError, TypeError) as error:
        message = str(error)
        if "not a callable object" in message:
            failure = "existing_instance_signature_inspection"
        elif "no DI candidate found" in message:
            failure = "no_matching_type_frame"
        else:
            raise
        report.update(outcome=failure, stage=stage, error_type=type(error).__name__)
    print(json.dumps(report, sort_keys=True))


@pytest.mark.parametrize("inject", (False, True), ids=("root", "explicit_map_injection"))
def test_characterize_callable_object_factory_binding(instance_book: Spellbook, inject: bool) -> None:
    """Prove callable binding currently produces a factory, preserving its normal behavior."""
    factory = CallableFactory()
    factory_id = instance_book.bind(
        spell=factory, existence="unique", spellframe="callable-providers", binding_name="factory",
    )
    spell = instance_book._spell_id_pool[factory_id]
    assert not spell.is_existing_creation
    target_id = instance_book.bind(spell=FactoryConsumer, existence="many") if inject else factory_id
    root = instance_book.conjure(dynamic=True)
    assert factory.calls == 0
    result = root.meld(spell_id=target_id)
    received = result.value if inject else result
    assert received is factory.product
    assert received is not factory
    assert factory.calls == 1
    print(json.dumps({
        "mode": "callable_map_injection" if inject else "callable_root",
        "existing_creation": False, "factory_calls": factory.calls, "outcome": "factory_product",
    }, sort_keys=True))
