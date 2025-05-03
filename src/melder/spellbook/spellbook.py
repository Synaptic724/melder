import enum
import uuid
from typing import Optional, List
from melder.utilities.interfaces import ISpellbook, ISeal, ISpell
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit import Conduit
from enum import Enum, auto
import threading


class SpellType(enum.Enum):
    """
    Enum for different types of spells.
    """
    NORMAL = auto()
    NAMED = auto()
    EXISTING_CLASS = auto()
    NORMAL_METHOD = auto()
    NAMED_METHOD = auto()


class Spell(ISpell):
    def __init__(
            self,
            name: str,
            description: str,
            existence: str,
            spell_type: str,
            owner_conduit_id: uuid.UUID = None,
            existing_object: object = None,
            dependency_graph: object = None,  # We'll type it more strictly later if needed
            tags: Optional[List[str]] = None,
            metadata: Optional[dict] = None
    ):
        super().__init__()
        self.spell_type = self.define_spell_type(spell_type)
        self._lock = threading.RLock()

        # Spell Type
        self.owned_spell = None

        # Spell Data
        self.uuid: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.existence: str = existence
        self.description: str = description
        self.owner_conduit_id: uuid.UUID = owner_conduit_id
        self.user_created_object: object = existing_object
        self.dependency_graph = dependency_graph

        # Spell Metadata
        self.tags = tags or []
        self.metadata = metadata or {}

    def define_spell_type(self, value: str) -> enum.Enum:
        """
        Convert a string to an Enum member safely.

        Args:
            enum_class (Type[Enum]): The enum class (e.g., SpellType).
            value (str): The string representation of the enum name.

        Returns:
            Enum: The corresponding Enum member.

        Raises:
            ValueError: If the value does not match any enum member.
        """
        with self._lock:
            try:
                return SpellType[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' is not a valid member of {SpellType.__name__}")

    def add_spell_details(self, dependency_graph: object, existing_object: object = None):
        """
        Add details to the spell.
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        with self._lock:
            self.dependency_graph = dependency_graph
            self.user_created_object = existing_object

    def add_owned_conduit(self, conduit_id: uuid.UUID):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        with self._lock:
            self.owner_conduit_id = conduit_id

    def __repr__(self):
        return f"Spell(name={self.name}, uuid={self.uuid}, owner={self.owner_conduit_id})"

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
        # Normal instance variables here
        super().__init__()
        self._lock = threading.RLock()
        self._conjured = False
        self._configuration_locked: bool = False
        self._configuration = Configuration()
        self._spells: ConcurrentDict[uuid.UUID, Spell] = ConcurrentDict()
        self._contracted_spells: ConcurrentDict[uuid.UUID, Spell] = ConcurrentDict()


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


    def seal(self):
        pass
