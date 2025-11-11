from threading import RLock
# Melder imports
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.general_base.sealable import Sealable
from melder.utilities.helpers.id_builder import IDBuilder


class Detail(Sealable):
    """
    Represents a spell-level permission entry for a specific conduit
    within a contract. This defines what access the conduit has to a spell.

    Fields:
    - spell_id: The identifier of the spell this permission applies to.
    - permissions: Permissions enum (read, create, block).

    Once sealed, the Detail becomes immutable and clears internal state.
    """

    def __init__(self, spell_id: str, permissions: Permissions):
        super().__init__()
        self._lock = RLock()
        self._id: str = IDBuilder.create_id()
        if not isinstance(permissions, Permissions):
            raise TypeError(
                f"permissions must be an instance of Permissions enum, got {type(permissions).__name__}"
            )

        with self._lock:
            self.spell_id: str = spell_id
            self.permissions: Permissions = permissions

    def seal(self):
        """
        Internal

        Seal this detail, nullifying sensitive data and marking it immutable.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True
            self.spell_id = None
            self.permissions = None
