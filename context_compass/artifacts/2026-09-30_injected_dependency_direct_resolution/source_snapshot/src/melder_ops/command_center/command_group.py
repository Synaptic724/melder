from __future__ import annotations

import threading
from melder import new_ulid
from typing import Optional, List, Any, Union, Dict, Iterable, Set, TYPE_CHECKING
from melder_ops.command_center.mission.status.status import MissionStatus
from melder_ops.concurrency.sync_types.sync_int import SyncInt
from melder_ops.command_center.activity.status.status import ActivityStatus
from melder_ops.command_center.agents.agent_types.agent import Agent
from melder_ops.synchronization.controllers.signal_controller import SignalController
from melder import Package as Pack
from melder import Cleanable
from melder_ops.utilities.general_helpers.init_helpers import InitHelpers

if TYPE_CHECKING:
    import logging
    from melder import Conduit
    from melder_ops.command_center.activity.base import BaseActivity
    from melder_ops.command_center.agent_pools.base import BaseAgentPool
    from melder_ops.command_center.command_center import CommandCenter
    from melder_ops.command_center.mission.base import BaseMission
    from melder_ops.command_center.spectrum.actions.action.action import Action as BaseAction
    from melder_ops.command_center.spectrum.interchange.base_connector import BaseConnector
    from melder_ops.command_center.spectrum.iris.channel_logger import ChannelLogger
    from melder_ops.command_center.spectrum.toolbox.base import BaseTool
    from melder_ops.command_center.strategic_command.strategic_command import StrategicCommand


# region CommandGroup
class CommandGroup(Cleanable):
    """
    CommandGroup
    ------------
    A container object that encapsulates a logical group of agents and activities under a single name,
    with its own lifecycle limits, registries, and behavior.

    It supports lifecycle operations like start, pause, cancel, deploy, and shutdown across all
    managed agents and activities. Integrates with the CommandCenter and SignalController for orchestration.

    Parameters:
    -----------
    command_center : CommandCenter
        The orchestrator that owns this group and handles agent/activity creation.
    group_name : str
        A unique name for identifying this group within the system.
    group_max_agents : int
        The maximum number of agents allowed to operate simultaneously within this group.
    group_type : Optional[str]
        An optional classification for the group (e.g., "ETL", "Modeling", etc.).
    conduit : Conduit
        Required native child scope supplied by the creating center or direct caller.
        The group adopts it on successful construction and retires it after members.
        Access through `conduit` is borrowed; callers must not retire it independently.
    """

    def __init__(self, command_center: CommandCenter, group_name: str, group_max_agents: int, total_agent_count: SyncInt,
                 external_signal_controller: Optional[SignalController] = None,
                 logger: Optional[Union[logging.Logger, ChannelLogger]] = None, group_type: str = None,
                 *, conduit: Conduit) -> None:
        """
        Initializes a new CommandGroup instance.

        A CommandGroup is a container that manages a coordinated group of agents and activities.
        It enforces its own maximum agent count (`max_agents`) and provides lifecycle operations
        and centralized control for orchestration, diagnostics, and shutdown.

        Parameters:
        -----------
        command_center : CommandCenter
            The controlling CommandCenter instance responsible for creating agents and activities.
            This reference is retained for future delegation of creation or orchestration tasks.

        group_name : str
            A unique name for this group, used for identification and lookup in higher-level registries.

        group_max_agents : int
            The maximum number of concurrent agents that can operate under this group.
            Acts as an internal quota to prevent overload and manage concurrency.

        group_type : Optional[str]
            An optional tag or label that classifies this group (e.g., "etl", "analytics", "simulation").
            Can be used for filtering, scheduling preferences, or display purposes.

        total_agent_count : SyncInt
            Borrowed center-wide counter; group cleanup does not dispose it.
        external_signal_controller : Optional[SignalController]
            Borrowed controller receiving registration and cleanup notifications.
        logger : Optional[Union[logging.Logger, ChannelLogger]]
            Explicit logger to wrap or adopt; absent input uses the hosted logging path.
        conduit : Conduit
            Required child of the center's native scope. None is refused before any
            local resource is initialized. Direct callers allocate it themselves.

        Lifecycle:
        ----------
        The center remains borrowed. Scope custody transfers only after the existing
        initialization succeeds; a failed constructor leaves native release with its
        caller. Explicit cleanup stops members, retires the scope and releases the
        logger last. A detached group must be cleaned before its center; late cleanup
        only drops the native handle if that center already retired its descendants.

        Raises:
        -------
        TypeError
            conduit is None; no identity, logger or child resource has been created.
        Exception
            Existing logger, controller or maintenance initialization fails. The
            creating caller remains responsible for the untransferred native scope.


        Attributes:
        -----------
        id : str
            A ULID-based unique identifier for this group instance.

        _agent_count : SyncInt
            A thread-safe counter tracking the number of active agents currently in the group.

        _group_max_agents : SyncInt
            The ceiling on agent count; enforced via `add_agent()` and respected during orchestration.

        _agents : Dict[str, Agent]
            Agent membership dictionary; compound mutations use the group lock.

        _activities : Dict[str, BaseActivity]
            Activity membership dictionary used by explicit member shutdown.

        _signal_controllers : Dict[str, SignalController]
            Registry of all signal controllers used by activities or agents in this group.
        """
        if conduit is None:
            raise TypeError("CommandGroup requires a conduit; pass its native asset scope.")
        super().__init__()
        self._id = new_ulid()
        self._lock: threading.RLock = threading.RLock()

        self.name = group_name
        self.type = group_type

        if logger is None:
            self._logger = InitHelpers.resolve_channel_logger(self, system_groups=["command_center","command_group"], groups=["command_center", "organization", "lifecycle", "signal_controller"], channels="system")
        else:
            # If a logger is provided, use it.
            self._logger = InitHelpers.resolve_safe_logger(logger)

        # --- External Controller Integration ---
        self._external_signal_controller = external_signal_controller
        if self._external_signal_controller:
            try:
                self._external_signal_controller.register(self)
                self._logger.info(f"CommandCenter '{self._id}' registered with external SignalController.", _manual_stack=True, _method_name="__init__")
            except Exception as e:
                self._logger.warning(f"Failed to register CommandCenter with external SignalController: {e}", exc_info=True, _manual_stack=True, _method_name="__init__")

        self._command_center: CommandCenter = command_center  # Reference to its creator for delegation

        # Internal registries for members assigned to this group
        self._agents: Dict[str, Agent] = {}
        self._signal_controllers: Dict[str, SignalController] = {}
        self._missions: Dict[str, BaseMission] = {}  # Missions are used to coordinate activities
        self._activities: Dict[str, BaseActivity] = {}
        self._agent_pools: Dict[str, BaseAgentPool] = {}  # UUID and Agent Container

        # --- Lifecycle Management ---
        self._strategic_command: StrategicCommand = self._command_center._strategic_command
        self._cleanup_tracker = command_center._cleanup_tracker

        if self._command_center.config.maintenance_group_name != group_name:
            self._maintenance_pool: BaseAgentPool = command_center._get_maintenance_pool()
        else:
            self._maintenance_pool = None

        # Counters
        self._agent_count = SyncInt(initial=0)
        self._total_agent_count: SyncInt = total_agent_count
        self._group_max_agents = SyncInt(initial=group_max_agents)
        self._conduit = conduit

