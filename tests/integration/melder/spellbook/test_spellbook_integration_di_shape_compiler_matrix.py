"""
Deep integration matrix for the DI-shape -> compiler-phase pipeline.

Purpose:
    Exercise every "way we do things" end to end through the REAL compiler
    phases (Phase 1 classification -> Phase 3 resolution -> Phase 4 spell
    validation -> Phase 5/6 system validation) and through conjure/meld
    resolution, using a real Spellbook/Conduit rather than hand-built stubs.

Contract:
    - Drives phases via tests.component.melder.spellbook.compiler_test_helpers.
    - Reads public spell surfaces: spell.requirements, spell.validation_result_phase4,
      spell.validation_result_phase6, spell.is_broken.
    - Covers the six ParameterDIShape classifications, the Phase-4 issue catalog,
      Phase-6 system state, and root meld entry modes.
    - A handful of tests intentionally *characterize current behavior* (including
      two suspected faults) so a later fault pass has a locked baseline; those are
      marked with `CHARACTERIZATION` in their docstring.

NOTE:
    Melder targets Python 3.14t (free-threaded); it relies on 3.14 deferred
    annotations and will not import under < 3.14. Run this suite on 3.14t.
"""
from __future__ import annotations

from typing import List, Optional, Protocol

import pytest

import tests.component.melder.spellbook.compiler_test_helpers as ch
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import (
    SpellValidity,
)
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.validation_system import (
    SpellValidationSystem,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)


# --------------------------------------------------------------------------- #
# Isolation fixture
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def _reset_aether_singleton() -> None:
    """Give every test a clean Aether singleton (mirrors validation-system suite)."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


# --------------------------------------------------------------------------- #
# Module-level test doubles (DI targets, protocol frames, consumers)
# --------------------------------------------------------------------------- #
class IEngine(Protocol):
    """Protocol frame for a single-provider dependency."""


class IPlugin(Protocol):
    """Protocol frame for collection DI."""


class IConfig(Protocol):
    """Protocol frame used for SpellMap / contract targeting."""


class Engine:
    """Concrete provider bound under IEngine."""

    def __init__(self) -> None:
        self.kind = "engine"


class AltEngine:
    """Second concrete provider for ambiguity/collision cases."""

    def __init__(self) -> None:
        self.kind = "alt"


class PluginA:
    """First IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "a"


class PluginB:
    """Second IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "b"


class Config:
    """Config provider for SpellMap tests."""

    def __init__(self) -> None:
        self.name = "cfg"


class NeedsEngineConcrete:
    """SINGLE_BY_ANNOTATION via concrete class."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine


class NeedsEngineProtocol:
    """SINGLE_BY_ANNOTATION via protocol frame."""

    def __init__(self, engine: IEngine) -> None:
        self.engine = engine


class NeedsOptionalEngine:
    """SINGLE_BY_ANNOTATION, optional."""

    def __init__(self, engine: Optional[IEngine] = None) -> None:
        self.engine = engine


class NeedsPlugins:
    """COLLECTION_BY_ANNOTATION via list[IPlugin]."""

    def __init__(self, plugins: List[IPlugin]) -> None:
        self.plugins = plugins


class NeedsConfigViaMap:
    """SPELLMAP_DEFAULT via explicit class map."""

    def __init__(self, config=SpellMap(Config)) -> None:
        self.config = config


class EngineHintButMapped:
    """Annotation + SpellMap default: SpellMap must win."""

    def __init__(self, engine: IEngine = SpellMap(Engine)) -> None:
        self.engine = engine


class PlainValue:
    """PLAIN unannotated required param."""

    def __init__(self, value) -> None:
        self.value = value


class BuiltinAnnotated:
    """Builtin annotation must classify PLAIN, not DI."""

    def __init__(self, count: int) -> None:
        self.count = count


class ListOfBuiltins:
    """list[int] must classify PLAIN, not COLLECTION."""

    def __init__(self, values: List[int]) -> None:
        self.values = values


class VarArgsSpell:
    """self/*args/**kwargs must classify IGNORE."""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs


