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

    Owned State:
        None beyond the base. `__slots__` is empty; the conduit id serves as
        BOTH the owner-conduit id and the concrete scope id, which is what makes
        this specialization a behaviour delta rather than a storage delta.

    Threading:
        Inherits the base `RLock` discipline; adds no locks of its own.

    Lifecycle / Cleanup:
        Created in `Conduit.__init__` and cleaned during conduit teardown.
        Inherits the base's idempotent, failure-aggregating disposal.

    Registration:
        MELDER KERNEL - guarded. Constructed only inside `Conduit.__init__`;
        never user-instantiated and never bindable.

    Subsystem Context:
        The conduit/root specialization of the generic `Creations` store, and
        the store `ConduitMeld` reads for caller-local existences
        (`unique_per_conduit`, `many`). Its sibling `ClusterCreations` covers
        cluster scope but extends `Cleanable` directly rather than this class.

    System Context:
        Extract/restore is the reason this subclass exists at all, and it exists
        for one flow: `Conduit.upgrade_to_normal(...)`. Upgrading a lesser
        conduit must PRESERVE the objects already constructed under it - the
        live instances are handed to the promoted conduit rather than rebuilt,
        because rebuilding would hand callers new objects while the old ones are
        still referenced. Restricting extract/restore to conduit/root scopes is
        the safety boundary: spellspace buckets are request-local and must never
        survive a scope transition, so they are deliberately outside this
        class's reach.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Conduit-owned live creation registry. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )

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

        Returns:
            None.
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

        Returns:
            None.
        """
        super().restore_spell_creations(spell_id, creations)
