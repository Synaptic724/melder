from typing import Optional, List, Any, Callable, Sequence, Protocol, Set, Tuple
import ulid
from threading import RLock
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces import (
    ISpell,
    ISpellDetailedProfile,
    ISpellGeneralProfile,
    ISpellbook,
    ISpellSystemStates,
)
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex
from melder.aether.dev_ops.spell_system_states.spell_system_state import (
    SpellSystemState,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class ISpellCrafterSurface(Protocol):
    """
    Narrow spell-owned compiler and validation surface consumed by `Spell`.

    Purpose:
        Break the local `spell.py` <-> `spell_crafter.py` type cycle while
        still documenting the exact crafter behavior `Spell` relies on.

    Contract:
        - Exposes read-only phase artifacts and validation status.
        - Exposes the phase-runner methods `Spell` delegates into.
        - Supports deterministic cleanup and phase-artifact cleanup.
    """

    requirements: Optional[SpellRequirements]
    symbolic_graph: Optional[SpellSymbolicGraph]
    resolution_frame: Any
    validation_result_phase4: Any
    validation_result_phase6: Any
    validated: bool
    is_broken: bool

    def cleanup(self) -> None:
        """
        Clean up the owned crafter state.
        """
        ...

    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_root_blueprints(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_root_blueprints_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_occurrence_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_injection_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_patch_maps(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_execution_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_system_validation_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def run_phase_change_control_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        ...

    def get_phase5_spell_ids(self) -> Set[str]:
        """
        Return the spell ids currently covered by local Phase 5 artifacts.
        """
        ...

    def get_phase5_root_ids(self) -> Tuple[str, ...]:
        """
        Return the root ids currently covered by local Phase 5 artifacts.
        """
        ...

    def cleanup_phase_artifacts(self) -> None:
        """
        Drop owned phase artifacts while keeping the crafter itself alive.
        """
        ...


#region Spell
class Spell(Cleanable, ISpell):
    """
    Internal

    Represents one registered spell inside the Melder runtime.

    A `Spell` is the canonical bind-time runtime record for one class,
    function, lambda, or existing object registration. It keeps the spell's
    structural identity, lifecycle policy, access policy, reflective profile,
    build-time artifacts, spell-local runtime helpers, and ownership metadata
    together so the rest of Melder can reason about one stable object instead
    of a loose bundle of values.

    Contract:
    - Wraps exactly one registered spell target plus its `SpellIndex`
      lineage/version record.
    - Owns spell-local mutable runtime state such as hooks, dependency/build
      artifacts, the spell-owned `CreationContextFactory`, the spell-owned
      `CreationContext`, execution-plan metrics, and mutation overlays.
    - Does not validate bind-time inputs by itself; upstream bind/examiner
      stages are expected to hand it already-validated configuration.
    - Uses an internal `RLock` to guard multi-field configuration and cleanup
      transitions.
    - Becomes unusable after `cleanup()` completes; later live-object methods
      are expected to fail through `check_cleaned()`.

    Core Responsibilities:
    - Holds an immutable reference to the object (function/class/instance) it represents.
    - Tracks configuration data: type, binding profile (if attached), spellframe,
      ownership, and hooks.
    - Defines dependency DAGs for invocation and construction (via external DAG /
      resolution pipelines).
    - Manages permission control via the `Permissions` enum.
    - Enables hook-based lifecycle support (pre, activation, post).
    - Acts as a source of truth for spell identity and access.
    - Stores conjure-time disposal metadata (matched method names + boolean flag).
    - Tracks whether runtime resolution is still required before first context build.
    - Caches Phase 11 execution-plan metrics (node count, max depth, etc.) for
      runtime path selection.

    Permissions (`Permissions` enum):
        - `read`: Allows other conduits to use the spell as-is, but not modify
          or recreate it.
        - `create`: Allows other conduits to instantiate or construct new
          versions.
        - `block`: Prevents external access. Internal owner-conduit access is
          still allowed.

    Key Concepts:
        - Each spell has a unique SHA256 `spell_id`, generated from its structural fingerprint.
        - `spellframe` distinguishes the context it was declared in (e.g., Protocol, class,
          or string frame).
        - Spells may be cleaned (`cleanup()`), after which modification is disallowed.
        - Dependency graphs and resolution profiles are produced by the Resolution / Meld
          pipeline, not by this class directly.
        - Permissions are enforced during conduit contract evaluation.

    Parameters:
        spell (Any):
            The actual object to register (function, class, lambda, or existing instance).

        spell_index (SpellIndex):
            Versioned identity for this spell (current + historical fingerprints).

        spellframe (Optional[Any]):
            Frame context (usually a Protocol, class, or string) to scope the spell's identity.

        binding_name (Optional[str]):
            The logical name this spell is bound to (e.g., "database", "engine").
            Normalized as part of the internal key via SpellInputUtils.
            May be None for unnamed/default bindings.

        spell_name (str):
            The actual internal name of the object or callable (for display/debugging).

        existence (Existence):
            The spell's lifecycle policy (unique, shared, etc.).

        spell_type (SpellType):
            Indicates if the spell is a class, method, lambda, or existing creation, and
            whether it participates in spellframes and/or binding names.

        spell_id (str):
            Unique identifier derived from object fingerprinting (SHA256).

        permissions (Permissions):
            Defines access control level for borrowing, invoking, or recreating this spell.

        aetheric_frame (str):
            Logical Aether frame / namespace this spell was registered under.

        profile (Optional[Any]):
            Optional reflective profile associated with this spell.

            Currently:
            - The Bind pipeline finishes by attaching a combined general or
              detailed spell profile here.
            - Those combined profiles still expose the underlying binding and
              resolution artifacts for downstream consumers.
            - Legacy usage expecting raw profile types should treat this field
              as an opaque introspection artifact and normalize it first.

        existing_object (Optional[object]):
            Optional pre-instantiated object to attach to the spell (EXISTING_CREATION* types).
            For factory-like spells (class/method/lambda), this is usually None.

        spellbook (Optional[ISpellbook]):
            Back-reference to the owning Spellbook. Primarily used for internal coordination
            (conduit ownership, graph wiring, diagnostics). May be None in some contexts.

        *args / **kwargs:
            Arbitrary tags and metadata for internal use or future extensions.

    Threading / Concurrency:
        - Internal multi-field mutation is guarded by `_lock`.
        - Spell-owned runtime context publication uses `_creation_context_switch`
          so only one builder wins publication at a time.
        - Higher-level conduit/spellbook orchestration still owns system-level
          concurrency decisions; this class only protects its own local state.

    Lifecycle / Cleanup:
        - `Spell` owns its `SpellCrafter`, spell-owned `CreationContextFactory`,
          spell-owned `CreationContext`, hook lists, dependency/build artifacts,
          and cached execution-plan metrics.
        - Conduit ownership can be restamped later, which invalidates the
          spell-owned `CreationContext` and rebuilds the spell-owned factory.
        - `cleanup()` is deterministic, best-effort for owned child cleanup, and
          clears references to prevent reuse-after-clean.

    Notes:
        - This class is never used directly by users. It is created during `bind()` and
          registered into the Spellbook and Aether.
        - Internal mutation after cleaning is disallowed.
        - Dependency graphs, resolution frames, and resolution profiles are produced
          by the Resolution / Meld layer; `Spell` itself does not execute resolution.

    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_activation_hooks",
        "_creation_context",
        "_creation_context_factory",
        "_creation_context_switch",
        "_crafter",
        "_dynamic_environment",
        "_hooks_enabled",
        "_id",
        "_is_class_spell",
        "_is_existing_creation",
        "_is_lambda_spell",
        "_is_method_spell",
        "_key",
        "_lock",
        "_mutation_override",
        "_owner_conduit_id",
        "_owner_conduit_name",
        "_owner_creations",
        "_post_hooks",
        "_pre_hooks",
        "_spell_system_states",
        "_spellbook",
        "aetheric_frame",
        "binding_name",
        "dependencies",
        "dependency_graph",
        "disposal_method_names",
        "existence",
        "has_disposal_methods",
        "metadata",
        "owned_spell",
        "permissions",
        "profile",
        "resolution_required",
        "resolution_complete",
        "execution_plan_step_count",
        "execution_plan_unique_spell_count",
        "execution_plan_max_occurrence_depth",
        "execution_plan_max_dependency_count",
        "execution_plan_has_calln",
        "execution_plan_has_contract_payloads",
        "execution_plan_has_existing_creations",
        "execution_plan_dispatch_route",
        "retries",
        "spell",
        "spell_id",
        "spell_index",
        "spell_name",
        "spell_type",
        "spellframe",
        "tags",
        "timeout",
        "user_created_object",
    ]
    def __init__(
            self,
            spell: Any,
            spell_index: SpellIndex,
            spellframe: Optional[Any],
            binding_name: Optional[str],
            spell_name: str,
            existence: Existence,
            spell_type: SpellType,
            spell_id: str,
            permissions: Permissions,
            aetheric_frame: str,
            profile: Optional[Any] = None,
            existing_object: Optional[object] = None,
            spellbook: Optional[ISpellbook] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        Internal constructor for a bound Spell record.

        Args:
            spell (Any): The underlying callable/class/instance being registered.
            spell_index (SpellIndex): Lineage/version tracker for this spell.
            spellframe (Optional[Any]): Logical frame/contract used to scope the spell.
            binding_name (Optional[str]): Optional binding key used to disambiguate spells under the same frame.
            spell_name (str): Resolved name for the spell (qualname or type name).
            existence (Existence): Lifecycle policy for instantiation/sharing semantics.
            spell_type (SpellType): Classification of the spell (class/method/lambda/existing-creation variants).
            spell_id (str): SHA256 fingerprint for this spell's structural identity.
            permissions (Permissions): Access policy for other conduits.
            aetheric_frame (str): Aether frame identifier this spell belongs to.
            profile (Optional[Any]): Binding/introspection profile attached by the examiner.
            existing_object (Optional[object]): Pre-created instance for EXISTING_CREATION* spell types.
            spellbook (Optional[ISpellbook]): Back-reference to the owning spellbook for coordination.
            *args: Optional positional metadata tags.
            **kwargs: Optional keyword metadata map attached to this spell.

        Notes:
            - Thread-safe configuration/cleanup is guarded by an internal RLock.
            - The canonical lookup key is normalized immediately via `SpellInputUtils`.
            - Validation of inputs (existence, permissions, profile shape) is expected to be enforced upstream by the Bind pipeline.
        """
        super().__init__()
        self._lock = RLock()
        self._id: str = str(ulid.ULID())  # Unique internal ID for tracking

        # Spell Data
        self.spell_index: SpellIndex = spell_index
        self.spell: Any = spell  # Object reference
        self.spell_id: str = spell_id  # SHA256 unique identifier
        self.spellframe: Optional[Any] = spellframe
        self.spell_type: SpellType = spell_type
        self._is_existing_creation: bool = spell_type in (
            SpellType.EXISTING_CREATION,
            SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
            SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        self._is_class_spell: bool = spell_type in (
            SpellType.SPELL,
            SpellType.SPELL_WITH_SPELLFRAME,
            SpellType.SPELL_WITH_BINDING_NAME,
            SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        self._is_method_spell: bool = spell_type in (
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        self._is_lambda_spell: bool = spell_type in (
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        self.user_created_object: Optional[object] = existing_object
        self.binding_name: Optional[str] = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence

        # Reflective spell profile.
        # Treated as opaque here; downstream consumers normalize general or
        # detailed profiles as needed.
        self.profile: Optional[Any] = profile

        self.aetheric_frame: str = aetheric_frame
        self.timeout: Optional[int] = None  # Optional timeout for spell execution
        self.retries: int = 0  # Number of retries allowed for spell execution

        # Permissions
        self.permissions: Permissions = permissions

        # Spellbook
        self._spellbook: Optional[ISpellbook] = spellbook

        # Spell Metadata
        self.tags = args if args else []
        self.metadata = kwargs if kwargs else {}
        self._mutation_override: dict = {}
        self.disposal_method_names: List[str] = []
        self.has_disposal_methods: bool = False

        # Hooks (private storage; Spellbook controls mutation)
        self._hooks_enabled: bool = False
        self._pre_hooks: List[Callable[..., Any]] = []
        self._activation_hooks: List[Callable[..., Any]] = []
        self._post_hooks: List[Callable[..., Any]] = []

        # Final build-time artifacts
        self.dependency_graph: Any = None
        self.dependencies: List[str] = []  # SHA256 spell IDs required for this spell to function

        # Phase 11 execution-plan metrics (populated during conjure).
        self.execution_plan_step_count: Optional[int] = None
        self.execution_plan_unique_spell_count: Optional[int] = None
        self.execution_plan_max_occurrence_depth: Optional[int] = None
        self.execution_plan_max_dependency_count: Optional[int] = None
        self.execution_plan_has_calln: Optional[bool] = None
        self.execution_plan_has_contract_payloads: Optional[bool] = None
        self.execution_plan_has_existing_creations: Optional[bool] = None
        self.execution_plan_dispatch_route: Optional[str] = None

        # Per-spell compiler / resolution helper (SpellCrafter).
        # This owns all Phase artifacts and is disposable.
        self._crafter: Optional[ISpellCrafterSurface] = None
        # Spell-owned meld execution context (created lazily by CreationContextFactory).
        self._creation_context: Optional[Any] = None
        # Spell-owned context factory configured at conduit ownership stamp time.
        self._creation_context_factory: Optional[CreationContextFactory] = None
        # Spell-owned selector latch for one-leader CreationContext publication.
        self._creation_context_switch: CounterSwitch = CounterSwitch(state=0)
        # Runtime mode carried from owning conduit for context factory wiring.
        self._dynamic_environment: bool = False
        # Runtime resolution gate flag (False for full AOT by default).
        self.resolution_required: bool = False
        # Runtime deferred-resolution completion flag.
        # Starts False and flips True only when Phase12 compile wiring completes.
        self.resolution_complete: bool = False

        # Created after Conduit made (ownership / scope integration)
        self._owner_conduit_id: Optional[str] = None
        self._owner_conduit_name: Optional[str] = None
        self.owned_spell: Optional[bool] = None
        self._owner_creations: Any = None  # Scope level creations for singletons

        # Spell System State
        self._spell_system_states: ISpellSystemStates = self._spellbook._spell_system_states

        # Key for the spell in the Spellbook (normalized)
        frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=self.spellframe,
            spell_name=self.spell_name,
            binding_name=self.binding_name,
        )
        self._key = (frame_key, bind_key)


    #region Disposal
    def cleanup(self) -> None:
        """
        Release spell-owned runtime state and permanently retire this Spell.

        Purpose:
            Deterministically tear down the spell-local runtime surface so later
            code cannot keep using stale build artifacts, runtime contexts, or
            owner references after the spell leaves service.

        Contract:
            - Idempotent: repeated calls become no-ops after `_cleaned` flips.
            - Thread-safe: acquires `_lock`, re-checks `_cleaned`, and then
              performs teardown under the guarded section.
            - Best-effort child cleanup: owned child cleanup failures are
              swallowed so teardown still reaches the final cleared state.
            - Clears hooks, metadata, dependency/build artifacts, execution-plan
              metrics, spell-owned factory/context state, conduit ownership
              state, spellbook references, and reflective profile state.
            - Sets `_cleaned` before the guarded section exits, then drops the
              `_lock` reference itself after teardown completes.

        Runtime resolution and instance lifecycle remain owned by the Resolution
        / Meld layer, not by this class.

        Returns:
            None.

        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            if self.dependency_graph is not None:
                try:
                    self.dependency_graph.cleanup()
                except Exception:
                    # Never let cleanup explosions propagate.
                    pass

            if self.profile is not None and isinstance(self.profile, Cleanable):
                try:
                    self.profile.cleanup()
                except Exception:
                    pass

            # Phase artifacts - deterministically dropped via SpellCrafter.
            if self._crafter is not None:
                try:
                    self._crafter.cleanup()
                except Exception:
                    # Never let cleanup explosions propagate.
                    pass
                self._crafter = None

            try:
                if self.spell_index is not None:
                    self.spell_index.cleanup()
            except Exception:
                pass
            # Drop references to help GC and enforce immutability after cleanup.
            self._cleanup_creation_context()
            self._cleanup_creation_context_factory()
            if self._creation_context_switch is not None:
                try:
                    self._creation_context_switch.cleanup()
                except Exception:
                    pass

            if self._pre_hooks is not None:
                self._pre_hooks.clear()
            if self._activation_hooks is not None:
                self._activation_hooks.clear()
            if self._post_hooks is not None:
                self._post_hooks.clear()
            if self.tags is not None and hasattr(self.tags, "clear"):
                try:
                    self.tags.clear()
                except Exception:
                    pass
            if isinstance(self.metadata, dict):
                self.metadata.clear()
            if isinstance(self.dependencies, list):
                self.dependencies.clear()
            if isinstance(self.disposal_method_names, list):
                self.disposal_method_names.clear()
            self._cleaned = True
            self._hooks_enabled = False

            del self._owner_creations
            del self.user_created_object
            del self._spell_system_states
            del self._spellbook
            del self._pre_hooks
            del self._activation_hooks
            del self._post_hooks
            del self.tags
            del self.metadata
            del self.dependencies
            del self.disposal_method_names
            del self.has_disposal_methods
            del self.dependency_graph
            del self.execution_plan_step_count
            del self.execution_plan_unique_spell_count
            del self.execution_plan_max_occurrence_depth
            del self.execution_plan_max_dependency_count
            del self.execution_plan_has_calln
            del self.execution_plan_has_contract_payloads
            del self.execution_plan_has_existing_creations
            del self.execution_plan_dispatch_route
            del self.profile
            del self.spell
            del self._key
            del self._is_existing_creation
            del self._is_class_spell
            del self._is_method_spell
            del self._is_lambda_spell
            del self._owner_conduit_id
            del self._owner_conduit_name
            del self.owned_spell
            del self._creation_context
            del self._creation_context_factory
            del self._creation_context_switch
            del self._dynamic_environment
            del self.resolution_required
            del self.resolution_complete
            del self.aetheric_frame
            del self.spell_index


    #endregion Disposal
    def _set_hooks(
            self,
            *,
            pre_hooks: Optional[Sequence[Callable[..., Any]]] = None,
            activation_hooks: Optional[Sequence[Callable[..., Any]]] = None,
            post_hooks: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> None:
        """
        Internal

        Attach lifecycle hook lists and update the spell hook gate.

        Contract:
            - Replaces only the hook lists provided (None means "leave as-is").
            - Updates `_hooks_enabled` based on current hook list contents.
            - Hook callability is validated by Spellbook before this is called.
            - Requires a live Spell instance.

        Args:
            pre_hooks:
                Optional list/tuple of pre-cast hooks. Each hook must accept no
                arguments and is invoked before resolution.
            activation_hooks:
                Optional list/tuple of activation hooks. Each hook receives the
                newly created instance as its first argument.
            post_hooks:
                Optional list/tuple of post-cast hooks. Each hook must accept no
                arguments and is invoked after resolution.

        Returns:
            None.

        Raises:
            RuntimeError: If the Spell has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if pre_hooks is not None:
                self._pre_hooks = list(pre_hooks)
            if activation_hooks is not None:
                self._activation_hooks = list(activation_hooks)
            if post_hooks is not None:
                self._post_hooks = list(post_hooks)
            self._hooks_enabled = bool(
                self._pre_hooks or self._activation_hooks or self._post_hooks
            )

    def _cleanup_creation_context(self) -> None:
        """
        Internal

        Dispose and clear the spell-owned CreationContext, if present.

        Contract:
            - Idempotent and safe to call repeatedly.
            - Best-effort cleanup; exceptions are
              swallowed so callers can continue ownership/dirty transitions.
            - Leaves `_creation_context` as `None`.
            - Resets `_creation_context_switch` to idle state (`0`) so
              future `get_or_build` calls can elect a new leader.
        """
        if self._creation_context is not None:
            try:
                self._creation_context.cleanup()
            except Exception:
                pass
            self._creation_context = None
        if self._creation_context_switch.state > 0:
            self._creation_context_switch.advance(
                -self._creation_context_switch.state
            )

    def _cleanup_creation_context_factory(self) -> None:
        """
        Internal

        Dispose and clear the spell-owned CreationContextFactory, if present.

        Contract:
            - Idempotent and safe to call repeatedly.
            - Best-effort cleanup; exceptions are swallowed so ownership
              transitions can continue.
            - Leaves `_creation_context_factory` as `None`.
        """
        if self._creation_context_factory is not None:
            try:
                self._creation_context_factory.cleanup()
            except Exception:
                pass
            self._creation_context_factory = None

    def _configure_creation_context_factory(
            self,
            *,
            dynamic_environment: bool,
            creation_gate_controller: CreationGateController,
    ) -> None:
        """
        Internal

        Rebuild the spell-owned CreationContextFactory for current conduit ownership.

        Purpose:
            Ensure CreationContextFactory dependencies track the latest owner
            conduit runtime mode and frame gate-governance surface.

        Contract:
            - Replaces any existing factory instance.
            - Stores dynamic mode on the spell for runtime metadata.
            - Requires a non-null CreationGateController.

        Args:
            dynamic_environment:
                True when the owning conduit runs in dynamic mode.
            creation_gate_controller:
                Frame-owned CreationGateController used by the factory for
                spell-lineage gate operations.

        Returns:
            None.

        Raises:
            ValueError:
                If `creation_gate_controller` is None.
        """
        if creation_gate_controller is None:
            raise ValueError("creation_gate_controller cannot be None.")
        self._cleanup_creation_context_factory()
        self._dynamic_environment = bool(dynamic_environment)
        self._creation_context_factory = CreationContextFactory(
            dynamic_environment=self._dynamic_environment,
            creation_gate_controller=creation_gate_controller,
        )

    def _get_or_build_creation_context(self) -> Any:
        """
        Internal

        Resolve or build the spell-owned CreationContext through its factory.

        Purpose:
            Provide one spell-local runtime entrypoint for creation-context
            retrieval so callers do not directly own factory references.

        Contract:
            - Requires the spell to have an initialized factory.
            - Delegates build/get policy to CreationContextFactory.
            - Returns a live CreationContext instance bound to this spell.

        Returns:
            Any:
                Spell-owned CreationContext instance.

        Raises:
            RuntimeError:
                If the spell has no configured CreationContextFactory.
        """
        creation_context_switch = self._creation_context_switch
        if creation_context_switch.state >= 2:
            return self._creation_context
        creation_context_factory = self._creation_context_factory
        return creation_context_factory.get_or_build_for_spell(self)


    #region Context Manager
    def __enter__(self) -> "Spell":
        """
        Acquire the spell's internal lock and return `self`.

        Purpose:
            Allow internal configuration code to group multiple field updates
            under the same lock without exposing `_lock` directly.

        Contract:
            - Intended for internal use only.
            - Does not perform a cleaned-state guard on its own; callers must
              ensure they are operating on a live spell.
            - Must be paired with `__exit__` to avoid leaking the lock.

        Returns:
            Spell:
                This spell instance while the internal lock is held.

        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Release the spell's internal lock after a context-manager block.

        Returns:
            None.

        """
        self._lock.release()
    #endregion Context Manager

    def __repr__(self) -> str:
        """
        Return a concise diagnostic representation for logging and debugging.

        Contract:
            - Includes spell name, binding key, frame label, and the SHA256
              spell identifier.
            - Falls back to `type(self.spell).__name__` when no explicit
              `spellframe` exists.

        Returns:
            str:
                Stable human-readable representation of this spell's identity.

        """
        if self.spellframe:
            frame = getattr(self.spellframe, "__name__", str(self.spellframe))
        else:
            frame = type(self.spell).__name__
        return (
            f"Spell(name={self.spell_name}, binding={self.binding_name or '__default__'}, "
            f"frame={frame}, SHA256={self.spell_id})"
        )

    #region Internal helpers
    def _ensure_crafter(self) -> ISpellCrafterSurface:
        """
        Lazily create and attach the spell-owned `SpellCrafter`.

        Contract:
            - Returns the same attached crafter until cleanup clears it.
            - Performs a local import to avoid circular import coupling between
              `spell.py` and `spell_crafter.py`.
            - Seeds the crafter with the current spell resolution profile when
              the attached reflective profile exposes one.

        Returns:
            SpellCrafter:
                The spell-owned crafter responsible for compiler and resolution phases.

        """
        if self._crafter is None:
            from melder.spellbook.spell_crafter.spell_crafter import SpellCrafter
            resolution_profile = None
            if isinstance(self.profile, (ISpellGeneralProfile, ISpellDetailedProfile)):
                resolution_profile = self.profile.resolution_profile
            self._crafter = SpellCrafter(
                self,
                resolution_profile=resolution_profile,
            )
        return self._crafter
    #endregion Internal helpers

    #region Introspection Helpers
    @property
    def key(self) -> tuple[str, str]:
        """
        Internal

        Return the canonical `(frame_key, binding_key)` lookup tuple.

        Contract:
            - Always reflects the bind-time normalized key produced by
              `SpellInputUtils.make_spell_key_from_parts(...)`.
            - Read-only at the Spell layer; callers must not mutate key
              semantics after bind time.

        Returns:
            tuple[str, str]:
                Canonical Spellbook dictionary key for this spell.

        """
        return self._key

    @property
    def is_existing_creation(self) -> bool:
        """
        Whether this spell represents an existing, pre-created object.

        Returns:
            bool:
                True only for `EXISTING_CREATION*` spell types.
        """
        return self._is_existing_creation

    @property
    def is_class_spell(self) -> bool:
        """
        Whether this spell represents a class-backed factory registration.

        Returns:
            bool:
                True only for `SPELL*` spell types.
        """
        return self._is_class_spell

    @property
    def is_method_spell(self) -> bool:
        """
        Whether this spell represents a non-lambda method or function registration.

        Returns:
            bool:
                True only for non-lambda `METHOD*` spell types.
        """
        return self._is_method_spell

    @property
    def is_lambda_spell(self) -> bool:
        """
        Whether this spell represents one of the lambda-backed method spell variants.

        Returns:
            bool:
                True only for lambda `METHOD*` spell types.
        """
        return self._is_lambda_spell

    @property
    def has_existing_object(self) -> bool:
        """
        Whether this spell currently holds a concrete user-provided object.

        Contract:
            - Meaningful only for `EXISTING_CREATION*` spell types.
            - Returns False for factory-style spell types even if they later
              create runtime instances through conduits.

        Returns:
            bool:
                True when `user_created_object` is currently attached.

        """
        return self.user_created_object is not None

    @property
    def owner_conduit_info(self) -> tuple[Optional[str], Optional[str]]:
        """
        Return the current conduit ownership tuple for this spell.

        Returns:
            tuple[Optional[str], Optional[str]]:
                `(owner_conduit_id, owner_conduit_name)` when ownership has been
                stamped, otherwise `(None, None)`.

        """
        return self._owner_conduit_id, self._owner_conduit_name

    @property
    def requirements(self) -> Optional["SpellRequirements"]:
        """
        Phase 1 artifact for this spell, if it has been computed.

        This is populated by :meth:`run_phase_requirements` via :class:`SpellCrafter`.
        """
        if self._crafter is None:
            return None
        return self._crafter.requirements

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.

        This is populated by :meth:`run_phase_symbolic_graph` via :class:`SpellCrafter`.
        """
        if self._crafter is None:
            return None
        return self._crafter.symbolic_graph

    @property
    def resolution_frame(self) -> Any:
        """
        Phase 3 local resolution frame / DAG for this spell, if it has been computed.

        This is populated by :meth:`run_phase_local_frame` via :class:`SpellCrafter`.
        Concrete type is intentionally opaque here; callers should treat it as
        an internal resolution artifact.
        """
        if self._crafter is None:
            return None
        return self._crafter.resolution_frame

    @property
    def validation_result_phase4(self) -> Any:
        """
        Phase 4 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        if self._crafter is None:
            return None
        return self._crafter.validation_result_phase4

    @property
    def validation_result_phase6(self) -> Any:
        """
        Phase 6 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        if self._crafter is None:
            return None
        return self._crafter.validation_result_phase6

    @property
    def validated(self) -> bool:
        """
        Whether Phase 4 validation currently considers this spell valid.

        Returns:
            bool:
                False until a crafter exists and its validation result marks the
                spell valid.

        """
        if self._crafter is None:
            return False
        return self._crafter.validated

    @property
    def is_broken(self) -> bool:
        """
        Whether validation currently classifies this spell as broken or unsafe.

        Returns:
            bool:
                False until a crafter exists and flags the spell as broken.

        """
        if self._crafter is None:
            return False
        return self._crafter.is_broken
    #endregion Introspection Helpers

    #region Configuration
    def invalidate_spell(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Invalidate this spell for a full next-meld rebuild.

        Purpose:
            Provide one spell-local helper for the common "this spell is no
            longer trustworthy; rebuild it on the next meld" path. This method
            is the spell-owned convenience wrapper over two different
            invalidation layers:

            1. spell-local runtime invalidation
               - clear the cached `CreationContext`
               - force deferred runtime resolution to run again
            2. lineage/control-plane invalidation
               - mark the lineage structurally gated in `SpellSystemStates`

        Contract:
            - Safe to call multiple times on a live spell.
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Clears the spell-owned `CreationContext` so cached runtime
              dispatch state cannot survive a structural invalidation.
            - Sets `resolution_complete=False` and `resolution_required=True`
              so the next meld re-enters the deferred runtime plan path after
              structural validation succeeds.
            - Uses `SpellSystemStates.mark_structural_change(...)` when the
              control-plane registry is available.
            - Defaults the reason to `SpellStateChangeReason.structure_changed`
              when callers do not supply a more specific reason.
            - Intentionally does not use transfer-only hard-disable semantics;
              this helper models the recoverable post-change posture rather than
              the unsafe mid-transfer posture.

        Args:
            change_reason:
                Optional structural change reason to record in the lineage
                state. When omitted, the helper uses
                `SpellStateChangeReason.structure_changed`.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell has already been cleaned, or if the spell is not
                attached to a dynamic runtime environment.
        """
        self.check_cleaned()
        if change_reason is None:
            change_reason = SpellStateChangeReason.structure_changed
        if not self._dynamic_environment:
            raise RuntimeError(
                "Dynamic environment is not enabled. Spell invalidation for revalidation requires dynamic mode."
            )

        with self._lock:
            self._cleanup_creation_context()
            self.resolution_complete = False
            self.resolution_required = True

        if self._spell_system_states is not None and self.spell_index is not None:
            self._spell_system_states.mark_structural_change(
                self.spell_index,
                change_reason,
            )

    def _add_owned_conduit(
            self,
            conduit_id: str,
            conduit_name: Optional[str] = None,
            creations: Any = None,
            *,
            dynamic_environment: bool,
            creation_gate_controller: CreationGateController,
    ) -> None:
        """
        Internal

        Records ownership information about the Conduit that \"owns\" this spell.

        This is used to:
        - Attach the spell to a specific Conduit identity (for logging, diagnostics, and scoping).
        - Provide a handle to the Conduit's creation scope (e.g., for singletons tied to that conduit).
        - Reconfigure CreationContextFactory dependencies for the new owner.
        - Invalidate the spell-owned CreationContext because ownership/scoping changed.

        Args:
            conduit_id (str):
                The unique ID of the conduit that owns this spell.
            conduit_name (Optional[str]):
                Human-readable name of the owning conduit, if available.
            creations (Any):
                Conduit-level creations container used for managing shared instances.
            dynamic_environment (bool):
                True when the owning conduit runs in dynamic mode.
            creation_gate_controller (CreationGateController):
                Frame-owned CreationGateController used by CreationContextFactory.

        Returns:
            None.
        """
        with self._lock:
            # Ownership changes invalidate spell-bound runtime context shape.
            self._cleanup_creation_context()
            self._configure_creation_context_factory(
                dynamic_environment=dynamic_environment,
                creation_gate_controller=creation_gate_controller,
            )
            self._owner_conduit_id = conduit_id
            self._owner_conduit_name = conduit_name
            self.owned_spell = True
            self._owner_creations = creations

    def _add_build_details(
            self,
            dag: Any,
            dependencies: List[str],
    ) -> None:
        """
        Internal

        Attach static build-time dependency graph details to this spell.

        This is typically invoked by the SpellCrafter / DAG builder after it has
        analyzed the spell's parameters and constructed a dependency DAG.

        Contract:
            - Replaces the current dependency graph/dependencies references.
            - Invalidates any existing spell-owned CreationContext so runtime
              shape is rebuilt against the updated spell structure.

        Args:
            dag:
                A static DAG representation for this spell's dependency structure.
                This object is considered immutable at runtime and may expose a
                `dispose()` method for cleanup.
            dependencies:
                A list of spell_ids (SHA256 fingerprints) that this spell depends on.

        Raises:
            ValueError:
                If `dag` is None or `dependencies` is None.
        """
        if dag is None:
            raise ValueError("Dependency graph cannot be None.")
        if dependencies is None:
            raise ValueError("Dependencies cannot be None.")

        with self._lock:
            self.dependency_graph = dag
            self.dependencies = dependencies
            self._cleanup_creation_context()


    #endregion Configuration
    #region Resolution Phases
    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 - Requirements extraction (facade).

        Delegates to the SpellCrafter to analyze constructor requirements
        and capture dependency metadata for this spell.

        Contract:
            - Requires a live Spell (not cleaned).
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute any later phases.

        Args:
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        Notes:
            Phase artifacts are cleaned after Phase 7; spell-level dependency
            data and system state remain available.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_requirements(cancel_event=cancel_event)

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 - Symbolic graph construction (facade).

        Delegates to the SpellCrafter to build the symbolic dependency graph
        for this spell from Phase 1 requirements.

        Contract:
            - Requires Phase 1 to have completed successfully.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_symbolic_graph(cancel_event=cancel_event)

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 3 - Local resolution frame / DAG (facade).

        Delegates to the SpellCrafter to resolve dependencies against the
        Spellbook and build the local resolution frame.

        Contract:
            - Requires Phases 1 and 2 to have completed successfully.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_local_frame(cancel_event=cancel_event)

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 - Per-spell validation (facade).

        Delegates to the SpellCrafter to validate this spell's Phase 1-3
        artifacts and set validated/broken flags.

        Contract:
            - Requires Phases 1-3 to have completed successfully.
            - Does not return a value; results are stored on the crafter.
            - Does not execute later phases.

        Args:
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_validation(cancel_event=cancel_event)

    def run_phase_root_blueprints(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 - Root blueprint construction (facade).

        Delegates to the SpellCrafter to build system-level DAG blueprints
        and a SpellSystemIndex for the current frame.

        Contract:
            - Requires Phase 4 to have completed successfully.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_root_blueprints(conduit_id, cancel_event=cancel_event)

    def run_phase_root_blueprints_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 local - target spell closure blueprint construction (facade).

        Delegates to the SpellCrafter to build local Phase 5 artifacts for the
        target spell and its dependency closure.

        Contract:
            - Requires Phase 4 to have completed successfully.
            - Scope is limited to this spell plus transitive dependencies.
            - Does not execute later phases.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_root_blueprints_local(conduit_id, cancel_event=cancel_event)

    def run_phase_occurrence_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation (facade).

        Delegates to the SpellCrafter to compile the occurrence plan for root
        spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_occurrence_plan(conduit_id, cancel_event=cancel_event)

    def run_phase_injection_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 9 - Injection plan compilation (facade).

        Delegates to the SpellCrafter to compile the injection plan for root
        spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 8 artifacts to be available.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_injection_plan(conduit_id, cancel_event=cancel_event)

    def run_phase_patch_maps(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 10 - Patch map compilation (facade).

        Delegates to the SpellCrafter to compile override and mutation patch maps
        for root spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 9 artifacts to be available.
            - Does not return a value; artifacts are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_patch_maps(conduit_id, cancel_event=cancel_event)

    def run_phase_execution_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 11 - Execution plan compilation (facade).

        Delegates to the SpellCrafter to compile the execution plan for
        root spells. Non-root spells are treated as a no-op.

        Contract:
            - Invalidates the spell-owned CreationContext after execution-plan
              changes so meld rebuilds a fresh spell-shaped runtime context.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_execution_plan(conduit_id, cancel_event=cancel_event)
        self._cleanup_creation_context()

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation (facade).

        Delegates to the SpellCrafter to validate system-level DAG integrity
        and update per-conduit resolution validity.

        Contract:
            - Requires Phase 5 to have completed successfully.
            - Does not return a value; results are stored on the crafter.
            - Does not execute later phases.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_system_validation(conduit_id, cancel_event=cancel_event)

    def run_phase_system_validation_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 local - scoped system validation (facade).

        Delegates to the SpellCrafter to validate only the local Phase 5 scope
        for this spell.

        Contract:
            - Requires local Phase 5 artifacts.
            - Updates per-conduit resolution validity for scoped ids only.
            - Does not execute later phases.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_system_validation_local(conduit_id, cancel_event=cancel_event)

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring (facade).

        Delegates to the SpellCrafter to ensure change-control wiring and
        component-of indexing are prepared for this frame.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; wiring occurs inside the crafter.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_change_control(conduit_id, cancel_event=cancel_event)

    def run_phase_change_control_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 local - scoped change-control wiring (facade).

        Delegates to the SpellCrafter to refresh change-control mappings only
        for locally revalidated roots.

        Contract:
            - Requires local Phase 5 artifacts.
            - Preserves component-of mappings for unrelated roots.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        Returns:
            None.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_change_control_local(conduit_id, cancel_event=cancel_event)

    def get_local_resolution_scoped_spell_ids(self) -> Set[str]:
        """
        Return the spell ids currently covered by this spell's local Phase 5 scope.

        Contract:
            - Always includes this spell's current `spell_id`.
            - Adds any additional spell ids present in the local Phase 5 system
              index when that artifact exists.

        Returns:
            Set[str]: Spell ids in the local target-resolution scope.
        """
        self.check_cleaned()
        scoped_spell_ids: Set[str] = {self.spell_id}
        crafter = self._ensure_crafter()
        scoped_spell_ids.update(crafter.get_phase5_spell_ids())
        return scoped_spell_ids

    def get_local_resolution_scoped_root_ids(self) -> Tuple[str, ...]:
        """
        Return the root ids currently covered by this spell's local Phase 5 scope.

        Contract:
            - Falls back to `(self.spell_id,)` when no local Phase 5 rooted
              blueprints are available yet.

        Returns:
            Tuple[str, ...]: Root ids in the local target-resolution scope.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        scoped_root_ids = crafter.get_phase5_root_ids()
        if len(scoped_root_ids) == 0:
            return (self.spell_id,)
        return scoped_root_ids

    def run_structural_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **structural phases only** (1-4) for this spell.

        Phases executed via the :class:`SpellCrafter`:

            1. Requirements extraction.
            2. Symbolic graph construction.
            3. Local resolution frame / DAG construction.
            4. Validation.

        Each phase honours the optional :class:`CancellationEvent`. If the
        event is set, the underlying phase methods will raise via
        ``cancel_event.throw_if_set()``.

        Raises:
            Exception: Propagates exceptions raised by the underlying phases.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()

        crafter.run_phase_requirements(cancel_event=cancel_event)
        crafter.run_phase_symbolic_graph(cancel_event=cancel_event)
        crafter.run_phase_local_frame(cancel_event=cancel_event)
        crafter.run_phase_validation(cancel_event=cancel_event)

    def run_all_phases(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **all compiler / resolution phases** for this spell, in order.

        Phases executed via the :class:`SpellCrafter`:

            - Phase 1: Requirements extraction.
            - Phase 2: Symbolic graph construction.
            - Phase 3: Local resolution frame / DAG construction.
            - Phase 4: Validation.
            - Phase 5: Root blueprint construction.
            - Phase 6: System validation.
            - Phase 7: Change-control wiring.
            - Phase 8: Occurrence plan compilation.
            - Phase 9: Injection plan compilation.
            - Phase 10: Patch map compilation.
            - Phase 11: Execution plan compilation.

        Each phase honours the optional :class:`CancellationEvent`. If the
        event is set, the underlying phase methods will raise via
        ``cancel_event.throw_if_set()``.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Raises:
            Exception: Propagates exceptions raised by the underlying phases.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()

        crafter.run_phase_requirements(cancel_event=cancel_event)
        crafter.run_phase_symbolic_graph(cancel_event=cancel_event)
        crafter.run_phase_local_frame(cancel_event=cancel_event)
        crafter.run_phase_validation(cancel_event=cancel_event)
        crafter.run_phase_root_blueprints(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_system_validation(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_change_control(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_occurrence_plan(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_injection_plan(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_patch_maps(conduit_id, cancel_event=cancel_event)
        crafter.run_phase_execution_plan(conduit_id, cancel_event=cancel_event)
        self._cleanup_creation_context()
        crafter.cleanup_phase_artifacts()


    #endregion Resolution Phases
    #region Spell Mutations
    @property
    def system_state(self) -> Optional["SpellSystemState"]:
        """
        Return the SpellSystemState instance associated with this spell's lineage.

        This is a read-mostly view into the change-control and validation state
        tracked by SpellSystemStates.

        Contract:
            - Mutation and contract operations can ask for the current lineage state.
            - Higher-level dev-ops and validation pipelines can inspect this value
              while orchestrating Phase 1-7 revalidation.
            - Returns `None` when SpellSystemStates is unavailable or the lineage is
              not currently tracked.

        Returns:
            Optional[SpellSystemState]:
                The state object for this spell's lineage, if available.

        """
        self.check_cleaned()
        if self._spell_system_states is None:
            return None

        # SpellSystemStates tracks states by SpellIndex.id / spell_id
        return self._spell_system_states.get_by_index_id(self.spell_index.id)


    # ------------------------------------------------------------------
    # Mutation override (graph overlay) API
    # ------------------------------------------------------------------
    @property
    def mutation_override(self) -> dict:
        """
        Current mutation override payload for this spell's DAG.

        This is a structural overlay that the mutation pipeline can apply to the
        spell's DI shape in Dynamic or AI-native mode. It is conceptually separate
        from normal SpellMap overrides:

        - `SpellMap.spell_override` -> per-call or per-site DI override.
        - `Spell.mutation_override` -> per-spell graph overlay used by the mutation hub.

        Semantics:
            - An empty dict (`{}`) is treated as "no active overlay" by default.
            - Higher-level mutation systems may refine that distinction later, but the
              Spell layer exposes the raw payload exactly as stored.

        Returns:
            dict:
                The concrete overlay payload currently attached to this spell.

        """
        # Expose the concrete container; callers can decide if '{}' means
        # "no overlay" or an explicit empty overlay.
        return self._mutation_override

    @property
    def has_mutation_override(self) -> bool:
        """
        Whether this spell currently has a non-empty mutation overlay.

        This is a convenience for Dynamic or AI-native flows that want a quick
        check before doing more expensive revalidation or graph rebuilds.

        Returns:
            bool:
                True when the current overlay payload is non-empty.

        """
        return bool(self._mutation_override)

    def apply_mutation_override(self, override: Optional[dict]) -> None:
        """
        Apply or update the DAG-level mutation override for this spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Requires overrides-enabled posture for this spell.
            - Stores the raw overlay payload on the spell.
            - Clears the spell-owned `CreationContext` so runtime shape is rebuilt
              on the next meld path.
            - Marks spell lineage state through SpellSystemStates when that service
              is available.
            - Treats `None` the same as an empty overlay payload.

        The actual rebuild or revalidation of the system graph is expected to be
        owned by the Phase 5-7 pipelines and the mutation hub.

        Args:
            override:
                New overlay payload. `None` or `{}` clears the overlay and leaves
                this spell in a no-active-overlay state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell is not attached to a dynamic runtime environment,
                or if overrides are disabled for this spell.

        """
        self.check_cleaned()
        if not self._dynamic_environment:
            raise RuntimeError(
                "Dynamic environment is not enabled. Mutation overrides require dynamic mode."
            )

        new_payload: dict = override if override is not None else {}
        self._mutation_override = new_payload
        if new_payload:
            change_reason = SpellStateChangeReason.mutation_contract_set
        else:
            change_reason = SpellStateChangeReason.mutation_contract_cleared
        self.invalidate_spell(change_reason=change_reason)


    def clear_mutation_override(self) -> None:
        """
        Clear any active mutation overlay for this spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Requires overrides-enabled posture for this spell.
            - Resets the local overlay payload back to the default empty dict.
            - Clears the spell-owned `CreationContext` so future meld work rebuilds
              runtime shape without the previous overlay.
            - Marks the lineage as mutation-cleared when SpellSystemStates is
              available.

        The actual effect on the compiled or system DAG remains owned by the
        higher-level mutation and validation pipelines.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell is not attached to a dynamic runtime environment,
                or if overrides are disabled for this spell.

        """
        self.check_cleaned()
        if not self._dynamic_environment:
            raise RuntimeError(
                "Dynamic environment is not enabled. Mutation overrides require dynamic mode."
            )

        if not self._mutation_override and not self.has_mutation_override:
            # Nothing to do; avoid spurious state changes.
            return

        self._mutation_override = {}
        self.invalidate_spell(
            change_reason=SpellStateChangeReason.mutation_contract_cleared,
        )

    #endregion Spell Mutations
#endregion Spell


