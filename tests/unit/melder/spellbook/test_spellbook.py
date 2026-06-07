import types
import threading
from types import MappingProxyType
from typing import Any, MutableMapping, Optional, cast

import pytest

import melder.aether.spellbook.spellbook as spellbook_module
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


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
    def __init__(
        self,
        spell_id="sid",
        versions=None,
        existing_object=None,
        *,
        spell_name=None,
        binding_name=None,
        spellframe=None,
        existence=Existence.unique,
        owner_conduit_id=None,
    ):
        """
        Purpose:
            Initialize the spell stub with identity and tracking data.
        Contract:
            Stores inputs verbatim and initializes cleanup tracking.
        Args:
            spell_id: Identifier used for spell_id and spell_name.
            versions: Optional iterable of version ids associated with the spell.
            existing_object: Optional existing instance attached to the spell.
            spell_name: Optional human-readable spell name override.
            binding_name: Optional binding name override.
            spellframe: Optional spellframe override.
            existence: Existence enum for authoring dump tests.
            owner_conduit_id: Optional owner conduit id for authoring dump tests.
        Returns:
            None.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name or spell_id
        self._versions = versions or {spell_id}
        self.user_created_object = existing_object
        self.cleaned = False
        self.cleanup_calls = 0
        self.permissions = Permissions.read
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.existence = existence
        self._compiler_artifact = SpellCompilerArtifact(spell_id)
        self.profile = None
        self.resolution_required = False
        self.resolution_complete = False
        self._owner_conduit_id = owner_conduit_id
        self._owner_conduit_name = None

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

    @property
    def owner_conduit_info(self):
        """
        Purpose:
            Return the current owner conduit tuple for authoring-dump tests.
        Contract:
            Returns `(owner_conduit_id, owner_conduit_name)`.
        Returns:
            tuple[object, object]: Current owner conduit tuple.
        """
        return self._owner_conduit_id, self._owner_conduit_name

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

    def run_phase_occurrence_plan(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 8 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("occurrence_plan", self.spell_id, conduit_id, cancel_event)

    def run_phase_injection_plan(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 9 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("injection_plan", self.spell_id, conduit_id, cancel_event)

    def run_phase_patch_maps(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 10 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("patch_maps", self.spell_id, conduit_id, cancel_event)

    def run_phase_execution_plan(self, conduit_id, cancel_event):
        """
        Purpose:
            Provide a deterministic Phase 11 marker for tests.
        Contract:
            Returns a tuple containing phase name, spell id, conduit id, and cancel event.
        Args:
            conduit_id: Conduit identifier forwarded by the scheduler.
            cancel_event: Cancellation event forwarded by the scheduler.
        Returns:
            tuple[str, str, str, object]: Phase marker tuple.
        """
        return ("execution_plan", self.spell_id, conduit_id, cancel_event)

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

    def _add_owned_conduit(
            self,
            cid,
            cname=None,
            creations=None,
            *,
            dynamic_environment=False,
            creation_gate_controller=None,
            caching_enabled=False,
    ):
        """
        Purpose:
            Capture conduit ownership metadata for assertions.
        Contract:
            Stores ownership metadata on the stub.
        Args:
            cid: Conduit identifier.
            cname: Optional conduit name.
            creations: Optional creation map.
            dynamic_environment: Dynamic-mode flag for the owning conduit.
            creation_gate_controller: Gate controller passed by caller.
        Returns:
            None.
        """
        self._owner = (
            cid,
            cname,
            creations,
            dynamic_environment,
            creation_gate_controller,
            caching_enabled,
        )

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
        self.__dynamic_environment__ = False
        self._creation_gate_controller = CreationGateController()
        self.registered = []
        self._dev_ops_manager = None

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
    def __init__(
            self,
            hooks=None,
            system_state=None,
            frozen=False,
            validate_ok=True,
            full_ahead_of_time_compilation: bool = True,
    ):
        """
        Purpose:
            Initialize the configuration stub.
        Contract:
            Stores hook data and validation flags.
        Args:
            hooks: Optional hook mapping.
            system_state: Optional SystemState override.
            frozen: Initial frozen flag.
            validate_ok: Whether validate() should succeed.
            full_ahead_of_time_compilation: Optional runtime mode flag returned by
                get_property("full_ahead_of_time_compilation").
        Returns:
            None.
        """
        self._hooks = hooks or {}
        self._system_state = system_state or SystemState.automatic
        self._full_ahead_of_time_compilation = full_ahead_of_time_compilation
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

    def get_conduit_hooks(self, sid):
        """
        Purpose:
            Return the configured conduit hook map.
        Contract:
            Returns the stored conduit hook mapping for any spellbook id.
        Args:
            sid: Spellbook id requested by caller.
        Returns:
            dict: Conduit hook mapping configured on the stub.
        """
        return self._hooks

    def get_property(self, name):
        """
        Purpose:
            Provide access to configuration properties.
        Contract:
            Returns system_state, disposal_method_names, or
            full_ahead_of_time_compilation when requested, otherwise None.
        Args:
            name: Property name to fetch.
        Returns:
            object | None: Property value for the requested name.
        """
        if name == "system_state":
            return self._system_state
        if name == "disposal_method_names":
            return []
        if name == "full_ahead_of_time_compilation":
            return self._full_ahead_of_time_compilation
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
        self.infos = []
        self.warnings = []
        self.errors = []
        self.criticals = []
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

    def info(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an info call.
        Contract:
            Appends (msg, method) to the info log.
        Args:
            msg: Info message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.infos.append((msg, method))

    def warning(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a warning call.
        Contract:
            Appends (msg, method) to the warning log.
        Args:
            msg: Warning message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.warnings.append((msg, method))

    def critical(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a critical call.
        Contract:
            Appends (msg, method) to the critical log.
        Args:
            msg: Critical message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.criticals.append((msg, method))

    def exception(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an exception-style error call.
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
        self.info_calls = []
        self.warning_calls = []
        self.error_calls = []
        self.critical_calls = []
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

    def info(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an info call.
        Contract:
            Appends (msg, method) to info_calls.
        Args:
            msg: Info message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.info_calls.append((msg, method))

    def warning(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a warning call.
        Contract:
            Appends (msg, method) to warning_calls.
        Args:
            msg: Warning message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.warning_calls.append((msg, method))

    def critical(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record a critical call.
        Contract:
            Appends (msg, method) to critical_calls.
        Args:
            msg: Critical message.
            method: Optional method name.
            **kwargs: Additional logging context.
        Returns:
            None.
        """
        self.critical_calls.append((msg, method))

    def exception(self, msg, method=None, **kwargs):
        """
        Purpose:
            Record an exception-style error call.
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
        self.cancel_event = types.SimpleNamespace(is_set=False)
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
        Tracks cleanup calls and shared-view lifecycle hooks.
    """
    def __init__(self):
        """
        Purpose:
            Initialize the validation system stub.
        Contract:
            Sets cleaned to False and resets shared-view tracking.
        Returns:
            None.
        """
        self.cleaned = False
        self.shared_view_prepared = False
        self.shared_view_cleared = False

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

    def prepare_shared_view(self, *, spellbook: object, cancel_event: Optional[object] = None) -> None:
        """
        Purpose:
            Record that shared-view preparation was invoked.
        Contract:
            - Marks shared_view_prepared True.
            - Leaves spellbook and cancel_event untouched.
        Args:
            spellbook: Spellbook instance for the validation run.
            cancel_event: Optional cancellation event.
        Returns:
            None.
        """
        self.shared_view_prepared = True

    def clear_shared_view(self) -> None:
        """
        Purpose:
            Record that shared-view cleanup was invoked.
        Contract:
            Marks shared_view_cleared True.
        Returns:
            None.
        """
        self.shared_view_cleared = True


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
    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", DummyPhaseScheduler)
    monkeypatch.setattr("melder.aether.spellbook.spellbook_creation_system.PhaseScheduler", DummyPhaseScheduler)
    yield


def _run_resolution_phases(sb: Spellbook, conduit_id: str):
    """
    Purpose:
        Execute Spellbook resolution phases through the extracted creation system.
    Contract:
        Passes the currently patched Spellbook PhaseScheduler class into
        SpellbookCreationSystem for deterministic unit-test behavior.
    Args:
        sb: Spellbook under test.
        conduit_id: Conduit scope identifier.
    Returns:
        dict: Phase result mapping from SpellbookCreationSystem.
    Raises:
        Exception: Propagates phase pipeline failures.
    """
    return SpellbookCreationSystem.run_resolution_phases(
        sb,
        conduit_id,
        phase_scheduler_cls=spellbook_module.PhaseScheduler,
    )


@pytest.fixture(autouse=True)
def patch_spell_validation_system(monkeypatch):
    """
    Purpose:
        Preserve compatibility with older test setup without patching a dead seam.
    Contract:
        The current Spellbook no longer exposes a module-level
        `SpellValidationSystem` construction seam, so this fixture is a no-op.
    Args:
        monkeypatch: Pytest fixture for patching module attributes.
    Returns:
        None.
    """
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

    def resolve_channel_logger(*args, **kwargs):
        """
        Purpose:
            Resolve channel logger instances for tests.
        Contract:
            Returns a wrapped DummyLogger.
        Returns:
            DummySafeLogger: Safe logger wrapper.
        """
        return DummySafeLogger(DummyLogger())

    monkeypatch.setattr("melder.aether.spellbook.spellbook.InitHelpers.resolve_safe_logger", resolve_safe_logger)
    monkeypatch.setattr("melder.aether.spellbook.spellbook.InitHelpers.resolve_channel_logger", resolve_channel_logger)
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

    monkeypatch.setattr("melder.aether.spellbook.spellbook.Spellbook._initialize_configuration", _stub_init_config)
    yield


