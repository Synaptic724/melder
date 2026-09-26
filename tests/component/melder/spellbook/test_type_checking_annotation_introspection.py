"""
Regression contracts: Melder introspection of user code annotated with TYPE_CHECKING-only names.

Python 3.14 evaluates annotations lazily. A type imported only under `typing.TYPE_CHECKING` - the
style Melder recommends - is unbound at runtime, so every VALUE-format read of such an annotation
raises NameError. These cases pin the symptoms that read used to produce inside Melder.
"""

import re
from collections.abc import Iterator
from types import SimpleNamespace
from typing import TYPE_CHECKING, Optional
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import SpellExaminer
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.ai_native_support_tools.protocol_crafter import ProtocolCrafter
from melder.utilities.helpers.package import Package

if TYPE_CHECKING:
    from decimal import Decimal


class TcEngine:
    """Provider whose type is available at runtime."""


class TcCar:
    """Consumer whose annotations name the TYPE_CHECKING-only `Decimal`."""

    ratio: Decimal

    def __init__(self, engine: TcEngine, price: Optional[Decimal] = None) -> None:
        """Store the engine and an optional price."""
        self.engine = engine
        self.price = price

    def quote(self, markup: Decimal) -> Decimal:
        """Return the markup unchanged."""
        return markup

    @property
    def list_price(self) -> Decimal:
        """Return the stored price."""
        return self.price


class TcGarage:
    """Consumer bound after conjure, depending on TcCar."""

    def __init__(self, car: TcCar) -> None:
        """Store the car."""
        self.car = car


def make_tc_car(engine: TcEngine, price: Optional[Decimal] = None) -> TcCar:
    """Factory with the same annotation pattern as TcCar."""
    return TcCar(engine, price)