class NeedsContract:
    """SPELL_CONTRACT via SpellContract default."""

    def __init__(self, cfg: IConfig = SpellContract(spellframe=IConfig)) -> None:
        self.cfg = cfg


class UnnormalizedBindingMap:
    """SpellMap binding_name not normalized -> warning."""

    def __init__(self, dep=SpellMap(Engine, binding_name="PRIMARY")) -> None:
        self.dep = dep


class NeedsPluginSet:
    """set[IPlugin] is an unsupported collection shape."""

    def __init__(self, plugins: set) -> None:  # annotated below via set[IPlugin]
        self.plugins = plugins


class NeedsPluginDict:
    """dict[str, IPlugin] is an unsupported collection shape."""

    def __init__(self, plugins: dict) -> None:  # annotated below via dict[str, IPlugin]
        self.plugins = plugins


# Give the collection-shape doubles genuine subscripted annotations.
NeedsPluginSet.__init__.__annotations__["plugins"] = set[IPlugin]
NeedsPluginDict.__init__.__annotations__["plugins"] = dict[str, IPlugin]


class Leaf:
    """No-dependency spell."""

    def __init__(self) -> None:
        self.ok = True


class OtherLeaf:
    """Second independent leaf."""

    def __init__(self) -> None:
        self.ok = True


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _make_spellbook() -> Spellbook:
    """Default (single-worker) spellbook."""
    spellbook = Spellbook()
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def _make_dynamic_spellbook() -> Spellbook:
    """Dynamic-mode spellbook (needed for contract sockets)."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _get_spell(spellbook: Spellbook, spell_id: str):
    """Resolve a bound spell by its versioned spell id."""
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def _param(spell, name: str):
    """Return the Phase-1 requirement record for a named parameter."""
    for parameter in spell.requirements.parameters:
        if parameter.name == name:
            return parameter
    raise AssertionError(f"parameter {name!r} not found in requirements")


def _phases_1_4(spell) -> None:
    """Run Phase 1-4 for a single spell."""
    ch.run_phase_requirements(spell)
    ch.run_phase_symbolic_graph(spell)
    ch.run_phase_local_frame(spell)
    ch.run_phase_validation(spell)


def _codes4(spell) -> set:
    """Phase-4 issue codes for a spell."""
    return {issue.code for issue in spell.validation_result_phase4.issues}


# =========================================================================== #
# Section A - Phase 1 classification (ParameterDIShape)
# =========================================================================== #
def test_phase1_plain_unannotated_param_classifies_plain() -> None:
    """An unannotated required param is PLAIN."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=PlainValue, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "value").di_shape is ParameterDIShape.PLAIN
    finally:
        spellbook.cleanup()


def test_phase1_builtin_annotation_classifies_plain() -> None:
    """A builtin annotation (int) is never a DI socket."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=BuiltinAnnotated, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "count").di_shape is ParameterDIShape.PLAIN
    finally:
        spellbook.cleanup()


def test_phase1_concrete_class_annotation_classifies_single() -> None:
    """A concrete-class annotation is SINGLE_BY_ANNOTATION."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsEngineConcrete, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "engine").di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    finally:
        spellbook.cleanup()


def test_phase1_protocol_annotation_classifies_single() -> None:
    """A protocol-frame annotation is SINGLE_BY_ANNOTATION."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "engine").di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    finally:
        spellbook.cleanup()


def test_phase1_list_frame_classifies_collection_with_element() -> None:
    """list[IPlugin] is COLLECTION_BY_ANNOTATION and carries the element type."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        param = _param(spell, "plugins")
        assert param.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
        assert param.collection_element_annotation is IPlugin
    finally:
        spellbook.cleanup()


def test_phase1_spellmap_default_classifies_spellmap() -> None:
    """A SpellMap default is SPELLMAP_DEFAULT and captures the map."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsConfigViaMap, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        param = _param(spell, "config")
        assert param.di_shape is ParameterDIShape.SPELLMAP_DEFAULT
        assert param.spellmap_default is not None
    finally:
        spellbook.cleanup()


def test_phase1_spell_contract_default_classifies_contract() -> None:
    """A SpellContract default is SPELL_CONTRACT."""
    spellbook = _make_dynamic_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsContract, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "cfg").di_shape is ParameterDIShape.SPELL_CONTRACT
    finally:
        spellbook.cleanup()


def test_phase1_self_and_varargs_classify_ignore() -> None:
    """self, *args and **kwargs are IGNORE."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=VarArgsSpell, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "args").di_shape is ParameterDIShape.IGNORE
        assert _param(spell, "kwargs").di_shape is ParameterDIShape.IGNORE
    finally:
        spellbook.cleanup()


