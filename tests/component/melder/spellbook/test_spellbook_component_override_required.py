"""Compiler contracts separating descriptive registrations from construction dependencies."""

from collections.abc import Iterator
from dataclasses import replace
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class Definition:
    """Application definition available for graph references independently of construction."""


class Implementation(Definition):
    """First ordinary provider of Definition for capability-precedence tests."""


class OtherImplementation(Definition):
    """Second provider keeps normal ambiguity and collection-order checks meaningful."""


class Consumer:
    """Require one Definition while allowing the compiler to select its supply policy."""

    def __init__(self, value: Definition) -> None:
        """Retain the supplied dependency for later runtime tests."""
        self.value = value


class OptionalConsumer:
    """A nullable annotation without a default still declares a required input."""

    def __init__(self, value: Optional[Definition]) -> None:
        """Retain the explicit value; omission is not implied by Optional."""
        self.value = value


class DefaultConsumer:
    """An ordinary default retains the established PLAIN policy."""

    def __init__(self, value: Optional[Definition] = None) -> None:
        """Retain the chosen default unless the caller explicitly replaces it."""
        self.value = value


class CollectionConsumer:
    """Request all executable providers while leaving descriptive definitions out."""

    def __init__(self, values: list[Definition]) -> None:
        """Store the ordered collection of providers."""
        self.values = values


class Unregistered:
    """A type deliberately absent from the registration pool."""


class DefinitionWithDependency:
    """Descriptive constructor requirements must not require a construction provider."""

    def __init__(self, dependency: Unregistered) -> None:
        """Describe an application dependency that Melder will not construct."""
        self.dependency = dependency


@pytest.fixture
def compiler_book() -> Iterator[Spellbook]:
    """Own one isolated compiler world and clean it after each contract test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame="override-required")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    try:
        yield book
    finally:
        book.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _selected(book: Spellbook, spell_id: str) -> Spell:
    """Return the exact selected record produced by this test's active bind."""
    spell = book.find_spell_by_id(spell_id)
    assert spell is not None and spell.spell_id == spell_id
    return spell


def _local_topology(book: Spellbook, spell_id: str, *, indexed: bool) -> SpellLocalTopology:
    """Run real phases 1-3 for one consumer, exercising indexed or ordinary candidate matching."""
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
def test_false_target_requires_override_and_retains_reference(
    compiler_book: Spellbook, indexed: bool, consumer_type: type,
) -> None:
    """Required and nullable inputs retain declarations but create no executable provider edge."""
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=consumer_type, existence="unique")
    topology = _local_topology(compiler_book, consumer_id, indexed=indexed)
    socket, = topology.sockets
    assert socket.socket_kind is SocketKind.OVERRIDE_REQUIRED
    assert socket.target_spell_ids == ()
    assert socket.referenced_spell_ids == (definition_id,)
    assert socket.parameter_kind == "POSITIONAL_OR_KEYWORD"
    assert socket.position == 0
    assert socket.dependency_key is not None
    spell = _selected(compiler_book, consumer_id)
    assert spell.dependencies == []
    assert tuple(spell.resolution_frame.ordered_node_ids) == (consumer_id,)
    assert spell.requirements.parameters[0].di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert spell.requirements.parameters[0].has_default is False


@pytest.mark.parametrize("indexed", [False, True])
def test_real_provider_takes_precedence_over_descriptive_definition(
    compiler_book: Spellbook, indexed: bool,
) -> None:
    """Implicit annotation matching selects the ordinary provider without poisoning the shared type."""
    compiler_book.bind(spell=Definition, existence="unique", binding_name="definition", resolvable=False)
    provider_id = compiler_book.bind(
        spell=Implementation, spellframe=Definition, existence="unique", binding_name="runtime",
    )
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=indexed).sockets
    assert socket.socket_kind is SocketKind.NORMAL
    assert socket.target_spell_ids == (provider_id,)
    assert socket.referenced_spell_ids == ()