#region Destructor
    def cleanup(self) -> None:
        """
        Disposes of the CommandGroup by orchestrating a cascading cleanup of its resources.
        This method is resilient, thread-safe, and idempotent.

        Existing member shutdown and registry/counter cleanup run under the group
        lock. Once terminal, native scope retirement runs outside that lock before
        logger cleanup. If the borrowed center is already cleaned, its descendant
        scopes may have been recycled; only drop the old native handle in that case.

        Raises:
            Exception: Native retirement fails. The group remains terminal and
                logger cleanup is still attempted; the native parent retains failed
                state for its own cleanup. Repeated group cleanup is a no-op.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            if self._logger is not None:
                self._logger.warning(
                    f"cleaning CommandGroup '{self.name}'...",
                    _manual_stack=True, _method_name="cleanup"
                )

            # --- Phase 1: Clean up internal components ---
            self._cleanup_components()

        # --- Phase 2: Clean up core components after the lock is released ---
            self._cleaned = True
        self._cleanup_core()


    def _cleanup_components(self) -> None:
        """
        Shut down members, clear plain registries and retire owned counters under the group lock.

        Preserve shutdown_all_members delegation and its member ownership. Dictionary
        clearing only releases membership references; it does not call member cleanup a
        second time. The owned agent-count and capacity SyncInt objects are cleaned
        independently, while the shared total-agent counter remains borrowed.

        Failure and lifecycle:
            Existing shutdown/counter failures are logged without preventing later
            cleanup. External controller notification/unregistration stays best-effort.
            The outer cleanup deletes references and retires the logger afterward.

        Returns:
            None. Called only by the admitted cleanup while its instance lock is held.
        """
        # 1) Gracefully shut down all members (best-effort)
        try:
            self.shutdown_all_members()
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"An error occurred during shutdown_all_members for group '{self.name}': {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_components"
                )

        # 2) Clear ordinary membership dictionaries after their existing member shutdown.
        self._missions.clear()
        self._activities.clear()
        self._signal_controllers.clear()
        self._agent_pools.clear()
        self._agents.clear()

        # 3) Retire the two owned counters independently; the shared total is borrowed.
        try:
            self._agent_count.cleanup()
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"Error cleaning up Agent Count in group '{self.name}': {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_components"
                )
        try:
            self._group_max_agents.cleanup()
        except Exception as e:
            if self._logger is not None:
                self._logger.error(
                    f"Error cleaning up Group Max Agents in group '{self.name}': {e}",
                    exc_info=True, _manual_stack=True, _method_name="_cleanup_components"
                )

        # 4) Handle external controller unregistration (best-effort)
        if self._external_signal_controller is not None:
            try:
                self._external_signal_controller.notify(self._id, "cleaned")
            except Exception:
                # ignore notify failures during teardown
                pass
            try:
                self._external_signal_controller.unregister(self._id)
            except Exception:
                # ignore unregister failures during teardown
                pass


    def _cleanup_core(self) -> None:
        """
        Release local references, retire the native scope and clean the logger last.

        Called outside the group lock after explicit member shutdown and terminal
        admission. Keep the borrowed center until native retirement checks whether
        ancestor cleanup already ended this scope's lease. Native failure propagates
        after the center reference and logger have been released.
        """
        # --- Drop All Owned Component References ---
        # Verified before converting: CommandGroup has no class-level defaults, so none
        # of these can silently fall back to a class attribute. The four unguarded
        # readers (_agent_creation_check, _eligibility_check, _validate_pool_tags,
        # create_agent) are all reached through check_cleaned()-guarded public entry
        # points and none are called from the teardown path.
        del self._signal_controllers
        del self._activities
        del self._missions
        del self._agents
        del self._agent_pools
        del self._agent_count
        del self._group_max_agents
        del self._external_signal_controller
        del self._strategic_command
        del self._cleanup_tracker
        del self._total_agent_count
        del self._maintenance_pool

        # --- Final Teardown of the Lock ---
        del self._lock

        try:
            self._cleanup_conduit()
        finally:
            del self._command_center
            # --- The Logger is the Very Last Thing to Go ---
            if self._logger is not None:
                try:
                    self._logger.info(
                        f"CommandGroup '{self.name}' cleaned.",
                        _manual_stack=True, _method_name="_cleanup_core"
                    )
                    # Probe retained: this logger may be a SafeLogger (resolve_safe_logger
                    # branch in __init__), which is NOT Cleanable and defines no cleanup().
                    if hasattr(self._logger, "cleanup"):
                        try:
                            self._logger.cleanup()
                        except Exception:
                            # per guidance: swallow any exception from logger cleanup
                            pass
                finally:
                    del self._logger

    def _cleanup_conduit(self) -> None:
        """End this group's native lease and drop its handle even if retirement fails.

        The borrowed center must still be retained. If it is already cleaned,
        ancestor retirement may have reassigned the pooled shell; do not clean
        that later owner's scope. Otherwise use Melder's public cleanup and let
        a native failure propagate, with failed state still owned by the parent.
        """
        try:
            if not self._command_center.cleaned:
                self._conduit.cleanup()
        finally:
            del self._conduit

    @property
    def conduit(self) -> Conduit:
        """Borrow this live group's native scope for scoped asset construction.

        The group owns retirement. Keep both the group and its center alive while
        using the returned handle; do not clean it independently. Removing group
        membership with cleanup=False does not move its scope to another parent.

        Returns:
            Conduit: The scope adopted at successful construction.

        Raises:
            RuntimeError: This group has already been cleaned.
        """
        self.check_cleaned()
        return self._conduit

    #region Lifecycle Control

    def shutdown_all_members(self):
        """
        Gracefully shut down *everything* in this CommandGroup by calling the
        specialized shutdown helpers in the correct order.

        Order:
            1.  Agent-pools       (they typically clean up the agents they own)
            2.  Missions          (high-level orchestrators of activities)
            3.  Activities        (so no agents are still working on them)
            4.  Any agents still registered directly with the group
            5.  Signal-controllers (communication buses)
        """
        self.check_cleaned()
        self._logger.info(f"Initiating full member shutdown for CommandGroup '{self.name}'...", _manual_stack=True, _method_name="shutdown_all_members")
        self._shutdown_missions()
        self._shutdown_activities()
        self._shutdown_agent_pools()
        #self._shutdown_agents()
        self._shutdown_signal_controllers()

        self._logger.info(f"Full member shutdown completed for CommandGroup '{self.name}'.", _manual_stack=True, _method_name="shutdown_all_members")

    def _shutdown_agent_pools(self):
        """
        Shuts down all agent pools in the group.
        """
        if not self._agent_pools: return
        self._logger.info(f"Shutting down all AgentPools in CommandGroup '{self.name}'...", _manual_stack=True, _method_name="_shutdown_agent_pools")
        for pool in list(self._agent_pools.values()):  # copy protects against mutation
            try:
                pool.cleanup()
                self._logger.info(f"Cleaned up pool '{pool.id}'.")
            except Exception as e:
                self._logger.error("Error cleaning AgentPool: %s", e, exc_info=True, _manual_stack=True, _method_name="_shutdown_agent_pools")
        self._logger.info(f"Finished shutting down AgentPools.", _manual_stack=True, _method_name="_shutdown_agent_pools")

    def _shutdown_missions(self):
        """
        Shuts down all missions in the group.
        """
        if not self._missions: return
        self._logger.info(f"Shutting down all Missions in CommandGroup '{self.name}'...", _manual_stack=True, _method_name="_shutdown_missions")
        for mission in list(self._missions.values()):
            try:
                mission.cleanup()
                self._logger.info(f"Cleaned up mission '{mission.id}'.", _manual_stack=True, _method_name="_shutdown_missions")
            except Exception as e:
                self._logger.error("Error shutting down Mission: %s", e, exc_info=True, _manual_stack=True, _method_name="_shutdown_missions")
        self._logger.info(f"Finished shutting down Missions.", _manual_stack=True, _method_name="_shutdown_missions")

    def _shutdown_activities(self):
        """
        Shuts down all activities in the group.
        """
        if not self._activities: return
        self._logger.info(f"Shutting down all Activities in CommandGroup '{self.name}'...", _manual_stack=True, _method_name="_shutdown_activities")
        for activity in list(self._activities.values()):
            try:
                activity.cleanup()
                self._logger.info(f"Cleaned up activity '{activity.id}'.", _manual_stack=True, _method_name="_shutdown_activities")
            except Exception as e:
                self._logger.error("Error shutting down Activity: %s", e, exc_info=True, _manual_stack=True, _method_name="_shutdown_activities")
        self._logger.info(f"Finished shutting down Activities.", _manual_stack=True, _method_name="_shutdown_activities")

    def _shutdown_agents(self):
        """
        Shuts down all agents still registered directly with the group.

        Pool-owned agents are normally already cleaned by `_shutdown_agent_pools`
        (they share this group's `_agents` registry), so this pass skips any agent
        whose `_cleaned` flag is set and only cleans stragglers registered outside
        a pool. Re-enabled per finding #54: while this call was commented out of
        `shutdown_all_members`, directly-registered agents were dropped uncleaned
        at group shutdown, contradicting step 4 of its documented order.
        """
        if not self._agents: return
        self._logger.info(f"Shutting down all Agents in CommandGroup '{self.name}'...", _manual_stack=True, _method_name="_shutdown_agents")
        for agent in list(self._agents.values()):
            try:
                if agent._cleaned:
                    continue
                agent.cleanup()
                self._logger.info(f"Cleaned up agent '{agent._id}'.", _manual_stack=True, _method_name="_shutdown_agents")
            except Exception as e:
                self._logger.error("Error shutting down Agent: %s", e, exc_info=True, _manual_stack=True, _method_name="_shutdown_agents")
        self._logger.info(f"Finished shutting down Agents.", _manual_stack=True, _method_name="_shutdown_agents")

    def _shutdown_signal_controllers(self):
        """
        Shuts down all signal controllers in the group.
        """
        if not self._signal_controllers: return
        self._logger.info(f"Shutting down all SignalControllers in CommandGroup '{self.name}'...", _manual_stack=True, _method_name="_shutdown_signal_controllers")
        for controller in list(self._signal_controllers.values()):
            try:
                controller.cleanup()
                self._logger.info(f"Cleaned up SignalController '{controller.name}'.", _manual_stack=True, _method_name="_shutdown_signal_controllers")
            except Exception as e:
                self._logger.error(f"Error shutting down SignalController '{controller.name}': {e}", exc_info=True, _manual_stack=True, _method_name="_shutdown_signal_controllers")
        self._logger.info(f"Finished shutting down SignalControllers.", _manual_stack=True, _method_name="_shutdown_signal_controllers")

    #endregion Lifecycle Control
#endregion Destructor

    @property
    def id(self) -> str:
        """
        The unique identifier for this BaseAgent instance, conforming to SignalController's contract.
        """
        return self._id

#region Signal Controller Integration

    def _notify(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """
        Helper to send notifications to the external signal controller if it exists.
        This allows the CommandCenter to be observable.
        """
        self.check_cleaned()
        if self._external_signal_controller and not self._external_signal_controller._cleaned:
            try:
                self._external_signal_controller.notify(self._id, event_type, data)
            except Exception as e:
                self._logger.error(f"Error notifying external SignalController: {e}", exc_info=True, _manual_stack=True, _method_name="_notify")

    def set_external_controller(self, controller: SignalController):
        """
        Sets an external SignalController to manage this CommandCenter.
        This allows the CommandCenter to be controlled remotely.
        """
        self.check_cleaned()
        if self._external_signal_controller:
            raise RuntimeError("External SignalController is already set.")
        if not isinstance(controller, SignalController):
            raise TypeError("Expected a SignalController instance.")
        self._external_signal_controller = controller
        try:
            self._external_signal_controller.register(self)
            self._logger.info(f"CommandCenter '{self._id}' registered with external SignalController.")
        except Exception as e:
            self._logger.warning(f"Failed to register CommandCenter with external SignalController: {e}",
                                 exc_info=True, _manual_stack=True, _method_name="set_external_controller")

    def _get_object_details(self) -> Dict[str, Any]:
        """
        Return a remotely-invocable command map for this CommandGroup.

        Keep this list in sync whenever you add / rename public methods,
        otherwise SignalController‑level introspection will break.
        """
        self.check_cleaned()

        return {
            "name": "CommandGroup",
            "commands": {
                # ---- Group Lifecycle & Introspection ----
                "shutdown_all_members": self.shutdown_all_members,
                "get_status_summary": self.get_status_summary,
                "increase_command_group_max_agents": self.increase_command_group_max_agents,
                "decrease_command_group_max_agents": self.decrease_command_group_max_agents,

                # ---- Agent & Agent Pool Management ----
                "create_agent_pool": self.create_agent_pool,
                "remove_agent_pool": self.remove_agent_pool,
                "find_agent_pool_by_name": self.find_agent_pool_by_name,
                "find_agent_pool_by_id": self.find_agent_pool_by_id,
                "list_agent_pools": self.list_agent_pools,
                "get_agent_pools_by_tags": self.get_agent_pools_by_tags,
                "create_agent": self.create_agent,
                "create_agents": self.create_agents,
                "add_agent_to_pool": self.add_agent_to_pool,
                "list_agents": self.list_agents,

                # ---- Activity Management ----
                "create_activity": self.create_activity,
                "remove_activity": self.remove_activity,
                "start_all_activities": self.start_all_activities,
                "pause_all_activities": self.pause_all_activities,
                "resume_all_paused_activities": self.resume_all_paused_activities,
                "cancel_all_activities": self.cancel_all_activities,
                "deploy_all_pending_activities": self.deploy_all_pending_activities,
                "list_activities": self.list_activities,

                # ---- Mission Management ----
                "create_mission": self.create_mission,
                "remove_mission": self.remove_mission,
                "pause_all_missions": self.pause_all_missions,
                "resume_all_paused_missions": self.resume_all_paused_missions,
                "cancel_all_missions": self.cancel_all_missions,
                "list_missions": self.list_missions,

                # ---- SignalController Management ----
                "add_signal_controller": self.add_signal_controller,
                "remove_signal_controller": self.remove_signal_controller,
                "get_signal_controller": self.get_signal_controller,
                "find_controller_by_name": self.find_controller_by_name,
                "list_signal_controllers": self.list_signal_controllers,
                "wire_controller_to_activity": self.wire_controller_to_activity,
                "wire_controller_to_agent": self.wire_controller_to_agent,
                "wire_controller_to_all_members": self.wire_controller_to_all_members,
                "subscribe_to_event_on_member": self.subscribe_to_event_on_member,
                "unsubscribe_from_event_on_member": self.unsubscribe_from_event_on_member,
                "add_hook_to_internal_controller": self.add_hook_to_internal_controller,
                "invoke_on_internal_controller": self.invoke_on_internal_controller,
                "unregister_object_from_internal_controller": self.unregister_object_from_internal_controller,

                # ---- Work & Strategy Execution ----
                "create_request": self.create_request,
                "create_requests": self.create_requests,
                "execute_strategy": self.execute_strategy,

                # ---- Resource Access ----
                "get_interchange_connector": self.get_interchange_connector,
                "build_tool": self.build_tool,
                "get_action": self.get_action,
            }
        }

#endregion Signal Controller Integration
# region SignalController Integration Wiring

    def add_signal_controller(self, name: str, controller: Optional[SignalController] = None,
                              logger: logging.Logger = None) -> SignalController:
        """
        Adds a new SignalController to the CommandCenter's management. If an existing
        controller instance is not provided, a new one is created. This allows the
        CommandCenter to manage multiple, named communication buses.

        Args:
            name (str): A unique name to identify this SignalController.
            controller (Optional[SignalController]): An existing SignalController instance.
                                                     If None, a new one will be created.
            logger (Optional[logging.Logger]): An optional logger for the SignalController.

        Returns:
            SignalController: The newly added or created SignalController instance.

        Raises:
            ValueError: If a SignalController with the same name already exists.
        """
        self.check_cleaned()
        with self._lock:
            existing = self.find_controller_by_name(name)
            if existing:
                self._logger.warning(
                    f"SignalController with name '{name}' already exists in command group '{self.name}'. Returning existing controller.")
                return existing
            else:
                new_controller = controller or SignalController(controller_name=name, logger=logger)
                new_controller._group_name = self.name
                new_controller._group_id = self._id
                self._signal_controllers[new_controller._id] = new_controller
                self._logger.info(f"Added SignalController: '{name}'")
                self._notify('SIGNAL_CONTROLLER_ADDED', {'controller_name': name, 'command_group': self._id,
                                                         'command_group_name': self.name})
                return new_controller

    def find_controller_by_name(self, name: str) -> Optional[SignalController]:
        """
        Finds a SignalController by its name within the specified command group.

        Args:
            name (str): The name of the SignalController to find.

        Returns:
            List[SignalController]: The SignalController instance if found, or None if not found.
        """
        self.check_cleaned()
        returnlist = []
        for controller in self._signal_controllers.values():
            if controller.name == name:
                returnlist.append(controller)

        if returnlist:
            # If multiple controllers with this name exist, raise an error
            if len(returnlist) > 1:
                self._logger.error(
                    f"Multiple SignalControllers with the name '{name}' exist in command group '{self.name}'. Please use a unique name.",
                    _manual_stack=True, _method_name="_internal_register", exec_info=True
                )
                raise ValueError(
                    f"Multiple SignalControllers with the name '{name}' exist in command group '{self.name}'. Please use a unique name.")
        controller = returnlist[0] if returnlist else None
        return controller

    def remove_signal_controller(self, signal_controller: SignalController, dispose: bool = True) -> bool:
        """
        Removes a SignalController from the CommandCenter.

        Args:
            signal_controller (SignalController): The SignalController instance to remove.
            dispose (bool): If True, the SignalController's cleanup() method will be
                            called upon removal. Defaults to True.

        Returns:
            bool: True if the controller was found and removed, False otherwise.
        """
        self.check_cleaned()
        if signal_controller._id in self._signal_controllers:
            controller = self._signal_controllers.pop(signal_controller._id)
            name = controller.name
            self._logger.info(f"Removed SignalController: '{name}'")
            self._notify('SIGNAL_CONTROLLER_REMOVED',
                         {'controller_name': name, 'command_group': self._id, 'command_group_name': self.name})
            controller._group_name = None
            controller._group_id = None
            if dispose:
                try:
                    controller.cleanup()
                except Exception as e:
                    self._logger.error(f"Error cleaning up SignalController '{name}': {e}", exc_info=True, _manual_stack=True, _method_name="remove_signal_controller")
            return True
        self._logger.warning(f"SignalController '{signal_controller.name}' not found in any command group.")
        return False

    def get_signal_controller(self, name: str) -> Optional[SignalController]:
        """
        Retrieves a SignalController from this group's local registry by its assigned name.

        Args:
            name (str): The name of the controller to retrieve.

        Returns:
            Optional[SignalController]: The controller instance, or None if not found in this group.
        """
        self.check_cleaned()

        for controller in self._signal_controllers.values():
            if controller.name == name:
                return controller
        self._logger.warning(f"SignalController '{name}' not found in group '{self.name}'.")
        return None

    def wire_controller_to_activity(self, controller_name: str, activity_id: str):
        """
        Attaches a SignalController managed by this group to a specific activity also within this group.
        This allows the activity to be observed and controlled via that controller's event bus.

        Args:
            controller_name (str): The name of the SignalController to attach.
            activity_id (str): The ID of the target activity.
        """
        self.check_cleaned()

        controller = self.get_signal_controller(controller_name)
        if not controller:
            self._logger.error(f"SignalController '{controller_name}' not found in any command group.", _exc_info=True, _manual_stack=True, _method_name="wire_controller_to_activity")
            raise ValueError(f"Controller '{controller_name}' not found in group '{self.name}'.")

        activity = self._activities.get(activity_id)
        if not activity:
            self._logger.error(f"Activity '{activity_id}' not found in group '{self.name}'.", _exc_info=True, _manual_stack=True, _method_name="wire_controller_to_activity")
            raise ValueError(f"Activity '{activity_id}' not found in group '{self.name}'.")

        # This assumes the BaseActivity has a method to accept a controller
        if hasattr(activity, 'set_external_controller'):
            activity.set_external_controller(controller)
        else:
            raise NotImplementedError(
                "The 'BaseActivity' class does not yet support the 'set_external_controller' method.")

    def wire_controller_to_agent(self, controller_name: str, agent_id: str):
        """
        Attaches a SignalController managed by this group to a specific agent also within this group.
        This allows the agent to be observed and controlled via that controller's event bus.

        Args:
            controller_name (str): The name of the SignalController to attach.
            agent_id (str): The ID of the target agent.
        """
        self.check_cleaned()

        controller = self.get_signal_controller(controller_name)
        if not controller:
            self._logger.error(f"SignalController '{controller_name}' not found in any command group.", _exc_info=True, _manual_stack=True, _method_name="wire_controller_to_agent")
            raise ValueError(f"Controller '{controller_name}' not found in group '{self.name}'.")

        agent = self._agents.get(agent_id)
        if not agent:
            self._logger.error(f"Agent '{agent_id}' not found in group '{self.name}'.", _exc_info=True, _manual_stack=True, _method_name="wire_controller_to_agent")
            raise ValueError(f"Agent '{agent_id}' not found in group '{self.name}'.")
        agent.set_external_controller(controller)

    def wire_controller_to_all_members(self, controller_name: str):
        """
        Wires a specified SignalController to ALL current activities and agents in this group.
        This is a powerful convenience method for establishing a universal communication bus for the group's workflow.

        Args:
            controller_name (str): The name of the SignalController to attach to all members.
        """
        self.check_cleaned()

        for activity_id in list(self._activities.keys()):
            self.wire_controller_to_activity(controller_name, activity_id)

        for agent_id in list(self._agents.keys()):
            self.wire_controller_to_agent(controller_name, agent_id)

    def subscribe_to_event_on_member(self, controller_name: str, object_id: str, event_type: str, callback: Pack):
        """
        Subscribes a callback to an event on a specific object managed by an internal SignalController.

        This method acts as a gateway, finding the specified internal controller by name and
        registering the subscription.

        Args:
            controller_name (str): The name of the internal SignalController to use.
            object_id (str): The ID of the object emitting the event.
            event_type (str): The name of the event to subscribe to (e.g., 'COMPLETED').
            callback (Callable): The function to call when the event occurs.

        Raises:
            ValueError: If no controller with the given name is managed by this group.
        """
        self.check_cleaned()
        Pack.verify(callback)
        controller = self.get_signal_controller(controller_name)
        if not controller:
            self._logger.error(f"SignalController '{controller_name}' not found in any command group.", _exc_info=True, _manual_stack=True, _method_name="subscribe_to_event_on_member")
            raise ValueError(f"No SignalController with the name '{controller_name}' is managed by this CommandGroup.")
        controller.subscribe(object_id, event_type, callback)


    def unsubscribe_from_event_on_member(self, controller_name: str, object_id: str, event_type: str,
                                         callback: Pack) -> None:
        """
        Unsubscribes a callback from an event on a specific object managed by an internal SignalController.

        This is crucial for resource management, allowing for the cleanup of event listeners
        when they are no longer needed.

        Args:
            controller_name (str): The name of the internal SignalController to use.
            object_id (str): The ID of the object that was being observed.
            event_type (str): The name of the event to unsubscribe from.
            callback (Callable): The specific function that was previously subscribed.

        Raises:
            ValueError: If no controller with the given name is managed by this group.
        """
        self.check_cleaned()
        Pack.verify(callback)
        controller = self.get_signal_controller(controller_name)
        if not controller:
            self._logger.error(f"SignalController '{controller_name}' not found in any command group.", _exc_info=True, _manual_stack=True, _method_name="unsubscribe_from_event_on_member")
            raise ValueError(f"No SignalController with the name '{controller_name}' is managed by this CommandGroup.")
        controller.unsubscribe(object_id, event_type, callback)

    def add_hook_to_internal_controller(self, controller_name: str, hook_type: str, callback: Pack):
        """
        Attaches a pre- or post-invocation hook to an internal SignalController for auditing or monitoring.

        This method finds the specified internal controller by name and adds the provided
        callback as a hook.

        Args:
            controller_name (str): The name of the controller to attach the hook to.
            hook_type (str): The type of hook, must be either 'pre_invoke' or 'post_invoke'.
            callback (Callable): The hook function to add.

        Raises:
            ValueError: If the controller name is not found or the hook_type is invalid.
        """
        self.check_cleaned()
        Pack.verify(callback)
        controller = self.get_signal_controller(controller_name)
        if not controller:
            raise ValueError(f"No SignalController with the name '{controller_name}' is managed by this CommandGroup.")

        if hook_type == 'pre_invoke':
            controller.add_pre_invoke_hook(callback)
        elif hook_type == 'post_invoke':
            controller.add_post_invoke_hook(callback)
        else:
            self._logger.error(f"Invalid hook_type '{hook_type}' specified. Must be 'pre_invoke' or 'post_invoke'.", _exc_info=True, _manual_stack=True, _method_name="add_hook_to_internal_controller")
            raise ValueError("hook_type must be either 'pre_invoke' or 'post_invoke'.")

    def invoke_on_internal_controller(self, controller_name: str, object_id: str, command: str, *args, **kwargs) -> Any:
        """
        Invokes a command on an object registered with a specific internal SignalController.

        Args:
            controller_name (str): The name of the internal SignalController to use.
            object_id (str): The ID of the target object on that controller.
            command (str): The name of the command to execute.
            *args: Positional arguments to pass to the command.
            **kwargs: Keyword arguments to pass to the command.

        Returns:
            Any: The result from the invoked command.

        Raises:
            ValueError: If no controller with the given name is managed by this group.
        """
        self.check_cleaned()
        controller = self.get_signal_controller(controller_name)
        if not controller:
            self._logger.error(f"SignalController '{controller_name}' not found in any command group.", _exc_info=True, _manual_stack=True, _method_name="invoke_on_internal_controller")
            raise ValueError(f"No SignalController with the name '{controller_name}' is managed by this CommandGroup.")
        return controller.invoke(object_id, command, *args, **kwargs)

    def unregister_object_from_internal_controller(self, controller_name: str, object_id: str):
        """
        Explicitly unregisters an object from an internal SignalController.

        This removes an object from the controller's management, stopping all future
        invocations and event subscriptions related to it through that controller.

        Args:
            controller_name (str): The name of the internal SignalController.
            object_id (str): The ID of the object to unregister.

        Raises:
            ValueError: If no controller with the given name is managed by this group.
        """
        self.check_cleaned()
        controller = self.get_signal_controller(controller_name)
        if not controller:
            raise ValueError(f"No SignalController with the name '{controller_name}' is managed by this CommandGroup.")
        controller.unregister(object_id)


#endregion SignalController Integration & Wiring
#region Agent Pool Management

    def create_agent_pool(self,
                          agent_pool_template_name: str = "general",
                          initial_capacity: int = 0,
                          agent_pool_name: Optional[str] = None,
                          agent_template_name: str = "general",
                          logger: Optional[Union[logging.Logger, ChannelLogger]] = None,
                          **kwargs) -> Optional[BaseAgentPool]:
        """
        Builds, registers, and optionally populates a new agent pool.

        This method prepares the necessary arguments for the agent pool's constructor,
        including the command_group context and logger, before calling the builder.

        Args:
            agent_pool_template_name (str): The symbolic name of the agent pool template to use.
            initial_capacity (int): If > 0, the pool will be immediately populated
                                    with this many agents. Defaults to 0.
            agent_pool_name (str, optional): A specific, human-readable name for this pool instance.
                                             If not provided, the pool may remain unnamed or use a default.
            agent_template_name (str): The template for the agents that will populate the pool.
                                       Defaults to "general".
            logger (logging.Logger, optional): A specific logger instance for the agent pool.
            **kwargs: Additional keyword arguments for the agent pool's constructor.

        Returns:
            The created agent pool, or None if creation fails. On a populate
            failure the just-registered pool is rolled back (unregistered and
            cleaned) before returning None, so no caller can obtain a
            half-initialized pool from this group (finding #31).

        Raises:
            ValueError: If a numeric/string argument is invalid, or if
                ``agent_pool_name`` duplicates the name of a pool already
                registered in this group - pool names are contractually unique
                within a CommandGroup (see ``find_agent_pool_by_name``;
                finding #82).
        """
        self.check_cleaned()
        if not isinstance(initial_capacity, int) or initial_capacity < 0:
            raise ValueError("Initial capacity must be a non-negative integer.")
        if not isinstance(agent_pool_template_name, str) or not agent_pool_template_name:
            raise ValueError("Agent pool template name must be a non-empty string.")
        if not isinstance(agent_template_name, str) or not agent_template_name:
            raise ValueError("Agent template name must be a non-empty string.")
        if agent_pool_name is not None:
            for existing_pool in self._agent_pools.values():
                if existing_pool.pool_name == agent_pool_name:
                    self._logger.error(f"An AgentPool named '{agent_pool_name}' already exists in CommandGroup '{self.name}'.", _manual_stack=True, _method_name="create_agent_pool")
                    raise ValueError(f"An AgentPool named '{agent_pool_name}' already exists in CommandGroup '{self.name}'.")

        # --- Prepare arguments for the BaseAgentPool constructor ---
        # Start with the user-provided kwargs.
        final_kwargs = kwargs.copy()

        # Add/overwrite the essential arguments required by the BaseAgentPool constructor.
        # This ensures the context is always correctly passed down.
        final_kwargs['command_group'] = self
        final_kwargs['pool_name'] = agent_pool_name
        final_kwargs['logger'] = logger
        final_kwargs['pool_template_name'] = agent_pool_template_name
        # The pool is melded from this group's own scope (Slice 1c); the builder requires it.
        final_kwargs['conduit'] = self.conduit

        agent_pool = None
        published = False
        try:
            # Call the builder with the fully constructed arguments.
            agent_pool = self._command_center._create_agent_pool(agent_pool_template_name, **final_kwargs)
            if agent_pool:
                self._agent_pools[agent_pool._id] = agent_pool
                published = True
                self._logger.info(f"Created AgentPool '{agent_pool_name or agent_pool._id}' in group '{self.name}'.")

                if initial_capacity > 0:
                    self.create_agents(count=initial_capacity, template_name=agent_template_name, agent_pool=agent_pool, **kwargs)

                return agent_pool
        except Exception as e:
            self._logger.error(f"Failed to create agent pool of type '{agent_pool_template_name}': {e}", exc_info=True, _manual_stack=True, _method_name="create_agent_pool")
            if published:
                # Roll back the partial registration (finding #31): the pool was
                # published to self._agent_pools before its population failed, so
                # remove it and clean it up rather than leaving a half-initialized
                # pool discoverable by name/id lookups.
                del self._agent_pools[agent_pool._id]
                try:
                    agent_pool.cleanup()
                except Exception as rollback_error:
                    self._logger.error(f"Rollback cleanup of AgentPool '{agent_pool._id}' failed: {rollback_error}", exc_info=True, _manual_stack=True, _method_name="create_agent_pool")

        return None

    def add_agent_to_pool(self, agent_template_name: str, pool: BaseAgentPool, **kwargs):
        """
        Creates a new agent from a template and adds it to the specified pool.

        This method now delegates the eligibility check to the `create_agent`
        method, which uses a tag-based system to validate if the agent can
        join the target pool.

        Args:
            agent_template_name (str): The name of the agent template to use.
            pool (BaseAgentPool): The pool instance to add the agent to.
            **kwargs: Additional keyword arguments for the agent's 'onboarding' logic.

        Raises:
            TypeError: If the agent's tags are not compatible with the target pool's tags.
        """
        self.check_cleaned()

        # This method is now a clean, high-level convenience wrapper.
        self.create_agent(
            agent_pool=pool,
            template_name=agent_template_name,
            **kwargs
        )

    def remove_agent_pool(self, agent_pool: BaseAgentPool, dispose: bool = True) -> bool:
        """
        Removes an agent pool from the CommandCenter's management by searching all groups.

        Args:
            agent_pool (BaseAgentPool): The agent pool instance to remove.
            dispose (bool): If True, the agent pool will be cleaned of after removal.

        Returns:
            bool: True if the agent pool was successfully removed, False if it was not found.
        """
        self.check_cleaned()

        if agent_pool._id in self._agent_pools:
            del self._agent_pools[agent_pool._id]
            self._logger.info(f"AgentPool '{agent_pool._id}' removed from CommandGroup '{self.name}'.")
            if dispose:
                agent_pool.cleanup()
            return True
        self._logger.warning(f"AgentPool '{agent_pool._id}' not found in any CommandGroup.", _manual_stack=True, _method_name="remove_agent_pool")
        return False

    def find_agent_pool_by_name(self, pool_name: str) -> Optional[BaseAgentPool]:
        """
        Searches for an agent pool by its human-readable name within this command group.

        Note: Pool names are not guaranteed to be unique across the entire system,
        but they should be unique within a CommandGroup. This method returns the
        first match found.

        Args:
            pool_name (str): The name of the agent pool to find.

        Returns:
            Optional[BaseAgentPool]: The agent pool instance if found, otherwise None.
        """
        self.check_cleaned()
        for pool in self._agent_pools.values():
            if pool.pool_name == pool_name:
                return pool
        return None

    def list_agent_pools(self) -> List[str]:
        """
        Lists the IDs of all agent pools currently managed by this CommandGroup.

        Returns:
            List[str]: A list of unique identifiers (ULIDs) for the agent pools.
        """
        self.check_cleaned()
        return list(self._agent_pools.keys())

    def get_agent_pools_by_tags(self, required_tags: Set[str]) -> List[BaseAgentPool]:
        """
        Finds and returns all agent pools within this group that match a given set of tags.

        An agent pool is considered a match if its tag set is a superset of the
        required_tags.

        Args:
            required_tags (Set[str]): A set of tags that the pools must have.

        Returns:
            List[BaseAgentPool]: A list of agent pool instances that match the criteria.
        """
        self.check_cleaned()
        if not required_tags:
            return []

        eligible_pools = []
        for pool in self._agent_pools.values():
            if required_tags.issubset(pool.tags):
                eligible_pools.append(pool)

        return eligible_pools

    def find_agent_pool_by_id(self, pool_id: str) -> Optional[BaseAgentPool]:
        """
        Searches for an agent pool by its unique ID within a specific command group.

        Args:
            pool_id (str): The unique identifier of the agent pool.

        Returns:
            Optional[BaseAgentPool]: The agent pool instance if found, or None if not found.
        """
        self.check_cleaned()
        return self._agent_pools.get(pool_id)

    def verify_agent_pool(self, agent_pool: BaseAgentPool) -> bool:
        """
        Verifies if the provided agent pool exists in a specified command group.

        Args:
            agent_pool (BaseAgentPool): The agent pool instance to verify.

        Returns:
            bool: True if the agent pool exists, False otherwise.
        """
        self.check_cleaned()
        return agent_pool._id in self._agent_pools

    def available_headroom(self) -> int:
        """
        Returns the remaining agent capacity for this command group.

        This is a group-scoped snapshot based on the current agent count and
        this group's max agent limit. It does not consider global command center
        limits and should be treated as advisory under concurrent changes.

        Returns:
            int: Non-negative number of additional agents this group can admit.
        """
        self.check_cleaned()
        headroom = self._group_max_agents - self._agent_count
        return headroom if headroom > 0 else 0

    def increase_command_group_max_agents(self, amount: int = 1) -> int:
        """
        Increases the maximum allowed concurrent agents.

        Args:
            amount (int): The number of additional agents to allow (must be positive).

        Raises:
            ValueError: If amount is not a positive integer.
        """
        self.check_cleaned()
        if not isinstance(amount, int) or amount < 1:
            self._logger.error("Amount must be a positive integer.", _manual_stack=True, _method_name="increase_command_group_max_agents")
            raise ValueError("Amount must be a positive integer.")
        if self._command_center.get_total_agents() + amount > self._command_center._max_size:
            self._logger.error(f"Cannot increase max agents by {amount} in CommandGroup '{self.name}'. Total active agents would exceed global limit of {self._command_center._max_size}.", _manual_stack=True, _method_name="increase_command_group_max_agents")
            raise RuntimeError(f"Cannot create CommandGroup '{self.name}'. Total active agents would exceed global limit of {self._command_center._max_size}, increase new total limit to create a new group.")
        with self._lock:
            self._group_max_agents += amount
            self._notify('CONFIG_CHANGED', {'setting': 'max_agents', 'new_value': self._group_max_agents, 'command_group': self})
        self._logger.info(f"Increased max agents by {amount} in CommandGroup '{self.name}'. New limit: {self._group_max_agents}")
        return int(self._group_max_agents)

    def decrease_command_group_max_agents(self, amount: int = 1) -> int:
        """
        Decreases the maximum allowed concurrent agents.

        Args:
            amount (int): The number of agents to remove from the cap (must be positive).

        Raises:
            ValueError: If amount is not a positive integer.
            RuntimeError: If the decrease would drop this group's cap below its
                current active agent count. Because the active count is never
                negative, this guard also keeps the cap itself from ever going
                negative (finding #5: the previous guard compared against the
                CommandCenter's global ``_max_size``, so a small group cap could
                be decreased straight through zero).

        Returns:
            int: The group's new maximum agent cap.
        """
        self.check_cleaned()
        if not isinstance(amount, int) or amount < 1:
            self._logger.error("Amount must be a positive integer.", _manual_stack=True, _method_name="decrease_command_group_max_agents")
            raise ValueError("Amount must be a positive integer.")
        with self._lock:
            new_limit = int(self._group_max_agents) - amount
            if self._agent_count > new_limit:
                self._logger.error(f"Cannot decrease max agents by {amount} in CommandGroup '{self.name}'. Current active agents: {self._agent_count}, attempted new limit: {new_limit}.", _manual_stack=True, _method_name="decrease_command_group_max_agents")
                raise RuntimeError("Cannot decrease below current active agent count.")
            self._group_max_agents -= amount
            self._notify('CONFIG_CHANGED', {'setting': 'max_agents', 'new_value': self._group_max_agents, 'command_group': self._id})
        self._logger.info(f"Decreased max agents by {amount} in CommandGroup '{self.name}'. New limit: {self._group_max_agents}")
        return int(self._group_max_agents)

#endregion Agent Pool Management
#region Agent Management

    def _create_and_register_agent(self, template_name: str, *args, **kwargs) -> Agent:
        """
        Internal method to create and register an agent under the group and global agent caps.

        The agent is melded through this group's own native scope, supplied as the factory's
        reserved `conduit` control argument; a caller's own `conduit` keyword is refused with
        TypeError. Melder retains no agent: the agent owns its lifecycle and cleans itself on
        its own thread, and this group's registry indexes it.

        Admission is atomic (finding #30): both cap checks and the create+register
        decision run under the group lock, so racing creators cannot overshoot the
        group cap. See the in-body comment for the residual cross-group global
        window and the reserve-at-creation alternative.

        Args:
            template_name (str): The symbolic name of the registered agent template.

        Returns:
            Agent: The newly constructed and registered agent instance.

        Raises:
            RuntimeError: If the group or global agent cap is reached, or the
                CommandCenter is cleaned.
            Exception: Any exceptions raised by the template factory.
        """
        if self._cleaned:
            raise RuntimeError("CommandCenter is cleaned.")

        with self._lock:
            # Atomic admission (finding #30): the cap checks and the create+register
            # decision run under the group lock, so concurrent creators cannot all
            # pass a stale count and overshoot the group cap. The global check below
            # closes the unbounded-global hole on this path; because each group
            # guards with its own lock, distinct groups admitting simultaneously can
            # still overshoot the global cap by at most (active groups - 1). If that
            # residual ever matters, switch to reserve-at-creation: enforce
            # sum-of-group-caps <= total_max_agents at group creation/resize (the
            # config-level half already exists via finding #29's validation).
            if self._agent_count >= self._group_max_agents:
                self._notify('WORKER_CAP_REACHED', {'max_agents': self._group_max_agents, 'command_group': self._id})
                self._logger.warning(f"Cannot create agent. Worker cap of {self._group_max_agents} reached in command group '{self.name}'.", _manual_stack=True, _method_name="_create_and_register_agent", exec_info=True)
                raise RuntimeError(f"Cannot create agent. Worker cap of {self._group_max_agents} reached.")

            if self._command_center.get_total_agents() >= self._command_center._max_size:
                self._logger.warning(f"Cannot create agent. Global agent cap of {self._command_center._max_size} reached.", _manual_stack=True, _method_name="_create_and_register_agent", exec_info=True)
                raise RuntimeError(f"Cannot create agent. Global agent cap of {self._command_center._max_size} reached.")

            # we need to fill the pool immediately upon creation; the agent is melded from this
            # group's own scope (Slice 2), untracked: the agent owns its lifecycle on its own thread
            agent = self._command_center._create_agent_from_template(
                template_name=template_name, conduit=self._conduit, **kwargs,
            )
            self._register_agent(agent)

        return agent

    def create_agent(self,
                     agent_pool: BaseAgentPool,
                     template_name: str = "general",
                     logger: Optional[Union[logging.Logger, ChannelLogger]] = None,
                     **kwargs) -> None:
        """
        Creates, configures, and allocates a new agent to a specific pool.

        Args:
            agent_pool (BaseAgentPool): The pool this agent will belong to.
            template_name (str): The template to use for the agent.
                                 Defaults to "general".
            logger (logging.Logger, optional): A specific logger instance for the agent.
            **kwargs: Additional attributes for the agent's 'onboarding' logic.

        Raises:
            RuntimeError: If the command group or global agent limit has been reached.
            TypeError: If the agent's tags are not compatible with the target pool's tags.
        """
        if not isinstance(template_name, str) or not template_name:
            self._logger.error("Template name must be a string.", _manual_stack=True, _method_name="create_agent", exec_info=True)
            raise ValueError("Template name must be a non-empty string.")

        self._agent_creation_check(1)
        # The eligibility check is now performed here, before agent creation.
        self._eligibility_check(template_name, agent_pool)

        # --- Prepare arguments for the BaseAgentPool constructor ---
        # Start with the user-provided kwargs.
        final_kwargs = kwargs.copy()

        # Add/overwrite the essential arguments required by the BaseAgentPool constructor.
        # This ensures the context is always correctly passed down.
        final_kwargs['command_group'] = self
        final_kwargs['pool_agent'] = True
        final_kwargs['agent_pool'] = agent_pool
        final_kwargs['logger'] = logger

        agent = self._create_and_register_agent(template_name=template_name, **final_kwargs)
        # 1. Create a Pack that WRAPS the function and its arguments without calling it.
        onboarding_task = Pack(agent_pool._agent_onboarding)

        # 2. Register the self-contained task.
        agent.register_job("onboarding", onboarding_task)
        agent.deploy()

    def _eligibility_check(self, template_name: str, agent_pool: BaseAgentPool) -> None:
        """
        Internal helper to check if an agent from a given template is eligible
        to join a specific agent pool based on their tags.

        An agent is eligible if the pool's tags are a superset of the agent's tags.

        Args:
            template_name (str): The name of the agent template to check.
            agent_pool (BaseAgentPool): The pool to check against.

        Raises:
            TypeError: If the agent's tags are not a subset of the pool's tags.
            KeyError: If the agent_template_name is not found in the builder.
        """
        # 1. Get the template's tags from the AgentBuilder.
        # This now retrieves from the structured AgentTemplate object.
        template_info = self._command_center._agent_builder.get_template_info(template_name)
        agent_tags = template_info.get("tags", set())
        agent_pool._eligibility_checker(agent_tags)

    def create_agents(self, count: int, template_name: str,
                      agent_pool: BaseAgentPool,
                      **kwargs) -> None:
        """
        Creates a batch of agents and registers them with this group and a specific pool.

        Args:
            count (int): The number of agents to create.
            template_name (str): The template to use for the agents.
            agent_pool (BaseAgentPool): The pool these agents will belong to.
            **kwargs: Additional attributes for the agents' 'onboarding' logic.

        Raises:
            RuntimeError: If the command group or global agent limit has been reached.

        """
        self.check_cleaned()
        self._agent_creation_check(count)

        for _ in range(count):
            # This reuses the single-agent creation logic we already defined
            self.create_agent(template_name=template_name, agent_pool=agent_pool, **kwargs)


    def _agent_creation_check(self, count: int):
        """
        Internal helper to check if the requested agent creation would exceed the maximum allowed agents

        Args:
            count (int): The number of agents to create.

        Raises:
            RuntimeError: If the requested count would exceed the maximum allowed agents in this group.

        """
        if self._agent_count + count > self._group_max_agents:
            self._notify(
                'AGENT_CREATION_LIMIT_REACHED',
                {
                    'requested_count': count,
                    'current_count': self._agent_count,
                    'max_allowed': self._group_max_agents,
                    'command_group': self._id,
                }
            )
            self._logger.warning(
                f"Agent creation blocked: requested {count}, current count is {self._agent_count}, "
                f"limit is {self._group_max_agents} in command group '{self.name}'.", _manual_stack=True, _method_name="_agent_creation_check", exec_info=True
            )
            raise RuntimeError(
                f"Agent creation failed: requested {count} agents, but this would exceed the limit of "
                f"{self._group_max_agents} in command group '{self.name}'."
            )


    def _register_agent(self, agent: Agent) -> None:
        """
        Internal helper to register an agent in the active list.
        """
        if not self._cleaned and agent is not None:
            with self._lock:
                agent._group_name = self.name
                agent._group_id = self._id
                self._agent_count.increment()
                self._total_agent_count.increment()
                self._agents[agent._id] = agent
                self._notify('AGENT_CREATED', {'agent_id': agent._id, 'template_name': agent._template_name, 'command_group': self._id, 'command_group_name': self.name})

    def _unregister_agent(self, agent: Agent):
        """
        Internal helper to unregister and forget an agent.
        """
        if not self._cleaned and agent is not None:
            with self._lock:
                agent._group_name = None
                agent._group_id = None
                if self._agents.pop(agent._id, None):
                    self._agent_count.decrement()
                    self._total_agent_count.decrement()
                    self._cleanup_tracker.track_agent(agent)
                    self._notify('AGENT_UNREGISTERED', {'agent_id': agent._id, 'command_group': self._id, 'command_group_name': self.name})


#endregion Agent Management
#region Activity Management

    def create_activity(self, name: str, **kwargs) -> Optional[BaseActivity]:
        """
        Creates and registers a new activity within this group.

        This method calls the CommandCenter's internal factory to build the activity,
        then registers the new instance with this group for management.

        The activity is melded through this group's own native scope, supplied as the
        factory's reserved `conduit` control argument; a caller's own `conduit` keyword is
        refused with TypeError. Melder retains nothing it builds here (custody Y): this
        group's registry, or whoever takes a detached activity, keeps custody and cleans it.

        Args:
            name (str): The name of the activity template to use.
            **kwargs: Keyword arguments for the activity's constructor.

        Returns:
            The created and registered BaseActivity instance, or None if creation fails.
        """
        self.check_cleaned()

        # 1. Call the CommandCenter's protected factory method with this group's scope
        activity = self._command_center._create_activity(name, conduit=self._conduit, **kwargs)

        if activity:
            # 2. Register the new activity with this group
            activity._group_name = self.name
            activity._command_group = self
            activity._group_id = self._id
            self._activities[activity.id] = activity
            self._notify('ACTIVITY_CREATED', {'activity_id': activity.id})

        return activity

    def remove_activity(self, activity_id: str, dispose: bool = True) -> bool:
        """
        Removes an activity from this group’s registry and optionally disposes it.
        This is a local management operation, as activities are owned by the group.
        """
        self.check_cleaned()

        activity = self._activities.pop(activity_id, None)
        if activity:
            if dispose:
                activity.cleanup()
            self._notify('ACTIVITY_REMOVED', {'activity_id': activity.id})
            self._logger.warning(f"Activity {activity.id} removed from group '{self.name}'.", _manual_stack=True, _method_name="remove_activity")
            return True
        return False

    def resume_all_paused_activities(self):
        """
        Resumes all activities in this group that are currently in the PAUSED state.
        """
        self.check_cleaned()
        self._logger.info(f"Attempting to resume all paused activities in group '{self.name}'.", _manual_stack=True, _method_name="resume_all_paused_activities")

        for activity in self._activities.values():
            if activity.get_status() == ActivityStatus.PAUSED:
                activity.resume()
                self._notify('ACTIVITY_RESUMED', {'activity_id': activity.id})
                self._logger.warning(f"Activity {activity.id} resumed.", _manual_stack=True, _method_name="resume_all_paused_activities")


    def start_all_activities(self):
        """
        Starts all PENDING activities within this group. This is a core management duty.
        """
        self.check_cleaned()

        for activity in list(self._activities.values()):
            if activity.get_status() == ActivityStatus.PENDING:
                activity.start()
                self._logger.info(f"Started activity '{activity.id}'.", _manual_stack=True, _method_name="start_all_activities")
                self._notify('ACTIVITY_STARTED', {'activity_id': activity.id})


    def pause_all_activities(self):
        """
        Pauses all RUNNING activities in this group.
        """
        self.check_cleaned()

        for activity in list(self._activities.values()):
            if activity.get_status() == ActivityStatus.RUNNING:
                activity.pause()
                self._logger.info(f"Paused activity '{activity.id}'.", _manual_stack=True, _method_name="pause_all_activities")
                self._notify('ACTIVITY_PAUSED', {'activity_id': activity.id})

    def cancel_all_activities(self):
        """
        Cancels all activities in this group that are in a non-terminal state.
        """
        self.check_cleaned()

        terminal_states = {ActivityStatus.COMPLETED, ActivityStatus.FAILED, ActivityStatus.CANCELLED,
                           ActivityStatus.CLEANED}
        for activity in list(self._activities.values()):
            if activity.get_status() not in terminal_states:
                activity.cancel()
                self._logger.info(f"Cancelled activity '{activity.id}'.", _manual_stack=True, _method_name="cancel_all_activities")
                self._notify('ACTIVITY_CANCELLED', {'activity_id': activity.id})

    def deploy_all_pending_activities(self, agents_per_activity: int, strategy: str = "command_group_pool_affinity_deploy",
                                      **kwargs):
        """
        Deploys a team of agents to every activity currently in the PENDING state.

        This is a high-level command to kickstart all planned tactical operations
        within the group that haven't been assigned agents yet.

        Args:
            agents_per_activity (int): The number of agents to create and assign to EACH
                                       pending activity in the target group.
            strategy (str): The deployment strategy to use for assigning agents. Defaults
                            to 'command_group_pool_affinity_deploy', which requires 'target_pool_name'
                            to be passed in **kwargs.
            **kwargs: Additional keyword arguments to be passed to the deployment strategy's
                      execute method (e.g., target_pool_name="my_pool").
        """
        self.check_cleaned()
        self._logger.info(f"Attempting to deploy agents to all pending activities in group '{self.name}'.", _manual_stack=True, _method_name="deploy_all_pending_activities")

        pending_activities = [
            activity for activity in self._activities.values()
            if activity.get_status() == ActivityStatus.PENDING
        ]

        if not pending_activities:
            self._logger.info(f"No pending activities found in group '{self.name}' to deploy.", _manual_stack=True, _method_name="deploy_all_pending_activities")
            return

        for activity in pending_activities:
            self._logger.info(f"Initiating deployment of {agents_per_activity} agents for pending activity '{activity.id}'.", _manual_stack=True, _method_name="deploy_all_pending_activities")
            try:
                # This now correctly calls the unified execute_strategy method.
                self.execute_strategy(
                    name=strategy,
                    command_type="deployment", # Added the required command_type
                    deployment=activity,
                    agent_count=agents_per_activity,
                    **kwargs
                )
            except Exception as e:
                self._logger.error(f"Failed to initiate deployment for activity '{activity.id}': {e}", exc_info=True, _manual_stack=True, _method_name="deploy_all_pending_activities")

#endregion Activity Management
#region Mission Management

    def create_mission(self, name: str, **kwargs) -> Optional[BaseMission]:
        """
        Creates and registers a new mission within this group.

        This method acts as a factory, using the CommandCenter's MissionBuilder
        to construct a new mission instance from a registered type. The new
        mission is then registered with this CommandGroup for management and
        orchestration.

        The mission is melded through this group's own native scope, supplied as the
        builder's reserved `conduit` control argument; a caller's own `conduit` keyword is
        refused with TypeError. Supplied objects (workflow activities, deploy_kwargs) reach
        the mission as the same objects. Melder retains nothing it builds here (custody Y):
        this group's registry, or whoever takes a detached mission, keeps custody and
        cleans it. Construction errors propagate as the builder raises them.

        Args:
            name (str): The name of the mission type to build (e.g., "general_mission").
            **kwargs: Keyword arguments for the mission's constructor.

        Returns:
            The created and registered BaseMission instance, or None if the mission type
            is not registered.
        """
        self.check_cleaned()

        # 1. Delegate the "building" of the blueprint to the CommandCenter's builder,
        #    through this group's scope.
        mission = self._command_center._mission_builder.build_mission(name, conduit=self._conduit, **kwargs)

        if mission:
            # 2. Register the new mission instance with this group.
            #    This is where we inject the group's context into the mission.
            mission._group_name = self.name
            mission._command_group = self
            mission._group_id = self._id
            self._missions[mission.id] = mission
            self._notify('MISSION_CREATED', {'mission_id': mission.id})
            self._logger.info(f"Mission '{mission.id}' created in group '{self.name}'.", _manual_stack=True, _method_name="create_mission")

        return mission

    def remove_mission(self, mission_id: str, dispose: bool = True) -> bool:
        """
        Removes a mission from this group’s registry and optionally disposes it.

        Args:
            mission_id (str): The unique ID of the mission to remove.
            dispose (bool): If True, the mission object will be cleaned of.

        Returns:
            True if the mission was found and removed, False otherwise.
        """
        self.check_cleaned()
        mission = self._missions.pop(mission_id, None)
        if mission:
            if dispose:
                mission.cleanup()
            self._notify('MISSION_REMOVED', {'mission_id': mission.id})
            self._logger.warning(f"Mission {mission.id} removed from group '{self.name}'.", _manual_stack=True, _method_name="remove_mission")
            return True
        return False

    def pause_all_missions(self):
        """
        Pauses all RUNNING missions in this group.
        """
        self.check_cleaned()
        self._logger.info(f"Attempting to pause all running missions in group '{self.name}'.", _manual_stack=True, _method_name="pause_all_missions")

        for mission in self._missions.values():
            if mission.get_status() == MissionStatus.RUNNING:
                mission.pause()
                self._notify('MISSION_PAUSED', {'mission_id': mission.id})
                self._logger.info(f"Mission {mission.id} paused.", _manual_stack=True, _method_name="pause_all_missions")

    def resume_all_paused_missions(self):
        """
        Resumes all missions in this group that are currently in the PAUSED state.
        """
        self.check_cleaned()
        self._logger.info(f"Attempting to resume all paused missions in group '{self.name}'.", _manual_stack=True, _method_name="resume_all_paused_missions")

        for mission in self._missions.values():
            if mission.get_status() == MissionStatus.PAUSED:
                mission.resume()
                self._notify('MISSION_RESUMED', {'mission_id': mission.id})
                self._logger.info(f"Mission {mission.id} resumed.", _manual_stack=True, _method_name="resume_all_paused_missions")

    def cancel_all_missions(self):
        """
        Cancels all missions in this group that are in a non-terminal state.
        """
        self.check_cleaned()
        self._logger.info(f"Attempting to cancel all non-terminal missions in group '{self.name}'.", _manual_stack=True, _method_name="cancel_all_missions")

        terminal_states = {MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELLED,
                           MissionStatus.cleaned}
        for mission in self._missions.values():
            if mission.get_status() not in terminal_states:
                mission.cancel()
                self._notify('MISSION_CANCELLED', {'mission_id': mission.id})
                self._logger.info(f"Mission {mission.id} cancelled.", _manual_stack=True, _method_name="cancel_all_missions")


#endregion Mission Management
#region Interchange Management

    def get_interchange_connector(self, name: str, retain_instance: bool = False) -> Optional[BaseConnector]:
        """
        Retrieves an InterchangeConnector by its name from the CommandGroup's interchange.

        Args:
            name (str): The name of the InterchangeConnector to retrieve.
            retain_instance (bool): If True, the connector will not be cleaned of after use.

        Returns:
            Optional[BaseConnector]: The requested InterchangeConnector instance, or None if not found.
        """
        self.check_cleaned()
        return self._command_center._interchange.get_connector(name, retain_instance=retain_instance)

#endregion Interchange Management
#region Toolbox Management

    def build_tool(self, name: str, **kwargs: Any) -> Optional[BaseTool]:
        """
        Build a caller-owned tool through this group's scope and the shared Toolbox.

        Toolbox resolves the registered class through Melder with these exact constructor
        inputs. The tool remains untracked and caller-owned; group cleanup does not dispose
        it. A caller cannot replace the reserved conduit argument. Existing pool, mission,
        activity and agent facades keep delegating here.

        Args:
            name (str): The name of the tool to build.
            **kwargs: Additional keyword arguments for the tool's constructor.

        Returns:
            Optional[BaseTool]: A fresh tool, or None when the alias is unknown.

        Raises:
            RuntimeError: This group is cleaned.
            TypeError: Inputs are refused or the caller supplies the reserved conduit key.
            Exception: Native resolution or the tool constructor fails; Toolbox preserves
                the original constructor error under its established error contract.
        """
        self.check_cleaned()
        return self._command_center._toolbox.build_tool(name, conduit=self._conduit, **kwargs)


#endregion Toolbox Management
#region Action Management

    def get_action(self, action_name: str) -> Optional[BaseAction]:
        """
        Retrieves an action by its name from the CommandGroup's action registry.

        Args:
            action_name (str): The name of the action to retrieve.

        Returns:
            Optional[BaseAction]: The requested action instance, or None if not found.
        """
        self.check_cleaned()
        return self._command_center._actions.get_action(action_name)

#endregion Action Management
#region Introspection & Reporting

    def get_status_summary(self) -> Dict[str, int]:
        """
        Returns a count of this group's activities, grouped by their current status.
        """
        self.check_cleaned()

        summary = {status.name: 0 for status in ActivityStatus}
        for activity in list(self._activities.values()):
            status_name = activity.get_status().name
            if status_name in summary:
                summary[status_name] += 1
        return summary

    def list_agents(self) -> List[str]:
        """
        Lists all agent IDs currently assigned to this group.
        """
        self.check_cleaned()
        return list(self._agents.keys())

    def list_activities(self) -> List[str]:
        """
        Lists all activity IDs currently being managed by this group.
        """
        self.check_cleaned()
        return list(self._activities.keys())

    def list_signal_controllers(self) -> List[str]:
        """
        Lists the names of all SignalControllers managed by this group.
        """
        self.check_cleaned()
        # Snapshot: registration and removal mutate `_signal_controllers` from other
        # threads and this accessor takes no lock. The sibling `list_missions` below
        # already materialises for the same reason.
        return [c.name for c in list(self._signal_controllers.values())]

    def list_missions(self) -> List[str]:
        """
        Lists all mission IDs currently being managed by this group.
        """
        self.check_cleaned()
        return list(self._missions.keys())

#endregion Introspection & Reporting
#region Work Management

    def _validate_pool_tags(self, target_pool: BaseAgentPool, required_tags: Optional[Set[str]]):
        """
        Validates that a target pool has the capabilities to handle a task.

        Args:
            target_pool: The agent pool being checked.
            required_tags: The set of tags the task requires.

        Raises:
            ValueError: If the pool does not have all the required tags.
        """
        # If no specific tags are required for the task, no validation is needed.
        if not required_tags:
            return

        # Check if the task's required tags are a subset of the pool's tags.
        if not required_tags.issubset(target_pool.tags):
            self._logger.error(
                f"Pool '{target_pool.pool_name}' with tags {target_pool.tags} does not meet the required tags {required_tags} for this task.",
                _manual_stack=True, _method_name="_validate_pool_tags"
            )
            raise ValueError(
                f"Pool '{target_pool.pool_name}' with tags {target_pool.tags} "
                f"does not meet the required tags {required_tags} for this task."
            )

    #TODO: This API is really weird because you gotta target a pool before you can submit
    def create_request(self,
                       pool_id: str,
                       request_type: str,
                       work_callable: Pack,
                       required_tags: Optional[Iterable[str]] = None,
                       **kwargs) -> Any:
        """
        Creates a single, generic, trackable request and submits it to a
        specific agent pool for processing.

        This is the primary, flexible entry point for submitting any kind of work
        to a pool, allowing for custom, user-defined workflows.

        Args:
            pool_id (str): The unique ID of the target agent pool within this group.
            request_type (str): A string identifying the type of request for the pool
                                to handle (e.g., "task", "deployment", "run_analysis").
            work_callable (Pack): The function to be executed by an agent.
            required_tags (Optional[Iterable[str]]): A set of tags that agents must
                                                     possess to be eligible for this work.
            **kwargs: Additional, request-type-specific arguments.

        Returns:
            A trackable "future-like" object representing the submitted request, as
            returned by the target pool.
        """
        self.check_cleaned()
        Pack.verify(work_callable)

        target_pool = self.find_agent_pool_by_id(pool_id)
        if not target_pool:
            self._logger.error(f"No agent pool with ID '{pool_id}' found in command group '{self.name}'.", _manual_stack=True, _method_name="create_request")
            raise ValueError(f"No agent pool with ID '{pool_id}' found in command group '{self.name}'.")

        # Validate that the pool can handle the required skills (tags).
        tag_set = set(required_tags) if required_tags is not None else None
        self._validate_pool_tags(target_pool, tag_set)

        # Delegate the actual handling of the request to the pool itself.
        # The pool is responsible for knowing what to do with the request_type.
        return target_pool.handle_request(
            request_type=request_type,
            work_callable=work_callable,
            required_tags=tag_set,
            **kwargs,
        )

    def create_requests(self, requests: Iterable[Dict[str, Any]]) -> List[Any]:
        """
        Creates a batch of trackable requests and submits them to their respective
        agent pools.

        This is a direct command that iterates through a list of request dictionaries,
        providing a convenient way to submit multiple, potentially different, work
        items in a single call.

        Args:
            requests (Iterable[Dict[str, Any]]): An iterable of dictionaries, where each
                dictionary defines a single work request. Each dict must contain:
                - 'pool_id' (str): The unique ID of the target agent pool.
                - 'request_type' (str): The string identifying the type of work.
                - 'work_callable' (Callable): The function to be executed.
                It can also contain optional keys like 'required_tags' and any other
                kwargs to be passed to the pool's request handler.

        Returns:
            A list of trackable "future-like" objects for each submitted request.
        """
        self.check_cleaned()

        results = []
        for request_params in requests:
            try:
                # Make a copy to avoid modifying the user's original dictionary
                params = request_params.copy()

                # Pop the main arguments from the dictionary
                pool_id = params.pop('pool_id')
                request_type = params.pop('request_type')
                work_callable = params.pop('work_callable')

                # The rest of the items in the dictionary are treated as **kwargs
                future_object = self.create_request(
                    pool_id=pool_id,
                    request_type=request_type,
                    work_callable=work_callable,
                    **params
                )
                results.append(future_object)
            except KeyError as e:
                self._logger.error(f"A request dictionary is missing a required key: {e}", exc_info=True, _manual_stack=True, _method_name="create_requests")
                raise ValueError(f"A request dictionary is missing a required key: {e}")
            except Exception as e:
                # Log the error and continue, or re-raise depending on desired strictness
                self._logger.error(f"Failed to process a request in batch: {request_params}. Error: {e}", exc_info=True, _manual_stack=True, _method_name="create_requests")
                # For now, we'll be strict and re-raise.
                raise

        return results


#endregion Work Management
#region Strategic Command Management

    def execute_strategy(self,
                         name: str,
                         command_type: str,
                         **kwargs: Any) -> Any:
        """
        Executes a registered CommandGroup-level strategy.

        This is the primary, generic entry point for all strategic operations
        within this CommandGroup. It finds the correct strategy based on its
        name and type, and then executes it, passing this CommandGroup instance
        as the operational context.

        Args:
            name (str): The unique name of the strategy to execute.
            command_type (str): The type of command (e.g., 'task', 'deployment', or a
                                custom type like 'sql_query').
            **kwargs: All other necessary arguments for the strategy, such as
                      'work_callable', 'required_tags', etc. These are passed
                      directly to the strategy's execute method.

        Returns:
            Any: The result of the strategy's execution.
        """
        self.check_cleaned()

        # We delegate the execution to the StrategicCommand module, providing
        # 'cg' as the scope and this CommandGroup instance as the context.
        return self._strategic_command.execute_strategy(
            name=name,
            command_structure_type='cg',
            command_type=command_type,
            context=self,
            **kwargs
        )

#endregion Strategic Command Management
#endregion CommandGroup
