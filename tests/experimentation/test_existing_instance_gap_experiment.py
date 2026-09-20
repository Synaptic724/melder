"""Observe existing-object gaps with stock planning and an isolated leaf hypothesis.

The leaf_probe fixture changes only two contract-default scanners in memory.
It never disables validation, changes production files or constitutes repair
acceptance. GAP JSON rows distinguish that diagnostic from the stock runtime.
"""

import json
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Optional, Protocol

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    CollectionValueConsumer,
    MappedValueConsumer,
    NestedValueConsumer,
    ValueConsumer,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from tests.integration.melder.spellbook.test_existing_instance_planning import (
        ExistingValue,
    )


class AlternateValue(SuppliedValue):
    """A second existing provider with a distinct spell name and shared frame."""


class DisposableValue:
    """Resource-free object exposing observable use and disposal operations."""

    def __init__(self, marker: str = "created") -> None:
        """Own a marker and disposal counter without allocating external resources."""
        self.marker = marker
        self.disposals = 0

    def dispose(self) -> None:
        """Count actual disposal invocations without relying on metadata inspection."""
        self.disposals += 1

    def read(self) -> str:
        """Return the marker so protocol satisfaction has an observable operation."""
        return self.marker


class ReadableValue(Protocol):
    """A real behavioral frame, including a method an incompatible object lacks."""

    def read(self) -> str:
        """Return the provider's diagnostic marker."""
        ...


class WrongValue:
    """Deliberately lacks the advertised concrete type and protocol operation."""


class PairConsumer:
    """Request the same existing provider through two independent parameters."""

    def __init__(self, left: SuppliedValue, right: SuppliedValue) -> None:
        """Retain both injected references to check aliasing and identity."""
        self.values = (left, right)


class NameTokenConsumer:
    """Exercise a genuine TYPE_CHECKING-only annotation instead of a runtime type."""

    def __init__(self, value: ExistingValue) -> None:
        """Retain the provider resolved from the unresolved annotation name."""
        self.value = value


class StringTokenConsumer:
    """Control for a literal forward name versus Python 3.14 deferred evaluation."""

    def __init__(self, value: "ExistingValue") -> None:
        """Deliberately keep a string annotation to compare the two supported input forms."""
        self.value = value


class DefaultConsumer:
    """Keep a selected default independent of an existing registered provider."""

    selected = SuppliedValue("selected-default")

    def __init__(self, value: SuppliedValue = selected) -> None:
        """Retain the default or explicit override exactly as supplied."""
        self.value = value


class NullableConsumer:
    """Keep a None default while an existing provider is registered."""

    def __init__(self, value: Optional[SuppliedValue] = None) -> None:
        """Retain the default without creating an inferred dependency."""
        self.value = value


class ContractConsumer:
    """Request an existing provider through a real linked contract."""

    def __init__(
            self,
            value: SuppliedValue = SpellContract(spellframe=SuppliedValue, binding_name="shared"),
    ) -> None:
        """Retain the contract-provided object for identity and post-unlink checks."""
        self.value = value


class ProtocolConsumer:
    """Use the method advertised by a protocol frame after injection."""

    def __init__(self, value: ReadableValue) -> None:
        """Retain the advertised provider; calling read tests its usable contract."""
        self.value = value


def factory_consumer(value: SuppliedValue) -> ValueConsumer:
    """Exercise a function's required existing dependency without wrapping the provider."""
    return ValueConsumer(value)


@pytest.fixture
def gap_book(instance_book: Spellbook) -> Spellbook:
    """Reuse the isolated book with its already-frozen production configuration."""
    return instance_book


