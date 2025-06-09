from typing import Type, Optional, Any, Dict, NamedTuple
from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID


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
    def _add_owned_conduit(self, conduit_id: UUID, conduit_name: str = None ):
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
    @abstractmethod
    def _lesser_conduit_spellbook_copy(self) -> 'ISpellbook':
        """
        Returns a copy of the spellbook for use in a lesser conduit.
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Find the spell ID based on the spell frame, spell name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Find the spell key based on the spell frame, spell name, and binding name.
        :param spellframe:
        :param spell_name:
        :param binding_name:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def inspect_spell(self, spell: Any) -> Optional[str]:
        """
        Inspects a spell to find its ID then checks if the spell exists in the Aether.
        :param spell:
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def bind(self, spell: Any, existence: 'Existence', whitelist: Optional[bool] = True, *, spellframe: Optional[Any] = None, name: Optional[str] = None, **kwargs) -> Optional[str]:
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
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def remove_bind(self, spell: Any):
        """
        Removes a spell from the registry. Typically used during teardown
        or re-binding scenarios.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def _find_spell(self, spell_id: UUID) -> Optional[Any]:
        """
        Internal spell resolution by UUID. Useful for resolving specific
        spell references across systems or conduit links.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def conjure(self, policy: Optional[str], name: str = None) -> Any:
        """
        Finalizes configuration and returns a new conduit bound to this Spellbook.

        Args:
            name: Optional name for the conduit.
            policy: Optional policy to apply to the conduit.

        Returns:
            A configured Conduit instance.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_configuration(self) -> 'Configuration':
        """
        Returns the current configuration used by this Spellbook.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def configure_conduit_state(self, **kwargs):
        """
        Apply configuration properties to the conduit before sealing.
        Raises if configuration is already locked.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def lock_configuration(self):
        """
        Locks the configuration to prevent further modification.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def is_configuration_locked(self) -> bool:
        """
        Returns whether the configuration has been locked.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def seal(self):
        """
        Optional system-level lock to finalize and seal the entire Spellbook.
        Typically called once before shutdown or final execution phase.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IBind:
    """
    Interface for a Bind, which is a binding mechanism for spells.
    """
    __slots__ = []

    @abstractmethod
    def bind(self, permissions: str, *, spell=None, spellframe=None, name=None, existence='Existence.unique'):
        """
        Binds a spell to the Spellbook.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IMeld(ISeal):
    """
    Interface for a Meld, which is a process of creating or materializing an object
    from the Conduit's registered spells.
    """
    __slots__ = []
    @abstractmethod
    def meld(self, spell, *, spellframe=None, name=None, spell_override: Optional[Dict[str, Any]] = None):
        """
        Melding is the process of creating or materializing an object
        from the Conduit's registered spells.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class IConduitWard(ISeal):
    """
    Interface for a ConduitWard, which manages the links between conduits.
    """
    __slots__ = []
#region Properties
    @abstractmethod
    @property
    def policy(self) -> 'IPolicy':
        """
        Returns the policy for the conduit ward.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    @policy.setter
    def policy(self, value: policy):
        """
        Sets the policy for the conduit ward.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    @property
    def conduit_type(self) -> 'ConduitState':
        """
        Gets the policy for the conduit ward.
        :return:
        """
        raise NotImplementedError("Subclasses must implement this method.")
#endregion

    @abstractmethod
    def _change_conduit_type(self, conduit_type: 'ConduitState'):
        """
        Changes the conduit type.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def remove_link(self, other_conduit):
        """
        Removes a link between two conduits.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_links(self):
        """
        Returns all active links.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IConduit(ISeal):
    """
    Interface for a Conduit, which behaves as both a scope and a factory within the system.
    """
    __slots__ = []

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Subclasses must implement this method.")

    @name.setter
    @abstractmethod
    def name(self, value: str):
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def link(self, target_conduit: 'IConduit') -> bool:
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

class IConduitCloud(ISeal):
    """
    Interface for a ConduitCloud, which manages multiple Conduits.
    """
    __slots__ = []

    @abstractmethod
    def get_conduit(self, name: str) -> IConduit:
        """
        Returns a Conduit by its name.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class ILink(ISeal):
    """
    Interface for a Link, which represents a connection between two Conduits.
    """
    __slots__ = []
    @abstractmethod
    def sever(self):
        """
        Sever the link between two Conduits.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class IDetail(ISeal):
    @property
    @abstractmethod
    def type(self) -> 'ContractTypes':
        pass

    @abstractmethod
    def affects_permissions(self) -> bool:
        """Indicates whether this detail modifies the spell permission map."""
        pass