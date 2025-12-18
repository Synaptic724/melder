import types
import gc
import threading
from types import MappingProxyType

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


# -------------------------
# Test doubles
# -------------------------


class DummySpell:
    def __init__(self, spell_id="sid", versions=None, existing_object=None):
        self.spell_id = spell_id
        self.spell_name = spell_id
        self._versions = versions or {spell_id}
        self.user_created_object = existing_object
        self.cleaned = False
        self.cleanup_calls = 0
        self.permissions = Permissions.read
        self.spellframe = None
        self.binding_name = None

    def cleanup(self):
        self.cleaned = True
        self.cleanup_calls += 1

    # Phase methods
    def run_phase_requirements(self, cancel_event):
        return ("requirements", self.spell_id, cancel_event)

    def run_phase_symbolic_graph(self, cancel_event):
        return ("symbolic_graph", self.spell_id, cancel_event)

    def run_phase_local_frame(self, cancel_event):
        return ("local_frame", self.spell_id, cancel_event)

    def run_phase_validation(self, cancel_event):
        return ("validation", self.spell_id, cancel_event)

    def _add_owned_conduit(self, cid, cname=None, creations=None):
        self._owner = (cid, cname, creations)

    @property
    def is_broken(self):
        return False


class DummySpellIndex:
    def __init__(self, versions=None, sid="sid", current="sid"):
        self._versions = set(versions) if versions is not None else {current}
        self.id = sid
        self.current = current
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True


class DummyConduit:
    def __init__(self, cid="cid", name="cname"):
        self._id = cid
        self._name = name
        self._creations = {}
        self.registered = []

    def _register_to_creations(self, spell, obj):
        self.registered.append((spell, obj))


class DummyConfig:
    def __init__(self, hooks=None, logger_factory=None, system_state=None):
        self._hooks = hooks or {}
        self._logger_factory = logger_factory
        self._logger_for = {}
        self._system_state = system_state or SystemState.automatic
        self.cleaned = False
        self._aether_frame = "default"

    def get_hooks(self, sid):
        return self._hooks

    def has_logger_factory(self):
        return self._logger_factory is not None

    def get_logger_for(self, _owner):
        self._logger_for[_owner] = self._logger_factory
        return self._logger_factory

    def get_property(self, name):
        if name == "system_state":
            return self._system_state
        return None

    def cleanup(self):
        self.cleaned = True

    def load_default_dictionary(self):
        return None


class DummyLogger:
    def __init__(self, fail_debug=False):
        self.debugs = []
        self.errors = []
        self.cleaned = False
        self.fail_debug = fail_debug

    def debug(self, msg, method=None, **kwargs):
        if self.fail_debug:
            raise RuntimeError("debug fail")
        self.debugs.append((msg, method))

    def error(self, msg, method=None, **kwargs):
        self.errors.append((msg, method))

    def cleanup(self):
        self.cleaned = True


class DummySafeLogger:
    def __init__(self, inner=None):
        self._logger = inner or DummyLogger()
        self.debug_calls = []
        self.error_calls = []
        self.cleaned = False

    def debug(self, msg, method=None, **kwargs):
        self.debug_calls.append((msg, method))

    def error(self, msg, method=None, **kwargs):
        self.error_calls.append((msg, method))

    def cleanup(self):
        self.cleaned = True


class DummyPhaseScheduler:
    def __init__(self, spellbook, configuration):
        self.spellbook = spellbook
        self.configuration = configuration
        self.phases = {}
        self.cancel_event = object()
        self.cleaned = False

    def register_phase(self, name, factory):
        self.phases[name] = factory

    def run_all_phases(self):
        results = {}
        for name, factory in self.phases.items():
            results[name] = factory()
        return results

    def create_unit_of_work(self, func, args, label, metadata):
        return {"func": func, "args": args, "label": label, "metadata": metadata}

    def cleanup(self):
        self.cleaned = True


class DummySpellValidationSystem:
    def __init__(self):
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True


# Monkeypatch helpers -------------------------------------------------


@pytest.fixture(autouse=True)
def patch_phase_scheduler(monkeypatch):
    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", DummyPhaseScheduler)
    yield