@pytest.fixture(autouse=True)
def fresh_utility_system() -> None:
    """
    Reset the utility-system singleton around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()


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


def test_initialize_logging_from_provider(monkeypatch):
    """
    Purpose:
        Ensure Spellbook resolves a logger from the provider path.
    Contract:
        The resolved logger is wrapped in DummySafeLogger.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If logger resolution is incorrect.
    """
    seen = {"called": False}

    def resolve_channel_logger(*args, **kwargs):
        seen["called"] = True
        return DummySafeLogger(DummyLogger())

    monkeypatch.setattr("melder.aether.spellbook.spellbook.InitHelpers.resolve_channel_logger", resolve_channel_logger)
    cfg = DummyConfig()
    sb = Spellbook(configuration=cfg)
    assert isinstance(sb._logger, DummySafeLogger)
    assert isinstance(sb._logger._logger, DummyLogger)
    assert seen["called"] is True


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


def test_get_spell_by_index_id_prefers_local_then_contracted() -> None:
    """
    Purpose:
        Verify stable SpellIndex lookup resolves local first, then contracted.
    Contract:
        - Local lineage matches return the local spell.
        - Contracted lineage matches return the contracted spell when local is absent.
        - Unknown lineage ids return None.
    Returns:
        None.
    Raises:
        AssertionError: If lineage lookup routing is incorrect.
    """
    sb = Spellbook()
    local_index = DummySpellIndex(sid="lineage-local", current="sid-local")
    local_spell = DummySpell(spell_id="sid-local")
    contracted_index = DummySpellIndex(
        sid="lineage-contracted",
        current="sid-contracted",
    )
    contracted_spell = DummySpell(spell_id="sid-contracted")
    sb._spells[local_index] = local_spell
    sb._contracted_spells["peer"] = {contracted_index: contracted_spell}

    assert sb.get_spell_by_index_id("lineage-local") is local_spell
    assert sb.get_spell_by_index_id("lineage-contracted") is contracted_spell
    assert sb.get_spell_by_index_id("missing-lineage") is None


def test_link_contract_manages_only_spellbook_contract_buckets() -> None:
    """
    Purpose:
        Validate link-contract bucket lifecycle on the Spellbook surface.
    Contract:
        - _create_link_contract creates the four contracted-spell bucket maps.
        - _sever_link_contract removes those bucket maps again.
    Returns:
        None.
    Raises:
        AssertionError: If link mirror registration is missing.
    """
    spellbook = Spellbook()
    spellbook._conduit = types.SimpleNamespace(_id="owner-1")

    try:
        spellbook._create_link_contract("peer-1")
        assert "peer-1" in spellbook._contracted_spells
        assert "peer-1" in spellbook._lookup_contracted_spells
        assert "peer-1" in spellbook._contracted_versions
        assert "peer-1" in spellbook._contracted_spells_by_id

        spellbook._sever_link_contract("peer-1")
        assert "peer-1" not in spellbook._contracted_spells
        assert "peer-1" not in spellbook._lookup_contracted_spells
        assert "peer-1" not in spellbook._contracted_versions
        assert "peer-1" not in spellbook._contracted_spells_by_id
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


def test_snapshot_state_returns_detached_copies() -> None:
    sb = Spellbook()
    idx = DummySpellIndex(current="sid-1")
    spell = DummySpell(spell_id="sid-1")
    sb._spells = {idx: spell}
    sb._lookup_spells = {("frame", "binding"): idx}
    sb._spell_versions = {"sid-1"}
    sb._contracted_spells = {"peer": {idx: spell}}
    sb._lookup_contracted_spells = {"peer": {("frame", "binding"): idx}}
    sb._contracted_versions = {"peer": {"sid-1"}}

    snapshot = sb.snapshot_state()

    snapshot["local_spells"].clear()
    snapshot["lookup_spells"].clear()
    snapshot["spell_versions"].clear()
    snapshot["contracted_spells"]["peer"].clear()
    snapshot["lookup_contracted_spells"]["peer"].clear()
    snapshot["contracted_versions"]["peer"].clear()

    assert sb._spells == {idx: spell}
    assert sb._lookup_spells == {("frame", "binding"): idx}
    assert sb._spell_versions == {"sid-1"}
    assert sb._contracted_spells["peer"] == {idx: spell}
    assert sb._lookup_contracted_spells["peer"] == {("frame", "binding"): idx}
    assert sb._contracted_versions["peer"] == {"sid-1"}


def test_mark_collection_dependents_dirty_noop_and_error_paths() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()

    sb._mark_collection_dependents_dirty(set())

    sb._spell_system_states = None
    with pytest.raises(RuntimeError, match="SpellSystemStates unavailable for revalidation."):
        sb._mark_collection_dependents_dirty({"frame"})

    class _StateSystem:
        def mark_collection_dependents_dirty(self, **kwargs):
            raise RuntimeError("boom")

    sb._spell_system_states = _StateSystem()
    with pytest.raises(RuntimeError, match="boom"):
        sb._mark_collection_dependents_dirty({"frame"})


def test_remove_link_contract_inconsistent_state_raises() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._contracted_spells = {"peer": {}}
    sb._lookup_contracted_spells = {}
    sb._contracted_versions = {"peer": set()}
    sb._contracted_spells_by_id = {"peer": {}}

    with pytest.raises(RuntimeError, match="Inconsistent link contract state"):
        sb._remove_link_contract("peer")


def test_try_update_staged_contract_keys_rebuilds_peer_scope(monkeypatch):
    sb = Spellbook()
    sb._aetheric_frame = "default"
    idx = DummySpellIndex()
    sb._lookup_contracted_spells = {"peer": {("new-frame", "new-binding"): idx}}
    updated = []

    session = types.SimpleNamespace(
        staged=types.SimpleNamespace(
            contract_keys=[("staged-frame", "staged-binding", "peer")]
        )
    )
    mediator = types.SimpleNamespace(
        get_session_for_identity=lambda **kwargs: session,
        update_transaction_for_identity=lambda **kwargs: updated.append(
            kwargs["contract_keys"]
        ),
    )
    monkeypatch.setattr(sb, "_get_required_transaction_mediator", lambda: mediator)

    sb._try_update_staged_contract_keys("peer")

    assert updated == [
        [
            ("new-frame", "new-binding", "peer"),
        ]
    ]


def test_begin_transaction_enforces_dynamic_mode_and_admission_failures(monkeypatch):
    class _TxnConfig:
        def __init__(self, system_state):
            self._system_state = system_state

        def has_property(self, name):
            return name == "system_state"

        def get_property(self, name):
            if name != "system_state":
                raise KeyError(name)
            return self._system_state

    sb = Spellbook(configuration=_TxnConfig(SystemState.automatic))
    sb._logger = DummySafeLogger()

    with pytest.raises(RuntimeError, match="does not declare support for 'link'"):
        sb.begin_transaction("link")

    sb._aetheric_frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-id",
        system_state=SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    change_control = types.SimpleNamespace(
        transaction_manager=lambda: types.SimpleNamespace(
            make_scope_key_spellbook=lambda spellbook_id: f"scope:{spellbook_id}",
            build_request=lambda **kwargs: types.SimpleNamespace(
                request_id="req-1",
                **kwargs,
            ),
        ),
        transaction_mediator=lambda: types.SimpleNamespace(
            has_active_session=lambda: False,
            start_transaction=lambda **kwargs: (_ for _ in ()).throw(
                RuntimeError(
                    "[TRANSACTION_MEDIATOR] Change-control admission denied "
                    "(reasons=['embargo']). conflicts=['c1']; embargoes=['e1']"
                )
            ),
        ),
    )
    monkeypatch.setattr(
        spellbook_module.Spellbook,
        "_aether",
        types.SimpleNamespace(
            _get_change_control_manager=lambda frame: change_control,
        ),
    )

    with pytest.raises(RuntimeError, match="admission denied"):
        sb.begin_transaction("bind")


def test_spellbook_builds_transaction_identity_at_init() -> None:
    sb = Spellbook()
    identity = sb._transaction_identity

    try:
        assert identity.owner_kind == "spellbook"
        assert identity.owner_id == sb._id
        assert identity.aetheric_frame_name == sb._aetheric_frame
        assert identity.supports_transaction("bind") is True
        assert identity.supports_transaction("scan") is True
        assert identity.supports_transaction("link") is False
        assert identity.supports_transaction("transfer_ownership") is False
        assert identity.supports_transaction("mutation") is False
        assert identity.supports_transaction("cluster_link") is False
    finally:
        sb.cleanup()


def test_end_transaction_guard_and_abort_paths(monkeypatch):
    sb = Spellbook()
    sb._logger = DummySafeLogger()

    mediator_state = {"session": None}
    mediator = types.SimpleNamespace(
        get_active_session=lambda: mediator_state["session"],
        get_session_for_identity=lambda **kwargs: (
            mediator_state["session"]
            if (
                mediator_state["session"] is not None
                and kwargs.get("transaction_type") == "bind"
                and mediator_state["session"].request.request_type == "bind"
            )
            else None
        ),
        get_session_by_request_id=lambda request_id: (
            mediator_state["session"]
            if mediator_state["session"] is not None
            and mediator_state["session"].request.request_id == request_id
            else None
        ),
        mark_active_session_abort_only=lambda reason, error=None: None,
        end_transaction_for_identity=lambda identity, transaction_type, success=True: mediator_state.update(session=None),
        end_transaction_by_request_id=lambda request_id, expected_type=None, success=True: mediator_state.update(session=None),
        get_active_request=lambda: (
            mediator_state["session"].request
            if mediator_state["session"] is not None
            else None
        ),
    )
    monkeypatch.setattr(
        sb,
        "_get_required_transaction_mediator",
        lambda: mediator,
    )

    with pytest.raises(RuntimeError, match="No active change transaction to end."):
        sb.end_transaction()

    mediator_state["session"] = types.SimpleNamespace(
        request=types.SimpleNamespace(
            request_id="req-1",
            request_type="link",
        ),
        depth=1,
    )
    with pytest.raises(RuntimeError, match="does not match the requested type"):
        sb.end_transaction("bind")

    abort_calls = []
    bind_request = types.SimpleNamespace(
        request_id="req-bind",
        request_type="bind",
    )
    mediator.end_transaction_for_identity = lambda identity, transaction_type, success=True: (
        abort_calls.append(bind_request.request_id),
        (_ for _ in ()).throw(RuntimeError("end bind boom")),
    )
    mediator_state["session"] = types.SimpleNamespace(
        request=bind_request,
        depth=1,
    )
    with pytest.raises(RuntimeError, match="end bind boom"):
        sb.end_transaction("bind")

    assert abort_calls == ["req-bind"]


def test_end_transaction_commit_path_and_context_manager() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    commit_calls = []
    session = types.SimpleNamespace(
        request=types.SimpleNamespace(
            request_id="req-link",
            request_type="link",
        ),
        depth=1,
    )
    mediator_state = {"session": session}
    sb._get_required_transaction_mediator = lambda: types.SimpleNamespace(
        get_active_session=lambda: mediator_state["session"],
        get_session_for_identity=lambda **kwargs: None,
        get_active_request=lambda: (
            mediator_state["session"].request
            if mediator_state["session"] is not None
            else None
        ),
        get_session_by_request_id=lambda request_id: (
            mediator_state["session"]
            if mediator_state["session"] is not None
            and mediator_state["session"].request.request_id == request_id
            else None
        ),
        end_transaction_by_request_id=lambda request_id, expected_type=None, success=True: (
            commit_calls.append((request_id, expected_type, success)),
            mediator_state.update(session=None),
        ),
    )
    sb.end_transaction("link")

    assert commit_calls == [
        (
            "req-link",
            "link",
            True,
        )
    ]

    calls = []
    sb.begin_transaction = lambda *args, **kwargs: calls.append(("begin", args[0]))
    sb.end_transaction = lambda transaction_type=None, success=True: calls.append(("end", transaction_type, success))

    with pytest.raises(RuntimeError, match="boom"):
        with sb.transaction("link"):
            raise RuntimeError("boom")

    assert calls == [
        ("begin", "link"),
        ("end", "link", False),
    ]


def test_bind_state_helpers_and_staged_binding_key_updates(monkeypatch):
    sb = Spellbook()
    sb._logger = DummySafeLogger()

    sb._prepare_bind_transaction_state()
    sb._pending_binding_frame_keys = {"frame-a"}
    sb._pending_structural_spells = ["spell-a"]
    sb._clear_bind_transaction_state()

    assert sb._pending_binding_frame_keys == set()
    assert sb._pending_structural_spells == []

    mediator = types.SimpleNamespace(
        get_session_for_identity=lambda **kwargs: None,
        update_transaction_for_identity=lambda **kwargs: None,
    )
    monkeypatch.setattr(sb, "_get_required_transaction_mediator", lambda: mediator)
    sb._conjured = True
    with pytest.raises(RuntimeError, match="requires an active binding transaction"):
        sb._ensure_binding_transaction_active(action="bind")

    updated = []
    session = types.SimpleNamespace(staged=types.SimpleNamespace(contract_keys=[]))
    mediator = types.SimpleNamespace(
        get_session_for_identity=lambda **kwargs: session,
        update_transaction_for_identity=lambda **kwargs: updated.append(
            kwargs["binding_keys"]
        ),
    )
    monkeypatch.setattr(sb, "_get_required_transaction_mediator", lambda: mediator)
    spell_a = types.SimpleNamespace(key=("frame-a", "binding-a"))
    spell_dup = types.SimpleNamespace(key=("frame-a", "binding-a"))
    spell_b = types.SimpleNamespace(key=("frame-b", "binding-b"))
    sb._pending_structural_spells = [spell_a, spell_dup, spell_b]

    sb._try_update_staged_binding_keys()

    assert updated == [
        [("frame-a", "binding-a"), ("frame-b", "binding-b")]
    ]


def test_bind_configuration_to_aether_and_frame_posture_reraise_failures(monkeypatch):
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = DummyConfig()
    sb._aetheric_frame = "ops"

    aether_stub = types.SimpleNamespace(
        _get_configuration=lambda frame: None,
        _bind_configuration=lambda configuration, frame: (_ for _ in ()).throw(
            RuntimeError("bind configuration boom")
        ),
        _ensure_frame=lambda frame: types.SimpleNamespace(
            bind_frame_configuration=lambda configuration: (_ for _ in ()).throw(
                RuntimeError("bind posture boom")
            )
        ),
    )
    monkeypatch.setattr(spellbook_module.Spellbook, "_aether", aether_stub)

    sb._aetheric_frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-id",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
        shared_framewide_spellbook_configuration=True,
    )
    with pytest.raises(RuntimeError, match="bind configuration boom"):
        sb._bind_configuration_to_aether()

    sb._aetheric_frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-id",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    with pytest.raises(RuntimeError, match="bind posture boom"):
        sb._bind_aetheric_frame_configuration_to_aether()


def test_bind_aetheric_frame_configuration_missing_config_raises() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._aetheric_frame_configuration = None

    with pytest.raises(RuntimeError, match="No frame configuration instance available to bind to Aether."):
        sb._bind_aetheric_frame_configuration_to_aether()


def test_spellbook_initializes_frame_owned_configuration_defaults() -> None:
    sb = Spellbook()
    frame_configuration = sb._aetheric_frame_configuration

    assert frame_configuration is not None
    assert frame_configuration.origin_spellbook_id is None
    assert frame_configuration.system_state is SystemState.automatic
    assert frame_configuration.ai_native_enabled is False
    assert frame_configuration.rift_enabled is False


def test_risk_manager_bridge_helpers_cover_success_none_and_error_paths(monkeypatch) -> None:
    """
    Purpose:
        Validate Spellbook risk-manager bridge helpers across success, no-op,
        and swallowed-error paths.
    Contract:
        - _get_risk_manager returns the live per-frame manager when DevOps exists.
        - _set_spellbook_validation_required coerces truthy/falsy inputs to bool.
        - register/unregister bridge helpers ignore missing inputs.
        - register/unregister bridge helpers swallow manager exceptions.
    Returns:
        None.
    Raises:
        AssertionError: If helper routing or no-op behavior is incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()

    calls = []

    class _RiskManager:
        def register_conduit(self, conduit_id, spellbook):
            calls.append(("register_conduit", conduit_id, spellbook))

        def unregister_conduit(self, conduit_id):
            calls.append(("unregister_conduit", conduit_id))

        def register_spell(self, conduit_id, spell):
            calls.append(("register_spell", conduit_id, spell))

        def unregister_spell(self, conduit_id, spell):
            calls.append(("unregister_spell", conduit_id, spell))

    risk_manager = _RiskManager()
    monkeypatch.setattr(
        spellbook_module.Spellbook,
        "_aether",
        types.SimpleNamespace(
            _get_devops_manager=lambda frame: types.SimpleNamespace(risk_manager=risk_manager),
        ),
    )

    assert sb._get_risk_manager() is risk_manager

    sb._set_spellbook_validation_required("yes")
    assert sb._spellbook_validation_required is True
    sb._set_spellbook_validation_required(0)
    assert sb._spellbook_validation_required is False

    spell = DummySpell(spell_id="sid-risk")
    conduit = types.SimpleNamespace(_id="conduit-risk")

    sb._register_conduit_with_risk_manager(None)
    sb._unregister_conduit_from_risk_manager("")
    sb._register_spell_with_risk_manager("", spell)
    sb._unregister_spell_with_risk_manager("conduit-risk", None)
    assert calls == []

    sb._register_conduit_with_risk_manager(conduit)
    sb._unregister_conduit_from_risk_manager("conduit-risk")
    sb._register_spell_with_risk_manager("conduit-risk", spell)
    sb._unregister_spell_with_risk_manager("conduit-risk", spell)

    assert calls == [
        ("register_conduit", "conduit-risk", sb),
        ("unregister_conduit", "conduit-risk"),
        ("register_spell", "conduit-risk", spell),
        ("unregister_spell", "conduit-risk", spell),
    ]

    monkeypatch.setattr(
        sb,
        "_get_risk_manager",
        lambda: types.SimpleNamespace(
            register_conduit=lambda conduit_id, spellbook: (_ for _ in ()).throw(RuntimeError("register boom")),
            unregister_conduit=lambda conduit_id: (_ for _ in ()).throw(RuntimeError("unregister boom")),
            register_spell=lambda conduit_id, live_spell: (_ for _ in ()).throw(RuntimeError("spell register boom")),
            unregister_spell=lambda conduit_id, live_spell: (_ for _ in ()).throw(RuntimeError("spell unregister boom")),
        ),
    )

    sb._register_conduit_with_risk_manager(conduit)
    sb._unregister_conduit_from_risk_manager("conduit-risk")
    sb._register_spell_with_risk_manager("conduit-risk", spell)
    sb._unregister_spell_with_risk_manager("conduit-risk", spell)

    monkeypatch.setattr(
        spellbook_module.Spellbook,
        "_aether",
        types.SimpleNamespace(
            _get_devops_manager=lambda frame: (_ for _ in ()).throw(RuntimeError("no devops")),
        ),
    )
    monkeypatch.setattr(
        sb,
        "_get_risk_manager",
        spellbook_module.Spellbook._get_risk_manager.__get__(sb, Spellbook),
    )
    assert sb._get_risk_manager() is None


