from uuid import uuid4, UUID
from logging import warning
from typing import Optional, List, Dict, Any, Type, Callable
from melder.aether.aether import Aether
from melder.spellbook.bind.graph_builder.inspector.spell_examiner import MethodProfile, ClassProfile
from melder.utilities.interfaces import ISpellbook, ISpell
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.bind.bind import Bind
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from threading import RLock
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.general_helpers import EnumHelpers
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

        # Spell Data
        self.spell = spell #Object reference
        self.spell_id: spell_id = spell_id
        self.spellframe: Optional[Any] = spellframe
        self.spell_type: SpellType = spell_type
        self.user_created_object: object = existing_object
        self.binding_name: str = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence
        self.profile: ClassProfile | MethodProfile = profile
        self.aetheric_frame: str = aetheric_frame

        # Permissions
        self.permissions: Permissions = permissions

        # Spell Metadata
        self.tags = args if args else []
        self.metadata = kwargs if kwargs else {}
        self.dependencies: List[str] = []  # SHA256 spell IDs required for this spell to function

        # hooks
        self.pre_hooks: List[Callable] = []
        self.activation_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []

        # Created During validation
        self.dependency_graph = None

        # Created after Conduit Made
        self._owner_conduit_id: UUID | None = None
        self._owner_conduit_name: str | None = None
        self.owned_spell = None

        # Key for the spell in the Spellbook
        self._key = (self.spellframe or type(self.spell).__name__, self.binding_name or "__default__")

    def __repr__(self):
        frame = self.spellframe.__name__ if self.spellframe else type(self.spell).__name__
        return (
            f"Spell(name={self.spell_name}, binding={self.binding_name or '__default__'}, "
            f"frame={frame}, SHA256={self.spell_id})"
        )

#region Configuration
    def _add_owned_conduit(self, conduit_id: UUID, conduit_name: str = None):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        with self._lock:
            self._owner_conduit_id = conduit_id
            self._owner_conduit_name = conduit_name
            self.owned_spell = True

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
#region Disposal
    def seal(self):
        """
        Seals the spell, preventing any further modifications.
        """
        with self._lock:
            if self._sealed:
                return
            self.dependency_graph.dispose()
            self._sealed = True
#endregion Disposal
#endregion Spell

#region Spellbook
class Spellbook(ISpellbook):
    """
    Public API

    🧙 The Spellbook is the central authority for all spell definitions, bindings, and conduit conjurations.

    It acts as a high-level composition container and registry. All spells added to a Spellbook must be
    uniquely identifiable and comply with the Aetheric access rules and configuration state.

     -------------------------------------------------------------------------------
     ⚠️  WARNING: DO NOT USE `aether_frame` UNLESS YOU UNDERSTAND THE IMPLICATIONS!
     ⚠️  IMPORTANT: AETHER FRAMES

     The `aether_frame` parameter allows multiple Spellbooks to share the same
     configuration and spell visibility. This feature is **extremely powerful**
     and supports system-wide coordination, contract binding, and cross-agent
     sharing of spells.

     🧠 However, **do not use `aether_frame` unless you have read the
     documentation** and understand the implications of shared scope,
     mutation locking, and distributed spell ownership.

     By default, the (aether_frame=None) will generate a unique frame that is isolated for general use.
     Which will work as intended for most use cases.
     -------------------------------------------------------------------------------

    Responsibilities:
    - Holds and registers all known spells (via `bind()`).
    - Ensures configuration is frozen and synchronized via the Aether.
    - Provides conduit conjuring (`conjure()`) based on validated spells.
    - Supports optional shared configuration state through the `aether_frame` system.

    Parameters:
        aetheric_frame (str, optional):
            A shared frame name used to join multiple Spellbooks under the same Aetheric
            configuration and spell contract scope. Refer to documentation before using.

    Usage Example:
        spellbook = Spellbook()
        spellbook.configure_aether_frame(system_state="automatic", debugging=True)
        spellbook.bind(my_spell, existence=Existence.SINGLETON)
        conduit = spellbook.conjure()

    Notes:
        - You may only conjure one conduit per spellbook instance.
        - Configuration is locked automatically upon conjuring.
        - If configuration is already shared via an aether frame, it will be reused.
    """
    _aether = Aether()
    def __init__(self, aetheric_frame: str = "default", configuration: Optional[Configuration] = None):
        super().__init__()
        self._lock = RLock()

        # Internal state
        self._conjured = False
        self._aetheric_frame = aetheric_frame
        if not isinstance(self._aetheric_frame, str):
            raise TypeError(f"aetheric_frame must be a string, got {type(self._aetheric_frame).__name__}")

        # Configuration state
        self._configuration_locked: bool = False
        self._configuration = configuration

        # Core spell storage (SHA256-keyed)
        self._spells: ConcurrentDict[str, Spell] = ConcurrentDict()
        self._lookup_spells: ConcurrentDict[tuple, str]  = ConcurrentDict()

        # Networked/remote spell support
        # Basically if we're using dynamic mode it's a dict of dicts else it's not
        # This is because we're interested in the contract spells from conduits
        self._contracted_spells: ConcurrentDict[UUID, ConcurrentDict[str, Spell]] = ConcurrentDict(ConcurrentDict())
        self._lookup_contracted_spells: ConcurrentDict[UUID, ConcurrentDict[tuple, str]]  = ConcurrentDict(ConcurrentDict())

        self._initialize_configuration()

        # Binding system
        self._bind = Bind()

