import uuid
from typing import Optional, List, Dict, Any, Type, Callable, NamedTuple
from melder.aether.aether import Aether
from melder.spellbook.bind.graph_builder.inspector.spell_examiner import MethodProfile, ClassProfile
from melder.utilities.interfaces import ISpellbook, ISeal, ISpell
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.bind.bind import Bind
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
import threading


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
            existing_object: object = None,
            *args,
            **kwargs
    ):
        super().__init__()
        self._lock = threading.RLock()

        # Spell Type
        self.owned_spell = None

        # Spell Data
        self.spell = spell
        self.spell_id: spell_id
        self.spellframe: Optional[Any] = spellframe
        self.spell_type: SpellType = spell_type
        self.user_created_object: object = existing_object
        self.binding_name: str = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence
        self.profile: ClassProfile | MethodProfile = profile

        # Spell Metadata
        self.tags = args if args else []
        self.metadata = kwargs if kwargs else {}

        # hooks
        self.pre_hooks: List[Callable] = []
        self.activation_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []

        # Created During validation
        self.dependency_graph = None

        # Created after Conduit Made
        self._owner_conduit_id: uuid.UUID | None = None

        # Key for the spell in the Spellbook
        self._key = (self.spellframe or type(self.spell), self.binding_name or "__default__")

    def _add_owned_conduit(self, conduit_id: uuid.UUID):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        with self._lock:
            self._owner_conduit_id = conduit_id
            self.owned_spell = True

    def _add_dag(self, dag: Any):
        """
        Add details to the spell.
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        if dag is None:
            raise ValueError("Dependency graph cannot be None.")

        with self._lock:
            self.dependency_graph = dag


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

    def __repr__(self):
        return f"Spell(name={self.spell_name}, binding={self.binding_name or '__default__'}, frame={self.spellframe}, uuid={self.spell_id})"

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


    def seal(self):
        """
        Seals the spell, preventing any further modifications.
        """
        with self._lock:
            if self._sealed:
                return
            self.dependency_graph.dispose()
            self._sealed = True


class Spellbook(ISpellbook):
    """
    The Spellbook acts as the authoritative registry for all active spells.
    It also manages configuration and controls Conduit conjuring.
    """
    _aether = Aether()
    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

        # Internal state
        self._conjured = False
        self._configuration_locked: bool = False
        self._configuration = Configuration()

        # Core spell storage (SHA256-keyed)
        self.__spells: ConcurrentDict[str, Spell] = ConcurrentDict()
        self.__lookup_spells: ConcurrentDict[tuple, str] = ConcurrentDict()

        # Networked/remote spell support
        self.__contracted_spells: ConcurrentDict[str, Spell] = ConcurrentDict()
        self.__lookup_contracted_spells: ConcurrentDict[tuple, str] = ConcurrentDict()

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

    def _lesser_conduit_spellbook_copy(self) -> ISpellbook:
        """
        Create a copy of the spellbook for a lesser conduit.
        This is a placeholder for the actual logic to create a lesser conduit copy.
        """
        with self._lock:
            spellbook = Spellbook()
            #spellbook._contracted_spells = self.__spells.copy()   We actually need the contract to create this effect
            #spellbook._lookup_contracted_spells = self.__lookup_spells.copy() We need to link to this object to create this effect
            spellbook._conjured = True
            spellbook._configuration_locked = True
            return spellbook


    def bind(self, spell, existence: Existence, *, spellframe=None, name=None, **kwargs) -> None:
        """
        Bind a spell to the spellbook using the `Bind` system.

        This will:
        - Inspect and profile the spell
        - Generate a fingerprint-based spell_id
        - Register it in the global registry

        Kwargs can be attached to add hooks into the spell.
        `pre_hooks`, `activation_hooks`, and `post_hooks` are all lists of callable functions.

        Example:
            dict = { "pre_hooks": [hook1, hook2], "activation_hooks": [hook3], "post_hooks": [hook4] }
        """
        try:
            spell = self._bind.bind(
                spell=spell,
                spellframe=spellframe,
                name=name,
                existence=existence
            )
            if Spellbook._aether._check_for_spell(spell.spell_id):
                raise RuntimeError(
                    f"Spell with ID {spell.spell_id} already exists in the registry."
                )
            self._add_hooks_to_spell(spell, **kwargs)
            self._lookup_spells[spell._key] = spell.spell_id
            self._spells[spell.spell_id] = spell
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
                if Spellbook._aether._check_for_spell(spell):
                    raise RuntimeError(
                        f"Spell with ID {spell} already exists in the registry."
                    )

    def _find_spell(self, spell_id: str) -> Optional[Spell]:
        """Internal method to locate a spell by its spell_id."""
        with self._lock:
            return self._spells.get(spell_id)

    def is_configuration_locked(self) -> bool:
        """Check whether spellbook configuration is frozen."""
        return self._configuration_locked

    def lock_configuration(self) -> None:
        """Lock configuration to prevent mutation."""
        if self._configuration_locked:
            raise RuntimeError("Configuration is already locked.")
        with self._lock:
            self._configuration_locked = True

    def configure_conduit_state(self, **kwargs) -> None:
        """
        Apply conduit-specific configuration properties.
        If the config is invalid or keys are wrong, the changes are discarded.
        """
        if self._configuration_locked:
            raise RuntimeError("Configuration is locked. Cannot modify conduit state.")

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
            conduit = Conduit(
                spellbook=self,
                name=name,
                conduit_state="normal",
                configuration=self._configuration
            )
            self._define_conduit_into_spells(conduit)
            return conduit

    def _define_conduit_into_spells(self, conduit: Conduit) -> None:
        """
        Define the conduit into all spells.
        This is a placeholder for the actual logic to define the conduit into spells.
        """
        with self._lock:
            for spell in self._spells.values():
                spell._add_owned_conduit(conduit.__creation_context__._conduit_id)
                #spell._add_dag(conduit.dependency_graph) # This is a placeholder for the actual DAG system

    def seal(self):
        """
        Finalize and seal the spellbook.
        (Optional override point for releasing resources or locking down the system.)
        """
        pass

    #endregion
