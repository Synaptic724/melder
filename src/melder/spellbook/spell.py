from typing import Optional, List, Any, Callable
import ulid
from threading import RLock

# Melder Imports
from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import MethodProfile, ClassProfile
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex


#region Spell
class Spell(ISpell, Cleanable):
    """
    Internal

    🪄 Represents a registered spell within the Melder system.

    A `Spell` encapsulates an instantiable or callable unit of logic (class or method)
    that can be bound, shared, and conjured via conduits within a Spellbook context.
    It includes type metadata, existence constraints, dependency information,
    and permission rules for downstream access.

    Core Responsibilities:
    - Holds an immutable reference to the object (function/class) it represents.
    - Tracks configuration data: type, profile, spellframe, ownership, and hooks.
    - Defines dependency DAGs for invocation and construction.
    - Manages permission control via the `Permissions` enum.
    - Enables hook-based lifecycle support (pre, activate, post).
    - Acts as a source of truth for spell identity and access.

    🔐 Permissions (Permissions Enum):
        - `read`: Allows other conduits to use the spell as-is, but not modify or recreate it.
        - `create`: Allows other conduits to instantiate or construct new versions.
        - `block`: Prevents external access. Internal (owner conduit) access is still allowed.

    🎯 Key Concepts:
        - Each spell has a unique SHA256 `spell_id`, generated from its signature and metadata.
        - `spellframe` distinguishes the context it was declared in (e.g., class name, Protocol, or string frame).
        - Spells may be cleaned (`cleanup()`), after which modification is disallowed.
        - Supports dependency-based object generation via a DAG executor (Resolution / Meld layer).
        - Permissions are enforced during conduit contract evaluation.

    Parameters:
        spell (Any):
            The actual object to register (function, class, or other construct).

        spell_index (SpellIndex):
            Versioned identity for this spell (current + historical fingerprints).

        spellframe (Optional[Any]):
            Frame context (usually a Protocol, class, or string) to scope the spell's identity.

        binding_name (str):
            The logical name this spell is bound to (e.g., "database", "engine").
            Normalized as part of the internal key via SpellInputUtils.

        spell_name (str):
            The actual internal name of the object or callable (for display/debugging).

        existence (Existence):
            The spell's lifecycle policy (unique, shared, etc.).

        spell_type (SpellType):
            Indicates if the spell is a class, method, lambda, or existing creation, and
            whether it participates in spellframes and/or binding names.

        profile (ClassProfile | MethodProfile):
            Captures metadata and reflection info from spell inspection.

        spell_id (str):
            Unique identifier derived from object fingerprinting (SHA256).

        permissions (Permissions):
            Defines access control level for borrowing, invoking, or recreating this spell.

        aetheric_frame (str):
            Logical Aether frame / namespace this spell was registered under.

        existing_object (Optional[object]):
            Optional pre-instantiated object to attach to the spell (EXISTING_CREATION* types).

        *args / **kwargs:
            Arbitrary tags and metadata for internal use or future extensions.

    Notes:
        - This class is never used directly by users. It is created during `bind()` and
          registered into the Spellbook and Aether.
        - Internal mutation after cleaning is disallowed.
        - Dependency graphs and resolution profiles are consumed by the Resolution / Meld
          layer; `Spell` itself does not execute resolution.
    """

    def __init__(
            self,
            spell: Any,
            spell_index: SpellIndex,
            spellframe: Optional[Any],
            binding_name: str,
            spell_name: str,
            existence: Existence,
            spell_type: SpellType,
            profile: ClassProfile | MethodProfile,
            spell_id: str,
            permissions: Permissions,
            aetheric_frame: str,
            existing_object: object = None,
            *args,
            **kwargs
    ):
        super().__init__()
        self._lock = RLock()
        self._id: str = str(ulid.ULID())  # Unique internal ID for tracking

        # Spell Data
        self.spell_index: SpellIndex = spell_index
        self.spell = spell  # Object reference
        self.spell_id: str = spell_id  # SHA256 unique identifier
        self.spellframe: Optional[Any] = spellframe
        self.spell_type: SpellType = spell_type
        self.user_created_object: object = existing_object
        self.binding_name: str = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence
        self.profile: ClassProfile | MethodProfile = profile
        self.aetheric_frame: str = aetheric_frame
        self.timeout: Optional[int] = None  # Optional timeout for spell execution
        self.retries: int = 0  # Number of retries allowed for spell execution

        # Permissions
        self.permissions: Permissions = permissions

        # Spell Metadata
        self.tags = args if args else []
        self.metadata = kwargs if kwargs else {}

        # hooks
        self.pre_hooks: List[Callable] = []
        self.activation_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []

        # Created During validation / graph construction
        self.dependency_graph = None
        self.dependencies: List[str] = []  # SHA256 spell IDs required for this spell to function

        # Optional resolution profile (DI contract), to be populated by SpellCrafter.
        self.resolution_profile: Any = None

        # Created after Conduit Made (ownership / scope integration)
        self._owner_conduit_id: str | None = None
        self._owner_conduit_name: str | None = None
        self.owned_spell = None
        self._owner_creations: Any = None  # Scope level creations for singletons

        # Key for the spell in the Spellbook (normalized)
        frame_key, bind_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=self.spellframe,
            spell_name=self.spell_name,
            binding_name=self.binding_name,
        )
        self._key = (frame_key, bind_key)

    #region Disposal
    def cleanup(self):
        """
        Cleans up the spell, preventing any further modifications.

        This:
        - Disposes the static dependency graph if one was attached and exposes a `dispose()` method.
        - Clears references to owner creations and user_created_object.
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
                dg.dispose()

            # Drop references to help GC and enforce immutability after cleanup.
            self._owner_creations = None
            self.user_created_object = None
            self.pre_hooks = []
            self.activation_hooks = []
            self.post_hooks = []

            self._cleaned = True
    #endregion Disposal

    #region Context Manager
    def __enter__(self):
        """
        Enters the context manager for Aether-related operations.

        This is mainly useful for internal configuration phases where multiple attributes
        (hooks, metadata, etc.) are being attached under the same lock.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context manager for Aether-related operations.
        """
        self._lock.release()
    #endregion Context Manager

    def __repr__(self):
        frame = self.spellframe.__name__ if self.spellframe else type(self.spell).__name__
        return (
            f"Spell(name={self.spell_name}, binding={self.binding_name or '__default__'}, "
            f"frame={frame}, SHA256={self.spell_id})"
        )

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
    #endregion Introspection Helpers

    #region Existing Object Transfer
    def take_existing_object(self) -> object | None:
        """
        Internal

        Atomically detach and return the existing object associated with this spell.

        This is the main hook used by Conduit / ResolutionFrame when materializing
        a Creation for an EXISTING_CREATION* spell:

            existing = spell.take_existing_object()
            creation = Creation(..., instance=existing, ...)

        Semantics:
            - Only valid for EXISTING_CREATION* SpellTypes (see `is_existing_creation`).
            - After this call, the Spell no longer owns the instance; it is expected
              to live inside a Creation / scope container.
            - Multiple calls are allowed; subsequent calls will return None.

        Returns:
            object | None:
                The detached existing object if it was present, otherwise None.

        Raises:
            RuntimeError:
                If called on a non-EXISTING_CREATION spell.
        """
        if not self.is_existing_creation:
            raise RuntimeError(
                "take_existing_object() is only valid for EXISTING_CREATION spells."
            )

        with self._lock:
            existing = self.user_created_object
            self.user_created_object = None
            return existing
    #endregion Existing Object Transfer

    #region Configuration
    def _add_owned_conduit(self, conduit_id: str, conduit_name: str = None, creations: Any = None):
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

    def _add_build_details(self, dag: Any, dependencies: List[str] = None):
        """
        Internal

        Attach static build-time dependency graph details to this spell.

        This is typically invoked by the SpellCrafter / DAG builder after it has
        analyzed the spell's parameters and constructed a dependency DAG.

        Args:
            dag (Any):
                A static DAG representation for this spell's dependency structure.
                This object is considered immutable at runtime and may expose a
                `dispose()` method for cleanup.
            dependencies (List[str]):
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

    #region Casting
    def cast(self) -> object:
        """
        Internal (Legacy Placeholder)

        Casts the spell.

        This method is intentionally **not implemented** in the new architecture.
        All resolution is handled via the Resolution / Meld pipeline using
        `SpellResolutionProfile` + `ResolutionFrame`.

        Notes:
            - Existing-creation spells are surfaced directly by Meld using
              `user_created_object` / `take_existing_object()`.
            - Class and method spells are instantiated/invoked by the resolution
              engine, not by this method.

        Raises:
            NotImplementedError: Always. This method is a legacy placeholder and
            should not be used.
        """
        raise NotImplementedError("Spell.cast() is not used; resolution is handled by Meld/ResolutionFrame.")
    #endregion Casting

#endregion Spell
