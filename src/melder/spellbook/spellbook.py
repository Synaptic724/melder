from types import MappingProxyType
from uuid import UUID
from typing import Optional, List, Any, Mapping
import ulid
from threading import RLock

# Melder Imports
from melder.aether.aether import Aether
from melder.utilities.interfaces.interfaces import ISpellbook, ISpell, IConfiguration
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.bind.bind import Bind
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions

#region Spellbook
class Spellbook(ISpellbook):
    """
    Public API

    🧙 The **Spellbook** is the central authority for all spell definitions, bindings, and conduit conjurations.

    It acts as a high-level composition container and registry. All spells added to a Spellbook must be
    uniquely identifiable and comply with the Aetheric access rules and configuration state.

     -------------------------------------------------------------------------------
     ⚠️  WARNING: DO NOT USE `aetheric_frame` UNLESS YOU UNDERSTAND THE IMPLICATIONS!
     ⚠️  IMPORTANT: AETHER FRAMES

     The `aetheric_frame` parameter allows multiple Spellbooks to share the same
     configuration and spell visibility. This feature supports system-wide coordination,
     contract binding, and cross-agent sharing of spells.

     🧠 **Do not use `aetheric_frame` unless you have read the documentation** and
     understand the implications of shared scope, mutation locking, and distributed
     spell ownership.

     By default, setting (aetheric_frame=None) will generate a unique, isolated frame.
     -------------------------------------------------------------------------------

    **Responsibilities:**
    * Holds and registers all known spells (via `bind()`).
    * Ensures configuration is frozen and synchronized via the Aether.
    * Provides conduit conjuring (`conjure()`) based on validated spells.
    * Supports optional shared configuration state through the `aetheric_frame` system.

    Args:
        aetheric_frame (str, optional):
            A shared frame name used to join multiple Spellbooks under the same Aetheric
            configuration and spell contract scope. Defaults to "default".
        configuration (Optional[Configuration]):
            An optional pre-configured `Configuration` instance to use, typically provided
            when creating a Spellbook for an existing Aether frame.

    Notes:
        * You may only conjure one conduit per spellbook instance.
        * Configuration is locked automatically upon conjuring.
        * If configuration is already shared via an Aether frame, it will be reused.
    """
    _aether = Aether()
    def __init__(self, aetheric_frame: str = "default", configuration: Optional[Configuration] = None):
        super().__init__()
        self._lock = RLock()
        self._id: str = str(ulid.ULID()) # Unique internal ID for tracking

        # Internal state
        self._conjured = False
        self._aetheric_frame = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")

        # Configuration state
        self._configuration_locked: bool = False
        self._configuration = configuration

        # Core spell storage (SHA256-keyed)
        self._spells: ConcurrentDict[str, ISpell] = ConcurrentDict()
        self._lookup_spells: ConcurrentDict[tuple, str]  = ConcurrentDict()

        # Networked/remote spell support
        # This stores spells borrowed from other conduits (keyed by peer Conduit UUID)
        self._contracted_spells: ConcurrentDict[UUID, ConcurrentDict[str, ISpell]] = ConcurrentDict(ConcurrentDict())
        self._lookup_contracted_spells: ConcurrentDict[UUID, ConcurrentDict[tuple, str]]  = ConcurrentDict(ConcurrentDict())

        self._initialize_configuration()

        # Binding system
        self._bind = Bind()

    #region Disposal

    def seal(self):
        """
        Public API

        Finalizes and seals the spellbook.

        (Optional override point for releasing resources or locking down the system.)
        """
        raise NotImplementedError("Sealing is not implemented yet.")

    #endregion Disposal


    #region Properties

    @property
    def spells(self) -> Mapping[str, ISpell]:
        """
        Public API

        Returns a read-only view of the local spells registered in this spellbook.
        This provides safe introspection without allowing mutation.

        Returns:
            Mapping[str, ISpell]: An immutable map of spell ID to spell object.
        """
        return MappingProxyType(self._spells)

    @property
    def contracted_spells(self) -> Mapping[UUID, Mapping[str, ISpell]]:
        """
        Public API

        Returns a per-conduit read-only view of all **borrowed** spells.
        Each conduit ID maps to its own immutable spell dict.

        Returns:
            Mapping[UUID, Mapping[str, ISpell]]: An immutable map of peer Conduit ID to an immutable map of borrowed spells.
        """
        return MappingProxyType({
            conduit_id: MappingProxyType(dict(spells))  # Make inner dict immutable too
            for conduit_id, spells in self._contracted_spells.items()
        })

    #endregion Properties

    #region Core Methods
    #region General Methods
    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a locally registered spell.

        Args:
            spell_id (str): The unique identifier of the spell.

        Returns:
            Optional[str]: The permissions ("read", "create", or "block") associated with the spell.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
        """
        spell = self._find_spell(spell_id)
        if spell:
            return spell.permissions.name
        else:
            raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")

    def _find_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        Locates a locally registered spell by its unique ID.

        Args:
            spell_id (str): The ID of the spell to find.

        Returns:
            Optional[ISpell]: The spell object if found, otherwise None.
        """
        return self._spells.get(spell_id)

    def _find_contracted_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        Locates a contracted spell by its unique ID by searching across all peer contracts.

        Args:
            spell_id (str): The ID of the contracted spell to find.

        Returns:
            Optional[ISpell]: The spell object if found.

        Raises:
            RuntimeError: If the contracted spell with the given ID is not found.
        """
        for contracted_spells in self._contracted_spells.values():
            if spell_id in contracted_spells:
                return contracted_spells[spell_id]
        raise RuntimeError(f"Contracted spell with ID {spell_id} not found in the spellbook.")

    def _find_spell_count(self) -> int:
        """
        Internal

        Returns the total number of locally registered spells.

        Returns:
            int: The count of local spells.
        """
        with self._lock:
            return len(self._spells) if self._spells else 0

    def _find_contracted_spell_count(self) -> int:
        """
        Internal

        Returns the number of peer conduits this spellbook currently has contracts with.

        Returns:
            int: The number of active contract links.
        """
        with self._lock:
            return len(self._contracted_spells) if self._contracted_spells else 0

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Finds a spell's unique ID (SHA256) using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[str]: The unique SHA256 identifier of the spell.

        Raises:
            RuntimeError: If the spell is not found in the spellbook (local or contracted).
        """
        # Key for the spell in the Spellbook
        key = self._make_spell_key(spellframe, spell_name, binding_name)


        if key in self._lookup_spells:
            return self._lookup_spells[key]

        for contracted_spells in self._lookup_contracted_spells.values():
            if key in contracted_spells:
                # If the spell is contracted, we need to return the spell_id from the contracted spells
                return contracted_spells[key]
        else:
            raise RuntimeError("Spell not found in the spellbook.")

    def _make_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> tuple:
        """
        Internal

        Creates a normalized key for spell lookups.

        Args:
            spellframe (str): The logical frame (can be None).
            spell_name (str): The primary name.
            binding_name (str): The binding name (can be None).

        Returns:
            tuple: (frame_or_name, binding_name_or_default)
        """
        return (spellframe or spell_name, binding_name or "__default__")

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's lookup key (`(frame_or_name, binding_name_or_default)`).

        Raises:
            RuntimeError: If the spell key is not found (local or contracted).
        """
        # Key for the spell in the Spellbook
        key = (spellframe or spell_name, binding_name or "__default__")

        if key in self._lookup_spells:
            return key
        for contracted_spells in self._lookup_contracted_spells.values():
            if key in contracted_spells:
                # If the spell is contracted, we need to return the spell_id from the contracted spells
                return key
        else:
            raise RuntimeError("Spell key not found in the spellbook.")


    def inspect_spell(self, spell: Any, aetheric_frame= "default") -> Optional[str]:
        """
        Public API

        Inspects an object instance to determine its unique SHA256 ID, then checks if that ID
        is registered anywhere in the Aether Registry (globally).

        Args:
            spell (Any): The object to inspect (class, function, or instance).
            aetheric_frame (str): The Aetheric Frame to check the global registry against.

        Returns:
            Optional[str]: The unique SHA256 ID of the spell if it is registered in the Aether, else None.
        """
        with self._lock:
            if isinstance(spell, object):
                spell_id = self._bind.spell_id_inspector(spell)
                if Spellbook._aether._check_for_spell(spell_id, aetheric_frame):
                    return spell_id
            return None


    def _check_all_spells(self) -> None:
        """
        Internal

        Performs a system check to verify that no locally bound spell ID is already
        registered in the global Aether registry for this frame.

        Raises:
            RuntimeError: If a spell ID is found to be duplicated in the Aether.
        """
        with self._lock:
            for spell in self._spells.keys():
                if Spellbook._aether._check_for_spell(spell, self._aetheric_frame):
                    raise RuntimeError(
                        f"Spell with ID {spell} already exists in the registry."
                    )


    #endregion General Methods
    #region Contract API
    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: UUID) -> Optional[ISpell]:
        """
        Internal

        Retrieves a contracted spell using its spell_id from the contract established with a specific conduit.

        Args:
            spell_id (str): The ID of the spell to find.
            conduit_id (UUID): The peer conduit whose contract holds the spell.

        Returns:
            Optional[ISpell]: The spell if found under that conduit's contract, else None.
        """
        if conduit_id not in self._contracted_spells:
            return None
        return self._contracted_spells[conduit_id].get(spell_id)

    def _create_link_contract(self, conduit_id: UUID):
        """
        Internal

        Initializes the internal storage maps for a new contract link with a peer conduit.

        This method ensures both `_contracted_spells` (value map) and `_lookup_contracted_spells` (key map)
        are initialized atomically to maintain consistent state.

        Args:
            conduit_id (UUID): The ID of the peer conduit to create the contract structure for.

        Raises:
            RuntimeError: If the contract structure is found in one map but not the other (inconsistent state).
        """
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells

        if a_exists != b_exists:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, _lookup_contracted_spells={b_exists}"
            )

        if not a_exists and not b_exists:
            with self._lock:
                self._contracted_spells[conduit_id] = ConcurrentDict()
                self._lookup_contracted_spells[conduit_id] = ConcurrentDict()

    def _remove_link_contract(self, conduit_id: UUID):
        """
        Internal

        Removes the internal storage maps for a dissolved contract link with a peer conduit.

        This ensures both maps are removed atomically and consistently.

        Args:
            conduit_id (UUID): The ID of the peer conduit whose contract structure should be removed.

        Raises:
            RuntimeError: If the contract structure is found in one map but not the other (inconsistent cleanup).
        """
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells

        if a_exists != b_exists:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, _lookup_contracted_spells={b_exists}"
            )

        if a_exists and b_exists:
            with self._lock:
                self._contracted_spells.pop(conduit_id)
                self._lookup_contracted_spells.pop(conduit_id)

    def _add_contracted_spell(self, spell: ISpell, conduit_id: UUID) -> None:
        """
        Internal

        Adds a specific spell (borrowed from a peer) to the contracted spells for the given conduit.

        Args:
            spell (ISpell): The spell object being contracted.
            conduit_id (UUID): The ID of the peer conduit providing the spell.
        """
        with self._lock:
            if conduit_id not in self._contracted_spells:
                self._create_link_contract(conduit_id)

            spell_key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)

            self._contracted_spells[conduit_id][spell.spell_id] = spell
            self._lookup_contracted_spells[conduit_id][spell_key] = spell.spell_id

    def _remove_contracted_spell(self, spell_id: str, conduit_id: UUID) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry.

        Args:
            spell_id (str): The ID of the spell to remove.
            conduit_id (UUID): The ID of the peer conduit the spell was contracted from.

        Raises:
            RuntimeError: If the conduit ID or spell ID/key is not found in the contracted maps.
        """
        with self._lock:
            if conduit_id not in self._contracted_spells:
                raise RuntimeError(f"No contracted spells found for conduit ID {conduit_id}.")

            spell_map = self._contracted_spells[conduit_id]
            if spell_id not in spell_map:
                raise RuntimeError(f"Spell ID {spell_id} not found for conduit ID {conduit_id}.")

            # Get spell info before deletion
            spell = spell_map[spell_id]
            key = self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)

            if key not in self._lookup_contracted_spells[conduit_id]:
                raise RuntimeError(f"Spell key {key} not found in lookup for conduit ID {conduit_id}.")

            # Delete from both maps
            spell_map.pop(spell_id, None)
            self._lookup_contracted_spells[conduit_id].pop(key, None)

    def _clear_contracted_spells_for_conduit(self, conduit_id: UUID) -> None:
        """
        Internal

        Clears all spells associated with a contracted conduit, retaining the contract structure.

        This operation removes all borrowed spells from a peer without dissolving the core contract link.

        Args:
            conduit_id (UUID): The ID of the peer conduit.

        Raises:
            RuntimeError: If the conduit ID does not exist or the maps are inconsistent.
        """
        with self._lock:
            if conduit_id not in self._contracted_spells or conduit_id not in self._lookup_contracted_spells:
                raise RuntimeError(f"No contracted spell maps found for conduit ID {conduit_id}.")

            # Clear spells and lookup entries, keeping the empty dicts intact
            self._contracted_spells[conduit_id].clear()
            self._lookup_contracted_spells[conduit_id].clear()

    def _sever_link_contract(self, conduit_id: UUID) -> None:
        """
        Internal

        Sever the link contract for a given conduit ID by removing all contracted spells and the contract structure itself.

        Args:
            conduit_id (UUID): The ID of the peer conduit.

        Raises:
            RuntimeError: If only one of the maps contains the conduit ID (inconsistent state).
        """
        with self._lock:
            a_exists = conduit_id in self._contracted_spells
            b_exists = conduit_id in self._lookup_contracted_spells

            if a_exists != b_exists:
                raise RuntimeError(
                    f"Inconsistent contract state for conduit ID {conduit_id}: "
                    f"_contracted_spells={a_exists}, _lookup_contracted_spells={b_exists}"
                )

            if a_exists and b_exists:
                self._contracted_spells.pop(conduit_id, None)
                self._lookup_contracted_spells.pop(conduit_id, None)

    #endregion Contract API
    #region Binding API

    def bind(self, spell, existence: Existence, *, permissions: str = "create", spellframe=None, binding_name=None,
             **kwargs) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        This method profiles the spell, computes a unique SHA256 ID, stores it locally,
        and assigns necessary lifecycle and permission policies.

        ──────────────────────────────────────────────
        🛡️ Permissions (access control to other conduits):
            - `"read"`: Allows other conduits to *use* but not create new instances.
            - `"create"` (default): Allows other conduits to both use *and* create instances.
            - `"block"`: Completely blocks access to the spell from other conduits.

        🔄 Existence (spell lifecycle):
            Determines how the spell instance is managed (e.g., `Existence.unique`, `Existence.many`).

        🪝 Lifecycle Hooks (optional `**kwargs`):
            - `pre_hooks`: Executed *before* the spell is constructed.
            - `activation_hooks`: Executed *during* spell construction.
            - `post_hooks`: Executed *after* the spell has been cast.

        ──────────────────────────────────────────────
        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read", "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among others in its frame.
            **kwargs: Optional lifecycle hooks (`pre_hooks`, `activation_hooks`, `post_hooks`).

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the spell is already bound in the Aether registry.
            TypeError: If invalid hook types are provided (not callable).
            ValueError: If the `permissions` string is invalid.
        """

        try:

            permissions = EnumHelpers.convert_enum_and_check(permissions, Permissions)  # Ensure the policy is valid
            spell = self._bind.bind(
                permissions=permissions,
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
                existence=existence,
                aetheric_frame=self._aetheric_frame,
            )
            if Spellbook._aether._check_for_spell(spell.spell_id, self._aetheric_frame):
                raise RuntimeError(
                    f"Spell with ID {spell.spell_id} already exists in the registry."
                )
            self._add_hooks_to_spell(spell, **kwargs)
            self._lookup_spells[spell._key] = spell.spell_id
            self._spells[spell.spell_id] = spell
            return spell.spell_id
        except Exception:
            raise

    def _add_hooks_to_spell(self, spell: ISpell, **kwargs) -> None:
        """
        Internal

        Attaches validation and lifecycle hooks to the newly bound spell object.

        Args:
            spell (ISpell): The newly created spell object.
            **kwargs: Contains optional keys for `pre_hooks`, `activation_hooks`, and `post_hooks`.

        Raises:
            TypeError: If any provided hook is not callable.
        """
        if not isinstance(spell, ISpell):
            raise TypeError("spell must be an instance of Spell.")

        with self._lock:
            if "pre_hooks" in kwargs:
                for hook in kwargs["pre_hooks"]:
                    if not callable(hook):
                        raise TypeError("pre_hooks must be a list of callables.")
                spell.pre_hooks = kwargs["pre_hooks"]
            if "activation_hooks" in kwargs:
                for hook in kwargs["activation_hooks"]:
                    if not callable(hook):
                        raise TypeError("activation_hooks must be a list of callables.")
                spell.activation_hooks = kwargs["activation_hooks"]
            if "post_hooks" in kwargs:
                for hook in kwargs["post_hooks"]:
                    if not callable(hook):
                        raise TypeError("post_hooks must be a list of callables.")
                spell.post_hooks = kwargs["post_hooks"]

    #endregion Binding API
    #region Configuration API
    def _initialize_configuration(self) -> None:
        """
        Internal

        Initializes the configuration for the Spellbook by attempting to retrieve an existing
        `Configuration` from the Aether based on the `aetheric_frame`. If none exists, a new
        default configuration is created.

        Raises:
            RuntimeError: If an existing configuration's frame does not match the Spellbook's frame.
        """
        self._configuration: Any = self._get_configuration_from_aether()

        if self._configuration:
            if self._configuration._aether_frame != self._aetheric_frame:
                raise RuntimeError("Configuration name does not match the aetheric frame.")
            self._configuration_locked = True
        else:
            self._configuration = Configuration(self._aetheric_frame)
            self._configuration_locked = False

    def _get_configuration_from_aether(self) -> IConfiguration | None:
        """
        Internal

        Retrieves the current configuration from the Aether's global registry.

        Returns:
            IConfiguration | None: The configuration instance for this Aether frame, or None if not registered.
        """
        return Spellbook._aether._get_configuration(self._aetheric_frame)

    def is_configuration_locked(self) -> bool:
        """
        Public API

        Checks whether the spellbook's configuration is currently locked (frozen) or not.

        Returns:
            bool: True if the configuration is locked, False otherwise.
        """
        return self._configuration_locked

    def configure_aether_frame(self,
                               *,
                               system_state: Optional[str],
                               debugging: Optional[bool],
                               disposal: Optional[bool],
                               disposal_method_names: Optional[List[str]]) -> None:
        """
        Public API

        Configures the systems operational state and access control behavior before the configuration is sealed.

        Once sealed during `conjure()`, the configuration becomes immutable.

        Args:
            system_state (str, optional):
                Defines the system mode ("automatic" or "dynamic").
            debugging (bool, optional):
                Enables internal UUID tagging for object tracking.
            disposal (bool, optional):
                Enables automatic resource disposal upon conduit sealing.
            disposal_method_names (List[str], optional):
                A list of method names to invoke on created objects during disposal.

        Raises:
            RuntimeError: If the configuration has already been locked/sealed.
            KeyError: If an unknown configuration key is provided.
            ValueError: If the provided configuration fails validation (e.g., invalid system state value).
        """
        if self._configuration_locked:
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")

        kwargs = {
            k: v for k, v in {
                "system_state": system_state,
                "debugging": debugging,
                "disposal": disposal,
                "disposal_method_names": disposal_method_names
            }.items() if v is not None
        }

        try:
            for key, value in kwargs.items():
                if key not in self._configuration.available_properties:
                    raise KeyError(
                        f"Unknown configuration key '{key}'. "
                        f"Allowed keys are: {list(self._configuration.available_properties.keys())}"
                    )

                self._configuration.set_property(key, value)

            if not self._configuration.validate():
                raise ValueError("Invalid configuration. Please check your settings.")

            self._configuration.freeze()
            self._configuration_locked = True
            Spellbook._aether._bind_configuration(
                self._configuration, self._aetheric_frame
            )
        except (KeyError, ValueError) as e:
            # If validation or key setting fails, revert the changes
            self._configuration.clear_properties()
            raise e
        except Exception:
            raise

    def get_configuration(self) -> Configuration:
        """
        Public API

        Returns the active configuration object for this Spellbook.

        Returns:
            Configuration: The configuration instance.
        """
        return self._configuration

    #endregion Configuration API
    #region Conduit API

    def create_new_preset_spellbook(self) -> 'Spellbook':
        """
        Internal

        Creates a new `Spellbook` instance that shares the configuration and Aether frame of the current Spellbook.

        This is used internally when upgrading a lesser conduit's spellbook to a normal conduit spellbook.

        Returns:
            Spellbook: A new Spellbook instance ready for use by a normal conduit.
        """
        return Spellbook(self._aetheric_frame, self._configuration)


    def conjure(self, policy: Optional[str] = "automatic", name: str = None) -> Conduit:
        """
        Public API

        Creates a new **Conduit** (execution channel) from this Spellbook.

        This method finalizes the configuration, validates all local spells, and instantiates the `Conduit`.

        Args:
            policy (str, optional):
                Determines the spell access control behavior for this conduit. Must match a `Policies` enum member.
                Defaults to "automatic".
            name (str, optional):
                An optional name for the conduit.

        Returns:
            Conduit: The newly created Conduit instance.

        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic policies are used when `system_state` is "automatic".
            ValueError: If the configuration fails validation or the policy string is invalid.

        Policies:
            - **Automatic Mode** (default policy is `automatic`):
                * `"automatic"`: Delegates access checks, disables linking.
            - **Dynamic Mode** (requires `system_state: "dynamic"`):
                * `"dynamic"`: Enables custom linking and access resolution.
                * `"whitelist_all"`: Grants access to all local spells.
                * `"block_all"`: Denies access to all spells unless explicitly whitelisted.
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. Only one is allowed per Spellbook."
                )

            if not self.is_configuration_locked():
                # Apply defaults, freeze, and register configuration if not done already
                self._configuration.load_default_dictionary()
                self._configuration.freeze()
                self._configuration_locked = True
                Spellbook._aether._bind_configuration(
                    self._configuration, self._aetheric_frame
                )

            self._check_system_state(policy)  # Ensure the system state is valid for conjuring
            policy = EnumHelpers.convert_enum_and_check(policy, Policies)  # Ensure the policy is valid
            self._check_all_spells()

            conduit = Conduit(
                spellbook=self,
                name=name,
                conduit_state=ConduitState.normal,
                configuration=self._configuration,
                aetheric_frame=self._aetheric_frame,
                policy=policy
            )
            self._conjured = True
            self._define_conduit_into_spells(conduit)
            return conduit

    def _check_system_state(self, policy: str) -> None:
        """
        Internal

        Checks if the requested policy is compatible with the current `system_state` configuration.

        Args:
            policy (str): The policy requested for the new Conduit.

        Raises:
            RuntimeError: If a dynamic policy is requested while `system_state` is set to "automatic".
        """
        if self._configuration.get_property("system_state") == "automatic" and policy != Policies.automatic:
            raise RuntimeError(
                "Cannot use dynamic policies in automatic mode. "
                "Please set system_state to 'dynamic' in the configuration."
            )


    def _define_conduit_into_spells(self, conduit: Conduit) -> None:
        """
        Internal

        Defines the newly created Conduit's ownership metadata into all locally bound spells.

        Args:
            conduit (Conduit): The newly conjured Conduit instance.
        """
        with self._lock:
            for spell in self._spells.values():
                # Placeholder: This logic needs to be fully implemented to link spells to their owner conduit and creation manager
                spell._add_owned_conduit(conduit.__creation_context__._conduit_id, conduit._name, conduit._creations)

    def _set_policy_state(self, policy: Policies) -> None:
        """
        Internal

        Placeholder method to set the policy state for the conduit.

        Args:
            policy (Policies): The policy to set.
        """
        with self._lock:
            if policy == Policies.whitelist_all:
                self._block_all_spells = False
                self._whitelist_all_spells = True
            elif policy == Policies.block_all:
                self._block_all_spells = True
                self._whitelist_all_spells = False

#endregion Conduit API

#endregion