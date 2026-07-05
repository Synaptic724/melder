"""
Aggressive error matrix - throw malformed / edge input at every resolution path.

Purpose:
    For each of the ~17 resolution ways, assert that bad input is *rejected*
    (raised or reported), never silently accepted. Grouped by where the failure
    surfaces: meld entry, bind eligibility, and conjure/compile.

Convention:
    - "should raise" tests use `pytest.raises(Exception)` (broad on purpose - the
      goal is to confirm rejection); the expected specific type is noted in the
      docstring so it can be tightened after a real run.
    - Negative-control tests assert an operation SUCCEEDS (warnings must not block).

NOTE:
    Run on Python 3.14t (melder relies on 3.14 deferred annotations).
"""
from __future__ import annotations

import json
from typing import List, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
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


# --------------------------------------------------------------------------- #
# Doubles
# --------------------------------------------------------------------------- #
class IEngine(Protocol):
    """Single-provider frame."""


class IPlugin(Protocol):
    """Collection frame."""


class IHasPing(Protocol):
    """Method-bearing protocol for structural bind checks."""

    def ping(self) -> str: ...


class Engine:
    def __init__(self) -> None:
        self.kind = "engine"


class AltEngine:
    def __init__(self) -> None:
        self.kind = "alt"


class Config:
    def __init__(self) -> None:
        self.name = "cfg"


class UnboundThing:
    """Never bound; used as an unresolvable dependency target."""

    def __init__(self) -> None:
        self.x = 1


class UnboundConfig:
    """Never bound; used as an unresolvable SpellMap target."""

    def __init__(self) -> None:
        self.y = 2


class NoPing:
    """Does not satisfy IHasPing (no `ping`)."""

    def __init__(self) -> None:
        self.ok = True


class UsesUnbound:
    def __init__(self, dep: UnboundThing) -> None:
        self.dep = dep


class UsesEngineProtocol:
    def __init__(self, engine: IEngine) -> None:
        self.engine = engine


class UsesMissingSpellMap:
    def __init__(self, dep=SpellMap(UnboundConfig)) -> None:
        self.dep = dep


class NeedsPluginSet:
    def __init__(self, plugins: set) -> None:
        self.plugins = plugins


class PlainValue:
    def __init__(self, value) -> None:
        self.value = value


NeedsPluginSet.__init__.__annotations__["plugins"] = set[IPlugin]


def _make_spellbook() -> Spellbook:
    spellbook = Spellbook()
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


# =========================================================================== #
# Section 1 - meld entry-point errors
# =========================================================================== #
def test_meld_with_no_arguments_raises() -> None:
    """meld() with none of spell/spell_name/spellframe must raise (ValueError)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld()
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_unknown_spell_id_raises() -> None:
    """meld(spell=<garbage id>) must raise (KeyError)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spell="0" * 64)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_unknown_spell_name_raises() -> None:
    """meld(spell_name="Nope") must raise (KeyError)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spell_name="DoesNotExist")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_unbound_class_raises() -> None:
    """meld(spell=Class) for an unbound class must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spell=UnboundThing)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_unbound_protocol_frame_raises() -> None:
    """meld(spellframe=Protocol) with nothing bound under it must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spellframe=IEngine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_unknown_string_frame_raises() -> None:
    """meld(spellframe="nope") must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spellframe="totally_unbound_frame")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_wrong_binding_name_raises() -> None:
    """meld(spell=Class, binding_name=<wrong>) must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="primary")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spell=Engine, binding_name="secondary")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_meld_invalid_override_type_raises() -> None:
    """meld(spell=..., spell_override=<not dict/list/tuple>) must raise (TypeError)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(Exception):
            conduit.meld(spell=engine_id, spell_override=12345)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# Section 2 - bind eligibility errors
# =========================================================================== #
def test_bind_module_raises() -> None:
    """Binding a module object must raise (E1)."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=json, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_bind_protocol_raises() -> None:
    """Binding a Protocol type (a frame, not a spell) must raise (E1)."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=IEngine, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_bind_lambda_without_binding_name_raises() -> None:
    """Binding a lambda without a binding_name must raise."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=lambda: Engine(), existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_bind_existing_instance_with_many_existence_raises() -> None:
    """Binding an existing instance with non-unique existence must raise."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=Config(), existence=Existence.many, permissions="create")
    finally:
        spellbook.cleanup()


def test_bind_class_missing_protocol_member_raises() -> None:
    """Binding a class that doesn't satisfy a Protocol frame must raise."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=NoPing, existence=Existence.unique, permissions="create", spellframe=IHasPing)
    finally:
        spellbook.cleanup()


def test_bind_duplicate_frame_binding_key_raises() -> None:
    """Two different spells under the same (frame_key, bind_key) must raise (RuntimeError)."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe="dup")
        with pytest.raises(Exception):
            spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe="dup")
    finally:
        spellbook.cleanup()


# =========================================================================== #
# Section 3 - conjure / compile faults
# =========================================================================== #
def test_conjure_with_cycle_raises() -> None:
    """A dependency cycle must block conjure (SpellbookValidationError)."""
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
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_with_unresolvable_dependency_raises() -> None:
    """A consumer depending on an unbound type must fail to conjure."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=UsesUnbound, existence=Existence.unique, permissions="create")
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_with_duplicate_spell_name_raises() -> None:
    """Duplicate visible spell_name (DUPLICATE_SPELL_NAME error) must block conjure."""
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
        spellbook.bind(spell=ContainerB.Service, existence=Existence.unique, permissions="create", binding_name="secondary")
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_with_unsupported_collection_shape_raises() -> None:
    """A set[IPlugin] DI annotation (UNSUPPORTED_COLLECTION_SHAPE) must block conjure."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_with_ambiguous_frame_di_raises() -> None:
    """Two default-binding providers under one frame make single DI ambiguous."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
            spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe=IEngine)
            spellbook.bind(spell=UsesEngineProtocol, existence=Existence.unique, permissions="create")
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_with_unresolvable_spellmap_default_raises() -> None:
    """A SpellMap default whose target is unbound must fail at Phase-3 resolution."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=UsesMissingSpellMap, existence=Existence.unique, permissions="create")
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_conjure_succeeds_with_required_hole_warning() -> None:
    """NEGATIVE CONTROL: a required plain param is a warning and must NOT block conjure."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PlainValue, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit is not None
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_conjure_leaf_only_succeeds() -> None:
    """NEGATIVE CONTROL: a clean leaf spell must conjure without error."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit is not None
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()
