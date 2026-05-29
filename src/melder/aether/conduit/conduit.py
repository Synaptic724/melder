import threading
import time
from contextlib import contextmanager
from types import ModuleType, TracebackType
from typing import (
    TYPE_CHECKING,
    Optional,
    Any,
    Tuple,
    Callable,
    Iterable,
    Dict,
    Generator,
    ClassVar,
)
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.meld.meld import Meld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.spellbook.bind.scan import Scan
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
if TYPE_CHECKING:
    from melder.nexus.nexus import Nexus
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
        TransactionMediator,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
    from melder.mutation_research.mutation_research import MutationResearch
    from melder.utilities.logger.safe_logger import SafeLogger
    from melder.utilities.synchronization.creation_gate import CreationGate
    from melder.utilities.synchronization.creation_gate_controller import CreationGateController

#region Conduit

class Conduit(Cleanable):
    """
    A `Conduit` is the runtime scope, execution boundary, and contract-aware access
    surface for one branch of the Melder graph.

    At runtime a conduit acts as the object that owns meld execution, spellspace
    scope, contract/link behavior, lesser-conduit lineage, and access to the
    frame-level services needed to create, share, and tear down spell-backed
    objects safely.

    Contract:
    - Owns one meld runtime, one creations manager, one conduit ward, one creation
      gate, spellspace tracking state, and conduit-local hook overlays.
    - Can create lesser conduits beneath its current root lineage.
    - Can link to peer conduits only when the runtime is in dynamic mode and the
      active policy allows it.
    - Uses a `CreationGate` to control meld entry and track in-flight meld work for
      safe drain and shutdown behavior.
    - Normal conduits own the Spellbook lifecycle; lesser conduits share the parent
      Spellbook and do not unregister frame-level state directly.
    - Becomes unusable after cleanup completes.

    Meld gating:
        Each conduit owns a `CreationGate` that can block or deny new meld calls.
        The gate tracks active melds via ticket registration so the system can
        drain in-flight work before shutdown or dynamic reconfiguration.

    Threading / Concurrency:
        - Uses an internal `RLock` for multi-step conduit state transitions.
        - Relies on `CreationGate` and `CreationGateController` for meld admission
          and lineage-aware gate control.
        - Delegates current-frame registration to the injected AethericFrame and
          reads lookup/cluster coordination through the frame-owned cloud service.
        - Delegates gate governance to the injected frame-owned
          `CreationGateController`.

    Lifecycle / Cleanup:
        - Normal and lesser conduits follow different cleanup paths.
        - Cleanup tears down meld/runtime state first, then contracts/links, then
          owned registries and logger state.
        - Logger cleanup is intentionally last.

    """
    __slots__ = Cleanable.__slots__ + [
       "_id",
       "_lock",
       "_name",
       "__dynamic_environment__",
       "_nexus_publish_enabled",
       "_aetheric_frame_name",
       "_aetheric_frame",
       "_configuration",
       "_conduit_state",
       "_spellbook",
       "_nexus",
       "_logger",
       "_root_conduit_id",
       "_transaction_identity",
       "_spellspace_stack",
       "_spellspace_registry",
       "_spellspace_pool",
       "_conduit_pool",
       "_creations",
       "_creation_gate_controller",
       "_creation_gate",
       "_conduit_hooks",
       "_meld_hooks",
       "_local_conduit_hooks",
       "_meld",
       "_conduit_ward",
        "_permanent_cleanup_requested",
    ]
    _DEFAULT_ROOT_CONDUIT_NAME: ClassVar[str] = "default"
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    def __init__(
            self,
            spellbook: Spellbook,
            configuration: SpellbookConfiguration,
            conduit_state: ConduitState,
            aetheric_frame_name: str,
            aetheric_frame: AethericFrame,
            policy: Policies,
            creation_gate_controller: CreationGateController,
            dynamic: bool = False,
            name: Optional[str] = None,
            logger: Any | None = None,
            conduit_id: Optional[str] = None,
            root_conduit_id: Optional[str] = None,
            creation_gate: CreationGate | None = None,
            conduit_hooks: Optional[dict[str, list[Any]]] = None,
            meld_hooks: Optional[dict[str, list[Callable[..., Any]]]] = None,
    ):
        """
        Public API

        Initializes a new Conduit.

        Args:
            spellbook (Spellbook):
                The Spellbook governing this Conduit.
            configuration (SpellbookConfiguration):
                The locked system configuration.
            conduit_state (ConduitState):
                The role of this Conduit ('normal' or 'lesser').
            aetheric_frame_name (str):
                The Aetheric frame name this Conduit belongs to.
            aetheric_frame (AethericFrame):
                The live frame object that owns registration and frame-local
                cloud services for this conduit.
            policy (Policies):
                The Conduit policy that governs linking and contract behavior.
            dynamic (bool, optional):
                If True, operate in dynamic mode.
            name (str, optional):
                An optional name for easier identification.
            logger (Any | None, optional):
                Optional logger instance or logger-like object.
            conduit_id (str | None, optional):
                Optional explicit conduit identifier. When None, an ID is generated
                via IDBuilder.create_id().
            root_conduit_id (str | None, optional):
                Root conduit id for this lineage. Required for lesser conduits.
            creation_gate_controller (CreationGateController):
                Frame-owned CreationGateController injected into this conduit at
                construction time.
            creation_gate (CreationGate | None, optional):
                Optional CreationGate to register for this conduit. When None,
                a new gate is created via the injected frame-owned
                CreationGateController.
            conduit_hooks (Optional[dict[str, list[Any]]], optional):
                Optional shared conduit hook map to attach by reference.
            meld_hooks (Optional[dict[str, list[Callable[..., Any]]]], optional):
                Optional shared meld hook map to attach by reference.

        Raises:
            TypeError:
                If configuration is not an SpellbookConfiguration, conduit_id is not a string,
                or root_conduit_id is not a string.
            ValueError:
                If conduit_id is provided but empty, or root_conduit_id is invalid
                for the requested conduit_state.
        """
        super().__init__()
        # General Init
        self._lock: threading.RLock = threading.RLock()
        if conduit_id is None:
            conduit_id = IDBuilder.create_id()
        elif not isinstance(conduit_id, str):
            raise TypeError(
                f"conduit_id must be a string when provided, got {type(conduit_id).__name__}"
            )
        elif not conduit_id:
            raise ValueError("conduit_id cannot be empty.")

        self._id: str = conduit_id
        self._permanent_cleanup_requested: bool = False
        self._name: Optional[str] = name
        self.__dynamic_environment__: bool = bool(dynamic)
        self._nexus_publish_enabled: bool = False
        self._aetheric_frame_name: str = aetheric_frame_name
        self._aetheric_frame: AethericFrame = aetheric_frame
        # Special Configuration
        if not isinstance(configuration, SpellbookConfiguration):
            raise TypeError(f"Expected SpellbookConfiguration instance, got {type(configuration).__name__}")

        self._configuration: SpellbookConfiguration = configuration
        self._conduit_state: ConduitState = conduit_state  # can be normal, lesser
        self._spellbook: Spellbook = spellbook
        self._nexus: Nexus = spellbook._nexus
        if creation_gate_controller is None:
            raise ValueError("creation_gate_controller cannot be None.")
        self._creation_gate_controller: CreationGateController = (
            creation_gate_controller
        )
        self._logger: SafeLogger = self._configure_logger(logger)

        if conduit_state is ConduitState.lesser:
            if root_conduit_id is None:
                raise RuntimeError(
                    "Lesser conduits require a root_conduit_id."
                )
            self._root_conduit_id: str = root_conduit_id
        else:
            self._root_conduit_id = self._id
        self._transaction_identity: DevopsIdentity = DevopsIdentity(
            owner_kind="conduit",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame_name,
            metadata={},
            available_transactions=tuple(),
        )
        self._transaction_identity.attach_registry(
            self._aetheric_frame.devops_information_registry,
            object_ref=self,
        )
        self._spellspace_stack: SpellSpaceThreadState = SpellSpaceThreadState()
        self._spellspace_registry: set[SpellSpace] = set()
        self._creations: Creations = Creations(
            conduit_id=self._id,
            spellspace_stack=self._spellspace_stack,
        )
        if creation_gate is None:
            creation_gate = self._create_gate_for_current_root(conduit_id)
        else:
            self._register_existing_gate_for_current_root(conduit_id, creation_gate)
        self._creation_gate: CreationGate = creation_gate

        if conduit_hooks is None:
            resolved_conduit_hooks = self._configuration.get_conduit_hooks(
                self._spellbook._id,
            )
            self._conduit_hooks = resolved_conduit_hooks or None
        else:
            self._conduit_hooks = conduit_hooks

        if meld_hooks is None:
            resolved_meld_hooks = self._configuration.get_meld_hooks(
                self._spellbook._id,
            )
            self._meld_hooks = resolved_meld_hooks or None
        else:
            self._meld_hooks = meld_hooks

        # Local hook overlays for this conduit only.
        self._local_conduit_hooks: dict[str, list[Any]] | None = None

        self._meld: Meld = Meld(
            creations=self._creations,
            spellbook=self._spellbook,
            conduit_id=self._id,
            resolution_conduit_id=self._root_conduit_id,
            dynamic_environment=self.__dynamic_environment__,
            meld_hooks=self._meld_hooks,
        )
        self._spellspace_pool: SpellSpacePool = SpellSpacePool(
            owner_conduit_id=self._id,
            meld=self._meld,
            creations=self._creations,
            spellspace_registry=self._spellspace_registry,
            baseline_idle=4,
            max_idle=4,
        )
        if conduit_state is ConduitState.normal:
            self._conduit_pool: ConduitPool = ConduitPool(
                root_conduit=self,
                baseline_idle=10,
                max_idle=10,
            )
        else:
            root_conduits = self._aetheric_frame._conduits
            root_conduit = root_conduits.get(self._root_conduit_id)
            if root_conduit is None:
                raise RuntimeError(
                    "Root conduit is unavailable for conduit pool wiring."
                )
            self._conduit_pool = root_conduit._conduit_pool
        self._configure_conduit_state()
        self._conduit_ward: ConduitWard = ConduitWard(
            conduit=self,
            dynamic=self.__dynamic_environment__,
            conduit_type=self._conduit_state,
            policy=policy,
            aetheric_frame=self._aetheric_frame,
        )
        self._refresh_devops_identity_state()



    #region Cleanup and Disposal
    def cleanup(self) -> None:
        """
        Public API

        Idempotently clean this conduit and release its owned runtime state.

        Contract:
            - Idempotent: repeated calls are safe after `_cleaned` flips.
            - Fires `on_conduit_cleanup_start` before teardown and
              `on_conduit_cleanup_complete` after teardown finishes.
            - Dispatches to the lesser- or normal-conduit cleanup path based on the
              current conduit state.
            - Tears down logger state last, after the rest of the runtime surface has
              been released.
            - This is local conduit teardown only; it does not clean Aether or the
              owning frame itself.

        Returns:
            None.

        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self._permanent_cleanup_requested:
                self._permanent_cleanup()
            else:
                self._prepare_for_pool()

    def _prepare_for_pool(self):
        """
        Reset one lesser conduit into the pooled idle state.

        Contract:
            - Normal conduits do not enter the lesser pool and still hard-clean.
            - Lesser conduits transition to `pooled_lesser` locally before they
              are returned to the root-owned pool.
            - Pool return is a local lifecycle change only; it does not refresh
              dev-ops identity or republish the conduit to Nexus.
        """
        if self._conduit_state is ConduitState.normal:
            self._permanent_cleanup()
            return
        self._cleanup_spellspaces_for_pool()
        self._creations.reset_non_spellspace_for_pool()
        self._conduit_ward._detach_for_pool()
        self._conduit_state = ConduitState.pooled_lesser
        self._conduit_ward._conduit_type = ConduitState.pooled_lesser
        if self._local_conduit_hooks is not None:
            self._local_conduit_hooks.clear()
        self._conduit_pool.return_lesser_conduit(self)

    def _cleanup_spellspaces_for_pool(self) -> None:
        """
        Internal

        Soft-clean active and registered spellspaces without destroying the pool.
        """
        try:
            stack = list(self._spellspace_stack.get())
            for space in stack:
                try:
                    space.cleanup()
                except Exception:
                    self._logger.error(
                        "Error cleaning spellspace for pool",
                        "_cleanup_spellspaces_for_pool",
                        exc_info=True,
                    )
            self._spellspace_stack.set([])
            for registered_space in list(self._spellspace_registry):
                try:
                    registered_space.cleanup()
                except Exception:
                    self._logger.error(
                        "Error cleaning registered spellspace for pool",
                        "_cleanup_spellspaces_for_pool",
                        exc_info=True,
                    )
        except Exception:
            self._logger.error(
                "Error flushing spellspaces for pool",
                "_cleanup_spellspaces_for_pool",
                exc_info=True,
            )

    def permanent_cleanup(self) -> None:
        """
        Permanently destroy this spellspace instead of returning it to a pool.

        Contract:
            - Flips the permanent cleanup flag immediately.
            - Reuses the normal cleanup entrypoint so all public teardown still
              flows through one surface.
        """
        self._permanent_cleanup_requested = True
        self.cleanup()

    def _permanent_cleanup(self):
        """
        Internal

        Cleans up all resources associated with the Conduit, including
        deregistering from Aether and Spellbook, and removing all references.
        """
        if self._conduit_hooks or self._local_conduit_hooks:
            self._fire_conduit_hooks("on_conduit_cleanup_start", self)
            self._cleaned = True
            if self._conduit_state in (
                    ConduitState.lesser,
                    ConduitState.pooled_lesser,
            ):
                self._cleanup_lesser_conduit()
            elif self._conduit_state == ConduitState.normal:
                self._cleanup_normal_conduit()
            else:
                self._logger.error("Unknown Conduit state during cleanup", "cleanup")
                raise RuntimeError("Conduit state is unknown during cleanup")
            self._fire_conduit_hooks("on_conduit_cleanup_complete", self)

            del self._conduit_hooks
            del self._meld_hooks
            del self._local_conduit_hooks

            # Logger last
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            del self._logger
        else:
            self._cleaned = True
            if self._conduit_state in (
                    ConduitState.lesser,
                    ConduitState.pooled_lesser,
            ):
                self._cleanup_lesser_conduit()
            elif self._conduit_state == ConduitState.normal:
                self._cleanup_normal_conduit()
            else:
                self._logger.error("Unknown Conduit state during cleanup", "cleanup")
                raise RuntimeError("Conduit state is unknown during cleanup")

            del self._conduit_hooks
            del self._meld_hooks
            del self._local_conduit_hooks

            # Logger last
            try:
                if hasattr(self._logger, "cleanup"):
                    self._logger.cleanup()
            except Exception:
                pass
            del self._logger

    def _cleanup_lesser_conduit(self) -> None:
        """
        Internal

        Cleans up a lesser Conduit.
        """
        self._remove_conduit_record_from_nexus()
        # Lesser conduits share the parent Spellbook and are not root-registered
        # in Aether. We tear down local runtime and lineage links, but do not
        # touch the shared Spellbook/Aether registries.
        if self._creation_gate_controller is not None:
            try:
                self._creation_gate_controller.unregister_conduit_gate(self._id)
            except Exception:
                self._logger.error(
                    "Error unregistering creation gate", "_cleanup_lesser_conduit", exc_info=True
                )
        if self._creation_gate is not None:
            self._creation_gate.cleanup()
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

        # Null internal references
        del self._conduit_ward
        del self._meld
        del self._creation_gate
        del self._creation_gate_controller
        del self._creations
        del self._aetheric_frame
        self._transaction_identity.cleanup()
        del self._transaction_identity
        del self._spellspace_stack
        del self._spellspace_registry
        del self._conduit_pool
        del self._spellbook
        del self._configuration
        del self._root_conduit_id
        del self._nexus


    def _cleanup_normal_conduit(self) -> None:
        """
        Internal

        Cleans up a normal Conduit.
        """
        self._remove_conduit_record_from_nexus()
        # 1) Meld runtime (stop new object creation paths)
        if self._creation_gate_controller is not None:
            try:
                self._creation_gate_controller.unregister_conduit_gate(self._id)
            except Exception:
                self._logger.error(
                    "Error unregistering creation gate", "_cleanup_normal_conduit", exc_info=True
                )
        if self._creation_gate is not None:
            self._creation_gate.cleanup()
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

        try:
            if self._conduit_pool is not None:
                self._conduit_pool.cleanup()
        except Exception:
            self._logger.error("Error cleaning conduit pool", "_cleanup_normal_conduit", exc_info=True)

        # 4) Unregister from Aether (spells + root conduit + cloud)
        try:
            if self._spellbook is not None:
                self._spellbook._unregister_conduit_spells_from_aether(self._id)
            self._remove_root_conduit()
            self._publish_frame_record_to_nexus()
        except Exception as e:
            self._logger.error(f"Error unregistering root conduit state: {e}", "_cleanup_normal_conduit", exc_info=True)

        # 4.5) Drop per-conduit resolution state (normal conduits only)
        try:
            if self._spellbook is not None and self._spellbook._spell_system_states is not None:
                self._spellbook._spell_system_states.drop_conduit_resolution_state(self._id)
        except Exception:
            self._logger.error("Error dropping conduit resolution state", "_cleanup_normal_conduit", exc_info=True)

        # 5) Spellbook (owned by normal conduits)
        try:
            if self._spellbook is not None:
                self._spellbook.cleanup()
        except Exception:
            self._logger.error("Error cleaning spellbook", "_cleanup_normal_conduit", exc_info=True)

        # 6) Null internal references
        del self._conduit_ward
        del self._meld
        del self._creation_gate
        del self._creation_gate_controller
        del self._aetheric_frame
        del self._creations
        del self._spellbook
        del self._configuration
        self._transaction_identity.cleanup()
        del self._transaction_identity
        del self._spellspace_stack
        del self._spellspace_registry
        del self._conduit_pool
        del self._aetheric_frame_name
        del self._root_conduit_id
        del self._nexus

    def _publish_conduit_record_to_nexus(self) -> None:
        """
        Internal

        Publish this conduit's current canonical record into Nexus when the
        conduit is eligible for passive ingest.

        Contract:
            - Published conduit states in the current passive-ingest slice are
              normal and lesser.
            - Publication is skipped when Nexus publication is disabled for this
              conduit.
            - Uses the conduit-owned Nexus reference directly.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if self._conduit_state not in (
                ConduitState.normal,
                ConduitState.lesser,
                ConduitState.pooled_lesser,
        ):
            return

        self._nexus._publish_conduit_record(self)

    def _publish_frame_record_to_nexus(self) -> None:
        """
        Internal

        Republish the owning frame summary into Nexus when this conduit changes
        frame-level overview data.

        Contract:
            - Uses the owning Spellbook as the frame-record publication source.
            - Skips publication when Nexus publication is disabled for this
              conduit.
            - Intended only for mutations that affect frame summary fields such
              as root-conduit inventory, conduit-cloud entries, or cluster
              inventory.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if self._spellbook is None:
            return

        self._nexus._publish_frame_record(self._spellbook)

    def _remove_conduit_record_from_nexus(self) -> None:
        """
        Internal

        Remove this conduit's canonical record from Nexus when the conduit is
        eligible for passive ingest.

        Contract:
            - Published conduit states in the current passive-ingest slice are
              normal and lesser.
            - Removal is skipped when Nexus publication is disabled for this
              conduit.
            - Uses the conduit-owned Nexus reference directly.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if self._conduit_state not in (
                ConduitState.normal,
                ConduitState.lesser,
                ConduitState.pooled_lesser,
        ):
            return

        self._nexus._remove_conduit_record(self._id, self._aetheric_frame_name)

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
                    space.permanent_cleanup()
                except Exception:
                    self._logger.error("Error cleaning spellspace", "_cleanup_spellspaces", exc_info=True)
            self._spellspace_stack.set([])
            if self._spellspace_registry is not None:
                for registered_space in list(self._spellspace_registry):
                    try:
                        registered_space.permanent_cleanup()
                    except Exception:
                        self._logger.error("Error cleaning spellspace", "_cleanup_spellspaces", exc_info=True)
                self._spellspace_registry.clear()
            if self._spellspace_pool is not None:
                self._spellspace_pool.cleanup()
        except Exception:
            self._logger.error("Error flushing spellspace stack", "_cleanup_spellspaces", exc_info=True)


    #endregion Cleanup and Disposal


    # ------------------------------------------------------------------ #
    # SpellSpace support
    # ------------------------------------------------------------------ #

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """
        Return the currently active SpellSpace for this Conduit, if any.

        Returns:
            SpellSpace | None: The top-of-stack SpellSpace, or None if no spellspace is active.
        """
        self.check_cleaned()
        return self._spellspace_stack.get_active()

    def create_spellspace(self) -> SpellSpace:
        """
        Create a SpellSpace bound to this Conduit.

        Purpose:
            Create a new spellspace scope owned by this Conduit and register
            it for cleanup bookkeeping.
        Contract:
            - Returns a new SpellSpace owned by this Conduit.
            - The SpellSpace is registered in the spellspace registry.
            - Lifecycle is manual unless used via `enter_spellspace`.

        Returns:
            SpellSpace: A new SpellSpace owned by this Conduit.
        """
        self.check_cleaned()
        return self._spellspace_pool.acquire()

    def _register_spellspace(self, space: SpellSpace) -> None:
        """
        Internal

        Track a SpellSpace for cleanup bookkeeping.

        Contract:
            - Adds the spellspace to the registry.
            - Safe to call multiple times for the same spellspace.

        Args:
            space (SpellSpace): The spellspace to track.
        """
        self._spellspace_registry.add(space)

    def _unregister_spellspace(self, space: SpellSpace) -> None:
        """
        Internal

        Remove a SpellSpace from cleanup bookkeeping.

        Contract:
            - Removes the spellspace from the registry if present.
            - Safe to call multiple times for the same spellspace.

        Args:
            space (SpellSpace): The spellspace to untrack.
        """
        self._spellspace_registry.discard(space)

    @contextmanager
    def enter_spellspace(self) -> Generator[SpellSpace, None, None]:
        """
        Context-managed SpellSpace. Pushes one thread-local scope, yields it,
        and cleans it on exit.

        Usage:
            with conduit.enter_spellspace() as space:
                space.meld(...)

        Ensures:
            - SpellSpace is activated before use as the current top-of-stack.
            - SpellSpace is cleaned on exit, even on exceptions.
            - Nested spellspace activation on the same thread is supported by
              push/pop stack semantics.
            - Stack integrity is validated to detect misuse.

        Yields:
            SpellSpace: The newly created, active spellspace for the duration of the context.

        Raises:
            SpellSpaceScopeError:
                If stack integrity is violated on exit.
        """
        space = self.create_spellspace()
        stack = self._spellspace_stack.get()
        stack.append(space)
        self._spellspace_stack.set(stack)
        try:
            yield space
        finally:
            stack = self._spellspace_stack.get()
            if not stack or stack[-1] is not space:
                raise SpellSpaceScopeError(
                    "SpellSpace stack corruption detected while exiting."
                )
            stack.pop()
            self._spellspace_stack.set(stack)
            space.cleanup()



    def _configure_logger(self, logger: Any) -> Any:
        """
        Internal

        Configures the logger for this Conduit.

        Args:
            logger (Any): The explicit logger instance, if one was supplied.
        Returns:
            SafeLogger: The configured SafeLogger instance.
        """
        if logger is not None:
            return InitHelpers.resolve_safe_logger(logger)
        return InitHelpers.resolve_channel_logger(
            self,
            groups=["lifecycle", "organization"],
            system_groups=["spellbook", "aether"],
            props={
                "aether_frame": self._aetheric_frame_name,
                "conduit_state": str(self._conduit_state),
            },
            channels="system",
        )

    def _refresh_devops_identity_state(self) -> None:
        """
        Internal

        Refresh the conduit dev-ops identity to match current runtime posture.

        Purpose:
            Keep the identity metadata and declared transaction surface aligned
            with the conduit role and dynamic posture, including lesser ->
            normal upgrade.
        """
        available_transactions: Tuple[str, ...] = tuple()
        if self._conduit_state is ConduitState.normal:
            available_transactions = (
                "bind",
                "scan",
                "link",
                "cluster_link",
                "mutation",
                "transfer_ownership",
            )
        self._transaction_identity.set_available_transactions(
            available_transactions
        )
        self._transaction_identity.update_metadata(
            conduit_id=self._id,
            spellbook_id=self._spellbook._id,
            conduit_state=self._conduit_state.value,
            root_conduit_id=self._root_conduit_id,
            dynamic_environment=self.__dynamic_environment__,
            parent_conduit_id=None,
        )

    def _bind_family_blocked_for_current_posture(self) -> bool:
        """
        Internal

        Return whether bind-family entry is disabled for this live conduit.

        Contract:
            - Conduits are post-conjure runtime objects, so
              `disable_all_transactions_after_conjure` applies immediately.
            - Non-dynamic posture blocks bind-family entry here even if the
              narrow disable flag is not set explicitly.
        """
        frame_configuration = self._spellbook._aetheric_frame_configuration
        if frame_configuration is None:
            return not self.__dynamic_environment__
        if frame_configuration.disable_bind:
            return True
        if frame_configuration.disable_all_transactions_after_conjure:
            return True
        return frame_configuration.system_state is not SystemState.dynamic

    def _transaction_blocked_for_current_posture(
            self,
            transaction_name: Optional[str],
    ) -> bool:
        """
        Internal

        Return whether one conduit transaction kind is blocked by frame posture.

        Contract:
            - Bind-family requests use the narrower bind/scan gate.
            - All other dynamic transaction families are blocked when the frame
              is not dynamic or when their specific disable flag is set.
        """
        if not transaction_name:
            return False
        frame_configuration = self._spellbook._aetheric_frame_configuration
        if frame_configuration is None:
            return transaction_name != "bind" and not self.__dynamic_environment__
        if transaction_name == "bind":
            return self._bind_family_blocked_for_current_posture()
        if frame_configuration.disable_all_transactions_after_conjure:
            return True
        if transaction_name == "link":
            return (
                frame_configuration.disable_linking
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == "transfer_ownership":
            return (
                frame_configuration.disable_transfer_of_ownership
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == "cluster_link":
            return (
                frame_configuration.disable_conduit_cluster
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == "mutation":
            return (
                frame_configuration.disable_mutations
                or frame_configuration.system_state is not SystemState.dynamic
            )
        return False

    def _resolve_logger_from_config(self) -> SafeLogger:
        """
        Internal

        Resolve a channel-backed SafeLogger from the supplied configuration context.

        Args:
            configuration (SpellbookConfiguration):
                The locked configuration driving conduit construction.

        Returns:
            SafeLogger: Resolved conduit logger instance.
        """
        return InitHelpers.resolve_channel_logger(
            self,
            groups=["lifecycle", "organization"],
            system_groups=["spellbook", "aether"],
            props={
                "aether_frame": self._aetheric_frame_name,
                "conduit_state": str(self._conduit_state),
            },
            channels="system",
        )

    def _configure_conduit_state(self) -> None:
        """
        Internal

        Configures the conduit state based on the provided configuration.

        Raises:
            RuntimeError: If normal conduit registration fails.
        """
        if self._conduit_state == ConduitState.normal:
            try:
                self._add_root_conduit()
                self._add_spells_to_aether()
            except Exception as e:
                self._logger.error(f"Normal conduit registration failed: {e}", "__init__", exc_info=True)
                raise
        elif self._conduit_state is ConduitState.lesser:
            if self._name is not None:
                self._logger.warning("Lesser conduits cannot have a name. Overriding to None.", "__init__")
                self._name = None

    def _register_to_creations(self, spell: Spell, instance: Any) -> None:
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
          `Creations.add_creation(...)`.
        - Disposal metadata from the spell is forwarded only when the retained
          entry actually needs explicit disposal tracking.

        This is primarily used during the conjure flow when a Conduit is
        first wired into its Spellbook and needs to prime its Creations
        store with pre-existing objects.
        """
        # Existing-object spells are semantically singletons in Melder.
        existence: Existence = spell.existence
        if spell.existence is not Existence.unique:
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
        self._creations.add_creation(
            spell_id,
            instance,
            has_disposal_methods=spell.has_disposal_methods,
            disposal_methods=spell.disposal_method_names,
        )



    #region Context Management
    def __enter__(self) -> "Conduit":
        """
        Public API

        Enter the conduit lock context and return `self`.

        Purpose:
            Allow internal or advanced coordinated operations to hold the conduit lock
            across a controlled block without exposing `_lock` directly.

        Returns:
            Conduit:
                This conduit instance while the lock is held.

        """
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Public API

        Exit the conduit lock context.

        Returns:
            None.

        """
        self._lock.release()

    #endregion Context Management
    #region Logger
    #endregion Logger
    #region Utilities
    def __repr__(self) -> str:
        """
        Public API

        Return a concise diagnostic representation of this conduit.

        Returns:
            str:
                Human-readable representation including conduit name and id.

        """
        self.check_cleaned()
        return (
            f"<Conduit name={self.name} "
            f"id={self._id}>"
        )

    #endregion Utilities

    #region Properties
    @property
    def id(self) -> str:
        """
        Public API

        Return the unique identifier of this conduit.

        Returns:
            str:
                This conduit's unique identifier.

        """
        self.check_cleaned()
        return self._id

    @property
    def name(self) -> Optional[str]:
        """
        Public API

        Return the human-readable name for this conduit, if one exists.

        Returns:
            Optional[str]:
                The configured conduit name, or `None` when the conduit is unnamed.

        """
        self.check_cleaned()
        return self._name if self._name else None


    @name.setter
    def name(self, name: str) -> None:
        """
        Public API

        Assign a name to this conduit exactly once.

        Contract:
            - Conduit names are write-once after creation.
            - Intended primarily for normal conduits that will participate in cloud or
              diagnostics surfaces.

        Args:
            name (str):
                Name to assign to this conduit.

        Raises:
            RuntimeError:
                If the conduit name is already set.

        """
        self.check_cleaned()
        if self._name is not None:
            self._logger.error("Attempt to rename conduit after name set", "name")
            raise RuntimeError("Conduit name is set.")
        self._name = name

    def get_conduit_cloud(self) -> "ConduitCloud":
        """
        Public API

        Return the frame-owned conduit cloud tied to this conduit.

        Returns:
            ConduitCloud: The `ConduitCloud` managed by this conduit’s
              `AethericFrame`.

        Raises:
            RuntimeError: If the conduit is cleaned.
        """
        self.check_cleaned()
        return self._aetheric_frame._conduit_cloud

    #endregion

    #region Conduit Configuration
    def register_conduit_hooks(
            self,
            hooks: dict[str, Any],
    ) -> None:
        """
        Public API

        Register hook callables for this Conduit.

        Hooks are always registered locally on this Conduit and do not propagate
        to other conduits or mutate the shared Configuration hook registry.

        Args:
            hooks: Mapping of hook name -> callable or iterable of callables.

        Raises:
            RuntimeError: If the conduit is cleaned.
            ValueError / TypeError: If hook names or values are invalid.
        """
        self.check_cleaned()
        if not hooks:
            return

        conduit_hook_updates: dict[str, Any] = {}
        meld_hook_updates: dict[str, Any] = {}
        for name, value in hooks.items():
            if name in self._configuration._MELD_HOOK_NAMES:
                meld_hook_updates[name] = value
            else:
                conduit_hook_updates[name] = value

        if conduit_hook_updates:
            self._ensure_local_conduit_hooks()
            local_conduit_hooks = self._local_conduit_hooks
            if local_conduit_hooks is None:
                raise RuntimeError("Local conduit hooks were not initialized.")
            self._merge_conduit_hooks(local_conduit_hooks, conduit_hook_updates)

        if meld_hook_updates:
            local_meld_hooks: dict[str, list[Any]] = {}
            self._merge_conduit_hooks(local_meld_hooks, meld_hook_updates)
            self._meld.set_meld_hooks(
                local_meld_hooks,
                create_local_hooks=True,
                overwrite=False,
            )

    def _add_root_conduit(self) -> None:
        """
        Internal

        Add this normal conduit into the current frame's root-conduit state.

        Raises:
            ValueError: If the conduit id or name already exists in the frame.
        """
        self._aetheric_frame.register_root_conduit(self)

    def _remove_root_conduit(self) -> None:
        """
        Internal

        Remove this normal conduit from the current frame's root-conduit state.

        Raises:
            ValueError: If the conduit is not present in the frame state.
        """
        self._aetheric_frame.unregister_root_conduit(self)


    #endregion Conduit Configuration
    #region Conduit Management
    def _ensure_local_conduit_hooks(self) -> None:
        """
        Internal

        Ensure the conduit has a local hook map for conduit-only overlays.

        Contract:
            - Local hooks are stored separately from shared lineage hooks.
            - Shared hook references remain intact.
        """
        if self._local_conduit_hooks is None:
            self._local_conduit_hooks = {}

    def _merge_conduit_hooks(self, hook_map: dict[str, list[Any]], hooks: dict[str, Any]) -> None:
        """
        Internal

        Merge hook values into the provided hook map.

        Contract:
            - Hook names must be in Configuration._ALLOWED_HOOKS.
            - Hook values must be a callable or a list/tuple of callables.
        """
        for name, value in hooks.items():
            if name not in self._configuration._ALLOWED_HOOKS:
                raise ValueError(f"Unknown hook name: {name!r}")
            if callable(value):
                hook_map.setdefault(name, []).append(value)
                continue
            if not isinstance(value, (list, tuple)):
                raise TypeError(
                    f"Value for hook '{name}' must be a callable or a list/tuple of callables."
                )
            for fn in value:
                if not callable(fn):
                    raise TypeError(
                        f"All entries for hook '{name}' must be callable."
                    )
            hook_map.setdefault(name, []).extend(value)

    def _collect_conduit_hook_chain(self, hook_name: str) -> list[Callable[..., Any]]:
        """
        Internal

        Collect the effective hook sequence for a hook name.

        Contract:
            - Local conduit hooks override shared conduit hooks for the same
              hook name.
            - Returned list is detached from internal maps only when needed.
        """
        if self._local_conduit_hooks is not None:
            local_hooks = self._local_conduit_hooks.get(hook_name)
            if local_hooks:
                return list(local_hooks)

        if self._conduit_hooks is not None:
            shared_hooks = self._conduit_hooks.get(hook_name)
            if shared_hooks:
                return list(shared_hooks)

        return []

    def _create_gate_for_current_root(self, conduit_id: str) -> CreationGate:
        """
        Internal

        Create and register a gate under this conduit's current root id.

        Purpose:
            Centralize conduit gate creation so root-lineage indexing is
            always applied consistently.

        Args:
            conduit_id (str):
                Conduit id used as the gate registry key.

        Returns:
            CreationGate:
                Newly created gate registered on the active controller.

        Raises:
            RuntimeError:
                Propagated if the controller has been cleaned.
            ValueError:
                Propagated for invalid or duplicate conduit/root keys.
        """
        return self._creation_gate_controller.create_conduit_gate(
            conduit_id,
            root_conduit_id=self._root_conduit_id,
        )

    def _register_existing_gate_for_current_root(
            self,
            conduit_id: str,
            gate: CreationGate,
    ) -> None:
        """
        Internal

        Register an existing gate under this conduit's current root id.

        Purpose:
            Attach caller-provided gate instances into controller lineage
            indices using current conduit root metadata.

        Args:
            conduit_id (str):
                Conduit id used as the gate registry key.
            gate (CreationGate):
                Existing gate instance to register.

        Returns:
            None.

        Raises:
            RuntimeError:
                Propagated if the controller has been cleaned.
            ValueError:
                Propagated for invalid or duplicate conduit/root keys.
        """
        self._creation_gate_controller.register_conduit_gate(
            conduit_id,
            gate,
            root_conduit_id=self._root_conduit_id,
        )

    def _set_creation_gate_controller_for_lineage(self) -> None:
        """
        Internal

        Rebind this conduit lineage into the frame-owned CreationGateController.

        Purpose:
            Ensure every conduit in the lineage is registered in the same
            DevOps-owned controller under the current root conduit id.

        Contract:
            - Requires a live conduit instance (`check_cleaned()` enforced).
            - Requires a live ConduitWard lineage on this conduit.
            - Uses `self._creation_gate_controller` as the single authority.
            - Re-registers each conduit's current gate under the current root id.
            - Creates a gate when a conduit has no existing gate.
            - Uses the ConduitWard lineage map to find descendants.
            - Uses strict controller calls (no swallowed errors or legacy paths).

        Threading:
            - Reads descendant snapshots under ConduitWard lock before
              recursive rebinding.

        Returns:
            None.
        """
        creation_gate_controller = self._creation_gate_controller
        if self._creation_gate is None:
            existing = creation_gate_controller.get_conduit_gate(self._id)
            if existing is None:
                self._creation_gate = self._create_gate_for_current_root(self._id)
            else:
                self._creation_gate = existing
        else:
            creation_gate_controller.unregister_conduit_gate(self._id)
            self._register_existing_gate_for_current_root(self._id, self._creation_gate)

        ward = self._conduit_ward
        with ward._lock:
            lesser_conduits = list(ward._lesser_conduits.values())
        for lesser_conduit in lesser_conduits:
            lesser_conduit._creation_gate_controller = creation_gate_controller
            lesser_conduit._root_conduit_id = self._root_conduit_id
            lesser_conduit._meld._resolution_conduit_id = self._root_conduit_id
            lesser_conduit._set_creation_gate_controller_for_lineage()

    def upgrade_to_normal(
            self,
            name: str,
            *,
            hooks: dict[str, Any] | None = None,
    ) -> None:
        """
        Public API

        Upgrades this Conduit from a lesser to a **normal** state.

        This process allows the conduit to create its own links through the Aether system.
        It effectively forks this conduit into a new tree, retaining its children and
        creation data, and establishes new links with the parent. The local Meld is
        rewired to the new Creations manager after transfer. Only a normal conduit
        can access the Spellbook to bind new spells.

        Optionally, in **dynamic mode**, you can supply a `hooks` mapping that will be
        registered through register_conduit_hooks(...) and attached only to this
        upgraded conduit:

            hooks = {
                "on_meld_pre_resolve": trace_before_meld,
                "on_conduit_post_link": [log_link, audit_link],
            }

        The hooks mapping shape is:

            hook_name -> callable | list[callable] | tuple[callable, ...]

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
            ValueError / TypeError:
                Propagated from register_conduit_hooks(...) if the hook set is invalid
                (unknown hook names, non-callables, etc.).
        Contract:
            - Preserves the current creations manager during lesser -> normal upgrade.
            - Rewires Meld/CreationContext execution to use the current creations manager.
            - Seeds per-conduit resolution state from the prior root conduit when available.
            - Rebinds lineage gates to the frame DevOps CreationGateController.
        """
        self.check_cleaned()
        with self._lock:
            if not self.__dynamic_environment__:
                self._logger.error("upgrade_to_normal in non-dynamic env", "upgrade_to_normal")
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._conduit_state != ConduitState.lesser:
                self._logger.error("upgrade_to_normal called when not lesser", "upgrade_to_normal")
                raise RuntimeError("Only lesser conduits can be upgraded.")

            try:
                # Snapshot root conduit resolution state before converting lineage.
                spell_system_states = None
                source_resolution_state = None
                source_conduit_id = None
                if self._spellbook is not None:
                    spell_system_states = self._spellbook._spell_system_states
                if spell_system_states is not None and self._conduit_ward is not None:
                    try:
                        root_conduit = self._conduit_ward.root_conduit
                    except Exception:
                        root_conduit = None
                    if root_conduit is not None:
                        source_conduit_id = root_conduit._id
                        source_resolution_state = spell_system_states.get_conduit_resolution_state(
                            source_conduit_id
                        )

                # Step 1: Change state + root name
                self._conduit_state = ConduitState.normal
                self._root_conduit_id = self._id
                self._name = name
                if self._transaction_identity._registry is None:
                    self._transaction_identity.attach_registry(
                        self._aetheric_frame.devops_information_registry,
                        object_ref=self,
                    )
                self._refresh_devops_identity_state()
                self._conduit_pool = ConduitPool(
                    root_conduit=self,
                    baseline_idle=10,
                    max_idle=10,
                )

                # Step 2: Keep the current creations object.
                # The creations owner id already matches this conduit id, so
                # lesser -> normal upgrade does not need to rebind ownership
                # metadata on the creations manager itself.

                # Step 2.1: Ensure Meld uses the same creations manager.
                if self._meld is not None:
                    self._meld._creations = self._creations
                    self._meld._resolution_conduit_id = self._root_conduit_id

                # Step 3: Reconfigure the conduit ward
                self._conduit_ward._convert_to_normal_conduit()
                self._transaction_identity.update_metadata(parent_conduit_id=None)

                # Step 3.5: Rebind gates for this lineage to the injected
                # frame-owned DevOps controller.
                self._set_creation_gate_controller_for_lineage()

                # Step 4: Reconfigure the spellbook
                self._spellbook.create_new_preset_spellbook()

                # Step 4.5: Seed resolution state from the former root conduit.
                if (
                        spell_system_states is not None
                        and source_resolution_state is not None
                        and source_conduit_id
                        and source_conduit_id != self._id
                ):
                    try:
                        target_state = spell_system_states.get_or_create_conduit_resolution_state(self._id)
                        target_state.bulk_set_spell_validity(
                            source_resolution_state.snapshot_spell_validity()
                        )
                        target_state.bulk_set_root_validity(
                            source_resolution_state.snapshot_root_validity()
                        )
                        target_state.record_diagnostics(
                            source_resolution_state.list_diagnostics()
                        )
                        if source_resolution_state.is_dirty():
                            target_state.mark_dirty()
                        else:
                            last_validated_at = source_resolution_state.last_validated_at()
                            if last_validated_at is not None:
                                target_state.clear_dirty(last_validated_at)
                    except Exception:
                        self._logger.error(
                            "Failed to seed conduit resolution state from root conduit.",
                            "upgrade_to_normal",
                            exc_info=True,
                        )

                # Step 5: Register as a full Conduit in frame-owned runtime state.
                self._add_root_conduit()

                # Step 6: If the caller supplied per-conduit hooks, register them now.
                if hooks:
                    self.register_conduit_hooks(hooks)

                self._publish_frame_record_to_nexus()
                self._publish_conduit_record_to_nexus()

            except Exception as e:
                self._logger.error(f"upgrade_to_normal failed: {e}", "upgrade_to_normal", exc_info=True)
                raise




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
        with self._lock:
            self._conduit_ward._set_new_policy(policy)

        self._publish_conduit_record_to_nexus()

    def create_lesser_conduit(self, logger: Any | None = None) -> "Conduit":
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook, Configuration, and
        injected frame-owned services, but is restricted in its ability to
        establish external links or register new spells. It owns a
        conduit-local CreationGate created by the lineage CreationGateController.
        Fresh lesser creation is published to Nexus when passive ingest is
        enabled. Reused pooled lesser conduits are reactivated locally without
        republishing or refreshing dev-ops identity metadata.

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
            Conduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent Conduit is cleaned.
        """
        self.check_cleaned()

        with self._lock:
            root_conduit: Optional["Conduit"]
            if self._conduit_state == ConduitState.normal:
                root_conduit = self
            else:
                if self._conduit_ward is None:
                    raise RuntimeError("Root conduit is not set for this lineage.")
                root_conduit = self._conduit_ward.root_conduit
            if root_conduit is None:
                raise RuntimeError("Root conduit is not set for this lineage.")
            if root_conduit._conduit_state != ConduitState.normal:
                raise RuntimeError("Root conduit must be a normal conduit.")
            root_conduit_id = root_conduit._id
            if self._conduit_hooks or self._local_conduit_hooks:
                # 1) Pre-create hook on the parent, if any.
                self._fire_conduit_hooks(
                    "on_conduit_pre_created",
                    self,  # parent_conduit
                )
                # 2) Construct the lesser conduit (activation point).
                new_conduit = root_conduit._conduit_pool.create_object()
                reused_from_pool = new_conduit is not None
                if new_conduit is None:
                    new_conduit = Conduit(
                        spellbook=self._spellbook,
                        configuration=self._configuration,
                        conduit_state=ConduitState.lesser,
                        aetheric_frame_name=self._aetheric_frame_name,
                        aetheric_frame=self._aetheric_frame,
                        policy=Policies.default,
                        dynamic=self.__dynamic_environment__,
                        logger=logger,
                        root_conduit_id=root_conduit_id,
                        creation_gate_controller=self._creation_gate_controller,
                        conduit_hooks=root_conduit._conduit_hooks,
                        meld_hooks=root_conduit._meld_hooks,
                    )
                new_conduit._conduit_state = ConduitState.lesser
                new_conduit._conduit_ward._conduit_type = ConduitState.lesser
                new_conduit._nexus_publish_enabled = self._nexus_publish_enabled

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
                if not reused_from_pool:
                    new_conduit._publish_conduit_record_to_nexus()
            else:
                new_conduit = root_conduit._conduit_pool.create_object()
                reused_from_pool = new_conduit is not None
                if new_conduit is None:
                    new_conduit = Conduit(
                        spellbook=self._spellbook,
                        configuration=self._configuration,
                        conduit_state=ConduitState.lesser,
                        aetheric_frame_name=self._aetheric_frame_name,
                        aetheric_frame=self._aetheric_frame,
                        policy=Policies.default,
                        dynamic=self.__dynamic_environment__,
                        logger=logger,
                        root_conduit_id=root_conduit_id,
                        creation_gate_controller=self._creation_gate_controller,
                        conduit_hooks=root_conduit._conduit_hooks,
                        meld_hooks=root_conduit._meld_hooks,
                    )
                new_conduit._conduit_state = ConduitState.lesser
                new_conduit._conduit_ward._conduit_type = ConduitState.lesser
                new_conduit._nexus_publish_enabled = self._nexus_publish_enabled
                self._conduit_ward._link_lesser_conduit(new_conduit)
                if not reused_from_pool:
                    new_conduit._publish_conduit_record_to_nexus()

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
        self._spellbook._register_conduit_spells_in_aether(self._id)



    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional["Conduit"]:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        This method queries the Aether to find the original source conduit for a specific spell ID.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Conduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellbook._get_conduit_by_spell_id(
                spell_id,
                aetheric_frame_name,
            )

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
            return self._spellbook._check_spell_id_in_aether(
                spell_id,
                aetheric_frame_name,
            )


    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Spell]:
        """
        Public API

        Retrieves a spell object by its unique version identifier (spell_id) from the
        spellbook of its owner.

        The method:
          1) Uses Aether to locate the owning conduit.
          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains
             this version ID.
          3) Returns the corresponding Spell instance if found.

        Args:
            spell_id (str): The unique version identifier of the spell (SHA256).
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Spell]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
            spell_id,
            aetheric_frame_name,
        )

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
    ) -> Optional[Spell]:
        """
        Public API

        Retrieve a spell object by its stable SpellIndex lineage id.

        Purpose:
            Expose the Spellbook-owned stable-lineage lookup path on the
            conduit facade so higher runtime surfaces can consume
            `spell_index_id` directly.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id (ULID) to resolve.

        Returns:
            Optional[Spell]:
                Matching spell object when found, otherwise None.

        Raises:
            RuntimeError:
                If the Conduit has been cleaned or the Spellbook is unavailable.
        """
        self.check_cleaned()
        spellbook = self._spellbook
        if spellbook is None:
            self._logger.error(
                "Spellbook is unavailable.",
                "get_spell_by_index_id",
                exc_info=True,
            )
            raise RuntimeError("Spellbook is unavailable.")
        return spellbook.get_spell_by_index_id(spell_index_id)


    def find_contracted_spell(self, spell_id: str) -> Optional[Spell]:
        """
        Internal

        Locate a contracted spell by its version spell_id across all peer
        conduits in this Spellbook.

        Args:
            spell_id (str): The unique version ID (SHA) of the spell to find.

        Returns:
            Optional[Spell]: The contracted spell instance, or None if not found.
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
          2) Spellbook._find_spell(SpellIndex) to retrieve the Spell.
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
        # This will raise RuntimeError if the key is not found; we translate to ValueError
        try:
            spell_index = self._spellbook.find_spell_index(spellframe, spell_name, binding_name)
        except RuntimeError as e:
            self._logger.error(str(e), "find_spell_id")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.") from e

        if spell_index is None:
            self._logger.error(f"Spell '{spell_name}' not found", "find_spell_id")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")

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
        spell_key = self._spellbook.find_spell_key(spellframe, spell_name, binding_name)
        if not spell_key:
            self._logger.error(f"Spell key for '{spell_name}' not found", "find_spell_key")
            raise ValueError(f"Spell '{spell_name}' not found in the spellbook.")
        return spell_key

    def _get_required_transaction_mediator(self) -> "TransactionMediator":
        """
        Internal

        Return the frame-owned live transaction mediator.

        Returns:
            TransactionMediator:
                Transaction mediator instance owned by the frame control plane.
        """
        return self._spellbook._get_required_transaction_mediator()

    def inspect_spell(
            self,
            spell: Any,
            aetheric_frame: str = "default",
    ) -> Optional[str]:
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

    def begin_transaction(
            self,
            transaction_type: str,
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["Conduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Conduit.

        Purpose:
            Admit a mutation request through the frame-owned transaction
            mediator and, for bind transactions, open the bind-family
            transaction window.
        Contract:
            - Only normal conduits may begin change-control transactions.
            - Admission is serialized by the mediator-owned change-control
              pipeline.
            - Bind transactions open the binding transaction window.
            - Link transactions must explicitly include the local conduit and peers.
            - Link and transfer transactions require dynamic mode.
        Args:
            transaction_type:
                Transaction type string value (e.g. "bind", "link").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
                Link transactions require explicit conduit objects.
            conduits:
                Optional list of conduit objects participating in the request.
                For link transactions, include the local conduit and peers.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If change-control admission is denied.
            RuntimeError: If a link transaction omits required conduit objects.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        Threading:
            Uses the Spellbook lock for local state; orchestrator handles admission state.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("begin_transaction called when conduit is not normal", "begin_transaction")
            raise RuntimeError("Only normal conduits can start change transactions.")
        mediator = self._get_required_transaction_mediator()
        existing_request = mediator.get_active_request()

        request_type_value: Optional[str] = None
        if isinstance(transaction_type, str):
            request_type_value = transaction_type.strip().lower()

        dynamic_only = {
            "link",
            "transfer_ownership",
            "mutation",
            "cluster_link",
        }
        if request_type_value in dynamic_only and not self.__dynamic_environment__:
            self._logger.error(
                "begin_transaction in non-dynamic env",
                "begin_transaction",
            )
            raise RuntimeError(
                "[CONDUIT] Change transactions require dynamic mode. "
                f"transaction_type='{request_type_value}'."
            )
        if self._transaction_blocked_for_current_posture(request_type_value):
            self._logger.error(
                "begin_transaction denied by current frame posture",
                "begin_transaction",
            )
            raise RuntimeError(
                "[CONDUIT] Change transaction is disabled for the current frame posture. "
                f"transaction_type='{request_type_value}'."
            )

        conduit_values: list[str] = []
        if conduits:
            for conduit in conduits:
                if not isinstance(conduit, Conduit):
                    self._logger.error(
                        "begin_transaction received non-conduit object",
                        "begin_transaction",
                    )
                    raise TypeError(
                        "conduits must contain Conduit-compatible objects."
                    )
                if conduit._id not in conduit_values:
                    conduit_values.append(conduit._id)

        if request_type_value == "link":
            if conduit_ids:
                for conduit_id in conduit_ids:
                    if conduit_id not in conduit_values:
                        conduit_values.append(conduit_id)
            link_metadata = dict(metadata) if metadata is not None else {}
            link_metadata.update({
                "origin_surface": "conduit.link",
                "conduit_ids": tuple(conduit_values),
                "scope_keys": tuple(scope_keys) if scope_keys is not None else tuple(),
                "scope_hashes": tuple(scope_hashes) if scope_hashes is not None else tuple(),
                "binding_keys": tuple(binding_keys) if binding_keys is not None else tuple(),
                "contract_keys": tuple(contract_keys) if contract_keys is not None else tuple(),
            })
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type="link",
                metadata=link_metadata,
            )
            return
        if request_type_value == "bind":
            self._spellbook.begin_transaction(
                "bind",
                conduit_id=self._id,
                scope_keys=scope_keys,
                scope_hashes=scope_hashes,
                binding_keys=binding_keys,
                metadata=metadata,
            )
            return
        if request_type_value == "transfer_ownership":
            transfer_metadata = dict(metadata) if metadata is not None else {}
            transfer_metadata.setdefault(
                "origin_surface",
                "conduit.transfer_spell_ownership",
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type="transfer_ownership",
                metadata=transfer_metadata,
            )
            return

        scope_values = list(scope_keys) if scope_keys else []
        base_scope = f"scope:conduit:{self._id}"
        if base_scope not in scope_values:
            scope_values.append(base_scope)
        if conduit_ids:
            for conduit_id in conduit_ids:
                if conduit_id not in conduit_values:
                    conduit_values.append(conduit_id)
        if self._id not in conduit_values:
            conduit_values.append(self._id)
        mediator.begin_transaction(
            identity=self._transaction_identity,
            transaction_type=transaction_type,
            existing_request_id=(
                existing_request.request_id
                if existing_request is not None
                else None
            ),
            initiator_conduit_id=self._id,
            spellbook_id=self._spellbook._id,
            conduit_ids=conduit_values,
            scope_keys=scope_values,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )

    def end_transaction(
            self,
            transaction_type: Optional[str] = None,
            *,
            success: bool = True,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Conduit.

        Purpose:
            Finalize an admitted change-control request through the
            mediator-owned transaction pipeline.
        Contract:
            - Only normal conduits may end change-control transactions.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        Threading:
            Uses the Spellbook lock for local state; orchestrator handles admission state.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("end_transaction called when conduit is not normal", "end_transaction")
            raise RuntimeError("Only normal conduits can end change transactions.")
        request_type_value: Optional[str] = None
        if isinstance(transaction_type, str):
            request_type_value = transaction_type.strip().lower()
        if request_type_value == "bind":
            self._spellbook.end_transaction("bind", success=success)
            return
        self._get_required_transaction_mediator().end_transaction(
            expected_type=transaction_type,
            success=success,
        )

    @contextmanager
    def transaction(
            self,
            transaction_type: str,
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["Conduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator["Conduit", None, None]:
        """
        Public API

        Context-managed change-control transaction for this Conduit.

        Purpose:
            Provide a safe begin/end wrapper for change-control transactions.
        Contract:
            - Begins a change-control transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Only normal conduits may enter this context.
            - Link transactions must explicitly include the local conduit and peers.
            - Link and transfer transactions require dynamic mode.
        Args:
            transaction_type:
                Transaction type string value (e.g. "bind", "link").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
                Link transactions require explicit conduit objects.
            conduits:
                Optional list of conduit objects participating in the request.
                For link transactions, include the local conduit and peers.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Yields:
            Conduit: The current Conduit instance for the duration of the transaction context.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If change-control admission is denied.
            RuntimeError: If a link transaction omits required conduit objects.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        self.check_cleaned()
        self.begin_transaction(
            transaction_type,
            conduit_ids=conduit_ids,
            conduits=conduits,
            scope_keys=scope_keys,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        try:
            yield self
        except Exception:
            self.end_transaction(transaction_type=transaction_type, success=False)
            raise
        else:
            self.end_transaction(transaction_type=transaction_type, success=True)

    def bind(
            self,
            *,
            spell: Any,
            existence: str | Existence,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Bind a spell into the Spellbook for future instantiation and dependency injection.

        Purpose:
            Register one class, function, lambda, or existing object through this
            conduit's Spellbook so later meld work can resolve it by spell identity,
            `(spellframe, binding_name)` lookup key, and lifecycle policy.

        Contract:
            - Only normal conduits may bind spells.
            - Requires an active binding transaction.
            - Delegates the actual bind pipeline to the owning Spellbook and returns
              the resulting `spell_id`.
            - Propagates lifecycle hooks only after validating that supplied hook values
              are callable.

        Permissions:
            - `read` lets other conduits consume the spell but not create new instances.
            - `create` lets other conduits consume and instantiate the spell.
            - `block` restricts access to the owning conduit.

        Lookup semantics:
            - `spellframe` provides the primary namespace or grouping key.
            - `binding_name` provides the secondary disambiguation key inside that
              frame.

        Optional lifecycle hooks (`**kwargs`):
            - `pre_hooks`
            - `activation_hooks`
            - `post_hooks`

        Args:
            spell (Any):
                The class, function, lambda, or existing object to register.
            existence (Existence):
                Lifecycle scope for the spell.
            permissions (str):
                Permission level exposed to other conduits (`read`, `create`, or
                `block`).
            spellframe:
                Logical interface, frame, or grouping key for the spell.
            binding_name:
                Secondary key used to distinguish this spell among others in the same
                frame.
            profile (str):
                Spell profile family to attach after bind completion.
            **kwargs:
                Optional lifecycle hooks and related bind-time metadata.

        Returns:
            str:
                The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError:
                If the conduit is cleaned, is not normal, no binding transaction is
                active, or the spell collides with an existing registry entry.
            TypeError:
                If invalid hook types are provided.

        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("bind called when conduit is not normal", "bind")
            raise RuntimeError("Only normal conduits can bind spells.")
        if self._bind_family_blocked_for_current_posture():
            self._logger.error("bind denied by current frame posture", "bind")
            raise RuntimeError(
                "[CONDUIT] Bind is disabled for the current frame posture."
            )
        with self.transaction("bind"):
            with self._lock:
                return self._spellbook._bind_under_active_transaction(
                    spell=spell,
                    existence=existence,
                    spellframe=spellframe,
                    binding_name=binding_name,
                    profile=profile,
                    permissions=permissions,
                    **kwargs,
                )

    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them into this
        Conduit's Spellbook.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        If a binding transaction is already active on the owning Spellbook,
        this call reuses that transaction window. Otherwise the conduit opens
        and closes its own binding transaction around the scan so direct
        conduit-side scans remain transaction-correct.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If an incompatible change transaction is already active.
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("scan called when conduit is not normal", "scan")
            raise RuntimeError("Only normal conduits can scan modules.")
        if self._bind_family_blocked_for_current_posture():
            self._logger.error("scan denied by current frame posture", "scan")
            raise RuntimeError(
                "[CONDUIT] Scan is disabled for the current frame posture."
            )
        with self.transaction("bind"):
            with self._lock:
                return Scan(self._spellbook).scan_module(module)


    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its version spell_id, **within this
        conduit.
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
            target_spell: Optional[Spell] = None

            # Walk local SpellIndex keys and check which lineage owns this version
            for spell_index, spell in self._spellbook._spells.items():
                if spell_index.has_version(spell_id):
                    target_spell = spell
                    break

        if target_spell is not None:
            perms = target_spell.permissions.name
            return perms

        self._logger.error(f"Spell with ID {spell_id} not found", "get_spell_permissions")
        raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")

    def get_mutation_research(self) -> MutationResearch:
        """
        Public API

        Return the Aether-owned MutationResearch root visible to this conduit.

        Purpose:
            Expose the process-wide mutation-research root through the conduit
            state to access the Aether-owned runtime surface.

        Returns:
            MutationResearch: Process-wide mutation-research root.

        Raises:
            RuntimeError:
                If the conduit has been cleaned, the conduit is not in a
                dynamic environment, or the Aether-owned MutationResearch root
                is unavailable.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            raise RuntimeError("Only normal conduits can access MutationResearch.")
        frame_configuration = self._spellbook._aetheric_frame_configuration
        if (
                not self.__dynamic_environment__
                or (
                    frame_configuration is not None
                    and (
                        frame_configuration.disable_mutations
                        or frame_configuration.disable_all_transactions_after_conjure
                    )
                )
        ):
            raise RuntimeError(
                "Dynamic environment is not enabled. Cannot access MutationResearch."
            )
        mutation_research: Optional[MutationResearch] = (
            self._spellbook._aether.mutation_research
        )
        if mutation_research is None:
            raise RuntimeError("MutationResearch is unavailable.")
        return mutation_research



    #endregion Spellbook Management API
    #region Cluster API
    def transfer_spell_ownership(
            self,
            *,
            spell: Spell | str | SpellIndex,
            target_conduit: "Conduit",
            move_creations: bool = False,
            include_dependencies: bool = False,
            force_unshare: bool = True,
            invalidate_after_transfer: bool = True,
            mark_dependencies_dirty: bool = False,
    ) -> dict:
        """
        Public API (dynamic mode)

        Transfer stewardship of a spell to another conduit.

        Contract:
            - Uses the normal `TRANSFER_OWNERSHIP` transaction path before the
              existing `TransferOfOwnership` execution helper runs.
            - Keeps request planning and admission in the mediator/strategy
              layer while leaving the irreversible runtime move in the transfer
              helper for now.

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
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("transfer_spell_ownership called when conduit is not normal", "transfer_spell_ownership")
            raise RuntimeError("Only normal conduits can transfer spell ownership.")
        if self._transaction_blocked_for_current_posture(
                "transfer_ownership",
        ):
            raise RuntimeError(
                "[CONDUIT] Ownership transfer is disabled for the current frame posture."
            )
        if not self.__dynamic_environment__:
            raise RuntimeError("Ownership transfer requires dynamic mode.")
        with self.transaction(
                "transfer_ownership",
                metadata=self._build_transfer_transaction_metadata(
                    spell=spell,
                    target_conduit=target_conduit,
                    move_creations=move_creations,
                    include_dependencies=include_dependencies,
                    force_unshare=force_unshare,
                    invalidate_after_transfer=invalidate_after_transfer,
                    mark_dependencies_dirty=mark_dependencies_dirty,
                ),
        ):
            return self._conduit_ward._transfer_spell_ownership(
                spell=spell,
                target_conduit=target_conduit,
                move_creations=move_creations,
                include_dependencies=include_dependencies,
                force_unshare=force_unshare,
                invalidate_after_transfer=invalidate_after_transfer,
                mark_dependencies_dirty=mark_dependencies_dirty,
            )

    def _build_transfer_transaction_metadata(
            self,
            *,
            spell: Spell | str | SpellIndex,
            target_conduit: "Conduit",
            move_creations: bool,
            include_dependencies: bool,
            force_unshare: bool,
            invalidate_after_transfer: bool,
            mark_dependencies_dirty: bool,
    ) -> Dict[str, object]:
        """
        Build normalized metadata for one ownership-transfer transaction.

        Purpose:
            Keep the conduit public transfer surface thin by normalizing the
            transfer request into metadata the strategy layer can validate and
            plan around before the existing `TransferOfOwnership` execution
            helper performs the runtime body.

        Contract:
            - Always records the target conduit id.
            - Records whichever stable spell identifier forms are available:
              current `spell_id` and/or stable `spell_index_id`.
            - Preserves the exact transfer-option booleans supplied by the
              caller.
            - Raises when the caller supplies an unsupported spell handle.

        Args:
            spell:
                Spell object, spell id string, or SpellIndex-like lineage
                object being transferred.
            target_conduit:
                Conduit that should become the new owner.
            move_creations:
                Whether creation state should move to the target.
            include_dependencies:
                Whether owned dependency lineages should also transfer.
            force_unshare:
                Whether borrower visibility should be stripped instead of
                repointed.
            invalidate_after_transfer:
                Whether the moved lineage should remain gated/dirty afterward.
            mark_dependencies_dirty:
                Whether dependencies should be dirtied when they are not moved.

        Returns:
            Dict[str, object]:
                Normalized transfer metadata for the strategy layer.
        """
        spell_id: Optional[str] = None
        spell_index_id: Optional[str] = None

        if isinstance(spell, str):
            spell_id = spell
        else:
            try:
                spell_id = spell.spell_id
                spell_index_id = spell.spell_index.id
            except AttributeError:
                try:
                    spell_index_id = spell.id
                    spell_id = spell.current
                except AttributeError as exc:
                    raise TypeError(
                        "spell must be a Spell-compatible object, SpellIndex-compatible "
                        "object, or spell_id string."
                    ) from exc

        metadata: Dict[str, object] = {
            "origin_surface": "conduit.transfer_spell_ownership",
            "target_conduit_id": target_conduit._id,
            "move_creations": move_creations,
            "include_dependencies": include_dependencies,
            "force_unshare": force_unshare,
            "invalidate_after_transfer": invalidate_after_transfer,
            "mark_dependencies_dirty": mark_dependencies_dirty,
        }
        if spell_id:
            metadata["spell_id"] = spell_id
        if spell_index_id:
            metadata["spell_index_id"] = spell_index_id
        return metadata
    #endregion Cluster API
    #region Meld

    def enable_meld(self) -> None:
        """
        Public API

        Enable meld execution for this conduit lineage.

        Purpose:
            Release any blocked meld calls and allow new melds to proceed.

        Contract:
            - Delegates to the local CreationGate for this conduit.
            - Gate governance is provided by DevOps CreationGateController.

        Raises:
            RuntimeError: If the Conduit has been cleaned.
        """
        self.check_cleaned()
        self._creation_gate.open()

    def disable_meld(self) -> None:
        """
        Public API

        Disable meld execution for this conduit lineage.

        Purpose:
            Block meld calls until enable_meld() is invoked.

        Contract:
            - Delegates to the local CreationGate for this conduit.
            - Gate governance is provided by DevOps CreationGateController.

        Raises:
            RuntimeError: If the Conduit has been cleaned.
        """
        self.check_cleaned()
        self._creation_gate.close()

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

        At the Conduit boundary, `meld` supports multiple root entry modes.
        Callers may resolve by:

        - `spell` as a **string** (treated as the canonical spell_id), or
        - `spell` as a **spell object** (class/function), or
        - `spellframe` as a **frame/protocol** (or string frame key), or
        - `spell_name` as a **logical name key** (string).

        These inputs are normalized and delegated to the underlying `Meld`
        instance, which resolves a concrete spell_id via SpellInputUtils.

        Resolution, reuse, and lifecycle behavior are delegated to
        the underlying Meld instance.

        In dynamic mode, this method uses the Conduit's CreationGate to control
        meld entry and track active meld tickets. In automatic mode, meld
        bypasses gate checks for a minimal hot path.

        Gate/ticketing behavior (dynamic mode only):
            - If the gate is terminally closed, raises immediately.
            - If the gate is disabled, blocks until re-enabled, then re-checks closure.
            - Registers a meld ticket for the duration of the call so the gate
              can track active work and drain safely during shutdown.

        Args:
            spell_name:
                Logical spell name (string). When provided without an explicit
                `spell` or `spellframe`, this is treated as the name-based key
                for resolution (via SpellInputUtils normalization).
            spell:
                Primary spell identifier. If a string, this is treated as the
                unique spell_id (typically the SHA256 version ID). If an
                object (class/function), it participates in key normalization.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution. If provided, it becomes the primary frame key.
            binding_name:
                Optional binding name (string) associated with the
                spell. Used as the binding key during resolution.
            spell_override:
                Optional per-call override payload (dict / list / tuple)
                passed through to Meld.meld for constructor/factory
                argument overrides.
        Returns:
            Any:
                The resolved component instance (reused or newly
                created) as returned by Meld.meld.

        Raises:
            RuntimeError:
                - If the Conduit has been cleaned.
                - If the underlying Meld instance is missing.
                - If the CreationGate is closed.
            ValueError:
                - If none of `spell_name`, `spell`, or `spellframe` are provided.
            TypeError:
                - If `spell_name` is not a string when provided.
                - If `binding_name` is not a string when provided.
            KeyError:
                Propagated from Meld.meld when a spell_id cannot be
                resolved.
            NotImplementedError:
                Propagated from Meld.meld for spell types or
                existence modes not yet implemented.
            HookExecutionError:
                Propagated from Meld.meld if hook execution fails.
        """
        self.check_cleaned()

        meld_component = self._meld

        if self.__dynamic_environment__:
            creation_gate = self._creation_gate

            if creation_gate.is_closed():
                raise RuntimeError(f"[CONDUIT: {self.id}] CreationGate is closed.")

            if not creation_gate.enabled:
                creation_gate.wait()
                if creation_gate.is_closed():
                    raise RuntimeError(f"[CONDUIT: {self.id}] CreationGate is closed.")

            try:
                # Track active melds for shutdown/drain semantics.
                creation_gate.register_ticket()
                return meld_component.meld(
                    spell_name=spell_name,
                    spell=spell,
                    spellframe=spellframe,
                    binding_name=binding_name,
                    spell_override=spell_override,
                )
            finally:
                creation_gate.unregister_ticket()

        return meld_component.meld(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )

    def meld_existing_spell(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Any:
        """
        Public API

        Return an already-existing live object for one resolved spell.

        Purpose:
            Expose the cold-path reuse-only runtime operation without adding
            branches to the hot `meld(...)` path.

        Args:
            spell_name:
                Logical spell name (string). When provided without an explicit
                `spell` or `spellframe`, this is treated as the name-based key
                for resolution.
            spell:
                Primary spell identifier as spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution.
            binding_name:
                Optional binding name associated with the spell.

        Returns:
            Any: Existing live runtime object for the resolved spell.

        Raises:
            RuntimeError:
                - If the Conduit has been cleaned.
                - If the underlying `Meld` instance is missing.
                - If the CreationGate is closed.
            ValueError:
                If the resolved spell is not currently live.
            RuntimeError:
                If the lifecycle does not support deterministic
                existing-object retrieval.
        """
        self.check_cleaned()

        meld_component = self._meld

        if self.__dynamic_environment__:
            creation_gate = self._creation_gate

            if creation_gate.is_closed():
                raise RuntimeError(f"[CONDUIT: {self.id}] CreationGate is closed.")

            if not creation_gate.enabled:
                creation_gate.wait()
                if creation_gate.is_closed():
                    raise RuntimeError(f"[CONDUIT: {self.id}] CreationGate is closed.")

            try:
                creation_gate.register_ticket()
                return meld_component.meld_existing_spell(
                    spell_name=spell_name,
                    spell=spell,
                    spellframe=spellframe,
                    binding_name=binding_name,
                )
            finally:
                creation_gate.unregister_ticket()

        return meld_component.meld_existing_spell(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    def has_live_creation(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> bool:
        """
        Public API

        Resolve a spell through the same identity path as `meld(...)`, but
        only report whether a live creation already exists.

        Purpose:
            Provide one no-create runtime probe that later static-access code
            can use to decide whether an object is already available without
            entering the meld creation path.

        Contract:
            - Mirrors the root identity inputs accepted by `meld(...)`.
            - Delegates all lookup and existence semantics to the owned
              `Meld` instance.
            - Never creates, registers, links, or mutates objects.
            - Does not interact with the dynamic creation gate, because the
              method is observational only.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            bool: True when the resolved spell already has a live creation in
            the relevant runtime scope.

        Raises:
            RuntimeError:
                If the Conduit has been cleaned or the underlying `Meld`
                instance is unavailable.
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are
                provided.
            KeyError:
                Propagated from `Meld` when a spell cannot be resolved.
        """
        self.check_cleaned()
        meld_component = self._meld
        if meld_component is None:
            raise RuntimeError("Meld component is unavailable.")
        return meld_component.has_live_creation(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    def describe_live_creation_status(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Dict[str, Any]:
        """
        Public API

        Resolve a spell through the same identity path as `meld(...)`, but
        return structured live-creation status for this conduit context.

        Purpose:
            Provide a richer diagnostic/runtime query surface over the same
            no-create probe used by `has_live_creation(...)`.

        Contract:
            - Mirrors the root identity inputs accepted by `meld(...)`.
            - Delegates all lookup and existence semantics to the owned
              `Meld` instance.
            - Never creates, registers, links, or mutates objects.
            - Reports the query as scoped to this conduit context.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            Dict[str, Any]: Structured live-creation status payload.

        Raises:
            RuntimeError:
                If the Conduit has been cleaned or the underlying `Meld`
                instance is unavailable.
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are
                provided.
            KeyError:
                Propagated from `Meld` when a spell cannot be resolved.
        """
        self.check_cleaned()
        meld_component = self._meld
        if meld_component is None:
            raise RuntimeError("Meld component is unavailable.")
        return meld_component.describe_live_creation_status(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )

    def describe_spells_in_conduit(self) -> list[dict[str, Any]]:
        """
        Public API

        Return a user-facing dump of spell targeting details visible through
        this conduit's Spellbook.

        Purpose:
            Expose the Spellbook-owned ACL-authoring dump on the conduit
            surface so advanced Rift and conduit users can inspect the visible
            spell set without reaching into the Spellbook directly.

        Contract:
            - Delegates to the owned `Spellbook`.
            - Returns detached dictionaries only.
            - Does not create, mutate, or resolve objects.

        Returns:
            list[dict[str, Any]]:
                Spell targeting details currently visible through this
                conduit's Spellbook.

        Raises:
            RuntimeError:
                If the Conduit has been cleaned or the underlying Spellbook is
                unavailable.
        """
        self.check_cleaned()
        spellbook = self._spellbook
        if spellbook is None:
            raise RuntimeError("Spellbook is unavailable.")
        return spellbook.describe_spells_in_spellbook()



    #endregion Meld
    #region Conduit Ward API
    def link(self, target_conduit: "Conduit") -> bool:
        """
        Public API

        Attempts to establish a link between this Conduit and a `target_conduit`.

        Linking is only allowed if the world is in dynamic mode. This process initiates a contract
        relationship between the two conduits based on the current policy.

        On success, the following hook will be fired on this Conduit (if configured):

            - "on_conduit_post_link(self, target_conduit)"

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            TypeError: If `target_conduit` is not an `Conduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
            RuntimeError: If the target conduit belongs to a different `AethericFrame`.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("link called when conduit is not normal", "link")
            raise RuntimeError("Only normal conduits can manage link services.")
        if self._transaction_blocked_for_current_posture(
                "link",
        ):
            self._logger.error("link denied by current frame posture", "link")
            raise RuntimeError(
                "[CONDUIT] Linking is disabled for the current frame posture."
            )
        if not self.__dynamic_environment__:
            self._logger.error("link in non-dynamic env", "link")
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")
        if not isinstance(target_conduit, Conduit):
            self._logger.error("link target not Conduit-compatible", "link")
            raise TypeError(f"Expected Conduit-compatible object, got {type(target_conduit).__name__}")
        if not target_conduit._id:
            self._logger.error("link target has no valid creation context", "link")
            raise RuntimeError("Target conduit does not have a valid creation context.")

        with self._lock:
            linked = self._conduit_ward._link(target_conduit)

        if linked:
            # Fire post-link hook with both ends of the relationship.
            if (
                (self._local_conduit_hooks and self._local_conduit_hooks.get("on_conduit_post_link"))
                or (self._conduit_hooks and self._conduit_hooks.get("on_conduit_post_link"))
            ):
                self._fire_conduit_hooks(
                    "on_conduit_post_link",
                    self,
                    target_conduit,
                )
            self._publish_conduit_record_to_nexus()
            if (
                target_conduit._nexus_publish_enabled
                and target_conduit._conduit_state is ConduitState.normal
            ):
                target_conduit._nexus._publish_conduit_record(target_conduit)

        return linked

    def sever_link(self, target_conduit: "Conduit") -> bool:
        """
        Public API

        Sever the link and the corresponding spell contracts between this Conduit and its target Conduit.

        This method validates the link's existence, ensures it can be severed according to policy,
        and removes the link and all contracted spells. This is intended for public use to dissolve a relationship.

        On success, the following hook will be fired on this Conduit (if configured):

            - "on_conduit_post_unlink(self, target_conduit)"

        Args:
            target_conduit (Conduit): The target Conduit whose link to sever.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
        """
        self.check_cleaned()
        if self._transaction_blocked_for_current_posture(
                "link",
        ):
            self._logger.error(
                "sever_link denied by current frame posture",
                "sever_link",
            )
            raise RuntimeError(
                "[CONDUIT] Linking is disabled for the current frame posture."
            )
        if not self.__dynamic_environment__:
            self._logger.error("sever_link in non-dynamic env", "sever_link")
            raise RuntimeError("Dynamic environment is not enabled. Cannot manage link services.")

        with self._lock:
            unlinked = self._conduit_ward._sever_link(target_conduit)

        if unlinked:
            # Fire post-unlink hook with both ends of the relationship.
            if self._conduit_hooks or self._local_conduit_hooks:
                self._fire_conduit_hooks(
                    "on_conduit_post_unlink",
                    self,
                    target_conduit,
                )
            self._publish_conduit_record_to_nexus()
            if (
                target_conduit._nexus_publish_enabled
                and target_conduit._conduit_state is ConduitState.normal
            ):
                target_conduit._nexus._publish_conduit_record(target_conduit)

        return unlinked

    def get_links(self) -> list["Conduit"]:
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
        with self._lock:
            return self._conduit_ward._get_links()

    def get_lesser_conduit(self, conduit_id: str) -> Optional["Conduit"]:
        """
        Internal

        Returns a specific lesser conduit (child) linked to this conduit by its ID.

        Args:
            conduit_id (str): The ID of the lesser conduit to retrieve.

        Returns:
            Optional["Conduit"]: The linked lesser conduit if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ward._get_lesser_conduit(conduit_id)


    def get_initiated_conduit(self, conduit_id: str) -> Optional["Conduit"]:
        """
        Public API

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the internal index to resolve an outbound connection,
        where this conduit was the **initiator** of the contract.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[Conduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ward._get_initiated_conduit(conduit_id)


    def get_provider_conduit(self, conduit_id: str) -> Optional["Conduit"]:
        """
        Public API

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the internal index to resolve an inbound connection,
        where another conduit linked to this one as the **provider**.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[Conduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ward._get_provider_conduit(conduit_id)


    def get_initiated_conduits(self) -> list["Conduit"]:
        """
        Public API

        Returns a list of all conduits that this conduit has initiated contracts toward (outbound links).

        This is useful for understanding the dependencies and relationships initiated by this conduit.

        Returns:
            list[Conduit]: A list of conduits this conduit linked to.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ward._get_initiated_conduits()

    def get_provider_conduits(self) -> list["Conduit"]:
        """
        Public API

        Returns a list of all conduits that have initiated contracts to this conduit (inbound links).

        These are the conduits that depend on this one for contracted spells.

        Returns:
            list[Conduit]: A list of conduits that have linked to this conduit as the provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._conduit_ward._get_provider_conduits()

    def cleanup_lesser_conduits(self) -> None:
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This prevents further operations on lesser conduits and is typically used when the parent
        is cleaning or undergoing a major state change (e.g., upgrade).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._conduit_ward.cleanup_all_lesser_conduits()

    #endregion Conduit Ward API
    #region Conduit Resolution Validation API
    def get_resolution_state(self) -> Optional[ConduitResolutionState]:
        """
        Public API

        Return the per-conduit resolution state for this conduit.

        Purpose:
            Provide access to conduit-scoped Phase 5-7 validity and diagnostics
            after linking/contracting without running validation.
        Contract:
            - Does not run validation or mutate any state.
            - For lesser conduits, uses the root conduit id.
            - Returns None when no resolution state has been recorded yet.
        Returns:
            ConduitResolutionState | None:
                The resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook is not available on this conduit.
        Threading:
            Uses the conduit lock to resolve lineage/root identity. The returned
            state is owned by SpellSystemStates and provides its own locking.
        """
        self.check_cleaned()

        with self._lock:
            conduit_id = self._id
            if self._conduit_state is ConduitState.lesser:
                if self._conduit_ward is None:
                    self._logger.error(
                        "Root conduit is not set for this lineage.",
                        "get_resolution_state",
                    )
                    raise RuntimeError("Root conduit is not set for this lineage.")
                root_conduit = self._conduit_ward.root_conduit
                if root_conduit is None:
                    raise RuntimeError("Root conduit is not set for this lineage.")
                conduit_id = root_conduit._id

            spellbook = self._spellbook
            if spellbook is None:
                self._logger.error(
                    "Spellbook is not available for this conduit.",
                    "get_resolution_state",
                )
                raise RuntimeError("Spellbook is not available for this conduit.")
            spell_system_states = spellbook._spell_system_states

        if spell_system_states is None:
            return None

        return spell_system_states.get_conduit_resolution_state(conduit_id)

    def validate_resolution(self, *, refresh_structural: bool = True) -> Optional[ConduitResolutionState]:
        """
        Public API

        Run structural and conduit-scoped resolution validation, then return the state.

        Purpose:
            Provide an explicit preflight validation hook after linking or
            contracting spells so callers (including AI users) can check
            readiness before performing work.
        Contract:
            - When refresh_structural is True, runs structural phases (1-4) first.
            - Always runs resolution phases (5-7) for this conduit scope.
            - Returns the conduit-scoped resolution state after validation.
        Args:
            refresh_structural:
                Whether to re-run structural validation (phases 1-4) before
                conduit-scoped phases. Defaults to True.
        Returns:
            ConduitResolutionState | None:
                The resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook or SpellSystemStates are unavailable.
            SpellbookValidationError:
                Propagated if structural or resolution validation fails.
        Threading:
            Resolves conduit identity under the conduit lock but executes phase
            pipelines outside of it to avoid long-held locks.
        """
        self.check_cleaned()

        with self._lock:
            conduit_id = self._id
            if self._conduit_state is ConduitState.lesser:
                if self._conduit_ward is None:
                    self._logger.error(
                        "Root conduit is not set for this lineage.",
                        "validate_resolution",
                    )
                    raise RuntimeError("Root conduit is not set for this lineage.")
                root_conduit = self._conduit_ward.root_conduit
                if root_conduit is None:
                    raise RuntimeError("Root conduit is not set for this lineage.")
                conduit_id = root_conduit._id

            spellbook = self._spellbook
            if spellbook is None:
                self._logger.error(
                    "Spellbook is not available for this conduit.",
                    "validate_resolution",
                )
                raise RuntimeError("Spellbook is not available for this conduit.")
            spell_system_states = spellbook._spell_system_states

        if spell_system_states is None:
            self._logger.error(
                "SpellSystemStates is not available for this conduit.",
                "validate_resolution",
            )
            raise RuntimeError("SpellSystemStates is not available for this conduit.")

        if refresh_structural:
            spellbook._run_structural_phases()

        spellbook._run_resolution_phases_for_conduit(conduit_id)

        return spell_system_states.get_conduit_resolution_state(conduit_id)

    #endregion Conduit Resolution Validation API
    #region Spell Contracting API
    def _qualify_contracts(self) -> None:
        """
        Internal

        Performs checks to ensure the conduit is in a state capable of managing spell contracts.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit.
            RuntimeError: If dynamic environment is not enabled.
        """

        if self._conduit_state != ConduitState.normal:
            self._logger.error("_qualify_contracts: not normal state", "_qualify_contracts")
            raise RuntimeError("Only normal conduits can create spell contracts.")
        if not self.__dynamic_environment__:
            self._logger.error("_qualify_contracts: non-dynamic env", "_qualify_contracts")
            raise RuntimeError("Dynamic environment is not enabled. Cannot interact with spell contracts.")

    def _resolve_contract_peer_ids(
            self,
            *,
            conduit: Optional["Conduit"],
            conduit_id: Optional[str],
            allow_all_links: bool,
    ) -> Tuple[str, ...]:
        """
        Internal

        Resolve peer conduit ids for contract gating.

        Purpose:
            Normalize the peer conduit targets used to validate a link
            transaction before contract mutation.
        Contract:
            - Returns a tuple of peer conduit ids to require in the active
              link transaction.
            - Raises if no peer is supplied and allow_all_links is False.
            - When allow_all_links is True, returns all currently linked peers.
        Args:
            conduit:
                Optional peer conduit instance.
            conduit_id:
                Optional peer conduit id.
            allow_all_links:
                When True, fall back to all current linked peers.
        Returns:
            Tuple[str, ...]:
                Peer conduit ids to validate in the active link transaction.
        Raises:
            RuntimeError: If no peer can be resolved and allow_all_links is False.
        Threading:
            Reads linked peers via ConduitWard which guards its state.
        """
        if conduit is not None:
            return (conduit._id,)
        if conduit_id is not None:
            return (conduit_id,)
        if not allow_all_links:
            raise RuntimeError(
                "[CONDUIT] Contract mutation requires a target conduit or conduit_id."
            )
        peers = self._conduit_ward._get_links()
        peer_ids = {peer._id for peer in peers if peer is not None}
        return tuple(peer_ids)

    def _require_link_transaction_for_contract(
            self,
            *,
            conduit: Optional["Conduit"],
            conduit_id: Optional[str],
            allow_all_links: bool,
    ) -> None:
        """
        Internal

        Require an active link change transaction for contract mutations.

        Purpose:
            Ensure contract mutations are performed only under a validated
            link transaction that names all participating conduits.
        Contract:
            - Requires an active change transaction of type LINK.
            - The active request must include this conduit id and the peer
              conduit ids in its conduit_ids list.
            - Raises with a descriptive error if the requirement is not met.
        Args:
            conduit:
                Optional peer conduit instance supplied to the contract call.
            conduit_id:
                Optional peer conduit id supplied to the contract call.
            allow_all_links:
                When True, allows peer resolution from all current links.
        Returns:
            None.
        Raises:
            RuntimeError: If no change transaction is active.
            RuntimeError: If the active transaction is not a link transaction.
            RuntimeError: If required conduit ids are missing from the transaction.
            RuntimeError: If the spellbook is unavailable.
        Threading:
            Reads the active request under the Spellbook lock.
        """
        spellbook = self._spellbook
        if spellbook is None:
            self._logger.error(
                "Spellbook unavailable for contract transaction check",
                "_require_link_transaction_for_contract",
            )
            raise RuntimeError("[CONDUIT] Spellbook is not available for contract operations.")

        mediator = spellbook._get_required_transaction_mediator()
        request = mediator.get_active_request()

        if request is None:
            self._logger.error(
                "Contract mutation requires active link transaction",
                "_require_link_transaction_for_contract",
            )
            raise RuntimeError(
                "[CONDUIT] Contract mutation requires an active link transaction. "
                "Call begin_transaction('link') on the borrower and include both "
                "borrower and peer conduits."
            )
        if request.request_type not in ("link", "cluster_link"):
            self._logger.error(
                "Contract mutation requires link transaction",
                "_require_link_transaction_for_contract",
            )
            raise RuntimeError(
                "[CONDUIT] Active change transaction is not a link transaction."
            )

        required_ids = self._resolve_contract_peer_ids(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=allow_all_links,
        )
        missing: list[str] = []
        if self._id not in request.conduit_ids:
            missing.append(self._id)
        for peer_id in required_ids:
            if peer_id not in request.conduit_ids:
                missing.append(peer_id)

        if missing:
            unique_missing = sorted(set(missing))
            self._logger.error(
                f"Link transaction missing conduit ids: {unique_missing}",
                "_require_link_transaction_for_contract",
            )
            raise RuntimeError(
                "[CONDUIT] Link transaction missing conduit ids required for contract mutation. "
                f"Missing={unique_missing}. Pass conduits including borrower and peer "
                "to begin_transaction('link')."
            )



    def add_spell_to_contract(
            self,
            *,
            spell: Optional[Spell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: DetailReason = DetailReason.manual,
            root_spell_id: Optional[str] = None,
            link_dependencies: bool = False,
    ) -> bool | None:
        """
        Public API

        Establishes a single spell contract between this conduit and another target conduit.

        This allows one conduit to borrow or grant a specific spell, identified either by object or ID,
        to/from a peer conduit. The contract defines the permissions under which the spell can be used.

        You must provide either a `spell` object or a `spell_id`. The target conduit must be specified
        either directly or resolved via its ID and aetheric frame. Contract mutations require an
        active link transaction that includes both conduits.

        Args:
            spell (Spell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell to contract.
            conduit (Conduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The str of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.
            reason (DetailReason): The reason for the contract (default is DetailReason.manual).
            link_dependencies (bool): Whether to link dependencies (default is False).
            root_spell_id (str, optional): The root spell id for this contract (default is None).

        Returns:
            bool | None: True if the contract was created, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=False,
        )

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

        if result and (
            (self._local_conduit_hooks and self._local_conduit_hooks.get("on_contract_created"))
            or (self._conduit_hooks and self._conduit_hooks.get("on_contract_created"))
        ):
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_created",
                    self,
                    peer,
                )

        return result



    def add_spells_to_contract(
            self,
            spell_ids: list[str],
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: DetailReason = DetailReason.manual,
            link_dependencies: bool = False,
    ) -> Dict[str, bool]:
        """
        Public API

        Establishes multiple spell contracts with another conduit in a single operation.

        Allows you to bulk-grant or bulk-borrow spells by specifying a list of spell IDs. Each spell
        will be contracted using the same permission level.

        Args:
            spell_ids (list[str]): List of spell IDs to contract.
            conduit (Conduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The id of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for all spells (default is "create").
            aetheric_frame (str): Optional frame override used to locate the target conduit.
            reason (DetailReason): The reason for the contract (default is DetailReason.manual).
            link_dependencies (bool): Whether to link dependencies (default is False).

        Returns:
            Dict: Dictionary of `spell_id` -> success boolean for each attempted contract.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=False,
        )

        report = self._conduit_ward._add_spells_to_contract(
            spell_ids=spell_ids,
            conduit=conduit,
            conduit_id=conduit_id,
            permissions=permissions,
            aetheric_frame=aetheric_frame,
            reason=reason,
            link_dependencies=link_dependencies,
        )

        normalized: dict[str, bool] = {}
        if isinstance(report, dict):
            success_values = report.get("success")
            failed_values = report.get("failed")
            if isinstance(success_values, list) and isinstance(failed_values, dict):
                for current_spell_id in success_values:
                    normalized[current_spell_id] = True
                for current_spell_id in failed_values.keys():
                    normalized.setdefault(current_spell_id, False)
            else:
                normalized = {spell_id: bool(value) for spell_id, value in report.items()}

        # Fire hook only if at least one contract addition succeeded.
        if normalized and any(value is True for value in normalized.values()) and (
            (self._local_conduit_hooks and self._local_conduit_hooks.get("on_contract_created"))
            or (self._conduit_hooks and self._conduit_hooks.get("on_contract_created"))
        ):
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None:
                self._fire_conduit_hooks(
                    "on_contract_created",
                    self,
                    peer,
                )

        return normalized


    def remove_spell_from_contract(
            self,
            *,
            spell: Optional[Spell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            root_spell_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API

        Removes a single spell contract between this conduit and another.

        Either the `spell` or `spell_id` can be provided to specify the contract to dissolve.
        Once removed, the spell is no longer accessible across the link.

        Args:
            spell (Spell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (Conduit, optional): The target conduit involved in the contract.
            conduit_id (str, optional): id of the target conduit (used if `conduit` not provided).
            aetheric_frame (str): Optional frame override to resolve the target conduit.

        Returns:
            bool | None: True if the spell was successfully removed from the contract, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=False,
        )

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
            if peer is not None and (self._conduit_hooks or self._local_conduit_hooks):
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return result

    def remove_spells_from_contract(
            self,
            *,
            spell_ids: Optional[list[str]] = None,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            root_spell_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> Dict[str, bool]:
        """
        Public API

        Removes multiple spells from an existing contract with a target conduit.

        Useful for bulk cleanup or revocation when retiring behaviors or permissions.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (Conduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.
            root_spell_id (str, optional): str of root spell ID (used if `conduit` is not provided).

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each removal attempt.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=False,
        )

        report = self._conduit_ward._remove_spells_from_contract(
            spell_ids=spell_ids,
            conduit=conduit,
            conduit_id=conduit_id,
            root_spell_id=root_spell_id,
            aetheric_frame=aetheric_frame,
        )

        normalized: dict[str, bool] = {}
        if isinstance(report, dict):
            success_values = report.get("success")
            failed_values = report.get("failed")
            if isinstance(success_values, list) and isinstance(failed_values, dict):
                for current_spell_id in success_values:
                    normalized[current_spell_id] = True
                for current_spell_id in failed_values.keys():
                    normalized.setdefault(current_spell_id, False)
            else:
                normalized = {spell_id: bool(value) for spell_id, value in report.items()}

        if normalized and any(value is True for value in normalized.values()):
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None and (self._conduit_hooks or self._local_conduit_hooks):
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return normalized

    def remove_root_from_contracts(self, *, root_spell_id: str, conduit: Optional["Conduit"] = None,
                                   conduit_id: Optional[str] = None, aetheric_frame: str = "default") -> dict:
        """
        Public API

        Removes a root spell_id (and any dependency Details attributed to it) from one
        contract or all contracts. Orphaned Details trigger contracted spell removal;
        empty contracts are severed.

        Contract mutations require an active link transaction that includes the
        borrower and the peer conduits involved in the contract cleanup.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=True,
        )
        return self._conduit_ward._remove_root_from_contracts(
            root_spell_id=root_spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            aetheric_frame=aetheric_frame,
        )

    def add_spell_to_contract_with_dependencies(
            self,
            *,
            spell: Optional[Spell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
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


    def _remove_all_spells_from_contract(
            self,
            *,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API

        Dissolves **all** spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the spell relationship between the two conduits.

        Args:
            conduit (Conduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            bool | None: True if all spells were successfully removed, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=False,
        )

        result = self._conduit_ward._remove_all_spells_from_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            aetheric_frame=aetheric_frame,
        )

        if result:
            peer = self._resolve_peer_conduit_for_contract_hooks(conduit, conduit_id, aetheric_frame)
            if peer is not None and (self._conduit_hooks or self._local_conduit_hooks):
                self._fire_conduit_hooks(
                    "on_contract_removed",
                    self,
                    peer,
                )

        return result

    def get_all_spells_in_contracts(self, validate: bool = True) -> Optional[dict[str, list[Tuple[str, Spell]]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts (i.e., borrowed spells).

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        Args:
            validate (bool): If True, performs contract consistency validation before returning data.

        Returns:
            Optional[dict[str, list[Tuple[str, Spell]]]]: Dictionary mapping peer conduit ids to lists of (spell_id, Spell) tuples,
            or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `validate` is not a boolean.
        """
        self._qualify_contracts()
        if not isinstance(validate, bool):
            self._logger.error("validate must be bool", "get_all_spells_in_contracts")
            raise TypeError(f"Expected validate to be a boolean, got {type(validate).__name__}")
        return self._conduit_ward._get_all_spells_in_contracts(validate=validate)

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, Spell]]:
        """
        Public API

        Searches all known contracts to find the origin of a specific contracted spell.

        Looks for a specific spell by ID and returns the str of the conduit it's contracted from
        along with the spell object, if found.

        Args:
            spell_id (str): The unique ID of the spell.

        Returns:
            Optional[tuple[str, Spell]]: Tuple of (`conduit_id`, `spell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `spell_id` is not a string.
        """
        self._qualify_contracts()
        if not isinstance(spell_id, str):
            self._logger.error("spell_id must be str", "get_spell_in_contracts")
            raise TypeError(f"Expected spell_id to be a string, got {type(spell_id).__name__}")
        return self._conduit_ward._get_spell_in_contracts(spell_id)

    def get_spells_in_contract_by_conduit(self, conduit_id: str) -> dict[str, list[tuple[str, Spell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a specific peer conduit, identified by id.

        Returns a detailed list of all spells that this conduit currently accesses or has granted
        through its relationship with the specified peer.

        Args:
            conduit_id (str): id of the target peer conduit.

        Returns:
            dict[str, list[tuple[str, Spell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `Spell`) tuples or None
            if not found. If a contract exists but has no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_id` is not a str.
        """
        self._qualify_contracts()
        if not isinstance(conduit_id, str):
            self._logger.error("conduit_id must be id", "get_spells_in_contract_by_conduit")
            raise TypeError(f"Expected conduit_id to be a id, got {type(conduit_id).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit(conduit_id)

    def get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, Spell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Performs resolution using a human-readable name instead of str.

        Args:
            conduit_name (str): Name of the peer conduit.

        Returns:
            dict[str, list[tuple[str, Spell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `Spell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_name` is not a string.
        """
        self._qualify_contracts()
        if not isinstance(conduit_name, str):
            self._logger.error("conduit_name must be str", "get_spells_in_contract_by_conduit_name")
            raise TypeError(f"Expected conduit_name to be a string, got {type(conduit_name).__name__}")
        return self._conduit_ward._get_spells_in_contract_by_conduit_name(conduit_name)


    def get_contracted_conduits(self) -> list[Tuple[str, "Conduit"]] | None:
        """
        Public API

        Lists all conduits that have an active spell contract with this conduit.

        Each returned conduit represents a peer in the current dynamic spell network.

        Returns:
            list[Tuple[str, Conduit]] | None: List of (`conduit_id`, `Conduit`) tuples, or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
        self._qualify_contracts()
        return self._conduit_ward._get_contracted_conduits()

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of Conduit state.

        Purpose:
            Provide a stable view of conduit metadata and Spellbook registries
            for diagnostics while transactions may be in-flight.
        Contract:
            - Returns detached copies of metadata and Spellbook snapshot data.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]:
                Snapshot payload with conduit metadata and Spellbook snapshot.
        Raises:
            RuntimeError: If the Conduit has been cleaned.
        Threading:
            Acquires the Conduit lock while copying local metadata, then
            snapshots the Spellbook outside the lock.
        """
        self.check_cleaned()
        snapshot_id = IDBuilder.create_id()
        captured_at_ms = int(time.time() * 1000.0)

        with self._lock:
            conduit_id = self._id
            conduit_name = self._name
            conduit_state = str(self._conduit_state)
            dynamic_environment = self.__dynamic_environment__
            aetheric_frame = self._aetheric_frame_name
            spellbook = self._spellbook

        spellbook_snapshot = None
        if spellbook is not None:
            spellbook_snapshot = spellbook.snapshot_state()

        return {
            "snapshot_id": snapshot_id,
            "captured_at_ms": captured_at_ms,
            "conduit_id": conduit_id,
            "conduit_name": conduit_name,
            "conduit_state": conduit_state,
            "dynamic_environment": dynamic_environment,
            "aetheric_frame": aetheric_frame,
            "spellbook_snapshot": spellbook_snapshot,
        }

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Public API

        Produces a detailed diagnostic summary of a contract established with a specific conduit.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduitÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¾ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢s name, the number of active spells involved, and permission levels.
        Primarily used for debugging, introspection, and UI inspection tools.

        Args:
            conduit_id (str): str of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including a list of spells and their permissions.

        Raises:
            RuntimeError: If the Conduit fails contract qualification checks (cleaned, not normal, not dynamic).
        """
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
        self._qualify_contracts()
        return self._conduit_ward._validate_received_contracts()


    #endregion Spell Contracting API


    #region Hooks
    def _resolve_peer_conduit_for_contract_hooks(
            self,
            conduit: "Conduit" | None,
            conduit_id: str | None,
            aetheric_frame: str,
    ) -> Optional["Conduit"]:
        """
        Internal

        Resolve the peer conduit instance for contract-related hooks.

        This helper normalizes the two input forms:

            - Direct `conduit` instance, or
            - `conduit_id` + `aetheric_frame`

        so that hooks can always receive a concrete Conduit object when
        possible.

        Args:
            conduit (Conduit | None):
                Optional direct conduit instance supplied by the caller.
            conduit_id (str | None):
                Optional conduit id, used when `conduit` is not provided.
            aetheric_frame (str):
                Frame hint; "default" means this Conduit's own frame.

        Returns:
            Optional[Conduit]:
                The resolved peer conduit, or None if it cannot be resolved.
        """
        if conduit is not None:
            return conduit

        if conduit_id is None:
            return None

        frame = self._aetheric_frame_name if aetheric_frame == "default" else aetheric_frame
        if frame != self._aetheric_frame_name:
            return None
        try:
            return self._aetheric_frame._conduit_cloud.get_conduit_by_id(
                conduit_id
            )
        except Exception:
            # Hooks are advisory; failure to resolve a peer must not
            # break the primary contract APIs.
            return None


    def _fire_conduit_hooks(self, hook_name: str, *conduits: "Conduit") -> None:
        """
        Internal

        Invoke all local Conduit hooks registered under hook_name, if any.

        This uses the hook map localized into this Conduit via
        :meth:`_initialize_conduit_hooks`. The contract is intentionally
        narrow and stable:

            - Shared lineage hooks run before local conduit hooks.
            - All hooks are plain callables.
            - They are invoked as: hook(*conduits)
            - Each element in conduits MUST be a Conduit instance.
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
        hook_chain = self._collect_conduit_hook_chain(hook_name)
        if not hook_chain:
            return

        for hook in hook_chain:
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
