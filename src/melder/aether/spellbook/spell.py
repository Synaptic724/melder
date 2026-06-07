from typing import TYPE_CHECKING, Optional, List, Any, Callable, Sequence, ClassVar, Union
import ulid
from threading import RLock
from types import TracebackType

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils

from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )
    from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
        SpellSystemValidationState,
    )
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import (
        SpellValidationResult,
    )



#region Spell

class Spell(Cleanable):
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
      `CreationContext`, execution-plan dispatch-route metadata, and mutation
      overlays.
    - Does not validate bind-time inputs by itself; upstream bind/examiner
      stages are expected to hand it already-validated configuration.
    - Uses an internal `RLock` to guard multi-field configuration and cleanup
      transitions.
    - Becomes unusable after `cleanup()` completes; later live-object methods
      are expected to fail through `check_cleaned()`.
    - Disposal methods should not be modified after creation as it will create
      problems with the runtime. The runtime will optimize creation and disposal
      methods added after the fact are ignored.

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
    - Tracks whether runtime resolution is still required before the first context build.
    - Caches the Phase 11 execution-plan dispatch-route hint used by current
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
            Maybe None for unnamed/default bindings.

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

        spellbook (Spellbook):
            Back-reference to the owning Spellbook. This is a required live-owner
            contract used for internal coordination, graph wiring, diagnostics,
            and spell-system-state attachment.

        *args / **kwargs:
            Arbitrary tags and metadata for internal use or future extensions.

    Threading / Concurrency:
        - '_Lock' guards internal multi-field mutation.
        - Spell-owned runtime context publication uses `_creation_context_switch`
          so only one builder wins publication at a time.
        - Higher-level conduit/spellbook orchestration still owns system-level
          concurrency decisions; this class only protects its own local state.

    Lifecycle / Cleanup:
        - `Spell` owns its spell compiler artifact foundation, spell-owned
          `CreationContextFactory`, spell-owned `CreationContext`, hook lists,
          dependency/build artifacts and cached execution-plan dispatch-route
          metadata.
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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_activation_hooks",
        "_creation_context",
        "_creation_context_factory",
        "_creation_context_switch",
        "_caching_enabled",
        "_compiler_artifact",
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
        "_spellbook_cleanup",
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
        "permissions",
        "profile",
        "resolution_required",
        "resolution_complete",
        "requires_spellspace_request",
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
            spellbook: "Spellbook",
            profile: Optional[Any] = None,
            existing_object: Optional[object] = None,
            *args: Any,
            **kwargs: Any,
    ):
        """
        Internal constructor for a bound Spell record.

        Args:
            spell (Any): The underlying callable/class/instance being registered.
            spell_index (SpellIndex): Lineage/version tracker for this spell.
            spellframe (Optional[Any]): Logical frame/contract used to scope the spell.
            binding_name (Optional[str]): Optional binding key is used to disambiguate spells under the same frame.
            spell_name (str): Resolved name for the spell (qualname or type name).
            existence (Existence): Lifecycle policy for instantiation/sharing semantics.
            spell_type (SpellType): Classification of the spell (class/method/lambda/existing-creation variants).
            spell_id (str): SHA256 fingerprint for this spell's structural identity.
            permissions (Permissions): Access policy for other conduits.
            aetheric_frame (str): Aether frame identifier this spell belongs to.
            profile (Optional[Any]): Binding/introspection profile attached by the examiner.
            existing_object (Optional[object]): Pre-created instance for EXISTING_CREATION* spell types.
            spellbook (Spellbook): Back-reference to the owning spellbook for coordination.
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
        self._spellbook: Spellbook = spellbook
        self._spellbook_cleanup: bool = False

        # Spell Metadata
        self.tags = list(args) if args else []
        self.metadata = kwargs if kwargs else {}
        self._mutation_override: Optional[dict[str, Any]] = None
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

        # Foundation artifact home for compiler/build state and validation
        # artifacts owned directly by the Spell.
        self._compiler_artifact: SpellCompilerArtifact = (
            SpellCompilerArtifact(self.spell_id)
        )
        # Spell-owned meld execution context (created lazily by CreationContextFactory).
        self._creation_context: Optional[CreationContext] = None
        # Spell-owned context factory configured at conduit ownership stamp time.
        self._creation_context_factory: Optional[CreationContextFactory] = None
        # Spell-owned selector latch for one-leader CreationContext publication.
        self._creation_context_switch: CounterSwitch = CounterSwitch(state=0)
        # Runtime cache policy mirror. Defaults to enabled and may be overridden
        # later by the owning Spellbook/Aether posture during conduit stamping.
        self._caching_enabled: bool = True
        # Runtime mode carried from owning conduit for context factory wiring.
        self._dynamic_environment: bool = False
        # Runtime resolution gate flag (False for full AOT by default).
        self.resolution_required: bool = False
        # Runtime deferred-resolution completion flag.
        # Starts False and flips True only when Phase12 compile wiring completes.
        self.resolution_complete: bool = False
        # Compiler-derived runtime request flag.
        # True means the rooted request graph contains a spellspace-scoped
        # dependency, and the spell therefore requires an active spellspace
        # request context at runtime.
        self.requires_spellspace_request: bool = False

        # Created after Conduit made (ownership / scope integration)
        self._owner_conduit_id: Optional[str] = None
        self._owner_conduit_name: Optional[str] = None
        self._owner_creations: Any = None  # Scope level creations for singletons

        # Spell System State
        self._spell_system_states: SpellSystemStates = self._spellbook._spell_system_states

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
        Release the spell-owned runtime state and permanently retire this Spell.

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
              `_lock` reference itself after the teardown completes.

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
            if not self._spellbook_cleanup:
                self._spellbook.cleanup_and_remove_spell(self)
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

            try:
                self._compiler_artifact.cleanup()
            except Exception:
                pass
            # Drop references to help GC and enforce immutability after cleanup.
            self._cleanup_creation_context()
            self._cleanup_creation_context_factory()
            try:
                self._creation_context_switch.cleanup()
            except Exception:
                pass

            if self._pre_hooks:
                self._pre_hooks.clear()
            if self._activation_hooks:
                self._activation_hooks.clear()
            if self._post_hooks:
                self._post_hooks.clear()
            if self.tags:
                self.tags.clear()
            if self.metadata:
                self.metadata.clear()
            if self._mutation_override:
                self._mutation_override.clear()
            if self.dependencies:
                self.dependencies.clear()
            if self.disposal_method_names:
                self.disposal_method_names.clear()
            self._cleaned = True
            self._hooks_enabled = False

            del self._owner_creations
            del self.user_created_object
            del self._spellbook_cleanup
            del self._spell_system_states
            del self._spellbook
            del self._pre_hooks
            del self._activation_hooks
            del self._post_hooks
            del self.tags
            del self.metadata
            del self._mutation_override
            del self.dependencies
            del self.disposal_method_names
            del self.dependency_graph
            del self.profile
            del self.spell
            del self._creation_context
            del self._creation_context_factory
            del self._creation_context_switch
            del self._caching_enabled
            del self._compiler_artifact
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
                arguments and be invoked before resolution.
            activation_hooks:
                Optional list/tuple of activation hooks. Each hook receives the
                newly created instance as its first argument.
            post_hooks:
                Optional list/tuple of post-cast hooks. Each hook must accept no
                arguments and be invoked after resolution.

        Returns:
            None.

        Raises:
            RuntimeError: If the Spell has already been cleaned.
        """
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
        if creation_context_factory is None:
            raise RuntimeError("Spell has no configured CreationContextFactory.")
        return creation_context_factory.get_or_build_for_spell(self)

    def emit_cache(self) -> bool:
        """
        Public API

        Emit this spell's current cache payload through its owning Spellbook.

        Purpose:
            Provide one spell-facing cache export entrypoint without moving
            cache ownership or file mutation into `CreationContext`.

        Contract:
            - Returns early when spell-level cache policy is disabled.
            - Delegates the real cache update to the owning Spellbook.
            - Requires the spell to still have a live owning Spellbook.

        Returns:
            bool:
                True when the spell emitted a cache payload, otherwise False.

        Raises:
            RuntimeError:
                If the spell no longer has an owning Spellbook.
        """
        self.check_cleaned()
        if not self._caching_enabled:
            return False
        spellbook = self._spellbook
        if spellbook is None:
            raise RuntimeError("Spell has no owning Spellbook surface.")
        return spellbook._emit_spell_cache(self)


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

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
    ) -> None:
        """
        Release the spell's internal lock after a context-manager's block.

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

        This is populated by the compiler artifact during structural phase
        execution.
        """
        return self._compiler_artifact._requirements

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.

        This is populated by the compiler artifact during structural phase
        execution.
        """
        return self._compiler_artifact._symbolic_graph

    @property
    def resolution_frame(self) -> Any:
        """
        Phase 3 local resolution frame / DAG for this spell, if it has been computed.

        This is populated by the compiler artifact during structural phase
        execution.
        Concrete type is intentionally opaque here; callers should treat it as
        an internal resolution artifact.
        """
        return self._compiler_artifact._resolution_frame

    @property
    def validation_result_phase4(self) -> Optional[SpellValidationResult]:
        """
        Phase 4 validation result for this spell, if it has been computed.

        This is populated by the compiler artifact during structural phase
        execution.
        """
        return self._compiler_artifact._validation_result_phase4

    @property
    def validation_result_phase6(self) -> Optional[SpellSystemValidationState]:
        """
        Phase 6 validation result for this spell, if it has been computed.

        This is populated by the compiler artifact during conduit-scoped
        validation.
        """
        return self._compiler_artifact._validation_result_phase6

    @property
    def validated(self) -> bool:
        """
        Whether Phase 4 validation currently considers this spell valid.

        Returns:
            bool:
                False until Phase 4 validation has populated the compiler
                artifact.

        """
        return self._compiler_artifact._validated_phase4

    @property
    def is_broken(self) -> bool:
        """
        Whether validation currently classifies this spell as broken or unsafe.

        Returns:
            bool:
                False until Phase 4 validation has populated the compiler
                artifact.

        """
        return self._compiler_artifact._is_broken
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
            - Clears the spell-owned `CreationContext` so the cached runtime dispatch state cannot survive a structural invalidation.
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
            caching_enabled: bool,
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
            caching_enabled (bool):
                True when the owning Spellbook/Aether posture wants this spell
                to emit runtime payloads into the cache.

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
            self._owner_creations = creations
            self._caching_enabled = caching_enabled

    def _add_build_details(
            self,
            dag: Any,
            dependencies: List[str],
    ) -> None:
        """
        Internal

        Attach static build-time dependency graph details to this spell.

        This is typically invoked by the structural DAG builder after it has
        analyzed the spell's parameters and constructed a dependency DAG.

        Contract:
            - Replaces the current dependency graph/dependencies references.
            - Invalidates any existing spell-owned CreationContext so the runtime shape is rebuilt against the updated spell structure.

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
            - Returns `None` when SpellSystemStates are unavailable or the lineage is
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
        Current persistent default override payload for this spell.

        This payload is pre-normalized into the same override-map shape that
        meld-time runtime overrides use. It is conceptually separate from the
        caller-supplied `spell_override` argument passed into `meld(...)`:

        - meld `spell_override` -> one-call runtime override payload
        - `Spell.mutation_override` -> persistent default override payload
          stored on the spell itself

        Semantics:
            - An empty dict (`{}`) means no active default payload.
            - Positional payloads are normalized into `{"__args__": [...]}`.
            - Keyword payloads are copied into a fresh dict so later meld calls
              do not depend on caller-owned containers.

        Returns:
            Optional[dict[str, Any]]:
                The normalized persistent default override payload currently
                attached to this spell, or `None` when no default payload is
                active.

        """
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

    def apply_mutation_override(
            self,
            override: Optional[Union[dict, list, tuple]],
    ) -> None:
        """
        Apply or replace the persistent default override payload for this spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Normalizes the payload into the same runtime override-map shape
              that meld-time caller overrides use.
            - Stores only the normalized runtime payload shape on the spell.
            - Does not invalidate the spell, clear CreationContext, or mark
              structural change state.
            - Treats `None` and empty dict payloads as "no active default
              override payload."

        Args:
            override:
                New persistent default override payload. Supported shapes match
                meld-time override payloads:
                - `dict` for targeted keyword-style overrides
                - `list` / `tuple` for root positional overrides
                - `None` to clear the default payload

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell is not attached to a dynamic runtime environment.
            TypeError:
                If `override` is not one of the supported override payload
                shapes.

        """
        self.check_cleaned()
        if not self._dynamic_environment:
            raise RuntimeError(
                "Dynamic environment is not enabled. Mutation overrides require dynamic mode."
            )

        self._mutation_override = self._normalize_mutation_override_payload(override)


    def clear_mutation_override(self) -> None:
        """
        Clear any active persistent default override payload for this spell.

        Contract:
            - Requires the spell to be attached to a dynamic runtime
              environment.
            - Resets the stored payload back to `None`.
            - Does not invalidate the spell or rebuild runtime shape.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the spell is not attached to a dynamic runtime environment.

        """
        self.check_cleaned()
        if not self._dynamic_environment:
            raise RuntimeError(
                "Dynamic environment is not enabled. Mutation overrides require dynamic mode."
            )
        self._mutation_override = None

    @staticmethod
    def _normalize_mutation_override_payload(
            override: Optional[Union[dict, list, tuple]],
    ) -> Optional[dict[str, Any]]:
        """
        Normalize one stored mutation override payload into runtime shape.

        Contract:
            - `None` and empty dict payloads normalize to `None`.
            - Dict payloads are shallow-copied into a fresh mapping.
            - Positional list/tuple payloads normalize to `{"__args__": [...]}`.
            - Raises on unsupported payload shapes instead of coercing them.
        """
        if override is None:
            return None

        if isinstance(override, dict):
            if not override:
                return None
            return dict(override)

        if isinstance(override, (list, tuple)):
            return {"__args__": list(override)}

        raise TypeError(
            "mutation_override must be a dict, list, or tuple."
        )

    #endregion Spell Mutations
#endregion Spell




