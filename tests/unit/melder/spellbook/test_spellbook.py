import types
import gc
import threading
from types import MappingProxyType
from typing import MutableMapping, cast

import pytest

from melder.aether.aether import Aether
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
    """
    Purpose:
        Provide a minimal spell stub for Spellbook tests.
    Contract:
        Exposes attributes and phase hooks that Spellbook depends on.
    """
    def __init__(self, spell_id="sid", versions=None, existing_object=None):
        """
        Purpose:
            Initialize the spell stub with identity and tracking data.
        Contract:
            Stores inputs verbatim and initializes cleanup tracking.
        Args:
            spell_id: Identifier used for spell_id and spell_name.
            versions: Optional iterable of version ids associated with the spell.
            existing_object: Optional existing instance attached to the spell.
        Returns:
            None.
        """
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
        """
        Purpose:
            Mark the spell stub as cleaned and track calls.
        Contract:
            Sets cleaned True and increments cleanup_calls.
        Returns:
            None.
        """
        self.cleaned = True
        self.cleanup_calls += 1

    # Phase methods
    def run_phase_requirements(self, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 1 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, and cancel event.
        Args:
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, object]: Phase marker tuple.
        """
        return ("requirements", self.spell_id, cancel_event)

    def run_phase_symbolic_graph(self, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 2 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, and cancel event.
        Args:
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, object]: Phase marker tuple.
        """
        return ("symbolic_graph", self.spell_id, cancel_event)

    def run_phase_local_frame(self, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 3 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, and cancel event.
        Args:
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, object]: Phase marker tuple.
        """
        return ("local_frame", self.spell_id, cancel_event)

    def run_phase_validation(self, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 4 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, and cancel event.
        Args:
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, object]: Phase marker tuple.
        """
        return ("validation", self.spell_id, cancel_event)

    def run_phase_root_blueprints(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 5 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("root_blueprints", self.spell_id, conduit_id, cancel_event)

    def run_phase_system_validation(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 6 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("system_validation", self.spell_id, conduit_id, cancel_event)

    def run_phase_change_control(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 7 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("change_control", self.spell_id, conduit_id, cancel_event)

    def _add_owned_conduit(self, cid, cname=None, creations=None):
        """
        Purpose:
            Capture conduit ownership metadata for assertions.
        Contract:
            Stores the conduit id, name, and creations on the stub.
        Args:
            cid: Conduit identifier.
            cname: Optional conduit name.
            creations: Optional creation map.
        Returns:
            None.
        """
        self._owner = (cid, cname, creations)

    @property
    def is_broken(self):
        """
        Purpose:
            Report whether the spell is broken.
        Contract:
            Always returns False for this stub.
        Returns:
            bool: False for the dummy spell.
        """
        return False


class DummySpellIndex:
    """
    Purpose:
        Provide a minimal SpellIndex stub with version tracking.
    Contract:
        Exposes has_version and cleanup for Spellbook internals.
    """
    def __init__(self, versions=None, sid="sid", current="sid"):
        """
        Purpose:
            Initialize the index stub with version metadata.
        Contract:
            Stores version ids and identifiers for later checks.
        Args:
            versions: Optional iterable of version ids.
            sid: Spell id for the index.
            current: Current version id for the index.
        Returns:
            None.
        """
        self._versions = set(versions) if versions is not None else {current}
        self.id = sid
        self.current = current
        self.cleaned = False

    def cleanup(self):
        """
        Purpose:
            Mark the index stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True

    def has_version(self, version_id):
        """
        Purpose:
            Report whether the index includes the given version id.
        Contract:
            Returns True when version_id is present in _versions.
        Args:
            version_id: Version id to check.
        Returns:
            bool: True when version_id is registered.
        """
        return version_id in self._versions

    def _set_owner_conduit_id(self, conduit_id):
        """
        Purpose:
            Capture the owner conduit id for assertions.
        Contract:
            Stores the conduit id on the stub.
        Args:
            conduit_id: Owner conduit identifier.
        Returns:
            None.
        """
        self.owner_conduit_id = conduit_id


class DummyConduit:
    """
    Purpose:
        Provide a conduit stub for Spellbook tests.
    Contract:
        Tracks registration calls for existing creations.
    """
    def __init__(self, cid="cid", name="cname"):
        """
        Purpose:
            Initialize the conduit stub.
        Contract:
            Stores identifiers and initializes registration tracking.
        Args:
            cid: Conduit identifier.
            name: Conduit name.
        Returns:
            None.
        """
        self._id = cid
        self._name = name
        self._creations = {}
        self.registered = []

    def _register_to_creations(self, spell, obj):
        """
        Purpose:
            Record registration of existing creations.
        Contract:
            Appends the spell and object to the registered list.
        Args:
            spell: Spell instance being registered.
            obj: Existing object bound to the spell.
        Returns:
            None.
        """
        self.registered.append((spell, obj))


class DummyConfig:
    """
    Purpose:
        Provide a lightweight configuration stub for Spellbook tests.
    Contract:
        Implements the configuration methods used by Spellbook.
    """
    def __init__(self, hooks=None, logger_factory=None, system_state=None, frozen=False, validate_ok=True):
        """
        Purpose:
            Initialize the configuration stub.
        Contract:
            Stores hook data, logger factory, and validation flags.
        Args:
            hooks: Optional hook mapping.
            logger_factory: Optional logger factory.
            system_state: Optional SystemState override.
            frozen: Initial frozen flag.
            validate_ok: Whether validate() should succeed.
        Returns:
            None.
        """
        self._hooks = hooks or {}
        self._logger_factory = logger_factory
        self._logger_for = {}
        self._system_state = system_state or SystemState.automatic
        self.cleaned = False
        self._aether_frame = "default"
        self._frozen = frozen
        self._validate_ok = validate_ok

    def get_hooks(self, sid):
        """
        Purpose:
            Return the configured hook map.
        Contract:
            Returns the stored hook mapping for any spellbook id.
        Args:
            sid: Spellbook id requested by caller.
        Returns:
            dict: Hook mapping configured on the stub.
        """
        return self._hooks

    def has_logger_factory(self):
        """
        Purpose:
            Indicate whether a logger factory is available.
        Contract:
            Returns True when _logger_factory is set.
        Returns:
            bool: True when logger_factory exists.
        """
        return self._logger_factory is not None

    def get_logger_for(self, _owner):
        """
        Purpose:
            Return a logger for the given owner.
        Contract:
            Records the factory used and returns it.
        Args:
            _owner: Spellbook owner identifier.
        Returns:
            object: The stored logger factory.
        """
        self._logger_for[_owner] = self._logger_factory
        return self._logger_factory

    def get_property(self, name):
        """
        Purpose:
            Provide access to configuration properties.
        Contract:
            Returns system_state when name is "system_state", otherwise None.
        Args:
            name: Property name to fetch.
        Returns:
            object | None: Property value for the requested name.
        """
        if name == "system_state":
            return self._system_state
        return None

    def validate(self):
        """
        Purpose:
            Validate the configuration stub.
        Contract:
            Returns the configured validation flag.
        Returns:
            bool: True when validation should succeed.
        """
        return self._validate_ok

    def freeze(self):
        """
        Purpose:
            Freeze the configuration stub.
        Contract:
            Sets the frozen flag to True.
        Returns:
            None.
        """
        self._frozen = True

    def cleanup(self):
        """
        Purpose:
            Mark the configuration stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True

    def load_default_dictionary(self):
        """
        Purpose:
            Provide a dictionary loader hook for Spellbook init.
        Contract:
            Returns None for the stub.
        Returns:
            None.
        """
        return None


class DummyLogger:
    """
    Purpose:
        Provide a logger stub with call tracking.
    Contract:
        Records debug/error calls and can simulate failures.
    """
    def __init__(self, fail_debug=False):
        """
        Purpose:
            Initialize the logger stub.
        Contract:
            Stores fail_debug flag and initializes call logs.
        Args:
            fail_debug: Whether debug() should raise.
        Returns:
            None.
        """
        self.debugs = []
        self.errors = []
        self.cleaned = False
        self.fail_debug = fail_debug

    def debug(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a debug call or raise when configured.
        Contract:
            Appends (msg, method) unless fail_debug is True.
        Args:
            msg: Debug message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        Raises:
            RuntimeError: If fail_debug is True.
        """
        if self.fail_debug:
            raise RuntimeError("debug fail")
        self.debugs.append((msg, method))

    def error(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an error call.
        Contract:
            Appends (msg, method) to the error log.
        Args:
            msg: Error message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.errors.append((msg, method))

    def cleanup(self):
        """
        Purpose:
            Mark the logger stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True


class DummySafeLogger:
    """
    Purpose:
        Provide a safe logger wrapper stub.
    Contract:
        Records debug/error calls without delegating.
    """
    def __init__(self, inner=None):
        """
        Purpose:
            Initialize the safe logger stub.
        Contract:
            Stores the inner logger and initializes call logs.
        Args:
            inner: Optional inner logger instance.
        Returns:
            None.
        """
        self._logger = inner or DummyLogger()
        self.debug_calls = []
        self.error_calls = []
        self.cleaned = False

    def debug(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a debug call.
        Contract:
            Appends (msg, method) to debug_calls.
        Args:
            msg: Debug message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.debug_calls.append((msg, method))

    def error(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an error call.
        Contract:
            Appends (msg, method) to error_calls.
        Args:
            msg: Error message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.error_calls.append((msg, method))

    def cleanup(self):
        """
        Purpose:
            Mark the safe logger stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True


class DummyPhaseScheduler:
    """
    Purpose:
        Provide a phase scheduler stub for Spellbook tests.
    Contract:
        Captures registered phases and can execute factories.
    """
    def __init__(self, spellbook, configuration):
        """
        Purpose:
            Initialize the scheduler stub.
        Contract:
            Stores spellbook/configuration and initializes phase registry.
        Args:
            spellbook: Spellbook under test.
            configuration: Configuration used by the scheduler.
        Returns:
            None.
        """
        self.spellbook = spellbook
        self.configuration = configuration
        self.phases = {}
        self.cancel_event = object()
        self.cleaned = False

    def register_phase(self, name, factory):
        """
        Purpose:
            Register a phase factory by name.
        Contract:
            Stores the factory in the phases mapping.
        Args:
            name: Phase name identifier.
            factory: Callable factory for phase units.
        Returns:
            None.
        """
        self.phases[name] = factory

    def run_all_phases(self):
        """
        Purpose:
            Execute all registered phase factories.
        Contract:
            Returns a mapping of phase names to factory results.
        Returns:
            dict: Mapping of phase names to results.
        """
        results = {}
        for name, factory in self.phases.items():
            results[name] = factory()
        return results

    def create_unit_of_work(self, func, args, label, metadata):
        """
        Purpose:
            Build a unit-of-work dictionary for the scheduler.
        Contract:
            Returns a dict with the provided fields.
        Args:
            func: Callable to execute.
            args: Positional arguments tuple.
            label: Label for the unit of work.
            metadata: Metadata dict for the unit.
        Returns:
            dict: Unit-of-work descriptor.
        """
        return {"func": func, "args": args, "label": label, "metadata": metadata}

    def cleanup(self):
        """
        Purpose:
            Mark the scheduler stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True


class DummySpellValidationSystem:
    """
    Purpose:
        Provide a validation system stub for Spellbook tests.
    Contract:
        Tracks cleanup calls.
    """
    def __init__(self):
        """
        Purpose:
            Initialize the validation system stub.
        Contract:
            Sets cleaned to False.
        Returns:
            None.
        """
        self.cleaned = False

    def cleanup(self):
        """
        Purpose:
            Mark the validation system stub as cleaned.
        Contract:
            Sets cleaned True.
        Returns:
            None.
        """
        self.cleaned = True


# Monkeypatch helpers -------------------------------------------------


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_tests():
    """
    Purpose:
        Ensure Spellbook tests do not share cleaned Aether state.
    Contract:
        Resets the Aether singleton and rebinds Spellbook._aether before and
        after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    yield
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()


@pytest.fixture(autouse=True)
def patch_phase_scheduler(monkeypatch):
    """
    Purpose:
        Replace the real PhaseScheduler with a stub for unit tests.
    Contract:
        Patches PhaseScheduler for the duration of each test.
    Args:
        monkeypatch: Pytest fixture for patching module attributes.
    Returns:
        None.
    """
    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", DummyPhaseScheduler)
    yield


@pytest.fixture(autouse=True)
def patch_spell_validation_system(monkeypatch):
    """
    Purpose:
        Replace SpellValidationSystem with a stub for unit tests.
    Contract:
        Patches SpellValidationSystem for the duration of each test.
    Args:
        monkeypatch: Pytest fixture for patching module attributes.
    Returns:
        None.
    """
    monkeypatch.setattr("melder.spellbook.spellbook.SpellValidationSystem", DummySpellValidationSystem)
    yield


@pytest.fixture(autouse=True)
def patch_init_helpers(monkeypatch):
    """
    Purpose:
        Patch InitHelpers.resolve_safe_logger to use test doubles.
    Contract:
        Returns a DummySafeLogger wrapper for any logger input.
    Args:
        monkeypatch: Pytest fixture for patching module attributes.
    Returns:
        None.
    """
    def resolve_safe_logger(logger):
        """
        Purpose:
            Resolve safe logger instances for tests.
        Contract:
            Wraps non-safe loggers in DummySafeLogger.
        Args:
            logger: Logger instance to wrap or pass through.
        Returns:
            DummySafeLogger: Safe logger wrapper.
        """
        if isinstance(logger, DummySafeLogger):
            return logger
        return DummySafeLogger(logger if logger is not None else DummyLogger())

    monkeypatch.setattr("melder.spellbook.spellbook.InitHelpers.resolve_safe_logger", resolve_safe_logger)
    yield


@pytest.fixture(autouse=True)
def patch_initialize_configuration(monkeypatch):
    """
    Purpose:
        Bypass heavy Aether/Configuration wiring for unit tests.
    Contract:
        Ensures Spellbook uses a DummyConfig and DummySafeLogger.
    Args:
        monkeypatch: Pytest fixture for patching module attributes.
    Returns:
        None.
    """

    def _stub_init_config(self):
        """
        Purpose:
            Provide a lightweight configuration initializer.
        Contract:
            Ensures configuration and logger are populated for tests.
        Args:
            self: Spellbook instance under test.
        Returns:
            None.
        """
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
    """
    Purpose:
        Verify Spellbook initializes core state with defaults.
    Contract:
        The lock is created, configuration is set, and frame defaults to "default".
    Returns:
        None.
    Raises:
        AssertionError: If any default initialization is incorrect.
    """
    cfg = DummyConfig()
    sb = Spellbook(configuration=cfg)
    assert isinstance(sb._lock, type(threading.RLock()))
    assert isinstance(sb._configuration, DummyConfig)
    assert sb._aetheric_frame == "default"


def test_init_type_error_on_non_str_frame():
    """
    Purpose:
        Ensure Spellbook rejects a non-string aetheric_frame.
    Contract:
        __init__ raises TypeError when aetheric_frame is not a string.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError):
        Spellbook(aetheric_frame=123)


def test_initialize_logging_explicit_logger():
    """
    Purpose:
        Verify an explicit logger is preserved during initialization.
    Contract:
        The supplied logger is stored without replacement.
    Returns:
        None.
    Raises:
        AssertionError: If the logger is replaced unexpectedly.
    """
    logger = DummySafeLogger()
    sb = Spellbook(configuration=DummyConfig(), logger=logger)
    assert sb._logger is logger


def test_initialize_logging_from_config(monkeypatch):
    """
    Purpose:
        Ensure Spellbook resolves a logger from configuration.
    Contract:
        The resolved logger is wrapped in DummySafeLogger.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If logger resolution is incorrect.
    """
    logger_factory = DummyLogger()
    cfg = DummyConfig(logger_factory=logger_factory)
    sb = Spellbook(configuration=cfg)
    assert isinstance(sb._logger, DummySafeLogger)
    assert isinstance(sb._logger._logger, DummyLogger)


def test_initialize_logging_failure_fallback(monkeypatch):
    """
    Purpose:
        Verify logging initialization falls back on logger failure.
    Contract:
        A failing logger is wrapped in DummySafeLogger without raising.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If fallback does not occur.
    """
    class ExplodingLogger:
        """
        Purpose:
            Provide a logger stub that fails on debug.
        Contract:
            debug raises RuntimeError to simulate logging failure.
        """
        def debug(self, *a, **k):
            """
            Purpose:
                Simulate a debug logging failure.
            Contract:
                Raises RuntimeError unconditionally.
            Args:
                *a: Positional arguments.
                **k: Keyword arguments.
            Returns:
                None.
            Raises:
                RuntimeError: Always raised to simulate failure.
            """
            raise RuntimeError("boom")

    sb = Spellbook(configuration=DummyConfig(), logger=ExplodingLogger())
    assert isinstance(sb._logger, DummySafeLogger)


def test_get_spell_permissions_success():
    """
    Purpose:
        Verify permissions are returned for a known spell.
    Contract:
        get_spell_permissions returns the spell permissions name.
    Returns:
        None.
    Raises:
        AssertionError: If permissions are incorrect.
    """
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells[idx] = spell
    sb._logger = DummySafeLogger()
    assert sb.get_spell_permissions(idx) == Permissions.read.name


def test_get_spell_permissions_missing_raises():
    """
    Purpose:
        Ensure missing spells raise on permission lookup.
    Contract:
        get_spell_permissions raises RuntimeError when index is not found.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb.get_spell_permissions(DummySpellIndex())


def test_find_spell_and_contracted_spell():
    """
    Purpose:
        Verify local and contracted spell lookup helpers.
    Contract:
        _find_spell returns local spells and _find_contracted_spell returns contracted.
    Returns:
        None.
    Raises:
        AssertionError: If lookup results are incorrect.
    """
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells[idx] = spell
    assert sb._find_spell(idx) is spell
    sb._contracted_spells["c1"] = {idx: spell}
    assert sb._find_contracted_spell(idx) is spell


def test_link_contract_registers_link_mirror() -> None:
    """
    Purpose:
        Validate link mirror registration during link contract lifecycle.
    Contract:
        - _create_link_contract registers borrower->provider in the mirror.
        - _sever_link_contract unregisters the mirror entry.
    Returns:
        None.
    Raises:
        AssertionError: If link mirror registration is missing.
    """
    spellbook = Spellbook()
    spellbook._conduit = types.SimpleNamespace(_id="owner-1")

    register_calls: list[tuple[str, str]] = []
    unregister_calls: list[tuple[str, str]] = []

    class _TransactionManagerStub:
        def register_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
            register_calls.append((borrower_conduit_id, provider_conduit_id))

        def unregister_link(self, *, borrower_conduit_id: str, provider_conduit_id: str) -> None:
            unregister_calls.append((borrower_conduit_id, provider_conduit_id))

    class _ChangeControlStub:
        def __init__(self, manager: _TransactionManagerStub) -> None:
            self._manager = manager

        def transaction_manager(self) -> _TransactionManagerStub:
            return self._manager

    class _AetherStub:
        def __init__(self, change_control: _ChangeControlStub) -> None:
            self._change_control = change_control

        def _get_change_control_manager(self, frame_name: str = "default") -> _ChangeControlStub:
            return self._change_control

    spellbook._aether = _AetherStub(_ChangeControlStub(_TransactionManagerStub()))

    try:
        spellbook._create_link_contract("peer-1")
        assert register_calls == [("owner-1", "peer-1")]

        spellbook._sever_link_contract("peer-1")
        assert unregister_calls == [("owner-1", "peer-1")]
    finally:
        spellbook.cleanup()


def test_set_policy_state_toggles_flags():
    """
    Purpose:
        Confirm policy state toggles internal policy flags.
    Contract:
        _set_policy_state updates block/whitelist flags based on policy.
    Returns:
        None.
    Raises:
        AssertionError: If flags do not reflect policy.
    """
    sb = Spellbook()
    sb._lock = DummyLock = type("DL", (), {"__enter__": lambda s: None, "__exit__": lambda s, a, b, c: None})()
    sb._set_policy_state(Policies.block_all)
    assert sb._block_all_spells is True
    sb._set_policy_state(Policies.whitelist_all)
    assert sb._whitelist_all_spells is True


def test_refresh_local_spell_versions_populates_versions():
    """
    Purpose:
        Verify local version cache collects all spell versions.
    Contract:
        _refresh_local_spell_versions aggregates version ids across spells.
    Returns:
        None.
    Raises:
        AssertionError: If version aggregation is incorrect.
    """
    sb = Spellbook()
    spell1 = DummySpell(spell_id="a", versions={"a", "b"})
    spell2 = DummySpell(spell_id="c", versions={"c"})
    sb._spells = {DummySpellIndex(versions=spell1._versions): spell1, DummySpellIndex(versions=spell2._versions): spell2}
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions == {"a", "b", "c"}


def test_refresh_contracted_spell_versions_populates_per_conduit():
    """
    Purpose:
        Ensure contracted version cache is built per conduit.
    Contract:
        _refresh_contracted_spell_versions records versions per conduit id.
    Returns:
        None.
    Raises:
        AssertionError: If contracted versions are incorrect.
    """
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
    """
    Purpose:
        Verify refresh-all delegates to local and contracted refreshers.
    Contract:
        _refresh_all_spell_versions calls both refresh helpers.
    Args:
        monkeypatch: Pytest fixture for patching instance methods.
    Returns:
        None.
    Raises:
        AssertionError: If either refresh helper is not called.
    """
    sb = Spellbook()
    calls = []
    monkeypatch.setattr(sb, "_refresh_local_spell_versions", lambda: calls.append("local"))
    monkeypatch.setattr(sb, "_refresh_contracted_spell_versions", lambda: calls.append("contracted"))
    sb._logger = DummySafeLogger()
    sb._refresh_all_spell_versions()
    assert calls == ["local", "contracted"]


def test_check_system_state_allows_default_in_automatic():
    """
    Purpose:
        Ensure default policy is rejected when automatic flag is False.
    Contract:
        _check_system_state raises for default policy in automatic state when not allowed.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._check_system_state(Policies.default, automatic=False)


def test_check_system_state_dynamic_in_automatic_raises():
    """
    Purpose:
        Verify dynamic policy is rejected in automatic mode when not allowed.
    Contract:
        _check_system_state raises when automatic is False and policy is dynamic,
        and the error message includes policy and system_state context.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError) as excinfo:
        sb._check_system_state(Policies.whitelist_all, automatic=False)
    message = str(excinfo.value)
    assert "policy=Policies.whitelist_all" in message
    assert "automatic=False" in message
    assert "system_state=SystemState.automatic" in message


def test_check_system_state_dynamic_allowed_when_automatic_flag_true():
    """
    Purpose:
        Confirm automatic flag does not override rejection for dynamic policy.
    Contract:
        _check_system_state raises even when automatic is True for dynamic policies,
        and the error message includes policy and allowed-policy context.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError) as excinfo:
        sb._check_system_state(Policies.whitelist_all, automatic=True)
    message = str(excinfo.value)
    assert "policy=Policies.whitelist_all" in message
    assert "allowed=default" in message


def test_define_conduit_stamps_owner_and_primes_existing():
    """
    Purpose:
        Verify conduit ownership and existing creations are registered.
    Contract:
        _define_conduit_into_spells sets owner info and registers existing objects.
    Returns:
        None.
    Raises:
        AssertionError: If owner or registration is missing.
    """
    sb = Spellbook()
    conduit = DummyConduit()
    spell_existing = DummySpell(existing_object="obj")
    spell_normal = DummySpell()
    idx_existing = DummySpellIndex()
    idx_normal = DummySpellIndex()
    spell_existing.spell_index = idx_existing
    spell_normal.spell_index = idx_normal
    sb._spells = {idx_existing: spell_existing, idx_normal: spell_normal}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(conduit)
    assert spell_existing._owner[0] == conduit._id
    assert conduit.registered[0][1] == "obj"


def test_define_conduit_handles_errors():
    """
    Purpose:
        Ensure errors defining conduit ownership are swallowed.
    Contract:
        _define_conduit_into_spells continues despite spell errors.
    Returns:
        None.
    Raises:
        AssertionError: If the spell handler is not invoked.
    """
    sb = Spellbook()
    bad_spell = DummySpell()

    def boom(*a, **k):
        """
        Purpose:
            Simulate a failing ownership hook.
        Contract:
            Always raises RuntimeError.
        Args:
            *a: Positional arguments.
            **k: Keyword arguments.
        Returns:
            None.
        Raises:
            RuntimeError: Always raised for the stub.
        """
        raise RuntimeError("boom")

    bad_spell._add_owned_conduit = boom
    sb._spells = {DummySpellIndex(): bad_spell}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(DummyConduit())
    # Should not raise


def test_phase_factories_build_units_and_label():
    """
    Purpose:
        Verify phase factories emit labeled units of work.
    Contract:
        Each phase factory creates units with expected labels.
    Returns:
        None.
    Raises:
        AssertionError: If labels are incorrect.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="x")
    sb._spells = {DummySpellIndex(): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    req_units = sb._phase_requirements_factory(scheduler)
    sym_units = sb._phase_symbolic_graph_factory(scheduler)
    loc_units = sb._phase_local_frame_factory(scheduler)
    val_units = sb._phase_validation_factory(scheduler)
    root_units = sb._phase_root_blueprints_factory(scheduler, "cid")
    sys_units = sb._phase_system_validation_factory(scheduler, "cid")
    change_units = sb._phase_change_control_factory(scheduler, "cid")
    assert req_units[0]["label"] == "requirements:x"
    assert sym_units[0]["label"] == "symbolic_graph:x"
    assert loc_units[0]["label"] == "local_frame:x"
    assert val_units[0]["label"] == "validation:x"
    assert root_units[0]["label"] == "root_blueprints:x"
    assert sys_units[0]["label"] == "system_validation:x"
    assert change_units[0]["label"] == "change_control:x"


def test_phase_factories_guard_cleaned():
    """
    Purpose:
        Ensure phase factories reject cleaned Spellbook instances.
    Contract:
        _phase_requirements_factory raises RuntimeError when cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned guard does not raise.
    """
    sb = Spellbook()
    sb._cleaned = True
    scheduler = DummyPhaseScheduler(sb, None)
    with pytest.raises(RuntimeError):
        sb._phase_requirements_factory(scheduler)


def test_run_resolution_phases_success(monkeypatch):
    """
    Purpose:
        Verify resolution phases run and return expected keys.
    Contract:
        _run_resolution_phases returns all phase results and sets validator.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If phases or validator are incorrect.
    """
    sb = Spellbook()
    spell = DummySpell()
    sb._spells = {DummySpellIndex(): spell}
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases("cid")
    assert set(results.keys()) == {
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "system_validation",
        "change_control",
    }
    assert isinstance(sb._spell_validator, DummySpellValidationSystem)


def test_run_resolution_phases_broken_spell_raises(monkeypatch):
    """
    Purpose:
        Ensure broken spells cause validation errors.
    Contract:
        _run_resolution_phases raises SpellbookValidationError for broken spells.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()

    class BrokenSpell(DummySpell):
        """
        Purpose:
            Provide a spell stub that reports broken status.
        Contract:
            is_broken always returns True.
        """
        @property
        def is_broken(self):
            """
            Purpose:
                Indicate broken status for the stub.
            Contract:
                Always returns True.
            Returns:
                bool: True for the broken spell.
            """
            return True

    sb._spells = {DummySpellIndex(): BrokenSpell()}
    sb._logger = DummySafeLogger()
    with pytest.raises(SpellbookValidationError):
        sb._run_resolution_phases("cid")


def test_run_resolution_phases_spell_status_error_treated_as_broken():
    """
    Purpose:
        Verify errors while checking spell status are treated as broken.
    Contract:
        _run_resolution_phases raises SpellbookValidationError on status errors.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()

    class ErrorSpell(DummySpell):
        """
        Purpose:
            Provide a spell stub that raises on status checks.
        Contract:
            is_broken raises RuntimeError.
        """
        @property
        def is_broken(self):
            """
            Purpose:
                Simulate a status check failure.
            Contract:
                Raises RuntimeError on access.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("oops")

    sb._spells = {DummySpellIndex(): ErrorSpell()}
    sb._logger = DummySafeLogger()
    with pytest.raises(SpellbookValidationError):
        sb._run_resolution_phases("cid")


def test_run_resolution_phases_cleans_scheduler_on_exception(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup occurs when phase execution fails.
    Contract:
        _run_resolution_phases raises and cleanup is still invoked.
    Args:
        monkeypatch: Pytest fixture for patching PhaseScheduler.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._logger = DummySafeLogger()

    class BoomScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler stub that raises on execution.
        Contract:
            run_all_phases raises RuntimeError.
        """
        def run_all_phases(self):
            """
            Purpose:
                Simulate execution failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", BoomScheduler)
    with pytest.raises(RuntimeError):
        sb._run_resolution_phases("cid")


def test_get_conjure_hook_map_no_config_returns_none():
    """
    Purpose:
        Ensure hook map returns None when configuration is missing.
    Contract:
        _get_conjure_hook_map returns None without a configuration.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = None
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_config_without_get_hooks_returns_none():
    """
    Purpose:
        Verify hook lookup returns None for configurations without hooks.
    Contract:
        _get_conjure_hook_map returns None when get_hooks is missing or empty.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    class BadConfig:
        """
        Purpose:
            Provide a configuration stub without hooks.
        Contract:
            get_hooks returns None for any id.
        """
        def get_hooks(self, sid):
            """
            Purpose:
                Return no hooks for the requested id.
            Contract:
                Always returns None.
            Args:
                sid: Spellbook id requested by caller.
            Returns:
                None.
            """
            return None

    sb = Spellbook(configuration=DummyConfig())
    sb._configuration = BadConfig()
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_empty_returns_none():
    """
    Purpose:
        Ensure empty hook maps are treated as absent.
    Contract:
        _get_conjure_hook_map returns None when hook map is empty.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    cfg = DummyConfig(hooks={})
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_get_conjure_hook_map_returns_map():
    """
    Purpose:
        Verify configured hooks are returned to the caller.
    Contract:
        _get_conjure_hook_map returns the stored hooks mapping.
    Returns:
        None.
    Raises:
        AssertionError: If the mapping does not match.
    """
    hooks = {"on_conduit_pre_created": [lambda: None]}
    cfg = DummyConfig(hooks=hooks)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() == hooks


def test_fire_conjure_hooks_executes_and_swallows_errors():
    """
    Purpose:
        Ensure conjure hooks execute in order and swallow errors.
    Contract:
        Errors in hooks do not stop subsequent hook execution.
    Returns:
        None.
    Raises:
        AssertionError: If hook execution order is incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    called = []

    def ok(arg=None):
        """
        Purpose:
            Record a successful hook invocation.
        Contract:
            Appends the tag and argument to the called list.
        Args:
            arg: Optional argument passed to the hook.
        Returns:
            None.
        """
        called.append(("ok", arg))

    def boom(arg=None):
        """
        Purpose:
            Simulate a failing hook invocation.
        Contract:
            Raises RuntimeError for all calls.
        Args:
            arg: Optional argument passed to the hook.
        Raises:
            RuntimeError: Always raised for the stub.
        """
        raise RuntimeError("boom")

    sb._fire_conjure_hooks({"h": [ok, boom, ok]}, "h", "arg")
    assert called == [("ok", "arg"), ("ok", "arg")]


def test_cleanup_idempotent_and_clears_fields():
    """
    Purpose:
        Verify cleanup is idempotent and clears core references.
    Contract:
        cleanup nulls key fields and marks the Spellbook as cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If fields are not cleared or cleaned flag is wrong.
    """
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
    """
    Purpose:
        Ensure cleanup of spells continues when a spell cleanup fails.
    Contract:
        _cleanup_spells cleans remaining spells despite exceptions.
    Returns:
        None.
    Raises:
        AssertionError: If cleanable spells are not cleaned.
    """
    sb = Spellbook()

    class BoomSpell(DummySpell):
        """
        Purpose:
            Provide a spell stub that raises on cleanup.
        Contract:
            cleanup raises RuntimeError to simulate failure.
        """
        def cleanup(self):
            """
            Purpose:
                Simulate a cleanup failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    s1 = DummySpell()
    s2 = BoomSpell()
    sb._spells = {DummySpellIndex(): s1, DummySpellIndex(): s2}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert s1.cleaned is True


def test_properties_return_proxies():
    """
    Purpose:
        Verify spells property returns a mapping proxy.
    Contract:
        spells exposes a MappingProxyType with the same entries.
    Returns:
        None.
    Raises:
        AssertionError: If proxy type or contents are incorrect.
    """
    sb = Spellbook()
    idx = DummySpellIndex()
    spell = DummySpell()
    sb._spells = {idx: spell}
    proxy = sb.spells
    assert isinstance(proxy, MappingProxyType)
    assert proxy[idx] is spell


def test_contracted_spells_property_returns_nested_proxies():
    """
    Purpose:
        Ensure contracted spells property returns nested proxies.
    Contract:
        contracted_spells returns MappingProxyType values for each conduit.
    Returns:
        None.
    Raises:
        AssertionError: If proxies are not returned as expected.
    """
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
    """
    Purpose:
        Verify Spellbook context manager acquires and releases the lock.
    Contract:
        __enter__ returns self and lock remains usable after exit.
    Returns:
        None.
    Raises:
        AssertionError: If context manager behavior is incorrect.
    """
    sb = Spellbook()
    with sb as ctx:
        assert ctx is sb
    assert sb._lock.acquire() is None or sb._lock.acquire() is True
    sb._lock.release()


def test_initialize_logging_upgrade_aether_logger(monkeypatch):
    """
    Purpose:
        Ensure upgrade does not replace an existing aether logger.
    Contract:
        _upgrade_aether_logger_if_possible keeps the existing logger.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If aether logger is replaced.
    """
    sb = Spellbook(configuration=DummyConfig(logger_factory=DummyLogger()))
    sb._logger = DummySafeLogger()
    original_logger = Spellbook._aether._logger
    # Force Aether logger to appear already-real so no upgrade occurs.
    sb._upgrade_aether_logger_if_possible()
    assert Spellbook._aether._logger is original_logger


def test_initialize_logging_does_not_upgrade_without_factory():
    """
    Purpose:
        Verify logger upgrade is skipped when no factory exists.
    Contract:
        _upgrade_aether_logger_if_possible leaves the logger unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If the logger is replaced without a factory.
    """
    sb = Spellbook(configuration=DummyConfig(logger_factory=None))
    original = Spellbook._aether._logger
    sb._logger = DummySafeLogger()
    sb._upgrade_aether_logger_if_possible()
    assert Spellbook._aether._logger is original


def test_run_resolution_phases_scheduler_cleanup_failure_logged(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup failures are swallowed and logged.
    Contract:
        _run_resolution_phases completes even if scheduler.cleanup fails.
    Args:
        monkeypatch: Pytest fixture for patching PhaseScheduler.
    Returns:
        None.
    Raises:
        AssertionError: If phase results are missing.
    """
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    class CleanupBoomScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler stub that fails during cleanup.
        Contract:
            cleanup raises RuntimeError.
        """
        def cleanup(self):
            """
            Purpose:
                Simulate cleanup failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("fail")

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", CleanupBoomScheduler)
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases("cid")
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
    """
    Purpose:
        Validate policy/state combinations against automatic mode rules.
    Contract:
        _check_system_state raises only when expect_raises is True.
    Args:
        policy: Policy value under test.
        automatic: Whether automatic mode is enabled.
        expect_raises: Whether a RuntimeError is expected.
    Returns:
        None.
    Raises:
        AssertionError: If behavior diverges from expect_raises.
    """
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
    """
    Purpose:
        Ensure get_spell_permissions returns the assigned permission.
    Contract:
        Returned permission name matches the spell's permission value.
    Args:
        perm: Permission enum assigned to the spell.
    Returns:
        None.
    Raises:
        AssertionError: If the permission name is incorrect.
    """
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
    """
    Purpose:
        Verify local spell version refresh handles multiple inputs.
    Contract:
        _refresh_local_spell_versions reflects the provided version set.
    Args:
        versions: Version set to apply to the index.
    Returns:
        None.
    Raises:
        AssertionError: If the refreshed versions are incorrect.
    """
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
    """
    Purpose:
        Ensure no-op hook combinations produce no calls.
    Contract:
        _fire_conjure_hooks leaves the call log unchanged in no-op cases.
    Args:
        hook_map: Hook mapping to test.
        hook_name: Hook name requested.
        expected_calls: Expected call list after invocation.
    Returns:
        None.
    Raises:
        AssertionError: If calls are recorded unexpectedly.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    called = []

    def wrapper(*args):
        """
        Purpose:
            Record hook invocations for assertions.
        Contract:
            Appends the arguments tuple to the call log.
        Args:
            *args: Hook invocation arguments.
        Returns:
            None.
        """
        called.append(args)

    if hook_map and "h" in hook_map and hook_map["h"]:
        hook_map = {"h": [wrapper]}

    sb._fire_conjure_hooks(hook_map, hook_name, "x")
    assert called == expected_calls


@pytest.mark.parametrize(
    "hooks,expected_none",
    [
        ({}, True),
        ({"on_conduit_pre_created": []}, False),
        ({"on_conduit_pre_created": [lambda: None]}, False),
    ],
)
def test_get_conjure_hook_map_variants(hooks, expected_none):
    """
    Purpose:
        Validate hook map return behavior for different configurations.
    Contract:
        _get_conjure_hook_map returns None or the hooks mapping as expected.
    Args:
        hooks: Hook mapping configured on the DummyConfig.
        expected_none: Whether None is expected.
    Returns:
        None.
    Raises:
        AssertionError: If the return value is incorrect.
    """
    cfg = DummyConfig(hooks=hooks)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    result = sb._get_conjure_hook_map()
    if expected_none:
        assert result is None
    else:
        assert result == hooks


@pytest.mark.parametrize(
    "existing_object",
    [None, "obj1", {"x": 1}],
)
def test_define_conduit_handles_multiple_objects(existing_object):
    """
    Purpose:
        Ensure conduit definition handles various existing object types.
    Contract:
        _define_conduit_into_spells sets owner metadata for the spell.
    Args:
        existing_object: Existing object bound to the spell.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata is not set.
    """
    sb = Spellbook()
    conduit = DummyConduit()
    spell = DummySpell(existing_object=existing_object)
    sb._spells = {DummySpellIndex(): spell}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(conduit)
    assert conduit._id in spell._owner


def test_refresh_contracted_spell_versions_handles_empty_maps():
    """
    Purpose:
        Verify contracted version refresh handles empty contracted maps.
    Contract:
        _refresh_contracted_spell_versions leaves contracted_versions empty.
    Returns:
        None.
    Raises:
        AssertionError: If contracted_versions is mutated unexpectedly.
    """
    sb = Spellbook()
    sb._contracted_spells = {}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions == {}


def test_phase_factories_return_empty_when_no_spells():
    """
    Purpose:
        Ensure phase factories return empty lists when no spells exist.
    Contract:
        All phase factories return empty unit lists with no spells.
    Returns:
        None.
    Raises:
        AssertionError: If any factory returns non-empty units.
    """
    sb = Spellbook()
    sb._spells = {}
    scheduler = DummyPhaseScheduler(sb, None)
    assert sb._phase_requirements_factory(scheduler) == []
    assert sb._phase_symbolic_graph_factory(scheduler) == []
    assert sb._phase_local_frame_factory(scheduler) == []
    assert sb._phase_validation_factory(scheduler) == []
    assert sb._phase_root_blueprints_factory(scheduler, "cid") == []
    assert sb._phase_system_validation_factory(scheduler, "cid") == []
    assert sb._phase_change_control_factory(scheduler, "cid") == []


def test_run_resolution_phases_with_multiple_spells():
    """
    Purpose:
        Verify resolution phases run with multiple spells present.
    Contract:
        _run_resolution_phases returns all expected phase keys.
    Returns:
        None.
    Raises:
        AssertionError: If expected keys are missing.
    """
    sb = Spellbook()
    spell1 = DummySpell(spell_id="a")
    spell2 = DummySpell(spell_id="b")
    sb._spells = {DummySpellIndex(sid="a"): spell1, DummySpellIndex(sid="b"): spell2}
    sb._logger = DummySafeLogger()
    results = sb._run_resolution_phases("cid")
    assert set(results.keys()) == {
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "system_validation",
        "change_control",
    }


def test_find_contracted_spell_raises_when_missing():
    """
    Purpose:
        Ensure contracted spell lookup raises when missing.
    Contract:
        _find_contracted_spell raises RuntimeError when no spell is found.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb._find_contracted_spell(DummySpellIndex())


def test_cleanup_spells_is_safe_when_none():
    """
    Purpose:
        Verify cleanup handles a None spell map safely.
    Contract:
        _cleanup_spells returns without raising and keeps _spells as None.
    Returns:
        None.
    Raises:
        AssertionError: If _spells is mutated unexpectedly.
    """
    sb = Spellbook()
    sb._spells = None
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert sb._spells is None


def test_cleanup_components_clears_contracts_and_versions():
    """
    Purpose:
        Ensure cleanup clears contracted maps and version caches.
    Contract:
        _cleanup_components nulls contracted spell maps and version caches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted state is not cleared.
    """
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
    """
    Purpose:
        Verify core cleanup nulls key references and handles logger safely.
    Contract:
        _cleanup_core clears bind, lock, and logger references.
    Returns:
        None.
    Raises:
        AssertionError: If core references remain set.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_core()
    assert sb._bind is None
    assert sb._lock is None
    assert sb._logger is None


def test_context_manager_reacquire_after_exit():
    """
    Purpose:
        Ensure the Spellbook lock is usable after context exit.
    Contract:
        Lock can be acquired again after leaving the context manager.
    Returns:
        None.
    Raises:
        AssertionError: If the lock cannot be acquired.
    """
    sb = Spellbook()
    with sb:
        pass
    assert sb._lock.acquire() is None or sb._lock.acquire() is True
    sb._lock.release()


def test_get_spell_permissions_missing_logs_and_raises():
    """
    Purpose:
        Ensure missing permission lookups raise consistently.
    Contract:
        get_spell_permissions raises RuntimeError for missing indices.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        sb.get_spell_permissions(DummySpellIndex())


def test_spells_property_is_immutable():
    """
    Purpose:
        Verify the spells property returns an immutable proxy.
    Contract:
        Assignment through the proxy raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If mutation does not raise.
    """
    sb = Spellbook()
    idx = DummySpellIndex()
    sb._spells = {idx: DummySpell()}
    proxy = sb.spells
    mutable = cast(MutableMapping[DummySpellIndex, DummySpell], proxy)
    with pytest.raises(TypeError):
        mutable[idx] = None


def test_contracted_spells_property_is_immutable():
    """
    Purpose:
        Verify contracted_spells returns immutable nested proxies.
    Contract:
        Assignment into the proxy raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If mutation does not raise.
    """
    sb = Spellbook()
    idx = DummySpellIndex()
    sb._contracted_spells = {"c": {idx: DummySpell()}}
    proxy = sb.contracted_spells
    mutable = cast(MutableMapping[str, object], proxy)
    with pytest.raises(TypeError):
        mutable["c"] = {}


def test_refresh_local_spell_versions_noop_when_cache_none():
    """
    Purpose:
        Ensure refresh does nothing when the version cache is None.
    Contract:
        _refresh_local_spell_versions leaves _spell_versions as None.
    Returns:
        None.
    Raises:
        AssertionError: If the cache is modified unexpectedly.
    """
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._spell_versions = None
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions is None


def test_refresh_contracted_spell_versions_noop_when_none():
    """
    Purpose:
        Verify contracted refresh is a no-op when contracted_spells is None.
    Contract:
        _refresh_contracted_spell_versions preserves contracted_versions.
    Returns:
        None.
    Raises:
        AssertionError: If contracted_versions is mutated.
    """
    sb = Spellbook()
    sb._contracted_spells = None
    sb._contracted_versions = {"x": {"v"}}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions == {"x": {"v"}}


def test_refresh_all_spell_versions_safe_when_contracted_none(monkeypatch):
    """
    Purpose:
        Ensure refresh-all works when contracted state is None.
    Contract:
        Both refresh helpers are invoked even with no contracted maps.
    Args:
        monkeypatch: Pytest fixture for patching instance methods.
    Returns:
        None.
    Raises:
        AssertionError: If either helper is skipped.
    """
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
    """
    Purpose:
        Verify hook execution continues after errors.
    Contract:
        _fire_conjure_hooks executes all hooks and ignores failures.
    Returns:
        None.
    Raises:
        AssertionError: If call order is incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    calls = []

    def ok(x):
        """
        Purpose:
            Record a hook call.
        Contract:
            Appends the value to the calls list.
        Args:
            x: Hook argument.
        Returns:
            None.
        """
        calls.append(("ok", x))

    def boom(x):
        """
        Purpose:
            Simulate a failing hook.
        Contract:
            Raises RuntimeError for any call.
        Args:
            x: Hook argument.
        Raises:
            RuntimeError: Always raised for the stub.
        """
        raise RuntimeError("boom")

    sb._fire_conjure_hooks({"h": [ok, boom, ok]}, "h", "val")
    assert calls == [("ok", "val"), ("ok", "val")]


def test_get_conjure_hook_map_handles_exception():
    """
    Purpose:
        Ensure exceptions during hook lookup are swallowed.
    Contract:
        _get_conjure_hook_map returns None when get_hooks raises.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    class RaisingConfig(DummyConfig):
        """
        Purpose:
            Provide a configuration stub that raises on subsequent hook lookup.
        Contract:
            get_hooks returns None once, then raises RuntimeError.
        """
        def __init__(self):
            """
            Purpose:
                Initialize the raising config stub.
            Contract:
                Sets up a call counter.
            Returns:
                None.
            """
            super().__init__()
            self.calls = 0

        def get_hooks(self, sid):
            """
            Purpose:
                Provide hooks or raise after the first call.
            Contract:
                Returns None on first call and raises thereafter.
            Args:
                sid: Spellbook id requested by caller.
            Returns:
                None.
            Raises:
                RuntimeError: After the first call.
            """
            self.calls += 1
            if self.calls == 1:
                return None
            raise RuntimeError("fail")

    sb = Spellbook(configuration=RaisingConfig())
    sb._logger = DummySafeLogger()
    assert sb._get_conjure_hook_map() is None


def test_upgrade_aether_logger_ignores_factory_errors(monkeypatch):
    """
    Purpose:
        Verify logger upgrade ignores factory exceptions.
    Contract:
        _upgrade_aether_logger_if_possible does not propagate factory errors.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If logger upgrade fails incorrectly.
    """
    class BadConfig(DummyConfig):
        """
        Purpose:
            Provide a configuration stub that raises when building loggers.
        Contract:
            get_logger_for raises RuntimeError.
        """
        def has_logger_factory(self):
            """
            Purpose:
                Indicate a logger factory is present.
            Contract:
                Always returns True.
            Returns:
                bool: True for the stub.
            """
            return True

        def get_logger_for(self, _owner):
            """
            Purpose:
                Simulate logger factory failure.
            Contract:
                Raises RuntimeError unconditionally.
            Args:
                _owner: Spellbook owner identifier.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    sb = Spellbook(configuration=BadConfig())
    sb._logger = DummySafeLogger()
    sb._upgrade_aether_logger_if_possible()
    assert isinstance(sb._logger, DummySafeLogger)


def test_initialize_logging_fallback_on_factory_failure(monkeypatch):
    """
    Purpose:
        Ensure initialization falls back when logger factory fails.
    Contract:
        Spellbook uses DummySafeLogger even if factory raises.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If fallback logger is not set.
    """
    class BadConfig(DummyConfig):
        """
        Purpose:
            Provide a configuration stub that raises during logger resolution.
        Contract:
            get_logger_for raises RuntimeError.
        """
        def has_logger_factory(self):
            """
            Purpose:
                Indicate a logger factory is present.
            Contract:
                Always returns True.
            Returns:
                bool: True for the stub.
            """
            return True

        def get_logger_for(self, _owner):
            """
            Purpose:
                Simulate logger factory failure.
            Contract:
                Raises RuntimeError unconditionally.
            Args:
                _owner: Spellbook owner identifier.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    sb = Spellbook(configuration=BadConfig())
    assert isinstance(sb._logger, DummySafeLogger)


def test_cleanup_spells_invokes_cleanup_on_each_spell():
    """
    Purpose:
        Verify cleanup invokes each spell's cleanup hook.
    Contract:
        _cleanup_spells marks every spell as cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If any spell is left uncleaned.
    """
    sb = Spellbook()
    s1 = DummySpell()
    s2 = DummySpell()
    sb._spells = {DummySpellIndex(): s1, DummySpellIndex(): s2}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert s1.cleaned and s2.cleaned


def test_cleanup_components_handles_none_configuration():
    """
    Purpose:
        Ensure cleanup tolerates a missing configuration.
    Contract:
        _cleanup_components completes when _configuration is None.
    Returns:
        None.
    Raises:
        AssertionError: If configuration is unexpectedly set.
    """
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
    """
    Purpose:
        Verify core cleanup swallows logger cleanup errors.
    Contract:
        _cleanup_core handles logger cleanup exceptions and nulls logger.
    Returns:
        None.
    Raises:
        AssertionError: If logger is not cleared.
    """
    class BadLogger(DummySafeLogger):
        """
        Purpose:
            Provide a logger stub that fails during cleanup.
        Contract:
            cleanup raises RuntimeError.
        """
        def cleanup(self):
            """
            Purpose:
                Simulate logger cleanup failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("cleanup fail")

    sb = Spellbook()
    sb._logger = BadLogger()
    sb._cleanup_core()
    assert sb._logger is None


def test_run_resolution_phases_cleans_scheduler_even_on_error(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup runs even when phases fail.
    Contract:
        _run_resolution_phases raises and still cleans the scheduler.
    Args:
        monkeypatch: Pytest fixture for patching PhaseScheduler.
    Returns:
        None.
    Raises:
        AssertionError: If scheduler is not cleaned.
    """
    class ExplodingScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler stub that raises during execution.
        Contract:
            run_all_phases raises RuntimeError.
        """
        def run_all_phases(self):
            """
            Purpose:
                Simulate phase execution failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    sched = ExplodingScheduler(None, None)
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._logger = DummySafeLogger()
    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", lambda *a, **k: sched)
    with pytest.raises(RuntimeError):
        sb._run_resolution_phases("cid")
    assert sched.cleaned is True


def test_find_spell_count_reports_len():
    """
    Purpose:
        Verify _find_spell_count returns the number of local spells.
    Contract:
        Count matches the length of the _spells mapping.
    Returns:
        None.
    Raises:
        AssertionError: If the count is incorrect.
    """
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
    """
    Purpose:
        Ensure contracted version refresh handles multiple version sets.
    Contract:
        _refresh_contracted_spell_versions records the expected set.
    Args:
        spell_versions: Version ids attached to the contracted index.
        expected: Expected version set stored after refresh.
    Returns:
        None.
    Raises:
        AssertionError: If stored versions are incorrect.
    """
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions=spell_versions): DummySpell()}}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions["c"] == expected


def test_phase_factories_metadata_contains_spell_id():
    """
    Purpose:
        Verify phase factory metadata includes spell_id.
    Contract:
        Each unit metadata contains the originating spell_id.
    Returns:
        None.
    Raises:
        AssertionError: If spell_id is missing in metadata.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="abc")
    sb._spells = {DummySpellIndex(sid="abc"): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    for units in (
        sb._phase_requirements_factory(scheduler),
        sb._phase_symbolic_graph_factory(scheduler),
        sb._phase_local_frame_factory(scheduler),
        sb._phase_validation_factory(scheduler),
        sb._phase_root_blueprints_factory(scheduler, "cid"),
        sb._phase_system_validation_factory(scheduler, "cid"),
        sb._phase_change_control_factory(scheduler, "cid"),
    ):
        assert units[0]["metadata"]["spell_id"] == "abc"


def test_context_manager_after_cleanup_raises_on_lock_use():
    """
    Purpose:
        Ensure context manager fails after cleanup.
    Contract:
        __enter__ raises when the Spellbook has been cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If __enter__ does not raise.
    """
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
    """
    Purpose:
        Verify policy-specific flags are set correctly.
    Contract:
        _set_policy_state sets block/whitelist flags based on policy.
    Args:
        policy: Policy value under test.
    Returns:
        None.
    Raises:
        AssertionError: If flags do not match the policy.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._lock = DummyLock = type("DL", (), {"__enter__": lambda s: None, "__exit__": lambda s, a, b, c: None})()
    sb._set_policy_state(policy)
    if policy == Policies.block_all:
        assert sb._block_all_spells is True
    elif policy == Policies.whitelist_all:
        assert sb._whitelist_all_spells is True
    else:
        # default policy should clear flags
        assert sb._block_all_spells is False
        assert sb._whitelist_all_spells is False


def test_find_spell_returns_none_for_missing():
    """
    Purpose:
        Ensure _find_spell returns None for missing indices.
    Contract:
        _find_spell returns None when the index is absent.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    assert sb._find_spell(DummySpellIndex()) is None


def test_refresh_local_spell_versions_noop_when_spells_none():
    """
    Purpose:
        Verify local version refresh is a no-op when spells is None.
    Contract:
        _refresh_local_spell_versions leaves _spell_versions unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If the cache is modified unexpectedly.
    """
    sb = Spellbook()
    sb._spells = None
    sb._spell_versions = set()
    sb._logger = DummySafeLogger()
    sb._refresh_local_spell_versions()
    assert sb._spell_versions == set()


def test_cleanup_spells_cleans_index_even_when_spell_raises():
    """
    Purpose:
        Ensure spell index cleanup occurs even if spell cleanup fails.
    Contract:
        _cleanup_spells cleans spell index objects regardless of spell errors.
    Returns:
        None.
    Raises:
        AssertionError: If spell indices are not cleaned.
    """
    class BoomSpell(DummySpell):
        """
        Purpose:
            Provide a spell stub that raises during cleanup.
        Contract:
            cleanup raises RuntimeError.
        """
        def cleanup(self):
            """
            Purpose:
                Simulate spell cleanup failure.
            Contract:
                Raises RuntimeError unconditionally.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    idx = DummySpellIndex()
    spell = BoomSpell()
    sb = Spellbook()
    sb._spells = {idx: spell}
    sb._logger = DummySafeLogger()
    sb._cleanup_spells()
    assert idx.cleaned is True


def test_cleanup_components_idempotent():
    """
    Purpose:
        Verify _cleanup_components can be called multiple times.
    Contract:
        Repeated cleanup leaves _spells as None without raising.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    sb._cleanup_components()
    assert sb._spells is None


def test_cleanup_core_handles_logger_none():
    """
    Purpose:
        Ensure _cleanup_core handles logger teardown gracefully.
    Contract:
        _cleanup_core clears the bind reference even when logger exists.
    Returns:
        None.
    Raises:
        AssertionError: If bind is not cleared.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_core()
    assert sb._bind is None


def test_fire_conjure_hooks_passes_args_and_kwargs():
    """
    Purpose:
        Verify hook invocation passes positional and keyword arguments.
    Contract:
        _fire_conjure_hooks passes provided args to the hook.
    Returns:
        None.
    Raises:
        AssertionError: If hook arguments are incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    captured = []

    def hook(a, b=None):
        """
        Purpose:
            Capture hook arguments for assertions.
        Contract:
            Appends the arguments tuple to captured.
        Args:
            a: First positional argument.
            b: Optional keyword argument.
        Returns:
            None.
        """
        captured.append((a, b))

    sb._fire_conjure_hooks({"h": [hook]}, "h", "x")
    assert captured == [("x", None)]


def test_define_conduit_handles_missing_owner_method():
    """
    Purpose:
        Ensure conduit definition tolerates owner hook failures.
    Contract:
        _define_conduit_into_spells invokes the hook and swallows errors.
    Returns:
        None.
    Raises:
        AssertionError: If the hook is not invoked.
    """
    class SpellNoOwner(DummySpell):
        """
        Purpose:
            Provide a spell stub that fails to accept ownership.
        Contract:
            _add_owned_conduit raises RuntimeError and counts calls.
        """
        def _add_owned_conduit(self, *a, **k):
            """
            Purpose:
                Simulate ownership hook failure.
            Contract:
                Increments call counter and raises RuntimeError.
            Args:
                *a: Positional arguments.
                **k: Keyword arguments.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            self.calls += 1
            raise RuntimeError("nope")

    sb = Spellbook()
    spell = SpellNoOwner()
    spell.calls = 0
    sb._spells = {DummySpellIndex(): spell}
    sb._logger = DummySafeLogger()
    sb._define_conduit_into_spells(DummyConduit())
    assert spell.calls == 1


def test_refresh_contracted_spell_versions_ignores_empty_versions():
    """
    Purpose:
        Verify contracted version refresh handles empty version sets.
    Contract:
        _refresh_contracted_spell_versions stores empty sets for empty versions.
    Returns:
        None.
    Raises:
        AssertionError: If the empty set is not recorded.
    """
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions=set()): DummySpell()}}
    sb._contracted_versions = {}
    sb._logger = DummySafeLogger()
    sb._refresh_contracted_spell_versions()
    assert sb._contracted_versions["c"] == set()