def test_phase1_optional_single_is_marked_optional() -> None:
    """Optional[IEngine] stays SINGLE but is flagged optional."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsOptionalEngine, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        param = _param(spell, "engine")
        assert param.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
        assert param.is_optional is True
    finally:
        spellbook.cleanup()


def test_phase1_spellmap_default_beats_annotation() -> None:
    """SpellMap default wins over an inferred type annotation."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=EngineHintButMapped, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "engine").di_shape is ParameterDIShape.SPELLMAP_DEFAULT
    finally:
        spellbook.cleanup()


def test_phase1_list_of_builtins_classifies_plain() -> None:
    """list[int] is a plain param, not collection DI."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=ListOfBuiltins, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert _param(spell, "values").di_shape is ParameterDIShape.PLAIN
    finally:
        spellbook.cleanup()


def test_phase1_existing_instance_yields_no_parameters() -> None:
    """An existing-instance bind has no constructor DI requirements."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=Config(), existence=Existence.unique, permissions="create", spellframe=IConfig
        )
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        assert spell.requirements.parameters == []
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Section B - Phase 4 clean validation per shape
# =========================================================================== #
def test_phase4_leaf_is_clean_and_not_broken() -> None:
    """A no-dependency spell validates clean."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert spell.validation_result_phase4.has_errors is False
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_single_concrete_dependency_is_clean() -> None:
    """SINGLE-by-concrete-class validates clean when the provider is bound."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        consumer_id = spellbook.bind(spell=NeedsEngineConcrete, existence=Existence.unique, permissions="create")
        consumer = _get_spell(spellbook, consumer_id)
        _phases_1_4(consumer)
        assert consumer.validation_result_phase4.has_errors is False
        assert consumer.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_single_protocol_dependency_is_clean() -> None:
    """SINGLE-by-protocol validates clean when a provider is bound under the frame."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        consumer_id = spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        consumer = _get_spell(spellbook, consumer_id)
        _phases_1_4(consumer)
        assert consumer.validation_result_phase4.has_errors is False
        assert consumer.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_collection_dependency_is_clean() -> None:
    """COLLECTION validates clean with multiple implementations under the frame."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=PluginB, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="b")
        consumer_id = spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        consumer = _get_spell(spellbook, consumer_id)
        _phases_1_4(consumer)
        assert consumer.validation_result_phase4.has_errors is False
        assert consumer.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_spellmap_default_is_clean() -> None:
    """SPELLMAP_DEFAULT validates clean when the mapped target is bound."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        consumer_id = spellbook.bind(spell=NeedsConfigViaMap, existence=Existence.unique, permissions="create")
        consumer = _get_spell(spellbook, consumer_id)
        _phases_1_4(consumer)
        assert consumer.validation_result_phase4.has_errors is False
        assert consumer.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_plain_required_param_warns_but_not_broken() -> None:
    """A required plain param is a REQUIRED_HOLE warning, not a break."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=PlainValue, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "REQUIRED_HOLE" in _codes4(spell)
        assert spell.validation_result_phase4.has_errors is False
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_two_independent_leaves_are_clean() -> None:
    """Two unrelated spells each validate clean in the same book."""
    spellbook = _make_spellbook()
    try:
        a_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        b_id = spellbook.bind(spell=OtherLeaf, existence=Existence.unique, permissions="create")
        for spell_id in (a_id, b_id):
            spell = _get_spell(spellbook, spell_id)
            _phases_1_4(spell)
            assert spell.is_broken is False
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Section C - Phase 4 issue catalog (faults, collisions, characterizations)
# =========================================================================== #
def test_phase4_duplicate_spell_name_errors_and_breaks() -> None:
    """Two visible spells sharing a name is a DUPLICATE_SPELL_NAME error."""
    spellbook = _make_spellbook()

    class ContainerA:
        class Service:
            def __init__(self) -> None:
                return None

    class ContainerB:
        class Service:
            def __init__(self) -> None:
                return None

    try:
        spellbook.bind(spell=ContainerA.Service, existence=Existence.unique, permissions="create")
        target_id = spellbook.bind(spell=ContainerB.Service, existence=Existence.unique, permissions="create", binding_name="secondary")
        spell = _get_spell(spellbook, target_id)
        _phases_1_4(spell)
        assert "DUPLICATE_SPELL_NAME" in _codes4(spell)
        assert spell.is_broken is True
    finally:
        spellbook.cleanup()


