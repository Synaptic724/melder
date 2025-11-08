import uuid
from threading import RLock
from typing import Optional, Dict, Any, NamedTuple, Callable, List, Union
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import IConduit, ISpellbook, ISpell, IMeld
from melder.aether.conduit.creations.creations import Creations, LesserCreations

#TODO: ENSURE MELD SUPPORTS DEBUGGER ACTIONS SUCH AS ATTACHING ID INTO OBJECTS, with SLOTS ignore features


class HookExecutionError(Exception):
    """
    Raised when a lifecycle hook fails during spell melding.

    Attributes:
        phase (str): The hook phase (e.g., 'pre_cast', 'activation', 'post_cast').
        hook_name (str): The name or representation of the hook that failed.
        original_exception (Exception): The original exception that was raised.
    """
    def __init__(self, phase: str, hook_name: str, original_exception: Exception):
        self.phase = phase
        self.hook_name = hook_name
        self.original_exception = original_exception
        super().__init__(f"[HOOK][{phase}] Hook '{hook_name}' failed: {type(original_exception).__name__}: {original_exception}")


class Meld(IMeld):
    """
    Meld is a class that represents a conduit for creating and managing spells.
    It provides methods to create, manage, and interact with spells and their configurations.
    """

    def __init__(self, creations: LesserCreations | Creations, spellbook: ISpellbook):
        super().__init__()
        self._lock = RLock()

        # Spellbook references
        self._owned_spells: ConcurrentDict[str, ISpell] = spellbook._spells
        self._contracted_spells: ConcurrentDict[str, ISpell] = spellbook._contracted_spells

        self._lookup_owned_spells: ConcurrentDict[tuple, str] = spellbook._lookup_spells
        self._lookup_contracted_spells: ConcurrentDict[tuple, str] = spellbook._lookup_contracted_spells

        # Conduit-local instantiation manager
        self._creations = creations

    def meld(
            self,
            spell: str = None,
            *,
            spellframe: str | object = None,
            binding_name: str = None,
            spell_override: Optional[dict | list | tuple] = None
    ) -> Optional[Any]:
        """
        Entry point for resolving and activating a spell.

        Delegates internal responsibilities to specialized methods for clarity.
        """
        with self._lock:
            target_spell = self._resolve_spell(spell, spellframe, binding_name)
            self._apply_override(target_spell, spell_override)
            self._execute_hooks(target_spell.pre_hooks, "pre_cast")
            self._register_spell(target_spell)
            self._execute_hooks(target_spell.activation_hooks, "activation")

            # TODO: Add casting/strategy logic here
            # instance = target_spell.cast()
            # instance = self._apply_spell_strategies(instance, target_spell)

            self._execute_hooks(target_spell.post_hooks, "post_cast")
            return self._finalize_meld(target_spell, spell_override)

    def _resolve_spell(self, spell: Any, spellframe: Any, binding_name: Optional[str]) -> ISpell:
        """
        Normalize the spell key and resolve the actual spell from the registry.
        Supports UUID or (frame, name) based lookup.
        """
        if isinstance(spell, uuid.UUID):
            result = self._owned_spells.get(spell) or self._contracted_spells.get(spell)
            if not result:
                raise KeyError(f"[MELD] No spell found with UUID: {spell}")
            return result

        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name
        )
        lookup_key = (frame_key, bind_key)

        spell_id = self._lookup_owned_spells.get(lookup_key) or self._lookup_contracted_spells.get(lookup_key)
        if not spell_id:
            raise KeyError(f"[MELD] No spell found for frame='{frame_key}', name='{bind_key}'")

        result = self._owned_spells.get(spell_id) or self._contracted_spells.get(spell_id)
        if not result:
            raise RuntimeError("[MELD] Spell ID resolved, but spell object is missing.")
        return result

    def _apply_override(self, spell: ISpell, override: Optional[Union[dict, list, tuple]]):
        """
        Apply optional override data to the spell metadata.
        """
        if override:
            spell.metadata["spell_override"] = override

    def _execute_hooks(self, hooks: List[Callable], phase: str):
        """
        Execute lifecycle hooks for the given phase.

        Args:
            hooks: List of hook functions to invoke.
            phase: One of: "pre_cast", "activation", or "post_cast"

        Raises:
            HookExecutionError: If any hook raises an exception.
        """
        for hook in hooks:
            try:
                hook()
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(phase, hook_name, e) from e

    def _register_spell(self, spell: ISpell):
        """
        Register the spell with the Creations system.
        """
        self._creations.register_spell(spell)

    def _finalize_meld(self, spell: ISpell, override: Optional[Any]) -> None:
        """
        Placeholder for final return value or strategy layer output.

        Args:
            spell (ISpell): The spell that was processed.
            override (Any): Any override data passed during resolution.

        Returns:
            None: This will eventually return a casted object.
        """
        # TODO: Return the constructed or proxied instance in future
        return None

    def seal(self) -> None:
        """
        Seal the conduit to prevent further modifications.

        Once sealed, all internal references are cleared, and no new spells can be melded.
        """
        with self._lock:
            if self._sealed:
                return

            self._owned_spells = None
            self._contracted_spells = None
            self._lookup_owned_spells = None
            self._lookup_contracted_spells = None
            self._creations = None
            self._sealed = True
