from typing import Optional, List, Any, Callable
import ulid
from threading import RLock
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionProfile,
)
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import ISpell, ISpellbook, ISpellSystemStates
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


#region Spell
class Spell(Cleanable, ISpell):
    """
    Internal

    🪄 Represents a registered spell within the Melder system.

    A `Spell` encapsulates an instantiable or callable unit of logic (class, function,
    lambda, or existing object) that can be bound, shared, and conjured via conduits
    within a Spellbook context. It includes type metadata, existence constraints,
    dependency information, and permission rules for downstream access.

    Core Responsibilities:
    - Holds an immutable reference to the object (function/class/instance) it represents.
    - Tracks configuration data: type, binding profile (if attached), spellframe,
      ownership, and hooks.
    - Defines dependency DAGs for invocation and construction (via external DAG /
      resolution pipelines).
    - Manages permission control via the `Permissions` enum.
    - Enables hook-based lifecycle support (pre, activation, post).
    - Acts as a source of truth for spell identity and access.

    🔐 Permissions (Permissions Enum):
        - `read`: Allows other conduits to use the spell as-is, but not modify or recreate it.
        - `create`: Allows other conduits to instantiate or construct new versions.
        - `block`: Prevents external access. Internal (owner conduit) access is still allowed.

    🎯 Key Concepts:
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
            - The Bind pipeline attaches a **SpellBindingProfile** instance here.
            - AI / analysis subsystems may later attach richer profiles (e.g. SpellAIProfile).
            - Legacy usage expecting ClassProfile / MethodProfile should treat this as
              an opaque introspection artifact.

        existing_object (Optional[object]):
            Optional pre-instantiated object to attach to the spell (EXISTING_CREATION* types).
            For factory-like spells (class/method/lambda), this is usually None.

        spellbook (Optional[ISpellbook]):
            Back-reference to the owning Spellbook. Primarily used for internal coordination
            (conduit ownership, graph wiring, diagnostics). Maybe None in some contexts.

        *args / **kwargs:
            Arbitrary tags and metadata for internal use or future extensions.

    Notes:
        - This class is never used directly by users. It is created during `bind()` and
          registered into the Spellbook and Aether.
        - Internal mutation after cleaning is disallowed.
        - Dependency graphs, resolution frames, and resolution profiles are produced
          by the Resolution / Meld layer; `Spell` itself does not execute resolution.
    """
    __melder_internal__ = _mrg.sentinel
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
        self.user_created_object: Optional[object] = existing_object
        self.binding_name: Optional[str] = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence

        # Reflective / binding profile (shape of the spell).
        # Typically, a SpellBindingProfile, but treated as opaque here.
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

        # Hooks
        self.pre_hooks: List[Callable[..., Any]] = []
        self.activation_hooks: List[Callable[..., Any]] = []
        self.post_hooks: List[Callable[..., Any]] = []

        # Final build-time artifacts
        self.dependency_graph: Any = None
        self.dependencies: List[str] = []  # SHA256 spell IDs required for this spell to function

        # Optional resolution profile (DI contract), to be populated by the
        # resolution pipeline (SpellExaminer → ResolutionProfileStrategy).
        self.resolution_profile: Optional[SpellResolutionProfile] = None

        # Per-spell compiler / resolution helper (SpellCrafter).
        # This owns all Phase 1–7 artifacts and is disposable.
        self._crafter: Optional["SpellCrafter"] = None

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
        Cleans up the spell, preventing any further modifications.

        This:
        - Disposes the static dependency graph if one was attached and exposes a `dispose()` method.
        - Clears references to owner creations and `user_created_object`.
        - Clears any compiler/phase artifacts via the attached :class:`SpellCrafter`.
        - Drops the Spellbook reference.
        - Marks the spell as cleaned so that further configuration is disallowed.

        Runtime resolution and instance lifecycle are owned by the Resolution / Meld layer,
        not by this class.

        Notes:
            - Idempotent: subsequent calls are safe and no-op after the first run.
            - Thread-safe: guarded by an internal RLock to avoid concurrent cleanup races.
            - Defensive: cleanup of child artifacts swallows exceptions to ensure teardown completes.
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

            if self.resolution_profile is not None:
                try:
                    self.resolution_profile.cleanup()
                except Exception:
                    pass

            if self.profile is not None and isinstance(self.profile, Cleanable):
                try:
                    self.profile.cleanup()
                except Exception:
                    pass

            # Phase artifacts – deterministically dropped via SpellCrafter.
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

            self._spellbook = None

            # Drop references to help GC and enforce immutability after cleanup.
            self._owner_creations = None
            self.user_created_object = None
            self._spell_system_states = None
            if self.pre_hooks is not None:
                self.pre_hooks.clear()
            if self.activation_hooks is not None:
                self.activation_hooks.clear()
            if self.post_hooks is not None:
                self.post_hooks.clear()
            if self.tags is not None and hasattr(self.tags, "clear"):
                try:
                    self.tags.clear()
                except Exception:
                    pass
            if isinstance(self.metadata, dict):
                self.metadata.clear()
            if isinstance(self.dependencies, list):
                self.dependencies.clear()
            self.pre_hooks = None
            self.activation_hooks = None
            self.post_hooks = None
            self.tags = None
            self.metadata = None
            self.dependencies = None
            self.dependency_graph = None
            self.resolution_profile = None
            self.profile = None
            self.spell = None
            self._key = None
            self._owner_conduit_id = None
            self._owner_conduit_name = None
            self.owned_spell = None
            self._owner_creations = None
            self.aetheric_frame = None
            self.spell_index = None

            self._cleaned = True
        self._lock = None
    #endregion Disposal

    #region Context Manager
    def __enter__(self) -> "Spell":
        """
        Enters the context manager for Aether-related operations.

        This is mainly useful for internal configuration phases where multiple attributes
        (hooks, metadata, etc.) are being attached under the same lock.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context manager for Aether-related operations.
        """
        self._lock.release()
    #endregion Context Manager

    def __repr__(self) -> str:
        """
        Return a concise, human-readable representation of the spell including name,
        binding, frame, and SHA256-derived spell ID. Used primarily for diagnostics
        and logging.
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
    def _ensure_crafter(self) -> "SpellCrafter":
        """
        Lazily create and attach the :class:`SpellCrafter` that owns this
        spell's compilation / resolution phases.

        We use a local import to avoid circular import issues between the
        `spell` and `spell_crafter` modules.
        """
        if self._crafter is None:
            from melder.spellbook.spell_crafter.spell_crafter import SpellCrafter
            self._crafter = SpellCrafter(self)
        return self._crafter
    #endregion Internal helpers

    #region Introspection Helpers
    @property
    def key(self) -> tuple[str, str]:
        """
        Internal

        Returns the canonical `(frame_key, binding_key)` used by the Spellbook
        for dictionary-based lookups. This is always normalized via SpellInputUtils.

        This is intentionally read-only; key semantics are controlled by binding time.
        """
        return self._key

    @property
    def is_existing_creation(self) -> bool:
        """
        Returns True if this spell represents an existing, pre-created object
        (EXISTING_CREATION* SpellTypes), rather than a factory.
        """
        return self.spell_type in {
            SpellType.EXISTING_CREATION,
            SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
            SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }

    @property
    def is_class_spell(self) -> bool:
        """
        Returns True if this spell represents a class-based factory (SPELL* SpellTypes).
        """
        return self.spell_type in {
            SpellType.SPELL,
            SpellType.SPELL_WITH_SPELLFRAME,
            SpellType.SPELL_WITH_BINDING_NAME,
            SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }

    @property
    def is_method_spell(self) -> bool:
        """
        Returns True if this spell represents a non-lambda method/function spell.
        """
        return self.spell_type in {
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }

    @property
    def is_lambda_spell(self) -> bool:
        """
        Returns True if this spell represents a lambda-based method spell.
        """
        return self.spell_type in {
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }

    @property
    def has_existing_object(self) -> bool:
        """
        Returns True if this spell currently holds a user-provided existing object.

        This is only meaningful for EXISTING_CREATION* SpellTypes; for other types
        it will always be False.
        """
        return self.user_created_object is not None

    @property
    def owner_conduit_info(self) -> tuple[Optional[str], Optional[str]]:
        """
        Returns `(owner_conduit_id, owner_conduit_name)` if this spell has
        been attached to a specific Conduit, otherwise `(None, None)`.
        """
        return self._owner_conduit_id, self._owner_conduit_name

    @property
    def requirements(self) -> Optional["SpellRequirements"]:
        """
        Phase 1 artifact for this spell, if it has been computed.

        This is populated by :meth:`run_phase_requirements` via :class:`SpellCrafter`.
        """
        crafter = self._crafter
        return crafter.requirements if crafter is not None else None

    @property
    def symbolic_graph(self) -> Optional["SpellSymbolicGraph"]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.

        This is populated by :meth:`run_phase_symbolic_graph` via :class:`SpellCrafter`.
        """
        crafter = self._crafter
        return crafter.symbolic_graph if crafter is not None else None

    @property
    def resolution_frame(self) -> Any:
        """
        Phase 3 local resolution frame / DAG for this spell, if it has been computed.

        This is populated by :meth:`run_phase_local_frame` via :class:`SpellCrafter`.
        Concrete type is intentionally opaque here; callers should treat it as
        an internal resolution artifact.
        """
        crafter = self._crafter
        return crafter.resolution_frame if crafter is not None else None

    @property
    def validation_result_phase4(self) -> Any:
        """
        Phase 4 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        crafter = self._crafter
        return crafter.validation_result_phase4 if crafter is not None else None

    @property
    def validation_result_phase6(self) -> Any:
        """
        Phase 6 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        crafter = self._crafter
        return crafter.validation_result_phase6 if crafter is not None else None

    @property
    def validated(self) -> bool:
        """
        True if the validation phase has run and marked this spell as validated.
        """
        crafter = self._crafter
        return crafter.validated if crafter is not None else False

    @property
    def is_broken(self) -> bool:
        """
        True if the validation phase classified this spell as broken / unsafe.
        """
        crafter = self._crafter
        return crafter.is_broken if crafter is not None else False
    #endregion Introspection Helpers

    #region Configuration
    def _add_owned_conduit(self, conduit_id: str, conduit_name: Optional[str] = None, creations: Any = None) -> None:
        """
        Internal

        Records ownership information about the Conduit that \"owns\" this spell.

        This is used to:
        - Attach the spell to a specific Conduit identity (for logging, diagnostics, and scoping).
        - Provide a handle to the Conduit's creation scope (e.g., for singletons tied to that conduit).

        Args:
            conduit_id (str):
                The unique ID of the conduit that owns this spell.
            conduit_name (Optional[str]):
                Human-readable name of the owning conduit, if available.
            creations (Any):
                Conduit-level creations container used for managing shared instances.
        """
        with self._lock:
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

            1. Requirements extraction.
            2. Symbolic graph construction.
            3. Local resolution frame / DAG construction.
            4. Validation.
            5. Root blueprint construction.
            6. System validation.
            7. Change-control wiring.

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
        crafter.cleanup_phase_artifacts()


    #endregion Resolution Phases
    #region Spell Mutations
    @property
    def system_state(self) -> Optional["SpellSystemState"]:
        """
        Return the SpellSystemState instance associated with this Spell's lineage.

        This is a *view* into the change-control / validation state tracked
        by SpellSystemStates. It is intentionally read-mostly at the Spell layer:

        - Mutation and contract operations can ask for the current state.
        - Higher-level dev-ops / validation pipelines can use this hook to
          inspect or assert state when orchestrating Phase 1–7 revalidation.

        Returns:
            SpellSystemState | None:
                The state object if SpellSystemStates is available and this
                spell has a registered lineage; otherwise None.
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
        Current mutation override payload for this Spell's DAG.

        This is a *structural overlay* that the mutation pipeline can apply
        to the spell's DI shape in Dynamic / AI-native mode. It is conceptually
        separate from normal SpellMap overrides:

        - SpellMap.spell_override → per-call / per-site DI override.
        - Spell.mutation_override → per-spell *graph* overlay used by the
          MutationContract / mutation hub.

        Semantics:
            - An empty dict (`{}`) is treated as “no active overlay” by
              default. The higher-level mutation system may refine this
              distinction later (e.g., between "no overlay" and "explicit
              empty override") but at the Spell level we simply expose the
              raw payload.
        """
        # Expose the concrete container; callers can decide if '{}' means
        # "no overlay" or an explicit empty overlay.
        return self._mutation_override

    @property
    def has_mutation_override(self) -> bool:
        """
        Whether this Spell currently has a non-empty mutation overlay.

        This is a convenience for Dynamic / AI-native flows that want a quick
        check before doing more expensive revalidation or graph rebuilds.
        """
        return bool(self._mutation_override)

    def apply_mutation_override(self, override: Optional[dict]) -> None:
        """
        Apply or update the DAG-level mutation override for this Spell.
        Instead, it:

        - Updates the local overlay payload; and
        - Marks the Spell's lineage as structurally changed via
          SpellSystemStates (if available), using a mutation_contract_*
          change reason.

        The actual rebuild / revalidation of the system graph is expected to
        be driven by the Phase 5–7 pipelines and the mutation hub.

        Args:
            override:
                New overlay payload. `None` or `{}` clears the overlay and
                leaves this Spell in a "no active mutation overlay" state.
        """
        self.check_cleaned()

        new_payload: dict = override if override is not None else {}
        self._mutation_override = new_payload

        if self._spell_system_states is not None and self.spell_index is not None:
            if new_payload:
                change_reason = SpellStateChangeReason.mutation_contract_set
            else:
                change_reason = SpellStateChangeReason.mutation_contract_cleared

            self._spell_system_states.mark_structural_change(
                self.spell_index,
                change_reason,
            )


    def clear_mutation_override(self) -> None:
        """
        Clear any active mutation overlay for this Spell.

        This resets the local overlay payload back to the default empty dict,
        and, if SpellSystemStates is available, marks the lineage as having
        rolled back a mutation.

        The actual effect on the compiled/system DAG is owned by the higher-
        level mutation / validation pipelines.
        """
        self.check_cleaned()

        if not self._mutation_override and not self.has_mutation_override:
            # Nothing to do; avoid spurious state changes.
            return

        self._mutation_override = {}

        if self._spell_system_states is not None and self.spell_index is not None:
            self._spell_system_states.mark_structural_change(
                self.spell_index,
                SpellStateChangeReason.mutation_contract_cleared,
            )

    #endregion Spell Mutations
#endregion Spell