def test_phase_factories_return_distinct_labels_per_spell():
    """
    Purpose:
        Ensure phase factories label units per spell.
    Contract:
        Each spell yields a distinct label in the units list.
    Returns:
        None.
    Raises:
        AssertionError: If labels are missing or duplicated.
    """
    sb = Spellbook()
    s1 = DummySpell(spell_id="a")
    s2 = DummySpell(spell_id="b")
    sb._spells = {DummySpellIndex(sid="a"): s1, DummySpellIndex(sid="b"): s2}
    scheduler = DummyPhaseScheduler(sb, None)
    req_units = sb._phase_requirements_factory(scheduler)
    assert {u["label"] for u in req_units} == {"requirements:a", "requirements:b"}


def test_set_policy_state_resets_flags_on_default():
    """
    Purpose:
        Verify default policy clears prior policy flags.
    Contract:
        _set_policy_state resets block/whitelist flags for default policy.
    Returns:
        None.
    Raises:
        AssertionError: If flags are not cleared.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._lock = type("DL", (), {"__enter__": lambda s: None, "__exit__": lambda s, a, b, c: None})()
    sb._set_policy_state(Policies.block_all)
    assert sb._block_all_spells is True
    sb._set_policy_state(Policies.default)
    assert sb._block_all_spells is False
    assert sb._whitelist_all_spells is False


def test_check_all_spells_raises_on_duplicate(monkeypatch):
    """
    Purpose:
        Ensure duplicate spell versions raise during validation.
    Contract:
        _check_all_spells raises RuntimeError when a duplicate is detected.
    Args:
        monkeypatch: Pytest fixture for patching aether checks.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()
    idx = DummySpellIndex(versions={"dup"})
    sb._spells = {idx: DummySpell()}
    sb._logger = DummySafeLogger()

    def fake_check_for_spell(version_id, frame):
        """
        Purpose:
            Simulate a duplicate spell detection.
        Contract:
            Always returns True to indicate duplication.
        Args:
            version_id: Version id to check.
            frame: Aetheric frame identifier.
        Returns:
            bool: True to indicate a duplicate.
        """
        return True

    monkeypatch.setattr(Spellbook._aether, "_check_for_spell", fake_check_for_spell)
    with pytest.raises(RuntimeError):
        sb._check_all_spells()