#region Core Methods
#region General Methods
    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its spell_id.
        :param spell_id: The unique identifier of the spell.
        :return: The permissions associated with the spell, or None if not found.
        """
        spell = self._find_spell(spell_id)
        if spell:
            return spell.permissions.name
        else:
            raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")

    def _find_spell(self, spell_id: str) -> Optional[Spell]:
        """
        Internal

        method to locate a spell by its spell_id.
        """
        return self._spells.get(spell_id)

    def _find_spell_count(self) -> int:
        """
        Internal

        Returns the number of spells in the spellbook.
        This is a simple utility method to check how many spells are currently registered.
        """
        with self._lock:
            return len(self._spells) if self._spells else 0

    def _find_contracted_spell_count(self) -> int:
        """
        Internal

        Returns the number of contracted spells in the spellbook.
        This is a simple utility method to check how many contracted spells are currently registered.
        """
        with self._lock:
            return len(self._contracted_spells) if self._contracted_spells else 0

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Find a spell by its frame, name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return:
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

        Create a normalized key for the spell in the Spellbook or contracted lookup.

        - If spellframe is not provided, fallback to spell_name.
        - If binding_name is not provided, default to '__default__'.

        Returns:
            tuple: (frame_or_name, binding_name)
        """
        return (spellframe or spell_name, binding_name or "__default__")

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Find a spell by its frame, name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return:
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


    def inspect_spell(self, spell: Any) -> Optional[str]:
        """
        Public API

        This method will inspect any object placed into it and check if it's
        a valid spell in the Aether Registry. Returns the SHA256 if found, else None
        :return:
        """
        with self._lock:
            if isinstance(spell, object):
                spell_id = self._bind.spell_id_inspector(spell)
                if Spellbook._aether._check_for_spell(spell_id, self._aetheric_frame):
                    return spell_id
            return None

    def _check_all_spells(self) -> None:
        """
        Check all spells in the spellbook for validity.
        This is a placeholder for the actual validation logic.
        """
        with self._lock:
            for spell in self._spells.keys():
                if Spellbook._aether._check_for_spell(spell, self._aetheric_frame):
                    raise RuntimeError(
                        f"Spell with ID {spell} already exists in the registry."
                    )


