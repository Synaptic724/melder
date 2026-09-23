import threading
import time
from collections.abc import Sequence
from contextlib import contextmanager
from types import ModuleType, TracebackType
from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    Any,
    Tuple,
    Callable,
    Iterable,
    Dict,
    Generator,
    ClassVar,
    Set,
)
# Melder Imports
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.meld.conduit_meld import ConduitMeld
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
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
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
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
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import ConduitResolutionState
    from melder.utilities.logger.safe_logger import SafeLogger
    from melder.utilities.synchronization.creation_gate import CreationGate
    from melder.utilities.synchronization.creation_gate_controller import CreationGateController
    from melder.crystallizer.crystallizer import Crystallizer
    from melder.mutation_research.mutation_research import MutationResearch


# NOTE: the former `_SpellSpaceContextManager` wrapper was removed:
# `SpellSpace` is now its own context manager, so the managed
# `with conduit.enter_spellspace() as space:` lane allocates zero per-cycle
# wrapper objects. Activation (pool acquire + thread-stack push) happens in
# `Conduit.enter_spellspace()`; LIFO-validated exit and pooled recycling live
# on `SpellSpace.__exit__`.

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
      Spellbook and retire only their own named discovery entry, never root ownership.
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

    Registration:
        MELDER KERNEL - guarded. A conduit is obtained from
        `Spellbook.conjure(...)` or `Conduit.create_lesser_conduit(...)`, never
        constructed directly and never bound as a spell. Guarding does not
        restrict USE: the conduit is the primary object a user holds and calls
        `meld(...)` on.

    Subsystem Context:
        The owner of the whole conduit subsystem. It composes one `ConduitMeld`
        (resolution), one `ConduitCreations` (live-object storage), one
        `ConduitWard` (contracts, policies, lineage), one `CreationGate`
        (admission), one `SpellSpacePool`, and one `ConduitPool`. Everything
        else in this package is reached THROUGH a conduit - which is why the
        vocabulary classes (`Policies`, `Permissions`, `ConduitState`) are the
        values a user hands to conduit verbs.

    System Context:
        A conduit is the boundary at which Melder's promises become concrete.
        Layer 4 of the runtime (Aether -> AethericFrame -> Spellbook -> CONDUIT
        -> Meld -> Creations): a `Spellbook` conjures exactly ONE conduit, and
        from that point the conduit is what the user actually holds.
        Two invariants explain most of its surface. First, DYNAMIC MODE GATES
        STRUCTURE: linking, severing, ownership transfer, and lesser-to-normal
        upgrade all require dynamic mode, because each rewires the resolution
        graph after conjure and an automatic-mode world promises a fixed,
        self-contained graph. Second, DRAIN BEFORE MUTATE: the `CreationGate`
        exists so in-flight melds can finish before shutdown or reconfiguration
        rather than being torn out mid-resolution - which is why the gate tracks
        tickets rather than just holding a boolean.
        The normal/lesser split is a lifetime story, not a capability one. A
        lesser conduit shares its parent's Spellbook and does not unregister
        frame-level state, so tearing one down cannot damage the root; upgrading
        one to normal PRESERVES its already-constructed objects rather than
        rebuilding them, because callers may already hold those instances.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. The runtime scope you hold after conjure. Call meld(...) to resolve
        instances, create_lesser_conduit(...) for child scopes, enter_spellspace() for request
        scope, and link(...)/sever_link(...)/transfer_spell_ownership(...) in dynamic mode only.
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
       "_cluster_creations",
       "_creation_gate_controller",
       "_creation_gate",
       "_conduit_hooks",
       "_meld_hooks",
       "_local_conduit_hooks",
       "_meld",
       "_conduit_ward",
        "_permanent_cleanup_requested",
        "_crystallizer",
        "_mutation_research",
    ]
    _DEFAULT_ROOT_CONDUIT_NAME: ClassVar[str] = "default"
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

        Contract:
            - Generates a conduit id when none is supplied; a supplied non-string id is
              rejected with `TypeError` rather than coerced.
            - Creates the reentrant lock that guards every later conduit operation.
            - A conduit is born in a specific `ConduitState`, and that state - not the
              frame posture - is what decides whether `scan`, `link` and cluster
              operations are even reachable: several refuse anything but `normal`.

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
                Selected lifecycle hooks. Normal roots copy the containers;
                lessers borrow the root map when no explicit map is supplied.
            meld_hooks (Optional[dict[str, list[Callable[..., Any]]]], optional):
                Selected Meld hooks, with the same root-copy/lesser-borrow rule.

        Raises:
            TypeError:
                If configuration is not an SpellbookConfiguration, conduit_id is not a string,
                or root_conduit_id is not a string.
            ValueError:
                If conduit_id is provided but empty, or root_conduit_id is invalid
                for the requested conduit_state.

        Returns:
            None.
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
        self._crystallizer: Crystallizer = spellbook._crystallizer
        # Borrowed world-root reference (owner ruling 2026-07-12): inherited
        # from the owning spellbook exactly like `_crystallizer` above, so
        # lesser conduits and the upgrade path share the same root for free.
        self._mutation_research: MutationResearch = spellbook._mutation_research
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
        self._transaction_identity: Optional[DevopsIdentity] = None
        if conduit_state is ConduitState.normal:
            self._ensure_transaction_identity_registered()
        self._spellspace_stack: SpellSpaceThreadState = SpellSpaceThreadState()
        self._spellspace_registry: set[SpellSpace] = set()
        self._creations: ConduitCreations = ConduitCreations(
            conduit_id=self._id,
        )
        if creation_gate is None:
            creation_gate = self._create_gate_for_current_root(conduit_id)
        else:
            self._register_existing_gate_for_current_root(conduit_id, creation_gate)
        self._creation_gate: CreationGate = creation_gate

        self._initialize_hook_baselines(conduit_hooks=conduit_hooks, meld_hooks=meld_hooks)

        self._meld: ConduitMeld = ConduitMeld(
            conduit_creations=self._creations,
            spellbook=self._spellbook,
            conduit_id=self._id,
            resolution_conduit_id=self._root_conduit_id,
            dynamic_environment=self.__dynamic_environment__,
            meld_hooks=self._meld_hooks,
        )
        self._spellspace_pool: SpellSpacePool = SpellSpacePool(
            owner_conduit_id=self._id,
            conduit_meld=self._meld,
            owner_conduit_creations=self._creations,
            spellspace_registry=self._spellspace_registry,
            spellspace_stack_state=self._spellspace_stack,
            baseline_idle=20,
            max_idle=20,
        )
        if conduit_state is ConduitState.normal:
            self._conduit_pool: ConduitPool = ConduitPool(
                root_conduit=self,
                baseline_idle=20,
                max_idle=20,
            )
            # Lineage-root store: a normal conduit is its own lineage root, so
            # its meld defaults `_root_creations` to its own creations at
            # construction; the door is handed that store for
            # `unique_per_conduit_lineage` melds.
            # Cluster team-store facade: a normal conduit is its own cluster
            # root, so it owns a fresh empty (inert) facade; it fills on
            # election, and a `unique_per_conduit_cluster` meld hard-errors until
            # then.
            self._cluster_creations = ClusterCreations()
        else:
            root_conduits = self._aetheric_frame._conduits
            root_conduit = root_conduits.get(self._root_conduit_id)
            if root_conduit is None:
                raise RuntimeError(
                    "Root conduit is unavailable for conduit pool wiring."
                )
            self._conduit_pool = root_conduit._conduit_pool
            # Lineage-root store: a lesser resolves `unique_per_conduit_lineage`
            # into the lineage root's creations (the single store shared across
            # the whole lineage), so point its meld at the root conduit's
            # lineage-root store.
            self._meld._root_creations = root_conduit._meld._root_creations
            # Cluster team-store facade: the conduit owns this resource (like
            # `_creations`); a lesser borrows its lineage root's facade so an
            # election on this lineage is visible here too.
            self._cluster_creations = root_conduit._cluster_creations
        # Hand the meld a reference to this conduit's cluster facade for
        # `unique_per_conduit_cluster` store-selection (the conduit owns it).
        self._meld._cluster_creations = self._cluster_creations
        self._configure_conduit_state()
        self._conduit_ward: ConduitWard = ConduitWard(
            conduit=self,
            dynamic=self.__dynamic_environment__,
            conduit_type=self._conduit_state,
            policy=policy,
            aetheric_frame=self._aetheric_frame,
        )
        self._refresh_devops_identity_state()
        # Config-less roots emit at initialization. Named lesser acquisition
        # emits later, after its name and actual parent link have been established;
        # unpublished/unnamed shells do not record a structural scope here.
        if conduit_state is ConduitState.normal:
            self._emit_conduit_twin()

    def _emit_conduit_twin(self) -> None:
        """
        Internal

        Emit a normal root or active named lesser's structural twin.

        Purpose:
            Roots emit at conjure and structural changes. Named lessers emit
            after parent attachment, including pooled acquisition. Their required
            ancestor descriptions are detached values inside this twin, so ordinary
            unnamed scopes need neither their own record nor a cleanup probe.

        Contract:
            - NO-OP unless a normal root or named lesser in the active dynamic
              recorded lane. No created objects, callback code or runtime resources
              enter the payload. Caller serializes the named lifecycle with its lock.
            - `link_targets` records OUTBOUND (initiated) links only:
              the ward's `_initiated_index` keys. Inbound edges are
              derivable from the initiators' twins, and restore
              re-establishes each link from its initiating side.

        Returns:
            None.
        """
        if self._conduit_state is not ConduitState.normal and (
                self._conduit_state is not ConduitState.lesser or self._name is None
        ):
            return
        if not self.__dynamic_environment__ or not self._crystallizer.activated:
            return
        configuration_payload: Dict[str, object] = {
            "conduit_state": self._conduit_state.name,
            "root_conduit_id": self._root_conduit_id,
            "spellspace_pool_present": self._spellspace_pool is not None,
            "conduit_pool_present": self._conduit_pool is not None,
        }
        if self._conduit_state is ConduitState.lesser:
            parent = self._conduit_ward._parent_conduit
            if parent is None:
                raise RuntimeError("A named lesser must be attached before recording its structure.")
            configuration_payload["parent_conduit_id"] = parent._id
            configuration_payload["lineage_ancestors"] = self._recorded_lineage_ancestors()
        self._crystallizer.emit(
            ConduitCrystal(
                conduit_id=self._id,
                spellbook_id=self._spellbook._id,
                conduit_name=self._name,
                policy_name=self._conduit_ward._policy.name,
                dynamic=self.__dynamic_environment__,
                link_targets=list(self._conduit_ward._initiated_index.keys()),
                configuration_payload=configuration_payload,
            )
        )

    def _recorded_lineage_ancestors(self) -> list[Dict[str, object]]:
        """Capture root-to-parent value rows for this attached named lesser.

        Contract:
            Called only while emitting a named structural record. Named ancestors
            remain references to their own twins; unnamed ancestors are the support
            values needed to rebuild the original hierarchy. No live object escapes.
            The caller holds its lifecycle/attachment window; callers must quiesce
            concurrent lineage mutation during promotion and live restore.
        Returns:
            list[Dict[str, object]]: Ancestor id/name/parent/policy, root first.
        """
        lineage: list[Dict[str, object]] = []
        ancestor = self._conduit_ward._parent_conduit
        while ancestor is not None:
            parent = ancestor._conduit_ward._parent_conduit
            lineage.append({
                "conduit_id": ancestor._id,
                "conduit_name": ancestor._name,
                "parent_conduit_id": None if parent is None else parent._id,
                "policy_name": ancestor._conduit_ward._policy.name,
            })
            ancestor = parent
        lineage.reverse()
        return lineage

    def _emit_conduit_retirement(self) -> None:
        """Retire this identity's structural record without touching its Book.

        Contract:
            Internal teardown may call after _cleaned is set. Dynamic/recorder
            gates are checked before reaching the facade. Lesser callers enter only
            inside the existing named branch, preserving unnamed pool-return cost.
            Identity-based removal also covers a failed normal promotion whose last
            emitted twin still referred to its former Book.
        Returns:
            None.
        """
        if self.__dynamic_environment__ and self._crystallizer.activated:
            self._crystallizer.emit_conduit_removed(self._id)

    def _emit_contract_record_for(self, peer_conduit: "Conduit") -> None:
        """
        Internal

        Re-emit the relationship snapshot for this conduit's contract with
        one peer, if such a contract exists.

        Purpose:
            Contract mutations commit through the ward but are admitted by
            this conduit's public contract verbs; each verb's success tail
            calls here so the record's ContractCrystal always reflects the
            post-transaction truth. Tolerates an absent contract (the
            mutation may have severed it - eviction is emitted by the
            ward's _remove_contract seam in that case).

        Args:
            peer_conduit:
                The other end of the contract relationship.

        Returns:
            None.
        """
        ward = self._conduit_ward
        contract_id = (
            ward._initiated_index.get(peer_conduit._id)
            or ward._received_index.get(peer_conduit._id)
        )
        if contract_id is None:
            return
        contract = ward._contracts.get(contract_id)
        if contract is None:
            return
        ward._emit_contract_record(contract)

    def _ensure_transaction_identity_registered(self) -> None:
        """
        Internal

        Ensure this conduit owns one attached transaction identity when normal.

        Contract:
            - No-op for lesser conduits.
            - Creates the conduit identity lazily on first normal-only need.
            - Attaches that identity to the frame dev-ops registry when not
              already attached.
        """
        if self._conduit_state is not ConduitState.normal:
            return
        if self._transaction_identity is None:
            self._transaction_identity = DevopsIdentity(
                owner_kind="conduit",
                owner_id=self._id,
                aetheric_frame_name=self._aetheric_frame_name,
                metadata={},
                available_transactions=tuple(),
            )
        if self._transaction_identity._registry is None:
            self._transaction_identity.attach_registry(
                self._aetheric_frame.devops_information_registry,
                object_ref=self,
            )



    #region Cleanup and Disposal
    def cleanup(self) -> None:
        """
        Public API

        Release this scope, recycling a lesser or permanently tearing down a root.

        Contract:
            - Permanent cleanup is idempotent after `_cleaned` flips. A successful
              soft lesser return ends its current use; callers must reacquire it
              through create_lesser_conduit before starting another use.
            - Permanent teardown fires `on_conduit_cleanup_start` and
              `on_conduit_cleanup_complete`. Soft return preserves the shell.
            - Dispatches to the lesser- or normal-conduit cleanup path based on the
              current conduit state.
            - Tears down logger state last, after the rest of the runtime surface has
              been released.
            - This is local conduit teardown only; it does not clean Aether or the
              owning frame itself.
            - Soft cleanup does not publish idle until descendants and named record/
              directory retirement finish. Failed cleanup remains owned for retry;
              already completed disposal work is not rolled back.

        Returns:
            None.

        Raises:
            ExceptionGroup: Creation disposal or descendant soft cleanup failed.
            Exception: Named record/directory retirement failed before pool return.

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

    def _prepare_for_pool(self) -> None:
        """
        Reset one lesser conduit into the pooled idle state.

        Contract:
            - Normal conduits do not enter the lesser pool and still hard-clean.
            - Lesser conduits transition to `pooled_lesser` locally before they
              are returned to the root-owned pool.
            - Anonymous pool return stays local and does not refresh dev-ops or
              Nexus. Named return first retires its published scope metadata.
            - Dispose Spaces and creations before clearing local lifecycle hooks
              and restoring temporary Meld hooks. The ordinary path checks one
              bool; only a modified Meld acquires its existing mutation lock.
            - Named scopes unregister and clear their label before idle publication.
              Unnamed return performs only the direct name check: no directory
              call, lock, allocation or scan is introduced on that branch.
            - Failed descendant cleanup or named record retirement keeps this
              scope attached and out of the pool so its owner can retry cleanup.

        Returns:
            None. The caller holds the conduit lock through idle publication.
        """
        if self._conduit_state is ConduitState.normal:
            self._permanent_cleanup()
            return
        self._cleanup_spellspaces_for_pool()
        self._creations.reset_for_pool()
        if self._name is not None:
            self._prepare_named_for_pool()
        else:
            self._conduit_ward._detach_for_pool()
        self._conduit_state = ConduitState.pooled_lesser
        self._conduit_ward._conduit_type = ConduitState.pooled_lesser
        if self._local_conduit_hooks is not None:
            self._local_conduit_hooks.clear()
        if self._meld._meld_hooks_modified:
            self._meld._reset_pooled_meld_hooks()
        self._conduit_pool.return_lesser_conduit(self)

    def _prepare_named_for_pool(self) -> None:
        """Retire a named scope only after descendants finish, retaining ownership on failure.

        Contract:
            The caller holds this Conduit's lock and has disposed its own stores.
            Children retire first so no checkpoint loses a named parent while its
            recorded descendants remain. Existing Nexus records become unnamed
            pooled values before the shell can be reused; this does not refresh
            compiled Rift membership. Keep the live name and parent until fallible
            publication finishes so a failure retains the cleanup route for retry.
            Own detachment is the final step; completed record/Cloud retirement
            is not rolled back if later publication fails.
            This helper is never entered for an unnamed pool return.
        Returns:
            None.
        Raises:
            ExceptionGroup: One or more descendants could not finish cleanup.
            Exception: Record, directory or Nexus publication failed before detachment.
        """
        self._conduit_ward._cleanup_children_for_pool()
        self._emit_conduit_retirement()
        self._publish_conduit_record_to_nexus(pooled=True)
        self._aetheric_frame._conduit_cloud._unregister_named_conduit(self)
        self._publish_frame_record_to_nexus()
        self._name = None
        self._conduit_ward._detach_for_pool()

    def _cleanup_spellspaces_for_pool(self) -> None:
        """
        Internal

        Soft-clean active and registered spellspaces without destroying the pool.

        Contract:
            - `_spellspace_stack` is always a `SpellSpaceThreadState`: it is
              assigned exactly once in `__init__` and only deleted during
              permanent teardown, so this path drains it directly without a
              defensive type probe.
        """
        # Hot path: runs once per pooled lesser cleanup (one per scope cycle).
        # The stack holder type is an owned lifecycle invariant; drain directly.
        active_spellspaces = self._spellspace_stack.drain()
        for spellspace in active_spellspaces:
            try:
                spellspace.cleanup()
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace for pool",
                    "_cleanup_spellspaces_for_pool",
                    exc_info=True,
                )

        while self._spellspace_registry:
            try:
                self._spellspace_registry.pop().cleanup()
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace for pool",
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

        Returns:
            None.
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

        Permanently retire a lesser and its owned runtime collaborators.

        Contract:
            Remove named discovery before deleting frame/ward references. Unnamed
            shells skip directory work. The shared Book and root maps remain owned
            by the lineage root; local children and stores follow existing teardown.
        Returns:
            None.
        """
        if self._name is not None:
            try:
                self._emit_conduit_retirement()
            except Exception:
                # Hard teardown must still remove discovery and release resources
                # if recording/cadence fails. Soft pool return remains retryable.
                self._logger.error("Error retiring lesser record", "_cleanup_lesser_conduit", exc_info=True)
            self._aetheric_frame._conduit_cloud._unregister_named_conduit(self)
            self._name = None
            try:
                self._publish_frame_record_to_nexus()
            except Exception:
                # Hard teardown must release owned resources even when an
                # observational frame-summary sink is unavailable.
                self._logger.error("Error publishing retired scope summary", "_cleanup_lesser_conduit", exc_info=True)
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
        # Cluster facade is borrowed from the root; drop the reference only --
        # never clean it (the root owns and cleans the facade).
        del self._cluster_creations
        del self._aetheric_frame
        if self._transaction_identity is not None:
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
        # Cluster facade: a normal conduit is its own cluster root and owns the
        # facade, so clean it here (lessers borrow it and never clean it).
        try:
            if self._cluster_creations is not None:
                self._cluster_creations.cleanup()
        except Exception:
            self._logger.error(
                "Error cleaning cluster facade", "_cleanup_normal_conduit", exc_info=True
            )
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

        # 4) Unregister from Aether (spells + root conduit + cloud).
        # Frame truth FIRST and independently (frame-truth hardening,
        # 2026-07-19): the frame's root-conduit registry must never retain
        # a cleaned husk because a sibling verb failed - e.g. a spellbook
        # already cleaned by an out-of-order teardown makes the spell
        # unregistration raise, and one shared try/except used to skip the
        # frame removal entirely. Each verb now fails alone and is logged
        # alone. Ordering is safe: spell unregistration works the frame's
        # SPELL registry keyed by conduit id and never reads the
        # root-conduit registry this removal pops.
        try:
            self._remove_root_conduit()
        except Exception as e:
            self._logger.error(f"Error removing root conduit from frame: {e}", "_cleanup_normal_conduit", exc_info=True)
        try:
            if self._spellbook is not None:
                self._spellbook._unregister_conduit_spells_from_aether(self._id)
        except Exception as e:
            self._logger.error(f"Error unregistering conduit spells: {e}", "_cleanup_normal_conduit", exc_info=True)
        try:
            self._publish_frame_record_to_nexus()
        except Exception as e:
            self._logger.error(f"Error publishing frame record to Nexus: {e}", "_cleanup_normal_conduit", exc_info=True)

        # 4.5) Drop per-conduit resolution state (normal conduits only)
        try:
            if self._spellbook is not None and self._spellbook._spell_system_states is not None:
                self._spellbook._spell_system_states.drop_conduit_resolution_state(self._id)
        except Exception:
            self._logger.error("Error dropping conduit resolution state", "_cleanup_normal_conduit", exc_info=True)

        # 5) Spellbook (owned by normal conduits)
        # Retire by scope identity before Book eviction too: failed promotion can
        # leave its last twin under the former Book even after runtime attachment.
        try:
            self._emit_conduit_retirement()
        except Exception:
            # Permanent teardown stays best-effort like adjacent owner cleanup;
            # a recorder/cadence failure must not strand the owned Book/resources.
            self._logger.error("Error retiring conduit record", "_cleanup_normal_conduit", exc_info=True)
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
        # Cluster facade was cleaned above (it is root-owned); drop the slot here.
        del self._cluster_creations
        del self._spellbook
        del self._configuration
        if self._transaction_identity is not None:
            self._transaction_identity.cleanup()
        del self._transaction_identity
        del self._spellspace_stack
        del self._spellspace_registry
        del self._conduit_pool
        del self._aetheric_frame_name
        del self._root_conduit_id
        del self._crystallizer
        del self._mutation_research
        del self._nexus

    def _publish_conduit_record_to_nexus(self, *, pooled: bool = False) -> None:
        """
        Internal

        Publish this conduit's current canonical record into Nexus when the
        conduit is eligible for passive ingest.

        Contract:
            - Publishes normal, lesser and retained pooled scope records.
            - Publication is skipped when Nexus publication is disabled for this
              conduit.
            - Uses the conduit-owned Nexus reference directly.
            - Named soft return may publish cleared pooled values before runtime
              detachment. It retains an existing record only; failed acquisition
              does not create a new record through this retirement path.

        Args:
            pooled: Publish an unnamed, detached pooled payload for this identity.
                The caller holds the scope's cleanup lock until actual pool return.

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

        self._nexus._publish_conduit_record(self, pooled=pooled)

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
            stack_holder = self._spellspace_stack
            if isinstance(stack_holder, SpellSpaceThreadState):
                stack = list(stack_holder.drain())
            else:
                stack = list(stack_holder.get())
                stack_holder.set([])
        except Exception:
            self._logger.error(
                "Error flushing spellspace stack",
                "_cleanup_spellspaces",
                exc_info=True,
            )
            return
        registry = list(self._spellspace_registry) if self._spellspace_registry is not None else []
        spellspaces = list(dict.fromkeys([*stack, *registry]))
        if self._spellspace_registry is not None:
            self._spellspace_registry.clear()
        for spellspace in spellspaces:
            try:
                spellspace.permanent_cleanup()
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace",
                    "_cleanup_spellspaces",
                    exc_info=True,
                )
        if self._spellspace_pool is not None:
            try:
                self._spellspace_pool.cleanup()
            except Exception:
                self._logger.error(
                    "Error cleaning spellspace pool",
                    "_cleanup_spellspaces",
                    exc_info=True,
                )


    #endregion Cleanup and Disposal


    # ------------------------------------------------------------------ #
    # SpellSpace support
    # ------------------------------------------------------------------ #

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """
        Return the currently active SpellSpace for this Conduit, if any.

        Contract:
            - THREAD-LOCAL: it returns the spellspace active on THE CALLING THREAD, not
              a conduit-wide value. Two threads inside the same conduit can see
              different answers, and one can see None while the other does not.
            - None means no spellspace is entered on this thread - a normal state,
              not an error.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

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
        return self._spellspace_pool.acquire(track_registry=True)

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

    def enter_spellspace(self) -> SpellSpace:
        """
        Acquire and activate one managed spellspace scope.

        Usage:
            with conduit.enter_spellspace() as space:
                space.meld(...)

        Contract:
            - Acquires one pooled spellspace and pushes it onto the calling
              thread's active-scope stack immediately (activation happens
              here, not in `__enter__`), then returns the space itself, which
              acts as its own context manager. No per-cycle wrapper object is
              allocated.
            - Nested activation is first-class: calling this inside an active
              scope pushes a new independent scope (A -> B -> C -> D to any
              depth); exits must unwind in LIFO order and are validated.
            - The space is cleaned (recycled to the conduit-local pool) on
              `with`-block exit, even on exceptions.
            - Callers that do not use a `with` block own the exit: they must
              call `space.__exit__(None, None, None)` (or unwind through
              conduit cleanup, which drains abandoned scopes best-effort).

        Returns:
            SpellSpace: The newly activated spellspace, already the current
            top-of-stack scope for the calling thread.

        Raises:
            SpellSpaceScopeError:
                On scope exit, if stack integrity is violated.
        """
        space = self._spellspace_pool.acquire_untracked()
        self._spellspace_stack.push(space)
        return space

    def prewarm_spellspaces(self, count: int) -> int:
        """
        Public API

        Ensure pooled spellspace shells exist before traffic arrives.

        Purpose:
            Move first-use spellspace construction cost (the shell, its
            spellspace-local creations registry, and its meld front door) from
            the first scope cycles to an explicit, owner-chosen moment.

        Contract:
            - Acquires and immediately releases pooled spellspaces so the
              idle pool holds at least `min(count, pool.max_idle)` shells.
            - Clamped to pool capacity: never builds shells the pool would
              immediately evict and destroy.
            - Prewarmed shells carry no scope contents and are not pushed on
              any thread's active-scope stack.
            - Idempotent in effect: already-idle shells count toward the
              target and are reused, not rebuilt.
            - Restore temporary owner hooks before publishing idle shells, just
              as normal Space return does. Acquisition reapplies current local
              owner hooks when the shell is actually leased.

        Args:
            count:
                Requested number of idle pooled spellspace shells. Must be
                positive.

        Returns:
            int: Number of idle shells ensured (the capacity-clamped target).

        Raises:
            ValueError: If `count` is not positive.
            RuntimeError: If the conduit has been cleaned.
        """
        self.check_cleaned()
        if count <= 0:
            raise ValueError(
                "prewarm_spellspaces requires a positive count; got "
                f"{count}. Provide how many idle shells should exist."
            )
        pool = self._spellspace_pool
        target = min(count, pool.max_idle)
        held = [pool.acquire_untracked() for _ in range(target)]
        for space in held:
            if space._meld._meld_hooks_modified:
                space._meld._reset_pooled_meld_hooks()
            pool.release(space)
        return target

    def prewarm_lesser_conduits(self, count: int) -> int:
        """
        Public API

        Ensure pooled lesser-conduit shells exist before traffic arrives.

        Purpose:
            Move first-use lesser construction cost (conduit shell, ward,
            creations registry, meld door, spellspace pool) from the first
            scope cycles to an explicit, owner-chosen moment. Useful for
            burst-concurrency starts; irrelevant for steady single-threaded
            reuse where one shell cycles forever.

        Contract:
            - Creates and immediately soft-cleans lesser conduits through the
              normal `create_lesser_conduit()` / `cleanup()` lanes, so all
              lifecycle hooks configured for lesser creation fire per shell
              exactly as they would for real traffic.
            - Clamped to pool capacity: ensures at most
              `min(count, pool.max_idle)` idle shells.
            - Idempotent in effect: already-idle shells are drained and
              returned, not duplicated.

        Args:
            count:
                Requested number of idle pooled lesser shells. Must be
                positive.

        Returns:
            int: Number of idle shells ensured (the capacity-clamped target).

        Raises:
            ValueError: If `count` is not positive.
            RuntimeError: If the conduit has been cleaned or lesser creation
                is invalid for this conduit's lineage.
        """
        self.check_cleaned()
        if count <= 0:
            raise ValueError(
                "prewarm_lesser_conduits requires a positive count; got "
                f"{count}. Provide how many idle shells should exist."
            )
        pool = self._conduit_pool
        target = min(count, pool.max_idle)
        held = [self.create_lesser_conduit() for _ in range(target)]
        for lesser in held:
            lesser.cleanup()
        return target



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
        if self._conduit_state is not ConduitState.normal:
            return
        self._ensure_transaction_identity_registered()
        self._transaction_identity.set_available_transactions(
            (
                "bind",
                "scan",
                "link",
                "unlink",
                "cluster_link",
                "mutation",
                "transfer_ownership",
                "notch",
                "add_to_index",
                "remove_from_index",
                "add_spell_or_index_to_contract",
                "remove_spell_or_index_from_contract",
            )
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
            transaction_name: Optional[ChangeTransactionType],
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
            return transaction_name != ChangeTransactionType.BIND and not self.__dynamic_environment__
        if transaction_name == ChangeTransactionType.BIND:
            return self._bind_family_blocked_for_current_posture()
        if frame_configuration.disable_all_transactions_after_conjure:
            return True
        if transaction_name == ChangeTransactionType.LINK:
            return (
                frame_configuration.disable_linking
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == ChangeTransactionType.TRANSFER_OWNERSHIP:
            return (
                frame_configuration.disable_transfer_of_ownership
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == ChangeTransactionType.CLUSTER_LINK:
            return (
                frame_configuration.disable_conduit_cluster
                or frame_configuration.system_state is not SystemState.dynamic
            )
        if transaction_name == ChangeTransactionType.MUTATION:
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

        Register a normal root or retain an unpublished lesser shell.

        Contract:
            Root admission publishes both ownership and named discovery. Lesser
            names are assigned by create_lesser_conduit for each acquisition and
            published only when its parent link is established.

        Raises:
            RuntimeError: If normal conduit registration fails.
        Returns:
            None.
        """
        if self._conduit_state == ConduitState.normal:
            try:
                self._add_root_conduit()
                self._add_spells_to_aether()
            except Exception as e:
                self._logger.error(f"Normal conduit registration failed: {e}", "__init__", exc_info=True)
                raise

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

        Contract:
            - Acquires the conduit lock and returns `self`, so `with conduit:` groups
              several operations under one lock rather than exposing `_lock`.
            - The lock is REENTRANT, so nested `with` blocks are legal and each level
              must exit.
            - Performs no cleaned-state check of its own; callers must be operating
              on a live conduit.

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

        Contract:
            - Releases unconditionally, including when the block raised. Exception
              arguments are accepted and IGNORED, so no exception is suppressed.
            - Exactly one release per `__enter__`; the lock is reentrant.

        Threading:
            Releases the conduit lock acquired by `__enter__`.

        Lifecycle / Cleanup:
            Performs no cleaned-state check - it is purely the unlock half.

        Raises:
            RuntimeError: If called without a matching `__enter__` on this thread.

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

        Contract:
            - GUARDED BY `check_cleaned()`, which is unusual for a repr: printing or
              logging a CLEANED conduit RAISES rather than degrading to a
              placeholder. Take care with debugger watches and post-teardown logging.
            - Shows name and id only, not state or contents.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

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

        Contract:
            - The conduit's stable identity, assigned at construction and unchanged for
              its life - including across cluster join and leave.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

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

        Contract:
            - NORMALIZES EMPTY TO NONE: an unnamed conduit and one named with an empty
              string are indistinguishable through this property, both reporting
              None.
            - Names are a convenience label, not identity - use `id` for identity.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

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
            - Normal-conduit labels remain write-once.
            - Lesser and pooled scopes reject this setter. Supply their name to
              create_lesser_conduit; release clears it internally before reuse.

        Args:
            name (str):
                Name to assign to this conduit.

        Raises:
            RuntimeError:
                If the conduit is lesser/pooled or its name is already set.


        Contract:
            - NORMALIZES EMPTY TO NONE: an unnamed conduit and one named with an empty
              string are indistinguishable through this property, both reporting
              None.
            - Names are a convenience label, not identity - use `id` for identity.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            raise RuntimeError(
                "Lesser conduit names are assigned only at creation; use "
                "create_lesser_conduit(name=...) for each scope."
            )
        if self._name is not None:
            self._logger.error("Attempt to rename conduit after name set", "name")
            raise RuntimeError("Conduit name is set.")
        self._name = name

    def get_conduit_cloud(self) -> "ConduitCloud":
        """
        Public API

        Return the frame-owned conduit cloud tied to this conduit.

        Contract:
            - Reaches THROUGH the aetheric frame to the frame-owned cloud, so the
              returned object is shared by every conduit on the frame - it is
              BORROWED, never owned here, and must not be cleaned by the caller.

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
    def _initialize_hook_baselines(
            self,
            *,
            conduit_hooks: Optional[dict[str, list[Any]]] = None,
            meld_hooks: Optional[dict[str, list[Callable[..., Any]]]] = None,
    ) -> None:
        """
        Establish hook-container ownership during construction or graduation.

        Args:
            conduit_hooks: Selected lifecycle events, or ordinary configuration/root defaults.
            meld_hooks: Selected Meld events, or ordinary configuration/root defaults.

        Contract:
            Normal roots own shallow container copies, even when empty. Lessers
            borrow root baselines so later shared edits remain visible. Callback
            objects are borrowed; frozen configuration containers are never mutated.
            Resets local lifecycle overlays. The caller initializes/rebinds Meld
            references afterward and owns quiescence during graduation.

        Returns:
            None.

        Raises:
            RuntimeError: A lesser has no live root from which to inherit hooks.
        """
        if self._conduit_state is ConduitState.normal:
            if conduit_hooks is None:
                conduit_hooks = self._configuration.get_conduit_hooks(self._spellbook._id)
            if meld_hooks is None:
                meld_hooks = self._configuration.get_meld_hooks(self._spellbook._id)
            self._conduit_hooks = {name: list(callbacks) for name, callbacks in conduit_hooks.items()}
            self._meld_hooks = {name: list(callbacks) for name, callbacks in meld_hooks.items()}
        else:
            root = self._aetheric_frame._conduits.get(self._root_conduit_id)
            if root is None:
                raise RuntimeError("Root conduit is unavailable for hook inheritance.")
            self._conduit_hooks = root._conduit_hooks if conduit_hooks is None else conduit_hooks
            self._meld_hooks = root._meld_hooks if meld_hooks is None else meld_hooks
        # Local event overlays are owned by this conduit only.
        self._local_conduit_hooks: Optional[dict[str, list[Any]]] = None

    @property
    def hooks_modified(self) -> bool:
        """
        Report local lifecycle overlays or temporary Meld hooks on this conduit.

        Contract:
            Diagnostic read under existing mutation locks. Root-shared changes
            update the baseline and do not themselves count as local divergence.
            Pool paths inspect existing local state and the Meld bool directly.

        Returns:
            bool: Whether lease return has local hook state to restore.

        Raises:
            RuntimeError: This conduit or its Meld has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return bool(self._local_conduit_hooks) or self._meld.hooks_modified

    def register_conduit_hooks(
            self,
            hooks: dict[str, Any],
            *,
            create_local_hooks: bool = True,
            overwrite: bool = False,
    ) -> None:
        """
        Public API

        Register hook callables for this Conduit.

        The default is local additive registration. Explicit shared mode updates
        a normal root's live baseline so inheriting scopes see the changes without
        a hierarchy walk. Configuration and other normal roots are unaffected.

        Contract:
            - Empty additive input is a no-op. Empty replacement selects both families.
            - SPLITS the supplied mapping into conduit-lane and meld-lane updates and
              applies each to its own registry, so one call can touch two subsystems.
            - Additive registration - it does not clear hooks registered earlier.
              overwrite=True replaces the supplied families instead.
            - Validates the whole batch before changing either family. Local
              lifecycle lists retain their existing event-shadow/fallback rules;
              local Meld updates copy the effective map. Shared mode selects the
              root baseline for the caller, dropping its selected local overrides.
            - Writers use existing locks and replace event lists. Readers retain
              current per-event semantics, not a whole-operation callback snapshot.

        Args:
            hooks: Mapping of hook name -> callable or iterable of callables.
            create_local_hooks: True isolates changes on this conduit. False is
                normal-root-only and publishes into its stable lineage maps.
            overwrite: True replaces each supplied family; omitted families stay
                unchanged. An empty replacement clears local lifecycle overlays
                (revealing inherited hooks) and installs an empty local Meld map;
                shared empty replacement clears both root baselines.

        Raises:
            RuntimeError: Cleaned conduit or a shared update attempted through a lesser.
            ValueError / TypeError: If hook names or values are invalid.

        Returns:
            None.
        """
        self.check_cleaned()
        if not hooks and not overwrite:
            return
        if not isinstance(hooks, dict):
            raise TypeError("Conduit hooks must be a dictionary of event names to callbacks.")
        if not create_local_hooks and self._conduit_state is not ConduitState.normal:
            raise RuntimeError("Shared hooks must be changed through the normal root conduit.")

        # Normalize into owned lists before publication, so a late invalid Meld
        # entry cannot leave a lifecycle update partially installed.
        normalized: dict[str, list[Any]] = {}
        self._merge_conduit_hooks(normalized, hooks)
        conduit_hook_updates: dict[str, Any] = {}
        meld_hook_updates: dict[str, Any] = {}
        for name, value in normalized.items():
            if name in self._configuration._MELD_HOOK_NAMES:
                meld_hook_updates[name] = value
            else:
                conduit_hook_updates[name] = value

        with self._lock:
            self.check_cleaned()
            if conduit_hook_updates or not normalized:
                if create_local_hooks:
                    if overwrite or self._local_conduit_hooks is None:
                        self._local_conduit_hooks = {}
                    target = self._local_conduit_hooks
                else:
                    target = self._conduit_hooks
                    if overwrite:
                        target.clear()
                    self._local_conduit_hooks = None
                for name, callbacks in conduit_hook_updates.items():
                    if callbacks:
                        target[name] = target.get(name, []) + callbacks
            if meld_hook_updates or not normalized:
                self._meld.register_meld_hooks(
                    meld_hook_updates,
                    create_local_hooks=create_local_hooks,
                    overwrite=overwrite,
                )

    def set_conduit_hooks(
            self,
            hooks: dict[str, Any],
            *,
            create_local_hooks: bool = True,
            overwrite: bool = True,
    ) -> None:
        """
        Replace supplied runtime hook families, with local state as the default.

        Args:
            hooks: Lifecycle/Meld events and callable or list/tuple values.
                Empty input replaces both families; it clears local lifecycle
                overlays and mutes local Meld callbacks, or clears shared roots.
            create_local_hooks: True changes this scope only. False publishes a
                normal root baseline update to inheriting scopes.
            overwrite: True replaces the selected family maps. False explicitly
                selects additive registration through the same implementation.

        Contract:
            Delegates complete validation, root authority and mutation locking to
            register_conduit_hooks. Callback objects are not cloned or invoked.

        Returns:
            None.

        Raises:
            RuntimeError: Cleaned scope or shared changes requested from a lesser.
            ValueError: Unknown hook event.
            TypeError: Invalid callback payload.
        """
        self.register_conduit_hooks(
            hooks, create_local_hooks=create_local_hooks, overwrite=overwrite,
        )

    def _validate_conduit_hooks_payload(
            self,
            hooks: Optional[Dict[str, Any]],
    ) -> None:
        """
        Internal

        Validate a hooks mapping without mutating any hook registry.

        Purpose:
            Give mutation-bearing flows a validate-before-mutate seam
            (BUG-071, 2026-07-17 audit: `upgrade_to_normal` registered hooks
            LAST, so an invalid payload raised after the upgrade had already
            committed irreversibly). Rejecting a bad payload here, before the
            first mutation, keeps a reported failure equal to zero state
            change.

        Contract:
            - Accepts None/empty as valid (registration would no-op).
            - Applies exactly the `_merge_conduit_hooks` rules by merging into
              a throwaway map: hook names must be in
              `Configuration._ALLOWED_HOOKS`; values must be a callable or a
              list/tuple of callables. Identical error surface by
              construction, zero duplicated validation logic.
            - Never touches `_local_conduit_hooks`, meld hooks, or any other
              owned state.

        Args:
            hooks:
                Candidate mapping of hook name -> callable or iterable of
                callables, or None.

        Raises:
            ValueError: On an unknown hook name.
            TypeError: On a non-callable hook value shape.
        """
        if not hooks:
            return
        scratch: Dict[str, Any] = {}
        self._merge_conduit_hooks(scratch, hooks)

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
            # Propagate the lineage-root store down with the root id: self is in
            # this lineage, so its meld already points at the lineage root's
            # store; the lesser's meld shares that same root store.
            lesser_conduit._meld._root_creations = self._meld._root_creations
            # Propagate the one lineage cluster facade down (the conduit owns it,
            # the meld only references it). Re-point the borrowed reference on
            # both the lesser conduit and its meld; never cleaned here.
            lesser_conduit._cluster_creations = self._cluster_creations
            lesser_conduit._meld._cluster_creations = self._cluster_creations
            lesser_conduit._set_creation_gate_controller_for_lineage()

    def upgrade_to_normal(
            self,
            name: str,
            *,
            configuration: Optional[SpellbookConfiguration] = None,
            hooks: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Promote this childless lesser into an independent normal root in place.

        Purpose:
            Keep this runtime's identity and retained creations while giving it
            a fresh, empty Spellbook for its own bindings and links. Spellbook's
            private existing-conduit conjure route owns configuration, phases,
            attachment and normal activation; this method prepares its target.

        Contract:
            - Requires a live, attached, childless lesser in a dynamic frame.
            - The new root has no parent or inherited definitions/contracts.
              Old spell IDs are no longer resolvable; retained objects remain
              in their existing stores for eventual disposal.
            - Uses ordinary Spellbook configuration selection: omitted local
              configuration means fresh defaults; frame-wide sharing adopts its
              canonical configuration and refuses a conflicting supplied object.
            - Bind callbacks start empty unless the selected configuration seeds
              them. Conduit/Meld hooks likewise start from that configuration.
              Changes to the new Book's Bind registry never change the old Book.
            - Validates hooks before mutation. Configuration/setup failures before
              Book attachment restore the lesser and retire only newly owned state.
              After attachment, publication failures leave a normal root whose
              cleanup belongs to the caller, as with ordinary conjure.
            - Reserves the requested name during preparation, retaining any existing
              lesser entry until root registration atomically replaces its alias.
              Same-name promotion is legal. Failure releases the temporary claim.

        Args:
            name: Name for the new root and ConduitCloud registration.
            configuration: Prepared same-frame configuration, or None for ordinary
                default/shared selection. A local configuration already owned by
                the former Book cannot be reused; supply a new one instead.
            hooks: Optional local runtime additions, installed after normal conjure
                activation. Values are callables or lists/tuples of callables.

        Raises:
            RuntimeError: Invalid lifecycle/posture, children, detached target,
                configuration conflict, gate drain timeout or conjure failure.
            ValueError: Duplicate name, invalid configuration, or unknown hook.
            TypeError: Invalid name, configuration type or hook payload.

        Returns:
            None. The same Conduit becomes the new Book's sole normal root.

        Threading / Lifecycle:
            Drains this conduit before taking structural locks. Parent ward is
            locked before the target conduit/ward for detachment. Admission is
            restored before activation callbacks; an initially parked gate stays
            parked. Callers must quiesce concurrent scope acquisition, managed
            SpellSpaces on other threads, and lineage mutation/teardown during
            graduation. No locking or checks are added to ordinary meld calls.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            parent, root = self._validate_normal_upgrade(name)
            # BUG-071: reject the complete hook payload before changing status.
            self._validate_conduit_hooks_payload(hooks)
            if configuration is not None:
                if not isinstance(configuration, SpellbookConfiguration):
                    raise TypeError("configuration must be a SpellbookConfiguration or None.")
                configuration.check_cleaned()
                if (
                        configuration is self._configuration
                        and not self._spellbook._is_frame_owned_shared_configuration(configuration)
                ):
                    raise ValueError(
                        "The former Spellbook owns this local configuration. Supply a new "
                        "configuration or omit it for defaults; only frame-owned policy is shared."
                    )

        # The concrete constructor is needed here; importing locally avoids the
        # Spellbook -> Conduit module cycle while keeping conjure owned by Book.
        from melder.aether.spellbook.spellbook import Spellbook

        gate = self._creation_gate
        gate_was_enabled = gate.enabled
        new_book: Optional[Spellbook] = None
        prepared = False
        # Retain only the state needed to unwind a failed, pre-attachment promotion.
        previous_name = self._name
        previous_policy = self._conduit_ward._policy
        cloud = self._aetheric_frame._conduit_cloud
        cloud._reserve_conduit_name(self, name)
        try:
            gate.close_and_drain()
            with parent._conduit_ward._lock:
                with self._lock:
                    self.check_cleaned()
                    self._validate_normal_upgrade(name)
                    new_book = Spellbook(
                        aetheric_frame=self._aetheric_frame_name,
                        configuration=configuration,
                    )
                    new_book.get_configuration().validate()
                    # Retain Creations; its owner/scope already use this conduit ID.
                    # New root resources replace borrowed ones without cleaning them.
                    self._conduit_pool = ConduitPool(root_conduit=self, baseline_idle=20, max_idle=20)
                    self._cluster_creations = ClusterCreations()
                    prepared = True
                    self._conduit_state = ConduitState.normal
                    self._root_conduit_id = self._id
                    self._conduit_ward._convert_to_normal_conduit()
                    self._set_creation_gate_controller_for_lineage()

            # Do not copy old root verdicts: the independent empty Book runs its
            # own normal phases under this preserved conduit ID before attachment.
            new_book._conjure_existing_conduit(
                self, dynamic=True, name=name, restore_gate_enabled=gate_was_enabled,
            )
            if hooks:
                self.register_conduit_hooks(hooks)
        finally:
            try:
                if new_book is not None and self._spellbook is not new_book:
                    # Conjure has not attached the new owner. Restore the original
                    # lesser before retiring the failed Book and its local resources.
                    try:
                        if prepared:
                            self._restore_lesser_after_failed_upgrade(
                                parent, root, previous_name, previous_policy,
                            )
                        new_book._spell_system_states.drop_conduit_resolution_state(self._id)
                    finally:
                        new_book.cleanup()
            finally:
                try:
                    cloud._release_conduit_name(self, name)
                finally:
                    if gate_was_enabled and not gate.is_closed():
                        gate.open()

    def _validate_normal_upgrade(self, name: str) -> tuple[Conduit, Conduit]:
        """
        Validate promotion admission without mutating the lesser or its owners.

        Args:
            name: Requested nonempty normal-root name.

        Contract:
            Called before draining and rechecked under the structural locks.
            Rejects pooled/detached shells, descendants and other scopes' names.
            The same live identity may keep its own name during promotion.
            The public upgrade entry point owns cleaned-state admission.

        Returns:
            tuple[Conduit, Conduit]: Former direct parent and lineage root.

        Raises:
            RuntimeError: Non-dynamic, non-lesser, closed or invalid lineage.
            TypeError: Name is not a string.
            ValueError: Name is empty or belongs to another root/lesser in this frame.
        """
        if not self.__dynamic_environment__:
            raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
        if self._conduit_state is not ConduitState.lesser:
            raise RuntimeError("Only lesser conduits can be upgraded.")
        if not isinstance(name, str):
            raise TypeError("The upgraded conduit's name must be a string.")
        if not name:
            raise ValueError("The upgraded conduit requires a nonempty root name.")
        if self._creation_gate.is_closed():
            raise RuntimeError("A terminally closed conduit cannot be upgraded.")
        parent = self._conduit_ward._parent_conduit
        root = self._conduit_ward._root_conduit
        if parent is None or root is None:
            raise RuntimeError("Only an attached lesser conduit can be upgraded; acquire it from its root first.")
        if self._conduit_ward._lesser_conduits:
            raise RuntimeError("Cannot upgrade a lesser with children. Clean up its lesser conduits first.")
        self._aetheric_frame._conduit_cloud._assert_name_available(name, self._id)
        return parent, root

    def _restore_lesser_after_failed_upgrade(
            self,
            parent: Conduit,
            root: Conduit,
            name: Optional[str],
            policy: Policies,
    ) -> None:
        """
        Undo target preparation when conjure failed before replacing its Book.

        Args:
            parent: Original direct parent, quiesced for this transition.
            root: Original lineage owner of the borrowed pool/cluster facade.
            name: Original lesser name.
            policy: Original ward policy.

        Contract:
            Retires newly allocated root resources and ward identity, restores
            both lineage directions and gate membership, and keeps Creations and
            the borrowed Book alive. Called only while the creation gate is parked.
            Parent ward locks precede target locks, matching detachment ordering.

        Returns:
            None. Any teardown failure propagates instead of claiming a full undo.
        """
        with parent._conduit_ward._lock:
            with self._lock:
                self._conduit_pool.cleanup()
                self._cluster_creations.cleanup()
                self._conduit_pool = root._conduit_pool
                self._cluster_creations = root._cluster_creations
                self._conduit_state = ConduitState.lesser
                self._root_conduit_id = root._id
                self._name = name
                with self._conduit_ward._lock:
                    if self._conduit_ward._devops_identity is not None:
                        self._conduit_ward._devops_identity.cleanup()
                        self._conduit_ward._devops_identity = None
                    self._conduit_ward._conduit_type = ConduitState.lesser
                    self._conduit_ward._parent_conduit = parent
                    self._conduit_ward._root_conduit = root
                    self._conduit_ward._policy = policy
                    parent._conduit_ward._lesser_conduits[self._id] = self
                self._set_creation_gate_controller_for_lineage()




    @property
    def policy(self) -> Policies:
        """
        Public API

        Return the linking policy currently in force on this Conduit's ward.

        Purpose:
            The counterpart read for `set_new_policy`. Without it the policy is
            a WRITE-ONLY setting: a caller could change how linking behaves and
            then had no public way to ask what the behaviour now is. Melder
            does not conflate "I set it" with "it is in force" anywhere else,
            and the ward is no exception - `set_new_policy` can refuse (lesser
            conduit, existing contracts, automatic frame), so the value a
            caller last passed is not evidence of the value that is live.

        Contract:
            - Reports the LIVE ward policy, not a remembered argument. After a
              `set_new_policy` that raised, this still reads the policy that
              survived the refusal.
            - Available in every mode. Unlike `set_new_policy`, reading is not
              gated on a dynamic frame - an automatic conduit can be asked what
              it enforces even though it can never be told to enforce something
              else.
            - Available on lesser conduits, which also cannot be written to.
            - Returns the `Policies` MEMBER, not its name. Use `.name` for the
              string form; `.value` is an integer because `Policies` is built
              on `auto()`.
            - The returned member may be passed straight back into
              `set_new_policy`, which accepts a member or its string name.

        Threading:
            Unsynchronized read of a single attribute. A caller racing
            `set_new_policy` observes either the old or the new member and
            never a partial state, but the answer is a snapshot - do not cache
            it across an operation that may re-policy the conduit.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The ward is owned by this conduit and
            is torn down with it.

        Returns:
            Policies: The linking policy the ward is currently enforcing.

        Raises:
            RuntimeError: If the Conduit has been cleaned.
        """
        self.check_cleaned()
        return self._conduit_ward._policy

    def set_new_policy(self, policy: Union[str, Policies]) -> None:
        """
        Public API

        Sets a new policy for this Conduit. This is only allowed in dynamic mode.

        Contract:
            - DYNAMIC MODE ONLY. On an automatic frame this raises `RuntimeError`
              rather than silently ignoring the request, and the refusal is logged.
            - Applies the policy through the conduit ward under the conduit lock, so
              the swap is atomic with respect to other conduit operations.
            - NOT A CONFIRMATION. A successful return means the ward accepted
              the swap; read `policy` when you need the value that is live.

        Args:
            policy (Union[str, Policies]): The new policy to set, governing
                linking behavior. Accepts a `Policies` member or its lowercase
                string name, so the member returned by `policy` round-trips
                back through this call unchanged.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
            ValueError: If `policy` is a string that names no `Policies` member.

        Returns:
            None.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error("set_new_policy in non-dynamic env", "set_new_policy")
            raise RuntimeError("Dynamic environment is not enabled. Cannot set new policy.")
        with self._lock:
            self._conduit_ward._set_new_policy(policy)

        self._publish_conduit_record_to_nexus()

    def create_lesser_conduit(
            self,
            logger: Optional[Any] = None,
            *,
            name: Optional[str] = None,
    ) -> Conduit:
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook, Configuration, and
        injected frame-owned services, but is restricted in its ability to
        establish external links or register new spells. It owns a
        conduit-local CreationGate created by the lineage CreationGateController.
        Named acquisition publishes current Nexus metadata on both fresh and
        pooled paths before post-created callbacks. Anonymous fresh allocation
        keeps its existing publication; anonymous pooled cycles remain local
        without refreshing Nexus or dev-ops identity metadata.

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

        Concurrency:
            The parent lock is held only for the cleaned re-check and the
            ward link plus named-only publication (a narrow window inside
            `_link_new_lesser_under_lock`).
            Pool acquisition, fresh construction, pooled-shell reactivation,
            hook firing, and anonymous Nexus publishing run outside the parent lock,
            so concurrent lesser creation from many threads does not
            serialize on this parent. Hook implementations must be
            thread-safe under concurrent lesser creation.

        Contract:
            - The ROOT is resolved before anything is built: a normal conduit is
              its own root; a lesser borrows the original root's Book and pool
              while preserving this caller as its immediate parent.
            - Lesser conduits are a LINEAGE attachment, not a peer link; this is why
              `link()` explicitly refuses a lesser target.
            - A supplied name is an exact, nonempty, frame-wide unique string in
              either mode. Fresh and pooled scopes receive it before activation;
              Cloud publishes it with parent attachment, before post-created.
            - Names are creation-only. Cleanup unregisters and clears a name before
              pool return; unnamed scopes perform no directory mutation.
            - Discovery returns a borrowed reference and does not extend lifetime.

        Returns:
            Conduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent or named child is cleaned during acquisition.
            ValueError: Name is empty or already owned/reserved in this frame.
            TypeError: A supplied name is not a string.

        Args:
            logger:
                Optional logger; its existing positional calling convention is retained.
            name:
                Optional exact name for this use of the child scope.
        """
        self.check_cleaned()
        if name is not None:
            if self._conduit_state is ConduitState.pooled_lesser:
                raise RuntimeError("Named lesser creation requires an active parent, not a pooled conduit.")
            self._aetheric_frame._conduit_cloud._assert_name_available(name)

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
            if reused_from_pool:
                # Only pooled shells need the pooled_lesser -> lesser
                # transition; freshly constructed conduits already
                # initialized both state fields as lesser.
                new_conduit._conduit_state = ConduitState.lesser
                new_conduit._conduit_ward._conduit_type = ConduitState.lesser
            new_conduit._nexus_publish_enabled = self._nexus_publish_enabled

            if name is not None:
                new_conduit._name = name

            # Fire activation hook with the new conduit instance.
            self._fire_conduit_hooks(
                "on_conduit_activated",
                new_conduit,  # new lesser conduit
            )

            # 3) Link the lesser conduit into the parent's ConduitWard
            #    inside the narrow parent-lock window.
            self._link_new_lesser_under_lock(new_conduit, name=name)

            # Fire post-create hook with both parent and child.
            self._fire_conduit_hooks(
                "on_conduit_post_created",
                self,         # parent_conduit
                new_conduit,  # child_conduit
            )
            if not reused_from_pool and name is None:
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
            if reused_from_pool:
                # Only pooled shells need the pooled_lesser -> lesser
                # transition; freshly constructed conduits already
                # initialized both state fields as lesser.
                new_conduit._conduit_state = ConduitState.lesser
                new_conduit._conduit_ward._conduit_type = ConduitState.lesser
            new_conduit._nexus_publish_enabled = self._nexus_publish_enabled
            if name is not None:
                new_conduit._name = name
            self._link_new_lesser_under_lock(new_conduit, name=name)
            if not reused_from_pool and name is None:
                new_conduit._publish_conduit_record_to_nexus()

        return new_conduit

    def _link_new_lesser_under_lock(
            self, new_conduit: Conduit, *, name: Optional[str] = None,
    ) -> None:
        """
        Internal

        Link one just-acquired lesser conduit inside the narrow parent-lock
        window.

        Contract:
            - Holds the parent lock ONLY for the cleaned re-check, ward link and
              named-only publication. Pool acquisition, fresh construction, pooled-shell
              reactivation, hook firing, and anonymous Nexus publishing all run
              outside this lock. Named publication runs inside the existing
              named-only child lock, ordering it before cleanup and reuse.
              (Contention harness, melds-off mode: the
              previous whole-body hold cost 58-73% of thread-time in
              root-lock wait at threads=3/5 with negative throughput
              scaling; see profile_scope_cycle_contention.py.)
            - Create racing parent cleanup stays safe: cleanup holds this
              same lock, so the re-check either links before the teardown
              sweep observes the child or takes the unwind path below.
            - Unwind path: an unnamed shell uses its existing soft-cleanup path.
              A named orphan is permanently retired when its parent has already
              been cleaned/pooled, because the old owner's pool may be gone.
            - Named children additionally hold their own lock across attachment
              and directory publication. Cleanup cannot publish that shell idle
              between those steps. Failed named admission retires the shell through
              existing cleanup after the directory lock has been released.

        Args:
            new_conduit (Conduit): The unlinked lesser conduit to link.
            name: Requested creation name; None preserves ordinary unnamed linking.

        Raises:
            RuntimeError: Parent or named child was retired during acquisition.
            ValueError: A competing scope claimed the requested name.
        """
        with self._lock:
            if not self._cleaned:
                if name is not None:
                    if self._conduit_state is ConduitState.pooled_lesser:
                        new_conduit.permanent_cleanup()
                        raise RuntimeError("Named lesser creation requires an active parent, not a pooled conduit.")
                    with new_conduit._lock:
                        if new_conduit._cleaned or new_conduit._conduit_state is not ConduitState.lesser:
                            raise RuntimeError("Named lesser was retired (cleaned or pooled) during its creation hook.")
                        try:
                            self._conduit_ward._link_lesser_conduit(new_conduit)
                            self._aetheric_frame._conduit_cloud._register_named_conduit(new_conduit)
                            # Cloud's leaf lock is released before record callbacks.
                            # The child lock orders emission before any return/reuse.
                            new_conduit._emit_conduit_twin()
                            new_conduit._publish_conduit_record_to_nexus()
                            new_conduit._publish_frame_record_to_nexus()
                        except Exception:
                            # Admission failed after shell acquisition: retire only
                            # this candidate, preserving the registered name owner.
                            new_conduit.cleanup()
                            raise
                    return
                self._conduit_ward._link_lesser_conduit(new_conduit)
                return
        # Parent cleaned between shell acquisition and the link window:
        # recycle the orphan shell, then raise the standard cleaned error.
        if name is not None:
            new_conduit.permanent_cleanup()
        else:
            new_conduit.cleanup()
        raise RuntimeError("Conduit has been cleaned.")




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

        Contract:
            - Resolves through the spellbook's Aether-wide lookup, so it can find a
              conduit in ANOTHER frame - it is not scoped to this conduit's frame
              unless you pass one.
            - Runs under the conduit lock.

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

        Contract:
            - An EXISTENCE PROBE across the Aether rather than a local check, so a True
              answer does not mean this conduit can reach or meld the spell - only
              that the id is known.
            - Runs under the conduit lock.

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

        Contract:
            - Resolves via the spellbook's Aether-wide lookup, so the returned spell may
              belong to a different conduit; ownership and permission are separate
              questions from resolvability.
            - Unlike its siblings, this one does NOT hold the conduit lock across the
              lookup.

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

        Contract:
            - Resolves by SPELL INDEX id, so it addresses a whole version LINEAGE
              rather than one version - the spell you get back is the lineage's
              current selection, not a fixed version.
            - Logs and handles an unavailable spellbook rather than dereferencing it,
              so a torn-down conduit fails loudly rather than with an AttributeError.

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

        Contract:
            - Searches CONTRACTED spells across EVERY peer conduit's contract map in
              this spellbook, not just this conduit's own - it answers "is this spell
              reachable to me by contract", not "did I bind it".
            - Returns None when no contract exposes the id; that is a normal answer,
              not an error.

        Threading:
            Walks the contract maps under the conduit lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the conduit has been cleaned.

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

        Contract:
            - TRANSLATES THE UNDERLYING ERROR: the spellbook raises `RuntimeError` for
              a missing key and this method re-raises it as `ValueError`, chaining the
              original. Catch `ValueError` here, not `RuntimeError`.
            - The translation is deliberate - at the conduit boundary a missing spell
              is a caller-input problem, not a runtime fault.

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

        Contract:
            - Treats a FALSY key as not-found and raises `ValueError`, so this never
              returns an empty key.
            - Like `find_spell_id`, it presents a missing spell as a caller-input
              error at the conduit boundary.

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

        Contract:
            - Delegates to the spellbook's frame-wide inspection while holding the
              CONDUIT lock, so it inherits that method's three-stage search and its
              habit of collapsing every failure into None.
            - A None result is therefore AMBIGUOUS between "not registered" and
              "lookup failed"; do not treat it as proof of absence.

        Threading:
            Holds the conduit lock across the spellbook call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the conduit has been cleaned.

        Returns:
            Optional[str]: The SHA256 unique ID of the spell if found, otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            return self._spellbook.inspect_spell(spell, aetheric_frame)

    def begin_transaction(
            self,
            transaction_type: ChangeTransactionType,
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
                Optional normalized scope keys. These ARE the admission
                vocabulary: they become the request's scope claims, and the
                moded claim table acquires and arbitrates them.
            scope_hashes:
                Optional normalized scope hashes. ADVISORY IDENTITY ONLY - they
                carry NO claims and are NOT checked for conflicts. Their only
                reader is the retired `ChangeControlConflictManager`, which
                nothing calls. Supplying hashes declares no overlap and buys no
                isolation; use `scope_keys` to declare scope.
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

        request_type_value = transaction_type

        dynamic_only = {
            "link",
            "transfer_ownership",
            "mutation",
            "cluster_link",
            "unlink",
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

        if request_type_value == ChangeTransactionType.LINK:
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
                transaction_type=ChangeTransactionType.LINK,
                metadata=link_metadata,
            )
            return
        if request_type_value == ChangeTransactionType.UNLINK:
            if conduit_ids:
                for conduit_id in conduit_ids:
                    if conduit_id not in conduit_values:
                        conduit_values.append(conduit_id)
            unlink_metadata = dict(metadata) if metadata is not None else {}
            unlink_metadata.update({
                "origin_surface": "conduit.sever_link",
                "conduit_ids": tuple(conduit_values),
                "scope_keys": tuple(scope_keys) if scope_keys is not None else tuple(),
                "scope_hashes": tuple(scope_hashes) if scope_hashes is not None else tuple(),
                "binding_keys": tuple(binding_keys) if binding_keys is not None else tuple(),
                "contract_keys": tuple(contract_keys) if contract_keys is not None else tuple(),
            })
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.UNLINK,
                metadata=unlink_metadata,
            )
            return
        if request_type_value == ChangeTransactionType.BIND:
            self._spellbook.begin_transaction(
                ChangeTransactionType.BIND,
                conduit_id=self._id,
                scope_keys=scope_keys,
                scope_hashes=scope_hashes,
                binding_keys=binding_keys,
                metadata=metadata,
            )
            return
        if request_type_value == ChangeTransactionType.TRANSFER_OWNERSHIP:
            transfer_metadata = dict(metadata) if metadata is not None else {}
            transfer_metadata.setdefault(
                "origin_surface",
                "conduit.transfer_spell_ownership",
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.TRANSFER_OWNERSHIP,
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
            transaction_type: Optional[ChangeTransactionType] = None,
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
        if transaction_type == ChangeTransactionType.BIND:
            self._spellbook.end_transaction(ChangeTransactionType.BIND, success=success)
            return
        self._get_required_transaction_mediator().end_transaction(
            expected_type=transaction_type,
            success=success,
        )

    @contextmanager
    def transaction(
            self,
            transaction_type: ChangeTransactionType,
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
                Optional normalized scope keys. These ARE the admission
                vocabulary: they become the request's scope claims, and the
                moded claim table acquires and arbitrates them.
            scope_hashes:
                Optional normalized scope hashes. ADVISORY IDENTITY ONLY - they
                carry NO claims and are NOT checked for conflicts. Their only
                reader is the retired `ChangeControlConflictManager`, which
                nothing calls. Supplying hashes declares no overlap and buys no
                isolation; use `scope_keys` to declare scope.
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

        Returns:
            Generator[Conduit, None, None]: A context manager yielding this conduit
                inside a held change-control transaction window.
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

    def add_bind_hooks(
            self,
            *,
            pre: Optional[Sequence[Callable[[Any], object]]] = None,
            activation: Optional[Sequence[Callable[[Spell], object]]] = None,
            post: Optional[Sequence[Callable[[Spell], object]]] = None,
    ) -> None:
        """
        Register bind lifecycle callbacks on this normal conduit's owning Spellbook.

        Purpose:
            Expose the same registration customization through the Conduit that
            already facades bind and bind_inactive, using one Book-owned registry.

        Contract:
            - Requires a live normal conduit. Lessers borrow a Book and cannot
              change its bind-hook policy through this facade.
            - Delegates unchanged to Spellbook.add_bind_hooks. Sequences append
              in order; all supplied callbacks are validated before mutation.
            - Pre receives the incoming reference and rejects by raising.
              Activation receives the actual newly constructed Spell; post
              receives the completed active or parked registration before outer
              transaction commit. Callback return values are ignored.
            - Updates affect subsequent binds through either the Book or Conduit;
              an in-flight bind retains its captured callback set.
            - Hook setup follows Book's live-update contract independently of
              configuration freeze. It does not enable binding when the frame's
              existing bind admission rules prohibit it.
            - Existing Conduit/Meld runtime hooks and per-Spell creation hooks
              remain separate. Recording and cleanup stay with the owning Book.

        Args:
            pre: Ordered synchronous reference-checking callbacks.
            activation: Ordered callbacks receiving the new Spell definition.
            post: Ordered callbacks receiving the completed binding.

        Threading:
            Adds no Conduit lock or transaction window around delegation. The
            Book/Bind owner coordinates registry updates and recording.

        Returns:
            None.

        Raises:
            RuntimeError: If the conduit is cleaned or is not normal.
            TypeError: If the owning Book rejects a non-callable callback.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("add_bind_hooks called when conduit is not normal", "add_bind_hooks")
            raise RuntimeError("Only normal conduits can configure Spellbook bind hooks.")
        self._spellbook.add_bind_hooks(pre=pre, activation=activation, post=post)

    def clear_bind_hooks(self) -> None:
        """
        Clear all bind lifecycle callbacks from this normal conduit's owning Book.

        Contract:
            - Requires a live normal conduit; lessers cannot clear the borrowed
              Book's registration policy.
            - Delegates to Spellbook.clear_bind_hooks. Future Book/Conduit binds
              see the empty registry; in-flight binds keep their captured set.
            - Leaves existing Spell creation hooks and Conduit/Meld runtime hooks
              unchanged. Does not dispose user callbacks or existing creations.
            - The Book refreshes recording markers where applicable. Setup and
              clearing do not change actual bind admission or frame posture.

        Threading:
            Delegates without an additional Conduit lock or transaction. Callback
            storage, synchronization and recording remain owned by Book/Bind.

        Returns:
            None.

        Raises:
            RuntimeError: If the conduit is cleaned or is not normal.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("clear_bind_hooks called when conduit is not normal", "clear_bind_hooks")
            raise RuntimeError("Only normal conduits can configure Spellbook bind hooks.")
        self._spellbook.clear_bind_hooks()

    def bind(
            self,
            *,
            spell: Any,
            existence: str | Existence,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            profile: str = "general",
            resolvable: bool = True,
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
            resolvable (bool):
                Native per-version resolution capability, forwarded unchanged to Spellbook.
                Defaults to True; False retains existing binding and lifetime rules.
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
                If invalid hook types or a non-bool resolvable value are provided.

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
        # The bind transaction now lives entirely inside Spellbook.bind(), which
        # opens the single bind window and runs the registration under it. The
        # conduit delegates rather than opening its own window: the mediator
        # forbids a second nested transaction root on the same thread, and
        # bind() claims the bind embargo before taking any object lock, so the
        # embargo-then-lock order is preserved.
        return self._spellbook.bind(
            spell=spell,
            existence=existence,
            spellframe=spellframe,
            binding_name=binding_name,
            profile=profile,
            resolvable=resolvable,
            permissions=permissions,
            **kwargs,
        )

    def bind_inactive(
            self,
            *,
            spell: Any,
            spell_index: Any,
            existence: Union[str, Existence],
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            profile: str = "general",
            resolvable: bool = True,
            **kwargs: Any,
    ) -> str:
        """
        Public API

        Stage a spell as an INACTIVE member of an existing owned `spell_index`,
        off the resolution surface, for later activation via `notch_spell`.

        Purpose:
            Create a spell and park it as an inactive candidate on an existing
            index in one call, so a later notch can promote it. This is the
            index-aware sibling of `bind` (which always activates its spell on a
            freshly minted index).

        Contract:
            - Only available in a dynamic environment; raises otherwise.
            - Only normal conduits may stage spells.
            - Delegates to the owning Spellbook's `bind_inactive` surface.
            - Change-control transaction admission for this staging op is owned by
              the conduit/mediator lane (wired separately); this facade performs
              the dynamic gate and delegation only, holding no transaction window.

        Args:
            spell (Any):
                The class, function, lambda, or existing object to register.
            spell_index (Any):
                The already-owned SpellIndex to attach the inactive spell to.
            existence (Union[str, Existence]):
                Lifecycle scope for the spell.
            permissions (str):
                Permission level exposed to other conduits (`read`, `create`, or
                `block`).
            spellframe (Any):
                Logical interface/frame grouping key for the spell.
            binding_name (Optional[str]):
                Secondary disambiguation key within the frame.
            profile (str):
                Spell profile family to attach after bind completion.
            resolvable (bool):
                Native capability of this parked version, forwarded unchanged to Spellbook.
                Defaults to True and is independent of active index selection.
            **kwargs:
                Optional lifecycle hooks (pre/activation/post).

        Returns:
            str:
                The SHA256 `spell_id` of the parked inactive spell.

        Raises:
            RuntimeError:
                If the conduit is cleaned, is not normal, the dynamic environment
                is not enabled, or there is no owning Spellbook.
            TypeError:
                If resolvable is not a bool or Bind rejects the target.
        """
        self.check_cleaned()
        if self._conduit_state is not ConduitState.normal:
            self._logger.error("bind_inactive called when conduit is not normal", "bind_inactive")
            raise RuntimeError("Only normal conduits can bind spells.")
        if not self.__dynamic_environment__:
            self._logger.error("bind_inactive called in non-dynamic env", "bind_inactive")
            raise RuntimeError(
                "Dynamic environment is not enabled. bind_inactive requires dynamic mode."
            )
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for bind_inactive.")
        new_spell_id = self._spellbook.bind_inactive(
            spell=spell,
            spell_index=spell_index,
            existence=existence,
            permissions=permissions,
            spellframe=spellframe,
            binding_name=binding_name,
            profile=profile,
            resolvable=resolvable,
            **kwargs,
        )
        # The new inactive member joined `spell_index`; if that index is shared
        # through an index-link, propagate the member to borrowers (parked copy +
        # per-member Detail), exactly like `add_to_spell_index` does after a move.
        self._conduit_ward._emit_index_member_added(spell_index, new_spell_id)
        return new_spell_id

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

        Contract:
            - NORMAL CONDUITS ONLY: a lesser or pooled conduit raises rather than
              scanning, checked before any posture rule.
            - Then posture-gated - refused when the frame disables the bind family,
              which includes post-conjure scanning on a non-dynamic frame.
            - Reuses an already-active binding transaction when one exists; otherwise
              opens and closes its own, so a direct conduit-side scan is always
              transaction-correct.

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
        with self.transaction(ChangeTransactionType.BIND):
            with self._lock:
                return Scan(self._spellbook).scan_module(module)


    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its version spell_id, **within this
        conduit**.
        This returns the access level ("read", "create", "block") defined when the
        spell was bound.

        Contract:
            - LOCAL ONLY. It walks THIS conduit's spellbook lineages, so a spell
              reachable by contract from a peer conduit is NOT found here.
            - Matches by LINEAGE MEMBERSHIP (`SpellIndex.has_spell`), so a superseded
              version id still resolves - and it resolves to the CURRENT permissions,
              not the permissions that version was bound with.
            - NEVER RETURNS None despite the `Optional[str]` annotation: a miss RAISES
              `RuntimeError`. Treat the annotation as wrong and the Raises block as
              authoritative.
            - Returns the permission enum's `.name` STRING, not the enum member.

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
                if spell_index.has_spell(spell_id):
                    target_spell = spell
                    break

        if target_spell is not None:
            perms = target_spell.permissions.name
            return perms

        self._logger.error(f"Spell with ID {spell_id} not found", "get_spell_permissions")
        raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")

    # NOTE (2026-07-11): get_mutation_research() DELETED - the conduit door
    # was ruled out of the converged MR model (owner ruling: conduits and
    # frames carry no mutation dimension). REVERSED for conduits/spellbooks
    # only by owner ruling 2026-07-12 (patch
    # mutation_research_accessor_doors_2026_07_12): the door returns below
    # as a borrowed get-the-object property. Frames still carry no mutation
    # dimension; the Rift rooms remain the mediated agent surface.

    @property
    def mutation_research(self) -> MutationResearch:
        """
        Return the Aether-hosted MutationResearch WORLD root.

        Purpose:
            Accessor door (owner ruling 2026-07-12): hand back the one
            process-wide research root from the conduit, mirroring how
            this conduit already carries `_crystallizer` from its owning
            spellbook.

        Contract:
            - The reference is BORROWED and world-scoped: it is the exact
              object `Aether().mutation_research` returns, never a
              conduit-scoped view. This conduit never cleans it.
            - The door only returns the object. Activation, liveness, and
              recording gates are enforced by the root's own verbs; an
              inactive root refuses research work itself.
            - Bound once at `__init__` from the owning spellbook; lesser
              conduits share the same root through the shared book. The
              reference is deleted during cleanup.

        Returns:
            MutationResearch: The hosted mutation-research singleton root.

        Raises:
            RuntimeError: If the conduit has been cleaned.
        """
        self.check_cleaned()
        return self._mutation_research



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
            move_creations:
                If True, move conduit-owned creation state; otherwise tear that
                source-side conduit-owned state down.
                Spellspace-local request objects are intentionally excluded from
                ownership transfer and are not preserved onto the target
                conduit.
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
                ChangeTransactionType.TRANSFER_OWNERSHIP,
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
        Build transfer metadata + discover the affected footprint for one transfer.

        Purpose:
            The conduit owns the `TRANSFER_OWNERSHIP` transaction, so it also owns
            the domain footprint discovery: here (before the window opens) it
            resolves the live spell, runs the read-only `TransferOfOwnership`
            preflight, and collects every affected participant. The DevOps strategy
            then stays envelope-only and plans scopes purely from this metadata.

        Contract:
            - Resolves the live source spell and runs the read-only transfer
              preflight to discover the affected footprint (source, target,
              borrowers, and cluster members) on the domain side.
            - Stamps the footprint into metadata: participant_conduit_ids,
              affected_cluster_ids, affected_identity_keys, binding_keys, the
              source/target spellbook ids, and the preflight borrower/dependency
              summaries.
            - Preserves the exact transfer-option booleans supplied by the caller.
            - Raises when the caller supplies an unsupported spell handle or the
              source spell cannot be resolved on this conduit.

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
                Transfer metadata, including the fully discovered affected
                footprint, for the (envelope-only) strategy layer.

        Threading:
            Runs before the `TRANSFER_OWNERSHIP` window opens. The preflight is
            read-only (`TransferOfOwnership._build_preflight_summary`) and does
            not mutate change-control, registry, or runtime state.
        """
        spell_id: Optional[str] = None
        spell_index_id: Optional[str] = None
        spell_obj: Optional[Spell] = None

        if isinstance(spell, str):
            spell_id = spell
        else:
            try:
                spell_id = spell.spell_id
                spell_index_id = spell.spell_index.id
                spell_obj = spell
            except AttributeError:
                try:
                    spell_index_id = spell.id
                    spell_id = spell.selected_spell_id
                except AttributeError as exc:
                    raise TypeError(
                        "spell must be a Spell-compatible object, SpellIndex-compatible "
                        "object, or spell_id string."
                    ) from exc

        if spell_obj is None:
            spell_obj = self._resolve_transfer_spell(
                spell_id=spell_id,
                spell_index_id=spell_index_id,
            )

        footprint = self._discover_transfer_footprint(
            spell_obj=spell_obj,
            target_conduit=target_conduit,
            move_creations=move_creations,
            include_dependencies=include_dependencies,
            force_unshare=force_unshare,
            invalidate_after_transfer=invalidate_after_transfer,
            mark_dependencies_dirty=mark_dependencies_dirty,
        )

        metadata: Dict[str, object] = {
            "origin_surface": "conduit.transfer_spell_ownership",
            "transfer_mode": "conduit_transfer_ownership",
            "source_conduit_id": self._id,
            "target_conduit_id": target_conduit._id,
            "spell_id": spell_obj.spell_id,
            "spell_index_id": spell_obj.spell_index.id,
            "binding_keys": (spell_obj.key,),
            "move_creations": move_creations,
            "include_dependencies": include_dependencies,
            "force_unshare": force_unshare,
            "invalidate_after_transfer": invalidate_after_transfer,
            "mark_dependencies_dirty": mark_dependencies_dirty,
            **footprint,
        }
        return metadata

    def _discover_transfer_footprint(
            self,
            *,
            spell_obj: "Spell",
            target_conduit: "Conduit",
            move_creations: bool,
            include_dependencies: bool,
            force_unshare: bool,
            invalidate_after_transfer: bool,
            mark_dependencies_dirty: bool,
    ) -> Dict[str, object]:
        """
        Discover the affected footprint of one ownership transfer (domain side).

        Purpose:
            Run the read-only `TransferOfOwnership` preflight and fold the source,
            target, borrowers, and cluster members into the participant + identity
            footprint that the (envelope-only) strategy plans scopes from. Kept out
            of `_build_transfer_transaction_metadata` to keep each method cohesive.

        Contract:
            - The preflight is read-only: it mutates no change-control, registry, or
              runtime state, and the helper is cleaned up on every exit path.

        Args:
            spell_obj: The resolved live spell being transferred.
            target_conduit: The conduit that will become the new owner.
            move_creations:
                Whether creation state should move to the target.
            include_dependencies:
                Whether owned dependency lineages should also transfer.
            force_unshare:
                Whether borrower visibility should be stripped instead of repointed.
            invalidate_after_transfer:
                Whether the moved lineage should remain gated/dirty afterward.
            mark_dependencies_dirty:
                Whether dependencies should be dirtied when they are not moved.

        Returns:
            Dict[str, object]:
                The discovered footprint: participant_conduit_ids,
                affected_cluster_ids, affected_identity_keys, the source/target
                spellbook ids, and the preflight borrower/dependency summaries.
        """
        # Local import: TransferOfOwnership lives under the ward (below this module
        # in the import graph); a local import avoids a module-import cycle.
        from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import (
            TransferOfOwnership,
        )

        registry = self._aetheric_frame.devops_information_registry

        transfer_helper = TransferOfOwnership(
            source_conduit=self,
            target_conduit=target_conduit,
            spell=spell_obj,
            move_creations=move_creations,
            include_dependencies=include_dependencies,
            force_unshare=force_unshare,
            invalidate_after_transfer=invalidate_after_transfer,
            mark_dependencies_dirty=mark_dependencies_dirty,
        )
        try:
            preflight_summary = transfer_helper._build_preflight_summary(spell_obj)
        finally:
            transfer_helper.cleanup()

        source_spellbook_id = self._resolve_spellbook_id_for_conduit(
            registry=registry,
            conduit=self,
        )
        target_spellbook_id = self._resolve_spellbook_id_for_conduit(
            registry=registry,
            conduit=target_conduit,
        )

        conduit_ids: Set[str] = {self._id, target_conduit._id}
        cluster_ids: Set[str] = set()
        affected_identity_keys: Set[Tuple[str, str]] = {
            ("conduit", self._id),
            ("conduit", target_conduit._id),
            ("conduit_ward", self._id),
            ("conduit_ward", target_conduit._id),
        }
        if source_spellbook_id is not None:
            affected_identity_keys.add(("spellbook", source_spellbook_id))
        if target_spellbook_id is not None:
            affected_identity_keys.add(("spellbook", target_spellbook_id))

        self._collect_cluster_memberships(
            registry=registry,
            conduit_id=self._id,
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )
        self._collect_cluster_memberships(
            registry=registry,
            conduit_id=target_conduit._id,
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )
        self._collect_borrower_participants(
            registry=registry,
            borrowers=preflight_summary["borrowers"],
            conduit_ids=conduit_ids,
            cluster_ids=cluster_ids,
            affected_identity_keys=affected_identity_keys,
        )

        return {
            "source_spellbook_id": source_spellbook_id,
            "target_spellbook_id": target_spellbook_id,
            "participant_conduit_ids": tuple(sorted(conduit_ids)),
            "affected_cluster_ids": tuple(sorted(cluster_ids)),
            "affected_identity_keys": tuple(sorted(affected_identity_keys)),
            "preflight_borrowers": tuple(
                sorted(self._normalize_borrower_metadata(preflight_summary["borrowers"]))
            ),
            "preflight_dependencies": tuple(preflight_summary["dependencies"]),
        }

    def _resolve_transfer_spell(
            self,
            *,
            spell_id: Optional[str],
            spell_index_id: Optional[str],
    ) -> "Spell":
        """
        Resolve the live spell being transferred from this (source) conduit.

        Purpose:
            Footprint discovery needs the live spell to run the read-only
            transfer preflight and to read its binding key. The source conduit
            owns the spell, so it is resolved directly here (domain side) rather
            than reached for by the DevOps strategy.

        Args:
            spell_id: Current spell id, if available.
            spell_index_id: Stable spell-index id, if available.

        Returns:
            Spell: The resolved live spell owned by this conduit.

        Raises:
            RuntimeError: If neither identifier resolves a local spell.
        """
        resolved: Optional[Spell] = None
        if isinstance(spell_index_id, str) and spell_index_id.strip():
            resolved = self.get_spell_by_index_id(spell_index_id)
        if resolved is None and isinstance(spell_id, str) and spell_id.strip():
            resolved = self.get_spell_by_id(spell_id, self._aetheric_frame_name)
        if resolved is None:
            raise RuntimeError(
                "[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit."
            )
        return resolved

    def _resolve_spellbook_id_for_conduit(
            self,
            *,
            registry: "DevopsInformationRegistry",
            conduit: "Conduit",
    ) -> Optional[str]:
        """
        Resolve the owning spellbook id for one conduit (registry-first).

        Args:
            registry: Frame-local topology registry for ownership lookups.
            conduit: Conduit whose owning spellbook should be resolved.

        Returns:
            Optional[str]: The owning spellbook id when available.
        """
        spellbook_id = registry.get_spellbook_for_conduit(conduit._id)
        if spellbook_id:
            return spellbook_id
        spellbook = conduit._spellbook
        if spellbook is None:
            return None
        return spellbook._id

    def _collect_cluster_memberships(
            self,
            *,
            registry: "DevopsInformationRegistry",
            conduit_id: str,
            conduit_ids: Set[str],
            cluster_ids: Set[str],
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> None:
        """
        Fold one conduit's cluster memberships into the transfer footprint.

        Purpose:
            A transfer touches every cluster the source/target belong to (the
            shared roots ripple across members), so the affected footprint must
            include those clusters and their members.

        Args:
            registry: Frame-local topology registry.
            conduit_id: Conduit whose memberships are folded in.
            conduit_ids: Participant conduit-id set being accumulated.
            cluster_ids: Cluster-id set being accumulated.
            affected_identity_keys: Affected identity-key set being accumulated.
        """
        resolved_cluster_ids = registry.get_clusters_for_conduit(conduit_id)
        for cluster_id in resolved_cluster_ids:
            cluster_ids.add(cluster_id)
            affected_identity_keys.add(("conduit_cluster", cluster_id))
            cluster_object = registry.get_object(
                owner_kind="conduit_cluster",
                owner_id=cluster_id,
            )
            if cluster_object is None:
                continue
            conduit_ids.update(cluster_object.get_members())

    def _collect_borrower_participants(
            self,
            *,
            registry: "DevopsInformationRegistry",
            borrowers: Iterable[Dict[str, object]],
            conduit_ids: Set[str],
            cluster_ids: Set[str],
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> None:
        """
        Fold borrower participants discovered during preflight into the footprint.

        Args:
            registry: Frame-local topology registry for spellbook ownership.
            borrowers: Borrower descriptors from the read-only transfer preflight.
            conduit_ids: Participant conduit-id set being accumulated.
            cluster_ids: Cluster-id set being accumulated.
            affected_identity_keys: Affected identity-key set being accumulated.
        """
        for borrower in borrowers:
            borrower_type = borrower.get("type")
            if borrower_type == "contract":
                borrower_conduit_id = borrower.get("borrower_conduit_id")
                if not isinstance(borrower_conduit_id, str) or not borrower_conduit_id:
                    continue
                conduit_ids.add(borrower_conduit_id)
                affected_identity_keys.add(("conduit", borrower_conduit_id))
                affected_identity_keys.add(("conduit_ward", borrower_conduit_id))
                borrower_spellbook_id = registry.get_spellbook_for_conduit(
                    borrower_conduit_id
                )
                if borrower_spellbook_id:
                    affected_identity_keys.add(("spellbook", borrower_spellbook_id))
            elif borrower_type == "cluster":
                cluster_id = borrower.get("cluster_id")
                if isinstance(cluster_id, str) and cluster_id:
                    cluster_ids.add(cluster_id)
                    affected_identity_keys.add(("conduit_cluster", cluster_id))
                member_conduit_ids = borrower.get("member_conduit_ids")
                if not isinstance(member_conduit_ids, tuple):
                    continue
                for member_id in member_conduit_ids:
                    if not isinstance(member_id, str) or not member_id:
                        continue
                    conduit_ids.add(member_id)
                    affected_identity_keys.add(("conduit", member_id))
                    affected_identity_keys.add(("conduit_ward", member_id))
                    member_spellbook_id = registry.get_spellbook_for_conduit(member_id)
                    if member_spellbook_id:
                        affected_identity_keys.add(("spellbook", member_spellbook_id))

    def _normalize_borrower_metadata(
            self,
            borrowers: Iterable[Dict[str, object]],
    ) -> Set[str]:
        """
        Build a lightweight, stable borrower summary for request metadata.

        Purpose:
            Keep request metadata descriptive without embedding the full mutable
            preflight payload.

        Args:
            borrowers: Borrower descriptors from the read-only transfer preflight.

        Returns:
            Set[str]: Stable string summaries of borrower participants.
        """
        normalized: Set[str] = set()
        for borrower in borrowers:
            borrower_type = borrower.get("type")
            if borrower_type == "contract":
                borrower_conduit_id = borrower.get("borrower_conduit_id")
                if isinstance(borrower_conduit_id, str) and borrower_conduit_id:
                    normalized.add(f"contract:{borrower_conduit_id}")
            elif borrower_type == "cluster":
                cluster_id = borrower.get("cluster_id")
                if isinstance(cluster_id, str) and cluster_id:
                    normalized.add(f"cluster:{cluster_id}")
        return normalized
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

        Returns:
            None.
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

        Returns:
            None.
        """
        self.check_cleaned()
        self._creation_gate.close()

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_id: str | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Public API

        Direct spell activation facade for this Conduit.

        At the Conduit boundary, `meld` supports multiple root entry modes.
        Callers may resolve by:

        - `spell` as a **string** (treated as a human SpellName), or
        - `spell` as a **spell object** (class/function/Protocol), or
        - `spell_id` as the canonical machine identity, or
        - `spellframe` as a **frame/protocol** (or string frame key), or
        - an explicit spellframe/binding address.

        Call shape:
            `spell` is the human-facing positional parameter. A string such as
            `"MyService"` resolves by logical SpellName. Machine callers use
            keyword-only `spell_id=...`, which is forwarded positionally into
            the internal door's existing ID fast lane.

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

        Contract:
            - HUMAN AND MACHINE IDENTITIES ARE DISTINCT: positional strings are
              logical SpellNames; opaque SHA identities use `spell_id=`. Concrete
              spell objects and spellframe/binding addresses remain supported.
            - `spell_id=` is forwarded directly into the internal positional ID
              fast lane and never enters human-name normalization.
            - GATING IS MODE-DEPENDENT: in dynamic mode entry runs through the
              creation gate and is ticketed; in automatic mode the gate is BYPASSED
              entirely for a minimal hot path. The same call therefore has different
              concurrency behaviour per frame posture.
            - A DISABLED GATE BLOCKS rather than failing: the call waits until the
              gate is re-enabled and then re-checks closure. A TERMINALLY CLOSED gate
              raises immediately. Distinguish the two - one is back-pressure, the
              other is refusal.
            - Resolution, reuse and lifetime are delegated to the Meld runtime and
              governed by the spell's `Existence`, not by this call.

        Args:
            spell:
                Human-facing target. Strings are logical SpellNames; classes,
                functions, and Protocols participate in key normalization.
            spell_id:
                Optional canonical SHA256 machine identity. Mutually exclusive
                with `spell` and delegated directly to the internal ID lane.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution. If provided, it becomes the primary frame key.
            binding_name:
                Optional binding name (string) associated with the
                spell. Used as the binding key during resolution.
            override:
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
                - If none of `spell`, `spell_id`, or `spellframe` are provided.
                - If both `spell` and `spell_id` are provided.
            TypeError:
                - If `spell_id` is not a string when provided.
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
        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")

        internal_spell = spell
        internal_spell_name = None
        if spell_id is not None:
            internal_spell = spell_id
        elif isinstance(spell, str):
            internal_spell = None
            internal_spell_name = spell

        if self.__dynamic_environment__:
            creation_gate = self._creation_gate

            # Ticket-first admission (drain-race fix 2026-07-12): the gate
            # verb acquires a VISIBLE ticket before validating state, so a
            # concurrent freeze-and-drain can never observe zero tickets
            # while this meld is between its check and its registration.
            # Raises the closed refusal itself; parks through temporary
            # freezes. On return this thread HOLDS the ticket.
            creation_gate.admit_ticket()
            try:
                # The internal door keeps its optimized positional ID spine;
                # the public facade has already separated human and machine inputs.
                return meld_component.meld(
                    internal_spell,
                    spell_name=internal_spell_name,
                    spellframe=spellframe,
                    binding_name=binding_name,
                    spell_override=override,
                )
            finally:
                creation_gate.unregister_ticket()

        # The internal door keeps its optimized positional ID spine; the public
        # facade has already separated human and machine inputs.
        return meld_component.meld(
            internal_spell,
            spell_name=internal_spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=override,
        )

    # Machine identity remains explicit at the public boundary via `spell_id=`;
    # this facade forwards it positionally into the internal ID fast lane.

    def purge(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_id: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            purge_all: bool = True,
    ) -> int:
        """
        Purge a registered target's retained creations through this conduit.

        Purpose:
            Expose targeted disposal without ending the conduit or removing the
            binding. Identity normalization mirrors this facade's meld method.

        Contract:
            - Delegates discovery and authority to the owned ConduitMeld door.
            - Many and per-conduit creations are local. Unique requires the
              binding owner, lineage the lineage root, and cluster its leader.
            - Never redirects into an active SpellSpace; use that space's purge.
            - Preserves the binding, compiled context, conduit and pools.

        Args:
            spell:
                Logical name, class/function reference or application instance.
                An instance is inspected for its class before ordinary lookup.
                The original reference is retained for single-object removal.
            spell_id:
                Explicit machine identity. Mutually exclusive with spell and
                forwarded directly into the internal id lookup lane.
            spellframe:
                Optional frame/type used by ordinary binding discovery.
            binding_name:
                Optional named binding within the selected frame.
            purge_all:
                True removes all retained target entries. False requires an
                instance as spell and removes only that object from the store.

        Returns:
            int:
                Removed creation count; zero when no matching entry is retained
                in the authorized store. Untracked many results cannot be purged.

        Raises:
            ValueError:
                If selectors conflict, no target is supplied, or single-object
                removal is requested without an instance.
            KeyError:
                If normal meld discovery cannot find the binding.
            RuntimeError:
                If cleaned, the cluster is inert, or this conduit lacks authority.
            TypeError:
                If purge_all is not a bool.
            ExceptionGroup:
                Disposal failures after selected entries have been removed.

        Threading / Concurrency:
            Creations coordinates removal with the existing creation writer
            locks and runs disposal after releasing them. This call does not
            drain in-flight resolution or perform an ownership transaction.

        Lifecycle / Cleanup:
            Existing application references remain valid Python references;
            they are not rewritten or revoked. Supplied objects also remain on
            their registration. Scope ownership must remain live for this call.
        """
        self.check_cleaned()
        if spell is not None and spell_id is not None:
            raise ValueError("purge accepts either `spell` or `spell_id`, not both.")
        internal_spell = spell
        internal_spell_name = None
        if spell_id is not None:
            internal_spell = spell_id
        elif isinstance(spell, str):
            internal_spell = None
            internal_spell_name = spell
        return self._meld.purge(
            internal_spell,
            spell_name=internal_spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            purge_all=purge_all,
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

        Contract:
            - The pre-resolved counterpart to `meld`: it skips input normalization
              because the spell is already identified, and is the path used when a
              caller already holds the object.
            - Shares `meld`'s gate behaviour exactly - ticketed through the creation
              gate in dynamic mode, bypassed in automatic mode - so the same
              blocking-versus-raising distinction applies.

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

            # Ticket-first admission (drain-race fix 2026-07-12): visible
            # ticket before state validation - see CreationGate.admit_ticket.
            creation_gate.admit_ticket()
            try:
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

        Admission:
            The link is admitted through the frame-owned change-control
            transaction mediator as a self-admitted `link` transaction (the
            same shape `sever_link` uses for `unlink`): the transaction is
            started before the ward mutation, the ward mutation runs inside
            the transaction window under the conduit lock, and the
            transaction ends with `success=False` when the mutation raises.

        On success, the following hook will be fired on this Conduit (if configured):

            - "on_conduit_post_link(self, target_conduit)"

        Contract:
            - NORMAL CONDUITS ONLY and DYNAMIC MODE ONLY; both are refused before any
              transaction is opened.
            - THE CHEAP GUARDS RUN BEFORE ADMISSION - self-link, lesser target, and
              cross-frame target are all rejected before the transaction starts, so
              an invalid link never consumes a transaction window.
            - Self-admitted `link` transaction, the same shape `sever_link` uses for
              `unlink`: started before the ward mutation, the mutation runs inside the
              window under the conduit lock, and the transaction ends with
              `success=False` if the mutation raises.
            - Fires `on_conduit_post_link` only on success.

        Args:
            target_conduit (Conduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If change-control admission is denied by the mediator.
            TypeError: If `target_conduit` is not an `Conduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
            RuntimeError: If linking this conduit to itself (guarded before
                transaction admission; the link strategy requires two
                distinct participants).
            RuntimeError: If the target is a lesser conduit (guarded before
                transaction admission; lineage attachment is not a peer link).
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
        # Identity guardrails fire BEFORE transaction admission: the link
        # strategy requires two DISTINCT participant conduits, so a
        # self-link can never be admitted and would otherwise surface as an
        # admission-plane error instead of this guardrail; a lesser target
        # would open a pointless transaction window just to be refused by
        # the ward. The ward re-checks both at the mutation site.
        if target_conduit._id == self._id:
            self._logger.error("link: self-link attempt", "link")
            raise RuntimeError("Cannot link a conduit to itself.")
        if target_conduit._conduit_state is ConduitState.lesser:
            self._logger.error("link: target is lesser conduit", "link")
            raise RuntimeError(
                "Cannot link to a lesser conduit. Use _link_lesser_conduit instead."
            )

        with self.transaction(ChangeTransactionType.LINK, conduits=[self, target_conduit]):
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
            # Record: the initiator's outbound topology changed; re-emit
            # its twin so link_targets carries the new edge, and record the
            # freshly created (or re-found) contract relationship itself.
            self._emit_conduit_twin()
            if self._crystallizer.activated:
                self._emit_contract_record_for(target_conduit)

        return linked

    def notch_spell(
            self,
            *,
            spell_index: Any,
            spell: Any,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.selected_different_spell,
    ) -> Any:
        """
        Public API

        Conduit facade for a SpellIndex notch: make `spell` the active
        (resolvable) spell in its index. Delegates to the owning Spellbook,
        which admits the `notch` change-control transaction.

        Contract:
            - DYNAMIC MODE ONLY; refused on an automatic frame.
            - REPOINTS THE ACTIVE MEMBER of an existing index - it does not create,
              bind or remove anything. The previous member stays in the lineage and
              remains resolvable by id.
            - The default `change_reason` is `selected_different_spell`, which records
              an ordinary selection rather than a mutation. Pass a mutation reason
              explicitly when that is what happened, because this default will
              otherwise misattribute the change in the state history.
            - Admitted as a `notch` change-control transaction by the owning
              spellbook, so it participates in change control rather than bypassing it.

        Args:
            spell_index: The SpellIndex whose active spell is switched.
            spell: The already-identified spell to make active.
            change_reason: Why the active member was repointed; defaults to
                `selected_different_spell` (general selection, not a mutation).

        Returns:
            Any: The owning Spellbook notch result.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error(
                "notch_spell called in non-dynamic env",
                "notch_spell",
            )
            raise RuntimeError(
                "Dynamic environment is not enabled. SpellIndex notch requires dynamic mode."
            )
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for notch_spell.")
        mediator = self._get_required_transaction_mediator()
        metadata: Dict[str, Any] = {
            "origin_surface": "conduit.notch_spell",
            "spellbook_id": self._spellbook._id,
            "owner_conduit_id": self._id,
            "spell_index_id": spell_index._id,
            "spell_id": spell.spell_id,
            "binding_key": spell._key,
            # Runtime-freeze facade (patch notch_conduit_gate_freeze_2026_07_12,
            # unelect precedent): the notch strategy's on_start quiesces the
            # sealed conduits' CreationGates through this DevOps facade so no
            # in-flight meld/validator can straddle the active-member repoint;
            # on_end reopens on every exit path via root finalize.
            "conduit_lineage_gate_ops": (
                self._aetheric_frame.dev_ops_manager.conduit_lineage_gate_ops
            ),
        }
        # The index's current active member is the outgoing spell. The conduit
        # admits the notch (it owns the change-control envelope); the owning
        # spellbook performs the local switch inside the held window; then this
        # conduit -- the only thing that knows about links -- walks its peers so
        # each borrower's spellbook parks its now-stale borrowed copy.
        outgoing_id = spell_index.selected_spell_id
        mediator.start_transaction(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.NOTCH,
            metadata=metadata,
        )
        try:
            result = self._spellbook._notch_spell(spell_index=spell_index, spell=spell, change_reason=change_reason)
        except Exception:
            mediator.end_transaction(expected_type="notch", success=False)
            raise
        mediator.end_transaction(expected_type="notch", success=True)
        if outgoing_id is not None and outgoing_id != spell.spell_id:
            self._deactivate_borrowed_spell(outgoing_id)
            # Index-link receivers follow the lineage: move their subscription head
            # to the new active member (park old, activate new) via the ward.
            self._conduit_ward._emit_index_notch(spell_index, outgoing_id, spell.spell_id)
        return result

    def add_to_spell_index(self, *, spell: Any, target_index: Any) -> Any:
        """
        Public API

        Conduit facade for moving an owned spell onto another SpellIndex.
        Delegates to the owning Spellbook, which admits the `add_to_index`
        change-control transaction.

        Contract:
            - DYNAMIC MODE ONLY; refused on an automatic frame with a logged
              `RuntimeError`.
            - Adds a version to the lineage WITHOUT making it active - selection is a
              separate `notch_spell` step, so adding is safe to do ahead of a switch.

        Args:
            spell: The owned, inactive spell to move.
            target_index: The index to move it onto.

        Returns:
            Any: The owning Spellbook's result.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error(
                "add_to_spell_index called in non-dynamic env",
                "add_to_spell_index",
            )
            raise RuntimeError(
                "Dynamic environment is not enabled. add_to_spell_index requires dynamic mode."
            )
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for add_to_spell_index.")
        mediator = self._get_required_transaction_mediator()
        metadata: Dict[str, Any] = {
            "origin_surface": "conduit.add_to_spell_index",
            "spellbook_id": self._spellbook._id,
            "source_spellbook_id": self._spellbook._id,
            "target_spellbook_id": self._spellbook._id,
            "owner_conduit_id": self._id,
            "source_conduit_id": self._id,
            "target_conduit_id": self._id,
            "spell_id": spell.spell_id,
            "spell_index_id": target_index._id,
            "binding_key": spell._key,
        }
        # Capture the source lineage BEFORE the move: the seam repoints
        # spell.spell_index to the target and destroys the source if it empties.
        source_index = spell.spell_index
        source_id = source_index.id
        moved_spell_id = spell.spell_id
        source_will_empty = source_index.is_sole_member(moved_spell_id)
        source_members = source_index.spells_in_index() if source_will_empty else set()
        mediator.start_transaction(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.ADD_TO_INDEX,
            metadata=metadata,
        )
        try:
            result = self._spellbook._add_to_spell_index(spell=spell, target_index=target_index)
        except Exception:
            mediator.end_transaction(expected_type="add_to_index", success=False)
            raise
        mediator.end_transaction(expected_type="add_to_index", success=True)
        # Eager index-link maintenance on BOTH sides. Target gains the member -> issue
        # its per-member contract on every target index-link. Source loses it -> drop
        # its per-member contract, or destroy the source's whole index-link if the move
        # emptied it.
        self._conduit_ward._emit_index_member_added(target_index, moved_spell_id)
        if source_id != target_index.id:
            if source_will_empty:
                self._conduit_ward._emit_index_destroy(source_id, source_members)
            else:
                self._conduit_ward._emit_index_member_removed(source_id, moved_spell_id)
        return result

    def remove_from_spell_index(self, *, spell: Any, source_index: Any) -> Any:
        """
        Public API

        Conduit facade for separating an owned spell out of its index into a fresh
        one. Delegates to the owning Spellbook, which admits the
        `remove_from_index` change-control transaction.

        Contract:
            - DYNAMIC MODE ONLY; refused on an automatic frame with a logged
              `RuntimeError`.
            - Removes a version from the lineage. Removal does NOT re-point the
              selection, so retiring the currently active member leaves the index
              selecting an id that is no longer a member - notch a new active member
              first.

        Args:
            spell: The owned, inactive spell to separate.
            source_index: The index the spell currently belongs to.

        Returns:
            Any: The owning Spellbook's result.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error(
                "remove_from_spell_index called in non-dynamic env",
                "remove_from_spell_index",
            )
            raise RuntimeError(
                "Dynamic environment is not enabled. remove_from_spell_index requires dynamic mode."
            )
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for remove_from_spell_index.")
        mediator = self._get_required_transaction_mediator()
        metadata: Dict[str, Any] = {
            "origin_surface": "conduit.remove_from_spell_index",
            "spellbook_id": self._spellbook._id,
            "source_spellbook_id": self._spellbook._id,
            "owner_conduit_id": self._id,
            "source_conduit_id": self._id,
            "spell_id": spell.spell_id,
            "spell_index_id": source_index._id,
            "binding_key": spell._key,
        }
        mediator.start_transaction(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.REMOVE_FROM_INDEX,
            metadata=metadata,
        )
        try:
            result = self._spellbook._remove_from_spell_index(spell=spell, source_index=source_index)
        except Exception:
            mediator.end_transaction(expected_type="remove_from_index", success=False)
            raise
        mediator.end_transaction(expected_type="remove_from_index", success=True)
        # Index-link receivers drop the removed member's per-member spell contract.
        self._conduit_ward._emit_index_member_removed(source_index.id, spell.spell_id)
        return result

    def cleanup_spell(self, *, spell: Any) -> None:
        """
        Public API

        Conduit facade for fully disposing an owned spell. Delegates to the
        owning Spellbook, which removes the spell from every resolution surface,
        drops its Creations, destroys its index if it was the sole member, and
        tears the spell object down.

        Args:
            spell: The owned spell to dispose.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for cleanup_spell.")
        # Capture the lineage id and whether disposal will destroy the index (the
        # spell is the sole member) BEFORE the spell is torn down.
        index = spell.spell_index
        index_id = index.id
        will_destroy = index.is_sole_member(spell.spell_id)
        # Capture the members BEFORE teardown: cleanup_spell destroys the index when the
        # spell is its sole member, so they cannot be read off the (cleaned) index after.
        destroyed_member_ids = index.spells_in_index() if will_destroy else set()
        self._spellbook.cleanup_spell(spell=spell)
        # A destroyed index-linked lineage must be dropped on its receivers so they
        # do not keep a subscription to a dead index.
        if will_destroy:
            self._conduit_ward._emit_index_destroy(index_id, destroyed_member_ids)

    def _deactivate_borrowed_spell(self, spell_id: str) -> None:
        """
        Internal

        Owner-side borrower fan-out: walk this conduit's active links and park every
        peer's contracted copy of `spell_id`. When this conduit notches an index, the
        outgoing spell's borrowed copies must go inactive in each linked peer.

        Link knowledge lives here, not in the spellbook: this conduit finds the peers
        through its ward (`_get_links()`) and tells each peer's spellbook to manage its
        own contracted maps via `_inactivate_contract_spell`. The per-peer call is
        idempotent (the spellbook no-ops when it is not holding the spell), so a peer
        that never borrowed `spell_id` is simply skipped.

        Args:
            spell_id (str): Version id of the spell whose borrowed copies to park.

        Returns:
            None.
        """
        self.check_cleaned()
        ward = self._conduit_ward
        if ward is None:
            return
        owner_id = self._id
        for peer in ward._get_links():
            peer_spellbook = peer._spellbook
            if peer_spellbook is None:
                continue
            peer_spellbook._inactivate_contract_spell(owner_id, spell_id)

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

        with self.transaction(ChangeTransactionType.UNLINK, conduits=[self, target_conduit]):
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

        Returns:
            None.
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
            - Requires an active change transaction of a link-pattern type
              (`link`, `cluster_link`, `cluster_join`, or `cluster_leave`), since
              cluster membership entry/exit shares/unshares contracts under a
              single transaction that seals every involved conduit.
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
        if request.request_type not in (
                "link",
                "cluster_link",
                "cluster_join",
                "cluster_leave",
        ):
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
        mediator = self._get_required_transaction_mediator()
        reuse_active_transaction = mediator.get_active_request() is not None
        if reuse_active_transaction:
            # Inside an existing link/cluster/transfer window: validate it seals the
            # contract surface (both conduits), then run the add inside that window.
            self._require_link_transaction_for_contract(
                conduit=conduit,
                conduit_id=conduit_id,
                allow_all_links=False,
            )
        else:
            # Standalone: self-admit a dedicated add_spell_to_contract transaction
            # that seals the borrower + provider conduits (and their wards).
            peer_conduit = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame,
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.ADD_SPELL_OR_INDEX_TO_CONTRACT,
                metadata={
                    "origin_surface": "conduit.add_spell_to_contract",
                    "spellbook_id": self._spellbook._id if self._spellbook is not None else None,
                    "owner_conduit_id": self._id,
                    "peer_conduit_id": peer_conduit._id if peer_conduit is not None else conduit_id,
                    "spell_id": spell.spell_id if spell is not None else spell_id,
                    "binding_key": spell._key if spell is not None else None,
                },
            )

        try:
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

            if self._crystallizer.activated:
                record_peer = self._resolve_peer_conduit_for_contract_hooks(
                    conduit, conduit_id, aetheric_frame
                )
                if record_peer is not None:
                    self._emit_contract_record_for(record_peer)

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
        except Exception:
            if not reuse_active_transaction:
                mediator.end_transaction(expected_type="add_spell_or_index_to_contract", success=False)
            raise
        if not reuse_active_transaction:
            mediator.end_transaction(expected_type="add_spell_or_index_to_contract", success=True)

        return result



    def add_index_to_contract(
            self,
            *,
            index: Any,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: DetailReason = DetailReason.manual,
    ) -> bool:
        """
        Public API

        Link a whole SpellIndex into a contract with a target conduit, so the
        borrower follows the index's active (selected) member rather than a
        captured version, admitted as an `add_spell_or_index_to_contract`
        change-control transaction. The index counterpart of
        `add_spell_to_contract`.

        Contract:
            - Reuses an active link/cluster/transfer window when one is already
              open (so the cluster and transfer flows are unaffected); otherwise
              self-admits a dedicated add_spell_or_index_to_contract transaction
              that seals the borrower + provider conduits (and their wards)
              EXCLUSIVE for the duration.
            - The index link itself runs inside the held window via the
              Conduit-owned `_conduit_ward._add_index_to_contract` seam.

        Args:
            index: The owned SpellIndex to share.
            conduit / conduit_id: The target (owner/provider) conduit.
            permissions: Permission to grant (default "create").
            aetheric_frame: Frame override used to locate the target conduit.
            reason: Why this index contract exists.

        Returns:
            bool: True if the index link was created.

        Raises:
            RuntimeError: If contract qualification fails (cleaned / not normal /
                not dynamic), or -- when reusing an existing window -- no active
                link transaction is present.
        Threading:
            The transaction embargo is acquired before the ward lock, so a
            concurrent bind/link cannot deadlock the add.
        """
        self._qualify_contracts()
        mediator = self._get_required_transaction_mediator()
        reuse_active_transaction = mediator.get_active_request() is not None
        if reuse_active_transaction:
            self._require_link_transaction_for_contract(
                conduit=conduit,
                conduit_id=conduit_id,
                allow_all_links=False,
            )
        else:
            peer_conduit = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame,
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.ADD_SPELL_OR_INDEX_TO_CONTRACT,
                metadata={
                    "origin_surface": "conduit.add_index_to_contract",
                    "spellbook_id": self._spellbook._id if self._spellbook is not None else None,
                    "owner_conduit_id": self._id,
                    "peer_conduit_id": peer_conduit._id if peer_conduit is not None else conduit_id,
                    "index_id": index.id,
                },
            )

        try:
            result = self._conduit_ward._add_index_to_contract(
                index=index,
                conduit=conduit,
                conduit_id=conduit_id,
                permissions=permissions,
                aetheric_frame=aetheric_frame,
                reason=reason,
            )

            if self._crystallizer.activated:
                record_peer = self._resolve_peer_conduit_for_contract_hooks(
                    conduit, conduit_id, aetheric_frame
                )
                if record_peer is not None:
                    self._emit_contract_record_for(record_peer)
        except Exception:
            if not reuse_active_transaction:
                mediator.end_transaction(expected_type="add_spell_or_index_to_contract", success=False)
            raise
        if not reuse_active_transaction:
            mediator.end_transaction(expected_type="add_spell_or_index_to_contract", success=True)

        return result

    def remove_index_from_contract(
            self,
            *,
            index_id: str,
            conduit: Optional["Conduit"] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> None:
        """
        Public API

        Release a whole SpellIndex-link from the contract with a target conduit and
        untrack the index on the borrower, admitted as a
        `remove_spell_or_index_from_contract` change-control transaction. The
        reverse of `add_index_to_contract`.

        Contract:
            - Reuses an active link/cluster/transfer window when one is already
              open (so the cluster and transfer flows are unaffected); otherwise
              self-admits a dedicated remove_spell_or_index_from_contract
              transaction that seals the borrower + provider conduits (and their
              wards) EXCLUSIVE for the duration.
            - The untrack itself runs inside the held window via the Conduit-owned
              `_conduit_ward._remove_index_from_contract` seam.

        Args:
            index_id: Stable id of the linked index to release.
            conduit / conduit_id: The target (owner/provider) conduit.
            aetheric_frame: Frame override used to locate the target conduit.

        Raises:
            RuntimeError: If contract qualification fails (cleaned / not normal /
                not dynamic), or -- when reusing an existing window -- no active
                link transaction is present.
        Threading:
            The transaction embargo is acquired before the ward lock, matching the
            add-side ordering, so a concurrent bind/link cannot deadlock the
            removal.

        Returns:
            None.
        """
        self._qualify_contracts()
        mediator = self._get_required_transaction_mediator()
        reuse_active_transaction = mediator.get_active_request() is not None
        if reuse_active_transaction:
            self._require_link_transaction_for_contract(
                conduit=conduit,
                conduit_id=conduit_id,
                allow_all_links=False,
            )
        else:
            peer_conduit = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame,
            )
            mediator.start_transaction(
                identity=self._transaction_identity,
                transaction_type=ChangeTransactionType.REMOVE_SPELL_OR_INDEX_FROM_CONTRACT,
                metadata={
                    "origin_surface": "conduit.remove_index_from_contract",
                    "spellbook_id": self._spellbook._id if self._spellbook is not None else None,
                    "owner_conduit_id": self._id,
                    "peer_conduit_id": peer_conduit._id if peer_conduit is not None else conduit_id,
                    "index_id": index_id,
                },
            )

        try:
            self._conduit_ward._remove_index_from_contract(
                index_id=index_id,
                conduit=conduit,
                conduit_id=conduit_id,
                aetheric_frame=aetheric_frame,
            )

            if self._crystallizer.activated:
                record_peer = self._resolve_peer_conduit_for_contract_hooks(
                    conduit, conduit_id, aetheric_frame
                )
                if record_peer is not None:
                    self._emit_contract_record_for(record_peer)
        except Exception:
            if not reuse_active_transaction:
                mediator.end_transaction(expected_type="remove_spell_or_index_from_contract", success=False)
            raise
        if not reuse_active_transaction:
            mediator.end_transaction(expected_type="remove_spell_or_index_from_contract", success=True)

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

        if self._crystallizer.activated:
            record_peer = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame
            )
            if record_peer is not None:
                self._emit_contract_record_for(record_peer)

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

        if self._crystallizer.activated:
            record_peer = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame
            )
            if record_peer is not None:
                self._emit_contract_record_for(record_peer)

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

        if self._crystallizer.activated:
            record_peer = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame
            )
            if record_peer is not None:
                self._emit_contract_record_for(record_peer)

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

        Contract:
            - REQUIRES AN ACTIVE LINK TRANSACTION; it is not a bare mutation. The
              transaction requirement is checked before anything is removed.
            - Qualifies contracts first, so the removal operates on a settled view
              rather than a stale one.
            - Removes the ROOT spell from contracts and returns a report of what was
              actually removed - read it rather than assuming a full sweep.

        Threading:
            Serialized by the surrounding link transaction.

        Lifecycle / Cleanup:
            Guarded via the contract-qualification path.

        Raises:
            RuntimeError: If no suitable link transaction is active.

        Returns:
            dict: Per-peer removal outcome keyed by contract, describing what was
                untracked on each side.

        Args:
            root_spell_id:
                Lineage root whose contracted details should be untracked across
                every peer contract this conduit participates in.
        """
        self._qualify_contracts()
        self._require_link_transaction_for_contract(
            conduit=conduit,
            conduit_id=conduit_id,
            allow_all_links=True,
        )
        removal_report = self._conduit_ward._remove_root_from_contracts(
            root_spell_id=root_spell_id,
            conduit=conduit,
            conduit_id=conduit_id,
            aetheric_frame=aetheric_frame,
        )
        if self._crystallizer.activated:
            record_peer = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame
            )
            if record_peer is not None:
                self._emit_contract_record_for(record_peer)
        return removal_report

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

        Contract:
            - CONVENIENCE WRAPPER over `add_spell_to_contract(...)` that stamps
              `DetailReason.root`, marking the spell as a deliberately contracted
              ROOT rather than something pulled in as a dependency.
            - It adds no logic of its own; every gate, transaction requirement and
              raise belongs to the wrapped call.
            - The reason stamp is what later lets contract reports tell roots apart
              from dependency-driven entries.

        Threading:
            Inherited from `add_spell_to_contract(...)`.

        Lifecycle / Cleanup:
            Inherited from `add_spell_to_contract(...)`.

        Raises:
            RuntimeError: Propagated from `add_spell_to_contract(...)`.

        Returns:
            Optional[bool]: True when the spell and its dependency closure were added,
                False when refused, None when there was no contract to act on.

        Args:
            spell:
                The spell or lineage to grant across the existing contract.
            peer_conduit:
                The borrowing peer that should gain access.
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

        if self._crystallizer.activated:
            record_peer = self._resolve_peer_conduit_for_contract_hooks(
                conduit, conduit_id, aetheric_frame
            )
            if record_peer is not None:
                self._emit_contract_record_for(record_peer)

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
        including the peer conduit's name, the number of active spells involved, and permission levels.
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
        :meth:`_ensure_local_conduit_hooks`, assembled per hook name by
        :meth:`_collect_conduit_hook_chain`. The contract is intentionally
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