@pytest.mark.parametrize("indexed", [False, True])
@pytest.mark.parametrize("provider_count", [0, 1, 2])
def test_collections_exclude_false_definitions_and_preserve_provider_order(
    compiler_book: Spellbook, indexed: bool, provider_count: int,
) -> None:
    """Zero providers remains an empty collection; definitions never become collection elements."""
    compiler_book.bind(spell=Definition, existence="unique", binding_name="definition", resolvable=False)
    provider_ids = [
        compiler_book.bind(spell=provider, spellframe=Definition, existence="unique", binding_name=provider.__name__)
        for provider in (Implementation, OtherImplementation)[:provider_count]
    ]
    consumer_id = compiler_book.bind(spell=CollectionConsumer, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=indexed).sockets
    assert socket.socket_kind is SocketKind.NORMAL
    assert socket.is_collection is True
    assert socket.target_spell_ids == tuple(provider_ids)
    assert socket.referenced_spell_ids == ()


def test_defaulted_parameter_stays_plain_with_a_false_registration(compiler_book: Spellbook) -> None:
    """The presence of a descriptive registration does not override an ordinary Python default."""
    compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=DefaultConsumer, existence="unique")
    socket, = _local_topology(compiler_book, consumer_id, indexed=True).sockets
    assert socket.socket_kind is SocketKind.NORMAL
    assert socket.target_spell_ids == socket.referenced_spell_ids == ()
    requirement, = _selected(compiler_book, consumer_id).requirements.parameters
    assert requirement.di_shape is ParameterDIShape.PLAIN
    assert requirement.default_value is None


def test_false_root_keeps_declaration_without_resolving_its_constructor(compiler_book: Spellbook) -> None:
    """An unregistered constructor dependency is descriptive data on a non-resolvable root."""
    definition_id = compiler_book.bind(spell=DefinitionWithDependency, existence="unique", resolvable=False)
    topology = _local_topology(compiler_book, definition_id, indexed=True)
    assert [socket.param_name for socket in topology.sockets] == ["dependency"]
    assert topology.sockets[0].target_spell_ids == ()
    definition = _selected(compiler_book, definition_id)
    assert definition.dependencies == []
    assert definition.requirements.parameters[0].annotation is Unregistered


def test_explicit_spellmap_keeps_the_false_target_even_with_a_provider(compiler_book: Spellbook) -> None:
    """Explicit selection becomes required supply instead of redirecting to another registration."""
    descriptor = SpellMap(spell=Definition, binding_name="definition")

    class MappedConsumer:
        """Select a specific descriptive registration through a real SpellMap."""

        def __init__(self, value: Definition = descriptor) -> None:
            """Retain the value supplied at construction rather than the DI descriptor."""
            self.value = value

    try:
        definition_id = compiler_book.bind(
            spell=Definition, existence="unique", binding_name="definition", resolvable=False,
        )
        compiler_book.bind(spell=Implementation, spellframe=Definition, existence="unique", binding_name="runtime")
        consumer_id = compiler_book.bind(spell=MappedConsumer, existence="unique")
        socket, = _local_topology(compiler_book, consumer_id, indexed=True).sockets
        assert socket.socket_kind is SocketKind.OVERRIDE_REQUIRED
        assert socket.target_spell_ids == ()
        assert socket.referenced_spell_ids == (definition_id,)
    finally:
        descriptor.cleanup()


@pytest.mark.parametrize("payload", [{}, {"x": 1}, []])
def test_false_spellmap_refuses_provider_construction_payload(compiler_book: Spellbook, payload: object) -> None:
    """Even an empty explicit construction payload is incompatible with a disabled provider."""
    descriptor = SpellMap(spell=Definition, override=payload)

    class MappedConsumer:
        """Declare an incompatible construction payload on a descriptive definition."""

        def __init__(self, value: Definition = descriptor) -> None:
            """Store the selected value if execution is ever requested."""
            self.value = value

    try:
        compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
        consumer_id = compiler_book.bind(spell=MappedConsumer, existence="unique")
        with pytest.raises(RuntimeError, match="non-resolvable.*override"):
            _local_topology(compiler_book, consumer_id, indexed=False)
    finally:
        descriptor.cleanup()


