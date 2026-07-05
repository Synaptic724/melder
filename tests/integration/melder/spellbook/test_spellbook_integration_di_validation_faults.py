"""
Fault suite for the two validation bugs found in the compiler read-through.

Fault A - DuplicateSpellNameStrategy is over-strict:
    It keys collisions on the bare `spell_name` and ignores spellframe /
    binding_name, so fully disambiguated same-name spells still error. This
    contradicts ticket A6 (ambiguity keyed by (frame_key, bind_key)) and the
    strategy's own remediation message.

Fault B - AnnotationShapeGuardStrategy ignores `di_shape`:
    It validates the raw annotation without consulting the Phase-1 classification,
    so a param overridden by an explicit SpellMap (or a plain list[int]) still
    draws annotation-shape diagnostics.

Convention:
    - `*_control_*` tests assert *correct current* behavior and should PASS today.
    - `*_fault_*` tests assert the *intended fixed* behavior and are marked xfail
      (strict=False) so they document the target and flip to XPASS once fixed.

NOTE:
    Run on Python 3.14t (melder relies on 3.14 deferred annotations).
"""
from __future__ import annotations

from typing import List, Protocol

import pytest

import tests.component.melder.spellbook.compiler_test_helpers as ch

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def _reset_aether_singleton() -> None:
    """Fresh Aether singleton per test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class IPlugin(Protocol):
    """Collection frame for the Fault-B doubles."""


class Config:
    def __init__(self) -> None:
        self.name = "cfg"


def _make_spellbook() -> Spellbook:
    spellbook = Spellbook()
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell(spellbook: Spellbook, spell_id: str):
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def _param(spell, name: str):
    for parameter in spell.requirements.parameters:
        if parameter.name == name:
            return parameter
    raise AssertionError(f"parameter {name!r} not found")


def _phases_1_4(spell) -> None:
    ch.run_phase_requirements(spell)
    ch.run_phase_symbolic_graph(spell)
    ch.run_phase_local_frame(spell)
    ch.run_phase_validation(spell)


def _codes4(spell) -> set:
    return {issue.code for issue in spell.validation_result_phase4.issues}


# =========================================================================== #
# Fault A - duplicate-name guard ignores frame/binding disambiguation
# =========================================================================== #
def test_fault_a_control_bare_duplicate_names_error() -> None:
    """CONTROL (should pass): two same-name spells with no discriminator error."""
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
        spellbook.bind(spell=ContainerA.Repo, existence=Existence.unique, permissions="create")
        target_id = spellbook.bind(spell=ContainerB.Repo, existence=Existence.unique, permissions="create", binding_name="secondary")
        spell = _get_spell(spellbook, target_id)
        _phases_1_4(spell)
        assert "DUPLICATE_SPELL_NAME" in _codes4(spell)
    finally:
        spellbook.cleanup()


@pytest.mark.xfail(reason="Fault A: guard ignores distinct spellframes", strict=False)
def test_fault_a_distinct_spellframes_should_not_error() -> None:
    """FAULT: same name under different Protocol/string frames should NOT be ambiguous."""
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
        spellbook.bind(spell=ContainerA.Repo, existence=Existence.unique, permissions="create", spellframe="users")
        target_id = spellbook.bind(spell=ContainerB.Repo, existence=Existence.unique, permissions="create", spellframe="orders")
        spell = _get_spell(spellbook, target_id)
        _phases_1_4(spell)
        assert "DUPLICATE_SPELL_NAME" not in _codes4(spell)
    finally:
        spellbook.cleanup()


@pytest.mark.xfail(reason="Fault A: remediation (distinct binding_name) does not clear the error", strict=False)
def test_fault_a_distinct_binding_names_should_clear_error() -> None:
    """FAULT: following the diagnostic's own advice (distinct binding_name) should clear it."""
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
        spellbook.bind(spell=ContainerA.Repo, existence=Existence.unique, permissions="create", binding_name="one")
        target_id = spellbook.bind(spell=ContainerB.Repo, existence=Existence.unique, permissions="create", binding_name="two")
        spell = _get_spell(spellbook, target_id)
        _phases_1_4(spell)
        assert "DUPLICATE_SPELL_NAME" not in _codes4(spell)
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Fault B - annotation-shape guard ignores di_shape precedence
# =========================================================================== #
class GenuineUnsupportedSet:
    """A real set[IPlugin] DI annotation (no SpellMap): must be flagged."""

    def __init__(self, plugins: set) -> None:
        self.plugins = plugins


class MappedButSetAnnotated:
    """SpellMap default overrides the annotation; the set[] shape must be ignored."""

    def __init__(self, plugins=SpellMap(Config)) -> None:
        self.plugins = plugins


class PlainListOfInts:
    """A plain list[int] config param: not DI, must not draw a DI warning."""

    def __init__(self, values: List[int]) -> None:
        self.values = values


GenuineUnsupportedSet.__init__.__annotations__["plugins"] = set[IPlugin]
MappedButSetAnnotated.__init__.__annotations__["plugins"] = set[IPlugin]


def test_fault_b_control_genuine_set_shape_errors() -> None:
    """CONTROL (should pass): a real set[IPlugin] DI annotation is flagged."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=GenuineUnsupportedSet, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)
    finally:
        spellbook.cleanup()


@pytest.mark.xfail(reason="Fault B: annotation guard ignores SPELLMAP_DEFAULT di_shape", strict=False)
def test_fault_b_spellmap_override_should_suppress_shape_error() -> None:
    """FAULT: when a SpellMap default wins, the annotation's shape must not be judged."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        spell_id = spellbook.bind(spell=MappedButSetAnnotated, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert _param(spell, "plugins").di_shape is ParameterDIShape.SPELLMAP_DEFAULT
        assert "UNSUPPORTED_COLLECTION_SHAPE" not in _codes4(spell)
    finally:
        spellbook.cleanup()


@pytest.mark.xfail(reason="Fault B: plain list[int] still draws a DI annotation warning", strict=False)
def test_fault_b_plain_list_of_ints_should_not_warn() -> None:
    """FAULT: a PLAIN list[int] param must not draw LIST_ELEMENT_NOT_DI_TARGET."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=PlainListOfInts, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert _param(spell, "values").di_shape is ParameterDIShape.PLAIN
        assert "LIST_ELEMENT_NOT_DI_TARGET" not in _codes4(spell)
    finally:
        spellbook.cleanup()