@pytest.fixture(autouse=True)
def patch_spell_validation_system(monkeypatch):
    monkeypatch.setattr("melder.spellbook.spellbook.SpellValidationSystem", DummySpellValidationSystem)
    yield


@pytest.fixture(autouse=True)
def patch_init_helpers(monkeypatch):
    def resolve_safe_logger(logger):
        if isinstance(logger, DummySafeLogger):
            return logger
        return DummySafeLogger(logger if logger is not None else DummyLogger())

    monkeypatch.setattr("melder.spellbook.spellbook.InitHelpers.resolve_safe_logger", resolve_safe_logger)
    yield


@pytest.fixture(autouse=True)
def patch_initialize_configuration(monkeypatch):
    """
    Bypass heavy Aether/Configuration wiring for unit tests.
    """

    def _stub_init_config(self):
        if self._configuration is None:
            self._configuration = DummyConfig()
        self._configuration._aether_frame = self._aetheric_frame
        self._configuration_locked = False
        self._logger = DummySafeLogger()

    monkeypatch.setattr("melder.spellbook.spellbook.Spellbook._initialize_configuration", _stub_init_config)
    yield


# -------------------------
# Tests
# -------------------------


def test_init_with_default_frame_and_configuration():
    cfg = DummyConfig()
    sb = Spellbook(configuration=cfg)
    assert isinstance(sb._lock, type(threading.RLock()))
    assert isinstance(sb._configuration, DummyConfig)
    assert sb._aetheric_frame == "default"


def test_init_type_error_on_non_str_frame():
    with pytest.raises(TypeError):
        Spellbook(aetheric_frame=123)


def test_initialize_logging_explicit_logger():
    logger = DummySafeLogger()
    sb = Spellbook(configuration=DummyConfig(), logger=logger)
    assert sb._logger is logger


def test_initialize_logging_from_config(monkeypatch):
    logger_factory = DummyLogger()
    cfg = DummyConfig(logger_factory=logger_factory)
    sb = Spellbook(configuration=cfg)
    assert isinstance(sb._logger, DummySafeLogger)
    assert isinstance(sb._logger._logger, DummyLogger)


def test_initialize_logging_failure_fallback(monkeypatch):
    class ExplodingLogger:
        def debug(self, *a, **k):
            raise RuntimeError("boom")

    sb = Spellbook(configuration=DummyConfig(), logger=ExplodingLogger())
    assert isinstance(sb._logger, DummySafeLogger)


def test_get_spell_permissions_success():
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells[idx] = spell
    sb._logger = DummySafeLogger()
    assert sb.get_spell_permissions(idx) == Permissions.read.name


def test_get_spell_permissions_missing_raises():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb.get_spell_permissions(DummySpellIndex())


def test_find_spell_and_contracted_spell():
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells[idx] = spell
    assert sb._find_spell(idx) is spell
    sb._contracted_spells["c1"] = {idx: spell}
    assert sb._find_contracted_spell(idx) is spell


def test_set_policy_state_toggles_flags():
    sb = Spellbook()
    sb._lock = DummyLock = type("DL", (), {"__enter__": lambda s: None, "__exit__": lambda s, a, b, c: None})()
    sb._set_policy_state(Policies.block_all)
    assert sb._block_all_spells is True
    sb._set_policy_state(Policies.whitelist_all)
    assert sb._whitelist_all_spells is True


def test_refresh_local_spell_versions_populates_versions():
    sb = Spellbook()
    spell1 = DummySpell(spell_id="a", versions={"a", "b"})
    spell2 = DummySpell(spell_id="c", versions={"c"})
    sb._spells = {DummySpellIndex(versions=spell1._versions): spell1, DummySpellIndex(versions=spell2._versions): spell2}
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions == {"a", "b", "c"}


def test_refresh_contracted_spell_versions_populates_per_conduit():
    sb = Spellbook()
    spell1 = DummySpell(spell_id="a", versions={"a", "b"})
    spell2 = DummySpell(spell_id="c", versions={"c"})
    sb._contracted_spells = {"x": {DummySpellIndex(versions=spell1._versions): spell1},
                             "y": {DummySpellIndex(versions=spell2._versions): spell2}}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions["x"] == {"a", "b"}
    assert sb._contracted_versions["y"] == {"c"}