_ADDRESS = re.compile(r"0x[0-9a-fA-F]+")


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """
    Purpose: Give each case an isolated Aether/Nexus world.
    Contract: Reset process roots before and after the case.
    Yields: None while the test uses the fresh world.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


def _conjured_world(frame: str, *, dynamic: bool) -> tuple[Spellbook, Conduit, str]:
    """
    Purpose: Bind TcEngine and TcCar, conjure, and return the book, conduit and TcCar spell id.
    Contract: Conjure releases the Phase-1 requirements of every spell.
    """
    book = Spellbook(aetheric_frame=frame)
    book.bind(spell=TcEngine, existence=Existence.unique, permissions="create")
    car_id = book.bind(spell=TcCar, existence=Existence.many, permissions="create")
    conduit = book.conjure(name=frame, dynamic=dynamic)
    return book, conduit, car_id


def test_late_bind_over_type_checking_annotated_provider_melds_in_dynamic_world() -> None:
    """
    Purpose: Regression for PhaseExecutionError(NameError) in phase occurrence_plan_local.
    Contract: A consumer bound after conjure over a provider whose annotations name a
        TYPE_CHECKING-only type resolves on the root and on a lesser scope.
    """
    book, conduit, _car_id = _conjured_world("tc-late-bind", dynamic=True)
    assert isinstance(conduit.meld(spell=TcCar), TcCar)

    book.bind(spell=TcGarage, existence=Existence.many, permissions="create")

    garage = conduit.meld(spell=TcGarage)
    assert isinstance(garage, TcGarage)
    assert isinstance(garage.car, TcCar)
    assert isinstance(conduit.create_lesser_conduit().meld(spell=TcGarage), TcGarage)


def test_occurrence_contract_fallbacks_read_defaults_through_type_checking_annotations() -> None:
    """
    Purpose: Regression for NameError in both `_iter_spell_contract_defaults` fallbacks.
    Contract: With requirements released, SpellContract defaults are still discovered.
    """
    contract = SpellContract(spellframe="TcFrame", binding_name="primary")

    def consumer(dep: TcEngine = contract, price: Optional[Decimal] = None) -> None:
        """Declare one SpellContract default beside a TYPE_CHECKING-only annotation."""
        return None

    spell = SimpleNamespace(
        is_existing_creation=False,
        _compiler_artifact=SimpleNamespace(_requirements=None),
        spell=consumer,
    )

    assert list(SpellOccurrenceGraphAnalyzerStrategy._iter_spell_contract_defaults(spell)) == [("dep", contract)]
    assert list(SpellOccurrenceContractProcessorStrategy._iter_spell_contract_defaults(spell)) == [("dep", contract)]


def test_conduit_ward_contract_keys_read_through_type_checking_annotations() -> None:
    """
    Purpose: Regression for NameError in ConduitWard._get_spell_contract_keys.
    Contract: SpellContract defaults are collected; the annotation is never evaluated.
    """
    _book, conduit, _car_id = _conjured_world("tc-ward", dynamic=True)
    contract = SpellContract(spellframe="TcFrame", binding_name="primary")

    def consumer(dep: TcEngine = contract, price: Optional[Decimal] = None) -> None:
        """Declare one SpellContract default beside a TYPE_CHECKING-only annotation."""
        return None

    spell = MagicMock(spec=Spell)
    spell.spell = consumer

    assert conduit._conduit_ward._get_spell_contract_keys(spell) == {contract.canonical_key}


def test_bind_fingerprint_text_is_address_free_for_type_checking_annotations() -> None:
    """
    Purpose: Regression for class spell ids changing between processes.
    Contract: The fingerprinted init_signature renders the unavailable name as source text and
        contains no ForwardRef owner or memory address; the cached signature object keeps
        its ForwardRef for the requirements finder.
    """
    book, _conduit, car_id = _conjured_world("tc-fingerprint", dynamic=False)
    binding_profile = book.find_spell_by_id(car_id).profile.binding_profile

    assert binding_profile.init_signature.endswith(", price: 'Optional[Decimal]' = None) -> None")
    assert "owner=" not in binding_profile.init_signature
    assert _ADDRESS.search(binding_profile.init_signature) is None
    assert "ForwardRef" in repr(binding_profile.init_signature_object.parameters["price"].annotation)


def test_package_describe_renders_type_checking_annotation() -> None:
    """
    Purpose: Regression for NameError in Package.describe and Package.signature.
    Contract: The unavailable name renders as its source text.
    """
    package = Package(make_tc_car)

    assert package.describe().endswith("price: 'Optional[Decimal]' = None) -> " + repr(TcCar)[8:-2])
    assert package.signature.arguments == {}


def test_protocol_crafter_mirrors_class_with_type_checking_annotations() -> None:
    """
    Purpose: Regression for NameError in ProtocolCrafter on user classes.
    Contract: Unavailable names render quoted, like other class names.
    """
    code = ProtocolCrafter().craft_protocol_code(TcCar)

    assert '    ratio: "Decimal"' in code
    assert '    list_price: "Decimal"' in code
    assert '    def quote(self, markup: "Decimal") -> "Decimal":' in code


def test_protocol_crafter_mirrors_melder_conduit() -> None:
    """
    Purpose: Regression for ProtocolCrafter failing on Melder's own Conduit.
    Contract: Every Conduit annotation can be read, so the protocol is generated.
    """
    assert "class IConduit(Protocol):" in ProtocolCrafter().craft_protocol_code(Conduit)


def test_detailed_profile_of_spell_with_type_checking_annotations() -> None:
    """
    Purpose: Regression for NameError in ClassInspector/MethodInspector via the detailed profile.
    Contract: Profile completion succeeds; unavailable names appear as source text.
    """
    book, _conduit, car_id = _conjured_world("tc-detailed", dynamic=False)

    profile = SpellExaminer().create_profile(book.find_spell_by_id(car_id), "detailed")

    assert profile.class_profile.annotations == {"ratio": "Decimal"}
    quote = profile.class_profile.members["quote"]
    assert quote["signature"] == "(self, markup: 'Decimal') -> 'Decimal'"
    assert _ADDRESS.search(profile.callable_profile.signature) is None
