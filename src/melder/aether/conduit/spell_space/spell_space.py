import threading
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type, Union, ClassVar

from melder.aether.conduit.creations.creations import Creations
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
if TYPE_CHECKING:
    from melder.aether.conduit.creations.conduit_creations import (
        ConduitCreations,
    )
    from melder.aether.conduit.meld.conduit_meld import ConduitMeld
    from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
    from melder.aether.conduit.spell_space.spell_space_thread_state import (
        SpellSpaceThreadState,
    )



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
        - Delegates runtime execution through one owned `SpellSpaceMeld`.
        - Clears spellspace-scoped instances through the injected `Creations`.
        - Unregisters itself from the injected spellspace registry on cleanup.
        - Does not own conduit-wide resolution caches or control-plane state.
        - Acts as its own context manager for the managed
          `with conduit.enter_spellspace() as space:` lane:
          `enter_spellspace()` acquires and activates the space (pool acquire
          plus thread-stack push) before the `with` statement runs, so
          `__enter__` is a trivial self-return and `__exit__` performs the
          LIFO pop-validated recycle. No per-cycle wrapper object exists.
        - Nested managed scopes are first-class: each `enter_spellspace()`
          call pushes one new independent scope onto the per-thread stack
          (A -> B -> C -> D to any depth), each scope owns its own
          spellspace-local storage, and exits must unwind in LIFO order.
        - One managed activation per acquisition: after `__exit__` recycles
          the space back to the pool, re-entering the same object is a caller
          contract violation (the trusted-private-caller posture documented
          on `SpellSpacePool.release`); LIFO validation in `pop_expected`
          fails fast on the common misuse shapes.

    Threading:
        - Uses an internal `RLock` for cleanup/reset idempotence.
        - The managed enter/exit lane itself is thread-confined by
          construction (pool deque hand-off plus per-thread stack), matching
          the `recycle_from_managed_context` confinement contract.

    Lifecycle:
        - Created by `Conduit.create_spellspace(...)` or `Conduit.enter_spellspace(...)`.
        - Normal cleanup returns the spellspace to its conduit-local pool.
        - Permanent cleanup drops all injected collaborators.

    Registration:
        MELDER KERNEL - guarded, access=public. Users DRIVE it as a context
        manager (`with conduit.enter_spellspace() as space:`) and meld against
        the active space, but never construct or `bind()` it - the conduit is the
        factory and the guard refuses binding.

    Subsystem Context:
        The scope handle of the conduit `spell_space` subsystem, backing
        `Existence.unique_per_spell_space`. The conduit is the factory; this
        object carries only the explicit collaborators it needs (an owned
        `SpellSpaceMeld` for execution, an injected `Creations` for its scoped
        instances, and the registry/pool it unregisters and recycles into). It
        holds NO live conduit back-reference. Managed entry lives on a per-thread
        stack, so nested `enter_spellspace()` scopes (A -> B -> C) each own their
        storage and must unwind LIFO.

    System Context:
        This is how the DGR gives a caller an EXPLICIT, nestable resolution
        window without leaking conduit-wide state into it: instances resolved as
        `unique_per_spell_space` live and die with the space, and `reset()` clears
        them and bumps a version so a recycled space cannot serve stale
        instances. Making the space its own context manager (trivial `__enter__`,
        LIFO-validated `__exit__` recycle) and confining the managed lane to one
        thread is what lets the pool hand spaces back and forth without per-cycle
        wrapper objects or cross-thread synchronization.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Explicit request scope for Existence.unique_per_spell_space. Enter via
        conduit.enter_spellspace(); meld only while it is the ACTIVE spellspace; reset() clears
        spellspace-scoped instances and bumps the version.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_owner_conduit_id",
        "_meld",
        "_creations",
        "_owner_conduit_creations",
        "_registry_tracked",
        "_spellspace_registry",
        "_spellspace_pool",
        "_spellspace_stack_state",
        "_permanent_cleanup_requested",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            conduit_meld: ConduitMeld,
            owner_conduit_creations: ConduitCreations,
            spellspace_registry: set["SpellSpace"],
            spellspace_pool: SpellSpacePool,
            spellspace_stack_state: SpellSpaceThreadState,
    ) -> None:
        """
        Create one explicit spellspace scope.

        Args:
            owner_conduit_id:
                Stable id of the conduit that created this spellspace.
            conduit_meld:
                Conduit-facing meld runtime used as the shared-core source for
                constructing this spellspace's dedicated front door.
            owner_conduit_creations:
                Conduit-owned creations manager used for conduit-scoped
                existences (`unique_per_conduit`, current `many`) beneath the
                spellspace front door.
            spellspace_registry:
                Conduit-owned registry set used for spellspace lifecycle
                bookkeeping and self-unregistration.
            spellspace_pool:
                Conduit-local pool that should receive this spellspace on
                normal cleanup.
            spellspace_stack_state:
                Conduit-owned per-thread active-scope stack holder. Injected
                (not owned) so `__exit__` can perform the LIFO pop-validated
                managed exit without a per-cycle wrapper object. The conduit
                owns its lifecycle; this spellspace only references it.


        Contract:
            - Builds a POOLED, REUSABLE scope object. Its identity is versioned rather
              than object-based precisely so the pool can recycle it: a handle held
              across a recycle boundary fails its active-scope check instead of
              silently attaching to a different request.
            - Constructs its own `Creations` store keyed to this space, so
              spellspace-scoped instances are isolated from conduit-scoped ones.

        Owned State:
            Owns its lock, id and creations store. Borrows the owning conduit's
            registry, meld runtime and thread-state holder.

        Threading:
            Creates the lock guarding later scope operations.

        Lifecycle / Cleanup:
            Reset returns it to the pool and bumps its version; permanent cleanup is
            what actually destroys it.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._owner_conduit_id: str = owner_conduit_id
        self._creations: Creations = Creations(
            owner_conduit_id=owner_conduit_id,
            id=self._id,
        )
        self._owner_conduit_creations: ConduitCreations = owner_conduit_creations
        # A spellspace is not a lineage root: a `unique_per_conduit_lineage`
        # spell resolved from within it stores in the owner conduit's lineage
        # root, so the spellspace meld is handed the owner conduit's lineage-root
        # store (`conduit_meld._root_creations`) and uses it for those melds.
        # Likewise a spellspace is not a cluster member: a
        # `unique_per_conduit_cluster` spell resolved from within it stores in
        # the owner conduit's elected-leader store, so the spellspace meld
        # references the owner conduit's cluster facade
        # (`conduit_meld._cluster_creations`) rather than owning its own. The
        # facade is filled on election by ConduitCluster, so a spellspace built
        # after election still resolves into the same leader store.
        self._meld: SpellSpaceMeld = SpellSpaceMeld(
            spellspace=self,
            spellspace_creations=self._creations,
            conduit_creations=self._owner_conduit_creations,
            root_creations=conduit_meld._root_creations,
            cluster_creations=conduit_meld._cluster_creations,
            spellbook=conduit_meld._spellbook,
            conduit_id=conduit_meld._conduit_id,
            resolution_conduit_id=conduit_meld._resolution_conduit_id,
            dynamic_environment=conduit_meld._dynamic_environment,
            meld_hooks=conduit_meld._meld_hooks,
        )
        # A temporary owner map must be reset on return even when this Space
        # never registers a callback itself.
        self._meld._inherit_meld_hooks(conduit_meld)
        self._registry_tracked: bool = False
        self._spellspace_registry: set[SpellSpace] = spellspace_registry
        self._spellspace_pool: SpellSpacePool = spellspace_pool
        self._spellspace_stack_state: SpellSpaceThreadState = (
            spellspace_stack_state
        )
        self._permanent_cleanup_requested: bool = False

    def __enter__(self) -> "SpellSpace":
        """
        Return this already-activated managed spellspace.

        Contract:
            - `Conduit.enter_spellspace()` performs the real activation work
              (pool acquisition plus per-thread stack push) before the `with`
              statement begins, so this method is a trivial self-return on
              the hot path.
            - Valid only for spaces handed out by `enter_spellspace()`; using
              a manually created (`create_spellspace()`) space as a context
              manager raises `SpellSpaceScopeError` on exit because it was
              never pushed onto the per-thread stack.

        Returns:
            SpellSpace: This spellspace, active as the current top-of-stack
            scope for the calling thread.
        """
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Pop this scope off the per-thread stack and recycle it.

        Contract:
            - Validates LIFO integrity: this space must be the current
              top-of-stack scope for the calling thread (nested scopes must
              unwind innermost-first).
            - Recycles through the managed pooled fast lane, which clears
              spellspace-local creations before pool return so scope teardown
              stays deterministic and owner-driven.
            - Runs on exceptions too, exactly like the former wrapper.
            - After exit this object belongs to the pool again; re-entering
              it without a fresh `enter_spellspace()` acquisition is a caller
              contract violation.

        Raises:
            SpellSpaceScopeError:
                If this space is not the calling thread's active top-of-stack
                scope.

        Returns:
            None.
        """
        self._spellspace_stack_state.pop_expected(self)
        self.recycle_from_managed_context()
        return None

    def cleanup(self) -> None:
        """
        Cleanup this spellspace through either the reusable or permanent lane.

        Contract:
            - Normal cleanup returns this spellspace to the conduit-local pool
              after reusable cleanup.
            - `permanent_cleanup()` forces the destructive lane even when a
              pool is attached.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self._permanent_cleanup_requested:
                self._cleanup_for_destroy()
                return
            self._cleanup_for_pool_reuse()
        self._spellspace_pool.release(self)

    def permanent_cleanup(self) -> None:
        """
        Permanently destroy this spellspace instead of returning it to a pool.

        Contract:
            - Flips the permanent cleanup flag immediately.
            - Reuses the normal cleanup entrypoint so all public teardown still
              flows through one surface.

        Returns:
            None.
        """
        self._permanent_cleanup_requested = True
        self.cleanup()

    def recycle_from_managed_context(self) -> None:
        """
        Recycle one managed pooled spellspace through the fast common lane.

        Purpose:
            Avoid the generic cleanup branch work on the common
            `enter_spellspace()` managed exit path, where the spellspace is
            untracked in the registry and is expected to return directly to the
            conduit-local pool after clearing only spellspace-local state.

        Contract:
            - Valid only for live managed spellspaces acquired through the
              untracked pool path.
            - Falls back to the generic cleanup entrypoint when permanent
              teardown was requested or the spellspace is registry-tracked.
            - Clears spellspace-local creations before returning this
              spellspace to the pool.
            - Keeps collaborator references intact for later reuse, restoring
              temporary hooks after disposal and before idle publication.

        Threading / Concurrency:
            - This lane runs without the spellspace `RLock` because managed
              spellspaces are thread-confined by construction: the pool's
              deque pop hands the object to exactly one thread, the object
              lives only on that thread's `SpellSpaceThreadState` stack, and
              `pop_expected(...)` validates LIFO ownership before this method
              runs. The pool's deque append on release is the hand-off point
              to the next acquiring thread.
            - The spellspace-local clear uses
              `Creations.reset_for_pool_unlocked()`: the same thread
              confinement that justifies skipping the spellspace lock also
              covers the store's internal lock on this lane. The clear remains
              explicit and immediate, not deferred; disposal-bearing stores
              still fall back to the fully locked teardown flow inside that
              method.
            - Concurrent external `cleanup()` / `permanent_cleanup()` against
              an in-flight managed spellspace is a caller contract violation
              (the object is not idle in the pool and not registry-tracked),
              matching the trusted-private-caller posture documented on
              `SpellSpacePool.release(...)`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if self._permanent_cleanup_requested or self._registry_tracked:
            self.cleanup()
            return
        # Common unchanged path is lock-free by the confinement contract above;
        # a temporary hook map uses the existing Meld lock only while resetting.
        # The unlocked variant is valid here precisely because this lane is
        # the confinement-guaranteed managed exit; the explicit
        # spellspace-local clear still happens before pool return so scope
        # teardown stays deterministic and owner-driven.
        self._creations.reset_for_pool_unlocked()
        if self._meld._meld_hooks_modified:
            self._meld._reset_pooled_meld_hooks()
        self._spellspace_pool.release(self)
        
    def _cleanup_for_pool_reuse(self) -> None:
        """
        Clear spellspace-scoped runtime state so this object can be retained.

        Contract:
            - Clears spellspace-scoped creations for this spellspace id.
            - Removes this spellspace from the active registry only when the
              current lifecycle path registered it there.
            - Still tolerates direct/manual registry insertion paths by
              discarding the spellspace when it is currently present.
            - Keeps collaborator references intact for later reuse.
            - Restores temporary Meld hooks after disposal, before idle publication.
        """
        self._creations.reset_for_pool()
        if self._registry_tracked or self in self._spellspace_registry:
            self._spellspace_registry.discard(self)
            self._registry_tracked = False
        self._permanent_cleanup_requested = False
        if self._meld._meld_hooks_modified:
            self._meld._reset_pooled_meld_hooks()

    def _cleanup_for_destroy(self) -> None:
        """
        Permanently destroy this spellspace and release collaborator references.

        Contract:
            - Clears spellspace-scoped creations before dropping references.
            - Removes this spellspace from the current registry when tracked.
            - Still tolerates direct/manual registry insertion paths by
              discarding the spellspace when it is currently present.
            - Deletes the pool reference as part of final teardown.
            - Cleans the owned Meld before dropping it, releasing both hook references.
        """
        self._creations.cleanup()
        self._meld.cleanup()
        if self._registry_tracked or self in self._spellspace_registry:
            self._spellspace_registry.discard(self)
        self._cleaned = True
        del self._registry_tracked
        del self._spellspace_registry
        del self._owner_conduit_id
        del self._meld
        del self._creations
        del self._owner_conduit_creations
        del self._spellspace_pool
        del self._spellspace_stack_state
        del self._permanent_cleanup_requested

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this spellspace.

        Contract:
            - The space's versioned identity, assigned at construction.
            - NOT `check_cleaned()` guarded, so it stays readable on a recycled or
              cleaned space - useful for logging a space you no longer hold.

        Threading:
            Unsynchronized read; safe from any thread.

        Lifecycle / Cleanup:
            Readable after cleanup, by design.

        Returns:
            str: Unique id assigned at construction.
        """
        return self._id

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this spellspace.

        Contract:
            - The conduit this space belongs to, fixed at construction - a pooled space
              is never re-homed to a different conduit.
            - NOT `check_cleaned()` guarded, matching `id`.

        Threading:
            Unsynchronized read; safe from any thread.

        Lifecycle / Cleanup:
            Readable after cleanup, by design.

        Returns:
            str: Owner conduit id injected at construction time.
        """
        return self._owner_conduit_id

    def meld(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_id: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            override: Optional[Union[dict, list, tuple]] = None,
    ) -> object:
        """
        Delegate one meld call through the injected Meld runtime.

        Call shape:
            Positional strings are human SpellNames. Machine callers use
            keyword-only `spell_id=...`. A warm id meld is served here from the
            spellspace door's fast-door entry; any other id meld is forwarded
            positionally to the door's existing ID fast lane.

        Contract:
            - Delegates resolution and lifecycle behavior to the shared
              conduit meld runtime through its spellspace front door.
            - Keeps human `spell` and machine `spell_id` identities mutually
              exclusive.
            - Warm id lane (2026-09-26): a `spell_id=...` meld with no
              `spell`, `spellframe` or `binding_name` reads the door's
              fast-door entry and applies the same guard ladder and arms as
              `SpellSpaceMeld.meld` (plain, non-empty dict override, bound
              existing object). A hit returns without entering the door; a miss
              or any failed guard continues in the door, so results, errors and
              the cache-emit check are identical to calling the door.
            - Propagates runtime failures from the meld pipeline unchanged.

        Returns:
            object: The resolved runtime object returned by the shared meld runtime.

        Args:
            spell:
                Human SpellName string or concrete spell/frame object.
            spell_id:
                Optional canonical SHA256 machine identity.
            override:
                Optional positional or keyword override payload.
        """
        # Warm id lane (2026-09-26): the dominant scoped call - `spell_id=...` alone - reads the
        # spellspace door's fast-door entry here, saving the door frame and its keyword marshaling on
        # a hit. The guard ladder and both arms mirror `SpellSpaceMeld.meld` and `Conduit.meld`
        # exactly (`Meld._fast_meld_doors` lists every reader); only guard reads sit inside the
        # AttributeError try, so an executor's own AttributeError is never swallowed. A miss continues
        # in the door's positional id lane; every other call shape keeps the path below.
        if (
            type(spell_id) is str
            and spell is None
            and spellframe is None
            and binding_name is None
        ):
            meld_door = self._meld
            fast_entry = meld_door._fast_meld_doors.get(spell_id)
            if fast_entry is not None:
                (
                    door_spell,
                    captured_context,
                    captured_epoch,
                    existing_object_entry,
                ) = fast_entry
                fast_executor = None
                try:
                    if (
                        not meld_door._meld_hooks
                        and door_spell._door_epoch == captured_epoch
                        and door_spell._creation_context is captured_context
                        and not meld_door._spellbook._spellbook_validation_required
                    ):
                        # Slots are read per hit: hydration swaps them in place.
                        if override is None:
                            fast_executor = captured_context._no_overrides_instance_executor
                        elif type(override) is dict and override:
                            fast_executor = captured_context._overrides_executor
                except AttributeError:
                    # Cleaned spell/context: guard miss; the door decides.
                    fast_executor = None
                if fast_executor is not None:
                    if override is None:
                        if existing_object_entry:
                            # Existing object: the door returns this same bound slot.
                            instance = door_spell.user_created_object
                        else:
                            instance = fast_executor(meld_door)
                    else:
                        instance = fast_executor(meld_door, override)[0]
                    spellbook = meld_door._spellbook
                    if spellbook._cache_emit_required:
                        spellbook._emit_cache_file_if_required()
                    return instance
            if override is None:
                return meld_door.meld(spell_id)
            return meld_door.meld(spell_id, spell_override=override)
        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")

        internal_spell = spell
        internal_spell_name = None
        if spell_id is not None:
            internal_spell = spell_id
        elif isinstance(spell, str):
            internal_spell = None
            internal_spell_name = spell

        return self._meld.meld(
            internal_spell,
            spell_name=internal_spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=override,
        )

    def purge(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_id: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            purge_all: bool = True,
    ) -> int:
        """
        Purge a registered target's retained creations from this SpellSpace.

        Purpose:
            Expose request-local retirement through the owned SpellSpaceMeld
            door while keeping this explicit scope usable.

        Contract:
            - SpellSpaceMeld authorizes only many and unique_per_spell_space.
            - The target store is always this space's own Creations. No conduit,
              Spell owner, lineage-root or cluster-leader store can be selected.
            - Identity normalization follows meld's name/type/frame/id rules.
            - Purge does not exit the scope, pop its stack or return it to a pool.

        Args:
            spell:
                Logical name, class/function reference or application instance.
                An instance is inspected for its class before ordinary lookup.
                The original reference is retained for single-object removal.
            spell_id:
                Explicit machine identity, mutually exclusive with spell.
            spellframe:
                Optional frame/type used by ordinary binding discovery.
            binding_name:
                Optional binding name within that frame.
            purge_all:
                True removes every retained local entry for the target. False
                requires an instance as spell and removes only that object.

        Returns:
            int:
                Removed local creation count; zero when none are retained.

        Raises:
            ValueError:
                If selectors conflict, no target is supplied, or single-object
                removal is requested without an instance.
            KeyError:
                If normal meld discovery cannot find the binding.
            RuntimeError:
                If permanently cleaned or the target has a broader lifetime.
            TypeError:
                If purge_all is not a bool.
            ExceptionGroup:
                Disposal failures after selected local entries have been removed.

        Threading / Lifecycle:
            Creations uses this space's store lock and releases it before
            disposal. Direct manual use needs no active managed stack entry.
            Managed thread confinement and pool ownership rules remain unchanged;
            a returned/recycled space must not be used through an old reference.
        """
        self.check_cleaned()
        if spell is not None and spell_id is not None:
            raise ValueError("purge accepts either `spell` or `spell_id`, not both.")
        internal_spell = spell
        internal_spell_name = None
        if spell_id is not None:
            internal_spell = spell_id
        elif isinstance(spell, str):
            internal_spell = None
            internal_spell_name = spell
        return self._meld.purge(
            internal_spell,
            spell_name=internal_spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
            purge_all=purge_all,
        )

    # Machine identity remains explicit at the public boundary via `spell_id=`;
    # this scope forwards it positionally into the internal ID fast lane.
