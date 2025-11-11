from threading import RLock
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable


@runtime_checkable
class ICleanable(Protocol):
    """
    Protocol definition for Cleanable.

    This protocol mirrors the public API of the Cleanable
    abstract base class.
    """

    _cleaned: "bool"

    @property
    def cleaned(self) -> "bool":
        """Returns True if the object has already been cleaned."""
        ...

    @property
    def is_cleaned(self) -> "bool":
        """Alias for `cleaned`."""
        ...

    def check_cleaned(self) -> "None":
        """
        Check if the object has been cleaned.

        Raises:
            RuntimeError: If the object has already been cleaned.
        """
        ...

    def cleanup(self) -> "None":
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...

    async def async_cleanup(self) -> "None":
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...

@runtime_checkable
class ISealable(Protocol):
    """
    ISealable
    -----------
    An Interface for all Sealable objects in the system.

    Objects that manage runtime, memory, open resources, or registration
    must implement this interface.

    Supports context-manager usage:
        with MyObject(...) as obj:
            ...
        # seal() is called automatically on exit.

    Contract:
    ---------
    - `seal()` must be safe to call multiple times.
    - All sealing must set `_sealed = True` when sealing completes.
    """

    _sealed: bool

    @property
    def sealed(self) -> bool:
        """Returns True if the object has already been sealed."""
        ...

    @property
    def is_sealed(self) -> bool:
        """Alias for `sealed`."""
        ...

    def check_sealed(self):
        """
        Check if the object has been sealed.

        Raises:
            RuntimeError: If the object has already been sealed.
        """
        ...

    def seal(self):
        """
        Seal must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...

    async def async_seal(self):
        """
        Seal must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...



