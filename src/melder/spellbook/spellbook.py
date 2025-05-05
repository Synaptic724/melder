import uuid
from typing import Optional, List, Dict, Any, Type, Callable, NamedTuple
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
            existing_object: object = None,
    ):
        super().__init__()
        self._lock = threading.RLock()

        # Spell Type
        self.owned_spell = None

        # Spell Data
        self.spell = spell
        self.spell_id: uuid.UUID = uuid.uuid4()
        self.spellframe: Optional[Any] = spellframe
        self.spell_type: SpellType = spell_type
        self.user_created_object: object = existing_object
        self.binding_name: str = binding_name
        self.spell_name: str = spell_name
        self.existence: Existence = existence
        self.profile: ClassProfile | MethodProfile = profile

        # Spell Metadata
        self.tags = []
        self.metadata = {}

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

    def add_spell_details(self, *args, **kwargs):
        """
        Add details to the spell.
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        with self._lock:
            self.tags = args
            self.metadata = kwargs

    def _add_owned_conduit(self, conduit_id: uuid.UUID):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        with self._lock:
            self._owner_conduit_id = conduit_id

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
    The Spellbook stores all spells and sets the system configuration
    if it's the first Spellbook created.
    """

    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()

        # Configuration
        self._conjured = False
        self._configuration_locked: bool = False
        self._configuration = Configuration()

        self.__spells: ConcurrentDict[uuid.UUID, Spell] = ConcurrentDict()
        self.__lookup_spells: ConcurrentDict[tuple, uuid.UUID] = ConcurrentDict()

        # Contracted Spells — Used for outbound links / remote contracts
        self.__contracted_spells: ConcurrentDict[uuid.UUID, Spell] = ConcurrentDict()
        self.__lookup_contracted_spells: ConcurrentDict[tuple, uuid.UUID] = ConcurrentDict()

        # SpellBinder — Used to register spells from user input
        self._bind = Bind()

#region properties
    @property
    def _spells(self) -> ConcurrentDict[uuid.UUID, Spell]:
        """
        All registered spells (UUID-keyed).
        """
        return self.__spells

    @property
    def _lookup_spells(self) -> ConcurrentDict[tuple, uuid.UUID]:
        """
        Lookup table from (interface, binding_name) to UUID.
        """
        return self.__lookup_spells

    @property
    def _contracted_spells(self) -> ConcurrentDict[uuid.UUID, Spell]:
        """
        Spells contracted from other conduits or networks.
        """
        return self.__contracted_spells

    @property
    def _lookup_contracted_spells(self) -> ConcurrentDict[tuple, uuid.UUID]:
        """
        Lookup table for contracted spells.
        """
        return self.__lookup_contracted_spells

#endregion
#region core methods
    def bind(self, spell, existence: Existence, *, spellframe=None, name=None):
        """
        Binds a new spell into the system via the SpellBinder.
        This stores the UUID and lookup key entry for fast resolution.
        """
        try:
            spell = self._bind.bind(
                spell=spell,
                spellframe=spellframe,
                name=name,
                existence=existence
            )
            self._lookup_spells[spell._key] = spell.spell_id
            self._spells[spell.spell_id] = spell
        except Exception:
            raise

    def _find_spell(self, spell_id: uuid.UUID) -> Optional[Spell]:
        """
        Find a spell by its ID.
        :param spell_id: The ID of the spell to find.
        :return: The found spell or None if not found.
        """
        with self._lock:
            return self._spells.get(spell_id)

    def is_configuration_locked(self) -> bool:
        """
        Check if the configuration for this Spellbook has been locked.
        """
        return self._configuration_locked

    def lock_configuration(self) -> None:
        """
        Lock this Spellbook's configuration, preventing future modification.
        """
        if self._configuration_locked:
            raise RuntimeError("Configuration is already locked.")
        with self._lock:
            self._configuration_locked = True

    def configure_conduit_state(self, **kwargs) -> None:
        """
        Configure the conduit state.

        Only verifies allowed keys at this stage.
        Type and value validation happens during final validation.

        If any configuration errors occur, all attempted settings are cleared.
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
        """
        Get the current configuration of the Spellbook.
        :return: The current configuration.
        """
        return self._configuration

    def conjure(self, name: str = None) -> Conduit:
        """
        Conjure a new Conduit from this Spellbook.

        Automatic mode:
            - Only one conduit per Spellbook.
            - Configuration is frozen once.

        Dynamic mode:
            - Each Spellbook can conjure once.
            - Configuration is frozen the first time.
        """
        with self._lock:
            if self._conjured:
                raise RuntimeError(
                    "This Spellbook has already conjured a Conduit. "
                    "Only one is allowed per Spellbook."
                )

            if not self.is_configuration_locked():
                self._configuration.load_default_dictionary()
                self._configuration.freeze()
                self._configuration_locked = True

            self._conjured = True
            return Conduit(spellbook=self, name=name, conduit_state="normal", configuration=self._configuration)

#endregion

    def seal(self):
        """
        Finalize the Spellbook (optional override).
        """
        pass
