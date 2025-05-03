import threading
from abc import ABC, abstractmethod
from typing import Type, Optional, Any


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



class ISpellbook(ISeal):
    """
    Interface for Spellbook, which is a graph structure that behaves like a scope and a factory.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def bind(self, spell):
        """
        Adds a new spell to the Spellbook.
        :param spell: The spell to add.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def remove_bind(self, spell):
        """
        Removes a spell from the Spellbook.
        :param spell: The spell to remove.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class ISpell(ISeal):
    """
    Interface for a Spell, which is a unit of magic that can be cast.
    """
    __slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    @abstractmethod
    def add_spell_details(self):
        """
        Casts the spell.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def add_owned_conduit(self):
        """
        Adds the conduit ID that owns this spell.
        :param conduit_id: The ID of the conduit that owns this spell.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def cast(self):
        """
        Casts the spell.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IBind(ISeal):
    """
    Interface for a Bind, which is a binding mechanism for spells.
    """
    #__slots__ = [] # Prevents memory leaks by ensuring the object is not kept alive by circular references.

    @abstractmethod
    def bind(self):
        """
        Binds a spell to the Spellbook.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def bind_named(self,
        name: str,
        spell: Any,
        spellframe: Type = None,
        existence: Optional[str] = None
    ):
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
    def meld(self):
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