def test_add_contracted_spell_updates_maps_and_notifies_when_conjured() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._contracted_spells = {}
    sb._lookup_contracted_spells = {}
    sb._contracted_versions = {}
    sb._contracted_spells_by_id = {}
    sb._conjured = True
    sb._conduit = DummyConduit("borrower", "borrower")
    dirty_calls = []
    staged_calls = []
    risk_calls = []
    sb._mark_collection_dependents_dirty = lambda frame_keys: dirty_calls.append(frame_keys)
    sb._try_update_staged_contract_keys = lambda conduit_id: staged_calls.append(conduit_id)
    sb._register_spell_with_risk_manager = (
        lambda conduit_id, spell: risk_calls.append((conduit_id, spell))
    )

    idx = DummySpellIndex(versions={"sid-1", "sid-2"}, sid="lineage", current="sid-1")
    idx._attach_contracted = lambda owner, conduit_id, spell: setattr(
        idx,
        "_contract_attachment",
        (owner, conduit_id, spell),
    )
    spell = DummySpell(
        spell_id="sid-1",
        versions={"sid-1", "sid-2"},
        spell_name="SpellName",
        binding_name="binding",
        spellframe="Frame",
    )
    spell.spell_index = idx
    spell.key = ("frame", "binding")

    sb._add_contracted_spell(spell, "peer")

    assert sb._contracted_spells["peer"][idx] is spell
    assert sb._lookup_contracted_spells["peer"] == {("frame", "binding"): idx}
    assert sb._contracted_versions["peer"] == {"sid-1", "sid-2"}
    assert dirty_calls == [{"frame"}]
    assert staged_calls == ["peer"]
    assert risk_calls == [("borrower", spell)]


