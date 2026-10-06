"""Registry and per-call builder for framework tool constructors.

Toolbox is a shared native-built manager: one instance per configured framework,
melded at the SPECTRUM label and borrowed by SpectrumResources. It maps symbolic names
to native class definitions and melds caller-owned tools from the requesting scope.
It owns the alias map, late-definition registry, lock, identity and logger. Products
remain untracked. Alias updates use its lock; native calls and constructors run outside it.
"""

import inspect
from threading import RLock
from typing import Any, Dict, Type, Optional, TYPE_CHECKING
from melder import Cleanable, MeldExecutionError, new_ulid
from melder_ops.command_center.spectrum.bootstraps.command_center_definitions import CommandCenterDefinitions
from melder_ops.command_center.spectrum.bootstraps.root_definitions import RootDefinitionRegistry

if TYPE_CHECKING:
    from melder import Conduit
    from melder_ops.command_center.spectrum.iris.channel_logger import ChannelLogger
    from melder_ops.command_center.spectrum.toolbox.base import BaseTool

class Toolbox(Cleanable):
    """
    A central registry and builder for creating instances of tool classes
    within the MelderOps framework.

    One shared native-built manager instance serves a configured framework. The registry
    holds class aliases, not live tools: each build call melds a fresh
    caller-owned instance, so registry state and tool execution state are distinct
    concerns and tools are free to hold per-instance state.

    This class allows for the dynamic registration and instantiation of
    `BaseTool` subclasses by a symbolic, namespaced name (e.g., "web.click"),
    promoting a decoupled and extensible architecture. It manages a collection
    of registered tool types, enabling an Agent to build a specific tool
    without directly importing its class.

    Registration admits a concrete class through RootDefinitionRegistry at the spectrum
    label before publishing its alias. Existing compatible definitions are borrowed;
    definitions introduced here are removed after their last alias or at cleanup.
    The framework root is borrowed and never cleaned by Toolbox.

    Alias replacement and orphan checks use the instance lock. Native operations and user
    constructors execute outside it. Callers coordinate last-alias retirement with builds
    and finish using this manager before cleanup; no lifetime reservation is implicit.
    Explicit cleanup removes owned definitions and retires the logger last, never tools.
    """
    __slots__ = Cleanable.__slots__ + ["_registry", "_registered", "_lock", "_logger", "_id", "_definitions"]

    def __init__(self, logger: ChannelLogger, *, root_conduit: Conduit) -> None:
        """
        Initializes a new instance of the Toolbox.

        A fresh builder is created with an empty internal registry for tool
        classes. It can be configured to automatically register any built-in
        default tool types. None ship today; the registry starts empty.

        Args:
            logger: Dedicated, uninitialized ChannelLogger supplied by the native scope.
                Its annotation feeds native manager construction and must stay resolvable.
            root_conduit: Borrowed framework root for late class definitions. Spectrum
                supplies this exact conduit through its meld override; never bind a conduit.

        This Toolbox generates its own fresh ULID during construction. The local registry
        is ready before the logger enrolls with that identity.
        Cleanup clears aliases, removes owned definitions and retires the logger last; returned tools
        remain caller-owned. Registering additional constructors after construction is allowed.
        Failed construction cleans initialized local state and the
        injected logger before propagating the original failure to the scope owner.
        """
        super().__init__()
        self._id: str = new_ulid()
        self._logger: ChannelLogger = logger
        self._lock: RLock = RLock()

        # Registry now stores tool classes (constructors)
        self._registry: Dict[str, Type[BaseTool]] = {}
        self._definitions = RootDefinitionRegistry(root_conduit, spellframe=CommandCenterDefinitions.SPECTRUM)
        self._registered: bool = False
        try:
            self._register_defaults()
            self._logger.initialize(
                name=f"{self._id}.{type(self).__name__}", id=self._id, channels=["system"],
                groups=["lifecycle", "configuration", "resources"], system_groups=["toolbox"],
            )
        except BaseException as error:
            try:
                self.cleanup()
            except Exception as cleanup_error:
                error.add_note(f"Toolbox construction cleanup also failed: {cleanup_error}")
            raise

    def cleanup(self) -> None:
        """
        Idempotent teardown:
          Phase 1 (under instance lock): internal registry cleanup
          Phase 2 (after lock): owned definitions, lock teardown, owned refs, logger last.
        Every definition removal is attempted before reporting a removal failure.
        Built tools and the borrowed framework root remain with their existing owners.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._logger is not None:
                self._logger.info(
                    f"Cleaning Toolbox (ID: {self._id})...",
                    _manual_stack=True, _method_name="cleanup"
                )

            # Phase 1: best-effort cleanup of the internal registry
            self._cleanup_internal_registry()

        # Phase 2: outside the lock
        self._cleanup_core()


    def _cleanup_internal_registry(self) -> None:
        """
        Clear registered tool classes while the caller holds the instance lock.

        The owned registry is an ordinary dictionary, not a Cleanable resource.
        Clearing releases class registrations without cleaning classes or the tool
        instances previously returned to callers. An empty registry is a no-op.
        Keep the container reference until _cleanup_core deletes it; logger teardown
        remains after registry retirement.

        Returns:
            None. The same dictionary is emptied in place.
        """
        self._registry.clear()


    def _cleanup_core(self) -> None:
        """
        Final teardown (outside the instance lock):
          1) remove owned definitions and release the borrowed root, then delete the
             instance-owned threading.RLock. The root and tool products are never cleaned.
          2) delete the owned registry; _registered is reset to False, a plain
             flag rather than an owned reference
          3) logger last, deleted after its own cleanup
        """
        failure: Optional[Exception] = None
        try:
            self._definitions.cleanup()
        except Exception as error:
            failure = error
        finally:
            del self._definitions
        del self._lock

        # 2) Drop the owned registry. Every public reader (register_tool,
        #    unregister_tool, build_tool, list_tools) calls check_cleaned() first, so
        #    they raise RuntimeError before reaching it; _cleanup_internal_registry()
        #    read it in phase 1.
        del self._registry
        self._registered = False  # basic type; fine to set terminal state

        # 3) Logger last, even when removing a native definition failed.
        if self._logger is not None:
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            finally:
                del self._logger
        if failure is not None:
            raise failure


    def _register_defaults(self) -> None:
        """
        Internal helper method to register any default, built-in tool classes.
        This is called during initialization. Currently registers nothing: the empty
        registry is the honest default, and hosts add constructors explicitly.
        """
        self.check_cleaned()
        if self._registered:
            return
        # --- Example of where you would register default tools ---
        # from .tools import DefaultClickTool
        # self.register_tool("web.click", DefaultClickTool)
        self._registered = True

    def register_tool(self, name: str, tool_class: Type[BaseTool]) -> None:
        """
        Admit a concrete tool definition, then publish its symbolic alias.

        Native admission precedes alias replacement, so a refused definition leaves the
        previous alias unchanged. An exact compatible class already in the root is borrowed;
        otherwise the registry binds it many and untracked at the spectrum label. Replacing
        the last alias of an owned class removes that definition without cleaning its products.

        Args:
            name (str): Any string, even empty, used as the registry key for this tool type (e.g., "web.click").
            tool_class (Type[BaseTool]): The concrete `BaseTool` subclass to register.

        Raises:
            TypeError: The name is not a string, or tool_class is not a concrete BaseTool subclass.
            ValueError: The native address has an incompatible class or lifetime.
            RuntimeError: If this Toolbox has already been cleaned.
            Exception: Native registration/removal fails; the original error propagates.
        """
        self.check_cleaned()
        if not isinstance(name, str):
            self._logger.error(f"Tool name must be a string, got {type(name).__name__}.", exc_info=True, _method_name="register_tool", _manual_stack=True)
            raise TypeError(f"Tool name must be a string, got {type(name).__name__}.")
        from melder_ops.command_center.spectrum.toolbox.base import BaseTool
        if not issubclass(tool_class, BaseTool):
            self._logger.error(f"Attempted to register invalid tool class '{tool_class.__name__}' that is not a subclass of BaseTool", _manual_stack=True, _method_name="register_tool", exc_info=True)
            raise TypeError(f"Registered class '{tool_class.__name__}' must be a subclass of BaseTool.")
        if inspect.isabstract(tool_class):
            raise TypeError(f"Tool class '{tool_class.__name__}' is abstract and cannot be registered.")
        self._definitions.ensure(tool_class)
        with self._lock:
            displaced = self._registry.get(name)
            self._registry[name] = tool_class
            orphaned = displaced is not None and not any(item is displaced for item in self._registry.values())
        if orphaned:
            self._definitions.release(displaced.__name__)

    def unregister_tool(self, name: str) -> None:
        """
        Removes an alias and retires its owned definition when no other alias uses it.

        Alias removal and the last-alias check use the instance lock; native removal runs
        outside it. Borrowed definitions and already built tools remain live. A failed
        native removal propagates and stays recorded for the manager's cleanup retry.

        Args:
            name (str): The registered name of the tool type to unregister.

        Raises:
            TypeError: If the name is not a string.
            KeyError: If no tool is registered with the given name.
            RuntimeError: If this Toolbox has already been cleaned.
        """
        self.check_cleaned()
        if not isinstance(name, str):
            self._logger.error(f"Attempted to unregister tool with invalid name type: {type(name).__name__}", _manual_stack=True, _method_name="unregister_tool", exc_info=True)
            raise TypeError(f"Tool name must be a string, got {type(name).__name__}.")
        with self._lock:
            removed = self._registry.pop(name, None)
            orphaned = removed is not None and not any(item is removed for item in self._registry.values())
        if removed is None:
            raise KeyError(f"No tool registered with name '{name}'.")
        if orphaned:
            self._definitions.release(removed.__name__)

    def build_tool(self, name: str, *, conduit: Conduit, **kwargs: Any) -> Optional[BaseTool]:
        """
        Meld a fresh tool through the requesting scope using its registered class definition.

        The caller owns the returned tool. Native construction is untracked, so removing
        aliases or cleaning the scope/Toolbox never disposes it. Arguments are passed as
        the meld override, retaining supplied object identities. Read the alias once;
        no Toolbox lock spans native resolution or a user constructor.

        Args:
            name (str): The name or alias of the tool type to build.
            conduit: Existing requesting scope with access to the framework definitions.
                This is a required control argument, never forwarded to the tool constructor.
            **kwargs: Arbitrary keyword arguments to be passed to the
                      constructor of the tool class.

        Returns:
            Optional[BaseTool]: An instantiated tool object if the
                                `name` is registered; otherwise, `None`.
        Raises:
            TypeError: If the registered class cannot be instantiated with the
                       provided keyword arguments, or if the built object is not a BaseTool.
            Exception: Any other constructor failure propagates unchanged.
            RuntimeError: If this Toolbox has already been cleaned.
        """
        self.check_cleaned()
        tool_class = self._registry.get(name)
        if tool_class is None:
            return None
        spell_id = self._definitions.definition_id(tool_class)
        try:
            # Native construction receives the caller's original arguments as overrides.
            instance = conduit.meld(spell_id=spell_id, override=kwargs)
        except TypeError as error:
            raise self._invalid_arguments(name, tool_class, error) from error
        except MeldExecutionError as error:
            if error.inner is None:
                raise
            if isinstance(error.inner, TypeError):
                raise self._invalid_arguments(name, tool_class, error.inner) from error
            raise error.inner from error
        from melder_ops.command_center.spectrum.toolbox.base import BaseTool
        if not isinstance(instance, BaseTool):
            self._logger.error(f"Factory for tool '{name}' did not return a BaseTool instance.", exc_info=True, _manual_stack=True, _method_name="build_tool")
            raise TypeError(f"Factory for tool '{name}' did not return a BaseTool instance.")
        return instance

    def _invalid_arguments(self, name: str, tool_class: Type[BaseTool], error: TypeError) -> TypeError:
        """Preserve Toolbox's constructor-argument diagnostic across the native boundary.

        Args:
            name: Alias selected by the caller.
            tool_class: Admitted class whose constructor refused the inputs.
            error: Original constructor TypeError, including one unwrapped from Melder.

        Returns:
            The logged TypeError to raise with its native or direct cause preserved.
        """
        message = (f"Failed to build tool '{name}'. "
                   f"Constructor of '{tool_class.__name__}' received invalid arguments: {error}")
        self._logger.error(message, exc_info=True, _manual_stack=True, _method_name="build_tool")
        return TypeError(message)

    def list_tools(self) -> list[str]:
        """
        Returns a list of all registered tool names.

        This provides a snapshot of the currently available tool types
        that can be instantiated using the `build_tool` method.

        Snapshot read using plain dictionary access without acquiring the instance lock.

        Returns:
            list[str]: A list of strings, where each string is the name of a registered tool.

        Raises:
            RuntimeError: If this Toolbox has already been cleaned.
        """
        self.check_cleaned()
        return list(self._registry.keys())
