from typing import Any, ClassVar, List, Optional, TYPE_CHECKING

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations


class ClusterCreations(Cleanable):
    """
    Facade over a cluster's elected-leader live creation store.

    Purpose:
        Front the `Creations` store owned by a cluster's elected leader conduit
        so every member of the cluster resolves `unique_per_conduit_cluster`
        instances into one shared team-store, regardless of which member owns
        the spell. The facade depends on `Creations`; `Creations` knows nothing
        about clusters.

    Contract:
        - References, never owns, the leader's `Creations`. `unbind()` drops the
          target only; it never cleans the underlying store, because the leader
          conduit owns and cleans that store itself.
        - Has exactly one piece of state callers must respect: `active`. Active
          when an elected leader's store is bound; disabled otherwise.
        - When disabled, the facade cannot be used: `get_creation` and
          `add_creation` raise. A `unique_per_conduit_cluster` meld does not work
          until a leader is elected.

    Threading:
        - No internal lock. The `elect_/unelect_conduit_cluster_leader`
          transactions freeze all melds before they bind/unbind, so the facade
          is never re-targeted while a meld is reading it. Concurrency safety
          comes from that transaction quiesce, not from this facade.

    Lifecycle:
        - `cleanup()` is idempotent: it disables the facade and drops the target
          reference (without cleaning the referenced store), then retires it.

    Registration:
        MELDER KERNEL - guarded. A per-cluster facade bound/unbound by the
        elect/unelect leader transactions; never user-constructed or bound.

    Subsystem Context:
        The cluster-sharing seam of the conduit `creations` subsystem. It fronts
        the `Creations` store owned by a cluster's ELECTED LEADER conduit so that
        every member resolving a `unique_per_conduit_cluster` spell lands in one
        shared team-store regardless of which member owns the spell. The
        elect/unelect-cluster-leader transactions bind and unbind its target;
        `Creations` itself knows nothing about clusters (the dependency points
        one way).

    System Context:
        Cluster-shared uniqueness needs a single home for the instance, but which
        conduit hosts it is a runtime election that can change. This facade is the
        indirection that lets members keep resolving through a stable handle while
        the actual store moves with the leader. It carries NO lock: the
        leader-election transactions freeze all in-flight melds before they
        re-target it, so safety comes from that transaction-level quiesce rather
        than facade-local synchronization - and disabled-until-a-leader-exists is
        an explicit refusal, not a silent empty store.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Facade over a cluster's elected-leader live creation store. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_store", "_active"]

    def __init__(self) -> None:
        """
        Initialize a disabled (unbound) cluster-creations facade.

        Contract:
            - Starts disabled with no target store: the cluster has no elected
              leader yet.

        Returns:
            None.
        """
        super().__init__()
        self._store: Optional[Creations] = None
        self._active: bool = False

    def cleanup(self) -> None:
        """
        Idempotently disable the facade and drop the leader store reference.

        Contract:
            - Disables the facade and drops the target reference without
              cleaning it; the leader conduit owns that store's lifecycle.
            - Idempotent.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._active = False
        del self._store
        del self._active

    def bind(self, store: Creations) -> None:
        """
        Bind the facade to an elected leader's creation store (activate).

        Contract:
            - Sets the target store and marks the facade active.
            - Called only inside the elect-leader transaction, after melds are
              frozen, so it never races a reader.

        Args:
            store:
                The leader conduit's `Creations` to front.

        Returns:
            None.
        """
        self.check_cleaned()
        self._store = store
        self._active = True

    def unbind(self) -> None:
        """
        Disable the facade and remove its target (deactivate).

        Contract:
            - Marks the facade disabled and drops the target reference. Never
              cleans the referenced store.
            - Called only inside the unelect-leader transaction, after melds are
              frozen.
            - Idempotent.

        Returns:
            None.
        """
        self.check_cleaned()
        self._active = False
        self._store = None

    def is_active(self) -> bool:
        """
        Return whether the facade is bound to a leader store.

        Returns:
            bool:
                True when an elected leader's store is bound; False when disabled.
        """
        self.check_cleaned()
        return self._active

    def resolved_store(self) -> "Creations":
        """
        Return the bound elected-leader `Creations`, or raise when inert.

        Purpose:
            Hand the meld front door the concrete leader store so the door can
            run the same get-or-create-once block the lineage route uses,
            locking the real store's `_lock`. The facade itself carries no lock;
            safety while a leader is bound/unbound comes from the
            `elect_/unelect_conduit_cluster_leader` transaction quiesce, not from
            this facade.

        Contract:
            - Returns the bound leader `Creations` when an elected leader is
              active.
            - Raises `RuntimeError` when disabled (no elected cluster leader),
              matching `get_creation` / `add_creation`, so a
              `unique_per_conduit_cluster` meld with no leader hard-errors at the
              meld door instead of resolving into nothing.

        Returns:
            Creations:
                The elected leader's live creation store.

        Raises:
            RuntimeError:
                When the facade is disabled (no elected cluster leader).
        """
        self.check_cleaned()
        if not self._active:
            raise RuntimeError(
                "cluster_creations is disabled: no elected cluster leader."
            )
        return self._store

    def get_creation(self, spell_id: str) -> Optional[Any]:
        """
        Return the shared cluster instance for a spell id, or `None`.

        Contract:
            - Delegates to the bound store.
            - Raises when disabled: a `unique_per_conduit_cluster` lookup with no
              elected leader is a hard error.

        Args:
            spell_id:
                SHA256 spell id to resolve.

        Returns:
            Optional[Any]:
                The shared instance, or `None` when not yet created.

        Raises:
            RuntimeError:
                When the facade is disabled (no elected cluster leader).
        """
        self.check_cleaned()
        if not self._active:
            raise RuntimeError(
                "cluster_creations is disabled: no elected cluster leader."
            )
        return self._store.get_creation(spell_id)

    def add_creation(
            self,
            spell_id: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register the shared cluster instance for a spell id into the leader store.

        Contract:
            - Delegates to the bound store, keyed by `spell_id`.
            - Raises when disabled: creating a `unique_per_conduit_cluster`
              instance with no elected leader is a hard error, never a silent
              drop or orphan.

        Args:
            spell_id:
                SHA256 spell id key.
            item:
                The live instance to store.
            has_disposal_methods:
                Whether disposal metadata is supplied for cleanup.
            disposal_methods:
                Optional disposal method names declared at bind time.

        Raises:
            RuntimeError:
                When the facade is disabled (no elected cluster leader).

        Returns:
            None.
        """
        self.check_cleaned()
        if not self._active:
            raise RuntimeError(
                "cluster_creations is disabled: no elected cluster leader."
            )
        self._store.add_creation(
            spell_id,
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
