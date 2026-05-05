from typing import Any, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IMeld(ICleanable, Protocol):
    """
    An Interface for the object resolution (melding) process.

    This is responsible for taking a spell request, resolving its dependencies,
    and "casting" it into a live object instance.
    """
    _id: str
    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Resolves and creates an instance of a spell.

        Args:
            spell_name (str, optional): Logical spell name key (string).
            spell (str | object, optional): Spell id (string) or spell object.
            spellframe (str | object, optional): Spellframe / protocol / frame key.
            binding_name (str, optional): Binding name used for lookup.
            spell_override (dict | list | tuple, optional): Per-call override payload.
        """
        ...

    def meld_existing_spell(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Any:
        """
        Return an already-existing live object for one resolved spell.
        """
        ...