def _structural_pass(book: Spellbook, compiler: SpellCompilerSystem) -> None:
    """Run each structural phase across the real book before advancing its barrier."""
    for spell in book.spells.values():
        compiler.run_phase_requirements(spell)
        compiler.run_phase_symbolic_graph(spell)
    for spell in book.spells.values():
        compiler.run_phase_local_frame(book, spell)
    for spell in book.spells.values():
        compiler.run_phase_validation(book, spell)


def test_required_override_validation_reports_the_consumer_and_reference(compiler_book: Spellbook) -> None:
    """Required supply is an informative warning at compile time, not a missing-provider error."""
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        spell = _selected(compiler_book, consumer_id)
        assert not spell.is_broken
        issues = [issue for issue in spell.validation_result_phase4.issues if issue.code == "OVERRIDE_REQUIRED"]
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert issues[0].details["parameter_name"] == "value"
        assert issues[0].details["referenced_spell_ids"] == (definition_id,)
    finally:
        compiler.cleanup()


def test_descriptive_back_reference_does_not_create_a_binding_cycle(compiler_book: Spellbook) -> None:
    """A descriptive constructor back-reference cannot recreate a construction-cycle edge."""
    class BackDefinition:
        """Reference the consuming type in an unexecuted constructor."""

        def __init__(self, consumer: BackConsumer) -> None:
            """Retain the application reference if constructed outside Melder."""
            self.consumer = consumer

    class BackConsumer:
        """Require a supplied BackDefinition value."""

        def __init__(self, definition: BackDefinition) -> None:
            """Retain the supplied definition value."""
            self.definition = definition

    compiler_book.bind(spell=BackDefinition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=BackConsumer, existence="unique")
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        assert all(not spell.is_broken for spell in compiler_book.spells.values())
        assert _selected(compiler_book, consumer_id).dependencies == []
    finally:
        compiler.cleanup()


def test_non_resolvable_constructor_is_not_restricted_to_di_shapes(compiler_book: Spellbook) -> None:
    """Ordinary Python set/variadic annotations on descriptive roots impose no DI requirements."""
    class DescriptiveOnly:
        """Represent an ordinary application definition whose constructor Melder never invokes."""

        def __init__(self, values: set[Definition], *extras: Definition) -> None:
            """Retain application arguments without declaring executable Melder dependencies."""
            self.values = values
            self.extras = extras

    definition_id = compiler_book.bind(spell=DescriptiveOnly, existence="unique", resolvable=False)
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        assert not _selected(compiler_book, definition_id).is_broken
    finally:
        compiler.cleanup()


@pytest.mark.parametrize("include_consumer", [False, True])
def test_phase5_executable_view_excludes_definitions_but_keeps_local_topology(
    compiler_book: Spellbook, include_consumer: bool,
) -> None:
    """False-only and mixed books retain descriptive state without building definition blueprints."""
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    anchor_id = compiler_book.bind(spell=Consumer, existence="unique") if include_consumer else definition_id
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        anchor = _selected(compiler_book, anchor_id)
        compiler.run_phase_root_blueprints(compiler_book, anchor, "compiler-conduit")
        artifact = anchor._compiler_artifact
        assert definition_id not in artifact._entire_dag_blueprint_phase5
        assert definition_id not in artifact._spell_system_index_phase5.nodes
        assert _selected(compiler_book, definition_id)._compiler_artifact._root_blueprint_phase5 is None
        assert compiler_book._spell_system_states.get_local_topology_by_id(definition_id) is not None
        expected_roots = {anchor_id} if include_consumer else set()
        assert set(artifact._entire_dag_blueprint_phase5) == expected_roots
        if include_consumer:
            socket, = artifact._root_blueprint_phase5.socket_refs
            assert socket.socket_kind is SocketKind.OVERRIDE_REQUIRED
    finally:
        compiler.cleanup()


def test_false_definition_has_no_executable_cache_obligation(compiler_book: Spellbook) -> None:
    """An explicitly descriptive registration must not keep a runnable book on the cache-miss path."""
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=compiler_book, dynamic=False, conduit_name="compiler-cache",
    )
    assert cache_state["live_spell_ids"] == {consumer_id}
    assert definition_id not in cache_state["missing_spell_ids"]


