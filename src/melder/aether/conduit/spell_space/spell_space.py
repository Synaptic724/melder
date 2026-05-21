import threading
from typing import TYPE_CHECKING, Optional, Union
from mypy_extensions import mypyc_attr
from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.conduit.meld.meld import Meld


@mypyc_attr(native_class=True)
class SpellSpace(Cleanable):
    """
    Explicit scope handle for `Existence.unique_per_spell_space`.

    Purpose:
        Represent one spellspace-bound resolution window without storing a live
        conduit back-reference. The conduit remains the factory for spellspaces,
        but the runtime scope object carries only the explicit collaborators it
        needs to execute, reset, and unregister itself.

    Contract:
        - Owns one stable spellspace id and one stable owner conduit id.
        - Delegates runtime execution through the injected `Meld`.
        - Clears spellspace-scoped instances through the injected `Creations`.
        - Unregisters itself from the injected spellspace registry on cleanup.
        - Enforces active-scope usage before `meld(...)` delegates.

    Threading:
        - Uses an internal `RLock` for cleanup/reset idempotence.

    Lifecycle:
        - Created by `Conduit.create_spellspace(...)` or `Conduit.enter_spellspace(...)`.
        - Cleanup is idempotent and drops all injected collaborators.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_owner_conduit_id",
        "_meld",
        "_creations",
        "_spellspace_registry",
        "_version",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            meld: Meld,
            creations: Creations,
            spellspace_registry: set[SpellSpace],
    ) -> None:
        """
        Create one explicit spellspace scope.

        Args:
            owner_conduit_id:
                Stable id of the conduit that created this spellspace.
            meld:
                Meld runtime used for explicit spellspace execution.
            creations:
                Creations manager used for spellspace-scoped storage cleanup and
                active-scope discovery.
            spellspace_registry:
                Conduit-owned registry set used for spellspace lifecycle
                bookkeeping and self-unregistration.

        Raises:
            ValueError:
                If any required collaborator is missing or invalid.
        """
        super().__init__()
        if not owner_conduit_id:
            raise ValueError("owner_conduit_id must not be empty.")
        if meld is None:
            raise ValueError("meld must not be None.")
        if creations is None:
            raise ValueError("creations must not be None.")
        if spellspace_registry is None:
            raise ValueError("spellspace_registry must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._owner_conduit_id: str = owner_conduit_id
        self._meld: Meld = meld
        self._creations: Creations = creations
        self._spellspace_registry: set[SpellSpace] = spellspace_registry
        self._version: int = 0

    def cleanup(self) -> None:
        """
        Finalize this spellspace and clear its scoped instances.

        Contract:
            - Idempotent cleanup.
            - Best-effort calls `reset()` before unregistering.
            - Removes this spellspace from the injected registry.
            - Releases all injected collaborators after cleanup.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
        try:
            self.reset()
        finally:
            self._spellspace_registry.discard(self)
            self._cleaned = True
            del self._spellspace_registry
            del self._owner_conduit_id
            del self._meld
            del self._creations

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
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this spellspace.

        Returns:
            str: Owner conduit id injected at construction time.
        """
        self.check_cleaned()
        return self._owner_conduit_id

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
            spell_name: Optional[str] = None,
            *,
            spell: Optional[Union[str, object]] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> object:
        """
        Delegate one meld call through the injected Meld runtime.

        Contract:
            - Requires this SpellSpace to be the currently active spellspace on
              the injected creations manager.
            - Delegates resolution and lifecycle behavior to `Meld`.
            - Propagates runtime failures from the meld pipeline unchanged.

        Returns:
            object: The resolved runtime object returned by `Meld`.

        Raises:
            SpellSpaceScopeError:
                If this spellspace is not the active scope.
            RuntimeError:
                If this spellspace has already been cleaned.
        """
        self.check_cleaned()
        if self._creations.get_active_spellspace() is not self:
            raise SpellSpaceScopeError(
                "SpellSpace.meld() requires this SpellSpace to be the active scope. "
                "Use 'with conduit.enter_spellspace()' to activate it."
            )
        return self._meld.meld(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )

    def reset(self) -> None:
        """
        Clear all spellspace-bound instances for this scope and bump version.

        Contract:
            - Delegates spellspace bucket clearing to the injected creations
              manager.
            - Increments the local version counter after successful clearing.

        Raises:
            RuntimeError:
                If this spellspace has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._creations.clear_spellspace_instances(self._id)
            self._version += 1