def test_check_all_spells_passes_when_unique(monkeypatch):
    """
    Purpose:
        Verify unique spell versions pass validation.
    Contract:
        _check_all_spells completes when duplicates are not reported.
    Args:
        monkeypatch: Pytest fixture for patching aether checks.
    Returns:
        None.
    Raises:
        AssertionError: If _check_all_spells raises unexpectedly.
    """
    sb = Spellbook()
    idx = DummySpellIndex(versions={"unique"})
    sb._spells = {idx: DummySpell()}
    sb._logger = DummySafeLogger()

    def fake_check_for_spell(version_id, frame):
        """
        Purpose:
            Simulate no duplicate detection.
        Contract:
            Always returns False to indicate uniqueness.
        Args:
            version_id: Version id to check.
            frame: Aetheric frame identifier.
        Returns:
            bool: False to indicate no duplicate.
        """
        return False

    monkeypatch.setattr(Spellbook._aether, "_check_for_spell", fake_check_for_spell)
    sb._check_all_spells()


def test_find_contracted_spell_by_id_finds_match():
    """
    Purpose:
        Verify contracted spell lookup by version id finds a match.
    Contract:
        _find_contracted_spell_by_id returns the matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If the matching spell is not returned.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="id1")
    idx = DummySpellIndex(versions={"v1"})
    sb._contracted_spells = {"c": {idx: spell}}
    assert sb._find_contracted_spell_by_id("v1", "c") is spell


def test_find_contracted_spell_by_id_returns_none_when_missing():
    """
    Purpose:
        Ensure contracted lookup returns None when version id is missing.
    Contract:
        _find_contracted_spell_by_id returns None for unknown versions.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned unexpectedly.
    """
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions={"v1"}): DummySpell()}}
    assert sb._find_contracted_spell_by_id("v2", "c") is None


def test_find_contracted_spell_by_id_returns_none_for_unknown_conduit():
    """
    Purpose:
        Ensure contracted lookup returns None for unknown conduit ids.
    Contract:
        _find_contracted_spell_by_id returns None when conduit is missing.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned unexpectedly.
    """
    sb = Spellbook()
    sb._contracted_spells = {"c": {DummySpellIndex(versions={"v1"}): DummySpell()}}
    assert sb._find_contracted_spell_by_id("v1", "missing") is None


def test_create_link_contract_initializes_maps():
    """
    Purpose:
        Verify link contract initialization creates all tracking maps.
    Contract:
        _create_link_contract populates contracted maps for the conduit id.
    Returns:
        None.
    Raises:
        AssertionError: If any map is missing the conduit id.
    """
    sb = Spellbook()
    sb._contracted_spells = {}
    sb._lookup_contracted_spells = {}
    sb._contracted_versions = {}
    sb._create_link_contract("cid")
    assert "cid" in sb._contracted_spells
    assert "cid" in sb._lookup_contracted_spells
    assert "cid" in sb._contracted_versions


def test_inspect_spell_returns_none_on_missing(monkeypatch):
    """
    Purpose:
        Ensure inspect_spell returns None when a spell is missing.
    Contract:
        inspect_spell returns None when aether check fails.
    Args:
        monkeypatch: Pytest fixture for patching aether checks.
    Returns:
        None.
    Raises:
        AssertionError: If a non-None id is returned.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._bind = types.SimpleNamespace(spell_id_inspector=lambda s: "id")
    monkeypatch.setattr(Spellbook._aether, "_check_for_spell", lambda *_: False)
    assert sb.inspect_spell(DummySpell()) is None


