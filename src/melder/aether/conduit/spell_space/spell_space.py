from __future__ import annotations

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.helpers.id_builder import IDBuilder


class SpellSpace(Cleanable):
    """
    Scope handle for `Existence.unique_per_spell_space`.

    The owning Conduit manages activation and storage; this object tracks identity,
    ownership, and versioning, and exposes reset/cleanup helpers.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_conduit",
        "_version",
    ]

    def __init__(self, owner_conduit) -> None:
        super().__init__()
        if owner_conduit is None:
            raise ValueError("owner_conduit must not be None.")
        self._id: str = IDBuilder.create_id()
        self._owner_conduit = owner_conduit
        self._version: int = 0

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> str:
        return self._id

    @property
    def owner_conduit(self):
        return self._owner_conduit

    @property
    def version(self) -> int:
        return self._version

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def meld(self, spell_or_key: object, *args, **kwargs):
        """
        Delegate to the owner conduit, enforcing that this SpellSpace is active.
        """
        self.check_cleaned()
        if self._owner_conduit.get_active_spellspace() is not self:
            raise SpellSpaceScopeError(
                "SpellSpace.meld() requires this SpellSpace to be the active scope. "
                "Use 'with conduit.enter_spellspace()' to activate it."
            )
        return self._owner_conduit.meld(spell_or_key, *args, **kwargs)

    def reset(self) -> None:
        """
        Clear all spellspace-bound instances for this space and bump version.
        """
        self.check_cleaned()
        creations = self._owner_conduit._creations
        if creations is None:
            raise SpellSpaceScopeError("Owner conduit does not expose spellspace storage.")
        creations.clear_spellspace_instances(self._id)
        self._version += 1

    def cleanup(self) -> None:
        """
        Finalize this SpellSpace and dispose spellspace-scoped instances.
        """
        if self._cleaned:
            return
        try:
            self.reset()
        finally:
            self._owner_conduit = None
            self._cleaned = True
