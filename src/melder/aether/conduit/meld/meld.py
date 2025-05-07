import uuid
from typing import Optional, Dict, Any, NamedTuple
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

        # Spellbook: stores all bound spell references by UUID
        self._owned_spell: ConcurrentDict[uuid.UUID, ISpell] = spellbook._spells
        self._contracted: ConcurrentDict[uuid.UUID, ISpell] = spellbook._contracted_spells

        # Lookup maps (interface + name) -> UUID
        self._owned_spells_lookup: ConcurrentDict[tuple, uuid.UUID] = spellbook._lookup_spells
        self._lookup_contracted_spells: ConcurrentDict[tuple, uuid.UUID] = spellbook._lookup_contracted_spells

        # Creation manager (conduit-local instantiation context)
        self._creations = creations

    def meld(self, spell=None, *, spellframe=None, name=None, spell_override: Optional[Dict[str, Any]] = None) -> None:
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



# ──────────────────────────────────────────────────────────────────────────────
# 📘 Spell Entry Matrix (User-facing fields)
# Each row defines how a spell can be resolved logically.
#
# Columns:
# spellname        — The name of the method or class
# interface        — The spellframe (interface or grouping class), or None
# binding_name     — Optional label provided by user to disambiguate multiple bindings
#───────────────────────────────────────────────────────────────────────────────
# SpellType                  | spellname         | interface           | binding_name
#────────────────────────────|-------------------|----------------------|----------------
#NORMAL                      | "MyService"       | None                 | None
#NAMED                       | "MyService"       | None                 | "alpha"
#NORMAL_INTERFACED           | "MyService"       | IMyService           | None
#NAMED_INTERFACED            | "MyService"       | IMyService           | "v1"
#EXISTING_CLASS              | "MyService"       | None                 | None
#EXISTING_INTERFACED_CLASS   | "MyService"       | IMyService           | None
#NORMAL_METHOD               | "process_data"    | None                 | None
#NAMED_METHOD                | "process_data"    | None                 | "process"
#NAMED_METHOD (interfaced)   | "process_data"    | IDataPipeline        | "process"
#NAMED_LAMBDA_METHOD         | "<lambda>"        | IMathOps             | "scale"
# ──────────────────────────────────────────────────────────────────────────────



# ──────────────────────────────────────────────────────────────────────────────
# 📘 Spell Entry Matrix (User-facing fields + bind/meld logic)
#
# Columns:
# spellname        — The name of the method or class
# interface        — The spellframe (interface or grouping class), or None
# binding_name     — Optional label provided by user to disambiguate multiple bindings
#
# Also includes:
# 🔧 bind(...) — How the spell is registered
# 🧩 meld(...) — How the spell is resolved
#───────────────────────────────────────────────────────────────────────────────
# SpellType                  | spellname         | interface           | binding_name | bind(...)                                             | meld(...)
#────────────────────────────|-------------------|----------------------|---------------|-------------------------------------------------------|-------------------------------
#NORMAL                      | "MyService"       | None                 | None          | bind(MyService)                                              | meld(MyService)
#NAMED                       | "MyService"       | None                 | "alpha"       | bind(MyService, name="alpha")                                | meld(MyService, name="alpha")  if already registered in normal interfaced do we throw??
#NORMAL_INTERFACED           | "MyService"       | IMyService           | None          | bind(MyService, spellframe=IMyService)                       | meld(IMyService)
#NAMED_INTERFACED            | "MyService"       | IMyService           | "v1"          | bind(MyService, spellframe=IMyService, name="v1")            | meld(IMyService, name="v1")    if already registered in normal interfaced do we throw??
#EXISTING_CLASS              | "MyService"       | None                 | None          | bind(my_service_instance)                                    | meld(MyService)
#EXISTING_INTERFACED_CLASS   | "MyService"       | IMyService           | None          | bind(my_service_instance, spellframe=IMyService)             | meld(IMyService)
#NORMAL_METHOD               | "process_data"    | None                 | None          | bind(process_data)                                           | meld(process_data)
#NAMED_METHOD                | "process_data"    | None                 | "process"     | bind(process_data, name="process")                           | meld("process")
#NAMED_METHOD (interfaced)   | "process_data"    | IDataPipeline        | "process"     | bind(process_data, name="process", spellframe=IDataPipeline) | meld(IDataPipeline, name="process")
#NAMED_LAMBDA_METHOD         | "<lambda>"        | IMathOps             | "scale"       | bind(lambda x: x+1, name="scale", spellframe=IMathOps)       | meld(IMathOps, name="scale")
# ──────────────────────────────────────────────────────────────────────────────