def test_inspect_spell_returns_id_when_found(monkeypatch):
    """
    Purpose:
        Verify inspect_spell returns an id when the spell exists.
    Contract:
        inspect_spell returns the inspector id when aether check passes.
    Args:
        monkeypatch: Pytest fixture for patching aether checks.
    Returns:
        None.
    Raises:
        AssertionError: If the returned id is incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._bind = types.SimpleNamespace(spell_id_inspector=lambda s: "id")
    monkeypatch.setattr(Spellbook._aether, "_check_for_spell", lambda *_: True)
    assert sb.inspect_spell(DummySpell()) == "id"


def test_validate_and_freeze_configuration_happy_path():
    """
    Purpose:
        Verify configuration validation and freeze succeeds.
    Contract:
        _validate_and_freeze_configuration locks configuration and freezes it.
    Returns:
        None.
    Raises:
        AssertionError: If configuration is not locked or frozen.
    """
    cfg = DummyConfig(frozen=False, validate_ok=True)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    sb._configuration = cfg
    sb._validate_and_freeze_configuration()
    assert sb._configuration_locked is True
    assert cfg._frozen is True


def test_validate_and_freeze_configuration_missing_raises():
    """
    Purpose:
        Ensure validation raises when configuration is missing.
    Contract:
        _validate_and_freeze_configuration raises RuntimeError when None.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = None
    with pytest.raises(RuntimeError):
        sb._validate_and_freeze_configuration()


