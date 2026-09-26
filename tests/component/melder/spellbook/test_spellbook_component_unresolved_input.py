"""Compiler contracts for typed parameters that no registered spell provides (UNRESOLVED_INPUT)."""

import annotationlib
import inspect
import logging
from collections.abc import Iterator
from typing import Optional, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class Unregistered:
    """A type deliberately absent from every registration pool."""


class Provider(Unregistered):
    """Ordinary provider used to turn the input into a normal edge."""


class OtherProvider(Unregistered):
    """Second provider keeps the two-candidate ambiguity error meaningful."""


class Consumer:
    """Require one typed value that nothing registered provides."""

    def __init__(self, value: Unregistered) -> None:
        """Retain the supplied value by identity."""
        self.value = value


class OptionalConsumer:
    """A nullable annotation without a default is still a required input."""

    def __init__(self, value: Optional[Unregistered]) -> None:
        """Retain the supplied value, including None."""
        self.value = value


class DefaultConsumer:
    """An ordinary Python default keeps PLAIN semantics."""

    def __init__(self, value: Optional[Unregistered] = None) -> None:
        """Retain the default unless a caller overrides it."""
        self.value = value


class CollectionConsumer:
    """Zero providers for a collection still injects an empty list."""

    def __init__(self, values: list[Unregistered]) -> None:
        """Store the ordered providers."""
        self.values = values


class KeywordConsumer:
    """Keyword-only unresolved input keeps its signature kind."""

    def __init__(self, *, value: Unregistered) -> None:
        """Retain the supplied value."""
        self.value = value


@pytest.fixture
def compiler_book() -> Iterator[Spellbook]:
    """Own one isolated compiler world and clean it after each contract test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame="unresolved-input")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    try:
        yield book
    finally:
        book.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _selected(book: Spellbook, spell_id: str) -> Spell:
    """Return the exact selected record produced by this test's bind."""
    spell = book.find_spell_by_id(spell_id)
    assert spell is not None and spell.spell_id == spell_id
    return spell


def _structural_pass(book: Spellbook, compiler: SpellCompilerSystem) -> None:
    """Run each structural phase across the real book before advancing its barrier."""
    for spell in book.spells.values():
        compiler.run_phase_requirements(spell)
        compiler.run_phase_symbolic_graph(spell)
    for spell in book.spells.values():
        compiler.run_phase_local_frame(book, spell)
    for spell in book.spells.values():
        compiler.run_phase_validation(book, spell)


def _local_topology(book: Spellbook, spell_id: str, *, indexed: bool) -> SpellLocalTopology:
    """Run real phases 1-3 for one consumer through indexed or ordinary candidate matching."""
    spell = _selected(book, spell_id)
    compiler = SpellCompilerSystem()
    try:
        compiler.run_phase_requirements(spell)
        compiler.run_phase_symbolic_graph(spell)
        compiler.run_phase_local_frame(book, spell, resolution_pass_cache={} if indexed else None)
    finally:
        compiler.cleanup()
    topology = book._spell_system_states.get_local_topology(spell.spell_index)
    assert topology is not None
    return topology


@pytest.mark.parametrize("indexed", [False, True])
@pytest.mark.parametrize("consumer_type", [Consumer, OptionalConsumer])
def test_zero_providers_compile_as_an_unresolved_input(
    compiler_book: Spellbook, indexed: bool, consumer_type: type,
) -> None:
    """No candidate at all yields an UNRESOLVED_INPUT socket with its watch key, not a Phase-3 error."""
    consumer_id = compiler_book.bind(spell=consumer_type, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=indexed).sockets
    assert socket.socket_kind is SocketKind.UNRESOLVED_INPUT
    assert socket.target_spell_ids == ()
    assert socket.referenced_spell_ids == ()
    assert socket.dependency_key == ("unregistered", "__default__")
    assert (socket.position, socket.parameter_kind) == (0, "POSITIONAL_OR_KEYWORD")
    assert _selected(compiler_book, consumer_id).dependencies == []


