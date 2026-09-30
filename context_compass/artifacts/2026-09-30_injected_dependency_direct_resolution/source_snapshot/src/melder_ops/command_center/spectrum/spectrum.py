import inspect
import threading
from melder import new_ulid
from typing import TYPE_CHECKING
from melder import Cleanable, MeldExecutionError
from melder_ops.command_center.spectrum.configurations.spectrum_configuration import SpectrumConfig
from melder_ops.command_center.spectrum.configurations.melder_configuration import MelderConfiguration
from melder_ops.command_center.spectrum.bootstraps.bootstrap_context import MelderOpsBootstrapContext
from melder_ops.command_center.spectrum.bootstraps.command_center_definitions import CommandCenterDefinitions
from melder_ops.command_center.spectrum.spectrum_bootstrap import SpectrumBootstrap
from melder_ops.command_center.spectrum.spectrum_controls import SpectrumControls
from melder_ops.command_center.spectrum.melder_setup.runtime import MelderRuntime

if TYPE_CHECKING:
    from melder_ops.command_center.spectrum.system_wide_tools.context_config import SpectrumContextConfig
    from melder_ops.command_center.spectrum.system_wide_tools.utilities import SpectrumUtilities
    from melder_ops.command_center.spectrum.system_wide_tools.builders import SpectrumBuilders
    from melder_ops.command_center.spectrum.system_wide_tools.resources import SpectrumResources
    from melder_ops.command_center.spectrum.interchange.interchange import Interchange
    from melder_ops.command_center.agents.spectre.spectre import Spectre
    from melder_ops.command_center.agents.agent_builder import AgentBuilder
    from melder_ops.command_center.activity.builder import ActivityBuilder
    from melder_ops.command_center.mission.builder import MissionBuilder
    from melder_ops.command_center.agent_pools.agent_pool_builder import AgentPoolBuilder
    from melder_ops.command_center.strategic_command.strategic_command import StrategicCommand
    from melder_ops.command_center.spectrum.toolbox.toolbox import Toolbox
    from melder_ops.command_center.spectrum.actions.actions import Actions
    from collections.abc import Callable
    from typing import Dict, Optional
    from melder import Conduit, Spellbook
    from melder_ops.command_center.command_center import CommandCenter
    from melder_ops.command_center.spectrum.configurations.command_center import CommandCenterConfig
    from melder_ops.command_center.spectrum.iris.iris import Iris
    from melder_ops.command_center.spectrum.iris.channel_logger import ChannelLogger
    from melder_ops.command_center.spectrum.bootstraps.iris_bootstrap import IrisBootstrap

class Spectrum(Cleanable):
    """
    The central, singleton manager and unified factory for the MelderOps framework.

    It manages the entire lifecycle: configuration, initialization of core resources,
    management of the global logging system (Iris), and the creation of operational
    nodes (CommandCenters).

    Optional Application Hosting:
        System recipes run on matching framework events; user recipes run only
        through start before assigned SpectrumControls. Registration is inert.
        Empty no-controls start does nothing, while user registrations without
        controls raise before any work. Direct configure/center use runs only
        its matching system recipes and does not require application controls.

        Callback requests are synchronous. Same-thread framework nesting is
        explicit; overlapping foreign requests, recursive triggers and cleanup
        during execution are refused. User code runs outside the registry lock.
        Each explicit dispatch may repeat its recipes; application state and
        regeneration policy belong to the supplied implementations.

    Callback Ownership:
        Bootstrap and controls instances are borrowed. Spectrum owns their
        registration metadata but never calls their cleanup methods. Stop
        application work before cleanup; cleanup does not implicitly call stop.

    Configuration Ownership:
        The first constructor adopts its supplied or default MelderConfiguration
        until host cleanup. Later explicit input must be that same object; changing
        native settings requires disposing the host and constructing a new one.
        Configure adopts its supplied or default SpectrumConfig for that attempt.
        Host cleanup and configure rollback dispose it after dependent runtime
        objects; callers do not retain a separate disposal obligation.

    Melder Composition:
        Construction initializes dynamic native targets with AI disabled by default,
        then registers the Spectrum class through its host bootstrap and conjures
        the default root without melding the host. Later configure
        builds Iris and the shared services through native class definitions. Spectrum
        retains explicit references and cleanup responsibility for its completed services.
        Additional targets conjure after their final initial contributor. Native
        process roots and supplied conduits remain externally owned. Framework
        borrowers retire before Iris and locally owned native targets.
    """
    _instance: Optional[Spectrum] = None
    _lock: threading.RLock = threading.RLock()
    _initialized: bool = False

    def __new__(cls, melder_config: Optional[MelderConfiguration] = None) -> Spectrum:
        """Reserve the singleton and the first caller's native configuration together.

        Args:
            melder_config: Live native setup facade, or None to select defaults.

        Contract:
            Validate explicit inputs before reserving an instance. Reservation and
            configuration selection share the class lock; a racing default caller
            cannot replace the first caller's custom input. __init__ completes native
            setup under the same lock before any public acquisition returns.

        Raises:
            TypeError: melder_config is not a MelderConfiguration.
            RuntimeError: The supplied configuration is already cleaned.
        """
        if melder_config is not None:
            if not isinstance(melder_config, MelderConfiguration):
                raise TypeError("melder_config must be a MelderConfiguration or None.")
            melder_config.check_cleaned()
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Spectrum, cls).__new__(cls)
                cls._instance._initializing = False
                cls._instance._melder_configuration = melder_config
            return cls._instance

    def __init__(self, melder_config: Optional[MelderConfiguration] = None) -> None:
        """Initialize Melder once while leaving framework configuration for configure().

        Args:
            melder_config: Native setup selected by the first construction. Omission
                initializes defaults. The host owns the selected facade thereafter.

        Thread-safety contract (free-threaded / no-GIL safe):
            Complete initialization under Spectrum._lock. get_instance enters this
            same admission path, so another thread waits for native setup. Recursive
            acquisition on the initializing thread is refused. Publish initialized
            state last, after every field and the default native root are ready.

        Failure and ownership:
            A failed native attempt cleans its locally owned targets/configuration,
            resets the singleton and preserves the original exception. Installed
            process policy remains native-owned. A caller holding a failed provisional
            instance cannot initialize it after the singleton has been replaced.

        Raises:
            RuntimeError: Initialization re-enters, the host is retiring, or a later
                explicit configuration differs from the first adopted facade.
            Exception: Native preparation, binding or conjure fails.
        """
        with Spectrum._lock:
            if self is not Spectrum._instance:
                raise RuntimeError("This Spectrum initialization was retired; acquire a new Spectrum instance.")
            if self._initialized:
                self.check_cleaned()
            if melder_config is not None and melder_config is not self._melder_configuration:
                raise RuntimeError(
                    "Spectrum already selected its Melder configuration. Supply custom settings on the "
                    "first Spectrum(melder_config=...) call, or clean the current host before replacing it."
                )
            if self._initialized:
                return
            if self._initializing:
                raise RuntimeError("Spectrum native initialization cannot recursively acquire Spectrum.")
            self._initializing = True
            super().__init__()

            # --- Core Singleton State and Threading ---
            self._id: str = new_ulid()
            # Borrowed, not owned: this is the CLASS lock, shared with every other
            # instance and with __new__. See _cleanup_core() for why teardown must
            # neither clean nor delete it.
            self._lock: Optional[threading.RLock] = Spectrum._lock
            self._configured: bool = False

            # --- Configuration and Context ---
            self._cfg: Optional[SpectrumConfig] = None
            self._environment: Optional[str] = None
            self._melder_runtime: Optional[MelderRuntime] = None
            self._configure_retry_blocked = False

            # --- Logging Fabric (IRIS) ---
            self._iris: Optional[Iris] = None
            self._logger: Optional[ChannelLogger] = None
            self._iris_bootstrap: Optional[IrisBootstrap] = None
            self._iris_bootstrap_context: Optional[MelderOpsBootstrapContext] = None

            # --- Global Registries (Service Locators) ---
            self._command_centers: Dict[str, CommandCenter] = {}      # CCs keyed by name
            self._all_command_centers: Dict[str, CommandCenter] = {}  # CCs keyed by ID

            # Borrowed recipes own their metadata; registration pins identity/routing.
            self._bootstraps: Dict[str, SpectrumBootstrap] = {}
            self._controls: Optional[SpectrumControls] = None
            self._operations: list[str] = []
            self._operation_owner: Optional[int] = None
            self._configuring = False

            # --- Shared Resource Managers (The "Resources Department") ---
            self.interchange: Optional[Interchange] = None
            self.toolbox: Optional[Toolbox] = None
            self.actions: Optional[Actions] = None

            # --- Shared Component Builders (The "Factories") ---
            self.agent_builder: Optional[AgentBuilder] = None
            self.activity_builder: Optional[ActivityBuilder] = None
            self.mission_builder: Optional[MissionBuilder] = None
            self.agent_pool_builder: Optional[AgentPoolBuilder] = None
            self.spectre_builder: Optional[Spectre] = None
            self.strategic_command: Optional[StrategicCommand] = None

            # Native-created access services explicitly retained and owned by Spectrum.
            self.builders: Optional[SpectrumBuilders] = None
            self.resources: Optional[SpectrumResources] = None
            self.utilities: Optional[SpectrumUtilities] = None
            self.context_config: Optional[SpectrumContextConfig] = None

            try:
                if self._melder_configuration is None:
                    self._melder_configuration = MelderConfiguration()
                self._melder_runtime = MelderRuntime(self._melder_configuration)
                self._melder_runtime.initialize()
                self._melder_runtime.register_host(Spectrum)
                self._melder_runtime.finalize_default()
            except BaseException as error:
                try:
                    self.cleanup()
                except Exception as cleanup_error:
                    error.add_note(f"Spectrum initialization cleanup also failed: {cleanup_error}")
                raise
            finally:
                self._initializing = False

            # Publish LAST: native targets as well as ordinary fields must be ready.
            self._initialized = True