def test_validate_and_freeze_configuration_frozen_short_circuits():
    """
    Purpose:
        Verify frozen configurations short-circuit validation.
    Contract:
        _validate_and_freeze_configuration sets locked when already frozen.
    Returns:
        None.
    Raises:
        AssertionError: If the configuration is not locked.
    """
    cfg = DummyConfig(frozen=True)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    sb._configuration = cfg
    sb._configuration_locked = False
    sb._validate_and_freeze_configuration()
    assert sb._configuration_locked is True


def test_validate_and_freeze_configuration_validation_failure_raises():
    """
    Purpose:
        Ensure validation failure raises ValueError.
    Contract:
        _validate_and_freeze_configuration raises when validate() fails.
    Returns:
        None.
    Raises:
        AssertionError: If validation failure does not raise.
    """
    cfg = DummyConfig(frozen=False, validate_ok=False)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    sb._configuration = cfg
    with pytest.raises(ValueError):
        sb._validate_and_freeze_configuration()


def test_run_resolution_phases_cleans_scheduler_on_success(monkeypatch):
    """
    Purpose:
        Verify scheduler cleanup occurs on successful phase execution.
    Contract:
        _run_resolution_phases cleans the scheduler after completion.
    Args:
        monkeypatch: Pytest fixture for patching PhaseScheduler.
    Returns:
        None.
    Raises:
        AssertionError: If scheduler is not cleaned.
    """
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    schedulers: list[DummyPhaseScheduler] = []
    sb._logger = DummySafeLogger()
    # Patch constructor to return our scheduler so we can check cleaned flag.
    import melder.spellbook.spellbook as spellbook_module
    def _make_scheduler(*args, **kwargs):
        sched = DummyPhaseScheduler(*args, **kwargs)
        sched.cleaned = False
        schedulers.append(sched)
        return sched
    monkeypatch.setattr(spellbook_module, "PhaseScheduler", _make_scheduler)
    results = sb._run_resolution_phases("cid")
    assert "requirements" in results
    assert schedulers
    assert all(sched.cleaned is True for sched in schedulers)


