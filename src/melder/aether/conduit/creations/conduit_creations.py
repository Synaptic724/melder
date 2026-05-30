from typing import Any, ClassVar, Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.creations.creations import (
    Creations,
)


class ConduitCreations(Creations):
    """
    Conduit-owned live creation registry.

    Purpose:
        Extend the scoped `Creations` base with conduit/root-only extraction
        and restore behavior.

    Contract:
        - Inherits singleton/many storage from `Creations`.
        - Uses the conduit id as both the owner-conduit id and the concrete
          scope id.
        - Extract/restore behavior is limited to conduit/root-only scopes.
        - Does not own any spellspace-local request buckets.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    def __init__(
            self,
            *,
            conduit_id: str,
    ) -> None:
        """
        Initialize the conduit-local creation registry.

        Purpose:
            Specialize the generic scoped `Creations` store for conduit-owned
            runtime state by collapsing owner identity and scope identity onto
            the same conduit id.

        Contract:
            - The conduit id is used as both `owner_conduit_id` and `id`.
            - This registry therefore models one conduit/root runtime scope,
              not a request-local spellspace scope.

        Args:
            conduit_id:
                Stable id of the conduit that owns this registry.

        Raises:
            ValueError:
                If `conduit_id` is empty.
        """
        super().__init__(
            owner_conduit_id=conduit_id,
            id=conduit_id,
        )

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
            - Intentionally excludes spellspace-local request objects because
              those live on `SpellSpace`-owned `Creations` instances instead.
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
            - Restores only conduit/root-owned state; it is not a spellspace
              replay surface.
        """
        super().restore_spell_creations(spell_id, creations)
