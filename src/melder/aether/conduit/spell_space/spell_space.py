from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellSpace
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.helpers.id_builder import IDBuilder


class SpellSpace(Cleanable, ISpellSpace):
    """
    Scope handle for `Existence.unique_per_spell_space`.

    Responsibilities:
    - Track identity/version for a spellspace scope owned by a Conduit.
    - Enforce activation correctness (only the active spellspace can meld).
    - Provide reset/cleanup hooks to clear spellspace-scoped instances.

    Lifecycle:
    - Created by a Conduit via `enter_spellspace()` or direct construction.
    - Must be the active spellspace on the owner Conduit to call `meld(...)`.
    - `reset()` clears spellspace-bound instances and bumps the version counter.
    - `cleanup()` is idempotent and releases the owner reference.
    """
    __melder_internal__ = _mrg.sentinel
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

    def cleanup(self) -> None:
        """
        Finalize this SpellSpace and dispose spellspace-scoped instances.

        Idempotent:
        - Calls reset() (best-effort) to clear spellspace-bound instances.
        - Drops the owner reference.
        - Unregisters from the owner Conduit cleanup registry.
        """
        if self._cleaned:
            return
        try:
            self.reset()
        finally:
            owner = self._owner_conduit
            if owner is not None:
                owner._unregister_spellspace(self)
            self._owner_conduit = None
            self._cleaned = True


    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> str:
        """
        Stable identifier for this SpellSpace.

        Returns:
            str: Unique ID assigned at construction.
        """
        return self._id

    @property
    def owner_conduit(self):
        """
        Owning Conduit for this spellspace.

        Returns:
            The Conduit instance that created/owns this SpellSpace.
        """
        return self._owner_conduit

    @property
    def version(self) -> int:
        """
        Monotonic version number incremented on each reset().

        Returns:
            int: Current version counter.
        """
        return self._version

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ):
        """
        Delegate to the owner Conduit’s `meld`, enforcing this SpellSpace is active.

        Mirrors `Conduit.meld(...)` and supports the same root entry modes:
        - `spell` as a string spell_id
        - `spell` as a spell object (class/function)
        - `spellframe` as a protocol/frame (or string frame key)
        - `spell_name` as a logical name key

        Resolution, reuse, and lifecycle behavior are delegated to the owner
        Conduit’s `Meld`.

        Args:
            spell_name: Logical spell name (string) used for name-based resolution.
            spell: Primary spell identifier (spell_id string or spell object).
            spellframe: Optional spellframe / protocol / string frame key.
            binding_name: Optional binding name (string) used for resolution.
            spell_override: Optional per-call override payload (dict/list/tuple).

        Returns:
            Any: The resolved component instance as returned by the owner Conduit’s `meld`.

        Raises:
            SpellSpaceScopeError: If this spellspace is not the active one on the owner.
            RuntimeError: If this SpellSpace has been cleaned.
            Other errors: Propagated from the owner Conduit’s `meld` (ValueError/TypeError/KeyError/NotImplementedError/etc.).
        """
        self.check_cleaned()
        if self._owner_conduit.get_active_spellspace() is not self:
            raise SpellSpaceScopeError(
                "SpellSpace.meld() requires this SpellSpace to be the active scope. "
                "Use 'with conduit.enter_spellspace()' to activate it."
            )
        return self._owner_conduit.meld(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )

    def reset(self) -> None:
        """
        Clear all spellspace-bound instances for this space and bump version.

        Raises:
            SpellSpaceScopeError: If the owner does not expose spellspace storage.
            RuntimeError: If this SpellSpace has been cleaned.
        """
        self.check_cleaned()
        creations = self._owner_conduit._creations
        if creations is None:
            raise SpellSpaceScopeError("Owner conduit does not expose spellspace storage.")
        creations.clear_spellspace_instances(self._id)
        self._version += 1