def test_phase4_duplicate_name_still_errors_with_distinct_frame_and_binding() -> None:
    """
    CHARACTERIZATION (suspected fault A): duplicate bare names still error even
    when fully disambiguated by different spellframe AND binding_name, despite
    the diagnostic telling the user to do exactly that.
    """
    spellbook = _make_spellbook()

    class ContainerA:
        class Repo:
            def __init__(self) -> None:
                return None

    class ContainerB:
        class Repo:
            def __init__(self) -> None:
                return None

    try:
        spellbook.bind(spell=ContainerA.Repo, existence=Existence.unique, permissions="create", spellframe="frame_a", binding_name="one")
        target_id = spellbook.bind(spell=ContainerB.Repo, existence=Existence.unique, permissions="create", spellframe="frame_b", binding_name="two")
        spell = _get_spell(spellbook, target_id)
        _phases_1_4(spell)
        # Documents present behavior; flip this to `not in` once fault A is fixed.
        assert "DUPLICATE_SPELL_NAME" in _codes4(spell)
    finally:
        spellbook.cleanup()


def test_phase4_unsupported_set_collection_shape_errors() -> None:
    """set[IPlugin] is an UNSUPPORTED_COLLECTION_SHAPE error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)
    finally:
        spellbook.cleanup()


def test_phase4_unsupported_dict_collection_shape_errors() -> None:
    """dict[str, IPlugin] is an UNSUPPORTED_COLLECTION_SHAPE error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginDict, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)
    finally:
        spellbook.cleanup()


def test_spellmap_construction_rejects_empty_target() -> None:
    """
    A SpellMap with neither spell nor spellframe is rejected at construction, so
    the Phase-4 SPELLMAP_MISSING_TARGET code is a defensive guard that normal
    (constructor-built) SpellMaps can never reach.
    """
    with pytest.raises(ValueError):
        SpellMap(spell=None, spellframe=None)


def test_phase4_spellmap_unnormalized_binding_name_warns() -> None:
    """A non-normalized SpellMap binding_name is a warning, not an error."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        spell_id = spellbook.bind(spell=UnnormalizedBindingMap, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "SPELLMAP_BINDING_NAME_NOT_NORMALIZED" in _codes4(spell)
    finally:
        spellbook.cleanup()


def test_phase4_dangling_dependency_marks_broken() -> None:
    """A dependency id absent from the visible pool is DANGLING_DEPENDENCY -> broken."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        ch.run_phase_symbolic_graph(spell)
        ch.run_phase_local_frame(spell)
        spell.dependencies = ["missing-id"]
        ch.run_phase_validation(spell)
        assert "DANGLING_DEPENDENCY" in _codes4(spell)
        assert spell.is_broken is True
    finally:
        spellbook.cleanup()