def test_conjure_hooks_fire_in_order(monkeypatch):
    """
    Purpose:
        Verify conjure hooks fire in the expected order.
    Contract:
        Pre, activated, and post hooks are invoked in sequence.
    Args:
        monkeypatch: Pytest fixture for patching Conduit and scheduler classes.
    Returns:
        None.
    Raises:
        AssertionError: If hook order is incorrect.
    """
    hooks_called = []

    def hook(name):
        """
        Purpose:
            Record hook invocation order.
        Contract:
            Appends the hook name to hooks_called.
        Args:
            name: Hook name label.
        Returns:
            None.
        """
        hooks_called.append(name)

    cfg = DummyConfig(
        hooks={
            "on_conduit_pre_created": [lambda: hook("pre")],
            "on_conduit_post_created": [lambda _: hook("post")],
            "on_conduit_activated": [lambda _: hook("activated")],
        }
    )
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    spell = DummySpell()
    sb._spells = {DummySpellIndex(): spell}
    # Minimal conduit that satisfies conjure expectations
    class DummyConduitObj:
        """
        Purpose:
            Provide a minimal conduit object for conjure tests.
        Contract:
            Exposes id/name/creations and a cleanup hook.
        """
        def __init__(self):
            """
            Purpose:
                Initialize the conduit object stub.
            Contract:
                Populates id, name, and creations.
            Returns:
                None.
            """
            self._id = "cid"
            self._name = "cname"
            self._creations = {}

        def cleanup(self):
            """
            Purpose:
                Provide a no-op cleanup method.
            Contract:
                Does not raise.
            Returns:
                None.
            """
            pass

    # Patch binder and crafter expectations that conjure touches
    sb._bind = types.SimpleNamespace(build_conduit=lambda *a, **k: DummyConduitObj())
    sb._validate_and_freeze_configuration = lambda: None
    sb._check_all_spells = lambda: None
    sb._logger = DummySafeLogger()
    # Replace Conduit with a lightweight stub to avoid interface checks.
    class StubConduit:
        """
        Purpose:
            Provide a minimal Conduit stub for conjure tests.
        Contract:
            Exposes id/name/creations and a cleanup hook.
        """
        def __init__(
                self,
                spellbook,
                name,
                conduit_state,
                configuration,
                aetheric_frame,
                policy,
                automatic,
                logger,
                conduit_id=None,
        ):
            """
            Purpose:
                Initialize the stub conduit.
            Contract:
                Populates id, name, and creations.
            Args:
                spellbook: Spellbook owner.
                name: Conduit name.
                conduit_state: Conduit state value.
                configuration: Configuration instance.
                aetheric_frame: Aetheric frame name.
                policy: Conduit policy value.
                automatic: Automatic mode flag.
                logger: Logger instance.
                conduit_id: Optional conduit id override for tests.
            Returns:
                None.
            """
            self._id = conduit_id or "cid"
            self._name = "cname"
            self._creations = {}

        def cleanup(self):
            """
            Purpose:
                Provide a no-op cleanup method.
            Contract:
                Does not raise.
            Returns:
                None.
            """
            pass

    import melder.spellbook.spellbook as spellbook_module
    monkeypatch.setattr(spellbook_module, "Conduit", StubConduit)
    # Stub binder to avoid building a real conduit; return the stub directly.
    sb._bind.build_conduit = lambda *a, **k: StubConduit(None, None, None, None, None, None, None)
    sb.conjure()
    assert hooks_called == ["pre", "activated", "post"]