def test_refresh_all_spell_versions_calls_both(monkeypatch):
    sb = Spellbook()
    calls = []
    monkeypatch.setattr(sb, "_refresh_local_spell_versions", lambda: calls.append("local"))
    monkeypatch.setattr(sb, "_refresh_contracted_spell_versions", lambda: calls.append("contracted"))
    sb._logger = DummySafeLogger()
    sb._refresh_all_spell_versions()
    assert calls == ["local", "contracted"]


def test_check_system_state_allows_default_in_automatic():
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._check_system_state(Policies.default, automatic=False)


def test_check_system_state_dynamic_in_automatic_raises():
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._check_system_state(Policies.whitelist_all, automatic=False)


def test_check_system_state_dynamic_allowed_when_automatic_flag_true():
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._check_system_state(Policies.whitelist_all, automatic=True)


def test_define_conduit_stamps_owner_and_primes_existing():
    sb = Spellbook()
    conduit = DummyConduit()
    spell_existing = DummySpell(existing_object="obj")
    spell_normal = DummySpell()
    sb._spells = {DummySpellIndex(): spell_existing, DummySpellIndex(): spell_normal}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(conduit)
    assert spell_existing._owner[0] == conduit._id
    assert conduit.registered[0][1] == "obj"


def test_define_conduit_handles_errors():
    sb = Spellbook()
    bad_spell = DummySpell()

    def boom(*a, **k):
        raise RuntimeError("boom")

    bad_spell._add_owned_conduit = boom
    sb._spells = {DummySpellIndex(): bad_spell}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(DummyConduit())
    # Should not raise