@pytest.mark.parametrize("phase_number", [8, 9, 10, 11])
def test_direct_plan_phase_entry_skips_non_resolvable_definitions(
    compiler_book: Spellbook, phase_number: int,
) -> None:
    """Direct compiler entry agrees with scheduler eligibility before requiring executable artifacts."""
    definition_id = compiler_book.bind(spell=DefinitionWithDependency, existence="unique", resolvable=False)
    spell = _selected(compiler_book, definition_id)
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        if phase_number == 8:
            compiler.run_phase_occurrence_plan(compiler_book, spell)
        elif phase_number == 9:
            compiler.run_phase_injection_plan(spell)
        elif phase_number == 10:
            compiler.run_phase_patch_maps(spell)
        else:
            compiler.run_phase_execution_plan(compiler_book, spell)
        assert spell._compiler_artifact._occurrence_graph_analysis is None
        assert spell._compiler_artifact._spell_codegen_model is None
        assert spell._compiler_artifact._spell_codegen_plan is None
        assert spell._compiler_artifact._spell_codegen_creation is None
    finally:
        compiler.cleanup()


@pytest.mark.parametrize("family", ["solo", "many_only", "generalized"])
def test_required_input_rows_survive_both_planner_variants(compiler_book: Spellbook, family: str) -> None:
    """Every plan family retains required-input identity independently of optional override metadata."""
    class RuntimeDependency:
        """Give non-solo consumers one real executable provider."""

    class MixedConsumer:
        """Use an ordinary provider and a required externally supplied definition value."""

        def __init__(self, dependency: RuntimeDependency, *, value: Definition) -> None:
            """Retain the provider and the keyword-only supplied input."""
            self.dependency = dependency
            self.value = value

    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    if family == "solo":
        consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
        expected = (("value", 0, "POSITIONAL_OR_KEYWORD", (definition_id,)),)
    else:
        compiler_book.bind(spell=RuntimeDependency, existence="many" if family == "many_only" else "unique")
        consumer_id = compiler_book.bind(spell=MixedConsumer, existence="many")
        expected = (("value", 1, "KEYWORD_ONLY", (definition_id,)),)
    compiler = SpellCompilerSystem()
    try:
        _structural_pass(compiler_book, compiler)
        consumer = _selected(compiler_book, consumer_id)
        compiler.run_phase_root_blueprints(compiler_book, consumer, "compiler-conduit")
        compiler.run_phase_occurrence_plan(compiler_book, consumer)
        compiler.run_phase_injection_plan(consumer)
        model = consumer._compiler_artifact._spell_codegen_model
        injection = model.injection_shape
        source = injection.instance_specs_by_instance_key[injection.root_instance_key].param_sources["value"]
        assert source.kind == "override_required"
        assert source.dependency_keys == ()
        assert source.referenced_spell_ids == (definition_id,)
        exported = SharedCompilerExecutions.build_injection_instance_rows(injection.instance_specs_by_instance_key)
        root_row = next(row for row in exported if row[0] == injection.root_instance_key)
        input_row = next(row for row in root_row[4] if row[0] == "value")
        assert input_row[6:] == expected[0][1:]
        for include_metadata in (False, True):
            signature = SharedCompilerExecutions.build_phase11_injection_spec_signature_row(
                injection.instance_specs_by_instance_key[injection.root_instance_key],
                include_override_metadata=include_metadata,
            )
            signature_input = next(row for row in signature[0] if row[0] == "value")
            assert signature_input[6:] == expected[0][1:]
        compiler.run_phase_patch_maps(consumer)
        plan = consumer._compiler_artifact._spell_codegen_plan
        for variant in (plan.no_overrides_plan, plan.overrides_plan):
            step = next(step for step in variant.steps if step.instance_key[0] == consumer_id)
            assert step.required_override_params == expected
            assert all(key[0] != definition_id for _, keys in step.dependency_resolution_order for key in keys)
    finally:
        compiler.cleanup()


