"""
One focused end-to-end test per DI resolution-contract item.

Purpose:
    Cover each of the 17 named ticket items (A1-A6, B1-B6, C1, D1-D2, E1-E2,
    G, H) with a single, direct integration test that binds real spells, conjures
    a conduit, and exercises the corresponding resolution/validation behavior.

Contract:
    - Uses a real Spellbook/Conduit (no stubs).
    - Each test's docstring names the ticket item it covers.
    - "Must reject" items assert a raised error at bind/conjure/meld time.

NOTE:
    Melder targets Python 3.14t; run this suite on 3.14t (it will not import
    under < 3.14 due to deferred-annotation reliance).
"""
from __future__ import annotations

import json
from typing import List, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


# --------------------------------------------------------------------------- #
# Isolation
# --------------------------------------------------------------------------- #
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


class IConfig(Protocol):
    """SpellMap-target frame."""


class Engine:
    def __init__(self) -> None:
        self.kind = "engine"


class AltEngine:
    def __init__(self) -> None:
        self.kind = "alt"


class PluginA:
    def __init__(self) -> None:
        self.tag = "a"


class PluginB:
    def __init__(self) -> None:
        self.tag = "b"


class Config:
    def __init__(self) -> None:
        self.name = "cfg"


class NamedService:
    def __init__(self, name: str) -> None:
        self.name = name


class Widget:
    def __init__(self, tag: str = "made") -> None:
        self.tag = tag


def make_widget() -> Widget:
    """Factory (method/lambda) spell for B5."""
    return Widget("factory")


class UsesEngineConcrete:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine


class UsesEngineProtocol:
    def __init__(self, engine: IEngine) -> None:
        self.engine = engine


class UsesPlugins:
    def __init__(self, plugins: List[IPlugin]) -> None:
        self.plugins = plugins


class UsesConfigMap:
    def __init__(self, config=SpellMap(Config)) -> None:
        self.config = config


class UsesConfigMapBinding:
    def __init__(self, config=SpellMap(Config, binding_name="primary")) -> None:
        self.config = config


class UsesConfigFrameOnly:
    def __init__(self, config=SpellMap(spell=None, spellframe=IConfig)) -> None:
        self.config = config


class UsesConfigFrameString:
    def __init__(self, config=SpellMap(spell=None, spellframe="configframe")) -> None:
        self.config = config


class UsesFactory:
    def __init__(self, widget=SpellMap(make_widget)) -> None:
        self.widget = widget


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _make_spellbook() -> Spellbook:
    spellbook = Spellbook()
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


# =========================================================================== #
# A - root meld entry modes
# =========================================================================== #
def test_a1_meld_by_spell_id() -> None:
    """A1: meld(spell=<spell_id>) returns an instance."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell=engine_id), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a2_meld_by_class_with_binding_name() -> None:
    """A2: meld(spell=Class, binding_name=...) resolves the named binding."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="primary")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell=Engine, binding_name="primary"), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a3_meld_by_protocol_spellframe() -> None:
    """A3: meld(spellframe=Protocol) resolves the provider bound under it."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spellframe=IEngine), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a5_root_spell_override_applies_kwargs() -> None:
    """A5: meld(spell=Class, spell_override={...}) forwards kwargs to the constructor."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=NamedService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NamedService, spell_override={"name": "overridden"})
        assert instance.name == "overridden"
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a6_meld_by_spell_name() -> None:
    """A6: meld(spell_name="Engine") resolves by human-readable name."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell_name="Engine"), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# B - constructor DI shapes
# =========================================================================== #
def test_b1_type_hint_concrete_class_injects_dependency() -> None:
    """B1: `dep: Engine` injects the concrete provider."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=UsesEngineConcrete, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesEngineConcrete)
        assert isinstance(instance.engine, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b2_type_hint_protocol_injects_dependency() -> None:
    """B2: `dep: IEngine` injects the provider bound under the frame."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        spellbook.bind(spell=UsesEngineProtocol, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesEngineProtocol)
        assert isinstance(instance.engine, Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b3_spellmap_default_explicit_class_injects() -> None:
    """B3: a SpellMap(Class) default resolves the mapped dependency."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=UsesConfigMap, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesConfigMap)
        assert isinstance(instance.config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b5_method_spell_via_spellmap_factory() -> None:
    """B5: a SpellMap(function) default resolves the factory's product."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=make_widget, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=UsesFactory, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesFactory)
        assert isinstance(instance.widget, Widget)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b6_existing_instance_frame_resolves_same_object() -> None:
    """B6: an existing-instance bind resolves to the exact stored object."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        config_instance = Config()
        spellbook.bind(spell=config_instance, existence=Existence.unique, permissions="create", spellframe=IConfig)
        conduit = spellbook.conjure(name="root")
        assert conduit.meld(spellframe=IConfig) is config_instance
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# C - collection DI
# =========================================================================== #
def test_c1_collection_list_frame_injects_all() -> None:
    """C1: list[IPlugin] receives every implementation bound under the frame."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=PluginB, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="b")
        spellbook.bind(spell=UsesPlugins, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesPlugins)
        assert len(instance.plugins) == 2
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# D - SpellMap capabilities
# =========================================================================== #
def test_d1_spellmap_explicit_class_with_binding_name() -> None:
    """D1: SpellMap(Class, binding_name=...) targets a specific binding."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", binding_name="primary")
        spellbook.bind(spell=UsesConfigMapBinding, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesConfigMapBinding)
        assert isinstance(instance.config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_d2_spellmap_frame_only_protocol() -> None:
    """D2: SpellMap(spell=None, spellframe=Protocol) resolves via frame only."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", spellframe=IConfig)
        spellbook.bind(spell=UsesConfigFrameOnly, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesConfigFrameOnly)
        assert isinstance(instance.config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_d2_spellmap_frame_only_string() -> None:
    """D2: SpellMap(spell=None, spellframe="<string>") resolves via string frame."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", spellframe="configframe")
        spellbook.bind(spell=UsesConfigFrameString, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesConfigFrameString)
        assert isinstance(instance.config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# E - eligibility & uniqueness
# =========================================================================== #
def test_e1_bind_rejects_module_as_spell() -> None:
    """E1: a module is not a valid spell target."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=json, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_e1_bind_rejects_protocol_as_spell() -> None:
    """E1: a Protocol type is a frame, not a bindable spell."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=IEngine, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_e2_ambiguous_frame_di_is_rejected() -> None:
    """E2: two default-binding providers under one frame make single DI ambiguous."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        with pytest.raises(Exception):
            spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
            spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe=IEngine)
            spellbook.bind(spell=UsesEngineProtocol, existence=Existence.unique, permissions="create")
            conduit = spellbook.conjure(name="root")
            conduit.meld(spell=UsesEngineProtocol)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# G - existence vs resolution separation
# =========================================================================== #
def test_g_unique_existence_reuses_instance() -> None:
    """G: unique existence returns the same instance across melds."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit.meld(spell=engine_id) is conduit.meld(spell=engine_id)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_g_many_existence_creates_new_instances() -> None:
    """G: many existence returns a fresh instance per meld."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.many, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit.meld(spell=engine_id) is not conduit.meld(spell=engine_id)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# H - spellframe types
# =========================================================================== #
def test_h_protocol_spellframe_resolves() -> None:
    """H: a Protocol spellframe resolves as a contract key."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spellframe=IEngine), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_h_string_spellframe_resolves() -> None:
    """H: a string spellframe resolves as a logical category key."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe="engines")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spellframe="engines"), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()
