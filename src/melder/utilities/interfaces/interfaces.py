from typing import Type, Optional, Any, Dict, Protocol, Union
from uuid import UUID

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


class ISpell(Protocol):
    """
    An Interface defining the shape of a 'Spell', a unit of logic that can be cast.

    This represents the blueprint for a service, component, or function that
    can be managed by the melder system.

    Attributes:
        post_hooks (Optional[Any]): A list of callables to run after the spell is cast.
        activation_hooks (Optional[Any]): A list of callables to run during casting.
        pre_hooks (Optional[Any]): A list of callables to run before casting.
        _owner_conduit_id (Optional[UUID]): The UUID of the Conduit that owns this spell.
        _permissions (Optional[Any]): The permissions object governing this spell's
            accessibility.
    """
    post_hooks: Optional[Any]
    activation_hooks: Optional[Any]
    pre_hooks: Optional[Any]
    _owner_conduit_id: Optional[UUID]
    _permissions: Optional[Any]

    def add_spell_details(self, *args, **kwargs):
        """
        Attaches detailed configuration or metadata to the spell.

        Args:
            *args: Positional arguments for configuration.
            **kwargs: Keyword arguments, often used for specific details like
                      'dependency_graph' or 'existing_object'.
        """
        ...

    def _add_owned_conduit(self, conduit_id: UUID, conduit_name: str = None ):
        """
        Assigns ownership of this spell to a specific Conduit.

        Args:
            conduit_id (UUID): The unique ID of the owning Conduit.
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

    def bind(self, spell: Any, existence: str, whitelist: Optional[bool] = True, *, spellframe: Optional[Any] = None, name: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Binds a new spell (blueprint) into this spellbook.

        This profiles the spell, generates its unique ID, and registers it
        with the specified lifecycle (existence) and metadata.

        Args:
            spell (Any): The class, function, or object to bind.
            existence (str): The lifecycle policy (e.g., "unique", "many").
            whitelist (Optional[bool], optional): Legacy flag, recommend using permissions.
            spellframe (Optional[Any], optional): The logical interface or group.
            name (Optional[str], optional): A unique binding name to disambiguate.
            **kwargs: Additional metadata, including lifecycle hooks
                      (e.g., `pre_hooks`, `post_hooks`).

        Returns:
            Optional[str]: The unique spell_id of the bound spell.
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
            conduit_id (UUID): The ID of the Conduit providing the spell.
        """
        ...

    def _create_link_contract(self, _id):
        """
        Internal: Initializes the storage for a new contract.

        Args:
            _id (UUID): The ID of the peer conduit.
        """
        ...

    def _sever_link_contract(self, _conduit_id):
        """
        Internal: Removes a contract and all associated borrowed spells.

        Args:
            _conduit_id (UUID): The ID of the peer conduit to sever ties with.
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
            conduit_id (UUID): The ID of the peer conduit.
        """
        ...

    def _clear_contracted_spells_for_conduit(self, conduit_id):
        """
        Internal: Clears all borrowed spells from a specific peer conduit.

        Args:
            conduit_id (UUID): The ID of the peer conduit.
        """
        ...

    def _find_contracted_spell(self, spell_id):
        """
        Internal: Finds a borrowed spell by its ID.

        Args:
            spell_id (str): The unique spell_id.
        """
        ...


class IBind(Protocol):
    """
    An Interface for a binding mechanism, responsible for profiling and
    registering a spell blueprint.
    """

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


class IMeld(Protocol):
    """
    An Interface for the object resolution (melding) process.

    This is responsible for taking a spell request, resolving its dependencies,
    and "casting" it into a live object instance.
    """
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

class IConduitWard(Protocol):
    """
    An Interface for a 'ConduitWard', managing links, policies, and contracts
    between its Conduit and other Conduits.

    Attributes:
        _contracts (Optional[Any]): Storage for active contracts.
        _lock (Optional[Any]): The concurrency lock.
        _received_index (Optional[Any]): Index of incoming links.
        _policy (Optional[Any]): The active access policy.
        _id (Optional[UUID]): The UUID of the Conduit this ward protects.
        _conduit (Optional['IConduit']): A reference to the Conduit itself.
    """
    _contracts: Optional[Any]
    _lock: Optional[Any]
    _received_index: Optional[Any]
    _policy: Optional[Any]
    _id: Optional[UUID]
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


class IConduit(ISealable, Protocol):
    """
    An Interface for a 'Conduit', the core execution scope and object factory.

    It owns a Spellbook (its registry) and a ConduitWard (its security)
    and is responsible for "melding" (creating) objects.

    Attributes:
        _conduit_state (Optional[Any]): The current state (e.g., 'normal', 'lesser').
        __creation_context__ (Optional[Any]): Metadata about its creation.
        _conduit_ward (IConduitWard): The ward managing its links and policies.
        _spellbook (ISpellbook): The registry of spells available to this conduit.
    """
    _conduit_state: Optional[Any]
    __creation_context__: Optional[Any]
    _conduit_ward: "IConduitWard"
    _spellbook: "ISpellbook"

    @property
    def name(self) -> str:
        """
        The human-readable name of this Conduit.
        """
        ...

    @name.setter
    def name(self, value: str):
        """
        Sets the human-readable name of this Conduit.
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
            conduit_id (UUID): The unique ID of the Conduit.
            aetheric_frame (str): The frame to search within.
        """
        ...


class IConduitCloud(Protocol):
    """
    An Interface for the 'ConduitCloud', a global registry for accessing
    named, top-level Conduits.
    """

    def get_conduit(self, name: str) -> "IConduit":
        """
        Retrieves a Conduit from the cloud by its registered name.

        Args:
            name (str): The unique name of the Conduit.

        Returns:
            IConduit: The Conduit instance.
        """
        ...


class ILink(Protocol):
    """
    An Interface representing a live connection (contract) between two Conduits.
    """
    def sever(self):
        """
        Severs the link, dissolving the contract between the two Conduits.
        """
        ...


class IDetail(Protocol):
    """
    An Interface for a 'Detail', a single permission or rule within a Contract.
    """
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