#endregion General Methods
#region Contract API

    def _create_link_contract(self, conduit_id: UUID):
        """
        Internal

        Create a link contract for the given conduit ID.

        This method ensures both internal maps (_contracted_spells and _lookup_contracted_spells)
        are initialized together. If only one exists, raises a RuntimeError to avoid partial state.
        """
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells

        if a_exists != b_exists:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, _lookup_contracted_spells={b_exists}"
            )

        if not a_exists and not b_exists:
            self._contracted_spells[conduit_id] = ConcurrentDict()
            self._lookup_contracted_spells[conduit_id] = ConcurrentDict()

    def _remove_link_contract(self, conduit_id: UUID):
        """
        Internal

        Remove a link contract for the given conduit ID.

        Ensures both internal maps (_contracted_spells and _lookup_contracted_spells)
        are removed together. If only one exists, raises a RuntimeError to avoid inconsistent cleanup.
        """
        a_exists = conduit_id in self._contracted_spells
        b_exists = conduit_id in self._lookup_contracted_spells

        if a_exists != b_exists:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}: "
                f"_contracted_spells={a_exists}, _lookup_contracted_spells={b_exists}"
            )

        if a_exists and b_exists:
            self._contracted_spells.pop(conduit_id)
            self._lookup_contracted_spells.pop(conduit_id)

    def _add_contracted_spell(self, spell: Spell, conduit_id: UUID) -> None:
        """
        Internal

        Add a spell to the contracted spells for the given conduit ID.
        Ensures both maps are updated atomically.
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

        Remove a spell from the contracted spells for the given conduit ID.
        Ensures both maps are cleaned consistently.
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

    #endregion Contract API
#region Binding API

    def bind(self, spell, existence: Existence, *, permissions: str = "create", spellframe=None, name=None, **kwargs) -> str:
        """
        Bind a spell to the spellbook using the `Bind` system.

        This will:
        - Inspect and profile the spell.
        - Generate a fingerprint-based spell_id.
        - Register it in the global registry under the given permissions.
        - Optionally attach lifecycle hooks.

        ⚠️ Permissions govern how the spell may be accessed by other conduits
        under contract or delegation. They do **not** affect spell behavior
        within the owner conduit.

        ──────────────────────────────────────────────
        Permissions:
            - "read":
                Allows downstream conduits to use the spell but not modify or recreate it.

            - "create":
                Grants full access — including creation of new instances derived from the spell.

            - "block":
                Disallows all borrowing or usage from other conduits.
                Still usable within the owning conduit.

        Parameters:
            spell (object):
                The spell object to bind.

            existence (Existence):
                Declares the lifecycle type of the spell (e.g., SINGLETON, TRANSIENT).

            permissions (str):
                Access level exposed to downstream conduits.
                Must be one of: "read", "create", "block"
                Defaults to "create".

            spellframe (str, optional):
                Optional frame/grouping for organizational lookup.

            name (str, optional):
                Optional override for spell binding name.

            **kwargs:
                - pre_hooks: List[Callable] — Executed before casting.
                - activation_hooks: List[Callable] — Executed during casting.
                - post_hooks: List[Callable] — Executed after casting.

        Returns:
            str: The unique SHA256 spell ID.
        """
        try:

            permissions = EnumHelpers.convert_enum_and_check(permissions, Permissions)  # Ensure the policy is valid
            spell = self._bind.bind(
                permissions=permissions,
                spell=spell,
                spellframe=spellframe,
                name=name,
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

    def _add_hooks_to_spell(self, spell: Spell, **kwargs) -> None:
        """
        Add hooks to the spell.
        :param spell:
        :param kwargs:
        :return:
        """
        if not isinstance(spell, Spell):
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
                        raise TypeError("pre_hooks must be a list of callables.")
                spell.activation_hooks = kwargs["activation_hooks"]
            if "post_hooks" in kwargs:
                for hook in kwargs["post_hooks"]:
                    if not callable(hook):
                        raise TypeError("pre_hooks must be a list of callables.")
                spell.post_hooks = kwargs["post_hooks"]

#endregion Binding API
#region Configuration API
    def _initialize_configuration(self) -> None:
        """
        Internal

        This method initializes the configuration for the Spellbook. It grabs the configuration from the Aether
        by providing the specific aetheric frame. It initializes the configuration if it does not exist.
        If the configuration already exists, it checks if the aetheric frame matches the one in the configuration.

        Raises:
            RuntimeError: If the configuration name does not match the aetheric frame.

        This is called during the Spellbook's initialization to ensure that the configuration is ready for use.
        """
        self._configuration: Any = self._get_configuration_from_aether

        if self._configuration:
            if self._configuration._aether_frame != self._aetheric_frame:
                raise RuntimeError("Configuration name does not match the aetheric frame.")
            self._configuration_locked = True
        else:
            self._configuration = Configuration(self._aetheric_frame)
            self._configuration_locked = False

    def _get_configuration_from_aether(self) -> Configuration:
        """
        Internal

        Retrieve the current configuration from the Aether.
        This is used to ensure that the spellbook's configuration is in sync with the Aether's state.

        :return: The current configuration for the Spellbook.
        """
        return Spellbook._aether._get_configuration(self._aetheric_frame)

    def is_configuration_locked(self) -> bool:
        """
        Check whether spellbook configuration is frozen.
        """
        return self._configuration_locked

    def configure_aether_frame(self,
                                *,
                                system_state: Optional[str],
                                debugging: Optional[bool],
                                disposal: Optional[bool],
                                disposal_method_names: Optional[List[str]]) -> None:
        """
        Configure the systems operational state and access control behavior.

        This method sets the configuration before it is sealed. Once sealed,
        the configuration becomes immutable. Invalid keys or configurations are rejected,
        and the conduit reverts to its prior state.

        Parameters:
            system_state (str):
                Indicates the type of conduit.
                - "Automatic": A standard conduit that operates under the default spell access control.
                Linking is disabled. Single Parent Conduit can be created. Conduit cloud disabled. Lesser conduits can be created.
                - "Dynamic": Allows for the creation of many conduits with dynamic linking capabilities.
                You gain access to the conduit cloud and can link to other conduits to contract their spells into any of your conduits.
                Conduits can be upgraded from lesser to normal, but not the other way around. Unlocks different kinds of policies not available in automatic mode.
                More details in documentation.

            debugging (bool):
                Enables internal UUID tagging for all objects created by the conduit.
                Useful for debugging object origins, especially across nested scopes.

            disposal (bool):
                Enables automatic disposal behavior. When the conduit is sealed,
                registered disposal methods will be invoked on objects created by this conduit.

            disposal_method_names (List[str]):
                A list of method names (e.g., ["close", "cleanup"]) to invoke on objects
                during disposal. These methods must exist on the objects produced by the conduit.

        Raises:
            RuntimeError:
                If the conduit configuration has already been locked/sealed.
            KeyError:
                If an invalid configuration key is provided.
            ValueError:
                If the provided configuration fails validation.
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
            self._configuration.clear_properties()
            raise e
        except Exception:
            raise

    def get_configuration(self) -> Configuration:
        """Return the active configuration for this Spellbook."""
        return self._configuration