def test_keyword_only_unresolved_input_keeps_its_signature_kind(compiler_book: Spellbook) -> None:
    """Position and kind survive so supply by name or position is judged against the real signature."""
    consumer_id = compiler_book.bind(spell=KeywordConsumer, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=True).sockets
    assert socket.socket_kind is SocketKind.UNRESOLVED_INPUT
    assert socket.parameter_kind == "KEYWORD_ONLY"


@pytest.mark.parametrize(("setup", "expected_kind"), [
    ("one_provider", SocketKind.NORMAL),
    ("definition_only", SocketKind.OVERRIDE_REQUIRED),
])
def test_existing_socket_kinds_are_unchanged(
    compiler_book: Spellbook, setup: str, expected_kind: SocketKind,
) -> None:
    """A provider still makes a normal edge; a non-resolvable definition still means OVERRIDE_REQUIRED."""
    if setup == "one_provider":
        compiler_book.bind(spell=Provider, spellframe=Unregistered, existence="unique")
    else:
        compiler_book.bind(spell=Unregistered, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=True).sockets
    assert socket.socket_kind is expected_kind


def test_two_providers_remain_an_ambiguity_error(compiler_book: Spellbook) -> None:
    """Ambiguity is a configuration error, never an input the caller could supply."""
    compiler_book.bind(spell=Provider, spellframe=Unregistered, existence="unique", binding_name="one")
    compiler_book.bind(spell=OtherProvider, spellframe=Unregistered, existence="unique", binding_name="two")
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    with pytest.raises(RuntimeError, match="multiple DI candidates"):
        _local_topology(compiler_book, consumer_id, indexed=True)


@pytest.mark.parametrize(("consumer_type", "expected_kind"), [
    (DefaultConsumer, SocketKind.NORMAL),
    (CollectionConsumer, SocketKind.NORMAL),
])
def test_defaults_and_collections_do_not_become_unresolved_inputs(
    compiler_book: Spellbook, consumer_type: type, expected_kind: SocketKind,
) -> None:
    """PLAIN defaults and empty collections keep their existing meaning with zero providers."""
    consumer_id = compiler_book.bind(spell=consumer_type, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=True).sockets
    assert socket.socket_kind is expected_kind
    assert socket.socket_kind is not SocketKind.UNRESOLVED_INPUT


def test_validation_warns_with_the_expected_type_and_keeps_the_spell_valid(compiler_book: Spellbook) -> None:
    """Phase 4 records an UNRESOLVED_INPUT warning naming the type; the spell is not broken."""
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        spell = _selected(compiler_book, consumer_id)
        assert not spell.is_broken
        issue, = [issue for issue in spell.validation_result_phase4.issues if issue.code == "UNRESOLVED_INPUT"]
        assert issue.severity == "warning"
        assert issue.details["parameter_name"] == "value"
        assert issue.details["expected_type"] == "Unregistered"
        assert issue.details["dependency_key"] == ("unregistered", "__default__")
        assert "UnresolvedInputError" in issue.message
    finally:
        compiler.cleanup()


@pytest.mark.parametrize("family", ["solo", "many_only", "generalized"])
def test_injection_source_and_rows_carry_the_unresolved_input(compiler_book: Spellbook, family: str) -> None:
    """Phase 9 emits an edge-less override source; exporters append position and kind only."""
    class RuntimeDependency:
        """Give non-solo consumers one real executable provider."""

    class MixedConsumer:
        """Use an ordinary provider plus a keyword-only unresolved input."""

        def __init__(self, dependency: RuntimeDependency, *, value: Unregistered) -> None:
            """Retain both values."""
            self.dependency = dependency
            self.value = value

    if family == "solo":
        consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
        expected_suffix = (0, "POSITIONAL_OR_KEYWORD")
    else:
        compiler_book.bind(spell=RuntimeDependency, existence="many" if family == "many_only" else "unique")
        consumer_id = compiler_book.bind(spell=MixedConsumer, existence="many")
        expected_suffix = (1, "KEYWORD_ONLY")
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        consumer = _selected(compiler_book, consumer_id)
        compiler.run_phase_root_blueprints(compiler_book, consumer, "compiler-conduit")
        compiler.run_phase_occurrence_plan(compiler_book, consumer)
        compiler.run_phase_injection_plan(consumer)
        injection = consumer._compiler_artifact._spell_codegen_model.injection_shape
        root_spec = injection.instance_specs_by_instance_key[injection.root_instance_key]
        source = root_spec.param_sources["value"]
        assert source.kind == "unresolved_input"
        assert source.dependency_keys == ()
        assert source.override_key == "value"
        assert source.referenced_spell_ids == ()
        assert root_spec.required_override_params == ()
        exported = SharedCompilerExecutions.build_injection_instance_rows(injection.instance_specs_by_instance_key)
        root_row = next(row for row in exported if row[0] == injection.root_instance_key)
        input_row = next(row for row in root_row[4] if row[0] == "value")
        assert input_row[6:] == expected_suffix
        for include_metadata in (False, True):
            signature = SharedCompilerExecutions.build_phase11_injection_spec_signature_row(
                root_spec, include_override_metadata=include_metadata,
            )
            signature_input = next(row for row in signature[0] if row[0] == "value")
            assert signature_input[6:] == expected_suffix
    finally:
        compiler.cleanup()