def test_remove_contracted_spell_updates_maps_and_notifies_when_conjured() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._contracted_spells = {"peer": {}}
    sb._lookup_contracted_spells = {"peer": {}}
    sb._contracted_versions = {"peer": set()}
    sb._contracted_spells_by_id = {}
    sb._conjured = True
    sb._conduit = DummyConduit("borrower", "borrower")
    staged_calls = []
    risk_calls = []
    sb._try_update_staged_contract_keys = lambda conduit_id: staged_calls.append(conduit_id)
    sb._unregister_spell_with_risk_manager = (
        lambda conduit_id, spell: risk_calls.append((conduit_id, spell))
    )

    idx = DummySpellIndex(versions={"sid-1", "sid-2"}, sid="lineage", current="sid-1")
    idx._detach_contracted = lambda owner, conduit_id: setattr(
        idx,
        "_contract_detached",
        (owner, conduit_id),
    )
    spell = DummySpell(
        spell_id="sid-1",
        versions={"sid-1", "sid-2"},
        spell_name="SpellName",
        binding_name="binding",
        spellframe="Frame",
    )
    spell.spell_index = idx
    sb._contracted_spells["peer"][idx] = spell
    sb._lookup_contracted_spells["peer"][("frame", "binding")] = idx
    sb._contracted_versions["peer"].update({"sid-1", "sid-2"})

    sb._remove_contracted_spell("sid-1", "peer")

    assert sb._contracted_spells["peer"] == {}
    assert sb._lookup_contracted_spells["peer"] == {}
    assert sb._contracted_versions["peer"] == set()
    assert staged_calls == ["peer"]
    assert risk_calls == [("borrower", spell)]


def test_remove_contracted_spell_missing_maps_and_missing_version_raise() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._contracted_spells = {}
    sb._lookup_contracted_spells = {}
    sb._contracted_versions = {}

    with pytest.raises(RuntimeError, match="No contracted spell maps found for conduit ID peer."):
        sb._remove_contracted_spell("sid-1", "peer")

    idx = DummySpellIndex(versions={"other"}, sid="lineage", current="other")
    spell = DummySpell(
        spell_id="other",
        versions={"other"},
        spell_name="SpellName",
        binding_name="binding",
        spellframe="Frame",
    )
    spell.spell_index = idx
    sb._contracted_spells = {"peer": {idx: spell}}
    sb._lookup_contracted_spells = {"peer": {("frame", "binding"): idx}}
    sb._contracted_versions = {"peer": {"other"}}

    with pytest.raises(RuntimeError, match="Spell version sid-1 not found for conduit ID peer."):
        sb._remove_contracted_spell("sid-1", "peer")


def test_cleanup_components_swallows_clear_and_cleanup_failures() -> None:
    class _BadMap(dict):
        def clear(self):
            raise RuntimeError("clear boom")

    class _BadConfig(DummyConfig):
        def cleanup(self):
            raise RuntimeError("config cleanup boom")

    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_spells = lambda: None
    sb._remove_spells_from_nexus = lambda: None
    sb._spells = _BadMap()
    sb._spells_by_id = _BadMap()
    sb._spell_id_pool = _BadMap()
    sb._lookup_spells = _BadMap()
    sb._contracted_spells = _BadMap()
    sb._contracted_spells_by_id = _BadMap()
    sb._lookup_contracted_spells = _BadMap()
    sb._configuration = _BadConfig()
    sb._spell_versions = _BadMap()
    sb._contracted_versions = _BadMap()
    sb._cleanup_components()

    assert not hasattr(sb, "_spells")
    assert not hasattr(sb, "_spells_by_id")
    assert not hasattr(sb, "_spell_id_pool")
    assert not hasattr(sb, "_lookup_spells")
    assert not hasattr(sb, "_contracted_spells")
    assert not hasattr(sb, "_contracted_spells_by_id")
    assert not hasattr(sb, "_lookup_contracted_spells")
    assert not hasattr(sb, "_configuration")
    assert not hasattr(sb, "_spell_versions")
    assert not hasattr(sb, "_contracted_versions")
    assert len(sb._logger.error_calls) >= 1


def test_cleanup_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner):
            self._owner = owner

        def __enter__(self):
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    sb = Spellbook()
    original_lock = sb._lock
    sb._lock = _FlipCleanedOnEnter(sb)
    try:
        sb.cleanup()
    finally:
        sb._lock = original_lock

    assert sb._cleaned is True


def test_refresh_nexus_publish_enabled_and_publish_helpers_cover_enabled_and_disabled_paths() -> None:
    publish_calls = []
    remove_calls = []

    sb = Spellbook()
    sb._id = "spellbook-id"
    sb._aetheric_frame = "ops"
    sb._nexus = types.SimpleNamespace(
        _publish_frame_record=lambda spellbook: publish_calls.append(("frame", spellbook._id)),
        _publish_conduit_record=lambda conduit: publish_calls.append(("conduit", conduit._id)),
        _publish_spell_record=lambda spellbook, spell, owner_conduit_id: publish_calls.append(
            ("spell", spell.spell_id, owner_conduit_id)
        ),
        _remove_spell_record=lambda spellbook_id, spell_id, frame: remove_calls.append(
            (spellbook_id, spell_id, frame)
        ),
    )
    spell = DummySpell(spell_id="sid-1", owner_conduit_id="owner-a")
    sb._spells = {DummySpellIndex(current="sid-1"): spell}
    conduit = DummyConduit("cid", "root")
    sb._conduit = conduit
    sb._conjured = True

    sb._aetheric_frame_configuration = None

    assert sb._refresh_nexus_publish_enabled() is False
    sb._publish_nexus_state_for_conjure(conduit)
    sb._publish_spell_record_to_nexus(spell)
    sb._replace_spell_record_in_nexus("old-id", spell)
    sb._remove_spells_from_nexus()

    assert conduit._nexus_publish_enabled is False
    assert publish_calls == []
    assert remove_calls == []

    sb._aetheric_frame_configuration = types.SimpleNamespace(rift_enabled=True)

    assert sb._refresh_nexus_publish_enabled() is True
    sb._publish_nexus_state_for_conjure(conduit)
    sb._publish_spell_record_to_nexus(spell)
    sb._replace_spell_record_in_nexus("old-id", spell)
    sb._remove_spells_from_nexus()

    assert conduit._nexus_publish_enabled is True
    assert publish_calls == [
        ("frame", "spellbook-id"),
        ("conduit", "cid"),
        ("spell", "sid-1", "cid"),
        ("spell", "sid-1", "owner-a"),
        ("spell", "sid-1", "owner-a"),
    ]
    assert remove_calls == [
        ("spellbook-id", "old-id", "ops"),
        ("spellbook-id", "sid-1", "ops"),
    ]


def test_register_contracted_spell_id_missing_map_and_collisions_raise() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    spell = DummySpell(spell_id="contracted-id")

    sb._contracted_spells_by_id = None
    with pytest.raises(RuntimeError, match="Contracted spell_id map is not available."):
        sb._register_contracted_spell_id("peer", "contracted-id", spell)

    sb._contracted_spells_by_id = {}
    with pytest.raises(RuntimeError, match="Contracted spell_id map missing for conduit_id=peer"):
        sb._register_contracted_spell_id("peer", "contracted-id", spell)

    other = DummySpell(spell_id="contracted-id")
    sb._contracted_spells_by_id = {"peer": {"contracted-id": other}}
    with pytest.raises(RuntimeError, match="Contracted spell_id collision for conduit_id=peer, spell_id=contracted-id"):
        sb._register_contracted_spell_id("peer", "contracted-id", spell)

    sb._contracted_spells_by_id = {"peer": {}}
    sb._spell_id_pool["contracted-id"] = other
    with pytest.raises(RuntimeError, match="Contracted spell_id collision for spell_id_pool spell_id=contracted-id"):
        sb._register_contracted_spell_id("peer", "contracted-id", spell)


def test_update_contracted_spell_id_error_paths_raise() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    spell = DummySpell(spell_id="old-id")

    sb._contracted_spells_by_id = None
    with pytest.raises(RuntimeError, match="Contracted spell_id map is not available."):
        sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)

    sb._contracted_spells_by_id = {}
    with pytest.raises(RuntimeError, match="Contracted spell_id map missing for conduit_id=peer"):
        sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)

    sb._contracted_spells_by_id = {"peer": {}}
    with pytest.raises(RuntimeError, match="Contracted spell_id not found for update \\(old_id=old-id\\)."):
        sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)

    other = DummySpell(spell_id="old-id")
    sb._contracted_spells_by_id = {"peer": {"old-id": other}}
    with pytest.raises(RuntimeError, match="Contracted spell_id mapped to a different spell \\(old_id=old-id\\)."):
        sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)

    sb._contracted_spells_by_id = {"peer": {"old-id": spell, "new-id": other}}
    with pytest.raises(RuntimeError, match="Contracted spell_id collision for new_id=new-id"):
        sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)


