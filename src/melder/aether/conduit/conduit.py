import threading
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional, Type, Any, Tuple

# Melder Imports
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import IConduit, ISpellbook, IConduitCloud, ISpell, IConfiguration, \
    ISafeLogger
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aether import Aether
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

#TODO: @GPT5, please inform Mark that he needs to implement Conduits hooks, for pre- during, and post activations so we can add Aspect Oriented Programming here

#region Conduit
class Conduit(Cleanable):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """
    _aether = Aether()
    __melder_internal__ = _mrg.sentinel
    def __init__(self, spellbook: ISpellbook, configuration: IConfiguration, conduit_state: ConduitState,
                 aetheric_frame: str, policy: Policies, automatic: bool = True, name: Optional[str] = None, logger: Any | None = None):
        """
        Public API

        Initializes a new Conduit.

        Args:
            spellbook (ISpellbook): The Spellbook governing this Conduit.
            configuration (IConfiguration): The locked system configuration.
            conduit_state (str): The role of this Conduit ('normal' or 'lesser').
            name (str, optional): An optional name for easier identification.
        """
        super().__init__()
        # General Init
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._name: str = name
        self.__debugger_mode__: bool = False
        self.__dynamic_environment__: bool = False
        self._automatic: bool = automatic
        self._aetheric_frame: str = aetheric_frame
        # Special Configuration
        if not isinstance(configuration, IConfiguration):
            raise TypeError(f"Expected IConfiguration instance, got {type(configuration).__name__}")

        self._configuration: IConfiguration = configuration
        self._logger: ISafeLogger = self._configure_logger(logger, configuration)
        # Now that configuration/logger are set, apply flags.
        self._apply_configuration_flags()
        # Override dynamic environment if caller requested automatic/dynamic explicitly.
        if automatic is not None:
            self.__dynamic_environment__ = not automatic
        self._logger.debug(
            f"Conduit __init__ starting (frame='{aetheric_frame}', state={conduit_state.name}, name={name})",
            "__init__"
        )

        self._conduit_state: ConduitState = conduit_state  # can be normal, lesser
        self._creations: Creations | LesserCreations = self._creations_configuration(configuration)
        self._spellbook: ISpellbook = spellbook
        self._meld: Meld = Meld(creations=self._creations, spellbook=self._spellbook)
        self._spellspace_stack: ContextVar[list[SpellSpace]] = ContextVar(
            f"_spellspace_stack_{self._id}", default=[]
        )

        # Localized hook map for this conduit.
        # Populated from Configuration using the Spellbook's ID.
        # Shape: { hook_name: [callables...] }
        self._conduit_hooks: dict[str, list[Any]] | None = None

        self._configure_conduit_state()

        # ID swap: pull any hooks registered under this Spellbook's ID in the
        # Configuration into this Conduit instance as a local hook map.
        self._initialize_conduit_hooks()

        self._conduit_ward: ConduitWard = ConduitWard(
            conduit=self,
            dynamic=self.__dynamic_environment__,
            conduit_type=self._conduit_state,
            policy=policy
        )

        self._logger.debug(
            f"Conduit initialized (id={self._id}, frame='{self._aetheric_frame}')",
            "__init__"
        )

    # ------------------------------------------------------------------ #
    # SpellSpace support
    # ------------------------------------------------------------------ #

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """
        Return the currently active SpellSpace for this Conduit, if any.

        Returns:
            SpellSpace | None: The top-of-stack SpellSpace, or None if no spellspace is active.
        """
        stack = self._spellspace_stack.get()
        if not stack:
            return None
        return stack[-1]

    def create_spellspace(self) -> SpellSpace:
        """
        Create a SpellSpace bound to this Conduit.

        Lifecycle is manual unless used via `enter_spellspace`.

        Returns:
            SpellSpace: A new SpellSpace owned by this Conduit.
        """
        return SpellSpace(self)

    @contextmanager
    def enter_spellspace(self) -> SpellSpace:
        """
        Context-managed SpellSpace. Pushes onto the stack, yields it, and cleans it on exit.

        Usage:
            with conduit.enter_spellspace() as space:
                space.meld(...)

        Ensures:
            - SpellSpace is activated before use (top of stack).
            - SpellSpace is cleaned on exit, even on exceptions.
            - Stack integrity is validated to detect misuse.

        Returns:
            SpellSpace: The newly created, active spellspace for the duration of the context.

        Raises:
            SpellSpaceScopeError: If stack integrity is violated on exit.
        """
        space = self.create_spellspace()
        stack = list(self._spellspace_stack.get())
        stack.append(space)
        self._spellspace_stack.set(stack)
        try:
            yield space
        finally:
            stack = list(self._spellspace_stack.get())
            if not stack or stack[-1] is not space:
                raise SpellSpaceScopeError(
                    "SpellSpace stack corruption detected while exiting."
                )
            stack.pop()
            self._spellspace_stack.set(stack)
            space.cleanup()



    def _configure_logger(self, logger: Any, configuration: IConfiguration) -> Any:
        """
        Internal

        Configures the logger for this Conduit.

        Args:
            logger (Any): The logger instance or configuration.
        Returns:
            SafeLogger: The configured SafeLogger instance.
        """
        if logger is not None:
            return InitHelpers.resolve_safe_logger(logger)
        else:
            return self._resolve_logger_from_config(configuration)

    def _configure_conduit_state(self):
        """
        Internal

        Configures the conduit state based on the provided configuration.

        Raises:
            RuntimeError: If normal conduit registration fails.
        """
        if self._conduit_state == ConduitState.normal:
            try:
                self._logger.debug("Registering normal conduit into Aether", "__init__")
                self._add_conduit_to_aether()
                self._add_spells_to_aether()
                if self.__dynamic_environment__ and self._name is not None:
                    self._logger.debug(f"Registering conduit in cloud as '{self._name}'", "__init__")
                    Conduit._aether._register_conduit_cloud(self, self._aetheric_frame)
            except Exception as e:
                self._logger.error(f"Normal conduit registration failed: {e}", "__init__", exc_info=True)
                raise
        elif self._conduit_state == ConduitState.lesser:
            if self._name is not None:
                self._logger.warning("Lesser conduits cannot have a name. Overriding to None.", "__init__")
                self._name = None

    def _register_to_creations(self, spell: ISpell, instance: Any) -> None:
        """
        Internal

        Eagerly register an **existing-object** spell as a unique creation
        in this Conduit's Creations manager.

        Semantics
        ---------
        - This helper is intended for spells that were bound with an already-
          constructed instance (existing-object spells).
        - These spells are treated as **singletons** for this Conduit and
          must use `Existence.unique`.
        - The instance is registered under `spell.spell_id` via
          `Creations.add_unique(...)`.

        This is primarily used during the conjure flow when a Conduit is
        first wired into its Spellbook and needs to prime its Creations
        store with pre-existing objects.
        """
        if not isinstance(self._creations, Creations):
            self._logger.error(
                "_register_to_creations called on non-normal creations",
                "_register_to_creations",
            )
            raise RuntimeError(
                "_register_to_creations can only be called on normal Creations instances."
            )

        creations: Creations = self._creations

        # Existing-object spells are semantically singletons in Melder.
        existence: Existence = spell.existence
        if existence is not Existence.unique:
            self._logger.error(
                f"_register_to_creations: existing-object spell {spell.spell_id} "
                f"has unsupported existence={existence}; expected Existence.unique.",
                "_register_to_creations",
            )
            raise RuntimeError(
                "Existing-object spells must use Existence.unique when "
                "registered into Creations."
            )

        spell_id: str = spell.spell_id
        creations.add_unique(spell_id, instance)



    def _initialize_conduit_hooks(self) -> None:
        """
        Internal

        Attach any configured system hooks that were registered under this
        Conduit's Spellbook into the Conduit instance.

        This is the "ID swap" boundary:

            - Registration happens per-Spellbook ID on `Configuration` via:

                  configuration.add_hook(spellbook_id, hook_name, hook)

            - At Conduit construction time, we look up that Spellbook ID
              and pull the hook map into a Conduit-local structure:

                  self._conduit_hooks: { hook_name: [callables...] }

        Rules:
            - Only NORMAL conduits participate; lesser conduits skip this.
            - If the Spellbook has no `id`, we log and bail.
            - If the Configuration does not expose `get_hooks(spellbook_id)`,
              we treat that as "no hooks registered" and bail quietly.
        """
        # Lesser conduits do not own their own hook sets.
        if self._conduit_state != ConduitState.normal:
            self._logger.debug(
                "_initialize_conduit_hooks: skipping for non-normal conduit",
                "_initialize_conduit_hooks",
            )
            return

        # Spellbook must expose an `id` (ISpellbook contract).
        try:
            spellbook_id = self._spellbook._id
        except AttributeError:
            self._logger.debug(
                "_initialize_conduit_hooks: Spellbook has no 'id' attribute; "
                "skipping hook attachment.",
                "_initialize_conduit_hooks",
            )
            return

        # Configuration may or may not support the hook registry yet.
        try:
            hook_map = self._configuration.get_hooks(spellbook_id)
        except AttributeError:
            self._logger.debug(
                "_initialize_conduit_hooks: Configuration has no get_hooks(spellbook_id); "
                "skipping hook attachment.",
                "_initialize_conduit_hooks",
            )
            return

        if not hook_map:
            self._logger.debug(
                f"_initialize_conduit_hooks: no hooks registered for spellbook_id={spellbook_id}; "
                "nothing to attach.",
                "_initialize_conduit_hooks",
            )
            return

        # At this point we conceptually "swap IDs": hooks registered under the
        # Spellbook's ID become owned by this Conduit instance.
        self._conduit_hooks = hook_map
        try:
            if self._meld is not None:
                self._meld.set_meld_hooks(self._conduit_hooks)
        except Exception:
            pass

        self._logger.debug(
            f"_initialize_conduit_hooks: attached {len(hook_map)} hook groups "
            f"from spellbook_id={spellbook_id} to conduit_id={self._id}",
            "_initialize_conduit_hooks",
        )



    #region Cleanup and Disposal
    def cleanup(self):
        """
        Public API

        Idempotently clean this Conduit, severing links, tearing down local
        runtime, and (for normal conduits) unregistering from Aether. This is
        local teardown only; it never cleans AethericFrame or Aether.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._logger.debug("cleanup start", "cleanup")
            self._fire_conduit_hooks("on_conduit_cleanup_start", self)
            self._cleaned = True
            # drop any active spellspace stack
            self._spellspace_stack.set([])
            if self._conduit_state == ConduitState.lesser:
                self._cleanup_lesser_conduit()
            elif self._conduit_state == ConduitState.normal:
                self._cleanup_normal_conduit()
            else:
                self._logger.error("Unknown Conduit state during cleanup", "cleanup")
                raise RuntimeError("Conduit state is unknown during cleanup")
            self._fire_conduit_hooks("on_conduit_cleanup_complete", self)

        # Logger last
        if self._logger is not None:
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            self._logger = None

        # Release lock reference after teardown
        self._lock = None


    def _cleanup_lesser_conduit(self):
        """
        Internal

        Cleans up a lesser Conduit.
        """
        # Lesser conduits share the parent Spellbook and are not root-registered
        # in Aether. We tear down local runtime and lineage links, but do not
        # touch the shared Spellbook/Aether registries.
        try:
            if self._meld is not None:
                self._meld.cleanup()
        except Exception:
            self._logger.error("Error cleaning meld", "_cleanup_lesser_conduit", exc_info=True)

        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_lesser_conduit", exc_info=True)

        self._cleanup_spellspaces()

        try:
            if self._creations is not None:
                self._creations.cleanup()
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_lesser_conduit", exc_info=True)

        if self._conduit_hooks is not None:
            self._conduit_hooks.clear()
        # Null internal references
        self._conduit_hooks = None
        self._conduit_ward = None
        self._meld = None
        self._creations = None
        self._spellspace_stack = None
        self._spellbook = None
        self._configuration = None


    def _cleanup_normal_conduit(self):
        """
        Internal

        Cleans up a normal Conduit.
        """
        # 1) Meld runtime (stop new object creation paths)
        try:
            if self._meld is not None:
                self._meld.cleanup()
        except Exception:
            self._logger.error("Error cleaning meld", "_cleanup_normal_conduit", exc_info=True)

        # 2) Ward (contracts + lesser lineage)
        try:
            if self._conduit_ward is not None:
                self._conduit_ward.cleanup()
        except Exception:
            self._logger.error("Error cleaning conduit ward", "_cleanup_normal_conduit", exc_info=True)

        # 2.5) Spellspaces (ensure stack is flushed)
        self._cleanup_spellspaces()

        # 3) Creations
        try:
            if self._creations is not None:
                self._creations.cleanup()
        except Exception:
            self._logger.error("Error cleaning creations", "_cleanup_normal_conduit", exc_info=True)

        # 4) Unregister from Aether (spells + root conduit + cloud)
        try:
            spell_indices = list(self._spellbook._spells.keys()) if self._spellbook is not None else []
            if spell_indices:
                Conduit._aether._remove_spells_from_aether(self._id, set(spell_indices), self._aetheric_frame)
            Conduit._aether._remove_conduit(self, self._aetheric_frame)
            if self.__dynamic_environment__ and self._name is not None:
                Conduit._aether._unregister_conduit_cloud(self, self._aetheric_frame)
        except Exception as e:
            self._logger.error(f"Error unregistering from Aether: {e}", "_cleanup_normal_conduit", exc_info=True)

        # 5) Spellbook (owned by normal conduits)
        try:
            if self._spellbook is not None:
                self._spellbook.cleanup()
        except Exception:
            self._logger.error("Error cleaning spellbook", "_cleanup_normal_conduit", exc_info=True)

        # 6) Null internal references
        self._conduit_ward = None
        self._meld = None
        self._creations = None
        if self._conduit_hooks is not None:
            self._conduit_hooks.clear()
        self._spellbook = None
        self._configuration = None
        self._conduit_hooks = None
        self._spellspace_stack = None
        self._aetheric_frame = None

    def _cleanup_spellspaces(self) -> None:
        """
        Internal

        Best-effort cleanup of any spellspaces still on the stack.
        """
        if self._spellspace_stack is None:
            return
        try:
            stack = list(self._spellspace_stack.get())
            for space in stack:
                try:
                    space.cleanup()
                except Exception:
                    self._logger.error("Error cleaning spellspace", "_cleanup_spellspaces", exc_info=True)
            self._spellspace_stack.set([])
        except Exception:
            self._logger.error("Error flushing spellspace stack", "_cleanup_spellspaces", exc_info=True)


    #endregion Cleanup and Disposal
    #region Context Management
    def __enter__(self):
        """
        Public API

        Enters the context of this Conduit.

        Returns:
            Conduit: The current Conduit instance.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Public API

        Exits the context of this Conduit.

        Args:
            exc_type: The exception type, if any.
            exc_value: The exception value, if any.
            traceback: The traceback object, if any.
        """
        self._lock.release()

    #endregion Context Management
    #region Logger
    def _resolve_logger_from_config(self, configuration: IConfiguration) -> ISafeLogger:
        """
        This internal method resolves the logger for this Conduit based on the provided configuration.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            SafeLogger: The resolved SafeLogger instance.
        """
        if configuration.has_logger_factory():
            return InitHelpers.resolve_safe_logger(configuration.get_logger_for(self))
        return InitHelpers.resolve_safe_logger(None)

    #endregion Logger
    #region Utilities
    def __repr__(self):
        """
        Public API

        Returns a string representation of the Conduit instance.
        :return:
        """
        return (
            f"<Conduit name={self.name} "
            f"id={self._id}>"
        )

    #endregion Utilities

    #region Properties
    @property
    def id(self):
        """
        Public API

        Returns the unique identifier of this Conduit.
        """
        return self._id

    @property
    def name(self) -> Optional[str]:
        """
        Public API

        Returns the name of this Conduit. Name must be created during conduit creation.
        """
        return self._name if self._name else None


    @name.setter
    def name(self, name: str) -> None:
        """
        Public API

        Allows user to name conduit if available

        Raises:
            RuntimeError: If the Conduit name is already set.
        """
        if self._name is not None:
            self._logger.error("Attempt to rename conduit after name set", "name")
            raise RuntimeError("Conduit name is set.")
        self._logger.debug(f"Conduit named '{name}'", "name")
        self._name = name

    #endregion



    #region Conduit Configuration
    def register_conduit_cloud(self, conduit: IConduit):
        """
        Public API

        Registers a conduit in the dynamic mode registry. You can use this method if you forgot to name your conduit in order
        to name it afterward and register it. You can only register it once.

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the conduit is a lesser conduit.
            RuntimeError: If the Conduit name is not set.
        """
        if self.__dynamic_environment__ == False:
            self._logger.error("register_conduit_cloud in non-dynamic env", "register_conduit_cloud")
            raise RuntimeError("Dynamic environment is not enabled. Cannot register in the conduit cloud.")
        if self._conduit_state == ConduitState.lesser:
            self._logger.error("register_conduit_cloud called on lesser conduit", "register_conduit_cloud")
            raise RuntimeError("Lesser conduits cannot register in the conduit cloud.")
        if self._name is None:
            self._logger.error("register_conduit_cloud called without conduit name", "register_conduit_cloud")
            raise RuntimeError("Conduit name is not set. Please set a name before registering in the conduit cloud.")
        self._logger.debug(f"Registering '{self._name}' into conduit cloud", "register_conduit_cloud")
        Conduit._aether._register_conduit_cloud(conduit, self._aetheric_frame)

    def unregister_conduit_cloud(self, conduit: IConduit):
        """
        Public API

        Unregisters a conduit from the dynamic mode registry (ConduitCloud).

        Args:
            conduit (IConduit): The conduit instance to unregister.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the conduit is a lesser conduit.
            RuntimeError: If the Conduit name is not set.
        """
        if self.__dynamic_environment__ is False:
            self._logger.error("unregister_conduit_cloud in non-dynamic env", "unregister_conduit_cloud")
            raise RuntimeError("Dynamic environment is not enabled. Cannot unregister from the conduit cloud.")
        if self._conduit_state == ConduitState.lesser:
            self._logger.error("unregister_conduit_cloud called on lesser conduit", "unregister_conduit_cloud")
            raise RuntimeError("Lesser conduits cannot unregister from the conduit cloud.")
        if self._name is None:
            self._logger.error("unregister_conduit_cloud called without conduit name", "unregister_conduit_cloud")
            raise RuntimeError("Conduit name is not set. Please set a name before unregistering from the conduit cloud.")
        self._logger.debug(f"Unregistering '{self._name}' from conduit cloud", "unregister_conduit_cloud")
        Conduit._aether._unregister_conduit_cloud(conduit, self._aetheric_frame)

    def _apply_configuration_flags(self):
        """
        Internal

        Sets the environment mode and debugging mode for this Conduit
        based on the configuration instance passed.
        """
        try:
            state = self._configuration.get_property("system_state")
            self.__dynamic_environment__ = (state == SystemState.dynamic)
            self.__debugger_mode__ = bool(self._configuration.get_property("debugging"))
            self._logger.debug(
                f"_apply_configuration_flags: system_state={state.name}, dynamic={self.__dynamic_environment__}, debugging={self.__debugger_mode__}",
                "_apply_configuration_flags"
            )
        except Exception as e:
            self._logger.error(f"_apply_configuration_flags failed: {e}", "__init__", exc_info=True)
            raise


    def _add_conduit_to_aether(self) -> None:
            """
            Internal

            Adds the newly created Conduit into the shared Aether world.

            Raises:
                RuntimeError: If Aether is not initialized.
            """
            if Conduit._aether is None:
                self._logger.error("Aether is not initialized", "_add_conduit_to_aether")
                raise RuntimeError("Aether is not initialized.")
            self._logger.debug("Adding conduit to Aether", "_add_conduit_to_aether")
            Conduit._aether._add_conduit(self, self._aetheric_frame)

    def _remove_conduit_from_aether(self) -> None:
        """
        Internal

        Removes this Conduit from the shared Aether world.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        if Conduit._aether is None:
            self._logger.error("Aether is not initialized", "_remove_conduit_from_aether")
            raise RuntimeError("Aether is not initialized.")
        self._logger.debug("Removing conduit from Aether", "_remove_conduit_from_aether")
        Conduit._aether._remove_conduit(self, self._aetheric_frame)


    def _creations_configuration(self, configuration: IConfiguration) -> Creations | LesserCreations:
        """
        Internal

        Returns the current creations configuration for this Conduit.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            Creations | LesserCreations: The appropriate creation manager based on conduit state.

        Raises:
            RuntimeError: If the Conduit state is unknown.
        """
        if self._conduit_state == ConduitState.lesser:
            self._logger.debug("Selecting LesserCreations", "_creations_configuration")
            return LesserCreations(
                disposal_enabled=configuration.get_property("disposal"),
                disposal_method_names=configuration.get_property("disposal_method_names"),
                conduit=self,
                parent_creations=getattr(self, "_parent_creations", None),
            )
        if self._conduit_state == ConduitState.normal:
            self._logger.debug("Selecting Creations", "_creations_configuration")
            return Creations(disposal_enabled=configuration.get_property("disposal"),
                             disposal_method_names=configuration.get_property("disposal_method_names"), conduit=self)
        self._logger.error("Unknown Conduit state", "_creations_configuration")
        raise RuntimeError("Conduit state is unknown")

    #endregion Conduit Configuration
    #region Conduit Management
    def _register_conduit_hooks_on_upgrade(
            self,
            hooks: dict[str, Any],
    ) -> None:
        """
        Internal

        Register per-conduit hooks for this upgraded Conduit into both:

            1) The Configuration hook registry, and
            2) This Conduit's local `_conduit_hooks` map,

        so that all downstream subsystems (Meld, ConduitWard, links, contracts,
        cleanup, etc.) see them immediately.

        Shape is identical to the Configuration registry:

            _hooks[owner_id][hook_name] -> list[callables]

        where `owner_id` here is this Conduit's `self._id`.

        Rules:
            - Only allowed when the system is in **dynamic** mode.
            - `hooks` values may be a single callable or an iterable of callables.
            - Hook names must be in Configuration._ALLOWED_HOOKS.
            - We first update Configuration via `add_hooks(...)`; only on success
              do we merge into the local `_conduit_hooks` map.
        """
        # Enforce dynamic environment – this is a dynamic-only feature.
        if not self.__dynamic_environment__:
            self._logger.error(
                "_register_conduit_hooks_on_upgrade in non-dynamic env",
                "_register_conduit_hooks_on_upgrade",
            )
            raise RuntimeError(
                "Dynamic environment is not enabled. Cannot register per-conduit hooks."
            )

        # 1) Push into Configuration using the existing hook API.
        #
        #    Note: While the config docs talk about "spellbook_id", the registry
        #    is just:
        #         ConcurrentDict[str, ConcurrentDict[str, list[Callable]]]
        #    and happily accepts any string key. We treat `self._id` as the
        #    owner ID for this conduit-specific hook set.
        self._configuration.add_hooks(self._id, **hooks)

        # 2) Mirror into this Conduit's local hook map so all future
        #    `_fire_conduit_hooks(...)` calls will see them immediately.
        if self._conduit_hooks is None:
            self._conduit_hooks = {}

        for name, value in hooks.items():
            if value is None:
                continue

            # Single callable
            if callable(value):
                self._conduit_hooks.setdefault(name, []).append(value)
                continue

            # Iterable of callables
            try:
                iterator = iter(value)
            except TypeError:
                raise TypeError(
                    f"Hook value for '{name}' must be a callable or an iterable of callables."
                )

            for fn in iterator:
                if not callable(fn):
                    raise TypeError(
                        f"All entries for hook '{name}' must be callable."
                    )
                self._conduit_hooks.setdefault(name, []).append(fn)

    def upgrade_to_normal(
            self,
            name: Optional[str] = None,
            *,
            hooks: dict[str, Any] | None = None,
    ) -> None:
        """
        Public API

        Upgrades this Conduit from a lesser to a **normal** state.

        This process allows the conduit to create its own links through the Aether system.
        It effectively forks this conduit into a new tree, retaining its children and
        creation data, and establishes new links with the parent. Only a normal conduit
        can access the Spellbook to bind new spells.

        Optionally, in **dynamic mode**, you can supply a `hooks` mapping that will be
        registered into the Configuration and attached to this Conduit:

            hooks = {
                "on_meld_pre_resolve": trace_before_meld,
                "on_conduit_post_link": [log_link, audit_link],
            }

        The shape mirrors the Configuration hook registry:

            _hooks[owner_id][hook_name] -> list[callables]

        where `owner_id` is this Conduit's id.

        Please name the conduit if your intention is to add it to the Conduit Cloud.

        Args:
            name (str, optional):
                An optional name to assign to the upgraded conduit.
            hooks (dict[str, Any] | None, keyword-only):
                Optional mapping of hook_name -> callable or iterable[callable].
                Only honored when the system is in dynamic mode.

        Raises:
            RuntimeError: If the dynamic environment is not enabled.
            RuntimeError: If the current conduit state is not 'lesser'.
            RuntimeError / ValueError / TypeError:
                Propagated from Configuration.add_hooks(...) if the hook set is invalid
                (frozen configuration, unknown hook names, non-callables, etc.).
        """
        with self._lock:
            self._logger.debug("upgrade_to_normal start", "upgrade_to_normal")
            if not self.__dynamic_environment__:
                self._logger.error("upgrade_to_normal in non-dynamic env", "upgrade_to_normal")
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._conduit_state != ConduitState.lesser:
                self._logger.error("upgrade_to_normal called when not lesser", "upgrade_to_normal")
                raise RuntimeError("Only lesser conduits can be upgraded.")

            try:
                # Step 1: Change state + optional name
                self._conduit_state = ConduitState.normal
                self._name = name

                # Step 1.1: Attach any Spellbook-level hooks now that we're normal.
                # This *only* wires the map into _conduit_hooks; it does NOT fire hooks.
                self._initialize_conduit_hooks()

                # Step 2: Transfer creation data from LesserCreations
                creations_data = self._creations.transfer_data_and_clear()

                # Step 3: Create new Creations and inject data
                new_creations = Creations(
                    disposal_enabled=self._configuration.get_property("disposal"),
                    disposal_method_names=self._configuration.get_property("disposal_method_names"),
                    conduit=self,
                )
                new_creations._upgrade_from_lesser_conduit(**creations_data)

                # Step 4: Replace the old creations
                self._creations = new_creations

                # Step 5: Reconfigure the conduit ward
                self._conduit_ward._convert_to_normal_conduit()

                # Step 6: Reconfigure the spellbook
                self._spellbook.create_new_preset_spellbook()

                # Step 7: Register as a full Conduit in Aether and Conduit Cloud
                Conduit._add_conduit_to_aether(self)
                if self.__dynamic_environment__ and self._name is not None:
                    Conduit._aether._register_conduit_cloud(self, self._aetheric_frame)

                # Step 8: If the caller supplied per-conduit hooks, register them now.
                if hooks:
                    self._register_conduit_hooks_on_upgrade(hooks)

            except Exception as e:
                self._logger.error(f"upgrade_to_normal failed: {e}", "upgrade_to_normal", exc_info=True)
                raise

        self._logger.debug("upgrade_to_normal complete", "upgrade_to_normal")



    def set_new_policy(self, policy: str) -> None:
        """
        Public API

        Sets a new policy for this Conduit. This is only allowed in dynamic mode.

        Args:
            policy (str): The new policy to set, governing linking behavior.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error("set_new_policy in non-dynamic env", "set_new_policy")
            raise RuntimeError("Dynamic environment is not enabled. Cannot set new policy.")
        self._logger.debug(f"set_new_policy -> {policy}", "set_new_policy")
        with self._lock:
            self._conduit_ward._set_new_policy(policy)

    def create_lesser_conduit(self, logger: Any | None = None) -> IConduit:
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook and Configuration but is restricted
        in its ability to establish external links or register new spells.

        If this (parent) Conduit has lifecycle hooks attached via the Configuration
        for its Spellbook, the following hooks will be fired in order:

            1. "on_conduit_pre_created"
                   Fired *before* the lesser Conduit is constructed.

                   Signature:
                       hook(parent_conduit)

            2. "on_conduit_activated"
                   Fired immediately after the lesser Conduit instance has been
                   constructed (its __init__ has run).

                   Signature:
                       hook(new_conduit)

            3. "on_conduit_post_created"
                   Fired after the lesser Conduit has been constructed and
                   linked into this parent's ConduitWard.

                   Signature:
                       hook(parent_conduit, new_conduit)

        Returns:
            IConduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug("Creating lesser conduit", "create_lesser_conduit")

        with self._lock:
            # 1) Pre-create hook on the parent, if any.
            self._fire_conduit_hooks(
                "on_conduit_pre_created",
                self,  # parent_conduit
            )

            # 2) Construct the lesser conduit (activation point).
            new_conduit = Conduit(
                spellbook=self._spellbook,
                configuration=self._configuration,
                conduit_state=ConduitState.lesser,
                aetheric_frame=self._aetheric_frame,
                policy=Policies.default,
                logger=logger,
            )
            # Provide parent creations reference for delegation of frame-level singletons.
            try:
                if isinstance(self._creations, Creations):
                    new_conduit._parent_creations = self._creations
                    try:
                        if isinstance(new_conduit._creations, LesserCreations):
                            new_conduit._creations._parent_creations = self._creations
                    except Exception:
                        pass
            except Exception:
                pass

            # Fire activation hook with the new conduit instance.
            self._fire_conduit_hooks(
                "on_conduit_activated",
                new_conduit,  # new lesser conduit
            )

            # 3) Link the lesser conduit into the parent's ConduitWard.
            self._conduit_ward._link_lesser_conduit(new_conduit)

            # Fire post-create hook with both parent and child.
            self._fire_conduit_hooks(
                "on_conduit_post_created",
                self,         # parent_conduit
                new_conduit,  # child_conduit
            )

        self._logger.debug("Lesser conduit created and linked", "create_lesser_conduit")
        return new_conduit




    #endregion Conduit Management
    #region Spellbook Management API
    def _add_spells_to_aether(self) -> None:
        """
        Internal

        Adds this Conduit's local spell lineages (SpellIndex keys) into the shared
        Aether world's registry.

        Aether is responsible for mapping individual version IDs inside each
        SpellIndex to the owning conduit.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        if Conduit._aether is None:
            self._logger.error("Aether is not initialized", "_add_spells_to_aether")
            raise RuntimeError("Aether is not initialized.")

        # NOTE: these are SpellIndex objects, not raw version SHA strings
        spell_indices = list(self._spellbook._spells.keys())
        self._logger.debug(
            f"Registering {len(spell_indices)} local spell lineages into Aether",
            "_add_spells_to_aether",
        )

        spell_set = set(spell_indices)
        Conduit._aether._add_spells_to_aether(self._id, spell_set, self._aetheric_frame)



    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        This method queries the Aether to find the original source conduit for a specific spell ID.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug(f"Resolve owner for spell_id={spell_id}", "get_conduit_by_spell_id")
        with self._lock:
            return Conduit._aether._get_conduit_by_spell_id(spell_id, aetheric_frame_name)

    def check_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Public API

        Checks if a spell with the given spell_id exists within the global Aether registry.

        Args:
            spell_id (str): The unique identifier of the spell to check (version SHA).
            aetheric_frame_name (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            bool: True if the spell exists in the Aether, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            raw = Conduit._aether._check_for_spell(spell_id, aetheric_frame_name)
            found = bool(raw)
        self._logger.debug(f"check_spell_id spell_id={spell_id} -> {found}", "check_spell_id")
        return found


    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Public API

        Retrieves a spell object by its unique version identifier (spell_id) from the
        spellbook of its owner.

        The method:
          1) Uses Aether to locate the owning conduit.
          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains
             this version ID.
          3) Returns the corresponding ISpell instance if found.

        Args:
            spell_id (str): The unique version identifier of the spell (SHA256).
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Any]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            owner = self.get_conduit_by_spell_id(spell_id, aetheric_frame_name)
            if owner is None:
                result = None
            else:
                # Walk the owner's SpellIndex keys and find the lineage that contains this version
                result = None
                for spell_index, spell in owner._spellbook._spells.items():
                    # SpellIndex is responsible for telling us whether it owns this version
                    if spell_index.has_version(spell_id):
                        result = spell
                        break

        self._logger.debug(
            f"get_spell_by_id spell_id={spell_id} -> {'hit' if result else 'miss'}",
            "get_spell_by_id",
        )
        return result


    def find_contracted_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        Locate a contracted spell by its version spell_id across all peer
        conduits in this Spellbook.

        Args:
            spell_id (str): The unique version ID (SHA) of the spell to find.

        Returns:
            Optional[ISpell]: The contracted spell instance, or None if not found.
        """
        self.check_cleaned()
        with self._lock:
            spellbook = self._spellbook

            # Walk all peer conduit contract maps in this spellbook
            for conduit_id in spellbook._contracted_spells.keys():
                # Delegate per-conduit search to Spellbook's helper
                spell = spellbook._find_contracted_spell_by_id(spell_id, conduit_id)
                if spell is not None:
                    return spell

        return None



    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Finds a spell's current version ID (SHA256 spell_id) using its logical identifiers.

        This now uses:
          1) Spellbook.find_spell_index(...) to locate the SpellIndex lineage.
          2) Spellbook._find_spell(SpellIndex) to retrieve the ISpell.
          3) Returns spell.spell_id (the current head version for that lineage).

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[str]: The current SHA256 identifier of the spell.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        self.check_cleaned()
        self._logger.debug(
            f"find_spell_id(frame={spellframe}, name={spell_name}, binding={binding_name})",
            "find_spell_id",
        )

        # This will raise RuntimeError if the key is not found; we translate to ValueError
        try:
            spell_index = self._spellbook.find_spell_index(spellframe, spell_name, binding_name)
        except RuntimeError as e:
            self._logger.error(str(e), "find_spell_id")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.") from e

        spell = self._spellbook._find_spell(spell_index)
        if spell is None:
            self._logger.error(f"Spell '{spell_name}' not found for SpellIndex {spell_index}", "find_spell_id")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")

        return spell.spell_id


    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The key is typically a tuple used for internal retrieval within the spellbook.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's key (frame, name, binding_name) tuple.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        self.check_cleaned()
        self._logger.debug(f"find_spell_key(frame={spellframe}, name={spell_name}, binding={binding_name})", "find_spell_key")
        spell_key = self._spellbook.find_spell_key(spellframe, spell_name, binding_name)
        if not spell_key:
            self._logger.error(f"Spell key for '{spell_name}' not found", "find_spell_key")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_key

    def inspect_spell(self, spell: Any, aetheric_frame= "default") -> Optional[str]:
        """
        Public API

        Inspects any object to determine if it is a valid, registered spell in the Aether Registry.

        This method uses the Spellbook's internal reflection to identify the spell.

        Args:
            spell (Any): The class, function, or object instance to inspect.
            aetheric_frame (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            Optional[str]: The SHA256 unique ID of the spell if found, otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellbook.inspect_spell(spell, aetheric_frame)

    def create_binder(
            self,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> 'SpellBinder':
        """
        Public API

        Creates a `SpellBinder` instance that provides an Autofac-style
        fluent syntax on top of `Conduit.bind(...)`.

        This does *not* introduce a new registration path; it simply
        forwards everything into the existing binding pipeline so all
        reflection, `SpellIndex` construction, `SpellType` classification,
        and validation flows remain exactly the same.

        Example:
            binder = spellbook.create_binder()

            binder.bind(MyService) \\
                  .as_unique() \\
                  .under_spellframe(IMyServiceProtocol) \\
                  .named("primary") \\
                  .with_permissions("create") \\
                  .finalize()

            # Reuse the same binder for another spell:
            binder.bind(OtherService, existence=Existence.many).finalize()

        Args:
            default_existence (Existence):
                Default lifecycle scope for fluent registrations started via
                this binder.

            default_permissions (str):
                Default permissions for fluent registrations (e.g. "create").

        Returns:
            SpellBinder:
                A reusable fluent registration helper bound to this Spellbook.
        """
        self.check_cleaned()
        return self._spellbook.create_binder(
            default_existence=default_existence,
            default_permissions=default_permissions,
        )

    def bind(self, *, spell, existence: str, permissions: str = "create", spellframe=None, binding_name=None, **kwargs) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        ──────────────────────────────────────────────
        🧠 Binding Overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell into the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to *use* the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use *and* create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        📦 Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        🔑 Binding Name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        ──────────────────────────────────────────────
        🪝 Lifecycle Hooks (optional `**kwargs`):

            - `pre_hooks`: List[Callable]
                Executed *before* the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: List[Callable]
                Executed *during* spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: List[Callable]
                Executed *after* the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            ⚠️ All hooks must be callables.

        ──────────────────────────────────────────────
        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs:
                - pre_hooks (Optional[List[Callable]]): Hooks executed before casting.
                - activation_hooks (Optional[List[Callable]]): Hooks executed during casting/construction.
                - post_hooks (Optional[List[Callable]]): Hooks executed after casting/construction.

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits can bind spells).
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        self.check_cleaned()
        if not self._conduit_state == ConduitState.normal:
            self._logger.error("bind called when conduit not normal", "bind")
            raise RuntimeError("Only normal conduits can bind spells.")
        self._logger.debug(
            f"bind(spell={getattr(spell, '__name__', type(spell).__name__)}, existence={existence}, permissions={permissions}, frame={spellframe}, binding={binding_name})",
            "bind"
        )
        with self._lock:
            return self._spellbook.bind(spell=spell, existence=existence, spellframe=spellframe, binding_name=binding_name, permissions=permissions, **kwargs)


    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its version spell_id, **within this
        conduit’s own spellbook**.

        This returns the access level ("read", "create", "block") defined when the
        spell was bound.

        Args:
            spell_id (str): Version SHA256 identifier of the spell.

        Returns:
            Optional[str]: The permissions associated with the spell's binding.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
        """
        self.check_cleaned()
        with self._lock:
            target_spell: Optional[ISpell] = None

            # Walk local SpellIndex keys and check which lineage owns this version
            for spell_index, spell in self._spellbook._spells.items():
                if spell_index.has_version(spell_id):
                    target_spell = spell
                    break

        if target_spell is not None:
            perms = target_spell.permissions.name
            self._logger.debug(
                f"get_spell_permissions spell_id={spell_id} -> {perms}",
                "get_spell_permissions",
            )
            return perms

        self._logger.error(f"Spell with ID {spell_id} not found", "get_spell_permissions")
        raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")



    #endregion Spellbook Management API
    #region Cluster API
    def create_cluster(self, cluster_name: str) -> None:
        """
        Public API

        Create a new conduit cluster in this conduit’s aetheric frame.
        """
        self.check_cleaned()
        Conduit._aether._create_cluster(cluster_name, self._aetheric_frame)

    def delete_cluster(self, cluster_name: str) -> None:
        """
        Public API

        Delete an existing conduit cluster in this conduit’s aetheric frame.
        """
        self.check_cleaned()
        Conduit._aether._remove_cluster(cluster_name, self._aetheric_frame)

    def join_cluster(self, cluster_name: str) -> None:
        """
        Public API

        Join an existing conduit cluster. Auto-sharing of eligible roots occurs on join.
        """
        self.check_cleaned()
        Conduit._aether._add_conduit_to_cluster(self, cluster_name, self._aetheric_frame)

    def leave_cluster(self, cluster_name: str) -> None:
        """
        Public API

        Leave a conduit cluster. Auto-teardown of shared roots occurs on leave.
        """
        self.check_cleaned()
        Conduit._aether._remove_conduit_from_cluster(self, cluster_name, self._aetheric_frame)

    def list_clusters(self) -> list[str]:
        """
        Public API

        List cluster names this conduit belongs to in its aetheric frame.
        """
        self.check_cleaned()
        return Conduit._aether._get_clusters_for_conduit(self._id, self._aetheric_frame)

    def refresh_cluster_shares(self) -> None:
        """
        Public API

        Refresh sharing of auto-shareable roots for this conduit across all clusters it belongs to.
        """
        self.check_cleaned()
        Conduit._aether._refresh_cluster_shares_for_conduit(self, self._aetheric_frame)

    def transfer_spell_ownership(
            self,
            *,
            spell: ISpell | str | SpellIndex,
            target_conduit: IConduit,
            move_creations: bool = False,
            include_dependencies: bool = False,
            force_unshare: bool = True,
            invalidate_after_transfer: bool = True,
            mark_dependencies_dirty: bool = False,
    ) -> dict:
        """
        Public API (dynamic mode)

        Transfer stewardship of a spell to another conduit.

        Args:
            spell: Spell object, spell_id, or SpellIndex to transfer.
            target_conduit: The conduit that will become the new steward.
            move_creations: If True, move creations; else tear them down at source.
            include_dependencies: If True, transfer owned dependencies as well.
            force_unshare: If True, strip all contracts/shares for this spell during transfer.
            invalidate_after_transfer: If True, mark lineage dirty after transfer.
            mark_dependencies_dirty: If True, mark dependency lineages dirty (even if not moved).

        Returns:
            dict: Preflight summary of the transfer plan.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            raise RuntimeError("Ownership transfer requires dynamic mode.")
        return self._conduit_ward._transfer_spell_ownership(
            spell=spell,
            target_conduit=target_conduit,
            move_creations=move_creations,
            include_dependencies=include_dependencies,
            force_unshare=force_unshare,
            invalidate_after_transfer=invalidate_after_transfer,
            mark_dependencies_dirty=mark_dependencies_dirty,
        )
    #endregion Cluster API
    #region Meld

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Public API

        Direct spell activation facade for this Conduit.

        At the Conduit boundary, `meld` is a **string-only** API:
        callers must always provide a concrete `spell` identifier
        (the spell's `spell_id`), and may optionally supply a
        logical `spellframe` and `binding_name` for metadata or
        downstream consumers.

        Resolution, reuse, and lifecycle behavior are delegated to
        the underlying ``Meld`` instance.

        Args:
            spell_name:
                Simple name of the spell (string).
            spell:
                The unique spell identifier (string) to resolve.
                This is typically the SHA256 version ID of the spell.
            spellframe:
                Optional logical spellframe identifier (string).
                Not used for resolution at this layer, but may be
                useful for tracing, logging, or future behavior.
            binding_name:
                Optional binding name (string) associated with the
                spell. Also not used for resolution here, but passed
                through to ``Meld.meld`` for potential consumers.
            spell_override:
                Optional payload (dict / list / tuple) attached to the
                Spell's metadata under the key ``"spell_override"``.

        Returns:
            Any:
                The resolved component instance (reused or newly
                created) as returned by ``Meld.meld``.

        Raises:
            RuntimeError:
                - If the Conduit has been cleaned.
                - If the underlying ``Meld`` instance is missing.
            TypeError:
                - If `spell` is not a non-empty string.
                - If `spellframe` is not a string when provided.
                - If `binding_name` is not a string when provided.
            KeyError:
                Propagated from ``Meld.meld`` when a spell_id cannot be
                resolved.
            NotImplementedError:
                Propagated from ``Meld.meld`` for spell types or
                existence modes not yet implemented.
            HookExecutionError:
                Propagated from ``Meld.meld`` if hook execution fails.
        """
        self.check_cleaned()

        if self._meld is None:
            self._logger.error("Meld instance is not available on this Conduit", "meld")
            raise RuntimeError("[CONDUIT] Meld instance is not available on this Conduit.")

        if spell_name is None and spell is None and spellframe is None:
            self._logger.error(
                "Conduit.meld requires at least one of spell_name, spell, or spellframe",
                "meld",
            )
            raise ValueError(
                "[CONDUIT] meld(...) requires at least one of "
                "`spell_name`, `spell`, or `spellframe`."
            )

        if spell_name is not None and not isinstance(spell_name, str):
            self._logger.error("spell_name must be a string when provided", "meld")
            raise TypeError(
                "[CONDUIT] 'spell_name' must be a string when "
                "provided to Conduit.meld()."
            )

        if binding_name is not None and not isinstance(binding_name, str):
            self._logger.error("binding_name must be a string identifier when provided", "meld")
            raise TypeError(
                "[CONDUIT] 'binding_name' must be a string identifier when "
                "provided to Conduit.meld()."
            )

        self._logger.debug(
            f"meld(spell_name={spell_name!r}, spell={spell!r}, "
            f"frame={spellframe!r}, binding={binding_name!r})",
            "meld",
        )

        self._fire_conduit_hooks("on_meld_pre_resolve", self)

        result = self._meld.meld(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )

        self._fire_conduit_hooks("on_meld_post_resolve", self)

        return result




    #endregion Meld
    #region Conduit Cloud
    def get_conduit_cloud(self) -> IConduitCloud:
        """
        Public API

        Returns the global Conduit Cloud, a registry of all normal conduits in the current Aetheric Frame.

        This object is designed to be used in dynamic mode only and serves as an Abstract Factory/Service Locator.

        Returns:
            IConduitCloud: The conduit cloud instance.

        Raises:
            RuntimeError: If the Conduit is a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if self._conduit_state == ConduitState.lesser:
            self._logger.error("get_conduit_cloud on lesser conduit", "get_conduit_cloud")
            raise RuntimeError("Lesser conduits cannot access the conduit cloud.")
        if not self.__dynamic_environment__:
            self._logger.error("get_conduit_cloud in non-dynamic env", "get_conduit_cloud")
            raise RuntimeError("Dynamic environment is not enabled. Cannot access conduit cloud.")
        self._logger.debug("get_conduit_cloud", "get_conduit_cloud")
        return Conduit._aether._get_conduit_cloud(self._aetheric_frame)

    #endregion Conduit Cloud
    #region Aether API
    def get_conduit_by_id(self, conduit_id: str, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its unique ID from the Aether.

        Args:
            conduit_id (str): The unique identifier of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If the `aetheric_frame` is not a string.
        """
        self.check_cleaned()

        if not isinstance(aetheric_frame, str):
            self._logger.error("aetheric_frame must be str", "get_conduit_by_id")
            raise TypeError(f"Expected aetheric_frame to be a string, got {type(aetheric_frame).__name__}")
        if aetheric_frame == "default":
            aetheric_frame = self._aetheric_frame
        self._logger.debug(f"get_conduit_by_id id={conduit_id}", "get_conduit_by_id")
        with self._lock:
            return Conduit._aether._get_conduit_by_id(conduit_id, aetheric_frame)

    def get_conduit_by_name(self, name: str, aetheric_frame:str = "default") -> Optional[IConduit]:
        """
        Public API

        Retrieves a conduit by its name from the Aether.

        Args:
            name (str): The name of the conduit.
            aetheric_frame (str): The aetheric frame to check against. Defaults to this conduit's frame.

        Returns:
            Optional[IConduit]: The conduit instance if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If the `aetheric_frame` is not a string.
        """
        self.check_cleaned()
        if not isinstance(aetheric_frame, str):
            self._logger.error("aetheric_frame must be str", "get_conduit_by_name")
            raise TypeError(f"Expected aetheric_frame to be a string, got {type(aetheric_frame).__name__}")
        if aetheric_frame == "default":
            aetheric_frame = self._aetheric_frame
        self._logger.debug(f"get_conduit_by_name name='{name}'", "get_conduit_by_name")
        with self._lock:
            return Conduit._aether._get_conduit_by_name(name, aetheric_frame)
    #endregion Aether API
    #region Conduit Ward API
    def link(self, target_conduit: IConduit) -> bool:
        """
        Public API

        Attempts to establish a link between this Conduit and a `target_conduit`.

        Linking is only allowed if the world is in dynamic mode. This process initiates a contract
        relationship between the two conduits based on the current policy.

        On success, the following hook will be fired on this Conduit (if configured):

            - "on_conduit_post_link(self, target_conduit)"

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            TypeError: If `target_conduit` is not an `IConduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error("link in non-dynamic env", "link")
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        if not isinstance(target_conduit, IConduit):
            self._logger.error("link target not IConduit", "link")
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        if not target_conduit._id:
            self._logger.error("link target has no valid creation context", "link")
            raise RuntimeError("Target conduit does not have a valid creation context.")
        self._logger.debug(f"link -> target={target_conduit._id}", "link")

        with self._lock:
            linked = self._conduit_ward._link(target_conduit)

        if linked:
            # Fire post-link hook with both ends of the relationship.
            self._fire_conduit_hooks(
                "on_conduit_post_link",
                self,
                target_conduit,
            )

        return linked

    def sever_link(self, target_conduit: IConduit) -> bool:
        """
        Public API

        Sever the link and the corresponding spell contracts between this Conduit and its target Conduit.

        This method validates the link's existence, ensures it can be severed according to policy,
        and removes the link and all contracted spells. This is intended for public use to dissolve a relationship.

        On success, the following hook will be fired on this Conduit (if configured):

            - "on_conduit_post_unlink(self, target_conduit)"

        Args:
            target_conduit (IConduit): The target Conduit whose link to sever.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error("sever_link in non-dynamic env", "sever_link")
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        self._logger.debug(f"sever_link target={target_conduit._id}", "sever_link")

        with self._lock:
            unlinked = self._conduit_ward._sever_link(target_conduit)

        if unlinked:
            # Fire post-unlink hook with both ends of the relationship.
            self._fire_conduit_hooks(
                "on_conduit_post_unlink",
                self,
                target_conduit,
            )

        return unlinked

    def get_links(self):
        """
        Public API

        Returns a list of all active peer links associated with this conduit.

        This list excludes links to lesser (child) conduits.

        Returns:
            list: A list of the linked conduit instances.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error("get_links in non-dynamic env", "get_links")
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        self._logger.debug("get_links", "get_links")
        with self._lock:
            return self._conduit_ward._get_links()

    def get_lesser_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Returns a specific lesser conduit (child) linked to this conduit by its ID.

        Args:
            conduit_id (str): The ID of the lesser conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked lesser conduit if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug(f"get_lesser_conduit id={conduit_id}", "get_lesser_conduit")
        with self._lock:
            return self._conduit_ward._get_lesser_conduit(conduit_id)


    def get_initiated_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the internal index to resolve an outbound connection,
        where this conduit was the **initiator** of the contract.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug(f"get_initiated_conduit id={conduit_id}", "get_initiated_conduit")
        with self._lock:
            return self._conduit_ward._get_initiated_conduit(conduit_id)


    def get_provider_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Public API

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the internal index to resolve an inbound connection,
        where another conduit linked to this one as the **provider**.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug(f"get_provider_conduit id={conduit_id}", "get_provider_conduit")
        with self._lock:
            return self._conduit_ward._get_provider_conduit(conduit_id)


    def get_initiated_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that this conduit has initiated contracts toward (outbound links).

        This is useful for understanding the dependencies and relationships initiated by this conduit.

        Returns:
            list[IConduit]: A list of conduits this conduit linked to.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug("get_initiated_conduits", "get_initiated_conduits")
        with self._lock:
            return self._conduit_ward._get_initiated_conduits()

    def get_provider_conduits(self) -> list[IConduit]:
        """
        Public API

        Returns a list of all conduits that have initiated contracts to this conduit (inbound links).

        These are the conduits that depend on this one for contracted spells.

        Returns:
            list[IConduit]: A list of conduits that have linked to this conduit as the provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug("get_provider_conduits", "get_provider_conduits")
        with self._lock:
            return self._conduit_ward._get_provider_conduits()

    def cleanup_lesser_conduits(self):
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This prevents further operations on lesser conduits and is typically used when the parent
        is cleaning or undergoing a major state change (e.g., upgrade).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._logger.debug("cleanup_lesser_conduits", "cleanup_lesser_conduits")
        self._conduit_ward.cleanup_all_lesser_conduits()

    #endregion Conduit Ward API
    #region Spell Contracting API
    def _qualify_contracts(self):
        """
        Internal

        Performs checks to ensure the conduit is in a state capable of managing spell contracts.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if self._conduit_state != ConduitState.normal:
            self._logger.error("_qualify_contracts: not normal state", "_qualify_contracts")
            raise RuntimeError("Only normal conduits can create spell contracts.")
        if not self.__dynamic_environment__:
            self._logger.error("_qualify_contracts: non-dynamic env", "_qualify_contracts")
            raise RuntimeError("Dynamic environment is not enabled. Cannot interact with spell contracts.")



    def add_spell_to_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None, conduit_id: str = None,
                              permissions: str = "create", aetheric_frame = "default", reason: DetailReason = DetailReason.manual,
                              root_spell_id: str | None = None, link_dependencies: bool = False) -> bool | None:
        """
        Public API

        Establishes a single spell contract between this conduit and another target conduit.

        This allows one conduit to borrow or grant a specific spell, identified either by object or ID,
        to/from a peer conduit. The contract defines the permissions under which the spell can be used.

        You must provide either a `spell` object or a `spell_id`. The target conduit must be specified
        either directly or resolved via its ID and aetheric frame.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The str of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            bool | None: True if the contract was created, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(
            f"add_spell_to_contract(spell_id={spell_id}, conduit_id={conduit_id}, perms={permissions}, link_deps={link_dependencies})",
            "add_spell_to_contract",
        )
        self._qualify_contracts()

        result = self._conduit_ward._add_spell_to_contract(
            spell=spell,
            spell_id=spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            permissions=permissions,
            aetheric_frame=aetheric_frame,
            reason=reason,
            root_spell_id=root_spell_id,
            link_dependencies=link_dependencies,
        )

        if result:
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_created",
                    self,
                    peer,
                )

        return result



    def add_spells_to_contract(self, spell_ids: list[str], conduit: IConduit = None, conduit_id: str = None,
                               permissions: str = "create", aetheric_frame = "default",
                               reason: DetailReason = DetailReason.manual, link_dependencies: bool = False) -> dict:
        """
        Public API

        Establishes multiple spell contracts with another conduit in a single operation.

        Allows you to bulk-grant or bulk-borrow spells by specifying a list of spell IDs. Each spell
        will be contracted using the same permission level.

        Args:
            spell_ids (list[str]): List of spell IDs to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The id of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for all spells (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each attempted contract.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(
            f"add_spells_to_contract(count={len(spell_ids)}, conduit_id={conduit_id}, perms={permissions}, link_deps={link_dependencies})",
            "add_spells_to_contract",
        )
        self._qualify_contracts()

        results = self._conduit_ward._add_spells_to_contract(
            spell_ids=spell_ids,
            conduit=conduit,
            conduit_id=conduit_id,
            permissions=permissions,
            aetheric_frame=aetheric_frame,
            reason=reason,
            link_dependencies=link_dependencies,
        )

        # Fire hook only if at least one contract addition succeeded.
        if results and any(results.values()):
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_created",
                    self,
                    peer,
                )

        return results


    def remove_spell_from_contract(self, *, spell: ISpell = None, spell_id: str = None, conduit: IConduit = None,
                                   conduit_id: str = None, root_spell_id: str | None = None, aetheric_frame = "default") -> bool | None:
        """
        Public API

        Removes a single spell contract between this conduit and another.

        Either the `spell` or `spell_id` can be provided to specify the contract to dissolve.
        Once removed, the spell is no longer accessible across the link.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target conduit involved in the contract.
            conduit_id (str, optional): id of the target conduit (used if `conduit` not provided).
            aetheric_frame (str): Optional frame override to resolve the target conduit.

        Returns:
            bool | None: True if the spell was successfully removed from the contract, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(
            f"remove_spell_from_contract(spell_id={spell_id}, conduit_id={conduit_id}, root_spell_id={root_spell_id})",
            "remove_spell_from_contract",
        )
        self._qualify_contracts()

        result = self._conduit_ward._remove_spell_from_contract(
            spell=spell,
            spell_id=spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            root_spell_id=root_spell_id,
            aetheric_frame=aetheric_frame,
        )

        if result:
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return result

    def remove_spells_from_contract(self, *, spell_ids: list[str] = None, conduit: IConduit = None,
                                    conduit_id: str = None, root_spell_id: str | None = None, aetheric_frame = "default") -> dict:
        """
        Public API

        Removes multiple spells from an existing contract with a target conduit.

        Useful for bulk cleanup or revocation when retiring behaviors or permissions.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each removal attempt.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(
            f"remove_spells_from_contract(count={0 if spell_ids is None else len(spell_ids)}, conduit_id={conduit_id}, root_spell_id={root_spell_id})",
            "remove_spells_from_contract",
        )
        self._qualify_contracts()

        results = self._conduit_ward._remove_spells_from_contract(
            spell_ids=spell_ids,
            conduit=conduit,
            conduit_id=conduit_id,
            root_spell_id=root_spell_id,
            aetheric_frame=aetheric_frame,
        )

        if results and any(results.values()):
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return results

    def remove_root_from_contracts(self, *, root_spell_id: str, conduit: IConduit = None,
                                   conduit_id: str = None, aetheric_frame: str = "default") -> dict:
        """
        Public API

        Removes a root spell_id (and any dependency Details attributed to it) from one
        contract or all contracts. Orphaned Details trigger contracted spell removal;
        empty contracts are severed.
        """
        self._logger.debug(
            f"remove_root_from_contracts(root_spell_id={root_spell_id}, conduit_id={conduit_id})",
            "remove_root_from_contracts",
        )
        self._qualify_contracts()
        return self._conduit_ward._remove_root_from_contracts(
            root_spell_id=root_spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            aetheric_frame=aetheric_frame,
        )

    def add_spell_to_contract_with_dependencies(
            self,
            *,
            spell: ISpell = None,
            spell_id: str = None,
            conduit: IConduit = None,
            conduit_id: str = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API helper

        Adds a spell to a contract and automatically links its dependencies
        (recursively) using the same permission level (downgraded to read when needed).
        """
        return self.add_spell_to_contract(
            spell=spell,
            spell_id=spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            permissions=permissions,
            aetheric_frame=aetheric_frame,
            reason=DetailReason.root,
            root_spell_id=spell_id,
            link_dependencies=True,
        )


    def _remove_all_spells_from_contract(self, *, conduit: IConduit = None, conduit_id: str = None, aetheric_frame = "default") -> bool | None:
        """
        Public API

        Dissolves **all** spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the spell relationship between the two conduits.

        Args:
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            bool | None: True if all spells were successfully removed, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(f"_remove_all_spells_from_contract(conduit_id={conduit_id})", "_remove_all_spells_from_contract")
        self._qualify_contracts()

        result = self._conduit_ward._remove_all_spells_from_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            aetheric_frame=aetheric_frame,
        )

        if result:
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return result

    def get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, ISpell]]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts (i.e., borrowed spells).

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        Args:
            validate (bool): If True, performs contract consistency validation before returning data.

        Returns:
            Optional[dict[str, list[Tuple[str, ISpell]]]]: Dictionary mapping peer conduit ids to lists of (spell_id, ISpell) tuples,
            or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `validate` is not a boolean.
        """
        self._logger.debug(f"get_all_spells_in_contracts(validate={validate})", "get_all_spells_in_contracts")
        self._qualify_contracts()
        if not isinstance(validate, bool):
            self._logger.error("validate must be bool", "get_all_spells_in_contracts")
            raise TypeError(f"Expected validate to be a boolean, got {type(validate).__name__}")
        return self._conduit_ward._get_all_spells_in_contracts(validate=validate)

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, ISpell]]:
        """
        Public API

        Searches all known contracts to find the origin of a specific contracted spell.

        Looks for a specific spell by ID and returns the str of the conduit it's contracted from
        along with the spell object, if found.

        Args:
            spell_id (str): The unique ID of the spell.

        Returns:
            Optional[tuple[str, ISpell]]: Tuple of (`conduit_id`, `spell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `spell_id` is not a string.
        """
        self._logger.debug(f"get_spell_in_contracts(spell_id={spell_id})", "get_spell_in_contracts")
        self._qualify_contracts()
        if not isinstance(spell_id, str):
            self._logger.error("spell_id must be str", "get_spell_in_contracts")
            raise TypeError(f"Expected spell_id to be a string, got {type(spell_id).__name__}")
        return self._conduit_ward._get_spell_in_contracts(spell_id)

    def get_spells_in_contract_by_conduit(self, conduit_id: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a specific peer conduit, identified by id.

        Returns a detailed list of all spells that this conduit currently accesses or has granted
        through its relationship with the specified peer.

        Args:
            conduit_id (str): id of the target peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_id` is not a str.
        """
        self._logger.debug(f"get_spells_in_contract_by_conduit(conduit_id={conduit_id})", "get_spells_in_contract_by_conduit")
        self._qualify_contracts()
        if not isinstance(conduit_id, str):
            self._logger.error("conduit_id must be id", "get_spells_in_contract_by_conduit")
            raise TypeError(f"Expected conduit_id to be a id, got {type(conduit_id).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit(conduit_id)

    def get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Performs resolution using a human-readable name instead of str.

        Args:
            conduit_name (str): Name of the peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_name` is not a string.
        """
        self._logger.debug(f"get_spells_in_contract_by_conduit_name(name='{conduit_name}')", "get_spells_in_contract_by_conduit_name")
        self._qualify_contracts()
        if not isinstance(conduit_name, str):
            self._logger.error("conduit_name must be str", "get_spells_in_contract_by_conduit_name")
            raise TypeError(f"Expected conduit_name to be a string, got {type(conduit_name).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit_name(conduit_name)


    def get_contracted_conduits(self) -> list[Tuple[str, IConduit]] | None:
        """
        Public API

        Lists all conduits that have an active spell contract with this conduit.

        Each returned conduit represents a peer in the current dynamic spell network.

        Returns:
            list[Tuple[str, IConduit]] | None: List of (`conduit_id`, `IConduit`) tuples, or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug("get_contracted_conduits", "get_contracted_conduits")
        self._qualify_contracts()
        return self._conduit_ward._get_contracted_conduits()

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Public API

        Produces a detailed diagnostic summary of a contract established with a specific conduit.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduit’s name, the number of active spells involved, and permission levels.
        Primarily used for debugging, introspection, and UI inspection tools.

        Args:
            conduit_id (str): str of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including a list of spells and their permissions.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug(f"_describe_contract(conduit_id={conduit_id})", "_describe_contract")
        self._qualify_contracts()
        return self._conduit_ward._describe_contract(conduit_id)

    def validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Public API

        Validates all known contracts attached to this conduit and confirms mutual agreement and consistency.

        This performs a deep validation pass, ensuring both sides list the same spells, permissions are symmetrical,
        and all referenced spells are valid.

        Returns:
            dict[str, bool]: Dictionary mapping contract ids to validation results:
                 - True: Contract is valid and consistent
                 - False: Contract is malformed or inconsistent

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug("validate_contracts_and_define", "validate_contracts_and_define")
        self._qualify_contracts()
        return self._conduit_ward._validate_contracts_and_define()


    def validate_received_contracts(self) -> bool:
        """
        Public API

        Performs a high-level validation check across all contracts involving this conduit.

        Aggregates the results of `_validate_contracts_and_define` to determine whether every connected
        contract is structurally valid and symmetrical.

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._logger.debug("validate_received_contracts", "validate_received_contracts")
        self._qualify_contracts()
        return self._conduit_ward._validate_received_contracts()


#endregion Spell Contracting API
#region Mutation Research
    def get_mutation_research(self):
        """
        Public API

        Returns the MutationResearch manager for this Conduit's Aetheric Frame.

        Mutation Research is a specialized system that allows AI agents to study and mutate spells and creations.
        If you are a human using this API directly, be aware that Mutation Research is primarily designed for AI-driven
        experimentation and may not be suitable for manual use.

        This method is only available when:
          - The Conduit is a NORMAL conduit.
          - The system is in DYNAMIC mode.

        Returns:
            MutationResearch: The mutation research manager for this Conduit's frame.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()

        # Validate state: must be normal + dynamic
        if self._conduit_state != ConduitState.normal:
            self._logger.error("get_mutation_research on non-normal conduit", "get_mutation_research")
            raise RuntimeError("Only normal conduits can access MutationResearch.")

        if not self.__dynamic_environment__:
            self._logger.error("get_mutation_research in non-dynamic env", "get_mutation_research")
            raise RuntimeError("Dynamic environment is not enabled. MutationResearch is unavailable.")

        # Pull from Aether
        self._logger.debug("Fetching MutationResearch for this conduit/frame", "get_mutation_research")
        return Conduit._aether._get_mutation_research(self._aetheric_frame)

#endregion Mutation Research


#region Hooks
    def _resolve_peer_conduit_for_contract_hooks(
            self,
            conduit: IConduit | None,
            conduit_id: str | None,
            aetheric_frame: str,
    ) -> Optional[IConduit]:
        """
        Internal

        Resolve the peer conduit instance for contract-related hooks.

        This helper normalizes the two input forms:

            - Direct `conduit` instance, or
            - `conduit_id` + `aetheric_frame`

        so that hooks can always receive a concrete Conduit object when
        possible.

        Args:
            conduit (IConduit | None):
                Optional direct conduit instance supplied by the caller.
            conduit_id (str | None):
                Optional conduit id, used when `conduit` is not provided.
            aetheric_frame (str):
                Frame hint; "default" means this Conduit's own frame.

        Returns:
            Optional[IConduit]:
                The resolved peer conduit, or None if it cannot be resolved.
        """
        if conduit is not None:
            return conduit

        if conduit_id is None:
            return None

        frame = self._aetheric_frame if aetheric_frame == "default" else aetheric_frame
        try:
            return Conduit._aether._get_conduit_by_id(conduit_id, frame)
        except Exception:
            # Hooks are advisory; failure to resolve a peer must not
            # break the primary contract APIs.
            return None


    def _fire_conduit_hooks(self, hook_name: str, *conduits: "Conduit") -> None:
        """
        Internal

        Invoke all local Conduit hooks registered under ``hook_name``, if any.

        This uses the hook map localized into this Conduit via
        :meth:`_initialize_conduit_hooks`. The contract is intentionally
        narrow and stable:

            - All hooks are plain callables.
            - They are invoked as: hook(*conduits)
            - Each element in ``conduits`` MUST be a Conduit instance.
            - Exceptions are logged and suppressed so hooks cannot
              destabilize core lifecycle behavior.

        Typical patterns:

            - on_conduit_pre_created(parent)
            - on_conduit_activated(new_conduit)
            - on_conduit_post_created(parent, new_conduit)
            - on_conduit_cleanup_start(conduit)
            - on_conduit_cleanup_complete(conduit)

        Args:
            hook_name (str):
                The canonical hook name to invoke
                (e.g., "on_conduit_pre_created", "on_conduit_post_created").
            *conduits:
                One or more Conduit instances passed directly to each hook.
        """
        hooks_by_name = self._conduit_hooks
        if not hooks_by_name:
            return

        hook_list = hooks_by_name.get(hook_name)
        if not hook_list:
            return

        for hook in list(hook_list):
            try:
                hook(*conduits)
            except Exception as e:
                # Hooks are advisory; they must not break Conduit behavior.
                self._logger.error(
                    f"Error while executing hook '{hook_name}': {e}",
                    "_fire_conduit_hooks",
                    exc_info=True,
                )


#endregion Hooks
#endregion Conduit