#endregion Configuration API
#region Conduit API

    def create_new_preset_spellbook(self) -> 'Spellbook':
        """
        Internal

        Converts the current spellbook to a normal conduit spellbook.

        This method is used to upgrade a lesser conduit spellbook to a normal conduit spellbook.
        It ensures that the configuration is locked and the spells are properly registered.

        Raises:
            RuntimeError: If the spellbook is already conjured or configuration is locked.
        """
        return Spellbook(self._aetheric_frame, self._configuration)


    def conjure(self, policy: Optional[str] = "automatic", name: str = None) -> Conduit:
        """
        Create a new Conduit (execution channel) from this Spellbook.

        name (str, optional):
            The name of the conduit. If not provided, it will remain null.

        policy (str):
                Determines the spell access control behavior for this conduit.
                Valid options match the `Policies` enum (see below).

        Rules:
        - Only one conduit per spellbook
        - Configuration is frozen at conjuring time

        Please note policies are only available in dynamic mode otherwise automatic mode is defined as default.
        You must select system state dynamic to use other policies.

        Policies:
            These control how a conduit resolves spell access. They operate under the current
            system mode (automatic or dynamic).

            In **automatic** mode *default*:
                - "automatic":
                    🔒 Disables linking from normal conduits.
                    ✅ Allows linking from lesser conduits only.
                    🔁 Delegates access checks to parent or source conduit.

            In **dynamic** mode:
                - "dynamic":
                    🔓 Enables custom runtime evaluation and linking.
                    🧠 Allows handler functions for advanced access resolution.
                    🔒 Selectively whitelist or block spells based on dynamic conditions.

                - "whitelist_all":
                    ✅ Grants access to all local spells in this conduit.
                    ⛔ Ignores individual `meta["whitelist"]` tags.
                    🔒 Only available under the "dynamic" policy mode.

                - "block_all":
                    ⛔ Denies access to all spells unless they explicitly declare
                       `meta["whitelist"] = True`.
                    📌 Applies to local spells only.
                    🔒 Only available under the "dynamic" policy mode.
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. Only one is allowed per Spellbook."
                )

            if not self.is_configuration_locked():
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
            # TODO: Implement validation cycle to ensure all spells are valid
            return conduit

    def _check_system_state(self, policy: str) -> None:
        """
        Check if the system state is valid for conjuring a conduit.

        :param policy: The policy to check against the current configuration.
        :raises RuntimeError: If the system state is not valid for conjuring.
        """
        if self._configuration.get_property("system_state") == "automatic" and policy != Policies.automatic:
            raise RuntimeError(
                "Cannot use dynamic policies in automatic mode. "
                "Please set system_state to 'dynamic' in the configuration."
            )


    def _define_conduit_into_spells(self, conduit: Conduit) -> None:
        """
        Define the conduit into all spells.
        This is a placeholder for the actual logic to define the conduit into spells.
        """
        with self._lock:
            for spell in self._spells.values():
                spell._add_owned_conduit(conduit.__creation_context__._conduit_id, conduit._name)
                #spell._add_build_details(conduit.dependency_graph) # This is a placeholder for the actual DAG system

    def _set_policy_state(self, policy: Policies) -> None:
        """
        Set the policy state for the conduit.
        This is a placeholder for the actual logic to set the policy state.
        :param policy: The policy to set.
        """
        with self._lock:
            if policy == Policies.whitelist_all:
                self._block_all_spells = False
                self._whitelist_all_spells = True
            elif policy == Policies.block_all:
                self._block_all_spells = True
                self._whitelist_all_spells = False

#endregion Conduit API

#region Disposal

    def seal(self):
        """
        Finalize and seal the spellbook.
        (Optional override point for releasing resources or locking down the system.)
        """
        raise NotImplementedError("Sealing is not implemented yet.")

#endregion Disposal

#endregion
