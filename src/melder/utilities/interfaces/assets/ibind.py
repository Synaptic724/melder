from typing import Any, Protocol, Union, runtime_checkable
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.assets.icleanable import ICleanable
from melder.utilities.interfaces.assets.ispell import ISpell

@runtime_checkable
class IBind(ICleanable, Protocol):
    """
    An Interface for a binding mechanism, responsible for profiling and
    registering a spell blueprint.
    """
    _id: str
    def bind(
            self,
            permissions: Permissions,
            existence : Existence,
            *,
            aetheric_frame: str,
            spell=None,
            spellframe=None,
            binding_name=None,
            profile: str = "general",
    ) -> Union[ISpell, Any]:
        """
        Binds a spell, creating its blueprint and returning it.

        Args:
            permissions (Permissions): The access policy for the spell.
            aetheric_frame (str): The Aetheric Frame this bind is part of.
            spell (Any, optional): The class, function, or object to bind.
            spellframe (Any, optional): The logical interface or group.
            binding_name (str, optional): A unique binding name.
            existence (str, optional): The lifecycle policy.

        Returns:
            Union[ISpell, Any]: The newly created ISpell blueprint.
        """
        ...
