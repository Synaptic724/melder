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

#region Spell
class Spell(ISpell):
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
            whitelist: bool = False,
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
        self.whitelist: bool = whitelist

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
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        if dag is None:
            raise ValueError("Dependency graph cannot be None.")
        if dependencies is None:
            raise ValueError("Dependencies cannot be None.")

        with self._lock:
            self.dependency_graph = dag
            self.dependencies = dependencies


    def add_hooks(self, pre_hooks: List[Callable], activation_hooks: List[Callable], post_hooks: List[Callable]):
        """
        Add hooks to the spell.
        :param pre_hooks: List of pre-cast hooks.
        :param activation_hooks: List of activation hooks.
        :param post_hooks: List of post-cast hooks.
        """
        with self._lock:
            self.pre_hooks = pre_hooks
            self.activation_hooks = activation_hooks
            self.post_hooks = post_hooks
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
    The Spellbook acts as the authoritative registry for all active spells.
    It also manages configuration and controls Conduit conjuring.
    """
    _aether = Aether()
    def __init__(self, conduit_type: ConduitState = None, aether_frame: str = None):
        super().__init__()
        self._lock = RLock()

        # Internal state
        self._conjured = False
        self._aetheric_frame = aether_frame
        self._configuration_locked: bool = False
        self._configuration = Configuration(self._aetheric_frame)
        self._conduit_type = ConduitState.resolve(conduit_type)

        # Core spell storage (SHA256-keyed)
        self.__spells: ConcurrentDict[str, Spell] = None if self._conduit_type == ConduitState.lesser else ConcurrentDict()
        self.__lookup_spells: ConcurrentDict[tuple, str] = None if self._conduit_type == ConduitState.lesser else ConcurrentDict()

        # Networked/remote spell support
        # Basically if we're using dynamic mode it's a dict of dicts else it's not
        # This is mainly because we need to maintain the contract system while using lesser scopes
        self.__contracted_spells: ConcurrentDict[str, ConcurrentDict[str, Spell]] | ConcurrentDict[str, Spell] | None = ConcurrentDict() if self._conduit_type == ConduitState.lesser else None
        self.__lookup_contracted_spells: ConcurrentDict[str, ConcurrentDict[tuple, str]] | ConcurrentDict[tuple, str] | None = ConcurrentDict() if self._conduit_type == ConduitState.lesser else None

        # Binding system
        self._bind = Bind()

#region Properties

    @property
    def _spells(self) -> ConcurrentDict[str, Spell]:
        return self.__spells

    @_spells.setter
    def _spells(self, value: ConcurrentDict[str, Spell]):
        self.__spells = value

    @property
    def _lookup_spells(self) -> ConcurrentDict[tuple, str]:
        return self.__lookup_spells

    @_lookup_spells.setter
    def _lookup_spells(self, value: ConcurrentDict[tuple, str]):
        self.__lookup_spells = value

    @property
    def _contracted_spells(self) -> ConcurrentDict[str, Spell]:
        return self.__contracted_spells

    @_contracted_spells.setter
    def _contracted_spells(self, value: ConcurrentDict[str, Spell]):
        self.__contracted_spells = value

    @property
    def _lookup_contracted_spells(self) -> ConcurrentDict[tuple, str]:
        return self.__lookup_contracted_spells

    @_lookup_contracted_spells.setter
    def _lookup_contracted_spells(self, value: ConcurrentDict[tuple, str]):
        self.__lookup_contracted_spells = value

#endregion

#region Core Methods

#region Binding API
    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Find a spell by its frame, name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return:
        """
        # Key for the spell in the Spellbook
        key = (spellframe or spell_name, binding_name or "__default__")

        if key in self._lookup_spells:
            return self._lookup_spells[key]
        elif key in self._lookup_contracted_spells:
            return self._lookup_contracted_spells[key]
        else:
            warning("Spell not found in the spellbook.")
            return None

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
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
        elif key in self._lookup_contracted_spells:
            return key
        else:
            warning("Spell not found in the spellbook.")
            return None


    def inspect_spell(self, spell: Any) -> Optional[str]:
        """
        This method will inspect any object placed into it and check if its
        a valid spell in the Aether Registry. Returns the SHA256 if found, else None
        :return:
        """
        with self._lock:
            if isinstance(spell, object):
                spell_id = self._bind.spell_id_inspector(spell)
                if Spellbook._aether._check_for_spell(spell_id, self._aetheric_frame):
                    return spell_id
            return None

    def _lesser_conduit_spellbook_copy(self) -> ISpellbook:
        """
        Create a copy of the spellbook for a lesser conduit.
        This is a placeholder for the actual logic to create a lesser conduit copy.
        """
        with self._lock:
            spellbook = Spellbook()
            spellbook._conjured = True
            spellbook._configuration_locked = True
            spellbook._conduit_type = ConduitState.lesser
            return spellbook

    def bind(self, spell, existence: Existence, whitelist: bool = True, *, spellframe=None, name=None, **kwargs) -> str:
        """
        Bind a spell to the spellbook using the `Bind` system.

        This will:
        - Inspect and profile the spell
        - Generate a fingerprint-based spell_id
        - Register it in the global registry

        Kwargs can be attached to add hooks into the spell.
        `pre_hooks`, `activation_hooks`, and `post_hooks` are all lists of callable functions.

        The return for this can be ignored and is only used in dynamic mode.

        :param spell: The spell to bind.
        :param existence: The existence type of the spell.
        :param spellframe: The frame of the spell.
        :param name: The name of the spell.
        :param whitelist: Whether to use a whitelist for the spell.
        :param kwargs: Additional keyword arguments for hooks.
        :return: The spell ID.

        Example:
            dict = { "pre_hooks": [hook1, hook2], "activation_hooks": [hook3], "post_hooks": [hook4] }
        """
        try:
            spell = self._bind.bind(
                whitelist=whitelist,
                spell=spell,
                spellframe=spellframe,
                name=name,
                existence=existence,
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

    def _find_spell(self, spell_id: str) -> Optional[Spell]:
        """Internal method to locate a spell by its spell_id."""
        with self._lock:
            return self._spells.get(spell_id)

#endregion Binding API
#region Configuration API
    def is_configuration_locked(self) -> bool:
        """Check whether spellbook configuration is frozen."""
        return self._configuration_locked

    def lock_configuration(self) -> None:
        """Lock configuration to prevent mutation."""
        if self._configuration_locked:
            raise RuntimeError("Configuration is already locked.")
        with self._lock:
            self._configuration_locked = True

    def configure_aether_frame(self,
                                *,
                                system_state: Optional[str],
                                debugging: Optional[bool],
                                disposal: Optional[bool],
                                disposal_method_names: Optional[List[str]],
                                policy: Optional[str]) -> None:
        """
        Configure the conduit’s operational state and access control behavior.

        This method sets the conduit’s configuration before it is sealed. Once sealed,
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

            policy (str):
                Determines the spell access control behavior for this conduit.
                Valid options match the `Policies` enum (see below).

        Policies:
            These control how a conduit resolves spell access. They operate under the current
            system mode (automatic or dynamic).

            In **automatic** mode:
                - "automatic":
                    🔒 Disables linking from normal conduits.
                    ✅ Allows linking from lesser conduits only.
                    🔁 Delegates access checks to parent or source conduit.

            In **dynamic** mode:
                - "dynamic":
                    🔓 Enables custom runtime evaluation and linking.
                    🧠 Allows handler functions for advanced access resolution.

                - "whitelist_all":
                    ✅ Grants access to all local spells in this conduit.
                    ⛔ Ignores individual `meta["whitelist"]` tags.
                    🔒 Only available under the "dynamic" policy mode.

                - "block_all":
                    ⛔ Denies access to all spells unless they explicitly declare
                       `meta["whitelist"] = True`.
                    📌 Applies to local spells only.
                    🔒 Only available under the "dynamic" policy mode.

            Available in all modes:
                - "delegate":
                    🔗 Forwards access decisions to a parent conduit.
                    🪶 Used by lesser conduits to inherit spell access without duplication.
                    📭 Does not host any spells itself.

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
                "disposal_method_names": disposal_method_names,
                "policy": policy
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
    def conjure(self, name: str = None) -> Conduit:
        """
        Create a new Conduit (execution channel) from this Spellbook.

        Rules:
        - Only one conduit per spellbook
        - Configuration is frozen at conjuring time
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. Only one is allowed per Spellbook."
                )
            self._check_all_spells()

            if not self.is_configuration_locked():
                self._configuration.load_default_dictionary()
                self._configuration.freeze()
                self._configuration_locked = True

            self._conjured = True
            self._conduit_type = ConduitState.normal
            conduit = Conduit(
                spellbook=self,
                name=name,
                conduit_state=ConduitState.normal,
                configuration=self._configuration,
                aetheric_frame=self._aetheric_frame,
            )
            self._define_conduit_into_spells(conduit)
            # TODO: Implement validation cycle to ensure all spells are valid
            return conduit

    def _define_conduit_into_spells(self, conduit: Conduit) -> None:
        """
        Define the conduit into all spells.
        This is a placeholder for the actual logic to define the conduit into spells.
        """
        with self._lock:
            for spell in self._spells.values():
                spell._add_owned_conduit(conduit.__creation_context__._conduit_id, conduit._name)
                #spell._add_build_details(conduit.dependency_graph) # This is a placeholder for the actual DAG system

#endregion Conduit API

#region Disposal

    def seal(self):
        """
        Finalize and seal the spellbook.
        (Optional override point for releasing resources or locking down the system.)
        """
        pass

#endregion Disposal

#endregion