def test_phase4_self_dependency_reports_self_and_cycle() -> None:
    """A spell depending on itself reports SELF_DEPENDENCY and CIRCULAR_DEPENDENCY."""
    spellbook = _make_spellbook()
    system = SpellValidationSystem()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        spell.dependencies = [spell_id]
        spell.dependency_graph = object()
        result = system.validate_spell(spell=spell, requirements=None, symbolic_graph=None, resolution_frame=object())
        try:
            codes = {issue.code for issue in result.issues}
            assert {"SELF_DEPENDENCY", "CIRCULAR_DEPENDENCY"} <= codes
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_phase4_missing_resolution_frame_errors() -> None:
    """A None resolution frame surfaces MISSING_RESOLUTION_FRAME."""
    spellbook = _make_spellbook()
    system = SpellValidationSystem()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        result = system.validate_spell(spell=spell, requirements=None, symbolic_graph=None, resolution_frame=None)
        try:
            assert "MISSING_RESOLUTION_FRAME" in {issue.code for issue in result.issues}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_phase4_missing_dependency_graph_warns_not_broken() -> None:
    """A missing dependency graph is a warning, not a break."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        ch.run_phase_symbolic_graph(spell)
        ch.run_phase_local_frame(spell)
        spell.dependency_graph = None
        ch.run_phase_validation(spell)
        assert "MISSING_DEPENDENCY_GRAPH" in _codes4(spell)
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_phase4_builtin_single_annotation_error_is_unreachable() -> None:
    """
    CHARACTERIZATION: DI_BUILTIN_ANNOTATION cannot fire end to end because Phase 1
    classifies a builtin-annotated param as PLAIN, so ParameterPolicy never sees a
    SINGLE builtin socket.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=BuiltinAnnotated, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "DI_BUILTIN_ANNOTATION" not in _codes4(spell)
    finally:
        spellbook.cleanup()


def test_phase4_contract_missing_provider_gates_as_warning() -> None:
    """In dynamic mode, a contract socket with no provider is a gating warning."""
    spellbook = _make_dynamic_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsContract, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "SPELL_CONTRACT_MISSING_PROVIDER" in _codes4(spell)
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Section D - Phase 6 system-level validation
# =========================================================================== #
def test_phase6_leaf_is_valid_and_conduit_state_valid() -> None:
    """A clean leaf passes Phase 6 and its conduit validity is valid."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        ch.run_phase_root_blueprints(spell, "cid")
        ch.run_phase_system_validation(spell, "cid")
        result = spell.validation_result_phase6
        assert result.is_valid is True
        state = spellbook._spell_system_states.get_conduit_resolution_state("cid")
        assert state.get_spell_validity(spell_id) is SpellValidity.valid
    finally:
        spellbook.cleanup()


def test_phase6_broken_spell_is_invalid_and_conduit_state_invalid() -> None:
    """A Phase-4-broken spell gates the lineage invalid at Phase 6."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        ch.run_phase_requirements(spell)
        ch.run_phase_symbolic_graph(spell)
        ch.run_phase_local_frame(spell)
        spell.dependencies = ["missing-id"]
        ch.run_phase_validation(spell)
        ch.run_phase_root_blueprints(spell, "cid")
        ch.run_phase_system_validation(spell, "cid")
        result = spell.validation_result_phase6
        assert result.is_valid is False
        assert "broken_spell_in_dag" in {diag.code for diag in result.errors}
        state = spellbook._spell_system_states.get_conduit_resolution_state("cid")
        assert state.get_spell_validity(spell_id) is SpellValidity.invalid
    finally:
        spellbook.cleanup()


def test_phase6_cycle_raises_at_root_blueprints() -> None:
    """A two-spell cycle raises during Phase-5 blueprint construction."""
    spellbook = _make_spellbook()

    class Alpha:
        def __init__(self, beta: Beta) -> None:
            self.beta = beta

    class Beta:
        def __init__(self, alpha: Alpha) -> None:
            self.alpha = alpha

    try:
        alpha_id = spellbook.bind(spell=Alpha, existence=Existence.unique, permissions="create", spellframe="Alpha")
        beta_id = spellbook.bind(spell=Beta, existence=Existence.unique, permissions="create", spellframe="Beta")
        for spell_id in (alpha_id, beta_id):
            spell = _get_spell(spellbook, spell_id)
            _phases_1_4(spell)
        with pytest.raises(RuntimeError, match="Cycle detected"):
            ch.run_phase_root_blueprints(_get_spell(spellbook, alpha_id), "cid")
    finally:
        spellbook.cleanup()


