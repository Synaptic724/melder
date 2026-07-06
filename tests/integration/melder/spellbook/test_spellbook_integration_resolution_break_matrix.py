"""
Adversarial break-matrix: try to break every resolution path in new ways.

Purpose:
    Beyond the first error matrix, throw a wider spread of malformed, hostile,
    and boundary input at all ~17 resolution forms (A1-H). Two flavors:
    "must reject" tests (bad input has to raise) and "silent-accept hunters"
    (input that should be rejected or produce an exact result - a wrong result
    is a real defect the assertion will catch).

Contract:
    - Real Spellbook/Conduit wiring; no stubs.
    - `pytest.raises(RESOLUTION_ERRORS)` asserts a *known* resolution error, so a
      stray AttributeError/NameError from a bad test fails loudly instead of
      masquerading as a pass.
    - Every test names the form and the adversarial vector it probes.

NOTE:
    Python 3.14t only (deferred annotations are relied upon; no
    `from __future__ import annotations` per profile policy).
"""
from typing import List, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)


RESOLUTION_ERRORS = (
    KeyError,
    ValueError,
    TypeError,
    RuntimeError,
    LookupError,
    SpellbookValidationError,
    PhaseExecutionError,
)


@pytest.fixture(autouse=True)
def _reset_aether_singleton() -> None:
    """Give each test a clean Aether singleton."""
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
    """Concrete engine provider."""

    def __init__(self) -> None:
        self.kind = "engine"


class AltEngine:
    """Second engine provider for collision/ambiguity."""

    def __init__(self) -> None:
        self.kind = "alt"


class Config:
    """Config provider."""

    def __init__(self) -> None:
        self.name = "cfg"


class PluginA:
    """First IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "a"


class PluginB:
    """Second IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "b"


class PluginC:
    """Third IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "c"


class NamedService:
    """Requires a plain `name` (override target)."""

    def __init__(self, name: str) -> None:
        self.name = name


class NeedsEngineConcrete:
    """B1 consumer (concrete hint)."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine


class NeedsEngineProtocol:
    """B2 consumer (protocol hint)."""

    def __init__(self, engine: IEngine) -> None:
        self.engine = engine


class NeedsConfigViaMap:
    """B3 consumer (SpellMap default)."""

    def __init__(self, config: object = SpellMap(Config)) -> None:
        self.config = config


class NeedsPlugins:
    """C1 consumer (collection)."""

    def __init__(self, plugins: List[IPlugin]) -> None:
        self.plugins = plugins


class NeedsEngineList:
    """C1 consumer over a concrete element type."""

    def __init__(self, engines: List[Engine]) -> None:
        self.engines = engines


def boom_factory() -> Engine:
    """B5 factory whose body raises to test error propagation through meld."""
    raise ValueError("boom-from-factory")


def _make_spellbook() -> Spellbook:
    """
    Default single-worker spellbook with system caching disabled.

    This suite tests RESOLUTION behavior, not the conjure cache. Every test
    conjures (frame=default, name="root") and several bind IDENTICAL
    module-level class sources (NeedsPlugins, Config, ...) into DIFFERENT
    pool compositions, so leaving caching on lets sibling tests replay each
    other's cached manifests out of the shared frame/conduit bundle. With
    caching off every conjure compiles from scratch, tests are
    order-independent, and no cache artifacts are written (same posture the
    cache suite's non-cache arms and test_aether use).
    """
    spellbook = Spellbook()
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return spellbook


