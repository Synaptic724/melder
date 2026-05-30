from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.creations.creations import (
    Creations,
)

if TYPE_CHECKING:
    from melder.aether.conduit.spell_space.spell_space import SpellSpace
    from melder.aether.conduit.spell_space.spell_space_thread_state import (
        SpellSpaceThreadState,
    )


class ConduitCreations(Creations):
    """
    Conduit-owned live creation registry.

    Purpose:
        Extend the scoped `Creations` base with conduit/root-only extraction
        and restore behavior.

    Contract:
        - Inherits singleton/many storage from `Creations`.
        - Does not own spellspace stacks, spellspace buckets, or any active
          spellspace lookup surface.
        - Extract/restore behavior is limited to conduit/root-only scopes.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = (
        "_spellspace_thread_state",
        "_spellspace_registry",
    )

    def __init__(
            self,
            *,
            conduit_id: str,
            spellspace_thread_state: SpellSpaceThreadState,
            spellspace_registry: set["SpellSpace"],
    ) -> None:
        """
        Initialize the conduit-local creation registry.

        Args:
            conduit_id:
                Stable id of the conduit that owns this registry.
            spellspace_thread_state:
                Conduit-owned thread-local spellspace stack used to resolve the
                currently active spellspace for spellspace-scoped runtime calls.
            spellspace_registry:
                Conduit-owned spellspace registry used for spellspace cleanup
                and lookup by id.

        Raises:
            ValueError:
                If `conduit_id` is empty.
        """
        super().__init__(
            owner_conduit_id=conduit_id,
            id=conduit_id,
        )
        self._spellspace_thread_state: SpellSpaceThreadState = (
            spellspace_thread_state
        )
        self._spellspace_registry: set[SpellSpace] = spellspace_registry

    def extract_spell_creations(
            self,
            spell_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Remove and return all conduit/root-owned creations for one spell id.

        Contract:
            - Uses the base scoped extraction behavior.
            - Exists as the conduit/root override seam so conduit-specific
              behavior can diverge later without moving callers again.
        """
        return super().extract_spell_creations(spell_id)

    def restore_spell_creations(
            self,
            spell_id: str,
            creations: List[Dict[str, Any]],
    ) -> None:
        """
        Restore conduit/root-owned creations previously extracted for one spell id.

        Contract:
            - Uses the base scoped restore behavior.
            - Exists as the conduit/root override seam so conduit-specific
              restore policy can diverge later without moving callers again.
        """
        super().restore_spell_creations(spell_id, creations)

    def get_active_spellspace(self) -> Optional["SpellSpace"]:
        """
        Return the currently active spellspace for this conduit context.

        Contract:
            - Reads only the conduit-owned thread-local spellspace stack.
            - Returns `None` when no spellspace is active on the current thread.
        """
        return self._spellspace_thread_state.get_active()

    def get_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
    ) -> Optional[Any]:
        """
        Return one spellspace-owned creation through the active spellspace.

        Contract:
            - Uses the current active spellspace as the routing source of truth.
            - Returns `None` when there is no active spellspace or the active
              spellspace id does not match the requested spellspace id.
            - Reads from the spellspace's own base `Creations` store.
        """
        active_spellspace = self.get_active_spellspace()
        if active_spellspace is None or active_spellspace.id != spellspace_id:
            return None
        return active_spellspace._creations.get_creation(spell_id)

    def register_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one spellspace-owned creation through the active spellspace.

        Contract:
            - Writes only through the current active spellspace's own base
              `Creations` store.
            - Raises when there is no matching active spellspace.
        """
        active_spellspace = self.get_active_spellspace()
        if active_spellspace is None or active_spellspace.id != spellspace_id:
            raise RuntimeError(
                "No matching active spellspace exists for spellspace creation registration."
            )
        active_spellspace._creations.add_creation(
            spell_id,
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Clear one spellspace's owned creation state.

        Contract:
            - Targets the registered spellspace by id.
            - No-ops when the spellspace id is not currently registered.
        """
        for spellspace in self._spellspace_registry:
            if spellspace.id == spellspace_id:
                spellspace._creations.reset_for_pool()
                return

    def push_active_spellspace(self, spellspace: "SpellSpace") -> None:
        """
        Push one spellspace onto the current thread's active stack.
        """
        stack = self._spellspace_thread_state.get()
        stack.append(spellspace)
        self._spellspace_thread_state.set(stack)

    def pop_active_spellspace(self, spellspace: "SpellSpace") -> None:
        """
        Pop the current thread's active spellspace, validating stack identity.
        """
        stack = self._spellspace_thread_state.get()
        if not stack or stack[-1] is not spellspace:
            raise RuntimeError(
                "Spellspace stack corruption detected while exiting spellspace meld."
            )
        stack.pop()
        self._spellspace_thread_state.set(stack)
