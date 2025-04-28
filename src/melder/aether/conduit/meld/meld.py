from typing import Optional
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import IConduit, ISpellbook, ISpell, IMeld
import threading
from melder.aether.conduit.creations.creations import Creations, LesserCreations
from enum import Enum, auto


class Meld(IMeld):
    """
    Meld is a class that represents a conduit for creating and managing spells.
    It provides methods to create, manage, and interact with spells and their configurations.
    """

    def __init__(self, creations: LesserCreations | Creations, spellbook: ISpellbook):
        super().__init__()
        self._lock = threading.RLock()

        # Spellbook
        self._owned_spell = spellbook._spells
        self._contracted = spellbook._contracted_spells

        # Creations
        self._creations = creations


    def meld(self) -> None:
        """
        Meld a spell with a conduit.

        Args:
            spell (ISpell): The spell to meld.
            conduit (IConduit): The conduit to meld with.
        """
        with self._lock:
            raise NotImplementedError("Meld method is not implemented yet.")


    def seal(self) -> None:
        """
        Seal the conduit to prevent further modifications.
        """
        with self._lock:
            if self._sealed:
                return
            self._owned_spell = None
            self._contracted = None
            self._creations = None
            self._sealed = True