def test_run_resolution_phases_propagates_phase_exception(monkeypatch):
    """
    Purpose:
        Ensure phase execution errors propagate to the caller.
    Contract:
        _run_resolution_phases raises when a phase raises.
    Args:
        monkeypatch: Pytest fixture for patching PhaseScheduler.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    class ExecScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler that executes units of work inline.
        Contract:
            run_all_phases executes unit functions sequentially.
        """
        def run_all_phases(self):
            """
            Purpose:
                Execute each registered unit of work inline.
            Contract:
                Invokes each unit function with its args.
            Returns:
                dict: Empty result mapping.
            """
            # Execute each unit of work to simulate real scheduling.
            for factory in self.phases.values():
                units = factory()
                for unit in units:
                    func = unit["func"]
                    args = unit["args"]
                    func(*args)
            return {}

    class BadSpell(DummySpell):
        """
        Purpose:
            Provide a spell stub that raises during Phase 1.
        Contract:
            run_phase_requirements raises RuntimeError.
        """
        def run_phase_requirements(self, cancel_event):
            """
            Purpose:
                Simulate phase failure.
            Contract:
                Raises RuntimeError unconditionally.
            Args:
                cancel_event: Cancellation event passed by scheduler.
            Raises:
                RuntimeError: Always raised for the stub.
            """
            raise RuntimeError("boom")

    sb = Spellbook()
    sb._spells = {DummySpellIndex(): BadSpell()}
    sb._logger = DummySafeLogger()
    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", ExecScheduler)
    with pytest.raises(RuntimeError):
        sb._run_resolution_phases("cid")