def test_phase6_consumer_chain_is_valid() -> None:
    """A consumer + its bound dependency both pass Phase 6."""
    spellbook = _make_spellbook()
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        consumer_id = spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        for spell_id in (engine_id, consumer_id):
            _phases_1_4(_get_spell(spellbook, spell_id))
        consumer = _get_spell(spellbook, consumer_id)
        ch.run_phase_root_blueprints(consumer, "cid")
        ch.run_phase_system_validation(consumer, "cid")
        assert consumer.validation_result_phase6.is_valid is True
    finally:
        spellbook.cleanup()


def test_phase6_reports_missing_index_node() -> None:
    """Removing a dependency node from the Phase-5 index surfaces missing_index_node."""
    spellbook = _make_spellbook()
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        consumer_id = spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        for spell_id in (engine_id, consumer_id):
            _phases_1_4(_get_spell(spellbook, spell_id))
        consumer = _get_spell(spellbook, consumer_id)
        ch.run_phase_root_blueprints(consumer, "cid")
        index = consumer._compiler_artifact._spell_system_index_phase5
        index.nodes.pop(engine_id)
        ch.run_phase_system_validation(consumer, "cid")
        codes = {diag.code for diag in consumer.validation_result_phase6.errors}
        assert "missing_index_node" in codes
        assert "root_not_viable" in codes
    finally:
        spellbook.cleanup()


def test_phase6_all_nodes_validated_has_no_missing_phase4() -> None:
    """When every node ran Phase 4, Phase 6 does not report missing_phase4_validation."""
    spellbook = _make_spellbook()
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        consumer_id = spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        for spell_id in (engine_id, consumer_id):
            _phases_1_4(_get_spell(spellbook, spell_id))
        consumer = _get_spell(spellbook, consumer_id)
        ch.run_phase_root_blueprints(consumer, "cid")
        ch.run_phase_system_validation(consumer, "cid")
        codes = {diag.code for diag in consumer.validation_result_phase6.errors}
        assert "missing_phase4_validation" not in codes
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Section E - End-to-end conjure + meld resolution
# =========================================================================== #
def test_e2e_meld_by_class_resolves_instance() -> None:
    """meld(spell=Class) returns a constructed instance."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=Engine)
        assert isinstance(instance, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_meld_by_spell_id_resolves_instance() -> None:
    """meld(spell=<spell_id>) returns a constructed instance."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=engine_id)
        assert isinstance(instance, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_meld_by_protocol_frame_resolves_instance() -> None:
    """meld(spellframe=Protocol) resolves the single provider bound under it."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spellframe=IEngine)
        assert isinstance(instance, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_meld_by_spell_name_resolves_instance() -> None:
    """meld(spell_name="Engine") resolves the default binding by name."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell_name="Engine")
        assert isinstance(instance, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_meld_collection_injects_all_implementations() -> None:
    """A list[IPlugin] consumer receives every implementation bound under the frame."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=PluginB, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="b")
        spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NeedsPlugins)
        assert len(instance.plugins) == 2
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_meld_spellmap_default_resolves_dependency() -> None:
    """A SpellMap-defaulted param is resolved to its mapped target at meld."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=NeedsConfigViaMap, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NeedsConfigViaMap)
        assert isinstance(instance.config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_existence_unique_reuses_instance() -> None:
    """Unique existence reuses one instance across melds within a conduit."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        first = conduit.meld(spell=engine_id)
        second = conduit.meld(spell=engine_id)
        assert first is second
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_existence_many_creates_new_instances() -> None:
    """Many existence produces a fresh instance per meld."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.many, permissions="create")
        conduit = spellbook.conjure(name="root")
        first = conduit.meld(spell=engine_id)
        second = conduit.meld(spell=engine_id)
        assert first is not second
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2e_conjure_raises_validation_error_on_cycle() -> None:
    """A dependency cycle blocks conjure with SpellbookValidationError."""
    spellbook = _make_spellbook()

    class Alpha:
        def __init__(self, beta: Beta) -> None:
            self.beta = beta

    class Beta:
        def __init__(self, alpha: Alpha) -> None:
            self.alpha = alpha

    try:
        spellbook.bind(spell=Alpha, existence=Existence.unique, permissions="create", spellframe="Alpha")
        spellbook.bind(spell=Beta, existence=Existence.unique, permissions="create", spellframe="Beta")
        with pytest.raises(SpellbookValidationError):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()