#region Destructor
    def cleanup(self) -> None:
        """
        Disposes Spectrum and all managed resources by orchestrating a cascading teardown.
        Idempotent and thread-safe.

        Callback Contract:
            Refuse cleanup while an application control or bootstrap invocation
            is active, before disposing any resources. Stop application work
            explicitly before cleanup; this method releases borrowed bootstrap
            and controls references without invoking their stop or cleanup hooks.

        Raises:
            RuntimeError: A callback request is still active. Wait for it to
                finish before retrying cleanup; no teardown occurred on refusal.
            Exception: Configuration disposal failed. Host references and singleton
                state are still released before that failure is raised.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._require_idle_operations("cleanup")

            if self._logger is not None:
                self._logger.warning(
                    "Shutting down entire MelderOps System.",
                    exc_info=False, _manual_stack=True, _method_name="cleanup"
                )
            self._cleaned = True

            # Phase 1: explicitly retire owned consumers before their shared providers.
            self._cleanup_command_centers()
            self._cleanup_services()
            self._cleanup_components()
            registration_error = self._remove_framework_bindings()

        # Phase 2: finish teardown outside the lock
        try:
            self._cleanup_core()
        except Exception as error:
            if registration_error is not None:
                error.add_note(f"Framework registration cleanup also failed: {registration_error}")
            raise
        if registration_error is not None:
            raise registration_error


    def _cleanup_command_centers(self) -> None:
        """
        Safely cleans up all active CommandCenters and their registries.

        Matches legacy order:
          1) iterate/cleanup via _all_command_centers (id-keyed)
          2) cleanup _all_command_centers registry
          3) cleanup _command_centers registry
        """
        # Nothing to do if both registries are missing
        if self._all_command_centers is None and self._command_centers is None:
            return

        # 1) Clean each CommandCenter via the id-keyed directory (legacy behaviour)
        try:
            if self._all_command_centers is not None:
                for cc_id, cc in list(self._all_command_centers.items()):
                    try:
                        cc.cleanup()
                    except Exception as e:
                        if self._logger is not None:
                            self._logger.error(
                                f"Error during CommandCenter cleanup (id={cc_id}): {e}",
                                exc_info=True, _manual_stack=True, _method_name="_cleanup_command_centers"
                            )
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"Error while iterating _all_command_centers for cleanup: {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_command_centers"
                )

        # 2) Best-effort cleanup of the id-keyed registry first (legacy order)
        try:
            if self._all_command_centers is not None:
                self._all_command_centers.clear()
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"Error cleaning _all_command_centers registry: {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_command_centers"
                )

        # 3) Then cleanup the name-keyed registry
        try:
            if self._command_centers is not None:
                self._command_centers.clear()
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"Error cleaning _command_centers registry: {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_command_centers"
                )

    def _cleanup_services(self) -> None:
        """
        Clean the four owned access services before their borrowed managers.

        Partial construction leaves unset fields as None. Each completed service
        releases its own resources; shared manager disposal belongs to Spectrum's
        following component phase. Continue after ordinary errors and log them.
        """
        services = {
            "SpectrumResources": self.resources,
            "SpectrumBuilders": self.builders,
            "SpectrumUtilities": self.utilities,
            "SpectrumContextConfig": self.context_config,
        }
        for name, instance in services.items():
            if instance is not None:
                try:
                    instance.cleanup()
                except Exception as e:
                    if self._logger is not None:
                        self._logger.error(
                            f"Error during {name} cleanup: {e}",
                            exc_info=True, _manual_stack=True, _method_name="_cleanup_services"
                        )


    def _cleanup_components(self) -> None:
        """
        Clean framework components explicitly before purging their native creations.
        """
        _component_map = {
            "Interchange": self.interchange,
            "Toolbox": self.toolbox,
            "Actions": self.actions,
            "AgentBuilder": self.agent_builder,
            "ActivityBuilder": self.activity_builder,
            "MissionBuilder": self.mission_builder,
            "AgentPoolBuilder": self.agent_pool_builder,
            "Spectre": self.spectre_builder,
            "StrategicCommand": self.strategic_command,
        }
        for name, instance in _component_map.items():
            if instance is not None:
                try:
                    instance.cleanup()
                except Exception as e:
                    if self._logger is not None:
                        self._logger.error(
                            f"Error during {name} cleanup: {e}",
                            exc_info=True, _manual_stack=True, _method_name="_cleanup_components"
                        )


    def _cleanup_core(self) -> None:
        """
        Final teardown outside the main lock:
          1) drop owned component references
          2) retire the Iris bootstrap and its native registrations
          3) retire locally owned native targets and adopted configurations
          4) release the borrowed class lock and final logger reference
          5) reset singleton flags/state

        Field policy:
            Owned object references are DELETED, so the first post-clean touch raises
            AttributeError at the real call site rather than sliding through a falsy
            None. State flags (`_configured`, `_environment`) and the
            class-level singleton markers are ASSIGNED, not deleted: they are scalars
            that later calls legitimately read, and `_instance`/`_initialized` must stay
            bound for the next Spectrum to construct.
        """
        # 1) Drop owned component references
        del self.interchange
        del self.toolbox
        del self.actions
        del self.agent_builder
        del self.activity_builder
        del self.mission_builder
        del self.agent_pool_builder
        del self.spectre_builder
        del self.strategic_command
        del self.builders
        del self.resources
        del self.utilities
        del self.context_config

        # Release borrowed callback references without disposing application objects.
        for bootstrap in self._bootstraps.values():
            bootstrap._detach_registration()
        self._bootstraps.clear()
        del self._bootstraps
        del self._controls
        del self._operations
        del self._operation_owner
        del self._configuring

        # 2) Iris's native creations retire after their framework consumers.
        errors: list[Exception] = []
        for failure in (
            self._cleanup_iris_bootstrap(), self._cleanup_configuration(),
            self._remove_configuration_bindings(), self._cleanup_native_configuration(), self._cleanup_melder(),
        ):
            if failure is not None:
                errors.append(failure)
        del self._iris
        del self._iris_bootstrap
        del self._iris_bootstrap_context
        del self._melder_runtime
        del self._melder_configuration

        # 3) Release the lock reference WITHOUT cleaning or deleting it.
        #    `self._lock` is `Spectrum._lock` - a CLASS attribute shared by every
        #    instance and used by __new__ to build the next one. Two consequences:
        #      - Cleaning it would destroy the lock the next Spectrum needs. The old
        #        `isinstance(lock, Cleanable)` branch never fired because the
        #        class lock is always a plain threading.RLock.
        #      - `del self._lock` would be worse than useless: the instance attribute
        #        shadows the class attribute, so deleting it silently falls back to
        #        the live class lock instead of raising. That is the class-default
        #        trap, the same shape as AgentTemplate.tags.
        #    Assigning None is therefore correct here and is a deliberate exception
        #    to the delete-owned-fields rule: this reference was borrowed, not owned.
        self._lock = None

        # 4) Logger last - everything above may need to report its own teardown.
        del self._logger
        del self._cfg
        del self._command_centers
        del self._all_command_centers
        del self._configure_retry_blocked

        # 5) Reset singleton state and config markers
        self._environment = None
        self._configured = False
        with Spectrum._lock:
            self._initialized = False
            Spectrum._instance = None
            Spectrum._initialized = False
        if len(errors) == 1:
            raise errors[0]
        if errors:
            raise ExceptionGroup("Spectrum native/configuration teardown failed.", errors)

    def _cleanup_iris_bootstrap(self, *, preserve_bindings: bool = False) -> Optional[Exception]:
        """Retire Iris-owned construction while preserving the initialized native target.

        Contract:
            Framework borrowers have already stopped. The bootstrap owns its Iris
            and introduced bindings; the host owns only the retained
            bootstrap/context wrappers. On rollback, purge runtime creations and retain
            the recipe/context and definitions for another build. Terminal cleanup
            disposes the recipe and then releases the context.
            Both fields are optional until framework configure reaches Iris setup.

        Args:
            preserve_bindings: True for recoverable configure rollback; False for shutdown.

        Returns:
            A collected cleanup failure, or None. The caller reports it after the
            remaining teardown and resets or deletes framework references.
        """
        errors: list[Exception] = []
        if self._iris_bootstrap is not None:
            try:
                if preserve_bindings:
                    self._iris_bootstrap.purge()
                else:
                    self._iris_bootstrap.cleanup()
            except Exception as error:
                errors.append(error)
            finally:
                if not preserve_bindings:
                    self._iris_bootstrap = None
        if self._iris_bootstrap_context is not None and (
                not preserve_bindings or self._iris_bootstrap is None):
            try:
                self._iris_bootstrap_context.cleanup()
            except Exception as error:
                errors.append(error)
            finally:
                self._iris_bootstrap_context = None
        if errors:
            return ExceptionGroup("Iris bootstrap cleanup failed.", errors)
        return None

    def _cleanup_native_configuration(self) -> Optional[Exception]:
        """Dispose the adopted native facade after its runtime has retired.

        Returns:
            None on success or before adoption; otherwise the disposal exception.
            Installed native policies keep the custody recorded by the facade.
            The caller deletes this host reference after collecting the outcome.
        """
        if self._melder_configuration is None:
            return None
        try:
            self._melder_configuration.cleanup()
        except Exception as error:
            return error
        return None

    def _cleanup_configuration(self) -> Optional[Exception]:
        """Dispose the adopted configuration after its runtime consumers stop.

        Returns:
            None when no configuration was adopted or disposal succeeds; otherwise
            the disposal exception for the caller to report after finishing teardown.

        Contract:
            The caller coordinates host shutdown and releases _cfg afterward.
            Capture ordinary cleanup failures so they cannot strand host references
            or replace the original configure failure during rollback.
        """
        if self._cfg is None:
            return None
        try:
            self._cfg.cleanup()
        except Exception as error:
            return error
        return None


#endregion Destructor

    @property
    def id(self) -> str:
        """The unique identifier for this Spectrum instance (ULID)."""
        return self._id

    @classmethod
    def get_instance(cls) -> Spectrum:
        """Acquire the initialized singleton, selecting native defaults on first use.

        Returns:
            The global Spectrum after native initialization completes. Framework
            configuration remains a separate configure call.

        Contract:
            Enter constructor admission even when an instance is already reserved,
            so concurrent callers never receive partially initialized native state.
            Custom settings must reach Spectrum(melder_config=...) before this call.

        Raises:
            RuntimeError: Acquisition re-enters initialization or encounters teardown.
            Exception: First native initialization fails.
        """
        return cls()

    @classmethod
    def current(cls) -> Optional[Spectrum]:
        """Borrow an initialized live host without constructing one.

        Returns:
            The existing host, including before framework configure, or None while
            absent, still initializing or cleaned. This is an observation, not a
            lifetime reservation; the caller coordinates later use with its owner.

        Threading:
            Read publication under the host's class lock. Convenience service
            lookups use this path so early logging never recursively creates a host.
        """
        with cls._lock:
            host = cls._instance
            if host is None or not host._initialized or host.cleaned:
                return None
            return host

    def create_spectrum_config(self) -> SpectrumConfig:
        """
        Factory method to create a new SpectrumConfig set in an unconfigured, mutable state,
        which can be used as a fluent builder for user configuration.

        Returns:
            SpectrumConfig: A new instance of SpectrumConfig with default settings.
        """
        return SpectrumConfig(factory_configure=True)

    def register_bootstrap(self, bootstrap: SpectrumBootstrap) -> None:
        """Register one prepared recipe without executing or configuring anything.

        Args:
            bootstrap: Live SpectrumBootstrap instance carrying its own metadata.
                System recipes require a trigger; user recipes must have none.

        Raises:
            TypeError: The value or build callback violates the synchronous contract.
            ValueError: Metadata is invalid or the name is already registered.
            RuntimeError: Spectrum is cleaned or the recipe is already registered.

        Ownership and Concurrency:
            Borrow the recipe with its constructor-defined metadata. The caller
            keeps it live until removal and invocation completion. Registration affects
            future selections and does not append work to the captured cohort.
            Controls need not be assigned yet; start validates that relationship.
        """
        if not isinstance(bootstrap, SpectrumBootstrap):
            raise TypeError("bootstrap must be a SpectrumBootstrap instance.")
        self._validate_callback(bootstrap.build, "bootstrap.build")
        self.check_cleaned()
        with Spectrum._lock:
            name = bootstrap._attach_registration()
            if name in self._bootstraps:
                bootstrap._detach_registration()
                raise ValueError(f"Bootstrap {name!r} is already registered.")
            self._bootstraps[name] = bootstrap

    def unregister_bootstrap(self, name: str) -> SpectrumBootstrap:
        """Remove a recipe's registration pin and return its borrowed instance.

        Args:
            name: Exact nonblank registered identity.

        Raises:
            TypeError: name is not str.
            ValueError: name is blank.
            KeyError: No recipe has this name.
            RuntimeError: Spectrum has been cleaned.

        Contract:
            No build, application stop or recipe cleanup is called. The instance's
            metadata remains fixed. A recipe already captured by an invocation is
            not cancelled; its owner must wait for that invocation before disposal.
        """
        self._validate_bootstrap_name(name)
        self.check_cleaned()
        with Spectrum._lock:
            bootstrap = self._bootstraps.pop(name)
            bootstrap._detach_registration()
            return bootstrap

    def get_bootstrap(self, name: str) -> SpectrumBootstrap:
        """Return the borrowed recipe registered under an exact identity.

        Args:
            name: Nonblank, case-sensitive registration name.

        Raises:
            TypeError: name is not str.
            ValueError: name is blank.
            KeyError: The name is absent.
            RuntimeError: Spectrum has been cleaned.

        Contract:
            Lookup is synchronized and performs no configuration or execution.
            The returned recipe remains owned by its caller or Melder registration.
        """
        self._validate_bootstrap_name(name)
        self.check_cleaned()
        with Spectrum._lock:
            return self._bootstraps[name]

    def describe_bootstraps(self) -> list[dict[str, object]]:
        """Inspect name, order, category, active state and trigger without running work.

        Returns:
            Independent value-only metadata dictionaries, ordered by integer
            priority with registration order breaking ties.

        Raises:
            RuntimeError: Spectrum has been cleaned.

        Concurrency:
            Registry membership is captured under the host lock and each recipe
            supplies a dictionary of immutable metadata. Replace registrations
            to change a later selection; mutating this result alters no recipe.
        """
        self.check_cleaned()
        with Spectrum._lock:
            return [
                bootstrap.describe()
                for bootstrap in sorted(self._bootstraps.values(), key=lambda item: item.order)
            ]

    def set_controls(self, controls: Optional[SpectrumControls]) -> None:
        """Assign borrowed application controls without starting or stopping anything.

        Args:
            controls: A concrete SpectrumControls instance, or None to detach it.

        Raises:
            TypeError: The value or one of its callbacks violates the contract.
            RuntimeError: Spectrum is cleaned or replacement would race an active
                request. Lifecycle callbacks cannot replace their own controls.

        Ownership:
            Callers own the old and new objects. Stop their application work before
            replacement. Same-thread framework setup may assign controls when no
            application lifecycle request is active; foreign operations may not.
        """
        if controls is not None:
            if not isinstance(controls, SpectrumControls):
                raise TypeError("controls must be a SpectrumControls instance or None.")
            for name, callback in (
                ("start", controls.start), ("stop", controls.stop),
                ("pause", controls.pause), ("resume", controls.resume),
            ):
                self._validate_callback(callback, f"controls.{name}")
        self.check_cleaned()
        with Spectrum._lock:
            if self._operations and (
                self._operation_owner != threading.get_ident()
                or any(name in ("start", "stop", "pause", "resume") for name in self._operations)
            ):
                self._require_idle_operations("set_controls")
            self._controls = controls

    def get_controls(self) -> Optional[SpectrumControls]:
        """Return the borrowed controls assignment, or None, without invoking it.

        Raises:
            RuntimeError: Spectrum has been cleaned.

        Contract:
            The synchronized lookup is available before configure. It neither
            transfers ownership nor infers the application's running state.
        """
        self.check_cleaned()
        with Spectrum._lock:
            return self._controls

    @property
    def configuration(self) -> SpectrumConfig:
        """Return the host-owned configuration used by framework setup.

        Raises:
            RuntimeError: The host is cleaned, unconfigured, or another thread is
                still completing configure hooks.

        Contract:
            A configuring system recipe may inspect the finalized configuration
            on its owning thread. Other callers receive it after configure succeeds.
            The returned reference is borrowed; Spectrum owns its disposal.
        """
        return self._check_configured()

    @property
    def melder_configuration(self) -> MelderConfiguration:
        """Borrow the native configuration adopted by the first Spectrum construction.

        Contract:
            Available before ordinary configure. The prepared facade belongs to the
            host; callers may inspect its selected native inputs but do not dispose
            it independently. Retrieving it performs no setup or reconfiguration.

        Raises:
            RuntimeError: The host is cleaned or another host operation prevents access.
        """
        self._require_melder()
        return self._melder_configuration

    def start(self) -> None:
        """Run active user recipes, then invoke the assigned application start.

        Returns:
            None. With neither controls nor user registrations, return without
            configuration, system hooks or any application action.

        Raises:
            RuntimeError: User recipes are registered without SpectrumControls,
                the host is cleaned, or a host operation is already active.
            TypeError: A callback does not complete synchronously with None.
            Exception: Configuration, build or application failures propagate.

        Execution:
            Check the controls relationship before side effects, including when
            the registered user recipes are inactive. Ensure configuration when
            controls exist, allowing its system hooks to finish first. Then capture
            active user recipes in numeric order, preserving registration order
            for ties, and run them before controls.start. System recipes are never
            included in the user cohort.

            Every explicit start can run the recipes again. Implementations own
            repeatability and compensation; there is no named-start selection or
            inferred application state machine. Callbacks execute outside the
            registry lock, and admission is released for every exit path.
        """
        self.check_cleaned()
        with Spectrum._lock:
            if self._controls is None:
                if any(not item.system_defined for item in self._bootstraps.values()):
                    raise RuntimeError(
                        "User bootstraps require SpectrumControls before start(); "
                        "assign controls with set_controls() or unregister the user recipes."
                    )
                return
            controls = self._controls
            self._begin_operation("start")
        try:
            if not self.is_configured():
                self.configure()
            with Spectrum._lock:
                bootstraps = self._select_bootstraps(system_defined=False)
            self._dispatch_bootstraps(bootstraps)
            self._invoke_callback(lambda: controls.start(self), "controls.start")
        finally:
            self._finish_operation()

    def stop(self) -> None:
        """Invoke application stop without configuration or bootstrap execution.

        Returns:
            None, including when no controls exist.

        Raises:
            RuntimeError: Spectrum is cleaned or a host operation is active.
            TypeError: The callback returns a value instead of None.
            Exception: Application failures propagate unchanged.

        Contract:
            Each request is synchronous and runs outside the registry lock.
            Controls own early/repeated stop behavior. Dispose host resources
            separately after application work has stopped using them.
        """
        controls = self._begin_control("stop")
        if controls is None:
            return
        try:
            self._invoke_callback(lambda: controls.stop(self), "controls.stop")
        finally:
            self._finish_operation()

    def pause(self) -> None:
        """Invoke optional application pause without running any recipes.

        Returns:
            None, including when controls are absent.

        Raises:
            NotImplementedError: Assigned controls do not implement pause.
            RuntimeError: Spectrum is cleaned or an operation is active.
            TypeError: The callback returns a value instead of None.
            Exception: Application failures propagate unchanged.

        Contract:
            The controls implementation owns valid application state transitions.
            The callback runs synchronously outside the registry lock.
        """
        controls = self._begin_control("pause")
        if controls is None:
            return
        try:
            self._invoke_callback(lambda: controls.pause(self), "controls.pause")
        finally:
            self._finish_operation()

    def resume(self) -> None:
        """Invoke optional application resume without running any recipes.

        Returns:
            None, including when controls are absent.

        Raises:
            NotImplementedError: Assigned controls do not implement resume.
            RuntimeError: Spectrum is cleaned or an operation is active.
            TypeError: The callback returns a value instead of None.
            Exception: Application failures propagate unchanged.

        Contract:
            The controls implementation owns valid application state transitions.
            The callback runs synchronously outside the registry lock.
        """
        controls = self._begin_control("resume")
        if controls is None:
            return
        try:
            self._invoke_callback(lambda: controls.resume(self), "controls.resume")
        finally:
            self._finish_operation()

    def run_system_bootstraps(
        self, trigger: str, command_center: Optional[CommandCenter] = None,
    ) -> None:
        """Run active framework recipes matching one exact trigger.

        Args:
            trigger: Nonblank system condition, such as CONFIGURE, COMMAND_CENTER
                or a custom regeneration condition.
            command_center: Optional borrowed live target. Required for the
                COMMAND_CENTER trigger and supplied by its automatic factory hook.

        Raises:
            TypeError: The trigger type or callback results are invalid.
            ValueError: Trigger is blank or a center event has no target.
            RuntimeError: Host/target is unavailable, another thread owns a host
                operation, or this trigger is recursively invoked.
            Exception: A selected recipe failure propagates unchanged.

        Contract:
            Framework configuration must be available. Automatic configure and
            center hooks use this same dispatcher; custom conditions are explicit.
            The caller supplies the typed center; dispatch checks its liveness
            without repeating a concrete isinstance check.
            Application controls are not required and user recipes are never
            selected. Dispatch does not itself restore, recreate or dispose any
            container; the selected recipes define those effects and their rollback.
        """
        SpectrumBootstrap._validate_name(trigger, "System bootstrap trigger")
        if command_center is not None:
            command_center.check_cleaned()
        if trigger == SpectrumBootstrap.COMMAND_CENTER and command_center is None:
            raise ValueError("The create_command_center trigger requires its target command center.")
        self._check_configured()
        with Spectrum._lock:
            self._begin_operation(f"system:{trigger}", allow_nested=True)
        try:
            with Spectrum._lock:
                bootstraps = self._select_bootstraps(system_defined=True, trigger=trigger)
            self._dispatch_bootstraps(bootstraps, command_center)
        finally:
            self._finish_operation()

    def _select_bootstraps(
        self, *, system_defined: bool, trigger: Optional[str] = None,
    ) -> list[tuple[str, SpectrumBootstrap]]:
        """Capture one matching recipe cohort while the host registry is locked.

        Returns:
            Names and borrowed live recipes in stable numeric order.

        Contract:
            Caller owns Spectrum._lock. All recipe metadata is constructor-only.
            Later registration replacement or removal does not change a cohort
            already captured for this invocation.
        """
        return [
            (name, bootstrap)
            for name, bootstrap in sorted(self._bootstraps.items(), key=lambda item: item[1].order)
            if bootstrap.system_defined == system_defined
            and bootstrap.active
            and (not system_defined or bootstrap.trigger == trigger)
        ]

    def _invoke_bootstrap(
        self, name: str, bootstrap: SpectrumBootstrap,
        command_center: Optional[CommandCenter] = None,
    ) -> None:
        """Invoke a selected live recipe against borrowed host/target references.

        Contract:
            Run outside the registry lock. A previously selected recipe may have
            been unregistered, but its owner must not clean it until this call
            finishes. The caller coordinates lifetime; no liveness probe is added.

        Raises:
            Exception: Build or synchronous-return validation fails.
        """
        self._invoke_callback(
            lambda: bootstrap.build(self, command_center), f"bootstrap {name!r}.build",
        )

    def _dispatch_bootstraps(
        self, bootstraps: list[tuple[str, SpectrumBootstrap]],
        command_center: Optional[CommandCenter] = None,
    ) -> None:
        """Run one captured recipe batch and coordinate its native target completion.

        Args:
            bootstraps: Stable host-selected name/recipe pairs. Later registry edits
                affect future batches, not this invocation.
            command_center: Optional borrowed center passed to matching system recipes.

        Contract:
            Runs outside the registry lock under existing Spectrum operation admission.
            Resolve every native selector before callbacks. Release one contribution
            after successful return and conjure when that target's final hold ends.
            Nested batches retain outer holds. Native initialization always precedes
            recipe dispatch; every selected target must already be declared.

        Failure:
            Abort remaining holds after callback/conjure failure. Annotate abort errors
            without replacing the original exception. Do not retry callbacks or infer
            compensation for arbitrary edits to an existing application graph.
        """
        keys = self._melder_runtime.begin_cohort(bootstraps)
        completed = 0
        try:
            for (name, bootstrap), key in zip(bootstraps, keys):
                self._invoke_bootstrap(name, bootstrap, command_center)
                # Finalization may fail after releasing the hold; do not release it twice.
                completed += 1
                self._melder_runtime.complete_contributor(key)
        except BaseException as error:
            try:
                self._melder_runtime.abort_cohort(keys[completed:])
            except Exception as abort_error:
                # Bookkeeping failure must not hide the recipe/conjure exception.
                error.add_note(f"Melder cohort abort also failed: {abort_error}")
            raise

    def _require_melder(self) -> MelderRuntime:
        """Require a usable native context through Spectrum's established lifetime gate.

        Returns:
            The runtime owned by this initialized host. No context, native frame or
            policy is constructed by this lookup.

        Raises:
            RuntimeError: Spectrum is cleaned, native initialization is incomplete,
                or a foreign thread owns an active host operation.
        """
        self.check_cleaned()
        with Spectrum._lock:
            if not self._initialized:
                raise RuntimeError("Spectrum native initialization has not completed.")
            if self._operations and self._operation_owner != threading.get_ident():
                self._require_idle_operations("access Melder targets")
            return self._melder_runtime

    def get_spellbook(
        self, spellbook_name: Optional[str] = None, *, frame_name: Optional[str] = None,
    ) -> Spellbook:
        """Borrow a declared native book for bootstrap registration or later dynamic binding.

        Args:
            spellbook_name: Logical target name; None uses the selected frame's default.
            frame_name: Declared frame; None uses the configured startup frame.

        Returns:
            The actual native Spellbook. Its owner remains the runtime or the external
            host that supplied it. Lookup never creates an undeclared target.

        Raises:
            KeyError: The effective frame/book pair is unknown.
            RuntimeError: Native initialization is incomplete, host/target is unavailable, or a
                foreign active operation prevents access.

        Lifecycle:
            Available after Spectrum construction, before ordinary configure.
            Callers keep the host and borrowed book alive while using the result.
        """
        return self._require_melder().get_spellbook(spellbook_name, frame_name=frame_name)

    def get_conduit(
        self, spellbook_name: Optional[str] = None, *, frame_name: Optional[str] = None,
    ) -> Conduit:
        """Borrow a declared native root after its initial contributors have finished.

        Args:
            spellbook_name: Explicit logical book name or None for frame-default routing.
            frame_name: Explicit declared frame or None for startup-frame routing.

        Returns:
            The existing live Conduit. Later dispatches retain that identity and use
            native dynamic registration; no additional root or lifetime is created.

        Raises:
            KeyError: The selected target is undeclared.
            RuntimeError: Initial registration or host initialization is incomplete,
                the host/root is unavailable or another operation prevents access.

        Ownership:
            Borrow only. The caller does not acquire cleanup authority over a root
            by retrieving it through Spectrum.
        """
        return self._require_melder().get_conduit(spellbook_name, frame_name=frame_name)

    def _cleanup_melder(self) -> Optional[Exception]:
        """Retire locally owned native targets after their framework and Iris borrowers.

        Returns:
            None when setup was absent or cleanup succeeds; otherwise the ordinary
            cleanup exception for terminal shutdown or failed initialization to report.

        Contract:
            Release the context reference in finally so retry/terminal cleanup cannot
            retain a retired runtime. The host already owns operation admission and
            teardown order. No Aether reset, logger reattachment or new native setup
            is performed here.
        """
        if self._melder_runtime is None:
            return None
        try:
            self._melder_runtime.cleanup()
        except Exception as error:
            return error
        finally:
            self._melder_runtime = None
        return None

    def _remove_framework_bindings(self) -> Optional[Exception]:
        """Purge retired framework creations and remove supplied-instance registrations.

        Returns:
            None when there is no runtime/cohort or removal succeeds; otherwise the
            collected native failure. Completed class registrations and native targets
            survive; a later configure attempt resolves fresh manager creations.

        Contract:
            Only rollback and terminal cleanup call this helper, after consumers finish
            explicit cleanup and operation admission has stopped competing work. Failed IDs remain tracked by the
            runtime; teardown continues and the caller reports the failure.
        """
        if self._melder_runtime is None:
            return None
        try:
            self._melder_runtime.remove_core_assets()
        except Exception as error:
            return error
        return None

    def _remove_configuration_bindings(self) -> Optional[Exception]:
        """Retire registered settings after Iris, preserving disposal errors for the caller.

        Return None before native initialization or after successful retirement.
        The configuration root remains explicitly owned by Spectrum; native purge
        may invoke its idempotent cleanup before Spectrum repeats it.
        """
        if self._melder_runtime is None:
            return None
        try:
            self._melder_runtime.remove_configuration()
        except Exception as error:
            return error
        return None

    def _begin_control(self, name: str) -> Optional[SpectrumControls]:
        """Capture controls and admit a top-level application request atomically.

        Returns:
            The borrowed controls after admission, or None without side effects.

        Raises:
            RuntimeError: Spectrum is cleaned or another operation is active.

        Contract:
            A non-None return must be paired with _finish_operation in finally.
            No callback or configuration work occurs under this helper's lock.
        """
        self.check_cleaned()
        with Spectrum._lock:
            if self._controls is None:
                return None
            controls = self._controls
            self._begin_operation(name)
            return controls

    def _begin_operation(self, name: str, *, allow_nested: bool = False) -> None:
        """Admit serialized host work, allowing explicitly supported same-thread nesting.

        Args:
            name: Internal operation identity, including the system trigger when relevant.
            allow_nested: Permit nesting on the owning thread if this identity
                is not already active.

        Raises:
            RuntimeError: Another thread owns execution, or the
                request would overlap/re-enter a disallowed operation.

        Contract:
            The public entry checks host lifetime before locking. Record ownership
            under Spectrum._lock and release it before callbacks. Each successful
            admission requires exactly one finally-based finish.
        """
        with Spectrum._lock:
            thread_id = threading.get_ident()
            if self._operations and (
                self._operation_owner != thread_id or not allow_nested or name in self._operations
            ):
                self._require_idle_operations(name)
            self._operations.append(name)
            self._operation_owner = thread_id

    def _finish_operation(self) -> None:
        """Release the innermost admitted operation, preserving any enclosing owner.

        Contract:
            Called by the admitted request's finally block. Cleanup cannot remove
            the stack while it is active. Emptying it makes the host available
            to another operation without changing application lifecycle state.
        """
        with Spectrum._lock:
            self._operations.pop()
            if not self._operations:
                self._operation_owner = None

    def _invoke_callback(self, callback: Callable[[], object], label: str) -> None:
        """Run a selected callback outside the registry lock and enforce completion.

        Args:
            callback: A synchronous closure over the borrowed callback and arguments.
            label: Diagnostic identity of the recipe or control.

        Raises:
            TypeError: Result is not None. Returned coroutine/generator objects
                are closed before rejection to avoid abandoning deferred work.
            Exception: Application failures propagate without translation.

        Contract:
            This helper does not schedule, retry or roll back user work.
        """
        result = callback()
        if result is None:
            return
        if inspect.iscoroutine(result):
            result.close()
        elif inspect.isgenerator(result):
            result.close()
        raise TypeError(
            f"{label} must complete synchronously and return None; "
            f"received {type(result).__name__}."
        )

    @staticmethod
    def _validate_bootstrap_name(name: str) -> None:
        """Validate an external lookup name without normalizing its identity.

        Raises:
            TypeError: name is not str.
            ValueError: name is blank.
        """
        SpectrumBootstrap._validate_name(name, "Bootstrap name")

    @staticmethod
    def _validate_callback(callback: object, label: str) -> None:
        """Refuse declared deferred execution before callback registration.

        Raises:
            TypeError: Value is not callable or is a coroutine/generator function.

        Contract:
            Runtime result validation also detects synchronous wrappers that
            return deferred objects. This check does not invoke application code.
        """
        if not callable(callback):
            raise TypeError(f"{label} must be callable.")
        if (inspect.iscoroutinefunction(callback) or inspect.isasyncgenfunction(callback)
                or inspect.isgeneratorfunction(callback)):
            raise TypeError(f"{label} must be synchronous and return None, not deferred execution.")

    def _require_idle_operations(self, requested: str) -> None:
        """Refuse an operation that would overlap already admitted host work.

        Args:
            requested: Diagnostic name of the refused request.

        Raises:
            RuntimeError: The operation stack is nonempty.

        Contract:
            Caller holds Spectrum._lock and has checked host liveness.
        """
        if self._operations:
            raise RuntimeError(
                f"Cannot {requested} while Spectrum operation {self._operations[-1]!r} is active; "
                "wait for it to finish before retrying."
            )

    def configure(self, config: Optional[SpectrumConfig] = None) -> None:
        """
        Assemble the framework once within Spectrum's already initialized Melder environment.

        Args:
            config: Ordinary framework settings, adopted for this attempt. None
                creates defaults. Supply native settings to the first constructor.

        Framework preparation (under self._lock):
          1) Prepare and store a finalized SpectrumConfig.
          2) Register actual Spectrum/Iris/Interchange settings as named unique inputs.
          3) Build Iris and the host logger, then declare native managers, access services,
             CommandCenter and the remaining command-center/foundation definitions.
          4) Resolve resources, builders and access services, retaining each result for
             explicit cleanup. Service constructors inspect no host readiness flags.
          5) Mark the framework assembled and execute system CONFIGURE recipes outside
             the registry lock; additional targets conjure after their final contributor.
          6) Expose completed configuration after all system recipes succeed.

        System recipes can use factories and the finalized configuration on the
        configuring thread. is_configured remains False until those recipes finish;
        other threads cannot use Spectrum's factories during this incomplete phase.
        User recipes and application controls do not execute here.

        Failure atomicity:
            If ANY step raises, the partially built state is unwound by
            _rollback_configure() (best-effort, reverse construction order) and
            the original exception is re-raised unchanged. After a failed
            configure(): self._configured is False (a corrected retry does not
            hit the "already been configured" guard), no access service remains available,
            and constructed framework resources are retired before retry.
            The constructor's native configuration and targets survive rollback.
            Completed manager, command_center definition and Iris class bindings survive;
            their creations are purged after explicit consumer cleanup. An incomplete
            definition batch is removed. Supplied-instance registrations are removed
            so the next attempt can publish its replacements. If retirement fails, retry
            is refused; clean the host before reconstructing.

        Raises:
            RuntimeError: If Spectrum has already been configured.
            Exception: Whatever the failing configuration step raised, re-raised
                unchanged after the rollback completes.
        """
        self.check_cleaned()
        with Spectrum._lock:
            if self._configuring:
                self._require_idle_operations("configure")
            if self._configured:
                raise RuntimeError("Spectrum has already been configured.")
            if self._configure_retry_blocked:
                raise RuntimeError(
                    "The previous framework rollback failed. Clean this Spectrum and create a new host "
                    "before configuring again; native registrations may remain from that attempt."
                )
            self._begin_operation("configure", allow_nested=True)
            self._configuring = True
        try:
            with Spectrum._lock:
                cfg = self._prepare_config(config)
                # Settings are fixed before native construction receives their actual instances.
                self._environment = cfg.environment

                self._melder_runtime.register_configuration(cfg)
                self._init_iris_and_logger(cfg)
                self._melder_runtime.register_managers()
                self._melder_runtime.register_definitions()

                self._init_resources()
                self._init_builders()
                self._init_services()
                self._configured = True
            self.run_system_bootstraps(SpectrumBootstrap.CONFIGURE)
        except BaseException as error:
            # Failed or interrupted setup must not expose a half-built host.
            with Spectrum._lock:
                configuration_error = self._rollback_configure()
            if configuration_error is not None:
                error.add_note(f"Configuration cleanup also failed: {configuration_error}")
            raise
        finally:
            with Spectrum._lock:
                self._configuring = False
                self._finish_operation()


    def _rollback_configure(self) -> Optional[Exception]:
        """
        Best-effort unwind of a partially completed configure() (runs under
        self._lock, invoked only from configure()'s failure path).

        Unwinds in reverse construction order, so each teardown step only touches
         the state built before the failure point:
          0) CommandCenters created by a system configure recipe are cleaned before
             the framework dependencies they borrowed are unpublished.
          1) Completed native access services
             (Resources/Builders/Utilities/ContextConfig)
             via _cleanup_services(), then their references are dropped.
          2) Directly owned parts (resources + builders) via
             _cleanup_components(), then their references are dropped.
          3) Native framework creations, followed by Iris and remaining local loggers.
             Keep completed class bindings and the Iris recipe/context for retry;
             remove registrations that contain this attempt's supplied instances.
          4) Adopted configuration cleanup, then markers (_cfg/_environment) and finally
             self._configured = False so a corrected retry can run.

        Error policy:
            This is the sanctioned best-effort broad-except zone: each phase is
            individually guarded so one failing teardown cannot abort the rest
            of the unwind, and the ORIGINAL configure() exception (re-raised by
            the caller) remains the surfaced failure. Native target/configuration
            lifetime continues. Return collected retirement failures for annotation;
            such a failure blocks configure retry until terminal host cleanup.
        """
        # 0) System configure recipes may have constructed centers before failing.
        self._cleanup_command_centers()
        errors: list[Exception] = []
        # 1) Retire completed access services before their borrowed managers.
        self._cleanup_services()
        self.builders = None
        self.resources = None
        self.utilities = None
        self.context_config = None

        # 2) Tear down directly owned components (per-item guarded inside).
        self._cleanup_components()
        registration_error = self._remove_framework_bindings()
        if registration_error is not None:
            errors.append(registration_error)
        self.interchange = None
        self.toolbox = None
        self.actions = None
        self.agent_builder = None
        self.activity_builder = None
        self.mission_builder = None
        self.agent_pool_builder = None
        self.spectre_builder = None
        self.strategic_command = None

        # 3) Retire Iris's owned native construction after all framework consumers.
        iris_error = self._cleanup_iris_bootstrap(preserve_bindings=True)
        if iris_error is not None:
            errors.append(iris_error)
        configuration_error = self._cleanup_configuration()
        if configuration_error is not None:
            errors.append(configuration_error)
        input_error = self._remove_configuration_bindings()
        if input_error is not None:
            errors.append(input_error)
        self._iris = None
        self._logger = None

        # 4) Dispose adopted configuration, then reset markers for a fresh retry.
        self._cfg = None
        self._environment = None
        self._configured = False
        self._configure_retry_blocked = bool(errors)
        if errors:
            return ExceptionGroup("Spectrum framework rollback failed.", errors)
        return None



    def _prepare_config(self, config: Optional[SpectrumConfig]) -> SpectrumConfig:
        """
        Build and finalize the SpectrumConfig used to wire Spectrum.

        Returns:
            SpectrumConfig: The finalized configuration object (stored on self._cfg).

        Invariants:
            - The returned config has passed ensure_fully_configured().
            - self._cfg is set for subsequent helpers to consult.
        """
        cfg = config if config is not None else SpectrumConfig()
        self._cfg = cfg
        cfg.ensure_fully_configured()
        return cfg


    def _init_iris_and_logger(self, cfg: SpectrumConfig) -> None:
        """
        Build Iris in the initialized native target, then obtain Spectrum's primary logger.

        Args:
            cfg: Finalized SpectrumConfig.

        Side effects:
            - The host retains its bootstrap/context before the first build so partial
              work stays owned. Retry reuses their class bindings with the new config.
              The context lends the existing default root.
            - self._iris borrows the native-created result configured by cfg.iris_config.
            - self._logger is registered via self._create_spectrum_logger().

        Raises:
            Exception: Native binding, validation, Iris assembly or enrollment fails.
                configure owns rollback; this method does not replace native targets.
        """
        from melder_ops.command_center.spectrum.bootstraps.iris_bootstrap import IrisBootstrap

        cfg.iris_config.check_configuration()
        if self._iris_bootstrap is None:
            frame_name, book_name = self._melder_configuration.resolve_target()
            self._iris_bootstrap_context = MelderOpsBootstrapContext(
                self._melder_runtime.get_spellbook(book_name, frame_name=frame_name),
                frame_name=frame_name,
                root_name=self._melder_runtime.get_conduit(book_name, frame_name=frame_name).name,
            )
            self._iris_bootstrap = IrisBootstrap(self._iris_bootstrap_context, cfg.iris_config)
        self._iris_bootstrap.build(configuration=cfg.iris_config)
        self._iris = self._iris_bootstrap.iris
        self._create_spectrum_logger()


    def _create_spectrum_logger(self) -> None:
        """
        Internal helper to register Spectrum itself with Iris and get its primary logger.
        """
        if not self._iris:
            raise RuntimeError("Iris is not initialized; cannot create Spectrum logger.")
        self._logger = self._iris.register(
            self,
            channels="system",
            groups=["lifecycle", "configuration", "singleton"],
            system_groups=["spectrum"]
        )

    def create_command_center(self, name: str, config: Optional[CommandCenterConfig] = None) -> CommandCenter:
        """
        Meld a CommandCenter in a new scope using the framework inputs prepared by configure().

        Args:
            name: Unique name for the CommandCenter.
            config: Optional CommandCenterConfig. If None, SpectrumConfig constructs
                a fresh configuration from its center template or ordinary defaults.
                An explicit configuration takes precedence and keeps its identity.

        Returns:
            CommandCenter: The constructed center, published only after its active
            system COMMAND_CENTER recipes complete. Its conduit is a fresh lesser
            scope from the host's configured default root. User recipes are not executed.

        Raises:
            RuntimeError: If Spectrum is not configured.
            ValueError: If a CommandCenter with the given name already exists.
            RuntimeError: If a required native access service is unavailable.
            RuntimeError: Another thread owns a host operation, or a center hook
                recursively requests another center before its current build ends.
            KeyError: The native target cannot resolve the command_center definition
                that configure declares through MelderRuntime.register_managers.
            Exception: Native construction or a system recipe fails. Hook failure cleans
                the unpublished center and preserves the original exception.

        Concurrency:
            Construct under the existing registry lock; execute system recipes
            outside it against the borrowed, unpublished center. The operation
            guard prevents competing construction while those recipes run.

        Scope ownership:
            Allocate after name validation and pass the scope through meld overrides.
            The scope is named "<root name>/center/<name>", the framework root's own
            name (self.get_conduit().name, "melderops" by default) as the prefix
            (owner decision 2026-09-27, convention A): a borrower with the center's
            frame_name and that name reaches the live scope through
            Aether().get_conduit_by_name(name, frame_name); the center itself keeps
            its reference. A name Melder finds already held in the frame is refused
            by create_lesser_conduit as Melder raises it (ValueError), before any
            meld; no pre-check and no retry.
            The returned center owns scope cleanup along with its explicit child
            cleanup, which releases the name. Spectrum releases the scope if
            construction fails; after a successful constructor, rollback delegates
            only to center.cleanup().
            Melder constructs the center; its existing child factories remain unchanged.
            The positional name is MelderRuntime.COMMAND_CENTER_SPELLFRAME: configure
            declares CommandCenter there with the default binding, so the two spellings
            must stay equal. Every constructor input arrives through the override,
            including this host's adopted MelderConfiguration: the center borrows it
            (exposed as melder_configuration and frame_name) and never cleans it.
        """
        self._check_configured()
        with Spectrum._lock:
            self._begin_operation("create_command_center", allow_nested=True)
        new_cc: Optional[CommandCenter] = None
        conduit: Optional[Conduit] = None
        try:
            with Spectrum._lock:
                if name in self._command_centers:
                    if self._logger is not None:
                        self._logger.error(
                            f"Command Center '{name}' already exists.",
                            _manual_stack=True, _method_name="create_command_center"
                        )
                    raise ValueError(f"A CommandCenter named '{name}' already exists.")

                # Allocate the center's asset scope, named by convention A, before passing it to
                # the constructor. The prefix is the framework root's own name.
                root = self.get_conduit()
                conduit = root.create_lesser_conduit(name=f"{root.name}/center/{name}")
                # Meld the center with existing host inputs and the scope that will own its assets.
                new_cc = conduit.meld("command_center", override={"name":name,
                            "context_config":self.context_config,
                            "config":(config if config is not None else self._cfg.create_command_center_config()),
                            "builders":self.builders,
                            "resources":self.resources,
                            "utilities":self.utilities,
                            "conduit":conduit,
                            "spectrum":self,
                            "melder_configuration":self._melder_configuration,})
            self.run_system_bootstraps(SpectrumBootstrap.COMMAND_CENTER, new_cc)
            # Hooks borrow the target; never publish one they improperly retired.
            new_cc.check_cleaned()
            with Spectrum._lock:
                # Publish by name and id only after all center construction hooks succeed.
                self._command_centers[name] = new_cc
                self._all_command_centers[new_cc.id] = new_cc
            return new_cc
        except BaseException as error:
            if new_cc is not None:
                try:
                    new_cc.cleanup()
                except Exception as cleanup_error:
                    # Best-effort rollback retains the hook failure as the primary error.
                    error.add_note(f"Unpublished center cleanup also failed: {cleanup_error}")
            elif conduit is not None:
                try:
                    conduit.cleanup()
                except Exception as cleanup_error:
                    error.add_note(f"Untransferred center scope cleanup also failed: {cleanup_error}")
            raise
        finally:
            self._finish_operation()


    def unregister_command_center(self, command_center: CommandCenter) -> None:
        """Remove a retiring center from this host's name and ID indexes.

        CommandCenter.cleanup calls this after releasing its own lock. Only
        entries referring to that exact instance are removed, so repeated calls,
        unpublished centers and callbacks from old same-name centers are harmless.
        This removes registration only; it never calls center or scope cleanup.

        Args:
            command_center: Retiring center whose identity remains available.

        Lifecycle and threading:
            Uses Spectrum's existing registry lock. This callback is valid during
            host shutdown, when Spectrum is already marked cleaned but its center
            indexes remain alive until every owned center finishes cleanup.
        """
        with Spectrum._lock:
            if self._command_centers.get(command_center.name) is command_center:
                del self._command_centers[command_center.name]
            if self._all_command_centers.get(command_center.id) is command_center:
                del self._all_command_centers[command_center.id]

    def get_command_center_by_name(self, name: str) -> Optional[CommandCenter]:
        """
        Retrieves a CommandCenter by its human-readable name.

        Args:
            name (str): The name of the CommandCenter to find.

        Returns:
            Optional[CommandCenter]: The CommandCenter instance if found, otherwise None.

        Raises:
            RuntimeError: If Spectrum has not been configured.
        """
        self._check_configured()
        return self._command_centers.get(name)

    def get_command_center_by_id(self, cc_id: str) -> Optional[CommandCenter]:
        """
        Retrieves a CommandCenter from the global directory by its unique, machine-readable ID.

        Args:
            cc_id (str): The unique ULID of the CommandCenter to find.

        Returns:
            Optional[CommandCenter]: The CommandCenter instance if found, otherwise None.

        Raises:
            RuntimeError: If Spectrum has not been configured.
        """
        self._check_configured()
        return self._all_command_centers.get(cc_id)

    def _check_configured(self) -> SpectrumConfig:
        """
        Enforce live framework access and configuration-hook thread ownership.

        Raises:
            RuntimeError: Spectrum is cleaned, unconfigured, or another thread
                is still completing its system configure recipes.

        Returns:
            The adopted configuration once this caller may use the framework.
        """
        self.check_cleaned()
        with Spectrum._lock:
            if self._configuring and self._operation_owner != threading.get_ident():
                raise RuntimeError("Spectrum is still completing system configure bootstraps on another thread.")
            if not self._configured or self._cfg is None:
                if self._logger is not None:
                    self._logger.error("Spectrum must be configured with .configure() before use.",
                                       _manual_stack=True, _method_name="_check_configured")
                raise RuntimeError("Spectrum must be configured with .configure() before use.")
            return self._cfg

    def is_configured(self) -> bool:
        """
        Report whether framework configuration and its system recipes have completed.

        Returns:
            bool: True after successful configure completion, False during its
                recipes, before configuration, or after cleanup.
        """
        with Spectrum._lock:
            return not self._cleaned and self._configured and not self._configuring

#region Spectrum Resources Initialization
    def _init_resources(self) -> None:
        """
        Resolve shared resources from their native class-name bindings.

        Creates:
            - self.interchange
            - self.toolbox
            - self.actions

        Notes:
            Each manager generates its ID and enrolls its native-injected logger.
            Interchange receives the actual prepared configuration registered before Iris setup.
            Toolbox borrows this root through override for late tool-class registration.
            All three are addressed at the spectrum label (CommandCenterDefinitions.SPECTRUM)
            with their class names, whatever the configured root is called.
            All definitions are validated before resolution. Native errors propagate to configure
            rollback; each successfully returned object is retained immediately for explicit cleanup.
        """
        conduit = self.get_conduit()
        self.interchange = conduit.meld(
            spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="Interchange",
        )
        self.toolbox = conduit.meld(
            spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="Toolbox",
            override={"root_conduit": conduit},
        )
        self.actions = conduit.meld(spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="Actions")


#endregion Spectrum Resources Initialization

#region Spectrum Builders Initialization
    def _init_builders(self) -> None:
        """
        Resolve shared builders through their named native class bindings.

        Creates:
            - self.agent_builder
            - self.activity_builder
            - self.mission_builder
            - self.agent_pool_builder
            - self.spectre_builder (bound to this Spectrum)
            - self.strategic_command

        Each migrated definition is unique in the native root and is addressed by its
        area label from CommandCenterDefinitions with its class name: AgentBuilder and
        Spectre at agents, ActivityBuilder at activity, MissionBuilder at mission,
        AgentPoolBuilder at agent_pools and StrategicCommand at strategic_command.
        Melder supplies its dedicated logger; its constructor generates identity and
        enrolls that logger. Store each result immediately so configure rollback retains
        explicit cleanup. These facades keep their current domain registries and
        dispensing behavior. Spectre borrows this existing host supplied through override
        and generates its own identity. The agent, activity, mission and pool builders and
        StrategicCommand borrow this root, supplied through override as root_conduit: they
        bind classes registered after configure into it and meld through the caller's scope.
        """
        conduit = self.get_conduit()
        self.agent_builder = conduit.meld(
            spellframe=CommandCenterDefinitions.AGENTS, binding_name="AgentBuilder",
            override={"root_conduit": conduit},
        )
        self.activity_builder = conduit.meld(
            spellframe=CommandCenterDefinitions.ACTIVITY, binding_name="ActivityBuilder",
            override={"root_conduit": conduit},
        )
        self.mission_builder = conduit.meld(
            spellframe=CommandCenterDefinitions.MISSION, binding_name="MissionBuilder",
            override={"root_conduit": conduit},
        )
        self.agent_pool_builder = conduit.meld(
            spellframe=CommandCenterDefinitions.AGENT_POOLS, binding_name="AgentPoolBuilder",
            override={"root_conduit": conduit},
        )
        self.spectre_builder = conduit.meld(
            spellframe=CommandCenterDefinitions.AGENTS, binding_name="Spectre",
            override={"spectrum_instance": self},
        )
        self.strategic_command = conduit.meld(
            spellframe=CommandCenterDefinitions.STRATEGIC_COMMAND, binding_name="StrategicCommand",
            override={"root_conduit": conduit},
        )


#endregion Spectrum Builders Initialization

#region Native Framework Access
    def _init_services(self) -> None:
        """Resolve and retain the four access services from their unique native definitions.

        Constructors receive explicit configuration, Iris, registry and manager
        dependencies from Melder. Each completed result is retained immediately
        so Spectrum can clean it if a later construction fails. No class lock,
        singleton marker or live-instance registration is installed here.

        The containing configure operation serializes construction. Convenience
        access is unavailable until each result has returned and been retained.
        """
        conduit = self.get_conduit()
        try:
            self.context_config = conduit.meld(
                spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="SpectrumContextConfig",
                override={"configuration": self._cfg},
            )
            self.utilities = conduit.meld(
                spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="SpectrumUtilities",
            )
            self.builders = conduit.meld(
                spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="SpectrumBuilders",
            )
            self.resources = conduit.meld(
                spellframe=CommandCenterDefinitions.SPECTRUM, binding_name="SpectrumResources",
            )
        except MeldExecutionError as error:
            # Keep the constructors' original failures as the configure contract promises.
            if error.inner is None:
                raise
            raise error.inner from error

#endregion Native Framework Access
#endregion Spectrum