def test_conjure_sets_conduit_and_marks_conjured(monkeypatch):
    """
    Purpose:
        Verify conjure sets conduit and marks the Spellbook as conjured.
    Contract:
        conjure sets _conjured True and attaches a conduit instance.
    Args:
        monkeypatch: Pytest fixture for patching scheduler and conduit classes.
    Returns:
        None.
    Raises:
        AssertionError: If conjure does not set expected state.
    """
    sb = Spellbook(configuration=DummyConfig())
    sb._logger = DummySafeLogger()
    sb._spells = {DummySpellIndex(): DummySpell()}

    class NoopScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler that returns empty phase results.
        Contract:
            run_all_phases returns an empty dict and cleanup marks cleaned.
        """
        def run_all_phases(self):
            """
            Purpose:
                Return an empty phase result mapping.
            Contract:
                Always returns {}.
            Returns:
                dict: Empty results.
            """
            return {}

        def cleanup(self):
            """
            Purpose:
                Mark the scheduler as cleaned.
            Contract:
                Sets cleaned True.
            Returns:
                None.
            """
            self.cleaned = True

    class StubConduit:
        """
        Purpose:
            Provide a minimal conduit stub for conjure tests.
        Contract:
            Exposes id/name/creations and a cleanup hook.
        """
        def __init__(self, *a, **k):
            """
            Purpose:
                Initialize the conduit stub.
            Contract:
                Populates id, name, and creations.
            Args:
                *a: Positional arguments.
                **k: Keyword arguments.
            Returns:
                None.
            """
            self._id = "cid"
            self._name = "cname"
            self._creations = {}

        def cleanup(self):
            """
            Purpose:
                Provide a no-op cleanup method.
            Contract:
                Does not raise.
            Returns:
                None.
            """
            pass

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", NoopScheduler)
    monkeypatch.setattr("melder.spellbook.spellbook.Conduit", StubConduit)
    sb._validate_and_freeze_configuration = lambda: None
    sb._bind_configuration_to_aether = lambda: None
    sb.conjure()
    assert sb._conjured is True
    assert isinstance(sb._conduit, StubConduit)


def test_conjure_twice_raises(monkeypatch):
    """
    Purpose:
        Ensure conjure cannot be invoked twice.
    Contract:
        The second conjure call raises RuntimeError with spellbook context.
    Args:
        monkeypatch: Pytest fixture for patching scheduler and conduit classes.
    Returns:
        None.
    Raises:
        AssertionError: If the second conjure does not raise.
    """
    sb = Spellbook(configuration=DummyConfig())
    sb._logger = DummySafeLogger()
    sb._spells = {DummySpellIndex(): DummySpell()}

    class NoopScheduler(DummyPhaseScheduler):
        """
        Purpose:
            Provide a scheduler that returns empty phase results.
        Contract:
            run_all_phases returns an empty dict.
        """
        def run_all_phases(self):
            """
            Purpose:
                Return an empty phase result mapping.
            Contract:
                Always returns {}.
            Returns:
                dict: Empty results.
            """
            return {}

    class StubConduit:
        """
        Purpose:
            Provide a minimal conduit stub for conjure tests.
        Contract:
            Exposes id/name/creations and a cleanup hook.
        """
        def __init__(self, *a, **k):
            """
            Purpose:
                Initialize the conduit stub.
            Contract:
                Populates id, name, and creations.
            Args:
                *a: Positional arguments.
                **k: Keyword arguments.
            Returns:
                None.
            """
            self._id = "cid"
            self._name = "cname"
            self._creations = {}

        def cleanup(self):
            """
            Purpose:
                Provide a no-op cleanup method.
            Contract:
                Does not raise.
            Returns:
                None.
            """
            pass

    monkeypatch.setattr("melder.spellbook.spellbook.PhaseScheduler", NoopScheduler)
    monkeypatch.setattr("melder.spellbook.spellbook.Conduit", StubConduit)
    sb._validate_and_freeze_configuration = lambda: None
    sb._bind_configuration_to_aether = lambda: None
    sb.conjure()
    with pytest.raises(RuntimeError) as excinfo:
        sb.conjure()
    message = str(excinfo.value)
    assert "spellbook_id=" in message
    assert "conduit_id=" in message


def test_refresh_local_spell_versions_thread_safe():
    """
    Purpose:
        Verify local version refresh is safe under concurrent calls.
    Contract:
        _refresh_local_spell_versions aggregates versions correctly across threads.
    Returns:
        None.
    Raises:
        AssertionError: If version aggregation is incorrect.
    """
    sb = Spellbook()
    idx = DummySpellIndex(versions={"v1", "v2"})
    sb._spells = {idx: DummySpell()}
    sb._spell_versions = set()
    sb._logger = DummySafeLogger()

    def worker():
        """
        Purpose:
            Invoke version refresh in a thread.
        Contract:
            Calls _refresh_local_spell_versions on the Spellbook.
        Returns:
            None.
        """
        sb._refresh_local_spell_versions()

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sb._spell_versions == {"v1", "v2"}