@pytest.mark.parametrize(("field", "value"), [
    ("referenced_spell_ids", ("other-definition",)),
    ("parameter_kind", "KEYWORD_ONLY"),
    ("position", 2),
    ("is_optional", True),
    ("is_collection", True),
    ("socket_kind", SocketKind.NORMAL),
])
def test_occurrence_signature_tracks_required_input_policy(
    compiler_book: Spellbook, field: str, value: object,
) -> None:
    """A topology replacement must change the analyzer key when consumed input policy changes."""
    compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=Consumer, existence="unique")
    topology = _local_topology(compiler_book, consumer_id, indexed=True)
    consumer = _selected(compiler_book, consumer_id)
    analyzer = SpellOccurrenceGraphAnalyzerStrategy()
    before = analyzer._build_graph_shape_rows(
        spellbook=compiler_book, spell_system_states=compiler_book._spell_system_states,
    )
    assert before is not None
    changed = SpellLocalTopology(consumer_id, [replace(topology.sockets[0], **{field: value})])
    compiler_book._spell_system_states.register_local_topology(consumer.spell_index, changed)
    after = analyzer._build_graph_shape_rows(
        spellbook=compiler_book, spell_system_states=compiler_book._spell_system_states,
    )
    assert after is not None and after != before


def test_late_contract_compilation_refuses_non_resolvable_provider(compiler_book: Spellbook) -> None:
    """Public contract sharing may expose a definition, but late compiler selection cannot execute it."""
    owner_book = Spellbook(aetheric_frame="override-required")
    owner_book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    contract = SpellContract(spellframe=Definition, binding_name="definition")
    try:
        owner = owner_book.conjure(dynamic=True, name="definition-owner")
        borrower = compiler_book.conjure(dynamic=True, name="definition-borrower")
        provider_id = owner.bind(
            spell=Definition, spellframe=Definition, binding_name="definition", existence="unique", resolvable=False,
        )
        owner.link(borrower)
        assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=owner, permissions="create")
        consumer_id = borrower.bind(spell=Consumer, existence="unique")
        with pytest.raises(MeldExecutionError, match="non-resolvable"):
            SpellOccurrenceGraphAnalyzerStrategy()._resolve_spell_contract_spell_id(
                contract=contract, consumer_spell=_selected(compiler_book, consumer_id),
                param_name="value", spellbook=compiler_book, allow_missing=True,
            )
    finally:
        contract.cleanup()
        owner_book.cleanup()


@pytest.mark.parametrize("consumer_type", [Consumer, OptionalConsumer])
def test_notch_from_definition_to_provider_revalidates_its_consumer(
    compiler_book: Spellbook, consumer_type: type,
) -> None:
    """Switching the selected capability must rebuild a consumer that had only a descriptive reference."""
    compiler_book._aetheric_frame_configuration.with_system_caching_enabled(False)
    definition_id = compiler_book.bind(spell=Definition, existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=consumer_type, existence="many")
    index = _selected(compiler_book, definition_id).spell_index
    conduit = compiler_book.conjure(dynamic=True, name="notch-required-input")
    provider_id = conduit.bind_inactive(spell=Definition, spell_index=index, existence="unique")
    provider = compiler_book._inactive_spells[provider_id]
    conduit.notch_spell(spell_index=index, spell=provider)
    result = conduit.meld(spell=consumer_type)
    assert isinstance(result.value, Definition)
    assert _selected(compiler_book, consumer_id).dependencies == [provider_id]


@pytest.mark.parametrize("consumer_type", [Consumer, OptionalConsumer])
def test_new_provider_revalidates_an_existing_override_required_consumer(
    compiler_book: Spellbook, consumer_type: type,
) -> None:
    """A newly bound True provider supersedes the existing implicit False-only selection on the next meld."""
    compiler_book._aetheric_frame_configuration.with_system_caching_enabled(False)
    compiler_book.bind(spell=Definition, binding_name="definition", existence="unique", resolvable=False)
    consumer_id = compiler_book.bind(spell=consumer_type, existence="many")
    conduit = compiler_book.conjure(dynamic=True, name="bind-required-input")
    provider_id = conduit.bind(
        spell=Implementation, spellframe=Definition, binding_name="runtime", existence="unique",
    )
    result = conduit.meld(spell=consumer_type)
    assert isinstance(result.value, Implementation)
    assert _selected(compiler_book, consumer_id).dependencies == [provider_id]