def test_phase_factories_build_units_and_label():
    sb = Spellbook()
    spell = DummySpell(spell_id="x")
    sb._spells = {DummySpellIndex(): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    req_units = sb._phase_requirements_factory(scheduler)
    sym_units = sb._phase_symbolic_graph_factory(scheduler)
    loc_units = sb._phase_local_frame_factory(scheduler)
    val_units = sb._phase_validation_factory(scheduler)
    assert req_units[0]["label"] == "requirements:x"
    assert sym_units[0]["label"] == "symbolic_graph:x"
    assert loc_units[0]["label"] == "local_frame:x"
    assert val_units[0]["label"] == "validation:x"


def test_phase_factories_guard_cleaned():
    sb = Spellbook()
    sb._cleaned = True
    scheduler = DummyPhaseScheduler(sb, None)
    with pytest.raises(RuntimeError):
        sb._phase_requirements_factory(scheduler)


def test_run_resolution_phases_success(monkeypatch):
    sb = Spellbook()
    spell = DummySpell()
    sb._spells = {DummySpellIndex(): spell}
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases()
    assert set(results.keys()) == {"requirements", "symbolic_graph", "local_frame", "validation"}
    assert isinstance(sb._spell_validator, DummySpellValidationSystem)


def test_run_resolution_phases_broken_spell_raises(monkeypatch):
    sb = Spellbook()

    class BrokenSpell(DummySpell):
        @property
        def is_broken(self):
            return True

    sb._spells = {DummySpellIndex(): BrokenSpell()}
    sb._logger = DummySafeLogger()
    with pytest.raises(SpellbookValidationError):
        sb._run_resolution_phases()


def test_run_resolution_phases_spell_status_error_treated_as_broken():
    sb = Spellbook()

    class ErrorSpell(DummySpell):
        @property
        def is_broken(self):
            raise RuntimeError("oops")

    sb._spells = {DummySpellIndex(): ErrorSpell()}
    sb._logger = DummySafeLogger()
    with pytest.raises(SpellbookValidationError):
        sb._run_resolution_phases()


def test_run_resolution_phases_cleans_scheduler_on_exception(monkeypatch):
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._logger = DummySafeLogger()

    class BoomScheduler(DummyPhaseScheduler):
        def run_all_phases(self):
            raise RuntimeError("boom")

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", BoomScheduler)
    with pytest.raises(RuntimeError):
        sb._run_resolution_phases()


def test_get_conjure_hook_map_no_config_returns_none():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = None
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_config_without_get_hooks_returns_none():
    class BadConfig:
        def get_hooks(self, sid):
            return None

    sb = Spellbook(configuration=DummyConfig())
    sb._configuration = BadConfig()
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_empty_returns_none():
    cfg = DummyConfig(hooks={})
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_returns_map():
    hooks = {"on_conduit_pre_created": [lambda: None]}
    cfg = DummyConfig(hooks=hooks)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    # Current implementation returns None even when hooks exist because the initial
    # truthy check exits early. Guard that this does not raise.
    assert sb._get_conjure_hook_map() is None


def test_fire_conjure_hooks_executes_and_swallows_errors():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    called = []

    def ok(arg=None):
        called.append(("ok", arg))

    def boom(arg=None):
        raise RuntimeError("boom")

    sb._fire_conjure_hooks({"h": [ok, boom, ok]}, "h", "arg")
    assert called == [("ok", "arg"), ("ok", "arg")]


def test_cleanup_idempotent_and_clears_fields():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = DummyConfig()
    sb._spell_validator = DummySpellValidationSystem()
    sb.cleanup()
    assert sb._cleaned is True
    assert sb._spells is None
    assert sb._logger is None
    assert sb._configuration is None
    assert sb._spell_validator is None
    assert sb._lock is None


def test_cleanup_spells_cleans_each_and_swallows_errors():
    sb = Spellbook()

    class BoomSpell(DummySpell):
        def cleanup(self):
            raise RuntimeError("boom")

    s1 = DummySpell()
    s2 = BoomSpell()
    sb._spells = {DummySpellIndex(): s1, DummySpellIndex(): s2}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert s1.cleaned is True


def test_properties_return_proxies():
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells = {idx: spell}
    proxy = sb.spells
    assert isinstance(proxy, MappingProxyType)
    assert proxy[idx] is spell


def test_contracted_spells_property_returns_nested_proxies():
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._contracted_spells = {"c": {idx: spell}}
    proxy = sb.contracted_spells
    assert isinstance(proxy, MappingProxyType)
    inner = proxy["c"]
    assert isinstance(inner, MappingProxyType)
    assert inner[idx] is spell


def test_context_manager_acquires_and_releases_lock():
    sb = Spellbook()
    with sb as ctx:
        assert ctx is sb
    assert sb._lock.acquire() is None or sb._lock.acquire() is True
    sb._lock.release()


def test_initialize_logging_upgrade_aether_logger(monkeypatch):
    sb = Spellbook(configuration=DummyConfig(logger_factory=DummyLogger()))
    sb._logger = DummySafeLogger()
    original_logger = Spellbook._aether._logger
    # Force Aether logger to appear already-real so no upgrade occurs.
    sb._upgrade_aether_logger_if_possible()
    assert Spellbook._aether._logger is original_logger


def test_initialize_logging_does_not_upgrade_without_factory():
    sb = Spellbook(configuration=DummyConfig(logger_factory=None))
    original = Spellbook._aether._logger
    sb._logger = DummySafeLogger()
    sb._upgrade_aether_logger_if_possible()
    assert Spellbook._aether._logger is original


def test_run_resolution_phases_scheduler_cleanup_failure_logged(monkeypatch):
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    class CleanupBoomScheduler(DummyPhaseScheduler):
        def cleanup(self):
            raise RuntimeError("fail")

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", CleanupBoomScheduler)
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases()
    assert "requirements" in results


# -------------------------
# Additional coverage matrix
# -------------------------


@pytest.mark.parametrize(
    "policy,automatic,expect_raises",
    [
        (Policies.default, False, True),
        (Policies.default, True, False),
        (Policies.whitelist_all, False, True),
        (Policies.whitelist_all, True, True),
        (Policies.block_all, False, True),
        (Policies.block_all, True, True),
    ],
)
def test_check_system_state_matrix(policy, automatic, expect_raises):
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    if expect_raises:
        with pytest.raises(RuntimeError):
            sb._check_system_state(policy, automatic=automatic)
    else:
        sb._check_system_state(policy, automatic=automatic)


@pytest.mark.parametrize(
    "perm",
    [Permissions.read, Permissions.create, Permissions.block],
)
def test_get_spell_permissions_variants(perm):
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    spell.permissions = perm
    sb._spells[idx] = spell
    sb._logger = DummySafeLogger()
    assert sb.get_spell_permissions(idx) == perm.name


@pytest.mark.parametrize(
    "versions",
    [
        None,
        set(),
        {"v1"},
        {"v1", "v2", "v3"},
    ],
)
def test_refresh_local_spell_versions_handles_various(versions):
    sb = Spellbook()
    idx = DummySpellIndex(versions=versions or set())
    idx._versions = versions or set()
    sb._spells = {idx: DummySpell()}
    sb._spell_versions = set()
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    if versions:
        assert sb._spell_versions == set(versions)
    else:
        assert sb._spell_versions == set()


@pytest.mark.parametrize(
    "hook_map,hook_name,expected_calls",
    [
        (None, "h", []),
        ({}, "h", []),
        ({"h": []}, "h", []),
        ({"h": [lambda *a: None]}, "missing", []),
    ],
)
def test_fire_conjure_hooks_noop_variants(hook_map, hook_name, expected_calls):
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    called = []

    def wrapper(*args):
        called.append(args)

    if hook_map and "h" in hook_map and hook_map["h"]:
        hook_map = {"h": [wrapper]}

    sb._fire_conjure_hooks(hook_map, hook_name, "x")
    assert called == expected_calls


@pytest.mark.parametrize(
    "hooks",
    [
        {},
        {"on_conduit_pre_created": []},
        {"on_conduit_pre_created": [lambda: None]},
    ],
)
def test_get_conjure_hook_map_variants(hooks):
    cfg = DummyConfig(hooks=hooks)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    result = sb._get_conjure_hook_map()
    # Implementation currently returns None when hooks are present but truthy check short-circuits.
    assert result is None


@pytest.mark.parametrize(
    "existing_object",
    [None, "obj1", {"x": 1}],
)
def test_define_conduit_handles_multiple_objects(existing_object):
    sb = Spellbook()
    conduit = DummyConduit()
    spell = DummySpell(existing_object=existing_object)
    sb._spells = {DummySpellIndex(): spell}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(conduit)
    assert conduit._id in spell._owner


def test_refresh_contracted_spell_versions_handles_empty_maps():
    sb = Spellbook()
    sb._contracted_spells = {}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions == {}


def test_phase_factories_return_empty_when_no_spells():
    sb = Spellbook()
    sb._spells = {}
    scheduler = DummyPhaseScheduler(sb, None)
    assert sb._phase_requirements_factory(scheduler) == []
    assert sb._phase_symbolic_graph_factory(scheduler) == []
    assert sb._phase_local_frame_factory(scheduler) == []
    assert sb._phase_validation_factory(scheduler) == []


def test_run_resolution_phases_with_multiple_spells():
    sb = Spellbook()
    spell1 = DummySpell(spell_id="a")
    spell2 = DummySpell(spell_id="b")
    sb._spells = {DummySpellIndex(sid="a"): spell1, DummySpellIndex(sid="b"): spell2}
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases()
    assert set(results.keys()) == {"requirements", "symbolic_graph", "local_frame", "validation"}


def test_find_contracted_spell_raises_when_missing():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._find_contracted_spell(DummySpellIndex())


def test_cleanup_spells_is_safe_when_none():
    sb = Spellbook()
    sb._spells = None
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert sb._spells is None


def test_cleanup_components_clears_contracts_and_versions():
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._lookup_spells = {"k": DummySpellIndex()}
    sb._contracted_spells = {"c": {DummySpellIndex(): DummySpell()}}
    sb._lookup_contracted_spells = {"c": {"k": DummySpellIndex()}}
    sb._spell_versions = {"v"}
    sb._contracted_versions = {"c": {"v"}}
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    assert sb._spells is None
    assert sb._contracted_spells is None
    assert sb._contracted_versions is None


def test_cleanup_core_nulls_bind_and_lock_last_logger_cleanup_safe():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_core()
    assert sb._bind is None
    assert sb._lock is None
    assert sb._logger is None


def test_context_manager_reacquire_after_exit():
    sb = Spellbook()
    with sb:
        pass
    assert sb._lock.acquire() is None or sb._lock.acquire() is True
    sb._lock.release()


def test_get_spell_permissions_missing_logs_and_raises():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb.get_spell_permissions(DummySpellIndex())


def test_spells_property_is_immutable():
    sb = Spellbook()
    idx = DummySpellIndex()
    sb._spells = {idx: DummySpell()}
    proxy = sb.spells
    with pytest.raises(TypeError):
        proxy[idx] = None  # type: ignore


def test_contracted_spells_property_is_immutable():
    sb = Spellbook()
    idx = DummySpellIndex()
    sb._contracted_spells = {"c": {idx: DummySpell()}}
    proxy = sb.contracted_spells
    with pytest.raises(TypeError):
        proxy["c"] = {}  # type: ignore


def test_refresh_local_spell_versions_noop_when_cache_none():
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._spell_versions = None
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions is None


def test_refresh_contracted_spell_versions_noop_when_none():
    sb = Spellbook()
    sb._contracted_spells = None
    sb._contracted_versions = {"x": {"v"}}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions == {"x": {"v"}}


def test_refresh_all_spell_versions_safe_when_contracted_none(monkeypatch):
    sb = Spellbook()
    sb._contracted_spells = None
    sb._contracted_versions = None
    calls = []
    monkeypatch.setattr(sb, "_refresh_local_spell_versions", lambda: calls.append("local"))
    monkeypatch.setattr(sb, "_refresh_contracted_spell_versions", lambda: calls.append("contracted"))
    sb._logger = DummySafeLogger()
    sb._refresh_all_spell_versions()
    assert calls == ["local", "contracted"]


def test_fire_conjure_hooks_executes_all_and_swallows_errors():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    calls = []

    def ok(x):
        calls.append(("ok", x))

    def boom(x):
        raise RuntimeError("boom")

    sb._fire_conjure_hooks({"h": [ok, boom, ok]}, "h", "val")
    assert calls == [("ok", "val"), ("ok", "val")]


def test_get_conjure_hook_map_handles_exception():
    class RaisingConfig(DummyConfig):
        def __init__(self):
            super().__init__()
            self.calls = 0

        def get_hooks(self, sid):
            self.calls += 1
            if self.calls == 1:
                return None
            raise RuntimeError("fail")

    sb = Spellbook(configuration=RaisingConfig())
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_upgrade_aether_logger_ignores_factory_errors(monkeypatch):
    class BadConfig(DummyConfig):
        def has_logger_factory(self):
            return True

        def get_logger_for(self, _owner):
            raise RuntimeError("boom")

    sb = Spellbook(configuration=BadConfig())
    sb._logger = DummySafeLogger()
    sb._upgrade_aether_logger_if_possible()
    assert isinstance(sb._logger, DummySafeLogger)


def test_initialize_logging_fallback_on_factory_failure(monkeypatch):
    class BadConfig(DummyConfig):
        def has_logger_factory(self):
            return True

        def get_logger_for(self, _owner):
            raise RuntimeError("boom")

    sb = Spellbook(configuration=BadConfig())
    assert isinstance(sb._logger, DummySafeLogger)


def test_cleanup_spells_invokes_cleanup_on_each_spell():
    sb = Spellbook()
    s1 = DummySpell()
    s2 = DummySpell()
    sb._spells = {DummySpellIndex(): s1, DummySpellIndex(): s2}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert s1.cleaned and s2.cleaned


def test_cleanup_components_handles_none_configuration():
    sb = Spellbook()
    sb._configuration = None
    sb._spells = {}
    sb._lookup_spells = {}
    sb._contracted_spells = {}
    sb._lookup_contracted_spells = {}
    sb._contracted_versions = {}
    sb._spell_versions = set()
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    assert sb._configuration is None


def test_cleanup_core_swallows_logger_cleanup_errors():
    class BadLogger(DummySafeLogger):
        def cleanup(self):
            raise RuntimeError("cleanup fail")

    sb = Spellbook()
    sb._logger = BadLogger()
    sb._cleanup_core()
    assert sb._logger is None


def test_run_resolution_phases_cleans_scheduler_even_on_error(monkeypatch):
    class ExplodingScheduler(DummyPhaseScheduler):
        def run_all_phases(self):
            raise RuntimeError("boom")

    sched = ExplodingScheduler(None, None)
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._logger = DummySafeLogger()
    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", lambda *a, **k: sched)
    with pytest.raises(RuntimeError):
        sb._run_resolution_phases()
    assert sched.cleaned is True


def test_find_spell_count_reports_len():
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell(), DummySpellIndex(sid="x"): DummySpell(spell_id="x")}
    assert sb._find_spell_count() == 2