@runtime_checkable
class ICreations(ISealable, Protocol):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon sealing.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ISealable` or configured cleanup methods.
    """

    # -----------------
    # Attributes
    # -----------------
    _lock: RLock
    _unique: 'ConcurrentDict[str, object]'
    _unique_per_scope: 'ConcurrentDict[str, object]'
    _many: 'ConcurrentDict[str, ConcurrentList[object]]'
    _unique_per_lineage: 'ConcurrentDict[str, object]'
    _unique_per_cluster: 'ConcurrentDict[str, object]'
    _disposal_enabled: bool
    _disposal_method_names: List[str]
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _seal_unique(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _seal_unique_per_lineage(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_lineage` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _seal_unique_per_cluster(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_cluster` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _seal_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _seal_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["seal", "cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Notes:
          - No Protocol/type checks are performed.
          - Cleanup semantics are entirely defined by the configured method list.

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def _upgrade_from_lesser_conduit(self, **kwargs: Any) -> None:
        """
        Internal

        Transfers creations data from a `LesserCreations` instance during a conduit upgrade.

        Args:
            **kwargs: Dictionary containing creation scopes (e.g., `unique_per_scope`, `many`).

        Raises:
            RuntimeError: If the `Creations` manager already contains objects before transfer.
        """
        ...

    def add_unique(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique` scope.
        """
        ...

    def add_unique_per_lineage(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_lineage` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_lineage` scope.
        """
        ...

    def add_unique_per_cluster(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_cluster` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_cluster` scope.
        """
        ...

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        ...

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is sealed.
        """
        ...


@runtime_checkable
class ILesserCreations(ISealable, Protocol):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    # -----------------
    # Attributes
    # -----------------
    _unique_per_scope: 'ConcurrentDict[str, object]'
    _many: 'ConcurrentDict[str, ConcurrentList[object]]'
    _disposal_enabled: bool
    _disposal_method_names: List[str]
    _lock: RLock
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _seal_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _seal_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["seal", "cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def transfer_data_and_clear(self) -> Dict[str, Any]:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and seals the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        ...

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        ...

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is sealed.
        """
        ...


@runtime_checkable
class ISpell(ISealable, Protocol):
    """
    An Interface defining the shape of a 'Spell', a unit of logic that can be cast.

    This represents the blueprint for a service, component, or function that
    can be managed by the melder system.

    Attributes:
        post_hooks (Optional[Any]): A list of callables to run after the spell is cast.
        activation_hooks (Optional[Any]): A list of callables to run during casting.
        pre_hooks (Optional[Any]): A list of callables to run before casting.
        _owner_conduit_id (Optional[str]): The id of the Conduit that owns this spell.
        _permissions (Optional[Any]): The permissions object governing this spell's
            accessibility.
    """
    post_hooks: Optional[Any]
    activation_hooks: Optional[Any]
    pre_hooks: Optional[Any]
    _owner_conduit_id: Optional[str]
    _permissions: Optional[Any]
    _id: str

    def add_spell_details(self, *args, **kwargs):
        """
        Attaches detailed configuration or metadata to the spell.

        Args:
            *args: Positional arguments for configuration.
            **kwargs: Keyword arguments, often used for specific details like
                      'dependency_graph' or 'existing_object'.
        """
        ...

    def _add_owned_conduit(self, conduit_id: str, conduit_name: str = None, creations: Any = None):
        """
        Assigns ownership of this spell to a specific Conduit.

        Args:
            conduit_id (str): The unique ID of the owning Conduit.
            conduit_name (str, optional): The human-readable name of the owning Conduit.
        """
        ...

    def _add_dag(self, dag: Any):
        """
        Attaches the resolved dependency graph (DAG) to the spell.

        Args:
            dag (Any): The dependency graph object required to cast this spell.
        """
        ...

    def cast(self):
        """
        Executes the spell's logic and returns the resulting object or value.
        """
        ...

@runtime_checkable
class ISpellbook(ISealable, Protocol):
    """
    An Interface for a 'Spellbook', the central registry and configuration manager
    for all spells within a Conduit.

    It behaves as the primary interface for binding, resolving, and configuring
    the spells available in its scope.

    Attributes:
        _lookup_contracted_spells (Optional[Any]): Internal lookup for borrowed spells.
        _lookup_spells (Optional[Any]): Internal lookup for owned spells.
        _contracted_spells (Optional[Any]): Storage for borrowed spells.
        _spells (Optional[Any]): Storage for spells owned by this spellbook.
        _bind (Optional[Any]): The internal binding mechanism.
    """
    _lookup_contracted_spells: Optional[Any]
    _lookup_spells: Optional[Any]
    _contracted_spells: Optional[Any]
    _spells: Optional[Any]
    _bind: Optional[Any]
    _id: str

    def _lesser_conduit_spellbook_copy(self) -> 'ISpellbook':
        """
        Creates a copy of the spellbook for use in a new lesser (child) conduit.

        Returns:
            ISpellbook: A new spellbook instance configured for a lesser conduit.
        """
        ...

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Finds the unique spell_id (SHA256 hash) for a spell.

        Args:
            spellframe: The logical grouping or interface of the spell.
            spell_name: The concrete name of the spell class/function.
            binding_name: The user-provided unique name for this binding.

        Returns:
            Optional[str]: The unique spell_id if found, otherwise None.
        """
        ...

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Finds the internal lookup key (tuple) for a spell.

        Args:
            spellframe: The logical grouping or interface of the spell.
            spell_name: The concrete name of the spell class/function.
            binding_name: The user-provided unique name for this binding.

        Returns:
            Optional[tuple]: The internal lookup key if found, otherwise None.
        """
        ...

    def inspect_spell(self, spell: Any, aetheric_frame: str = "default") -> Optional[str]:
        """
        Inspects an object to find its spell_id and checks if it exists in the Aether.

        Args:
            spell (Any): The spell object or class to inspect.
            aetheric_frame (str, optional): The Aetheric Frame to search within.

        Returns:
            Optional[str]: The spell_id if the spell is found in the registry.
        """
        ...


    def bind(self, spell, existence: 'Existence', *, permissions: str = "create", spellframe=None, binding_name=None,
             **kwargs) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder’s system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        ──────────────────────────────────────────────
        🧠 Binding Overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell into the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to *use* the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use *and* create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        📦 Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        🔑 Binding Name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        ──────────────────────────────────────────────
        🪝 Lifecycle Hooks (optional `**kwargs`):

            - `pre_hooks`: List[Callable]
                Executed *before* the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: List[Callable]
                Executed *during* spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: List[Callable]
                Executed *after* the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            ⚠️ All hooks must be callables.

        ──────────────────────────────────────────────
        Parameters:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs:
                - pre_hooks: Optional[List[Callable]]
                - activation_hooks: Optional[List[Callable]]
                - post_hooks: Optional[List[Callable]]

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        ...

    def remove_bind(self, spell: Any):
        """
        Removes a spell blueprint from this spellbook.

        Args:
            spell (Any): The spell object or class to remove.
        """
        ...

    def _find_spell(self, spell_id: str) -> Optional[Any]:
        """
        Internal method to resolve a spell blueprint directly by its ID.

        Args:
            spell_id (str): The unique spell_id (SHA256 hash).

        Returns:
            Optional[Any]: The spell object if found.
        """
        ...

    def conjure(self, policy: Optional[str], name: str = None) -> Any:
        """
        Finalizes the spellbook configuration and conjures its governing Conduit.

        This locks the spellbook's configuration and creates the live
        execution scope (Conduit) that this spellbook defines.

        Args:
            policy (Optional[str]): The policy for the new Conduit (e.g., "automatic", "dynamic").
            name (str, optional): An optional name for the Conduit.

        Returns:
            Any: The newly created Conduit instance.
        """
        ...

    def get_configuration(self) -> 'Configuration':
        """
        Retrieves the configuration object associated with this spellbook.

        Returns:
            Configuration: The configuration instance.
        """
        ...

    def configure_conduit_state(self, **kwargs):
        """
        Applies settings to the spellbook's configuration before it is locked.

        Args:
            **kwargs: Configuration keys and values to set.
        """
        ...

    def lock_configuration(self):
        """
        Locks the spellbook's configuration, preventing further changes.
        """
        ...

    def is_configuration_locked(self) -> bool:
        """
        Checks if the spellbook's configuration is locked.

        Returns:
            bool: True if locked, False otherwise.
        """
        ...

    def create_new_preset_spellbook(self):
        """
        Creates a new spellbook, typically for upgrading a lesser conduit.
        """
        ...

    def get_spell_details(self, spell_id):
        """
        Retrieves the detailed profile for a registered spell.

        Args:
            spell_id (str): The unique spell_id.
        """
        ...

    def _add_contracted_spell(self, spell, conduit_id):
        """
        Internal: Adds a borrowed (contracted) spell to the spellbook.

        Args:
            spell (Any): The spell object.
            conduit_id (str): The ID of the Conduit providing the spell.
        """
        ...

    def _create_link_contract(self, _id):
        """
        Internal: Initializes the storage for a new contract.

        Args:
            _id (str): The ID of the peer conduit.
        """
        ...

    def _sever_link_contract(self, _conduit_id):
        """
        Internal: Removes a contract and all associated borrowed spells.

        Args:
            _conduit_id (str): The ID of the peer conduit to sever ties with.
        """
        ...

    def _inspect_spell_using_aetheric_frame(self, spell, aetheric_frame):
        """
        Internal: Inspects a spell within the context of a specific Aetheric Frame.

        Args:
            spell (Any): The spell object.
            aetheric_frame (str): The frame to search within.
        """
        ...

    def _remove_contracted_spell(self, spell_id, conduit_id):
        """
        Internal: Removes a single borrowed spell from a contract.

        Args:
            spell_id (str): The ID of the spell to remove.
            conduit_id (str): The ID of the peer conduit.
        """
        ...

    def _clear_contracted_spells_for_conduit(self, conduit_id):
        """
        Internal: Clears all borrowed spells from a specific peer conduit.

        Args:
            conduit_id (str): The ID of the peer conduit.
        """
        ...

    def _find_contracted_spell(self, spell_id):
        """
        Internal: Finds a borrowed spell by its ID.

        Args:
            spell_id (str): The unique spell_id.
        """
        ...

@runtime_checkable
class IBind(ISealable, Protocol):
    """
    An Interface for a binding mechanism, responsible for profiling and
    registering a spell blueprint.
    """
    _id: str
    def bind(self, permissions: 'Permissions', *, aetheric_frame: str, spell=None, spellframe=None, name=None,
             existence='Existence.unique') -> 'Union["ISpell", Any]':
        """
        Binds a spell, creating its blueprint and returning it.

        Args:
            permissions (Permissions): The access policy for the spell.
            aetheric_frame (str): The Aetheric Frame this bind is part of.
            spell (Any, optional): The class, function, or object to bind.
            spellframe (Any, optional): The logical interface or group.
            name (str, optional): A unique binding name.
            existence (str, optional): The lifecycle policy.

        Returns:
            Union[ISpell, Any]: The newly created ISpell blueprint.
        """
        ...

@runtime_checkable
class IMeld(ISealable, Protocol):
    """
    An Interface for the object resolution (melding) process.

    This is responsible for taking a spell request, resolving its dependencies,
    and "casting" it into a live object instance.
    """
    _id: str
    def meld(self, spell, *, spellframe=None, name=None, spell_override: Optional[Dict[str, Any]] = None):
        """
        Resolves and creates an instance of a spell.

        Args:
            spell (Any): The spell to resolve (e.g., by class, name, or ID).
            spellframe (Any, optional): The logical interface to resolve against.
            name (str, optional): The unique binding name to resolve.
            spell_override (Optional[Dict[str, Any]], optional): A dictionary
                of dependencies to override for this cast only.
        """
        ...
@runtime_checkable
class IConduitWard(ISealable, Protocol):
    """
    An Interface for a 'ConduitWard', managing links, policies, and contracts
    between its Conduit and other Conduits.

    Attributes:
        _contracts (Optional[Any]): Storage for active contracts.
        _lock (Optional[Any]): The concurrency lock.
        _received_index (Optional[Any]): Index of incoming links.
        _policy (Optional[Any]): The active access policy.
        _id (Optional[str]): The ID of the Conduit this ward protects.
        _conduit (Optional['IConduit']): A reference to the Conduit itself.
    """
    _contracts: Optional[Any]
    _lock: Optional[Any]
    _received_index: Optional[Any]
    _policy: Optional[Any]
    _id: str
    _conduit: Optional['IConduit']
    @property
    def policy(self) -> 'IPolicy':
        """
        The current access control policy for this Conduit.
        """
        ...

    @policy.setter
    def policy(self, value: 'IPolicy'):
        """
        Sets the access control policy for this Conduit.
        """
        ...

    @property
    def conduit_type(self) -> 'ConduitState':
        """
        The current state of the Conduit (e.g., 'normal', 'lesser').
        """
        ...

    def _change_conduit_type(self, conduit_type: 'ConduitState'):
        """
        Internal: Changes the state of the Conduit.

        Args:
            conduit_type (ConduitState): The new state.
        """
        ...

    def remove_link(self, other_conduit):
        """
        Removes a link between this Conduit and another.

        Args:
            other_conduit (Any): The peer Conduit to unlink from.
        """
        ...

    def get_links(self):
        """
        Retrieves a list of all active links (contracts) with peer Conduits.

        Returns:
            A list of active links.
        """
        ...

    def _remove_contract(self, _conduit):
        """
        Internal: Removes a specific contract.

        Args:
            _conduit (Any): The peer Conduit whose contract should be removed.
        """
        ...

@runtime_checkable
class IConduit(ISealable, Protocol):
    """
    An Interface for a 'Conduit', the core execution scope and object factory.

    It owns a Spellbook (its registry) and a ConduitWard (its security)
    and is responsible for "melding" (creating) objects.

    Attributes:
        _conduit_state (Optional[Any]): The current state (e.g., 'normal', 'lesser').
        _conduit_ward (IConduitWard): The ward managing its links and policies.
        _spellbook (ISpellbook): The registry of spells available to this conduit.
    """
    _conduit_state: Optional[Any]
    _conduit_ward: IConduitWard
    _spellbook: ISpellbook
    _aetheric_frame : str
    _id: str

    @property
    def name(self) -> Optional[str]:
        """
        The human-readable name of the Conduit this ward protects.
        """
        ...

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the human-readable name of the Conduit this ward protects.
        """
        ...

    def link(self, target_conduit: 'IConduit') -> bool:
        """
        Establishes a contract link with another Conduit (in 'dynamic' mode).

        Args:
            target_conduit (IConduit): The peer Conduit to link with.

        Returns:
            bool: True if linking was successful.
        """
        ...

    def meld(self, spell_name: str, spell_type: str, spellframe: Type = None):
        """
        Resolves and creates an instance of a spell from this Conduit's scope.

        Args:
            spell_name (str): The name of the spell to resolve.
            spell_type (str): The type of spell (e.g., 'class', 'method').
            spellframe (Type, optional): The logical interface to resolve against.
        """
        ...

    def create_lesser_conduit(self):
        """
        Creates a new, lightweight child scope (lesser conduit).

        Returns:
            A new IConduit instance in the 'lesser' state.
        """
        ...

    def check_spell_id(self, spell_id, aetheric_frame):
        """
        Checks if a spell_id exists within a given Aetheric Frame.

        Args:
            spell_id (str): The unique spell_id.
            aetheric_frame (str): The frame to search within.
        """
        ...

    def inspect_spell(self, spell, aetheric_frame):
        """
        Inspects an object to find its spell_id within a given frame.

        Args:
            spell (Any): The spell object.
            aetheric_frame (str): The frame to search within.
        """
        ...

    def get_spell_by_id(self, spell_id, aetheric_frame):
        """
        Retrieves a spell blueprint by its ID from a given frame.

        Args:
            spell_id (str): The unique spell_id.
            aetheric_frame (str): The frame to search within.
        """
        ...

    def get_conduit_by_id(self, conduit_id, aetheric_frame):
        """
        Retrieves a peer Conduit by its ID from a given frame.

        Args:
            conduit_id (str): The unique ID of the Conduit.
            aetheric_frame (str): The frame to search within.
        """
        ...


class ILink(ISealable, Protocol):
    """
    An Interface representing a live connection (contract) between two Conduits.
    """
    _id: str
    def sever(self):
        """
        Severs the link, dissolving the contract between the two Conduits.
        """
        ...


class IDetail(ISealable, Protocol):
    """
    An Interface for a 'Detail', a single permission or rule within a Contract.
    """
    _id: str
    @property
    def type(self) -> 'ContractTypes':
        """
        The type of contract detail (e.g., 'grant', 'borrow').
        """
        ...

    def affects_permissions(self) -> bool:
        """
        Checks if this detail modifies spell permissions.

        Returns:
            bool: True if this detail grants or revokes spell access.
        """
        ...


class IConduitCloud(ISealable, Protocol):
    """
    An Interface for an abstract factory for named conduits.

    The ConduitCloud provides a central location to retrieve conduits by a
    human-readable name, intended for top-level access in
    highly dynamic systems.
    """
    _id: str

    def get_conduit(self, name: str) -> IConduit:
        """
        Retrieves a conduit by its registered name.

        Args:
            name (str): The unique name of the conduit.

        Returns:
            IConduit: The conduit instance.

        Raises:
            RuntimeError: If the ConduitCloud is sealed.
            ValueError: If a conduit with that name is not found.
        """
        ...

    def _register_conduit(self, conduit: IConduit):
        """
        Registers a named conduit into the cloud. (Internal use)

        Args:
            conduit (IConduit): The conduit instance to register.

        Raises:
            ValueError: If the conduit's name is None or already exists
                in the registry.
        """
        ...


class IAethericFrame(ISealable, Protocol):
    """
    An Interface for an isolated "universe" or "frame" within the Aether.

    An AethericFrame holds all top-level conduits, spell registries, and
    configurations for a specific, isolated domain.

    Attributes:
        name (str): The unique name of this frame.
        _configuration (Optional[Any]): The frozen configuration for this frame.
        _conduit_cloud (IConduitCloud): The abstract factory for named conduits.
        _conduits (ConcurrentDict[str, IConduit]): Stores all root conduits.
        _spell_registry (ConcurrentDict[str, ConcurrentSet[str]]): Maps
            conduit ids to their owned spell IDs.
        _conduit_clusters (ConcurrentDict[str, ConcurrentList[str]]): Organizes
            conduits into named groups.
    """
    name: str
    _id: str
    _configuration: Optional[Any]  # Use 'Configuration' if it's a known type
    _conduit_cloud: IConduitCloud
    _conduits: 'ConcurrentDict[str, IConduit]'
    _spell_registry: 'ConcurrentDict[str, ConcurrentSet[str]]'
    _conduit_clusters: 'ConcurrentDict[str, ConcurrentList[str]]'

@runtime_checkable
class IAether(ISealable, Protocol):
    """
    An Interface for the global singleton that holds and manages all AethericFrames.

    Aether is the top-level "universe" of the melder system and acts as the
    central service provider for other internal components of the library.
    """

    def _bind_configuration(self, configuration: Any, aetheric_frame_name: str = "default") -> None:
        """
        Binds a configuration object to a specific Aetheric Frame.

        Args:
            configuration: The configuration object to bind.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_configuration(self, aetheric_frame_name: str = "default") -> Optional[Any]:
        """
        Retrieves the configuration object from a specific Aetheric Frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            The configuration object, or None if not set.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _register_conduit_cloud(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Registers a conduit with the ConduitCloud of a specific frame.

        Args:
            conduit: The conduit to register.
            aetheric_frame_name: The name of the frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Retrieves the ConduitCloud instance from a specific frame.

        Args:
            aetheric_frame_name: The name of the frame.

        Returns:
            IConduitCloud: The ConduitCloud for that frame.

        Raises:
            ValueError: If the specified frame does not exist.
        """
        ...

    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its name.

        Args:
            name (str): The name of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _get_conduit_by_id(self, signature: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds a root conduit within a frame by its id.

        Args:
            signature (str): The id of the conduit.
            aetheric_frame_name (str): The name of the frame to search in.

        Returns:
            IConduit: The found conduit.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _add_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Adds a new root conduit to a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID already exists.
        """
        ...

    def _remove_conduit(self, conduit: IConduit, aetheric_frame_name: str = "default"):
        """
        Removes a root conduit from a frame. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit is not found.
        """
        ...

    def _create_cluster(self, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Creates a new conduit cluster within a frame. (Internal use)

        Args:
            cluster_name (str): The name for the new cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the cluster name is taken.
        """
        ...

    def _add_conduit_to_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Adds a conduit's str to a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to add.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _remove_conduit_from_cluster(self, conduit: IConduit, cluster_name: str, aetheric_frame_name: str = "default"):
        """
        Removes a conduit's str from a cluster. (Internal use)

        Args:
            conduit (IConduit): The conduit to remove.
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduits_in_cluster(self, cluster_name: str, aetheric_frame_name: str = "default") -> 'ConcurrentList[str]':
        """
        Gets a list of all conduit id in a specific cluster.

        Args:
            cluster_name (str): The name of the cluster.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            ConcurrentList[str]: A list of conduit ids.

        Raises:
            ValueError: If the frame or cluster does not exist.
        """
        ...

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> IConduit:
        """
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            IConduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        """
        ...

    def _check_for_spell(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Checks if a spell ID is registered in any conduit within a frame.

        Args:
            spell_id (str): The spell ID to check.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            bool: True if the spell exists, False otherwise.

        Raises:
            ValueError: If the frame does not exist.
        """
        ...

    def _add_spells_to_aether(self, conduit_id: str, spell_set: 'ConcurrentSet[str]', aetheric_frame_name: str = "default"):
        """
        Registers a set of spell IDs as being owned by a specific conduit.

        Args:
            conduit_id (str): The id of the owning conduit.
            spell_set (ConcurrentSet[str]): A set of spell IDs to register.
            aetheric_frame_name (str): The name of the frame.

        Raises:
            ValueError: If the frame does not exist or the conduit ID is
                already registered.
        """
        ...

    def seal_aetheric_frames(self):
        """
        Seals all aetheric frames and their contents.
        """
        ...

@runtime_checkable
class IChannelLogger(ICleanable, Protocol):
    """
    ChannelLogger
    -------------
    Concurrency-safe facade over one or more Python `logging.Logger` instances,
    registered to IRIS channels. Emits a single `LogRecord` per call, forwards it
    to all configured loggers, then notifies IRIS subscribers.

    This version adds **local state controls** so each ChannelLogger can be
    independently enabled/disabled and filtered by a minimum level, with
    optional **overrides** that can be imposed by a higher-level controller.

    Additions:
    - **groups** (membership): `ConcurrentSet[str]` of tokens (e.g., "SYSTEM", "PIPELINE_A").
      Snapshot is attached to each record as `record.groups` (List[str]).
    - **properties** (key/value): `ConcurrentDict[str, Any]` of flat scalars you want
      stamped on every record (e.g., small IDs/flags). Snapshot is attached to each
      record as `record.properties` (Dict[str, Any]).
      (Thread/agent fields from `ContextFilter` are still injected separately.)
    - **state**:
        * `enabled` (bool): default, local on/off switch.
        * `min_level` (int): default local minimum level (e.g., `logging.INFO`).
        * `override_enabled` (Optional[bool]): if set, takes precedence over `enabled`.
        * `override_min_level` (Optional[int]): if set, takes precedence over `min_level`.

    Snapshot semantics:
    - On emit, the logger captures *current* groups/properties under lock and
      attaches those snapshots to the `LogRecord`. Mutations after that do not
      affect the already-created record.
    """
    _id: str
    @property
    def id(self) -> str:
        """
        Get the unique ID of this ChannelLogger.

        Returns:
            str: The ID assigned at construction.
        """
        ...

    @property
    def last_log_time(self) -> float:
        """
        Get the UNIX timestamp of the last emitted (accepted) log call for this ChannelLogger.

        Returns:
            float: Seconds since the epoch for the last accepted record emit attempt.
        """
        ...

    @property
    def name(self) -> str:
        """
        Get the name of this ChannelLogger.

        Returns:
            str: The name assigned at construction.
        """
        ...

    # ===== Channels =====
    def add_channel(self, channel_name: str) -> None:
        """
        Route this ChannelLogger to an additional IRIS channel.

        Creates/attaches the child logger under the channel's parent logger name
        (e.g., "Iris.<console>.<{registrant}>") and records the routing in
        self._channels / self._loggers.
        """
        ...

    def remove_channel(self, channel_name: str) -> bool:
        """
        Stop routing this ChannelLogger to a specific IRIS channel.

        We detect the child logger(s) to drop by inspecting their *parent* logger’s
        monkey-patched attribute `_command_ops_name`, which IrisChannel sets when
        constructing the parent (e.g., "console").
        """
        ...

    # ===== State (enabled/min level/overrides) =====
    def set_enabled(self, value: bool) -> None:
        """
        Set the local enabled flag.

        Args:
            value: True to enable locally, False to disable locally.

        Notes:
            - If `override_enabled` is set (not None), it *overrides* this local flag.
            - Use `get_effective_enabled()` to read the computed effective state.
        """
        ...

    def get_enabled(self) -> bool:
        """
        Get the current local enabled flag (ignoring overrides).

        Returns:
            bool: The local `enabled` setting.
        """
        ...

    def set_override_enabled(self, value: Optional[bool]) -> None:
        """
        Set or clear the override for the enabled flag.

        Args:
            value: True/False to force enabled/disabled; None to remove the override.

        Notes:
            - When not None, `override_enabled` takes precedence over the local `enabled`.
        """
        ...

    def clear_override_enabled(self) -> None:
        """
        Clear the enabled override, reverting to the local `enabled` flag.
        """
        ...

    def get_override_enabled(self) -> Optional[bool]:
        """
        Get the current override for the enabled flag.

        Returns:
            Optional[bool]: The `override_enabled` value (True/False), or None if unset.
        """
        ...

    def get_effective_enabled(self) -> bool:
        """
        Compute the effective enabled state for this ChannelLogger.

        Returns:
            bool: `override_enabled` if set; otherwise the local `enabled` flag.
        """
        ...

    def set_min_level(self, level: str) -> None:
        """
        Set the local minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET   (0):    Special value; if used as a threshold it effectively lets everything through.
            - DEBUG    (10):   Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO     (20):   High-level operational events (what the system is doing).
            - WARNING  (30):   Something unexpected or suboptimal happened, but the system can continue.
            - ERROR    (40):   A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50):   The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level name (e.g., "INFO").

        Notes:
            - Records with a level *below* the effective min level are dropped.
            - If `override_min_level` is set, it takes precedence.
        """
        ...

    def get_min_level(self) -> int:
        """
        Get the current local minimum logging level (ignoring overrides).

        Returns:
            int: The local `min_level` integer.
        """
        ...

    def set_override_min_level(self, level: Optional[str]) -> None:
        """
        Set or clear the override for the minimum logging level.

        Level Reference (standard `logging` levels):
            - NOTSET   (0):    Special value; if used as a threshold it effectively lets everything through.
            - DEBUG    (10):   Detailed diagnostic information useful for development and deep troubleshooting.
            - INFO     (20):   High-level operational events (what the system is doing).
            - WARNING  (30):   Something unexpected or suboptimal happened, but the system can continue.
            - ERROR    (40):   A failure occurred for the current operation; the system may still be running.
            - CRITICAL (50):   The system is in a bad state and may require immediate attention / shutdown.

        Args:
            level: A standard logging level integer (e.g., `INFO`), or None to clear the override.

        Notes:
            - When not None, `override_min_level` takes precedence over local `min_level`.
        """
        ...

    def clear_override_min_level(self) -> None:
        """
        Clear the min-level override, reverting to the local `min_level`.
        """
        ...

    def get_override_min_level(self) -> Optional[int]:
        """
        Get the current override for the minimum logging level.

        Returns:
            Optional[int]: The `override_min_level` value, or None if unset.
        """
        ...

    def _effective_min_level(self) -> int:
        """
        Compute the effective minimum logging level for this ChannelLogger.

        Returns:
            int: `override_min_level` if set; otherwise the local `min_level`.
        """
        ...

    def _should_emit(self, record_level: int) -> bool:
        """
        Decide whether a record at `record_level` should be emitted given current state.

        Args:
            record_level: The logging level of the prospective record (e.g., `logging.DEBUG`).

        Returns:
            bool: True if the ChannelLogger is effectively enabled *and*
                  `record_level >= effective_min_level`; otherwise False.

        Notes:
            - This method performs no side effects and does not construct a `LogRecord`.
            - Called early in `_log()` to avoid unnecessary work when filtered out.
        """
        ...

    # ===== Groups =====
    def add_group(self, name: str) -> None:
        """
        Add a group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behavior:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def remove_group(self, name: str) -> None:
        """
        Remove a group token if present.

        Args:
            name: Group token to remove.

        Behavior:
            - No error if not present (discard semantics).
        """
        ...

    def clear_groups(self) -> None:
        """
        Remove all group tokens from this ChannelLogger.
        """
        ...

    def get_groups_snapshot(self) -> List[str]:
        """
        Get a stable, sorted snapshot of current group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Properties =====
    def set_property(self, key: str, value: Any) -> None:
        """
        Set or update a property to stamp on subsequent records.

        Args:
            key: Non-empty string key (conventional guidance: <= 64 chars, token-like).
            value: Scalar value (str/int/float/bool) recommended. Small payloads only.

        Notes:
            - No serialization is performed here; downstream formatters/archivers decide.
            - Oversized or complex values may increase log overhead.
        """
        ...

    def set_properties(self, data: Dict[str, Any]) -> None:
        """
        Bulk update of properties.

        Args:
            data: Mapping of keys to values. Falsy/empty keys are skipped.

        Notes:
            - Each entry is applied atomically under the internal lock.
        """
        ...

    def remove_property(self, key: str) -> None:
        """
        Remove a property if present.

        Args:
            key: Property key to remove.

        Behavior:
            - Silent no-op when the key is absent.
        """
        ...

    def clear_properties(self) -> None:
        """
        Remove all properties from this ChannelLogger.
        """
        ...

    def get_properties_snapshot(self) -> Dict[str, Any]:
        """
        Get a shallow copy snapshot of all properties.

        Returns:
            Dict[str, Any]: Copy of current properties suitable for attaching to a record.
        """
        ...

    # ===== Emit / Logging =====
    def mask_log(
            self,
            level: int,
            message: str,
            *,
            owner: object,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
            exc_info: Union[None, bool, BaseException] = None,
            **kwargs: Any
    ) -> None:
        """
        Log once with masking enabled, using the owner's display identity
        ('<ULID>.<ClassName>'), and optionally overriding groups/system_groups/properties.
        """
        ...

    def _should_fast_exit(self, level: int) -> bool:
        """
        Fast-path filter to avoid work when logger is cleaned/disabled or level is below gates.
        """
        ...

    def _resolve_caller(self, tmpl_logger, *, stacklevel: int, manual_stack: bool, kwargs: dict):
        """
        Compute caller metadata for LogRecord creation.
        Returns: (fn, lno, func, sinfo)
        """
        ...

    def _normalize_exc_info(self, exc_info):
        """
        Normalize exc_info to either a (type, value, tb) tuple or None.

        - True           -> sys.exc_info(), unless outside an except block (then None)
        - tuple          -> passthrough
        - other truthy   -> None (conservative)
        - falsy/None     -> None
        """
        ...

    def _build_record(
            self,
            tmpl_logger,
            *,
            level: int,
            msg: str,
            args: tuple,
            exc_info,
            fn: str,
            lno: int,
            func: str,
            sinfo,
    ):
        """
        Build a LogRecord with real caller metadata so formatter can render method/module/line.
        """
        ...

    def _apply_identity_and_tags(self, record, *, mask: bool, kwargs: dict):
        """
        Apply identity (id/name) and group/property tags to the LogRecord.
        """
        ...

    def _emit_record(self, record):
        """
        Fan-out to all backing loggers and notify per-channel subscribers.
        """
        ...

    def _log(self, level: int, msg: str, *args, mask: bool = False, **kwargs):
        """
        Internal logging method that creates and dispatches a LogRecord to all
        configured loggers if enabled and above the min level.

        Args:
            level: Logging level (e.g., `logging.INFO`).
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            mask: If True, use masked identity and optional overrides from kwargs.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).
                     Internal keys consumed here (and removed):
                       - _stack_info: bool -> if True, compute caller info (default False)
                       - stacklevel: int -> passed to findCaller (default 3)
                       - _mask_display_name/_mask_display_id/_groups_override/
                         _system_groups_override/_properties_override (masking branch)
        """
        ...

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `INFO` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `WARNING` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    warn = warning  # alias

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `ERROR` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with `DEBUG` level.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments (e.g., `exc_info`).

        Notes:
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def exception(self, msg: str, *args, **kwargs) -> None:
        """
        Convenience helper to log an exception with `ERROR` level, including traceback.

        Args:
            msg: Message string or format string.
            *args: Positional args used with `msg` if it's a format string.
            **kwargs: Additional keyword arguments. `exc_info` is forced to True.

        Notes:
            - Equivalent to `error(..., exc_info=True)`.
            - Subject to effective enablement and min-level filtering.
        """
        ...

    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with CRITICAL level.s
        """
        ...

    fatal = critical

    # ===== System Groups =====
    def _add_system_group(self, name: str) -> None:
        """
        Internal: add a single system group token.

        Args:
            name: Non-empty string token. No normalization is applied.

        Behavior:
            - No-op if `name` is falsy.
            - Safe under concurrent calls.
        """
        ...

    def _add_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: add multiple system group tokens.

        Args:
            names: Iterable of tokens. Falsy/empty tokens are skipped. If None, no-op.

        Behavior:
            - Safe under concurrent calls.
        """
        ...

    def _remove_system_group(self, name: str) -> None:
        """
        Internal: remove a system group token if present.

        Args:
            name: Token to remove.

        Behavior:
            - Silent no-op if not present (discard semantics).
        """
        ...

    def _remove_system_groups(self, names: Optional[Iterable[str]]) -> None:
        """
        Internal: remove multiple system group tokens.

        Args:
            names: Iterable of tokens to remove. If None, no-op.

        Behavior:
            - Silent no-op on missing tokens.
        """
        ...

    def _clear_system_groups(self) -> None:
        """
        Internal: remove all system group tokens.
        """
        ...

    def _has_system_group(self, name: str) -> bool:
        """
        Internal: check membership of a system group token.

        Args:
            name: Token to check.

        Returns:
            bool: True if present, else False.
        """
        ...

    def _get_system_groups_snapshot(self) -> List[str]:
        """
        Internal: get a stable, sorted snapshot of current system group tokens.

        Returns:
            List[str]: Unique tokens sorted case-insensitively.
        """
        ...

    # ===== Metadata convenience =====
    def add_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add group tokens and/or set properties in one call.

        Args:
            groups: Iterable of group tokens to add (ignored if None).
            properties: Mapping of properties to set/overwrite (ignored if None).
        """
        ...

    def remove_metadata(
            self,
            *,
            groups: Optional[Iterable[str]] = None,
            properties: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Remove group tokens and/or delete properties in one call.

        Args:
            groups: Iterable of group tokens to remove (ignored if None).
            properties: Iterable of property keys to delete (ignored if None).
        """
        ...

    def refresh_properties(self, **kwargs: Any) -> None:
        """
        Refresh (set/overwrite) per-record properties in-place.

        Usage:
            ch.refresh_properties(open=self._open, queued=queue.size)
        """
        ...

    refresh_props = refresh_properties




@runtime_checkable
class IConfiguration(ISealable, Protocol):
    """
    Configuration governs the behavior of the entire system.

    It acts as the configuration core for:
    * **Conduit Management:** How Conduits handle service lifecycles.
    * **Dynamic Behavior:** Flags controlling dynamic linking, expansion, and policies.
    * **System Flags:** Global settings like debugging mode and resource disposal.

    This object should only be configured once and then frozen to prevent any further changes,
    enforcing idempotent laws across the system. Thread-safe operations are ensured with RLock.
    """

    # --- Attributes (surface expectations only) ---
    _frozen: bool
    available_properties: 'ConcurrentDict[str, Type]'
    _logger_factory: 'Pack[[object], Any] | None'
    _aether_frame: str
    _id: str

    # --- Lifecycle ---

    def seal(self) -> None:
        """
        Seals the configuration, preventing any further modifications and cleaning up resources.

        This method sets both the `sealed` and `frozen` flags.
        """
        ...

    # --- Core property API ---

    def set_logger_factory(self, factory: Callable[[object], Any] = None) -> None:
        """
        Set the logger factory used to produce per-object loggers.

        Contract:
            factory(obj: object) -> Any   # e.g., Iris ChannelLogger, SafeLogger, stdlib Logger, or None

        Usage:
            - Call with no arguments to install the implementation's default factory
              (the concrete Configuration uses StdLoggerFactory()).
            - Or pass a specific factory to override the default.

        Rules:
            - Must be set BEFORE freeze().
        """
        ...

    def get_logger_for(self, obj: object) -> Any | None:
        """
        Resolve a logger-like for 'obj' using the current logger factory.

        Returns:
            Any | None: Whatever the factory returns, or None if no factory is set.
        """
        ...

    def has_logger_factory(self) -> bool:
        """
        Returns:
            bool: True if a logger factory has been set; False otherwise.
        """
        ...

    def set_property(self, key: str, value: Any) -> None:
        """
        Defines or overwrites a property in the configuration.

        - **Idempotent properties** (e.g., 'system_state') can only be set *once* before the configuration is sealed.
        - **Non-idempotent properties** can be freely modified before the configuration is frozen.

        Args:
            key (str): The name of the property to set.
            value (Any): The value for the property.

        Raises:
            RuntimeError: If the configuration is sealed or frozen.
            RuntimeError: If attempting to modify an idempotent property that is already set.
            TypeError: If `key` is not a string.
            ValueError: If an enum conversion fails.
        """
        ...

    def clear_properties(self) -> None:
        """
        Clears all properties in the configuration.

        This method is useful for resetting the configuration to its initial state before it is frozen.

        Raises:
            RuntimeError: If the configuration is sealed or frozen.
        """
        ...

    def freeze(self) -> None:
        """
        Freezes the configuration property system.

        Once frozen, no properties, including non-idempotent ones, can be modified.
        Validation is performed automatically upon freezing.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If configuration validation fails prior to freezing (e.g., missing required properties).
        """
        ...

    def validate(self) -> bool:
        """
        Validates that all required configuration properties exist and match expected types.

        Performs both presence/type checks and enum-specific validation.

        Returns:
            bool: True if all validation checks pass.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If any property is missing or has the wrong type/value.
        """
        ...

    def validate_enums(self) -> bool:
        """
        Internal

        Validates that all properties intended to be Enums (like `SystemState`) are indeed set to a valid Enum instance.

        Returns:
            bool: True if all enum values are valid.

        Raises:
            RuntimeError: If the configuration is sealed.
            ValueError: If a known enum property is set to an invalid type.
        """
        ...

    def get_property(self, key: str) -> Any:
        """
        Retrieves the value of a configuration property.

        Args:
            key (str): The name of the property.

        Returns:
            Any: The stored value (str, int, bool, Enum, etc.).

        Raises:
            RuntimeError: If the configuration is sealed.
            KeyError: If the property does not exist in the configuration.
        """
        ...

    def has_property(self, key: str) -> bool:
        """
        Checks if a configuration property is defined.

        Args:
            key (str): The property name to check.

        Returns:
            bool: True if the property exists, False otherwise.

        Raises:
            RuntimeError: If the configuration is sealed.
        """
        ...

    def __iter__(self) -> Iterator[str]:
        """
        Allows iteration over the configuration properties (keys).

        Returns:
            Iterator: Property names (keys) in the configuration.
        """
        ...

    def load_default_dictionary(self) -> None:
        """
        Loads and applies a default set of properties atomically.

        This method sets sensible defaults for core properties like `system_state`, `debugging`, and `disposal`.

        Raises:
            RuntimeError: If the configuration is sealed.
        """
        ...

    # ---------------------------
    # Fluent / Builder-style API
    # ---------------------------

    def clear_logger_factory(self) -> 'IConfiguration':
        """
        Clear the logger factory (pre-freeze only) and return `self`.
        """
        ...

    def with_logger_factory(self, factory: Callable[[object], Any]) -> 'IConfiguration':
        """
        Fluent

        Set the logger factory (factory(obj) -> Any) and return `self`.
        Must be called before freeze().
        """
        ...

    def with_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load Melder’s standard defaults into this configuration and return `self`
        so you can keep chaining.

        Behavior:
        - Sets: system_state="automatic", debugging=False, disposal=False,
          disposal_method_names=[].
        - Respects idempotency and immutability rules (raises if frozen or sealed).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_system_state(self, state: 'SystemState | str') -> 'IConfiguration':
        """
        Fluent

        Set the system state ("automatic" or "dynamic") and return `self`.

        Notes:
        - Accepts either SystemState or a case-insensitive string.
        - Idempotent: can be set only once before freeze; attempting to overwrite raises.

        Args:
            state: Desired system state (SystemState or "automatic"|"dynamic").

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_debugging(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable or disable debugging and return `self`.

        Args:
            enabled: True to enable debugging; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal(self, enabled: bool = True) -> 'IConfiguration':
        """
        Fluent

        Enable or disable disposal features and return `self`.

        Args:
            enabled: True to enable disposal semantics; False to disable.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def with_disposal_method_names(self, names: list[str]) -> 'IConfiguration':
        """
        Fluent

        Replace the entire list of disposal method names and return `self`.

        Example:
            cfg.with_disposal_method_names(["close", "cleanup"])

        Args:
            names: Full replacement list of method names (strings).

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def add_disposal_methods(self, *names: str) -> 'IConfiguration':
        """
        Fluent

        Append one or more disposal method names (deduplicated, order-preserving)
        and return `self`.

        Behavior:
        - Initializes the list to [] if unset.
        - Preserves existing order; adds new names at the end if not already present.

        Args:
            *names: One or more method names to add.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def finalize(self) -> 'IConfiguration':
        """
        Fluent

        Validate and freeze, returning `self`.

        Returns:
            IConfiguration: This same configuration instance (for chaining).
        """
        ...

    def build(self) -> 'IConfiguration':
        """
        Fluent alias for finalize().
        """
        ...

    def dynamic_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load defaults and set dynamic state, returning `self`.
        """
        ...

    def automatic_defaults(self) -> 'IConfiguration':
        """
        Fluent

        Load defaults and set automatic state, returning `self`.
        """
        ...

@runtime_checkable
class ISafeLogger(ICleanable, Protocol):
    """
    Structural contract for SafeLogger-like objects.

    Masking (optional; default False):
      - When `mask=True` and the underlying logger is a ChannelLogger, the call routes
        to ChannelLogger.mask_log(...) using the provided identity & tags.
      - When wrapping a standard logging.Logger, masking params are ignored (no-op).

    Notes:
      - Signatures mirror SafeLogger's public API (including mask options).
      - `exception()` is an explicit helper (equivalent to error(..., exc_info=True)).
      - `cleanup()` aligns with Cleanable semantics.
    """

    # Optional: some implementations surface an identifier
    _id: str  # runtime presence not enforced by Protocol, but allowed for duck-typing

    # ---- Core API --------------------------------------------------------------

    def debug(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def info(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def warning(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def error(
            self,
            msg: str,
            method_name: str,
            *,
            exc_info: Union[None, bool, BaseException] = True,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def exception(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def critical(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    # ---- Lifecycle ------------------------------------------------------------


@runtime_checkable
class IContract(ISealable, Protocol):
    """
    A symmetric contract between two conduit wards.

    Each contract maintains permission details for both sides independently.
    There is no directional bias (no initiator or provider); both parties
    may define what spells they allow the other to use.

    Fields:
    - _ward_a / _ward_b: The two conduit ward participants in this contract.
    - _details_a / _details_b: Spell permission maps for each ward's view.
    - _id: Unique identifier for this contract instance.
    """

    _id: str
    _ward_a: IConduitWard
    _ward_b: IConduitWard
    _details_a: 'ConcurrentDict[str, IDetail]'
    _details_b: 'ConcurrentDict[str, IDetail]'

    def _clean_up(self) -> None:
        """
        Internal

        Seal and clear all spell details from both sides.
        """
        ...

    def _get_peer(self, ward: IConduitWard) -> IConduitWard:
        """
        Internal

        Return the opposite conduit in this contract.
        """
        ...

    def _get_opposite_conduit(self, contract: 'IContract', known_id: str) -> Optional[IConduit]:
        """
        Internal

        Helper to find the opposite conduit in a contract based on a known conduit ID.
        :param contract:
        :param known_id:
        :return:
        """
        ...

    def _get_detail_map(self, ward: IConduitWard) -> 'ConcurrentDict[str, IDetail]':
        """
        Internal

        Helper to return the permission map associated with a given ward.
        """
        ...

    def _add(self, ward: IConduitWard, contract_detail: IDetail) -> None:
        """
        Internal

        Add a spell-level permission detail to the contract on behalf of the given ward.
        """
        ...

    def _remove(self, ward: IConduitWard, spell_id: str) -> None:
        """
        Internal

        Remove a spell-level permission detail from the given ward's view.
        """
        ...

    def _clear_contract(self) -> None:
        """
        Internal

        Clear all spell details from both sides of the contract.
        This is typically called when sealing the contract.
        """
        ...

    def _check_if_exists_and_permissions(self, ward: IConduitWard, spell_id: str, permission: 'Permissions') -> bool:
        """
        Internal

        Check if the given ward has permission for the specified spell.
        """
        ...

    def _check_if_exists(self, ward: IConduitWard, spell_id: str) -> bool:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        ...

    def _find_spell_in_ward(self, spell_id: str) -> IConduitWard | None:
        """
        Internal

        Check if a spell exists in the given ward's permission map.
        """
        ...

    def _grant(self, ward: IConduitWard, spell_ids: list[str], permission: 'Permissions') -> None:
        """
        Internal

        Grant a list of spells with a single permission type for the specified ward.

        Args:
            ward (IConduitWard): The ward granting access.
            spell_ids (list[str]): List of spell IDs to grant.
            permission (Permissions): The permission level to assign.
        """
        ...