def test_unregister_contracted_spell_id_error_paths_raise() -> None:
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    spell = DummySpell(spell_id="contracted-id")

    sb._contracted_spells_by_id = None
    with pytest.raises(RuntimeError, match="Contracted spell_id map is not available."):
        sb._unregister_contracted_spell_id("peer", "contracted-id", spell)

    sb._contracted_spells_by_id = {}
    with pytest.raises(RuntimeError, match="Contracted spell_id map missing for conduit_id=peer"):
        sb._unregister_contracted_spell_id("peer", "contracted-id", spell)

    sb._contracted_spells_by_id = {"peer": {}}
    with pytest.raises(RuntimeError, match="Contracted spell_id not found for removal \\(spell_id=contracted-id\\)."):
        sb._unregister_contracted_spell_id("peer", "contracted-id", spell)

    other = DummySpell(spell_id="contracted-id")
    sb._contracted_spells_by_id = {"peer": {"contracted-id": other}}
    with pytest.raises(RuntimeError, match="Contracted spell_id mapped to a different spell \\(spell_id=contracted-id\\)."):
        sb._unregister_contracted_spell_id("peer", "contracted-id", spell)


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
        SpellbookCreationSystem.check_system_state raises for default policy in automatic state when not allowed.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError):
        SpellbookCreationSystem.check_system_state(sb, Policies.default, dynamic=True)


def test_check_system_state_dynamic_in_automatic_raises():
    """
    Purpose:
        Verify dynamic policy is rejected in automatic mode when not allowed.
    Contract:
        SpellbookCreationSystem.check_system_state raises when automatic is False and policy is dynamic,
        and the error message includes policy and system_state context.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError) as excinfo:
        SpellbookCreationSystem.check_system_state(sb, Policies.whitelist_all, dynamic=True)
    message = str(excinfo.value)
    assert "policy=Policies.whitelist_all" in message
    assert "dynamic=True" in message
    assert "system_state=SystemState.automatic" in message


def test_check_system_state_dynamic_policy_rejected_when_dynamic_disabled():
    """
    Purpose:
        Confirm automatic flag does not override rejection for dynamic policy.
    Contract:
        SpellbookCreationSystem.check_system_state raises even when automatic is True for dynamic policies,
        and the error message includes policy and allowed-policy context.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    sb = Spellbook(configuration=DummyConfig(system_state=SystemState.automatic))
    sb._logger = DummySafeLogger()
    with pytest.raises(RuntimeError) as excinfo:
        SpellbookCreationSystem.check_system_state(sb, Policies.whitelist_all, dynamic=False)
    message = str(excinfo.value)
    assert "policy=Policies.whitelist_all" in message
    assert "allowed=default" in message


