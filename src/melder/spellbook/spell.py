from __future__ import annotations

from typing import Optional, List, Any, Callable
import ulid
from threading import RLock

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
class Spell(ISpell, Cleanable):
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
        # This owns all Phase 1–4 artifacts and is disposable.
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
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            dg = self.dependency_graph
            if dg is not None and hasattr(dg, "dispose"):
                try:
                    dg.dispose()
                except Exception:
                    # Never let cleanup explosions propagate.
                    pass

            # Phase artifacts – deterministically dropped via SpellCrafter.
            if self._crafter is not None:
                try:
                    self._crafter.cleanup()
                except Exception:
                    # Never let cleanup explosions propagate.
                    pass
                self._crafter = None

            self._spellbook = None

            # Drop references to help GC and enforce immutability after cleanup.
            self._owner_creations = None
            self.user_created_object = None
            self._spell_system_states = None
            self.pre_hooks = []
            self.activation_hooks = []
            self.post_hooks = []

            self._cleaned = True
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
        frame = self.spellframe.__name__ if self.spellframe else type(self.spell).__name__
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
    def validation_result(self) -> Any:
        """
        Phase 4 validation result for this spell, if it has been computed.

        This is populated by :meth:`run_phase_validation` via :class:`SpellCrafter`.
        """
        crafter = self._crafter
        return crafter.validation_result if crafter is not None else None

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

    #region Resolution Phases (facades over SpellCrafter)
    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 – Requirements Extraction (facade).

        Delegates to :class:`SpellCrafter` to:

            - Inspect the spell’s constructor/signature and metadata.
            - Determine dependencies (spellframes, binding names, types, etc.).
            - Capture existence constraints that are relevant to resolution.

        Side effects:
            - Stores a :class:`SpellRequirements` instance inside the crafter.

        The return value is intentionally ignored at the Spell level; callers
        should access :attr:`requirements` if they need the artifact.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_requirements(cancel_event=cancel_event)

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 – Symbolic Graph Construction (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Use Phase 1 requirements to construct a per-spell symbolic graph.
            - Represent DI relationships as nodes/edges, without binding to
              concrete creations yet.

        The Spell class does not use the return value; later phases read
        artifacts via the crafter if needed.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_symbolic_graph(cancel_event=cancel_event)

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 3 – Local Resolution Frame / DAG (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Translate the symbolic graph into a concrete, per-spell
              resolution frame / local DAG.
            - Encode the order and actions required for resolution.
            - Eventually push the final DAG into this Spell via
              :meth:`_add_build_details`.

        The Spell class does not use the return value; later phases read
        artifacts via the crafter if needed.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_local_frame(cancel_event=cancel_event)

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 – Validation (facade).

        Delegates to :class:`SpellCrafter`.

        In the full implementation, this will:

            - Validate the resolution frame and requirements.
            - Populate underlying validation results.
            - Set validated/broken flags.

        The Spell class does not use the return value; callers consult
        :attr:`validated` and :attr:`is_broken`.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()
        crafter.run_phase_validation(cancel_event=cancel_event)

    def run_all_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **all compiler / resolution phases**
        (Phase 1–4) for this spell, in order.

        Currently, this means:

            1. Requirements extraction.
            2. Symbolic graph construction (placeholder).
            3. Local resolution frame / DAG (placeholder).
            4. Validation (placeholder).

        Each phase honours the optional :class:`CancellationEvent`. If the
        event is set, the underlying phase methods will raise via
        ``cancel_event.throw_if_set()``.
        """
        self.check_cleaned()
        crafter = self._ensure_crafter()

        crafter.run_phase_requirements(cancel_event=cancel_event)
        crafter.run_phase_symbolic_graph(cancel_event=cancel_event)
        crafter.run_phase_local_frame(cancel_event=cancel_event)
        crafter.run_phase_validation(cancel_event=cancel_event)


    #endregion Resolution Phases
#endregion Spell