# =========================================================================== #
# A1 / A2 - spell_id and class entry
# =========================================================================== #
def test_a1_empty_string_spell_id_raises() -> None:
    """A1: an empty spell_id must be rejected, not resolved to anything."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell="")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a1_none_spell_raises() -> None:
    """A1/A2: meld(spell=None) must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=None)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a1_wellformed_but_unbound_sha_raises() -> None:
    """A1: a syntactically valid but unbound 64-hex id must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell="a" * 64)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a1_meld_after_conduit_cleanup_raises() -> None:
    """A1: melding through a cleaned conduit must raise (no use-after-clean)."""
    spellbook = _make_spellbook()
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        conduit.cleanup()
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=engine_id)
    finally:
        spellbook.cleanup()


def test_a2_garbage_object_as_spell_raises() -> None:
    """A2: a non-class, non-id object (int) must be rejected."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=42)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a2_class_bound_only_under_binding_name_default_lookup_raises() -> None:
    """A2: a class bound only under a binding_name is not resolvable by default."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="named")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# A5 - overrides
# =========================================================================== #
def test_a5_override_unknown_kwarg_is_rejected() -> None:
    """A5 hunter: an override key that isn't a constructor param must not be silently dropped."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=Engine, spell_override={"not_a_param": 1})
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a5_override_too_many_positional_args_raises() -> None:
    """A5: a positional override longer than the signature must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=Engine, spell_override=[1, 2, 3, 4])
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a5_override_supplies_required_plain_param() -> None:
    """A5 behavior: a dict override fills a required plain param."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=NamedService, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NamedService, spell_override={"name": "explicit"})
        assert instance.name == "explicit"
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a5_override_wins_over_injected_dependency() -> None:
    """A5 precedence: an explicit override replaces the value DI would inject."""
    spellbook = _make_spellbook()
    conduit = None
    sentinel = Engine()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IEngine)
        spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NeedsEngineProtocol, spell_override={"engine": sentinel})
        assert instance.engine is sentinel
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a5_empty_dict_override_falls_back_to_normal_resolution() -> None:
    """A5 behavior: an empty override is a no-op and normal resolution succeeds."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell=Engine, spell_override={}), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# A6 - spell_name
# =========================================================================== #
def test_a6_empty_spell_name_raises() -> None:
    """A6: an empty spell_name must raise, not resolve arbitrarily."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell_name="")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a6_class_object_as_spell_name_is_leniently_resolved() -> None:
    """A6 characterization: a class passed as spell_name is folded to its frame key and resolves (loose typing on spell_name; not a hard error)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell_name=Engine), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a6_spell_name_is_case_insensitive() -> None:
    """A6 behavior: name resolution is case-folded (frame keys are lowercased)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell_name="ENGINE"), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_a6_spell_name_with_wrong_binding_raises() -> None:
    """A6: a name with a binding_name that was never bound must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="primary")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell_name="Engine", binding_name="secondary")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# B1 / B2 - constructor type-hint DI
# =========================================================================== #
def test_b1_concrete_dependency_unbound_fails_conjure() -> None:
    """B1: a concrete dependency that is never bound must fail conjure."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsEngineConcrete, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_b1_dependency_only_under_binding_defers_and_conjures() -> None:
    """B1 characterization: a provider bound only under a binding_name leaves the bare hint unsatisfied, but that is a warning - conjure still succeeds (the failure is deferred to meld)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="named")
        spellbook.bind(spell=NeedsEngineConcrete, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit is not None
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b1_deep_chain_missing_leaf_fails_conjure() -> None:
    """B1: a 3-deep chain with an unbound leaf must fail conjure."""
    spellbook = _make_spellbook()

    class Leaf:
        def __init__(self, engine: Engine) -> None:
            self.engine = engine

    class Mid:
        def __init__(self, leaf: Leaf) -> None:
            self.leaf = leaf

    try:
        # Engine intentionally NOT bound -> the leaf can't resolve.
        spellbook.bind(spell=Leaf, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=Mid, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_b2_provider_under_different_frame_fails_conjure() -> None:
    """B2: a provider registered under a different frame can't satisfy IEngine."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_b2_provider_bound_under_own_class_only_fails_frame_hint() -> None:
    """B2: a provider bound without the frame key can't satisfy the protocol hint."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=NeedsEngineProtocol, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


# =========================================================================== #
# B3 / B5 - SpellMap default and callable spells
# =========================================================================== #
def test_b3_spellmap_matches_target_under_any_binding() -> None:
    """B3 characterization: SpellMap(Class) with no binding_name matches that class under ANY binding, so a binding-only registration still resolves."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", binding_name="named")
        spellbook.bind(spell=NeedsConfigViaMap, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spell=NeedsConfigViaMap).config, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b3_override_beats_spellmap_default() -> None:
    """B3 precedence: an explicit override replaces a SpellMap-default value."""
    spellbook = _make_spellbook()
    conduit = None
    sentinel = Config()
    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=NeedsConfigViaMap, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NeedsConfigViaMap, spell_override={"config": sentinel})
        assert instance.config is sentinel
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b5_factory_error_propagates_through_meld() -> None:
    """B5: an exception inside a factory spell must propagate out of meld."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=boom_factory, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spell=boom_factory)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b5_lambda_with_binding_name_resolves_output() -> None:
    """B5 behavior: a lambda bound under a string frame + binding resolves to its output."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(
            spell=lambda: Engine(),
            existence=Existence.unique,
            permissions="create",
            spellframe="factories",
            binding_name="engine",
        )
        conduit = spellbook.conjure(name="root")
        assert isinstance(conduit.meld(spellframe="factories", binding_name="engine"), Engine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# B6 - existing instances
# =========================================================================== #
def test_b6_existing_instance_resolves_same_object_by_frame() -> None:
    """B6 behavior: an existing-instance bind returns the exact stored object."""
    spellbook = _make_spellbook()
    conduit = None
    instance = Config()
    try:
        spellbook.bind(spell=instance, existence=Existence.unique, permissions="create", spellframe=IConfig)
        conduit = spellbook.conjure(name="root")
        assert conduit.meld(spellframe=IConfig) is instance
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_b6_two_existing_instances_same_frame_default_collide() -> None:
    """B6/E2: two existing instances under the same frame+default binding must collide at bind."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Config(), existence=Existence.unique, permissions="create", spellframe=IConfig)
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=Config(), existence=Existence.unique, permissions="create", spellframe=IConfig)
    finally:
        spellbook.cleanup()


# =========================================================================== #
# C1 - collection DI
# =========================================================================== #
def test_c1_zero_implementations_fails_conjure() -> None:
    """C1: in an AUTOMATIC book a required collection with no providers fails fast at conjure via the phase-6 EmptyCollectionStrategy (composition is final, so the socket can never be satisfied; dynamic books instead warn and inject [] pending contracts)."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_c1_single_implementation_injects_one() -> None:
    """C1: exactly one provider yields a one-element list."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert len(conduit.meld(spell=NeedsPlugins).plugins) == 1
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_c1_three_implementations_injects_all_three() -> None:
    """C1: three providers under one frame all get injected."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=PluginB, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="b")
        spellbook.bind(spell=PluginC, existence=Existence.unique, permissions="create", spellframe=IPlugin, binding_name="c")
        spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert len(conduit.meld(spell=NeedsPlugins).plugins) == 3
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_c1_mixed_existence_still_injects_all() -> None:
    """C1: providers with different existence (unique + many) still all appear."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.unique, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=PluginB, existence=Existence.many, permissions="create", spellframe=IPlugin, binding_name="b")
        spellbook.bind(spell=NeedsPlugins, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert len(conduit.meld(spell=NeedsPlugins).plugins) == 2
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_c1_collection_over_concrete_element_type() -> None:
    """C1 characterization: list[Engine] over a concrete element resolves the bound engine(s)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe=Engine)
        spellbook.bind(spell=NeedsEngineList, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert len(conduit.meld(spell=NeedsEngineList).engines) == 1
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_c1_single_many_existence_member_injects_one_element_list() -> None:
    """C1 regression: a lone many-existence provider still injects a one-element list (many_only lane)."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=PluginA, existence=Existence.many, permissions="create", spellframe=IPlugin)
        spellbook.bind(spell=NeedsPlugins, existence=Existence.many, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=NeedsPlugins)
        assert isinstance(instance.plugins, list)
        assert len(instance.plugins) == 1
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# D1 / D2 - SpellMap capabilities
# =========================================================================== #
def test_d2_frame_only_unbound_frame_fails_conjure() -> None:
    """D2: SpellMap(spell=None, spellframe=<unbound>) must fail to resolve."""
    spellbook = _make_spellbook()

    class UsesUnboundFrameMap:
        def __init__(self, cfg: object = SpellMap(spell=None, spellframe="never_bound_frame")) -> None:
            self.cfg = cfg

    try:
        spellbook.bind(spell=UsesUnboundFrameMap, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_d1_spellmap_wrong_binding_fails_conjure() -> None:
    """D1: SpellMap(Class, binding_name=<wrong>) must fail to resolve."""
    spellbook = _make_spellbook()

    class UsesWrongBindingMap:
        def __init__(self, cfg: object = SpellMap(Config, binding_name="wrong")) -> None:
            self.cfg = cfg

    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", binding_name="right")
        spellbook.bind(spell=UsesWrongBindingMap, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_d2_frame_only_ambiguous_two_defaults_fails() -> None:
    """D2: two default-binding providers under a frame make frame-only SpellMap ambiguous."""
    spellbook = _make_spellbook()

    class UsesFrameMap:
        def __init__(self, cfg: object = SpellMap(spell=None, spellframe=IConfig)) -> None:
            self.cfg = cfg

    try:
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=Config, existence=Existence.unique, permissions="create", spellframe=IConfig)
            spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe=IConfig)
            spellbook.bind(spell=UsesFrameMap, existence=Existence.unique, permissions="create")
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_d1_two_params_same_target_both_resolved() -> None:
    """D1 behavior: two SpellMap params pointing at one target both resolve."""
    spellbook = _make_spellbook()
    conduit = None

    class UsesTwoConfigs:
        def __init__(
            self,
            a: object = SpellMap(Config),
            b: object = SpellMap(Config),
        ) -> None:
            self.a = a
            self.b = b

    try:
        spellbook.bind(spell=Config, existence=Existence.unique, permissions="create")
        spellbook.bind(spell=UsesTwoConfigs, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        instance = conduit.meld(spell=UsesTwoConfigs)
        assert isinstance(instance.a, Config) and isinstance(instance.b, Config)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_d_spellmap_binding_only_no_target_raises_at_construction() -> None:
    """D: a SpellMap with only a binding_name and no target is rejected at construction."""
    with pytest.raises(RESOLUTION_ERRORS):
        SpellMap(spell=None, spellframe=None, binding_name="orphan")


# =========================================================================== #
# E1 / E2 - eligibility & uniqueness
# =========================================================================== #
def test_e1_bind_none_raises() -> None:
    """E1: binding None is not a valid spell target."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=None, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_e1_bind_primitive_value_raises() -> None:
    """E1: binding a primitive (int) is not a valid spell."""
    spellbook = _make_spellbook()
    try:
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=123, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


def test_e2_concrete_default_binding_missing_defers_and_conjures() -> None:
    """E2 characterization: a concrete hint with no default-binding provider is a deferred warning; conjure succeeds rather than failing eagerly."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", binding_name="only")
        spellbook.bind(spell=NeedsEngineConcrete, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit is not None
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_e2_rebinding_same_class_raises_collision() -> None:
    """E2 characterization: rebinding the identical class is NOT idempotent - it raises a spell_id collision because each bind builds a new Spell wrapper. Candidate UX bug."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
    finally:
        spellbook.cleanup()


# =========================================================================== #
# G - existence
# =========================================================================== #
def test_g_unique_same_instance_across_entry_modes() -> None:
    """G: a unique spell resolves to the same instance via class and via id."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        assert conduit.meld(spell=Engine) is conduit.meld(spell=engine_id)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_g_many_distinct_across_repeated_melds() -> None:
    """G: a many spell yields distinct instances on each meld."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        engine_id = spellbook.bind(spell=Engine, existence=Existence.many, permissions="create")
        conduit = spellbook.conjure(name="root")
        seen = {id(conduit.meld(spell=engine_id)) for _ in range(3)}
        assert len(seen) == 3
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


# =========================================================================== #
# H - spellframe types
# =========================================================================== #
def test_h_string_frame_and_protocol_frame_same_key_collide() -> None:
    """H hunter: a string frame and a Protocol whose name normalizes to it share a key."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe="iengine")
        with pytest.raises(RESOLUTION_ERRORS):
            spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe=IEngine)
    finally:
        spellbook.cleanup()


def test_h_same_string_frame_distinct_bindings_resolve() -> None:
    """H behavior: two providers under one string frame are pickable by binding_name."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe="engines", binding_name="primary")
        spellbook.bind(spell=AltEngine, existence=Existence.unique, permissions="create", spellframe="engines", binding_name="secondary")
        conduit = spellbook.conjure(name="root")
        primary = conduit.meld(spellframe="engines", binding_name="primary")
        secondary = conduit.meld(spellframe="engines", binding_name="secondary")
        assert isinstance(primary, Engine) and isinstance(secondary, AltEngine)
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_h_unknown_binding_under_known_frame_raises() -> None:
    """H: a valid frame with an unbound binding_name must raise."""
    spellbook = _make_spellbook()
    conduit = None
    try:
        spellbook.bind(spell=Engine, existence=Existence.unique, permissions="create", spellframe="engines", binding_name="primary")
        conduit = spellbook.conjure(name="root")
        with pytest.raises(RESOLUTION_ERRORS):
            conduit.meld(spellframe="engines", binding_name="ghost")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()