@pytest.fixture(params=("stock", "leaf_probe"))
def planning_mode(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """Compare stock behavior against only the two known existing-leaf corrections.

    Class/factory inspection, provider resolution, validation and execution
    remain unchanged. Pytest restores both static methods after every case.
    """
    mode: str = request.param
    if mode == "leaf_probe":
        analyze_original = SpellOccurrenceGraphAnalyzerStrategy._iter_spell_contract_defaults
        process_original = SpellOccurrenceContractProcessorStrategy._iter_spell_contract_defaults

        def analyze(spell: Spell) -> Iterable[tuple[str, SpellContract]]:
            """Treat the existing provider as a leaf; preserve ordinary analyzer behavior."""
            return () if spell.is_existing_creation else analyze_original(spell)

        def process(spell: Spell) -> Iterable[tuple[str, SpellContract]]:
            """Apply the identical leaf hypothesis at the independent processor boundary."""
            return () if spell.is_existing_creation else process_original(spell)

        monkeypatch.setattr(SpellOccurrenceGraphAnalyzerStrategy, "_iter_spell_contract_defaults", staticmethod(analyze))
        monkeypatch.setattr(SpellOccurrenceContractProcessorStrategy, "_iter_spell_contract_defaults", staticmethod(process))
    return mode


def observe(report: dict[str, object], action: Callable[[], None]) -> None:
    """Print outcomes while keeping incorrect identity assertions as hard test failures.

    Runtime refusals are observations, not successful injection. Their stage
    and full error are retained for analysis; no production exception is hidden
    from the resulting GAP record. AssertionError is deliberately not caught.
    """
    try:
        action()
    except (RuntimeError, TypeError, ValueError, KeyError, AttributeError, NameError) as error:
        report.update(outcome="refused", error_type=type(error).__name__, error=str(error))
    else:
        report["outcome"] = "completed"
    print("GAP " + json.dumps(report, sort_keys=True))


@pytest.mark.parametrize("scenario", (
    "direct", "nested", "collection", "pair", "function", "name_token", "string_token", "map",
    "override", "missing_provider_override", "default", "default_override", "none_default",
))
def test_existing_injection_paths(gap_book: Spellbook, planning_mode: str, scenario: str) -> None:
    """Compare actual consumer identity across required, explicit, default and override paths."""
    supplied = SuppliedValue("supplied")
    alternate = AlternateValue("alternate")
    replacement = SuppliedValue("replacement")
    report: dict[str, object] = {"case": scenario, "planning": planning_mode, "stage": "bind"}

    def action() -> None:
        """Build one consumer graph and assert its exact supplied references when it succeeds."""
        if scenario != "missing_provider_override":
            gap_book.bind(
                spell=supplied, existence="unique",
                spellframe="named-values" if scenario == "map" else None if scenario in ("name_token", "string_token") else SuppliedValue,
                binding_name="chosen" if scenario == "map" else None,
            )
        consumer: object = ValueConsumer
        if scenario == "nested":
            gap_book.bind(spell=ValueConsumer, existence="many")
            consumer = NestedValueConsumer
        elif scenario == "collection":
            gap_book.bind(spell=alternate, existence="unique", spellframe=SuppliedValue, binding_name="alternate")
            consumer = CollectionValueConsumer
        elif scenario == "pair":
            consumer = PairConsumer
        elif scenario == "function":
            consumer = factory_consumer
        elif scenario == "name_token":
            consumer = NameTokenConsumer
        elif scenario == "string_token":
            consumer = StringTokenConsumer
        elif scenario == "map":
            consumer = MappedValueConsumer
        elif scenario in ("default", "default_override"):
            consumer = DefaultConsumer
        elif scenario == "none_default":
            consumer = NullableConsumer
        target = gap_book.bind(spell=consumer, existence="unique" if scenario == "function" else "many")
        report["stage"] = "conjure"
        root = gap_book.conjure(dynamic=True)
        report["stage"] = "meld"
        overrides = {"value": replacement} if "override" in scenario else None
        result = root.meld(spell_id=target, override=overrides)
        if scenario == "nested":
            assert result.child.value is supplied
        elif scenario == "collection":
            assert len(result.values) == 2
            assert result.values[0] is supplied and result.values[1] is alternate
        elif scenario == "pair":
            assert result.values[0] is supplied and result.values[1] is supplied
        else:
            expected = replacement if overrides else DefaultConsumer.selected if scenario == "default" else None if scenario == "none_default" else supplied
            assert result.value is expected
        report["identity_preserved"] = True

    observe(report, action)


def test_deferred_annotation_with_class_provider(gap_book: Spellbook) -> None:
    """Determine whether the annotation failure also occurs without an existing-instance provider."""
    gap_book.bind(spell=SuppliedValue, existence="unique")
    report: dict[str, object] = {"case": "deferred_class_provider", "planning": "stock", "stage": "bind_consumer"}

    def action() -> None:
        """Stop at consumer registration, before any class construction could be requested."""
        gap_book.bind(spell=NameTokenConsumer, existence="many")

    observe(report, action)


@pytest.mark.parametrize("scope,existence", (
    ("root", "many"), ("root", "unique"),
    ("lesser", "unique_per_conduit"), ("spellspace", "unique_per_spell_space"),
))
def test_existing_consumer_scope_reuse(
        gap_book: Spellbook, planning_mode: str, scope: str, existence: str,
) -> None:
    """Prove consumer lifetime and supplied-provider identity independently across real scopes."""
    supplied = SuppliedValue("shared")
    report: dict[str, object] = {"case": "consumer_scope_" + scope + "_" + existence, "planning": planning_mode, "stage": "bind"}

    def action() -> None:
        """Meld twice, release the selected scope and verify owner access afterward."""
        provider_id = gap_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
        consumer_id = gap_book.bind(spell=ValueConsumer, existence=existence)
        report["stage"] = "conjure"
        root = gap_book.conjure(dynamic=True)
        door = root.create_lesser_conduit() if scope == "lesser" else root.create_spellspace() if scope == "spellspace" else root
        report["stage"] = "meld"
        try:
            first = door.meld(spell_id=consumer_id)
            second = door.meld(spell_id=consumer_id)
            assert first.value is supplied and second.value is supplied
            assert (first is second) == (existence != "many")
            report.update(identity_preserved=True, consumer_reused=first is second)
        finally:
            if scope != "root":
                door.cleanup()
        assert root.meld(spell_id=provider_id) is supplied

    observe(report, action)


@pytest.mark.parametrize("valid", (False, True))
def test_class_protocol_admission_control(gap_book: Spellbook, valid: bool) -> None:
    """Compare existing-object frame admission with the real class-profile validation gate."""
    report: dict[str, object] = {"case": "class_protocol_valid" if valid else "class_protocol_invalid", "planning": "stock", "stage": "bind"}

    def action() -> None:
        """Register only the class, isolating frame validation from planning and construction."""
        gap_book.bind(spell=DisposableValue if valid else WrongValue, existence="unique", spellframe=ReadableValue)

    observe(report, action)


@pytest.mark.parametrize("lookup", ("id", "instance", "class", "name", "frame", "named"))
def test_existing_root_lookup_forms(gap_book: Spellbook, lookup: str) -> None:
    """Characterize actual public lookup forms rather than reusing spell_id for every case."""
    supplied = SuppliedValue("lookup")
    report: dict[str, object] = {"case": "lookup_" + lookup, "planning": "stock", "stage": "bind"}

    def action() -> None:
        """Bind the metadata needed by this lookup and verify stable repeated identity."""
        target = gap_book.bind(
            spell=supplied, existence="unique",
            spellframe=SuppliedValue if lookup == "frame" else None,
            binding_name="chosen" if lookup == "named" else None,
        )
        root = gap_book.conjure(dynamic=True)
        report["stage"] = "meld"
        if lookup == "id":
            value = root.meld(spell_id=target)
        elif lookup == "instance":
            value = root.meld(spell=supplied)
        elif lookup == "class":
            value = root.meld(spell=SuppliedValue)
        elif lookup == "name":
            value = root.meld("ExistingValue")
        elif lookup == "frame":
            value = root.meld(spellframe=SuppliedValue)
        else:
            value = root.meld(spell=SuppliedValue, binding_name="chosen")
        assert value is supplied
        assert root.meld(spell_id=target) is supplied
        assert root.meld_existing_spell(spell=target) is supplied
        report["identity_preserved"] = True

    observe(report, action)


@pytest.mark.parametrize("scope", ("root", "lesser", "spellspace"))
@pytest.mark.parametrize("late_bind", (False, True))
def test_existing_scope_identity(gap_book: Spellbook, scope: str, late_bind: bool) -> None:
    """Check eager/late registration, scope release and subsequent owner use."""
    supplied = DisposableValue("survives-scope")
    report: dict[str, object] = {"case": "scope_" + scope, "late_bind": late_bind, "planning": "stock", "stage": "bind"}

    def action() -> None:
        """Resolve through one scope and prove releasing it preserves the original object."""
        root = gap_book.conjure(dynamic=True) if late_bind else None
        target = gap_book.bind(spell=supplied, existence="unique", spellframe=DisposableValue)
        if root is None:
            root = gap_book.conjure(dynamic=True)
        door = root.create_lesser_conduit() if scope == "lesser" else root.create_spellspace() if scope == "spellspace" else root
        report["stage"] = "meld"
        try:
            assert door.meld(spell_id=target) is supplied
            assert door.meld(spell_id=target) is supplied
        finally:
            if scope != "root":
                door.cleanup()
        assert root.meld(spell_id=target) is supplied
        assert supplied.read() == "survives-scope" and supplied.disposals == 0
        report.update(identity_preserved=True, disposals_after_scope=supplied.disposals)

    observe(report, action)


@pytest.mark.parametrize("payload", ("none", "empty", "replacement"))
def test_existing_root_overrides(gap_book: Spellbook, payload: str) -> None:
    """Observe whether an override is meaningful or rejected for an already-created root."""
    supplied = SuppliedValue("original")
    target = gap_book.bind(spell=supplied, existence="unique")
    root = gap_book.conjure(dynamic=True)
    report: dict[str, object] = {"case": "root_override_" + payload, "planning": "stock", "stage": "meld"}

    def action() -> None:
        """Keep the original object unchanged even when its override request is refused."""
        override = None if payload == "none" else {} if payload == "empty" else {"marker": "replacement"}
        assert root.meld(spell_id=target, override=override) is supplied
        assert supplied.marker == "original"
        report["identity_preserved"] = True

    observe(report, action)
    assert supplied.marker == "original"


@pytest.mark.parametrize("kind", ("instance", "class"))
def test_existing_disposal_policy(gap_book: Spellbook, kind: str) -> None:
    """Compare requested disposal names with actual cleanup calls, using a class control."""
    supplied = DisposableValue("external")
    target = gap_book.bind(
        spell=supplied if kind == "instance" else DisposableValue,
        existence="unique", disposal_method_names=["dispose"],
    )
    spell = gap_book.find_spell_by_id(target)
    assert spell is not None
    methods = list(spell.disposal_method_names)
    root = gap_book.conjure(dynamic=True)
    value = root.meld(spell_id=target)
    if kind == "instance":
        assert value is supplied
    root.cleanup()
    assert value.disposals == (0 if kind == "instance" else 1)
    print("GAP " + json.dumps({
        "case": "disposal_" + kind, "planning": "stock", "outcome": "completed",
        "requested": ["dispose"], "retained_methods": methods, "disposals": value.disposals,
    }, sort_keys=True))


@pytest.mark.parametrize("frame_kind", ("concrete", "protocol"))
def test_existing_mismatched_frame(gap_book: Spellbook, planning_mode: str, frame_kind: str) -> None:
    """Observe whether the runtime rejects a supplied object that cannot satisfy its advertised frame."""
    supplied = WrongValue()
    report: dict[str, object] = {"case": "wrong_frame_" + frame_kind, "planning": planning_mode, "stage": "bind"}

    def action() -> None:
        """Record admission and injection separately from usable type/behavior satisfaction."""
        gap_book.bind(spell=supplied, existence="unique", spellframe=ReadableValue if frame_kind == "protocol" else SuppliedValue)
        report["binding_accepted"] = True
        target = gap_book.bind(spell=ProtocolConsumer if frame_kind == "protocol" else ValueConsumer, existence="many")
        report["stage"] = "conjure"
        root = gap_book.conjure(dynamic=True)
        report["stage"] = "meld"
        value = root.meld(spell_id=target).value
        assert value is supplied
        report.update(injected_incompatible_instance=True, identity_preserved=True)
        if frame_kind == "protocol":
            report["stage"] = "consumer_use"
            value.read()

    observe(report, action)


@pytest.mark.parametrize("contract", (False, True), ids=("annotation", "spell_contract"))
def test_existing_linked_injection(gap_book: Spellbook, planning_mode: str, contract: bool) -> None:
    """Import a real existing provider through read permission and resolve it from a borrower."""
    supplied = SuppliedValue("owner-value")
    provider_id = gap_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue, binding_name="shared")
    owner = gap_book.conjure(dynamic=True, name="owner")
    borrower_book = Spellbook(aetheric_frame="existing-instance-planning-regression")
    report: dict[str, object] = {"case": "linked_contract" if contract else "linked_annotation", "planning": planning_mode, "stage": "link"}

    def action() -> None:
        """Keep real contract validation and prove the borrower receives the owner's object."""
        borrower = borrower_book.conjure(dynamic=True, name="borrower")
        assert borrower.link(owner)
        assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=owner, permissions="read")
        report["stage"] = "bind_consumer"
        target = borrower.bind(spell=ContractConsumer if contract else ValueConsumer, existence="many")
        report["stage"] = "meld"
        value = borrower.meld(spell_id=target).value
        assert value is supplied
        report["identity_preserved"] = True

    try:
        observe(report, action)
    finally:
        if not borrower_book.cleaned:
            if borrower_book.conduit is None:
                borrower_book.cleanup()
            else:
                borrower_book.conduit.cleanup()
    assert owner.meld(spell_id=provider_id) is supplied


@pytest.mark.parametrize("kind", ("false", "zero", "empty_list", "empty_dict"))
def test_existing_falsey_values(gap_book: Spellbook, kind: str) -> None:
    """Resolve falsey non-None supplied values by ID without confusing presence with truthiness."""
    supplied = False if kind == "false" else 0 if kind == "zero" else [] if kind == "empty_list" else {}
    report: dict[str, object] = {"case": "falsey_" + kind, "planning": "stock", "stage": "bind"}

    def action() -> None:
        """Verify the exact falsey object survives eager registration and repeated lookup."""
        target = gap_book.bind(spell=supplied, existence="unique", binding_name="falsey")
        root = gap_book.conjure(dynamic=True)
        report["stage"] = "meld"
        assert root.meld(spell_id=target) is supplied
        assert root.meld_existing_spell(spell=target) is supplied
        report["identity_preserved"] = True

    observe(report, action)