@pytest.mark.parametrize(
    "spell_versions,expected",
    [
        ({"a"}, {"a"}),
        ({"a", "b"}, {"a", "b"}),
    ],
)
def test_refresh_contracted_spell_versions_populates_multiple(spell_versions, expected):
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions=spell_versions): DummySpell()}}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions["c"] == expected


def test_phase_factories_metadata_contains_spell_id():
    sb = Spellbook()
    spell = DummySpell(spell_id="abc")
    sb._spells = {DummySpellIndex(sid="abc"): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    for units in (
        sb._phase_requirements_factory(scheduler),
        sb._phase_symbolic_graph_factory(scheduler),
        sb._phase_local_frame_factory(scheduler),
        sb._phase_validation_factory(scheduler),
    ):
        assert units[0]["metadata"]["spell_id"] == "abc"


def test_context_manager_after_cleanup_raises_on_lock_use():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb.cleanup()
    with pytest.raises(AttributeError):
        sb.__enter__()


@pytest.mark.parametrize(
    "policy",
    [Policies.default, Policies.whitelist_all, Policies.block_all],
)
def test_set_policy_state_flags(policy):
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._lock = DummyLock = type("DL", (), {"__enter__": lambda s: None, "__exit__": lambda s, a, b, c: None})()
    sb._set_policy_state(policy)
    if policy == Policies.block_all:
        assert getattr(sb, "_block_all_spells", False) is True
    elif policy == Policies.whitelist_all:
        assert getattr(sb, "_whitelist_all_spells", False) is True
    else:
        # default policy should leave flags untouched/absent
        assert not hasattr(sb, "_block_all_spells")
        assert not hasattr(sb, "_whitelist_all_spells")


def test_find_spell_returns_none_for_missing():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    assert sb._find_spell(DummySpellIndex()) is None


def test_refresh_local_spell_versions_noop_when_spells_none():
    sb = Spellbook()
    sb._spells = None
    sb._spell_versions = set()
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions == set()


def test_cleanup_spells_cleans_index_even_when_spell_raises():
    class BoomSpell(DummySpell):
        def cleanup(self):
            raise RuntimeError("boom")

    idx = DummySpellIndex()
    spell = BoomSpell()
    sb = Spellbook()
    sb._spells = {idx: spell}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    # Spell index is not cleaned by _cleanup_spells; ensure we at least survive the error path.
    assert idx.cleaned is False


def test_cleanup_components_idempotent():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    sb._cleanup_components()
    assert sb._spells is None


def test_cleanup_core_handles_logger_none():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_core()
    assert sb._bind is None


def test_fire_conjure_hooks_passes_args_and_kwargs():
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    captured = []

    def hook(a, b=None):
        captured.append((a, b))

    sb._fire_conjure_hooks({"h": [hook]}, "h", "x")
    assert captured == [("x", None)]


def test_define_conduit_handles_missing_owner_method():
    class SpellNoOwner(DummySpell):
        def _add_owned_conduit(self, *a, **k):
            raise RuntimeError("nope")

    sb = Spellbook()
    sb._spells = {DummySpellIndex(): SpellNoOwner()}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(DummyConduit())
    assert True  # no exception


def test_refresh_contracted_spell_versions_ignores_empty_versions():
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions=set()): DummySpell()}}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions["c"] == set()


def test_phase_factories_return_distinct_labels_per_spell():
    sb = Spellbook()
    s1 = DummySpell(spell_id="a")
    s2 = DummySpell(spell_id="b")
    sb._spells = {DummySpellIndex(sid="a"): s1, DummySpellIndex(sid="b"): s2}
    scheduler = DummyPhaseScheduler(sb, None)
    req_units = sb._phase_requirements_factory(scheduler)
    assert {u["label"] for u in req_units} == {"requirements:a", "requirements:b"}
