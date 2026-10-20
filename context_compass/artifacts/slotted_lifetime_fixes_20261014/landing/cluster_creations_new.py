from typing import Any, ClassVar, List, Optional, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations


class ClusterCreations(Cleanable):
    """
    Facade over a cluster's team store, active while the cluster has an elected leader.

    Purpose:
        Front the `Creations` team store that a `ConduitCluster` owns, so every
        member of the cluster resolves `unique_per_conduit_cluster` instances
        into one shared store, regardless of which member owns the spell. The
        facade depends on `Creations`; `Creations` knows nothing about clusters.

    Contract:
        - References, never owns, the cluster's team store. `unbind()` drops the
          target only; it never cleans the underlying store, because the cluster
          owns and cleans that store itself (0.2.8237; until then the target was
          the elected leader conduit's own `Creations`, which that conduit
          cleaned with itself).
        - Has two pieces of state callers must respect: `active` and
          `leader_conduit_id`. Active when the cluster has an elected leader and
          the team store is bound; disabled otherwise. `leader_conduit_id` is the
          elected leader's conduit id while active (the conduit with purge
          authority over the store) and None while disabled.
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
          reference and the leader id (without cleaning the referenced store),
          then retires it.

    Registration:
        MELDER KERNEL - guarded. A per-root facade bound/unbound by the
        elect/unelect leader transactions; never user-constructed or bound.

    Subsystem Context:
        The cluster-sharing seam of the conduit `creations` subsystem. It fronts
        the `Creations` team store owned by a `ConduitCluster` so that every
        member resolving a `unique_per_conduit_cluster` spell lands in one
        shared store regardless of which member owns the spell. The
        elect/unelect-cluster-leader transactions bind and unbind its target;
        `Creations` itself knows nothing about clusters (the dependency points
        one way).

    System Context:
        Cluster-shared uniqueness needs a single home for the instance, and the
        home is the cluster: a leader is a runtime election that can change, so
        the store belongs to the cluster and outlives every election, and the
        facade only says whether it is being served (a leader is elected) and by
        whose authority. It carries NO lock: the leader-election transactions
        freeze all in-flight melds before they re-target it, so safety comes
        from that transaction-level quiesce rather than facade-local
        synchronization - and disabled-until-a-leader-exists is an explicit
        refusal, not a silent empty store.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Facade over a cluster's team store, active while the cluster has an
        elected leader. Melder kernel machinery: read it to understand the runtime, do not drive
        it directly.
    """

    __slots__ = Cleanable.__slots__ + ["_store", "_active", "_leader_conduit_id"]

    def __init__(self) -> None:
        """
        Initialize a disabled (unbound) cluster-creations facade.

        Contract:
            - Starts disabled with no target store and no leader id: the root is
              in no cluster with an elected leader yet.

        Returns:
            None.
        """
        super().__init__()
        self._store: Optional[Creations] = None
        self._active: bool = False
        self._leader_conduit_id: Optional[str] = None

    def cleanup(self) -> None:
        """
        Idempotently disable the facade and drop the team store reference.

        Contract:
            - Disables the facade and drops the target reference and the leader
              id without cleaning the store; the cluster owns that store's
              lifecycle.
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
        del self._leader_conduit_id

    def bind(self, store: Creations, leader_conduit_id: str) -> None:
        """
        Bind the facade to the cluster's team store under an elected leader (activate).

        Contract:
            - Sets the target store and the elected leader's conduit id and marks
              the facade active.
            - Called only inside the elect-leader transaction (or the join
              transaction of a member joining a cluster with a leader), after
              melds are frozen, so it never races a reader.

        Args:
            store:
                The cluster's team store (`ConduitCluster._team_store`) to front.
            leader_conduit_id:
                Conduit id of the elected leader: the conduit with purge
                authority over the store while it stays elected.

        Returns:
            None.
        """
        self.check_cleaned()
        self._store = store
        self._leader_conduit_id = leader_conduit_id
        self._active = True

    def unbind(self) -> None:
        """
        Disable the facade and remove its target (deactivate).

        Contract:
            - Marks the facade disabled and drops the target reference and the
              leader id. Never cleans the referenced store.
            - Called only inside the unelect-leader transaction, after melds are
              frozen, or by a member's exit.
            - Idempotent.

        Returns:
            None.
        """
        self.check_cleaned()
        self._active = False
        self._store = None
        self._leader_conduit_id = None

    def is_active(self) -> bool:
        """
        Return whether the facade is bound to the team store under an elected leader.

        Returns:
            bool:
                True when the cluster has an elected leader and the team store is
                bound; False when disabled.
        """
        self.check_cleaned()
        return self._active

    @property
    def leader_conduit_id(self) -> Optional[str]:
        """
        Return the elected leader's conduit id while the facade is active, else None.

        Purpose:
            Name the conduit with purge authority over the cluster's team store.
            The store's own `owner_conduit_id` is the cluster id (the cluster owns
            the store), so the meld's purge authority reads the leader from here
            (0.2.8237).

        Returns:
            Optional[str]: The elected leader's conduit id, or None while disabled.

        Raises:
            RuntimeError: If the facade has been cleaned.
        """
        self.check_cleaned()
        return self._leader_conduit_id

    def resolved_store(self) -> "Creations":
        """
        Return the bound team store, or raise when inert.

        Purpose:
            Hand the meld front door the concrete team store so the door can
            run the same get-or-create-once block the lineage route uses,
            holding the real store's `slot_guard(spell_id)` across the build
            (the store's `_lock` is only a leaf around publish). The facade
            itself carries no lock;
            safety while a leader is bound/unbound comes from the
            `elect_/unelect_conduit_cluster_leader` transaction quiesce, not from
            this facade.

        Contract:
            - Returns the cluster's team store when a leader is elected (active).
            - Raises `RuntimeError` when disabled (no elected cluster leader),
              matching `get_creation` / `add_creation`, so a
              `unique_per_conduit_cluster` meld with no leader hard-errors at the
              meld door instead of resolving into nothing.

        Returns:
            Creations:
                The cluster's live team store.

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
        Register the shared cluster instance for a spell id into the team store.

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
