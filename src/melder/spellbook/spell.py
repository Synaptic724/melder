from uuid import UUID
from typing import Optional, List, Any, Callable
import ulid
from threading import RLock

# Melder Imports
from melder.aether.conduit.spell_crafter.inspector.spell_examiner import MethodProfile, ClassProfile
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions

#region Spell
class Spell(ISpell):
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
        - `spellframe` distinguishes the context it was declared in (e.g., class name).
        - Spells may be sealed (`seal()`), after which modification is disallowed.
        - Supports dependency-based object generation via a DAG executor.
        - Permissions are enforced during conduit contract evaluation.

    Parameters:
        spell (Any):
            The actual object to register (function, class, or other construct).

        spellframe (Optional[Any]):
            Frame context (usually a class or module) to scope the spell's identity.

        binding_name (str):
            The logical name this spell is bound to (e.g., "database", "engine").

        spell_name (str):
            The actual internal name of the object or callable (for display/debugging).

        existence (Existence):
            The spell's lifecycle policy (singleton, transient, etc.).

        spell_type (SpellType):
            Indicates if the spell is a class, method, or other construct.

        profile (ClassProfile | MethodProfile):
            Captures metadata and reflection info from spell inspection.

        spell_id (str):
            Unique identifier derived from object fingerprinting.

        permissions (Permissions):
            Defines access control level for borrowing, invoking, or recreating this spell.

        existing_object (Optional[object]):
            Optional pre-instantiated object to attach to the spell.

        *args / **kwargs:
            Arbitrary tags and metadata for internal use or future extensions.

    Notes:
        - This class is never used directly by users. It is created during `bind()` and
          registered into the Spellbook and Aether.
        - Internal mutation after sealing is disallowed.
        - Dependency graphs and hooks must be defined prior to casting.
    """

    def __init__(
            self,
            spell: Any,
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
        self._id: str = str(ulid.ULID()) # Unique internal ID for tracking

        # Spell Data
        self.spell = spell #Object reference
        self.spell_id: str = spell_id
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

        # Created During validation
        self.dependency_graph = None
        self.dependencies: List[str] = []  # SHA256 spell IDs required for this spell to function

        # Created after Conduit Made
        self._owner_conduit_id: UUID | None = None
        self._owner_conduit_name: str | None = None
        self.owned_spell = None
        self._owner_creations: Any = None # Scope level creations for singletons

        # Key for the spell in the Spellbook
        self._key = (self.spellframe or type(self.spell).__name__, self.binding_name or "__default__")

    #region Disposal
    def seal(self):
        """
        Seals the spell, preventing any further modifications.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self.dependency_graph.dispose()
            self._sealed = True
    #endregion Disposal

    def __repr__(self):
        frame = self.spellframe.__name__ if self.spellframe else type(self.spell).__name__
        return (
            f"Spell(name={self.spell_name}, binding={self.binding_name or '__default__'}, "
            f"frame={frame}, SHA256={self.spell_id})"
        )

    #region Configuration
    def _add_owned_conduit(self, conduit_id: UUID, conduit_name: str = None, creations: Any = None):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        with self._lock:
            self._owner_conduit_id = conduit_id
            self._owner_conduit_name = conduit_name
            self.owned_spell = True
            self._owner_creations = creations

    def _add_build_details(self, dag: Any, dependencies: List[str] = None):
        """
        Add details to the spell.
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
        Casts the spell.
        This is a placeholder for the actual casting logic.
        """
        raise NotImplementedError("Not implemented.")
        with self._lock:
            if self._sealed:
                raise RuntimeError("Spell is sealed and cannot be cast.")
            # Implement the actual casting logic here
            if self.user_created_object:
                # If an existing object is provided, use it
                return self.user_created_object
            else:
                return self.dependency_graph.execute()

#endregion Casting
#endregion Spell