def test_define_conduit_stamps_owner_and_primes_existing():
    """
    Purpose:
        Verify conduit ownership and existing creations are registered.
    Contract:
        SpellbookCreationSystem.define_conduit_into_spells sets owner info and registers existing objects.
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
    SpellbookCreationSystem.define_conduit_into_spells(sb, conduit)
    assert spell_existing._owner[0] == conduit._id
    assert conduit.registered[0][1] == "obj"
    assert spell_existing.resolution_required is False
    assert spell_existing.resolution_complete is False
    assert spell_normal.resolution_required is False
    assert spell_normal.resolution_complete is False


def test_define_conduit_sets_resolution_required_when_jit_enabled():
    """
    Purpose:
        Verify conjure ownership wiring marks spells as runtime-resolution-required
        when full AOT compilation is disabled.
    Contract:
        SpellbookCreationSystem.define_conduit_into_spells sets
        `resolution_required=True` for local spells when
        full_ahead_of_time_compilation=False.
    Returns:
        None.
    Raises:
        AssertionError: If propagation is not applied.
    """
    frame_name = "jit_propagation_test_frame"
    cfg = DummyConfig(full_ahead_of_time_compilation=False)
    cfg._aether_frame = frame_name
    sb = Spellbook(aetheric_frame=frame_name, configuration=cfg)
    conduit = DummyConduit()
    spell = DummySpell()
    idx = DummySpellIndex()
    spell.spell_index = idx
    sb._spells = {idx: spell}
    sb._logger = DummySafeLogger()

    SpellbookCreationSystem.define_conduit_into_spells(sb, conduit)

    assert spell.resolution_required is True
    assert spell.resolution_complete is False


def test_bind_after_conjure_sets_resolution_required_when_jit_enabled(monkeypatch):
    """
    Purpose:
        Verify late binds inherit JIT runtime-resolution requirements.
    Contract:
        When a conduit already exists and full AOT is disabled, `bind()` stamps
        `resolution_required=True` while preserving ownership, creations
        registration, lineage registration, and risk-manager registration.
    Args:
        monkeypatch: Pytest fixture for patching Aether helpers.
    Returns:
        None.
    Raises:
        AssertionError: If propagation or existing side effects are missing.
    """
    frame_name = "bind_post_conjure_jit_frame"
    cfg = DummyConfig(full_ahead_of_time_compilation=False)
    cfg._aether_frame = frame_name
    sb = Spellbook(aetheric_frame=frame_name, configuration=cfg)
    sb._logger = DummySafeLogger()
    sb._conjured = True
    sb._conduit = DummyConduit(cid="jit-cid", name="jit-conduit")
    sb._bind_family_disabled_for_current_posture = lambda: False
    sb._binding_transaction_is_active = lambda: True
    sb._ensure_binding_transaction_active = lambda action: None
    sb._assert_lookup_key_available = lambda **kwargs: None
    sb._add_hooks_to_spell = lambda spell, **kwargs: None

    lineage_calls = []
    risk_calls = []
    register_single_calls = []
    sb._spell_system_states = types.SimpleNamespace(
        register_index=lambda spell_index: lineage_calls.append((spell_index, new_spell))
    )
    sb._register_spell_with_risk_manager = (
        lambda conduit_id, spell: risk_calls.append((conduit_id, spell))
    )

    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, *a, **k: False)
    monkeypatch.setattr(
        type(Spellbook._aether),
        "_register_single_spell_index",
        lambda self, conduit_id, spell_index, frame: register_single_calls.append(
            (conduit_id, spell_index, frame)
        ),
    )

    idx = DummySpellIndex(sid="jit-sid", current="jit-sid")
    idx._attach_owner = lambda owner, spell: setattr(idx, "_attached_owner", owner)
    new_spell = DummySpell(spell_id="jit-sid", existing_object="existing")
    new_spell.spell_index = idx
    new_spell._key = ("jit-frame", "jit-binding")
    new_spell.key = new_spell._key
    sb._bind = types.SimpleNamespace(bind=lambda **kwargs: new_spell)

    result = sb.bind(spell=object(), existence=Existence.unique, permissions="create")

    assert result == "jit-sid"
    assert new_spell.resolution_required is True
    assert new_spell.resolution_complete is False
    assert new_spell._owner[0] == "jit-cid"
    assert sb._conduit.registered == [(new_spell, "existing")]
    assert len(lineage_calls) == 1
    assert lineage_calls[0][1] is new_spell
    assert risk_calls == [("jit-cid", new_spell)]
    assert register_single_calls == [("jit-cid", idx, frame_name)]


def test_bind_after_conjure_keeps_resolution_required_false_when_aot_enabled(monkeypatch):
    """
    Purpose:
        Verify late binds preserve default AOT runtime-resolution semantics.
    Contract:
        When full AOT remains enabled, `bind()` stamps
        `resolution_required=False` for newly bound spells after conjure.
    Args:
        monkeypatch: Pytest fixture for patching Aether helpers.
    Returns:
        None.
    Raises:
        AssertionError: If default AOT propagation is not preserved.
    """
    frame_name = "bind_post_conjure_aot_frame"
    cfg = DummyConfig(full_ahead_of_time_compilation=True)
    cfg._aether_frame = frame_name
    sb = Spellbook(aetheric_frame=frame_name, configuration=cfg)
    sb._logger = DummySafeLogger()
    sb._conjured = True
    sb._conduit = DummyConduit(cid="aot-cid", name="aot-conduit")
    sb._bind_family_disabled_for_current_posture = lambda: False
    sb._binding_transaction_is_active = lambda: True
    sb._ensure_binding_transaction_active = lambda action: None
    sb._assert_lookup_key_available = lambda **kwargs: None
    sb._add_hooks_to_spell = lambda spell, **kwargs: None
    sb._spell_system_states = types.SimpleNamespace(
        register_index=lambda spell_index: None
    )
    sb._register_spell_with_risk_manager = lambda conduit_id, spell: None

    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, *a, **k: False)
    monkeypatch.setattr(
        type(Spellbook._aether),
        "_register_single_spell_index",
        lambda self, conduit_id, spell_index, frame: None,
    )

    idx = DummySpellIndex(sid="aot-sid", current="aot-sid")
    idx._attach_owner = lambda owner, spell: None
    new_spell = DummySpell(spell_id="aot-sid")
    new_spell.spell_index = idx
    new_spell._key = ("aot-frame", "aot-binding")
    new_spell.key = new_spell._key
    new_spell.resolution_required = True
    sb._bind = types.SimpleNamespace(bind=lambda **kwargs: new_spell)

    result = sb.bind(spell=object(), existence=Existence.unique, permissions="create")

    assert result == "aot-sid"
    assert new_spell.resolution_required is False
    assert new_spell.resolution_complete is False


def test_define_conduit_handles_errors():
    """
    Purpose:
        Ensure errors defining conduit ownership are swallowed.
    Contract:
        SpellbookCreationSystem.define_conduit_into_spells continues despite spell errors.
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
    SpellbookCreationSystem.define_conduit_into_spells(sb, DummyConduit())
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
    spell.is_existing_creation = False
    spell._compiler_artifact._root_blueprint_phase5 = object()
    sb._spells = {DummySpellIndex(): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    compiler_system = SpellCompilerSystem()
    req_units = SpellbookCreationSystem.phase_requirements_factory(sb, scheduler, compiler_system)
    sym_units = SpellbookCreationSystem.phase_symbolic_graph_factory(sb, scheduler, compiler_system)
    loc_units = SpellbookCreationSystem.phase_local_frame_factory(sb, scheduler, compiler_system)
    val_units = SpellbookCreationSystem.phase_validation_factory(sb, scheduler, compiler_system)
    root_units = SpellbookCreationSystem.phase_root_blueprints_factory(sb, scheduler, compiler_system, "cid")
    occ_units = SpellbookCreationSystem.phase_occurrence_plan_factory(sb, scheduler, compiler_system, "cid")
    inj_units = SpellbookCreationSystem.phase_injection_plan_factory(sb, scheduler, compiler_system, "cid")
    patch_units = SpellbookCreationSystem.phase_patch_maps_factory(sb, scheduler, compiler_system, "cid")
    sys_units = SpellbookCreationSystem.phase_system_validation_factory(sb, scheduler, compiler_system, "cid")
    change_units = SpellbookCreationSystem.phase_change_control_factory(sb, scheduler, compiler_system, "cid")
    assert req_units[0]["label"] == "requirements:x"
    assert sym_units[0]["label"] == "symbolic_graph:x"
    assert loc_units[0]["label"] == "local_frame:x"
    assert val_units[0]["label"] == "validation:x"
    assert root_units[0]["label"] == "root_blueprints:x"
    assert occ_units[0]["label"] == "occurrence_plan:x"
    assert inj_units[0]["label"] == "injection_plan:x"
    assert patch_units[0]["label"] == "patch_maps:x"
    assert sys_units[0]["label"] == "system_validation:x"
    assert change_units[0]["label"] == "change_control:x"


def test_phase_factories_guard_cleaned():
    """
    Purpose:
        Ensure phase factories reject cleaned Spellbook instances.
    Contract:
        SpellbookCreationSystem.phase_requirements_factory raises RuntimeError when cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned guard does not raise.
    """
    sb = Spellbook()
    sb._cleaned = True
    scheduler = DummyPhaseScheduler(sb, None)
    compiler_system = SpellCompilerSystem()
    with pytest.raises(RuntimeError):
        SpellbookCreationSystem.phase_requirements_factory(sb, scheduler, compiler_system)


def test_run_resolution_phases_success(monkeypatch):
    """
    Purpose:
        Verify resolution phases run and return expected keys.
    Contract:
        SpellbookCreationSystem.run_resolution_phases returns all phase results.
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
    results = _run_resolution_phases(sb, "cid")
    assert set(results.keys()) == {
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "occurrence_plan",
        "injection_plan",
        "execution_plan",
        "patch_maps",
        "system_validation",
        "change_control",
    }


def test_run_resolution_phases_broken_spell_raises(monkeypatch):
    """
    Purpose:
        Ensure broken spells cause validation errors.
    Contract:
        SpellbookCreationSystem.run_resolution_phases raises SpellbookValidationError for broken spells.
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
        _run_resolution_phases(sb, "cid")


def test_run_resolution_phases_spell_status_error_treated_as_broken():
    """
    Purpose:
        Verify errors while checking spell status are treated as broken.
    Contract:
        SpellbookCreationSystem.run_resolution_phases raises SpellbookValidationError on status errors.
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
        _run_resolution_phases(sb, "cid")


def test_run_resolution_phases_cleans_scheduler_on_exception(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup occurs when phase execution fails.
    Contract:
        SpellbookCreationSystem.run_resolution_phases raises and cleanup is still invoked.
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

    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", BoomScheduler)
    with pytest.raises(RuntimeError):
        _run_resolution_phases(sb, "cid")


def test_get_conjure_hook_map_no_config_returns_none():
    """
    Purpose:
        Ensure hook map returns None when configuration is missing.
    Contract:
        SpellbookCreationSystem.get_conjure_hook_map returns None without a configuration.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._configuration = None
    assert SpellbookCreationSystem.get_conjure_hook_map(sb) is None


def test_get_conjure_hook_map_config_without_get_hooks_returns_none():
    """
    Purpose:
        Verify hook lookup returns None for configurations without hooks.
    Contract:
        SpellbookCreationSystem.get_conjure_hook_map returns None when get_hooks is missing or empty.
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
    assert SpellbookCreationSystem.get_conjure_hook_map(sb) is None


def test_get_conjure_hook_map_empty_returns_none():
    """
    Purpose:
        Ensure empty hook maps are treated as absent.
    Contract:
        SpellbookCreationSystem.get_conjure_hook_map returns None when hook map is empty.
    Returns:
        None.
    Raises:
        AssertionError: If a hook map is returned.
    """
    cfg = DummyConfig(hooks={})
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    assert SpellbookCreationSystem.get_conjure_hook_map(sb) is None


def test_get_conjure_hook_map_returns_map():
    """
    Purpose:
        Verify configured hooks are returned to the caller.
    Contract:
        SpellbookCreationSystem.get_conjure_hook_map returns the stored hooks mapping.
    Returns:
        None.
    Raises:
        AssertionError: If the mapping does not match.
    """
    hooks = {"on_conduit_pre_created": [lambda: None]}
    cfg = DummyConfig(hooks=hooks)
    sb = Spellbook(configuration=cfg)
    sb._logger = DummySafeLogger()
    assert SpellbookCreationSystem.get_conjure_hook_map(sb) == hooks


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

    SpellbookCreationSystem.fire_conjure_hooks(sb, {"h": [ok, boom, ok]}, "h", "arg")
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
    sb.cleanup()
    assert sb._cleaned is True
    assert not hasattr(sb, "_spells")
    assert not hasattr(sb, "_logger")
    assert not hasattr(sb, "_configuration")
    assert hasattr(sb, "_lock")


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


def test_run_resolution_phases_scheduler_cleanup_failure_logged(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup failures are swallowed and logged.
    Contract:
        SpellbookCreationSystem.run_resolution_phases completes even if scheduler.cleanup fails.
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

    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", CleanupBoomScheduler)
    sb._logger = DummySafeLogger()
    results = _run_resolution_phases(sb, "cid")
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
        SpellbookCreationSystem.check_system_state raises only when expect_raises is True.
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
            SpellbookCreationSystem.check_system_state(sb, policy, dynamic=not automatic)
    else:
        SpellbookCreationSystem.check_system_state(sb, policy, dynamic=not automatic)


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
        SpellbookCreationSystem.fire_conjure_hooks leaves the call log unchanged in no-op cases.
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

    SpellbookCreationSystem.fire_conjure_hooks(sb, hook_map, hook_name, "x")
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
        SpellbookCreationSystem.get_conjure_hook_map returns None or the hooks mapping as expected.
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
    result = SpellbookCreationSystem.get_conjure_hook_map(sb)
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
        SpellbookCreationSystem.define_conduit_into_spells sets owner metadata for the spell.
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
    SpellbookCreationSystem.define_conduit_into_spells(sb, conduit)
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
    compiler_system = SpellCompilerSystem()
    assert SpellbookCreationSystem.phase_requirements_factory(sb, scheduler, compiler_system) == []
    assert SpellbookCreationSystem.phase_symbolic_graph_factory(sb, scheduler, compiler_system) == []
    assert SpellbookCreationSystem.phase_local_frame_factory(sb, scheduler, compiler_system) == []
    assert SpellbookCreationSystem.phase_validation_factory(sb, scheduler, compiler_system) == []
    assert SpellbookCreationSystem.phase_root_blueprints_factory(sb, scheduler, compiler_system, "cid") == []
    assert SpellbookCreationSystem.phase_occurrence_plan_factory(sb, scheduler, compiler_system, "cid") == []
    assert SpellbookCreationSystem.phase_injection_plan_factory(sb, scheduler, compiler_system, "cid") == []
    assert SpellbookCreationSystem.phase_patch_maps_factory(sb, scheduler, compiler_system, "cid") == []
    assert SpellbookCreationSystem.phase_system_validation_factory(sb, scheduler, compiler_system, "cid") == []
    assert SpellbookCreationSystem.phase_change_control_factory(sb, scheduler, compiler_system, "cid") == []


def test_run_resolution_phases_with_multiple_spells():
    """
    Purpose:
        Verify resolution phases run with multiple spells present.
    Contract:
        SpellbookCreationSystem.run_resolution_phases returns all expected phase keys.
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
    results = _run_resolution_phases(sb, "cid")
    assert set(results.keys()) == {
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "occurrence_plan",
        "injection_plan",
        "execution_plan",
        "patch_maps",
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


def test_cleanup_spells_requires_live_spell_map():
    """
    Purpose:
    Verify the internal spell cleanup helper requires a live spell map.
    Contract:
        `_cleanup_spells()` is an internal helper and raises when `_spells`
        has already been torn down or replaced with `None`.
    Returns:
        None.
    Raises:
        AssertionError: If _spells is mutated unexpectedly.
    """
    sb = Spellbook()
    sb._spells = None
    sb._logger = DummySafeLogger()
    with pytest.raises(AttributeError):
        sb._cleanup_spells()


def test_cleanup_components_clears_contracts_and_versions():
    """
    Purpose:
        Ensure cleanup clears contracted maps, id maps, and version caches.
    Contract:
        _cleanup_components nulls contracted spell maps, id maps, and version caches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted state is not cleared.
    """
    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._lookup_spells = {"k": DummySpellIndex()}
    sb._spells_by_id = {"owned": DummySpell(spell_id="owned")}
    sb._contracted_spells = {"c": {DummySpellIndex(): DummySpell()}}
    sb._lookup_contracted_spells = {"c": {"k": DummySpellIndex()}}
    sb._spell_versions = {"v"}
    sb._contracted_versions = {"c": {"v"}}
    sb._contracted_spells_by_id = {"c": {"contracted": DummySpell(spell_id="contracted")}}
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    assert not hasattr(sb, "_spells")
    assert not hasattr(sb, "_spells_by_id")
    assert not hasattr(sb, "_contracted_spells")
    assert not hasattr(sb, "_contracted_versions")
    assert not hasattr(sb, "_contracted_spells_by_id")


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
    assert not hasattr(sb, "_bind")
    assert hasattr(sb, "_lock")
    assert not hasattr(sb, "_logger")


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
        SpellbookCreationSystem.fire_conjure_hooks executes all hooks and ignores failures.
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

    SpellbookCreationSystem.fire_conjure_hooks(sb, {"h": [ok, boom, ok]}, "h", "val")
    assert calls == [("ok", "val"), ("ok", "val")]


def test_get_conjure_hook_map_handles_exception():
    """
    Purpose:
        Ensure exceptions during hook lookup are swallowed.
    Contract:
        SpellbookCreationSystem.get_conjure_hook_map returns None when get_hooks raises.
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
    assert SpellbookCreationSystem.get_conjure_hook_map(sb) is None


def test_initialize_logging_fallback_on_provider_failure(monkeypatch):
    """
    Purpose:
        Ensure initialization falls back when provider resolution fails.
    Contract:
        Spellbook uses DummySafeLogger even if provider resolution raises.
    Args:
        monkeypatch: Pytest fixture for patching dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If fallback logger is not set.
    """
    monkeypatch.setattr(
        "melder.aether.spellbook.spellbook.InitHelpers.resolve_channel_logger",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    sb = Spellbook(configuration=DummyConfig())
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
    assert not hasattr(sb, "_configuration")


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
    assert not hasattr(sb, "_logger")


def test_run_resolution_phases_cleans_scheduler_even_on_error(monkeypatch):
    """
    Purpose:
        Ensure scheduler cleanup runs even when phases fail.
    Contract:
        SpellbookCreationSystem.run_resolution_phases raises and still cleans the scheduler.
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
    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", lambda *a, **k: sched)
    with pytest.raises(RuntimeError):
        _run_resolution_phases(sb, "cid")
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
    spell.is_existing_creation = False
    spell._compiler_artifact._root_blueprint_phase5 = object()
    sb._spells = {DummySpellIndex(sid="abc"): spell}
    scheduler = DummyPhaseScheduler(sb, None)
    compiler_system = SpellCompilerSystem()
    for units in (
        SpellbookCreationSystem.phase_requirements_factory(sb, scheduler, compiler_system),
        SpellbookCreationSystem.phase_symbolic_graph_factory(sb, scheduler, compiler_system),
        SpellbookCreationSystem.phase_local_frame_factory(sb, scheduler, compiler_system),
        SpellbookCreationSystem.phase_validation_factory(sb, scheduler, compiler_system),
        SpellbookCreationSystem.phase_root_blueprints_factory(sb, scheduler, compiler_system, "cid"),
        SpellbookCreationSystem.phase_occurrence_plan_factory(sb, scheduler, compiler_system, "cid"),
        SpellbookCreationSystem.phase_injection_plan_factory(sb, scheduler, compiler_system, "cid"),
        SpellbookCreationSystem.phase_patch_maps_factory(sb, scheduler, compiler_system, "cid"),
        SpellbookCreationSystem.phase_system_validation_factory(sb, scheduler, compiler_system, "cid"),
        SpellbookCreationSystem.phase_change_control_factory(sb, scheduler, compiler_system, "cid"),
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
    with pytest.raises(RuntimeError):
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


def test_cleanup_components_is_single_use_internal_helper():
    """
    Purpose:
    Verify `_cleanup_components()` is not an idempotent public surface.
    Contract:
        A second direct call fails once the first call has deleted owned
        fields.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._cleanup_components()
    with pytest.raises(AttributeError):
        sb._cleanup_components()


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
    assert not hasattr(sb, "_bind")


def test_fire_conjure_hooks_passes_args_and_kwargs():
    """
    Purpose:
        Verify hook invocation passes positional and keyword arguments.
    Contract:
        SpellbookCreationSystem.fire_conjure_hooks passes provided args to the hook.
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

    SpellbookCreationSystem.fire_conjure_hooks(sb, {"h": [hook]}, "h", "x")
    assert captured == [("x", None)]


def test_define_conduit_handles_missing_owner_method():
    """
    Purpose:
        Ensure conduit definition tolerates owner hook failures.
    Contract:
        SpellbookCreationSystem.define_conduit_into_spells invokes the hook and swallows errors.
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
    SpellbookCreationSystem.define_conduit_into_spells(sb, DummyConduit())
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
    compiler_system = SpellCompilerSystem()
    req_units = SpellbookCreationSystem.phase_requirements_factory(sb, scheduler, compiler_system)
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

    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, version_id, frame: fake_check_for_spell(version_id, frame))
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

    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, version_id, frame: fake_check_for_spell(version_id, frame))
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
    sb._contracted_spells_by_id = {}
    sb._conduit = DummyConduit(cid="borrower", name="borrower")
    sb._create_link_contract("cid")
    assert "cid" in sb._contracted_spells
    assert "cid" in sb._lookup_contracted_spells
    assert "cid" in sb._contracted_versions
    assert "cid" in sb._contracted_spells_by_id


def test_register_owned_spell_id_adds_mapping():
    """
    Purpose:
        Verify owned spell_id registration populates the owned map.
    Contract:
        _register_owned_spell_id stores the spell by current id.
    Returns:
        None.
    Raises:
        AssertionError: If the owned id map is missing the entry.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="owned-id")
    sb._register_owned_spell_id("owned-id", spell)
    assert sb._spells_by_id["owned-id"] is spell


def test_register_owned_spell_id_rejects_collision():
    """
    Purpose:
        Ensure owned spell_id registration rejects collisions.
    Contract:
        _register_owned_spell_id raises when the id maps to a different spell.
    Returns:
        None.
    Raises:
        AssertionError: If a collision does not raise.
    """
    sb = Spellbook()
    spell_a = DummySpell(spell_id="owned-id")
    spell_b = DummySpell(spell_id="owned-id")
    sb._register_owned_spell_id("owned-id", spell_a)
    with pytest.raises(RuntimeError, match="spell_id collision"):
        sb._register_owned_spell_id("owned-id", spell_b)


def test_update_owned_spell_id_updates_map_and_versions():
    """
    Purpose:
        Verify owned spell_id updates swap map entries and track versions.
    Contract:
        _update_owned_spell_id removes the old id and registers the new id.
    Returns:
        None.
    Raises:
        AssertionError: If the map or version cache is not updated.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="old-id")
    sb._spell_versions = {"old-id"}
    sb._register_owned_spell_id("old-id", spell)
    sb._update_owned_spell_id("old-id", "new-id", spell)
    assert "old-id" not in sb._spells_by_id
    assert sb._spells_by_id["new-id"] is spell
    assert "new-id" in sb._spell_versions


def test_update_owned_spell_id_replaces_nexus_record_when_publish_enabled(monkeypatch):
    """
    Purpose:
        Verify owned spell-id updates replace the canonical Nexus spell record.
    Contract:
        `_update_owned_spell_id` removes the old Nexus record key and publishes
        the new one when Nexus publication is enabled.
    Returns:
        None.
    Raises:
        AssertionError: If Nexus remove/publish calls are not made as expected.
    """
    from melder.aether.aether import Aether
    from melder.nexus.nexus import Nexus

    Aether._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Spellbook._aether = Aether()

    sb = Spellbook()
    sb._nexus_publish_enabled = True
    sb._aetheric_frame = "default"
    sb._spell_versions = {"old-id"}
    spell = DummySpell(spell_id="new-id")
    spell._owner_conduit_id = "owner-cid"
    sb._register_owned_spell_id("old-id", spell)

    removed = []
    published = []

    monkeypatch.setattr(
        Nexus,
        "_remove_spell_record",
        lambda self, spellbook_id, spell_id, frame_name: removed.append(
            (spellbook_id, spell_id, frame_name)
        ) or True,
    )
    monkeypatch.setattr(
        Nexus,
        "_publish_spell_record",
        lambda self, spellbook, spell_obj, owner_conduit_id: published.append(
            (spellbook._id, spell_obj.spell_id, owner_conduit_id)
        ) or True,
    )

    sb._update_owned_spell_id("old-id", "new-id", spell)

    assert removed == [(sb._id, "old-id", "default")]
    assert published == [(sb._id, "new-id", "owner-cid")]


def test_unregister_owned_spell_id_removes_nexus_record_when_publish_enabled(monkeypatch):
    """
    Purpose:
        Verify owned spell removal clears the canonical Nexus spell record.
    Contract:
        `_unregister_owned_spell_id` removes the Nexus record when publication
        is enabled.
    Returns:
        None.
    Raises:
        AssertionError: If the Nexus remove call is missing.
    """
    from melder.aether.aether import Aether
    from melder.nexus.nexus import Nexus

    Aether._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Spellbook._aether = Aether()

    sb = Spellbook()
    sb._nexus_publish_enabled = True
    sb._aetheric_frame = "default"
    spell = DummySpell(spell_id="owned-id")
    sb._register_owned_spell_id("owned-id", spell)

    removed = []

    monkeypatch.setattr(
        Nexus,
        "_remove_spell_record",
        lambda self, spellbook_id, spell_id, frame_name: removed.append(
            (spellbook_id, spell_id, frame_name)
        ) or True,
    )

    sb._unregister_owned_spell_id("owned-id", spell)

    assert removed == [(sb._id, "owned-id", "default")]


def test_spell_id_pool_matches_owned_and_contracted_union() -> None:
    """
    Purpose:
        Verify spell_id_pool reflects the union of owned and contracted ids.
    Contract:
        _spell_id_pool keys equal owned ids plus all contracted ids, and each
        pooled spell instance matches the source map.
    Returns:
        None.
    Raises:
        AssertionError: If pool keys or values diverge from the owned/contracted maps.
    """
    sb = Spellbook()
    owned_spell = DummySpell(spell_id="owned-id")
    contracted_spell = DummySpell(spell_id="contracted-id")
    sb._register_owned_spell_id("owned-id", owned_spell)
    sb._conduit = DummyConduit(cid="borrower", name="borrower")
    sb._create_link_contract("peer")
    sb._register_contracted_spell_id("peer", "contracted-id", contracted_spell)

    # Materialize id sets for deterministic comparison of union coverage.
    owned_ids = set(sb._spells_by_id.keys())
    contracted_ids = set()
    for spell_map in sb._contracted_spells_by_id.values():
        contracted_ids.update(spell_map.keys())
    expected_ids = owned_ids.union(contracted_ids)

    assert set(sb._spell_id_pool.keys()) == expected_ids
    for spell_id in expected_ids:
        pooled = sb._spell_id_pool[spell_id]
        if spell_id in sb._spells_by_id:
            assert pooled is sb._spells_by_id[spell_id]
            continue
        matched = None
        for spell_map in sb._contracted_spells_by_id.values():
            if spell_id in spell_map:
                matched = spell_map[spell_id]
                break
        assert matched is not None
        assert pooled is matched


def test_unregister_owned_spell_id_removes_mapping() -> None:
    """
    Purpose:
        Verify owned spell_id unregistration clears owned maps.
    Contract:
        _unregister_owned_spell_id removes entries from the owned id map and pool.
    Returns:
        None.
    Raises:
        AssertionError: If owned maps retain the removed spell_id.
    """
    sb = Spellbook()
    spell = DummySpell(spell_id="owned-id")
    sb._register_owned_spell_id("owned-id", spell)
    assert sb._spells_by_id["owned-id"] is spell
    assert sb._spell_id_pool["owned-id"] is spell
    sb._unregister_owned_spell_id("owned-id", spell)
    assert "owned-id" not in sb._spells_by_id
    assert "owned-id" not in sb._spell_id_pool


def test_unregister_owned_spell_id_rejects_mismatch() -> None:
    """
    Purpose:
        Ensure owned spell_id unregistration rejects mismatched spells.
    Contract:
        _unregister_owned_spell_id raises when the id maps to a different spell.
    Returns:
        None.
    Raises:
        AssertionError: If the mismatch does not raise.
    """
    sb = Spellbook()
    spell_a = DummySpell(spell_id="owned-id")
    spell_b = DummySpell(spell_id="owned-id")
    sb._register_owned_spell_id("owned-id", spell_a)
    with pytest.raises(RuntimeError, match="Owned spell_id mapped"):
        sb._unregister_owned_spell_id("owned-id", spell_b)


def test_register_contracted_spell_id_adds_mapping():
    """
    Purpose:
        Verify contracted spell_id registration populates the per-conduit map.
    Contract:
        _register_contracted_spell_id stores the spell under the conduit id.
    Returns:
        None.
    Raises:
        AssertionError: If the contracted id map is missing the entry.
    """
    sb = Spellbook()
    sb._conduit = DummyConduit(cid="borrower", name="borrower")
    sb._create_link_contract("peer")
    spell = DummySpell(spell_id="contracted-id")
    sb._register_contracted_spell_id("peer", "contracted-id", spell)
    assert sb._contracted_spells_by_id["peer"]["contracted-id"] is spell


def test_update_contracted_spell_id_updates_map_and_versions():
    """
    Purpose:
        Verify contracted spell_id updates swap map entries and track versions.
    Contract:
        _update_contracted_spell_id removes the old id and registers the new id.
    Returns:
        None.
    Raises:
        AssertionError: If the map or version cache is not updated.
    """
    sb = Spellbook()
    sb._conduit = DummyConduit(cid="borrower", name="borrower")
    sb._create_link_contract("peer")
    spell = DummySpell(spell_id="old-id")
    sb._register_contracted_spell_id("peer", "old-id", spell)
    sb._contracted_versions["peer"] = {"old-id"}
    sb._update_contracted_spell_id("peer", "old-id", "new-id", spell)
    assert "old-id" not in sb._contracted_spells_by_id["peer"]
    assert sb._contracted_spells_by_id["peer"]["new-id"] is spell
    assert "new-id" in sb._contracted_versions["peer"]


def test_unregister_contracted_spell_id_removes_mapping():
    """
    Purpose:
        Verify contracted spell_id removal clears the map entry.
    Contract:
        _unregister_contracted_spell_id removes the spell from the id map.
    Returns:
        None.
    Raises:
        AssertionError: If the id map entry remains after removal.
    """
    sb = Spellbook()
    sb._conduit = DummyConduit(cid="borrower", name="borrower")
    sb._create_link_contract("peer")
    spell = DummySpell(spell_id="contracted-id")
    sb._register_contracted_spell_id("peer", "contracted-id", spell)
    sb._unregister_contracted_spell_id("peer", "contracted-id", spell)
    assert "contracted-id" not in sb._contracted_spells_by_id["peer"]


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
    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, *_: False)
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
    monkeypatch.setattr(type(Spellbook._aether), "_check_for_spell", lambda self, *_: True)
    assert sb.inspect_spell(DummySpell()) == "id"


def test_describe_spells_in_spellbook_returns_authoring_dump_in_stable_order():
    """
    Purpose:
        Verify Spellbook exposes the smaller ACL-authoring dump for visible spells.
    Contract:
        - Uses the spell-id pool as the visible spell set.
        - Returns the requested selector/ownership fields only.
        - Sorts deterministically by spell name, binding name, and spell id.
    Returns:
        None.
    Raises:
        AssertionError: If the dump content or ordering is incorrect.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    alpha_spell = DummySpell(
        "sha-b",
        spell_name="AlphaSpell",
        binding_name="zeta",
        spellframe="FrameB",
        existence=Existence.many,
        owner_conduit_id="conduit-2",
    )
    beta_spell = DummySpell(
        "sha-a",
        spell_name="AlphaSpell",
        binding_name=None,
        spellframe="FrameA",
        existence=Existence.unique,
        owner_conduit_id="conduit-1",
    )
    sb._spell_id_pool = {
        alpha_spell.spell_id: alpha_spell,
        beta_spell.spell_id: beta_spell,
    }

    result = sb.describe_spells_in_spellbook()

    assert result == [
        {
            "spell_id": "sha-a",
            "spell_name": "AlphaSpell",
            "binding_name": "__default__",
            "spellframe": "FrameA",
            "existence": "unique",
            "owner_conduit_id": "conduit-1",
        },
        {
            "spell_id": "sha-b",
            "spell_name": "AlphaSpell",
            "binding_name": "zeta",
            "spellframe": "FrameB",
            "existence": "many",
            "owner_conduit_id": "conduit-2",
        },
    ]


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
        SpellbookCreationSystem.run_resolution_phases cleans the scheduler after completion.
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
    import melder.aether.spellbook.spellbook as spellbook_module
    def _make_scheduler(*args, **kwargs):
        sched = DummyPhaseScheduler(*args, **kwargs)
        sched.cleaned = False
        schedulers.append(sched)
        return sched
    monkeypatch.setattr(spellbook_module, "PhaseScheduler", _make_scheduler)
    results = _run_resolution_phases(sb, "cid")
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
        def __init__(self, dev_ops_manager):
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
                spellbook=None,
                name=None,
                conduit_state=None,
                configuration=None,
                aetheric_frame_name=None,
                aetheric_frame=None,
                policy=None,
                dynamic=None,
                automatic=None,
                logger=None,
                conduit_id=None,
                creation_gate_controller=None,
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
                aetheric_frame_name: Aetheric frame name.
                aetheric_frame: Live frame object.
                policy: Conduit policy value.
                dynamic: Dynamic mode flag.
                automatic: Backward-compatible automatic mode flag.
                logger: Logger instance.
                conduit_id: Optional conduit id override for tests.
                creation_gate_controller: Optional creation-gate controller dependency.
            Returns:
                None.
            """
            self._id = conduit_id or "cid"
            self._name = name or "cname"
            self._aetheric_frame_name = aetheric_frame_name
            self._aetheric_frame = aetheric_frame
            self._creations = {}

    import melder.aether.spellbook.spellbook_creation_system as creation_system_module
    monkeypatch.setattr(creation_system_module, "Conduit", StubConduit)
    # Stub binder to avoid building a real conduit; return the stub directly.
    sb._bind.build_conduit = lambda *a, **k: StubConduit(None, None, None, None, None, None, None)
    sb.conjure(name="root")
    assert hooks_called == ["pre", "activated", "post"]


def test_run_resolution_phases_propagates_phase_exception(monkeypatch):
    """
    Purpose:
        Ensure phase execution errors propagate to the caller.
    Contract:
        SpellbookCreationSystem.run_resolution_phases raises when a phase raises.
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

    sb = Spellbook()
    sb._spells = {DummySpellIndex(): DummySpell()}
    sb._logger = DummySafeLogger()
    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", ExecScheduler)
    monkeypatch.setattr(
        "melder.aether.spellbook.spell_compiler.spell_compiler_system.SpellCompilerSystem.run_phase_requirements",
        lambda self, spell, cancel_event=None: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(RuntimeError):
        _run_resolution_phases(sb, "cid")


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

    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", NoopScheduler)
    monkeypatch.setattr("melder.aether.spellbook.spellbook_creation_system.Conduit", StubConduit)
    sb._validate_and_freeze_configuration = lambda: None
    sb._bind_configuration_to_aether = lambda: None
    sb.conjure(name="root")
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

    monkeypatch.setattr("melder.aether.spellbook.spellbook.PhaseScheduler", NoopScheduler)
    monkeypatch.setattr("melder.aether.spellbook.spellbook_creation_system.Conduit", StubConduit)
    sb._validate_and_freeze_configuration = lambda: None
    sb._bind_configuration_to_aether = lambda: None
    sb.conjure(name="root")
    with pytest.raises(RuntimeError) as excinfo:
        sb.conjure(name="root-2")
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






