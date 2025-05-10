from typing import Type, Optional, Any, Dict, NamedTuple
from abc import ABC, abstractmethod
from typing import Optional, Any
import uuid
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.utilities.concurrent_dictionary import ConcurrentDict


# We got two of the same types of classes, I wanted to stick to the magic theme because it's pretty fun :P
class ISeal(ABC):
    """
    Abstract base class for all disposable objects in the system.

    Usage:
        Any object that holds threads, memory, open resources, or registration
        within ThreadFactory must implement this.

        Automatically supports context-manager usage:
            with MyObject(...) as obj:
                ...
            # dispose() is called automatically on exit.

    Implementations MUST:
        - Provide a `seal()` method.
        - Register all their cleanups inside `seal()`.
        - Handle multiple calls to `seal()` gracefully.
    """
    __slots__ = ["_sealed"] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    def __init__(self):
        self._sealed = False

    @property
    def sealed(self):
        """
        Check if the object is sealed.
        :return: True if sealed, False otherwise.
        """
        return self._sealed

    @abstractmethod
    def seal(self):
        """
        Seal must be implemented by subclasses.
        It MUST:
            - Release all allocated resources.
            - Kill or join all running threads.
            - Deregister itself from any supervisors or orchestrators.
            - Clear any persistent state to avoid memory leakage.
            - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IDisposable(ABC):
    """
    Abstract base class for all disposable objects in the system.

    Usage:
        Any object that holds threads, memory, open resources, or registration
        within ThreadFactory must implement this.

        Automatically supports context-manager usage:
            with MyObject(...) as obj:
                ...
            # dispose() is called automatically on exit.

    Implementations MUST:
        - Provide a `dispose()` method.
        - Register all their cleanups inside `dispose()`.
        - Optionally provide a `cleanup()` alias.
        - Handle multiple calls to `dispose()` gracefully.
    """
    __slots__ = ["_disposed", ] # Prevents memory leaks by ensuring the object is not kept alive by circular references.

    def __init__(self):
        self._disposed = False

    @property
    def disposed(self):
        """
        Check if the object is sealed.
        :return: True if sealed, False otherwise.
        """
        return self._disposed

    @abstractmethod
    def dispose(self):
        """
        Dispose must be implemented by subclasses.
        It MUST:
            - Release all allocated resources.
            - Kill or join all running threads.
            - Deregister itself from any supervisors or orchestrators.
            - Clear any persistent state to avoid memory leakage.
            - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement this method.")

class ISpell(ISeal):
    """
    Interface for a Spell, which is a unit of magic that can be cast.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def add_spell_details(self, *args, **kwargs):
        """
        Add details to the spell.
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def _add_owned_conduit(self, conduit_id: uuid.UUID):
        """
        Add the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def _add_dag(self, dag: Any):
        """
        Add details to the spell.
        :param dependency_graph: DAG system of dependencies.
        :param existing_object: existing object if applicable.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def cast(self):
        """
        Casts the spell.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class ISpellbook(ISeal):
    """
    Interface for a Spellbook — the central registry and configuration manager
    for all spells in the system. It behaves as a binder, store, and
    configuration authority for conduits.
    """
    @property
    @abstractmethod
    def _spells(self) -> ConcurrentDict[uuid.UUID, ISpell]:
        pass

    @property
    @abstractmethod
    def _contracted_spells(self) -> ConcurrentDict[uuid.UUID, ISpell]:
        pass

    @property
    @abstractmethod
    def _lookup_spells(self) -> ConcurrentDict[tuple, uuid.UUID]:
        pass

    @property
    @abstractmethod
    def _lookup_contracted_spells(self) -> ConcurrentDict[tuple, uuid.UUID]:
        pass

    @abstractmethod
    def bind(self, *, spell: Any, existence: Existence, spellframe: Optional[Any] = None, name: Optional[str] = None):
        """
        Register a new spell with the spellbook.

        Args:
            spell: The class, method, or lambda to register.
            existence: The lifecycle pattern (unique, many, etc.).
            spellframe: Optional interface or grouping type.
            name: Optional user-defined binding name.
        """
        pass

    @abstractmethod
    def remove_bind(self, spell: Any):
        """
        Removes a spell from the registry. Typically used during teardown
        or re-binding scenarios.
        """
        pass

    @abstractmethod
    def _find_spell(self, spell_id: uuid.UUID) -> Optional[Any]:
        """
        Internal spell resolution by UUID. Useful for resolving specific
        spell references across systems or conduit links.
        """
        pass

    @abstractmethod
    def conjure(self, name: Optional[str] = None) -> Any:
        """
        Finalizes configuration and returns a new conduit bound to this Spellbook.

        Args:
            name: Optional name for the conduit.

        Returns:
            A configured Conduit instance.
        """
        pass

    @abstractmethod
    def get_configuration(self) -> Configuration:
        """
        Returns the current configuration used by this Spellbook.
        """
        pass

    @abstractmethod
    def configure_conduit_state(self, **kwargs):
        """
        Apply configuration properties to the conduit before sealing.
        Raises if configuration is already locked.
        """
        pass

    @abstractmethod
    def lock_configuration(self):
        """
        Locks the configuration to prevent further modification.
        """
        pass

    @abstractmethod
    def is_configuration_locked(self) -> bool:
        """
        Returns whether the configuration has been locked.
        """
        pass

    @abstractmethod
    def seal(self):
        """
        Optional system-level lock to finalize and seal the entire Spellbook.
        Typically called once before shutdown or final execution phase.
        """
        pass


class IBind:
    """
    Interface for a Bind, which is a binding mechanism for spells.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.

    @abstractmethod
    def bind(self):
        """
        Binds a spell to the Spellbook.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IMeld(ISeal):
    """
    Interface for a Meld, which is a process of creating or materializing an object
    from the Conduit's registered spells.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def meld(self, spell, *, spellframe=None, name=None, spell_override: Optional[Dict[str, Any]] = None):
        """
        Melding is the process of creating or materializing an object
        from the Conduit's registered spells.
        """
        raise NotImplementedError("Subclasses must implement this method.")



class IConduit(ISeal):
    """
    Interface for a Conduit, which behaves as both a scope and a factory within the system.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def link(self):
        """
        Links this Conduit to another Conduit.
        Only allowed if the world environment is dynamic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def meld(self, spell_name: str, spell_type: str, spellframe: Type = None):
        """
        Melding is the process of creating or materializing an object
        from the Conduit's registered spells.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def create_lesser_conduit(self):
        """
        Creates a new lesser Conduit (child scope) beneath this Conduit.
        """
        raise NotImplementedError("Subclasses must implement this method.")



class ILink(ISeal):
    """
    Interface for a Link, which represents a connection between two Conduits.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def sever(self):
        """
        Sever the link between two Conduits.
        """
        raise NotImplementedError("Subclasses must implement this method.")
