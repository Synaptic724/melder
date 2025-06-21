#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

import uuid
from typing import Optional, Dict, Any, NamedTuple
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import IConduit, ISpellbook, ISpell, IMeld
from threading import RLock
from melder.aether.conduit.creations.creations import Creations, LesserCreations
from enum import Enum, auto


class Meld(IMeld):
    """
    Meld is a class that represents a conduit for creating and managing spells.
    It provides methods to create, manage, and interact with spells and their configurations.
    """

    def __init__(self, creations: LesserCreations | Creations, spellbook: ISpellbook):
        super().__init__()
        self._lock = RLock()

        # Spellbook: stores all bound spell references by UUID
        self._owned_spell: ConcurrentDict[str, ISpell] = spellbook._spells
        self._contracted: ConcurrentDict[str, ISpell] = spellbook._contracted_spells

        # Lookup maps (interface + name) -> UUID
        self._owned_spells_lookup: ConcurrentDict[tuple, str] = spellbook._lookup_spells
        self._lookup_contracted_spells: ConcurrentDict[tuple, str] = spellbook._lookup_contracted_spells

        # Creation manager (conduit-local instantiation context)
        self._creations = creations

    def meld(self, spell=None, *, spellframe=None, name=None, spell_override: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Meld a spell with the conduit by resolving it from the spellbook,
        optionally overriding parameters.

        Args:
            spell (Any): Optional UUID or resolution hint for the spell.
            spellframe (Optional[type]): Interface or grouping frame.
            name (Optional[str]): Binding name (used for named/interfaced spells).
            spell_override (Optional[dict]): Parameter overrides for the spell.
        """
        with self._lock:
            if isinstance(spell, uuid.UUID):
                target_spell = self._owned_spell.get(spell) or self._contracted.get(spell)
                if not target_spell:
                    raise KeyError(f"[MELD] No spell found with UUID: {spell}")
            else:
                lookup_key = (spellframe, name or "__default__")
                spell_id = self._owned_spells_lookup.get(lookup_key) or self._lookup_contracted_spells.get(lookup_key)
                if not spell_id:
                    raise KeyError(f"[MELD] No spell found for frame={spellframe}, name={name}")
                target_spell = self._owned_spell.get(spell_id) or self._contracted.get(spell_id)

            # Apply spell override metadata (if any)
            if spell_override:
                target_spell.metadata["spell_override"] = spell_override

            # Register the spell with creations for instancing
            self._creations.register_spell(target_spell)

            print(
                f"[MELD] Melded {target_spell.spell_name} -> {type(self._creations).__name__} | override: {bool(spell_override)}"
            )

    def seal(self) -> None:
        """
        Seal the conduit to prevent further modifications.
        """
        with self._lock:
            if self._sealed:
                return

            self._owned_spell = None
            self._contracted = None
            self._owned_spells_lookup = None
            self._lookup_contracted_spells = None
            self._creations = None
            self._sealed = True
            print("[MELD] Conduit sealed. Resources released.")
