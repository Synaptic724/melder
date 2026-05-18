import threading
from typing import Optional
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispellspace import ISpellSpace
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.helpers.id_builder import IDBuilder


class SpellSpace(Cleanable, ISpellSpace):
    """
    Scope handle for `Existence.unique_per_spell_space`.

    `SpellSpace` is the explicit runtime token that marks one spellspace-bound
    resolution window on a conduit. It does not resolve anything by itself; it
    enforces that spellspace-scoped meld calls only happen while this scope is
    the currently active spellspace on the owner conduit.

    Responsibilities:
    - hold one stable identity for the spellspace scope
    - track a monotonic version that changes on reset
    - enforce active-scope usage for spellspace-bound meld calls
    - clear spellspace-scoped instances when reset or cleanup occurs

    Lifecycle:
    - created by a conduit via `enter_spellspace()` or direct construction
    - must be the active spellspace on the owner conduit before `meld()` may
      delegate successfully
    - `reset()` clears spellspace-bound instances and bumps the version counter
    - `cleanup()` is idempotent and detaches the scope from the owner conduit
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_owner_conduit",
        "_version",
    ]

    def __init__(self, owner_conduit) -> None:
        """
        Create one spellspace scope owned by a conduit.

        Args:
            owner_conduit: Conduit that owns this spellspace and will service
                spellspace-scoped meld calls.

        Raises:
            ValueError: If `owner_conduit` is `None`.
        """
        super().__init__()
        if owner_conduit is None:
            raise ValueError("owner_conduit must not be None.")
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._owner_conduit: IConduit = owner_conduit
        self._version: int = 0

    def cleanup(self) -> None:
        """
        Finalize this spellspace and clear its scoped instances.

        Contract:
        - Idempotent cleanup.
        - Best-effort calls `reset()` before detaching from the owner.
        - Unregisters this scope from the owner conduit before releasing the
          owner reference.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
        try:
            self.reset()
        finally:
            owner = self._owner_conduit
            if owner is not None:
                owner._unregister_spellspace(self)
            self._cleaned = True
            del self._owner_conduit

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this spellspace.

        Returns:
            str: Unique id assigned at construction.
        """
        self.check_cleaned()
        return self._id

    @property
    def owner_conduit(self):
        """
        Return the conduit that owns this spellspace.

        Returns:
            The conduit instance that created and owns this spellspace.
        """
        self.check_cleaned()
        return self._owner_conduit

    @property
    def version(self) -> int:
        """
        Return the monotonic version counter for this scope.

        Returns:
            int: Current version, incremented by each successful `reset()`.
        """
        self.check_cleaned()
        return self._version

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
        Delegate to the owner conduit’s `meld`, enforcing active-scope usage.

        Mirrors `Conduit.meld(...)` and supports the same root entry modes:
        - `spell` as a string spell id
        - `spell` as a spell object (class/function)
        - `spellframe` as a protocol/frame or string frame key
        - `spell_name` as a logical name key

        Resolution, reuse, and lifecycle behavior are delegated to the owner
        conduit’s `Meld`.

        Args:
            spell_name: Logical spell name used for name-based resolution.
            spell: Primary spell identifier (spell id string or spell object).
            spellframe: Optional spellframe / protocol / string frame key.
            binding_name: Optional binding name used for resolution.
            spell_override: Optional per-call override payload
                (`dict` / `list` / `tuple`).

        Returns:
            Any: The resolved component instance returned by the owner
            conduit’s `meld`.

        Raises:
            SpellSpaceScopeError: If this spellspace is not the active one on
                the owner conduit.
            RuntimeError: If this spellspace has already been cleaned.
            Other errors: Propagated from the owner conduit’s `meld`
                (`ValueError`, `TypeError`, `KeyError`,
                `NotImplementedError`, and related runtime failures).
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
        Clear all spellspace-bound instances for this scope and bump version.

        Raises:
            SpellSpaceScopeError: If the owner does not expose spellspace
                storage.
            RuntimeError: If this spellspace has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            creations = self._owner_conduit._creations
            if creations is None:
                raise SpellSpaceScopeError(
                    "Owner conduit does not expose spellspace storage."
                )
            creations.clear_spellspace_instances(self._id)
            self._version += 1