def test_conjure_reports_unresolved_inputs_once(caplog: pytest.LogCaptureFixture) -> None:
    """Conjure succeeds and logs one INFO line listing Spell.param -> ExpectedType."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    logger = logging.getLogger("melder.tests.unresolved_input_report")
    book = Spellbook(aetheric_frame="unresolved-input-report", logger=logger)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    try:
        book.bind(spell=Consumer, existence="many")
        with caplog.at_level(logging.INFO, logger=logger.name):
            conduit = book.conjure()
        lines = [record.getMessage() for record in caplog.records if "unresolved input" in record.getMessage()]
        assert len(lines) == 1
        assert "Consumer.value -> Unregistered" in lines[0]
        conduit.cleanup()
    finally:
        book.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


@pytest.mark.parametrize("consumer_type", [Consumer, OptionalConsumer])
def test_late_provider_turns_the_unresolved_input_into_a_normal_edge(
    compiler_book: Spellbook, consumer_type: type,
) -> None:
    """Binding a matching provider after conjure re-resolves the consumer on its next meld."""
    consumer_id = compiler_book.bind(spell=consumer_type, existence="many")
    conduit = compiler_book.conjure(dynamic=True, name="late-provider")
    try:
        with pytest.raises(UnresolvedInputError):
            conduit.meld(spell=consumer_type)
        provider_id = conduit.bind(spell=Provider, spellframe=Unregistered, existence="unique")
        result = conduit.meld(spell=consumer_type)
        assert isinstance(result.value, Provider)
        assert _selected(compiler_book, consumer_id).dependencies == [provider_id]
        socket, = compiler_book._spell_system_states.get_local_topology(
            _selected(compiler_book, consumer_id).spell_index,
        ).sockets
        assert socket.socket_kind is SocketKind.NORMAL
    finally:
        conduit.cleanup()


def test_unresolved_input_error_is_a_meld_execution_error() -> None:
    """Existing handlers that catch MeldExecutionError keep catching the specific error."""
    assert issubclass(UnresolvedInputError, MeldExecutionError)


@pytest.mark.parametrize(("annotation", "expected"), [
    (Unregistered, "Unregistered"),
    (Optional[Unregistered], "Unregistered"),
    (Union[Unregistered, None], "Unregistered"),
    ("Unregistered", "Unregistered"),
    ("'Unregistered'", "Unregistered"),
    (list[Unregistered], repr(list[Unregistered])),
])
def test_expected_type_name_renders_annotations(annotation: object, expected: str) -> None:
    """One naming rule for the warning and the error: unwrap Optional, quotes and forward refs."""
    assert UnresolvedInputError.expected_type_name(annotation) == expected


def test_expected_type_name_uses_the_written_name_of_an_unresolvable_forward_ref() -> None:
    """A TYPE_CHECKING-only name read with FORWARDREF renders as written, never raising."""
    def target(value: NotImportedAtRuntime) -> None:
        """Carry an annotation that cannot be evaluated."""

    parameter = inspect.signature(target, annotation_format=annotationlib.Format.FORWARDREF).parameters["value"]
    assert UnresolvedInputError.expected_type_name(parameter.annotation) == "NotImportedAtRuntime"
