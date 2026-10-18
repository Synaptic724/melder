from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell

class ManyDisposalBucket:
    """
    Cleanup-only record of one `many` key that declared disposal methods.

    Purpose:
        Replace the per-entry `(object, disposal_methods)` tuples a many key
        used to mirror into `_disposable_creations` with one record per key
        (2026-10-01): the key's live bucket, aliased, plus the Spell-owned
        method list recorded once. A warm registration is then one list append
        instead of a tuple allocation and two appends.

    Contract:
        - `entries` IS the live many bucket held in `_creations` - the same
          list object, never a copy - so the live and disposal views cannot
          diverge and a single-object purge needs one removal.
        - `methods` is the Spell's established ordered disposal list, retained
          by reference (never matched, reordered or copied), identical for
          every entry of the key: a spell id hashes its resolved disposal
          names, so one key carries one declaration.
        - Both fields are borrowed. The owning `Creations` store detaches the
          record (cleanup, clear, purge, extract) and disposes from it; the
          record itself owns nothing and needs no cleanup.

    AGENT_ACCESS: internal
    """

    __slots__ = ("entries", "methods")

    def __init__(self, entries: List[object], methods: List[str]) -> None:
        """
        Bind the key's live bucket and its disposal list.

        Args:
            entries: The live many bucket of the key (aliased, not copied).
            methods: The Spell-owned ordered disposal method names.

        Returns:
            None.
        """
        self.entries = entries
        self.methods = methods


class HolderDisposalEntry:
    """
    Cleanup-only record of one slotted holder and the `many` children built for it.

    Purpose:
        Keep a holder's disposal-bearing `many` children with the holder
        (slotted_lifetime_ownership, 0.2.8238). Since 0.2.8235 an emitted miss
        registers each child in the holder's store before it builds the
        holder; once the holder is published, the miss moves those children
        out of their spells' `many` buckets into this record
        (`Creations.adopt_children`). Every store verb keyed by the holder -
        purge, extract/restore for an ownership transfer, whole-store disposal
        - then reaches the children with the holder, through one dict read.

    Contract:
        - `item` is the holder: the object `_creations` holds under the
          holder's spell id.
        - `methods` is the holder Spell's established ordered disposal list,
          retained by reference. It is empty when the holder declares no
          disposal method; the record then exists for the holder's children.
        - `children` lists `(child, child_methods)` pairs in build order;
          `child_methods` is the child Spell's own list, the object its
          `ManyDisposalBucket` carried, retained by reference.
        - A child is in exactly one place: its spell's `many` bucket or one
          holder record, never both.
        - Disposal runs the holder's methods, then each child's, newest child
          first, so a holder whose own disposal uses a child still finds it
          open (`Creations._dispose_holder_entry`).
        - Every field is borrowed. The owning `Creations` store detaches the
          record (cleanup, clear, purge, extract) and disposes from it; the
          record owns nothing and needs no cleanup.

    AGENT_ACCESS: internal
    """

    __slots__ = ("item", "methods", "children")

    def __init__(
            self,
            item: object,
            methods: List[str],
            children: List[Tuple[object, List[str]]],
    ) -> None:
        """
        Bind the holder, its disposal list and its adopted children.

        Args:
            item: The holder object (borrowed).
            methods: The holder Spell's ordered disposal method names (borrowed;
                an empty list when the holder declares none).
            children: `(child, child_methods)` pairs in build order. The list
                object itself is kept.

        Returns:
            None.
        """
        self.item = item
        self.methods = methods
        self.children = children


StoredDisposalEntry = Tuple[object, List[str]]
StoredDisposalValue = Union[StoredDisposalEntry, ManyDisposalBucket, HolderDisposalEntry]


class Creations(Cleanable):
    """
    Scoped live creation registry.

    Purpose:
        Own the live object store for exactly one scoped creations owner
        without conduit spellspace stacks or spellspace-id bucket indirection.

    Contract:
        - One `Creations` instance belongs to one concrete scope id.
        - `_creations` is the authoritative live-object registry for that scope.
        - `_disposable_creations` is cleanup-only metadata and is never used
          for normal runtime retrieval.
        - Unique entries use `spell_id -> object`.
        - Many entries use `spell_id -> list[object]`.
        - Disposal metadata mirrors only entries that declared disposal
          methods:
          - unique: `spell_id -> (object, disposal_methods)`
          - many: `spell_id -> ManyDisposalBucket` whose `entries` IS the
            live many bucket (the same list object, never a copy) and
            whose `methods` is the Spell-owned list recorded once, at the
            key's first registration (2026-10-01; before, a second list of
            `(object, methods)` tuples was appended in step with the live
            bucket, a tuple and a second append per creation). A many key
            therefore carries one disposal declaration: every entry of the
            key is disposal-bearing or none is.
          - a slotted holder that adopted `many` children (0.2.8238):
            `spell_id -> HolderDisposalEntry` (the holder, its methods -
            possibly none - and its children with theirs) in place of the
            tuple. Adopted children leave their spell's bucket, so a `many`
            key holds only objects that no holder owns.
        - Managed pools (2026-10-15, managed_spell_quantity): a root store keeps one
          `ManagedSpellQuantity` per `Existence.managed_spell_quantity` version it
          owns in `_managed_quantities[spell_id]`, a map of its own: `_creations`
          never holds a pool, so lookups, live probes and purge never meet one.
          `ensure_managed_quantity` composes it at owner stamping; cleanup cleans
          the pools before the disposable registry; extract/restore move a pool
          as a `managed` row; an ownership transfer's rollback takes back a pool
          its stamp composed (`discard_managed_quantity`, identity-checked);
          purge returns 0 for a managed spell. The store registers every pool it
          takes with `ReleaseManagedSpell` and unregisters every pool it gives up
          (S4), outside the store lock, so the registry holds exactly the pools
          live stores hold.
        - Cleanup and reusable clearing are explicit, idempotent, and aggregate
          disposal failures.
        - Disposal names are the established Spell-owned list, retained directly
          through registration and in-memory transfer. This store does not match,
          reorder, or clear that list; it owns the entries and their instances.

    Owned State:
        `_owner_conduit_id`, a stable `_id`, one store `RLock`, the two
        registries (`_creations`, `_disposable_creations`), the per-slot
        build-guard table (`_slot_guards`) and the managed pools
        (`_managed_quantities`, spell id -> `ManagedSpellQuantity`, 2026-10-15).

    Threading:
        Two lock roles, and keeping them apart is what makes resolution
        deadlock-free.

        - `_lock` (the store lock) is a LEAF lock over the two registries. It
          is held only for dict reads and writes: publish of disposal-bearing
          entries, many append, child adoption, purge detach, extract/restore
          and whole-store swap. It is never held while acquiring another lock
          and never around user code. (A publish without disposal methods is
          one atomic dict store under the caller's build lock; see
          `add_creation`.)
        - `slot_guard(spell_id)` returns one `RLock` per slot - a spell id
          whose Existence promises at most one object in this store. Generated
          doors and plan steps hold it across recheck -> construct -> publish,
          so only builders of the SAME slot wait for each other. `unique`
          spells use `Spell._lock` for the same job, because a unique spell has
          exactly one slot (its owner store).

        Lock order is always build lock (slot guard or `Spell._lock`) first,
        store lock last. Build locks are taken consumer before provider along
        the dependency graph, which has no cycles, so no wait cycle can form.
        Before 2026-09-25 the store lock itself was held across whole builds;
        a thread holding it could then wait on a unique's `Spell._lock` while
        that unique's builder waited on the store - a deadlock. Reads and writes
        race freely under free-threaded 3.14t, so neither lock is optional.

    Lifecycle / Cleanup:
        Idempotent. Cleanup runs the declared disposal methods and AGGREGATES
        failures rather than stopping at the first one - a single badly behaved
        object must not strand the rest of the scope's teardown, so callers may
        see an ExceptionGroup. Aggregation is per method as well as per object
        (2026-09-27): every declared method of every object runs, and each
        failing method is one `RuntimeError` in the group, chained from the
        exception it raised. Before, an object's first failing method ended
        that object's disposal and the original exception was dropped.

        Disposal runs in REVERSE CREATION ORDER, newest entry first, including
        within a `many` bucket. Resolution registers a dependency before the
        dependent that holds it, so forward teardown would dispose the
        dependency while a dependent's own disposal method may still need it.
        For the same reason a holder's record disposes the holder before the
        children it adopted, newest child first (0.2.8238).
        This covers ordering within ONE scope; ordering between scopes is the
        conduit cleanup cascade's job.

    Registration:
        MELDER KERNEL. The one subclass, `ConduitCreations`, is melder-internal and
        constructed only inside `Conduit.__init__`; there is no injection seam.
        `ClusterCreations` does NOT extend this class - it extends `Cleanable`
        directly. A cluster's team store is a plain `Creations` that its
        `ConduitCluster` builds and owns (0.2.8237).

    Subsystem Context:
        The storage layer beneath `Meld`. Meld decides WHICH store an
        `Existence` routes to; this class is what one such store actually is.
        `ConduitCreations` specializes it for conduit/root scope, and the two
        meld doors read these stores rather than owning object lifetime
        themselves.

    System Context:
        The two-registry split is the important design choice and it is easy to
        misread as duplication. `_creations` is the AUTHORITATIVE live-object
        registry and is the only thing consulted during resolution;
        `_disposable_creations` is cleanup-only metadata that mirrors just those
        entries which declared disposal methods. Keeping them apart means the
        resolution hot path never pays for disposal bookkeeping, and it means
        an object without disposal methods costs nothing extra to track.
        This is also why the store is generic over scope rather than
        conduit-specific: the same structure serves conduit, root, cluster,
        lineage, and spellspace scopes, so a lifetime is expressed by WHICH
        instance holds the object, not by a different storage shape per mode.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Scoped live creation registry. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_owner_conduit_id",
        "_id",
        "_lock",
        "_creations",
        "_disposable_creations",
        "_slot_guards",
        "_managed_quantities",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            id: str,
    ) -> None:
        """
        Initialize one scoped creation registry.

        Purpose:
            Create the smallest live-object store that can own one scope's
            runtime creations without any ambient spellspace-stack or
            conduit-lineage lookup rules.

        Contract:
            - `owner_conduit_id` identifies the conduit that owns the scope.
            - `id` identifies the concrete scope itself (conduit id,
              spellspace id, or another explicit owner id).
            - Initializes one live registry and one detached cleanup-metadata
              registry.
            - Does not pre-populate any spell buckets.

        Args:
            owner_conduit_id:
                Stable id of the conduit that owns the scope.
            id:
                Stable id of the owning scope.

        Raises:
            ValueError:
                If either identifier is empty.

        Returns:
            None.
        """
        super().__init__()
        if not owner_conduit_id:
            raise ValueError("owner_conduit_id must not be empty.")
        if not id:
            raise ValueError("id must not be empty.")

        self._owner_conduit_id: str = owner_conduit_id
        self._id: str = id
        self._lock = RLock()
        self._creations: Dict[str, Any] = {}
        self._disposable_creations: Dict[str, Any] = {}
        # One build guard per slot, created on first use and kept for this
        # store's lifetime (bounded by the number of spell ids built here).
        self._slot_guards: Dict[str, RLock] = {}
        # One pool per managed spell version this (root) store owns, composed at
        # owner stamping (`ensure_managed_quantity`). Kept apart from `_creations`:
        # a pool is not an object, and no resolution path may read one as such.
        self._managed_quantities: Dict[str, ManagedSpellQuantity] = {}
        # Note: resolution-store selection for broad-lived existences
        # (`unique_per_conduit_lineage` lineage root, `unique_per_conduit_cluster`
        # cluster team store) lives on the meld front doors
        # (`ConduitMeld` / `SpellSpaceMeld`), not on this store. `Creations` is a
        # pure scoped live-object bucket and intentionally holds no pointer to
        # any other `Creations`; the resolving door is handed the target store
        # at runtime by the meld instead of dereferencing it off the caller's
        # store.

    def cleanup(self) -> None:
        """
        Dispose tracked entries and permanently retire this registry.

        Contract:
            - Idempotent.
            - Detaches live and disposable registries, and the managed pools,
              before disposal work.
            - Unregisters the managed pools from `ReleaseManagedSpell`, then
              cleans them FIRST, newest first (2026-10-15): a pool is
              composed at conjure, before the uniques its objects hold, so the
              registry's newest-first walk would close those uniques under live
              pooled objects. A pool's cleanup disposes its idle objects and every
              child recorded for its objects; objects out stay their holders'.
            - Uses `_disposable_creations` only for explicit teardown work.
            - Raises `ExceptionGroup` after best-effort disposal attempts; a
              pool's failures join it as their own chained `RuntimeError`s.
            - Drops the live field surface after cleanup so later use fails
              honestly instead of reading stale state.
            - Keeps `_lock` as a deliberate post-cleanup tombstone: a build
              that was already in flight (holding only its slot guard) may
              still publish afterwards, and it must be able to take the store
              lock and observe `_cleaned` instead of failing on a missing
              attribute. See `add_creation`.

        Threading:
            - Performs the detach step under `_lock`.
            - Does not wait for in-flight builds: they hold slot guards, not the
              store lock. A build that publishes after this point is refused
              and its object disposed by `add_creation`.
            - Disposal work happens after detach so callers cannot keep racing
              the live registries while cleanup is executing.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            disposable_creations = self._disposable_creations
            creations = self._creations
            managed_quantities = self._managed_quantities
            self._creations = {}
            self._disposable_creations = {}
            self._managed_quantities = {}

        pools = list(reversed(managed_quantities.values()))
        # Outside the store lock (a leaf): no release can be routed to a pool this store is about to retire.
        self._unregister_managed_quantities(pools)
        errors = self._cleanup_managed_quantities(pools)
        managed_quantities.clear()
        try:
            errors.extend(self._dispose_disposable_registry(disposable_creations))
        except Exception as exc:
            errors.append(exc)
        disposable_creations.clear()
        creations.clear()

        del self._creations
        del self._disposable_creations
        del self._managed_quantities
        del self._slot_guards
        del self._owner_conduit_id
        del self._id
        # `_lock` is intentionally retained (tombstone): a racing publish takes
        # it and observes `_cleaned` rather than a missing attribute.

        if errors:
            raise ExceptionGroup("Errors occurred during cleaning", errors)

    def _attempt_cleanup(self, entry: StoredDisposalEntry) -> List[Exception]:
        """
        Run every declared disposal method of one tracked entry and collect each failure.

        Purpose:
            Dispose one object as fully as its declared methods allow. Each
            method usually releases a different resource, so one failing method
            must not skip the methods declared after it (owner decision,
            2026-09-27; before, the first failure ended the object's disposal).

        Contract:
            - Invokes the method names in their declared order, each exactly
              once, whether or not an earlier one raised.
            - Every method that raises `Exception` - including a name the
              object lacks, as `AttributeError` - yields one `RuntimeError`
              naming the object and the method. Its `__cause__` is the exception
              the method raised, so the original type and traceback survive.
            - The error text never depends on the object's or the exception's
              `__str__` succeeding; see `_describe_for_disposal_error`.
            - A `BaseException` that is not an `Exception` (for example
              `KeyboardInterrupt`) propagates, as before.
            - Does not mutate the entry or its borrowed method-name list.

        Args:
            entry:
                `(object, disposal_method_names)` tuple.

        Returns:
            List[Exception]:
                One wrapped error per failing method, in declared order; empty
                when every method succeeded.
        """
        item, method_names = entry
        errors: List[Exception] = []
        for method_name in method_names:
            try:
                method = item.__getattribute__(method_name)
                method()
            except Exception as ex:
                error = RuntimeError(
                    f"Failed to dispose object {self._describe_for_disposal_error(item)} "
                    f"using method '{method_name}': {self._describe_for_disposal_error(ex)}"
                )
                # A returned (never raised) error gets no implicit chaining, so
                # attach the original explicitly: its type and traceback are what
                # the caller needs to act on the failure.
                error.__cause__ = ex
                errors.append(error)
        return errors

    @staticmethod
    def _describe_for_disposal_error(value: object) -> str:
        """
        Return text for a disposal error without trusting `value.__str__`.

        Purpose:
            A half-disposed object's `__str__` may read the very resource its
            failing disposal just broke. Formatting it inside the error path used
            to raise out of `_attempt_cleanup` and strand every object not yet
            disposed (fixed 2026-09-27).

        Contract:
            - Returns `str(value)` when that succeeds.
            - Otherwise returns `<Type object at 0x...; str() raised ErrorType>`,
              built only from the type name and `id()`, which cannot raise.
            - Best-effort reporting inside disposal: the `Exception` from
              `__str__` is named in the fallback text, not propagated.

        Args:
            value:
                The object being disposed, or the exception one of its methods
                raised.

        Returns:
            str: Text safe to embed in a disposal error message.
        """
        try:
            return str(value)
        except Exception as ex:
            return f"<{type(value).__qualname__} object at {id(value):#x}; str() raised {type(ex).__name__}>"

    def _dispose_many_creations(
            self,
            bucket: ManyDisposalBucket,
    ) -> List[Exception]:
        """
        Dispose every object of one detached many record.

        Purpose:
            Share the multi-object disposal loop between targeted purge and
            whole-store cleanup without constructing a temporary registry.

        Contract:
            - Visit `bucket.entries` newest-first, preserving many disposal
              order.
            - Delegate each object to `_attempt_cleanup` paired with the key's
              one method list (`bucket.methods`), which runs every method name
              in order and returns one error per failing method.
            - Collect every failure and continue with the other objects.
            - Do not mutate the record, clear its borrowed method-name list, or
              reach into a live creation store.

        Args:
            bucket:
                The detached `ManyDisposalBucket` of one many target: its
                `entries` is the detached live bucket, still in registration
                order.

        Returns:
            List[Exception]:
                Disposal failures in attempt order. The caller aggregates or
                raises them after processing its selected retirement set.

        Threading / Lifecycle:
            The caller has already detached the record under the appropriate
            writer lock. This helper takes no lock and owns no scope policy;
            user disposal methods run after the removal locks are released.
        """
        errors: List[Exception] = []
        methods = bucket.methods
        for item in reversed(bucket.entries):
            errors.extend(self._attempt_cleanup((item, methods)))
        return errors

    def _dispose_disposable_registry(
            self,
            disposable_registry: Dict[str, Any],
    ) -> List[Exception]:
        """
        Dispose every entry recorded in one detached disposable registry.

        Purpose:
            Preserve whole-store disposal order while using the same singular
            and many-object mechanics as targeted purge.

        Contract:
            - Singleton metadata delegates to `_attempt_cleanup`.
            - Many buckets delegate to `_dispose_many_creations`.
            - Holder records delegate to `_dispose_holder_entry`: the holder,
              then its adopted children newest-first (0.2.8238). The three-way
              dispatch is inline, as `_dispose_entry` spells it out, so a scope
              exit pays no extra call per record.
            - Collected failures never prevent trying the next selected object;
              every failing method of every object contributes one error.
            - The caller owns registry detachment and final reference release.

        Args:
            disposable_registry:
                Detached cleanup-only metadata mapping.

        Ordering:
            REVERSE CREATION ORDER. Entries are disposed newest-first, and the
            same rule applies inside a `many` bucket. This matters because
            resolution builds a dependency before the dependent that holds it,
            so the dependency is registered FIRST; walking forward would tear it
            down while a dependent's own disposal method may still reach for it.
            No ordering structure is needed to achieve this - `_disposable_creations`
            is a plain dict, dict iteration is insertion-ordered by language
            guarantee, and insertion happens at creation time, so the registry
            already IS the creation-order record.

            This orders teardown WITHIN one scope only. Ordering BETWEEN scopes
            (lesser conduit before root, narrower existence before broader) is
            owned by the conduit cleanup cascade, not by this method.

        Returns:
            List[Exception]:
                Collected disposal failures, in the order the failures occurred.
        """
        errors: List[Exception] = []
        for value in reversed(disposable_registry.values()):
            if isinstance(value, tuple):
                errors.extend(self._attempt_cleanup(value))
            elif isinstance(value, ManyDisposalBucket):
                errors.extend(self._dispose_many_creations(value))
            else:
                errors.extend(self._dispose_holder_entry(value))
        return errors

    def _dispose_holder_entry(self, entry: HolderDisposalEntry) -> List[Exception]:
        """
        Dispose one detached holder record: the holder, then its adopted children.

        Purpose:
            Give every retirement keyed by a holder - whole-store disposal and
            purge - one way to take the holder's `many` children with it
            (0.2.8238).

        Contract:
            - Runs the holder's declared methods first (none when its list is
              empty), then each child's methods, newest child first, so a holder
              whose own disposal uses a child still finds it open.
            - Every method of every object runs even after one fails; each
              failure is one chained `RuntimeError` from `_attempt_cleanup`.
            - Does not mutate the record or its borrowed lists and takes no
              lock: the caller detached the record and released its locks.

        Args:
            entry:
                The detached `HolderDisposalEntry`.

        Returns:
            List[Exception]:
                Disposal failures in attempt order; empty when every method
                succeeded.
        """
        errors = self._attempt_cleanup((entry.item, entry.methods))
        for child, methods in reversed(entry.children):
            errors.extend(self._attempt_cleanup((child, methods)))
        return errors

    def _dispose_entry(self, value: StoredDisposalValue) -> List[Exception]:
        """
        Dispose one detached disposal-registry value, whatever its shape.

        Purpose:
            One dispatch over the three record shapes `_disposable_creations`
            holds, for retirements of one record such as purge (0.2.8238).
            Whole-store disposal runs the same dispatch inline in its loop.

        Contract:
            - An `(object, methods)` tuple goes to `_attempt_cleanup`.
            - A `ManyDisposalBucket` goes to `_dispose_many_creations` (newest
              object first).
            - A `HolderDisposalEntry` goes to `_dispose_holder_entry` (the
              holder, then its children newest-first).
            - Takes no lock; the caller detached the value first.

        Args:
            value:
                The detached record.

        Returns:
            List[Exception]:
                Disposal failures in attempt order.
        """
        if isinstance(value, tuple):
            return self._attempt_cleanup(value)
        if isinstance(value, ManyDisposalBucket):
            return self._dispose_many_creations(value)
        return self._dispose_holder_entry(value)

    def slot_guard(self, spell_id: str) -> RLock:
        """
        Return the build guard for one slot in this store.

        Purpose:
            Give "build this slot at most once" its own lock, so the store lock
            only ever protects the registries and can stay a leaf. A slot is a
            spell id whose Existence promises at most one object in this store:
            `unique_per_conduit`, `unique_per_spell_space`,
            `unique_per_conduit_lineage` and `unique_per_conduit_cluster`.
            (`unique` uses `Spell._lock` instead; `many` has no slot.)

        Contract:
            - Returns the same `RLock` for a spell id on every call for this
              store's lifetime, including across `clear_all()` and
              `reset_for_pool()`.
            - A hit is one lock-free dict read. The first request for a slot
              publishes a new `RLock` with `dict.setdefault`, which is atomic on
              a builtin dict with `str` keys (GIL and free-threaded builds), so
              concurrent first requests converge on one guard.
            - Returning or holding a guard never implies holding `_lock`.
            - Generated doors and plan steps inline the hit as
              `store._slot_guards.get(spell_id) or store.slot_guard(spell_id)`
              (one method call fewer per cold build). `_slot_guards` is
              therefore part of this class's internal contract: a plain
              `dict` of spell id -> `RLock` whose entries are never replaced
              or removed while the store is live.

        Args:
            spell_id:
                Stable spell id of the slot being built or retired.

        Returns:
            RLock:
                The slot's build guard. Re-entrant, so a door and the root plan
                step (or a same-thread nested meld) can both take it.

        Raises:
            AttributeError:
                After `cleanup()`, like every other live-surface read of a
                retired store.

        Threading:
            Callers hold the guard across recheck -> construct -> publish and
            acquire it BEFORE `_lock`, never while holding `_lock`.
        """
        guard = self._slot_guards.get(spell_id)
        if guard is None:
            guard = self._slot_guards.setdefault(spell_id, RLock())
        return guard

    def _refuse_publish_into_cleaned_store(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool,
            disposal_methods: Optional[List[str]],
    ) -> None:
        """
        Dispose an object whose build finished after this store was cleaned, then raise.

        Purpose:
            Keep the "a retired store owns nothing" rule when a build that held
            only its slot guard finishes after `cleanup()`. The object was built
            for this scope, so its declared disposal methods run here rather than
            leaking an undisposed object to the caller.

        Contract:
            - Called only after `add_creation`/`add_many_creations` observed
              `_cleaned` under `_lock`, with that lock already released.
            - Runs every declared disposal method outside any lock, even after
              one of them fails.
            - Always raises; never registers anything.

        Args:
            key: Spell id the object would have been published under.
            item: The just-built object.
            has_disposal_methods: Whether the spell declared disposal methods.
            disposal_methods: The Spell-owned disposal method names.

        Raises:
            RuntimeError:
                Always. Chained from the disposal error when one method failed,
                or from an `ExceptionGroup` of every failure when several did.
        """
        disposal_errors: List[Exception] = []
        if has_disposal_methods:
            disposal_errors = self._attempt_cleanup(
                (item, disposal_methods if disposal_methods is not None else [])
            )
        message = (
            f"{self.__class__.__name__} was cleaned while creation '{key}' was "
            f"being built; the new instance was not registered"
            + (" and its disposal methods were run." if has_disposal_methods else ".")
            + " Quiesce melds on a scope before cleaning it."
        )
        if len(disposal_errors) == 1:
            raise RuntimeError(message) from disposal_errors[0]
        if disposal_errors:
            raise RuntimeError(message) from ExceptionGroup(
                f"Errors occurred disposing creation '{key}'", disposal_errors
            )
        raise RuntimeError(message)

    def add_creation(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one scoped singleton creation.

        Contract:
            - Stores the live object in `_creations`.
            - Stores cleanup metadata in `_disposable_creations` only when
              disposal methods were declared.
            - Rejects duplicate keys across both registries.
            - Treats the stored object itself as the authoritative runtime
              payload; there is no `Creation.value` wrapper in the live store.
            - Retains the supplied disposal list directly, including an empty
              list. Omitted names use an empty list when disposal is enabled.
            - Refuses a cleaned store: the object is disposed (when it declared
              disposal methods) and `RuntimeError` is raised.

        Raises:
            ValueError:
                If the key is already registered.
            RuntimeError:
                If this store was cleaned while the object was being built.

        Threading:
            - Callers hold the slot's build lock (the slot guard, or
              `Spell._lock` for `unique`) - that is what makes "check, build,
              publish" happen once per slot - and never the store lock across
              the build. A caller that still holds `_lock` re-enters it safely.
            - Disposal-bearing entries publish under the store lock (`_lock`)
              as a leaf, because the live and disposal writes must land
              together relative to purge detach, reusable clears and cleanup
              (a clear iterates the detached disposal map).
            - Entries without disposal methods publish with ONE lock-free dict
              write (measured: the leaf lock cost ~58 ns per cold build on
              3.14t). This is safe because the build lock already excludes
              every other publisher of the key, a single dict store is atomic
              on GIL and free-threaded builds, and the only other writers are
              whole-store swaps: a write racing `clear_all()`/`reset_for_pool()`
              lands in the detached generation and is dropped with it (the
              build straddled the clear; there is nothing to dispose). A write
              racing `cleanup()` is a caller contract violation: it is refused
              here, dropped with the detached map, or fails on the retired
              store's missing registry - and has no disposal methods to leak.

        Returns:
            None.
        """
        if not has_disposal_methods:
            if not self._cleaned:
                if key in self._creations or key in self._disposable_creations:
                    raise ValueError(f"Key {key} already exists in creations.")
                self._creations[key] = item
                return
        else:
            with self._lock:
                if not self._cleaned:
                    if key in self._creations or key in self._disposable_creations:
                        raise ValueError(f"Key {key} already exists in creations.")
                    self._creations[key] = item
                    self._disposable_creations[key] = (
                        item,
                        disposal_methods if disposal_methods is not None else [],
                    )
                    return
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )

    def add_many_creations(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one creation into the scoped `many` list for a spell id.

        Contract:
            - Appends the live object into `_creations[key]`.
            - For a disposal-bearing key, records the Spell-owned method list
              ONCE, at the key's first registration, in a `ManyDisposalBucket`
              under `_disposable_creations[key]` whose `entries` is the live
              bucket itself; later registrations of the key append only.
            - Rejects collisions with non-list slots, and a registration whose
              disposal declaration disagrees with the key's existing entries:
              one many key carries one declaration (the spell id hashes the
              resolved disposal names, so a live world cannot produce a mix).
            - Preserves insertion order; the disposal view is the live bucket,
              so the two cannot diverge (BUG-073, 2026-07-17 audit, now by
              construction: the first-use bucket and its record are created
              in one critical section under `_lock`).
            - Retains the supplied disposal list directly; omitted names use
              an empty list when disposal is enabled.
            - Emitted plans and executors call `register_many` instead: the
              same shape without the keyword marshaling and the checks this
              public verb keeps (2026-10-01).

        Threading:
            - Runs under `_lock` (re-entrant, shared with extract/restore/
              clear); every successfully returned managed creation is
              represented in both registries once this method returns.
            - `_lock` is a leaf here: only dict work runs under it. A cleaned
              store is refused the same way as in `add_creation`.

        Raises:
            ValueError:
                If the key already holds a non-list slot, or if the disposal
                declaration disagrees with the key's existing entries.
            RuntimeError:
                If this store was cleaned while the object was being built.

        Returns:
            None.
        """
        with self._lock:
            if not self._cleaned:
                self._append_many_locked(
                    key,
                    item,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )

    def register_many(
            self,
            key: str,
            item: object,
            disposal_methods: List[str],
    ) -> None:
        """
        Register one disposal-bearing `many` creation on the warm path.

        Purpose:
            The registration emitted plans and executors run on every creation
            of a disposal-bearing `many` root (2026-10-01). It is the
            `add_many_creations` shape without the keyword marshaling and the
            checks that verb keeps for callers it cannot trust: one lock, one
            dict read, one list append (measured 204 -> 104 ns per
            registration on 3.14t, GIL off).

        Contract:
            - Precondition, guaranteed by the emitters and NOT checked here:
              `key` is a `many` spell id whose Spell declares disposal methods,
              and `disposal_methods` is that Spell's own ordered list, the same
              object on every call for the key. A spell id hashes its resolved
              disposal names, so one key cannot carry two declarations, and one
              Existence per Spell means the key's live slot is a list or absent.
              Callers that cannot promise this use `add_many_creations`.
            - The first registration of the key creates the live bucket and
              its `ManyDisposalBucket` record (the bucket itself plus the
              method list) in one critical section; every later one appends.
            - Refuses a cleaned store exactly like `add_many_creations`: the
              object's disposal methods run and `RuntimeError` is raised.

        Args:
            key: The many spell id.
            item: The just-built object.
            disposal_methods: The Spell-owned ordered disposal method names.

        Raises:
            RuntimeError:
                If this store was cleaned while the object was being built.

        Threading:
            `_lock` is a leaf here: only the dict read, the first-use stores
            and the append run under it. A build that finishes after
            `cleanup()` observes `_cleaned` through the tombstone lock and is
            refused outside it, with no lock held while its methods run.

        Returns:
            None.
        """
        # Explicit acquire/release: the with-statement costs ~14 ns per call
        # on 3.14t (measured 2026-10-01), a tenth of this verb.
        lock = self._lock
        lock.acquire()
        try:
            if not self._cleaned:
                bucket = self._creations.get(key)
                if bucket is None:
                    bucket = []
                    self._creations[key] = bucket
                    self._disposable_creations[key] = ManyDisposalBucket(
                        bucket, disposal_methods,
                    )
                bucket.append(item)
                return
        finally:
            lock.release()
        self._refuse_publish_into_cleaned_store(
            key,
            item,
            has_disposal_methods=True,
            disposal_methods=disposal_methods,
        )

    def _append_many_locked(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool,
            disposal_methods: Optional[List[str]],
    ) -> None:
        """
        Append one many creation through the checked public verb; caller holds `_lock`.

        Contract:
            - The caller holds `_lock` and has checked the store is not cleaned.
            - Validates before it appends, so a refused registration leaves the
              store untouched.
            - Creates the first-use bucket and, for a disposal-bearing key, its
              `ManyDisposalBucket` record in one critical section. The record
              IS the live bucket, so the live and disposal views cannot diverge
              (the BUG-073 invariant, now by construction).

        Raises:
            ValueError:
                If the key already holds a non-list live slot or a non-many
                disposable slot, or if this registration's disposal declaration
                disagrees with the key's existing entries: one many key carries
                one declaration (the spell id fixes it).
        """
        bucket = self._creations.get(key)
        if bucket is not None and not isinstance(bucket, list):
            raise ValueError(
                f"Key {key} already exists in creations with non-list slot."
            )
        record = self._disposable_creations.get(key)
        if has_disposal_methods:
            if record is None:
                if bucket:
                    raise ValueError(
                        f"Key {key} already holds many creations registered without disposal "
                        f"methods; one many key carries one disposal declaration."
                    )
            elif not isinstance(record, ManyDisposalBucket):
                raise ValueError(
                    f"Key {key} already exists in disposable creations with non-list slot."
                )
        elif record is not None:
            raise ValueError(
                f"Key {key} already holds many creations registered with disposal "
                f"methods; one many key carries one disposal declaration."
            )
        if bucket is None:
            bucket = []
            self._creations[key] = bucket
        if has_disposal_methods and record is None:
            self._disposable_creations[key] = ManyDisposalBucket(
                bucket,
                disposal_methods if disposal_methods is not None else [],
            )
        bucket.append(item)

    def adopt_children(
            self,
            holder_key: str,
            holder: object,
            children: Tuple[Tuple[str, object], ...],
    ) -> None:
        """
        Record a just-published holder's `many` children with the holder.

        Purpose:
            Make a slotted holder own the disposal-bearing `many` children built
            for it (slotted_lifetime_ownership, 0.2.8238). An emitted miss builds
            and registers each child in this store (`register_many`, before the
            holder's build lock), then builds and publishes the holder; right
            after publication, under the holder's build lock, it calls this verb,
            which moves the children out of their spells' `many` buckets into
            the holder's disposal record. Purge, extract/restore and whole-store
            disposal of the holder then take the children with it.

        Contract:
            - Cold path only: one call per holder publication.
            - Does nothing when this store was cleaned, or when the slot no
              longer holds `holder` (a whole-store clear swapped the registries
              after publication, and the children went with that generation).
            - Each `(child_key, child)` is removed by identity from the key's
              live bucket, scanning from the end - the child was appended
              moments ago, so the scan normally stops at once. The key's method
              list is taken from its `ManyDisposalBucket`. A bucket left empty
              is dropped with its record, so a later registration of that key
              starts again at the end of the registry. A child no longer in its
              bucket (a concurrent `many` purge retired it) is skipped.
            - The holder's disposal value becomes a `HolderDisposalEntry`: a
              `(holder, methods)` tuple is replaced in place, keeping its
              registry position; a holder published without disposal methods
              gets a new record with `methods=[]`. With no child found, nothing
              changes.
            - Children registered without disposal methods are never passed in:
              no store tracks them.

        Args:
            holder_key:
                The holder's spell id (its slot in this store).
            holder:
                The holder object just published under `holder_key`.
            children:
                `(child_spell_id, child)` pairs in build order - exactly the
                disposal-bearing `many` children the miss registered here.

        Returns:
            None.

        Threading:
            The caller holds the holder's build lock (its slot guard, or
            `Spell._lock` for `unique`); this verb takes the store lock as a
            leaf, as every registration does, so no lock-order edge is added.
            No user code runs under it.
        """
        with self._lock:
            if self._cleaned or self._creations.get(holder_key) is not holder:
                return
            adopted: List[Tuple[object, List[str]]] = []
            for child_key, child in children:
                record = self._disposable_creations.get(child_key)
                if record is None:
                    continue
                bucket = record.entries
                for index in range(len(bucket) - 1, -1, -1):
                    if bucket[index] is child:
                        del bucket[index]
                        break
                else:
                    continue
                adopted.append((child, record.methods))
                if not bucket:
                    del self._creations[child_key]
                    del self._disposable_creations[child_key]
            if not adopted:
                return
            current = self._disposable_creations.get(holder_key)
            if current is None:
                self._disposable_creations[holder_key] = HolderDisposalEntry(holder, [], adopted)
            elif isinstance(current, HolderDisposalEntry):
                current.children.extend(adopted)
            else:
                self._disposable_creations[holder_key] = HolderDisposalEntry(holder, current[1], adopted)

    def get_creation(self, spell_id: str) -> Optional[Any]:
        """
        Return one scoped live object by spell id.

        Contract:
            - Reads only `_creations`.
            - Never consults `_disposable_creations`.
            - Returns the stored object directly.
        """
        return self._creations.get(spell_id)

    def ensure_managed_quantity(self, spell: Spell) -> ManagedSpellQuantity:
        """
        Return the pool of one managed spell version in this store, composing it on first use.

        Purpose:
            Give every `Existence.managed_spell_quantity` version a pool in its
            owner root's store the moment the owner is stamped
            (`Spell._add_owned_conduit`: conjure, a post-conjure bind or
            bind_inactive, the transfer flip), so a lease always finds one.

        Contract:
            - Idempotent: one pool per (store, spell id); a second call returns
              the same pool. A rebind under the same content-stable id meets the
              pool its earlier definition left (as a slotted replacement meets
              its slot, 0.2.8219), which takes the new Spell object and its
              settings (`ManagedSpellQuantity._rebind_spell`): a managed spell's
              settings are not part of its spell_id (0.2.8254), so a rebind with
              another mode, limit, timeout or reset names keeps the pool, its
              objects and its count.
            - A new pool is composed from the Spell's options and owned by this
              store's conduit (`owner_conduit_id`); it holds no object yet.
            - Registers the pool with `ReleaseManagedSpell` under this store's
              root (idempotent; a rebind that brought another class object
              re-keys it), so a release of its class reaches it.
            - Never touches `_creations` or `_disposable_creations`.

        Args:
            spell:
                A Spell bound with `Existence.managed_spell_quantity`.

        Returns:
            ManagedSpellQuantity: The version's pool in this store.

        Raises:
            RuntimeError:
                If this store has been permanently cleaned, or no live
                `ReleaseManagedSpell` exists to register with.
            ValueError:
                If the spell is not `Existence.managed_spell_quantity` (the pool
                refuses it; nothing is stored), or no Aether built the registry.

        Threading:
            The map read and write run under the store lock, a leaf; composing a
            pool runs no user code. Called under the Spell's lock by owner
            stamping, the established build-lock-then-store-lock order. A rebind
            runs after this lock is released, because it takes the pool's lock
            (a leaf held only for field writes and a notify); the pool is then
            registered with `ReleaseManagedSpell` (its own lock is a leaf held
            only to publish). So the orders are Spell lock -> store lock, Spell
            lock -> pool lock and Spell lock -> registry lock, and the store lock
            stays a leaf.
        """
        with self._lock:
            self.check_cleaned()
            spell_id = spell.spell_id
            pool = self._managed_quantities.get(spell_id)
            rebind = pool is not None
            if pool is None:
                pool = ManagedSpellQuantity(spell=spell, owner_conduit_id=self._owner_conduit_id)
                self._managed_quantities[spell_id] = pool
            owner_conduit_id = self._owner_conduit_id
        if rebind:
            # Outside the store lock: the rebind takes the pool's lock, and the store lock stays a leaf.
            pool._rebind_spell(spell)
        ReleaseManagedSpell().register(pool, root_conduit_id=owner_conduit_id)
        return pool

    def get_managed_quantity(self, spell_id: str) -> Optional[ManagedSpellQuantity]:
        """
        Return the pool this store holds for one managed spell version, if any.

        Contract:
            - One lock-free dict read of `_managed_quantities`; None when the
              store holds no pool under the id (not managed, not stamped here, or
              moved away by an ownership transfer).
            - Never builds a pool.

        Args:
            spell_id:
                The managed spell's spell_id.

        Returns:
            Optional[ManagedSpellQuantity]: The pool, or None.

        Raises:
            AttributeError:
                After `cleanup()`, like every other live-surface read of a
                retired store.
        """
        return self._managed_quantities.get(spell_id)

    def discard_managed_quantity(self, spell_id: str, pool: ManagedSpellQuantity) -> bool:
        """
        Give up one pool this store holds, when it is still the pool under the id.

        Purpose:
            Take back a pool an owner stamp composed in this store. An ownership
            transfer's rollback uses it to remove the empty pool its stamp of the
            target root composed (`TransferOfOwnership._discard_composed_pool`,
            2026-10-15), so a failed transfer leaves the target store as it was.

        Contract:
            - Removes `pool` only when it is the pool this store holds under
              `spell_id` (identity). Any other pool under the id, or none, is left
              as it is and the call answers False, so a pool the store held before
              the stamp, or one an extract already took, is never touched.
            - Unregisters the removed pool from `ReleaseManagedSpell` after the
              store lock, as every store verb that gives a pool up does (S4).
            - Never cleans the pool and never touches `_creations` or
              `_disposable_creations`: the removed pool is the caller's, who
              decides its end (the transfer's rollback cleans it).
            - Idempotent for one pool: a second call answers False.

        Args:
            spell_id:
                The managed spell's spell_id the pool is held under.
            pool:
                The pool to give up.

        Returns:
            bool: True when the pool was removed; False when this store does not
            hold it under `spell_id`.

        Raises:
            RuntimeError:
                If this store has been permanently cleaned (its cleanup already
                gave its pools up), as `ensure_managed_quantity` refuses.

        Threading:
            The identity check and the removal run under the store lock, a leaf,
            so of two racing calls exactly one removes the pool; the unregister
            runs after the lock, so the registry's leaf lock is never taken under
            the store lock.
        """
        with self._lock:
            self.check_cleaned()
            if self._managed_quantities.get(spell_id) is not pool:
                return False
            del self._managed_quantities[spell_id]
        self._unregister_managed_quantities([pool])
        return True

    @staticmethod
    def _unregister_managed_quantities(pools: List[ManagedSpellQuantity]) -> None:
        """
        Unregister pools this store gives up from `ReleaseManagedSpell`.

        Contract:
            - Unregisters each pool from the live registry (idempotent there).
            - Does nothing when no live registry exists: Aether cleans the registry only after its frames, so a store
              torn down later (or after a test reset the registry) has nothing to unregister from.
            - Takes no store lock: the caller detached the pools first.

        Args:
            pools:
                The pools to unregister.

        Returns:
            None.
        """
        registry = ReleaseManagedSpell._live_instance()
        if registry is None:
            return
        for pool in pools:
            registry.unregister(pool)

    @staticmethod
    def _cleanup_managed_quantities(pools: List[ManagedSpellQuantity]) -> List[Exception]:
        """
        Clean detached pools in the given order and collect their failures.

        Contract:
            - Every pool is cleaned even after one fails.
            - A pool's `ExceptionGroup` is flattened into its chained
              `RuntimeError`s, so the store's own group keeps one error per failing
              disposal method; any other exception is kept as raised.
            - Takes no lock: the caller detached the pools first.

        Args:
            pools:
                The pools to clean, in cleaning order.

        Returns:
            List[Exception]: The collected failures, in attempt order.
        """
        errors: List[Exception] = []
        for pool in pools:
            try:
                pool.cleanup()
            except ExceptionGroup as group:
                errors.extend(group.exceptions)
            except Exception as exc:
                errors.append(exc)
        return errors

    def purge(
            self,
            spell: Spell,
            *,
            purge_all: bool = True,
            creation: Optional[object] = None,
    ) -> int:
        """
        Dispose and remove one registered target's creations from this store.

        Purpose:
            Provide native targeted retirement using the same disposal metadata
            and helpers as whole-store cleanup, without extracting transfer rows.

        Contract:
            - The concrete Meld door has already selected and authorized this
              store. Creations neither discovers scopes nor authorizes callers.
            - True removes the target key from both live and disposal registries.
              Many removes its retained bucket; every other existence removes
              one stored value, even when that value is falsey or a container.
            - False removes only the supplied creation and its disposal record.
              Other many entries remain in their original order. Empty buckets
              are removed; an absent reference leaves the store unchanged.
            - Disposal uses the recorded methods without rematching or copying
              the Spell-owned method-name list. Many entries run newest-first;
              each object's methods run in their established order.
            - A holder's record is detached with the holder, so the `many`
              children it adopted are disposed after it, newest first (0.2.8238);
              the count stays the target's own entries. A `many` target's bucket
              holds only children that no holder adopted, so purging a child
              spell never disposes a child its live holder still uses.
            - Every declared method runs even after one fails; each failure is
              collected and other selected objects are still attempted, matching
              cleanup.
            - Unrelated keys, the registration and this reusable store survive.
            - A managed spell (`Existence.managed_spell_quantity`) returns 0 and
              touches nothing: purge is not part of the managed design (owner,
              2026-10-15), and its objects live in a pool, never in `_creations`.

        Args:
            spell:
                Existing definition discovered by Meld. Its id selects the
                stored entry, and its Existence selects multiplicity and the
                same writer-lock family used during creation.
            purge_all:
                True retires every retained entry for the discovered target.
                False retires one entry for the supplied object reference.
            creation:
                Original application instance, required when purge_all is False.
                Ignored for whole-target removal; never used to discover a spell.

        Returns:
            int:
                Number of removed creations, or zero when the target key is
                absent or the supplied instance is not retained. An untracked
                many result contributes no retained entry.

        Raises:
            RuntimeError:
                If this store has been permanently cleaned.
            ValueError:
                If single-object retirement has no supplied creation reference.
            ExceptionGroup:
                Collected disposal failures after removal and best-effort
                processing of the selected objects. There is no disposal rollback.

        Threading / Concurrency:
            Retirement takes the slot's build lock first, then this store's leaf
            lock, so it waits for an in-flight build of the same slot and never
            removes a half-built entry: `unique` takes Spell._lock;
            `unique_per_conduit`, `unique_per_spell_space`, lineage and cluster
            take `slot_guard(spell_id)` of this store (the lineage/cluster store
            selected by their Meld door); `many` has no slot and takes only the
            store lock. Both maps detach in one critical section. All removal
            locks are released before any user disposal method runs.

        Lifecycle / Cleanup:
            Detached live references stay alive until lock release, so implicit
            finalizers also run outside that critical section. Later replacement
            registrations are untouched, and repeated purge of an absent key
            returns zero. References held by application code are not revoked.
        """
        self.check_cleaned()
        if not purge_all and creation is None:
            raise ValueError("Single-object purge requires a creation reference.")
        existence = spell.existence
        if existence is Existence.managed_spell_quantity:
            return 0
        if existence is Existence.unique:
            with spell._lock:
                count, retired, disposal = self._detach_purge_entries(
                    spell, purge_all=purge_all, creation=creation,
                )
        elif existence is Existence.many:
            count, retired, disposal = self._detach_purge_entries(
                spell, purge_all=purge_all, creation=creation,
            )
        else:
            with self.slot_guard(spell.spell_id):
                count, retired, disposal = self._detach_purge_entries(
                    spell, purge_all=purge_all, creation=creation,
                )
        errors: List[Exception] = []
        if disposal is not None:
            errors = self._dispose_entry(disposal)
        # Keep non-disposable objects alive until the removal locks are released.
        del retired
        if errors:
            raise ExceptionGroup("Errors occurred during creations purge", errors)
        return count

    def _detach_purge_entries(
            self,
            spell: Spell,
            *,
            purge_all: bool,
            creation: Optional[object],
    ) -> Tuple[int, object, Optional[StoredDisposalValue]]:
        """
        Detach one target's paired entries while holding this store's writer lock.

        Purpose:
            Separate atomic registry removal from user disposal callbacks while
            preserving a strong reference to every removed live value.

        Contract:
            - The caller already holds the slot's build lock: Spell._lock for
              unique, this store's `slot_guard` for the other slotted
              existences, none for many.
            - Rechecks cleaned state after acquiring the store lock.
            - Key membership determines presence; Existence determines whether
              the value is one object or an owned many bucket.
            - Removes no other key and does not inspect caller/scope identity.
            - Single retirement touches only the supplied creation, preserving
              all other entries and their disposal metadata in a many bucket.
            - Performs no disposal and never builds extraction/restore payloads.

        Args:
            spell: Discovered definition supplying the exact id and Existence.
            purge_all: Whether to detach the entire target or one supplied instance.
            creation: Original instance for single retirement; otherwise ignored.

        Returns:
            Tuple[int, object, Optional[StoredDisposalValue]]:
                Removal count, detached live value and detached disposal metadata.
                The caller retains these references beyond lock release. An
                absent key returns (0, None, None).

        Raises:
            RuntimeError: If the store was permanently cleaned before removal.

        Threading / Lifecycle:
            The store lock covers membership, count and both pops. No callback
            runs here; the caller owns disposal and release of the returned values.
        """
        with self._lock:
            self.check_cleaned()
            spell_id = spell.spell_id
            if spell_id not in self._creations:
                return 0, None, None
            live = self._creations[spell_id]
            if not purge_all:
                if spell.existence is Existence.many:
                    return self._detach_single_many_creation(spell_id, creation)
                if live is not creation:
                    return 0, None, None
            count = len(live) if spell.existence is Existence.many else 1
            self._creations.pop(spell_id)
            disposal = self._disposable_creations.pop(spell_id, None)
            return count, live, disposal

    def _detach_single_many_creation(
            self,
            spell_id: str,
            creation: object,
    ) -> Tuple[int, object, Optional[StoredDisposalEntry]]:
        """
        Detach one supplied object from an already-selected many bucket.

        Purpose:
            Preserve paired live/disposal removal for single-object purge without
            changing registration storage or creating a reverse discovery index.

        Contract:
            - The caller holds this store's lock and established key presence.
            - Search only this target's bucket, using object identity so custom
              equality cannot select a different creation or invoke user code.
            - Remove one retained entry. The disposal record aliases the live
              bucket, so that one removal retires it from both views; the
              returned disposal entry pairs the object with the key's method
              list when the key is disposal-bearing.
            - Preserve remaining order and remove the bucket, and its record,
              only when empty.
            - Missing references return zero; no disposal callback runs here.

        Args:
            spell_id: Existing key selected through normal spell discovery.
            creation: Original application instance requested for retirement.

        Returns:
            Tuple[int, object, Optional[StoredDisposalEntry]]:
                Count, detached live object and its optional disposal record.
                The caller retains both references until removal locks release.

        Threading / Lifecycle:
            Called only inside `_detach_purge_entries`' locked critical section.
            This helper owns no scope policy, additional lock or disposal action.
        """
        bucket = self._creations[spell_id]
        for index, retired in enumerate(bucket):
            if retired is creation:
                break
        else:
            return 0, None, None

        bucket.pop(index)
        record = self._disposable_creations.get(spell_id)
        if not bucket:
            del self._creations[spell_id]
            if record is not None:
                del self._disposable_creations[spell_id]
        if record is None:
            return 1, retired, None
        return 1, retired, (retired, record.methods)

    def extract_spell_creations(
            self,
            spell_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Remove and return all locally owned creations for one spell id.

        Contract:
            - Extracts only this scoped store's local state.
            - Preserves enough metadata for later restore.
            - Supports both singleton and `many` storage shapes.
            - Does not reach into external owners or adjacent scopes.
            - Returns raw stored objects plus disposal metadata, not a richer
              wrapper object.
            - Retains each established method-list reference in the returned
              rows; this in-memory handoff is not a serialization boundary.
            - A holder's row carries the children it adopted (0.2.8238):
              `children` lists `{"stored", "disposal_methods"}` rows in build
              order, and a holder without disposal methods of its own is
              `disposable` with an empty `disposal_methods` list, so a restore
              (an ownership transfer's move or its rollback) takes the children
              wherever the holder goes.
            - A managed spell's pool travels as one row (2026-10-15):
              `{"scope": "managed", "disposable": False, "stored": pool}` - the
              same `ManagedSpellQuantity` object with its idle objects, count and
              children records - and this store gives the pool up, unregistering
              it from `ReleaseManagedSpell` after the store lock (S4).

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        """
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            pool = self._managed_quantities.pop(spell_id, None)
            if pool is not None:
                extracted.append({"scope": "managed", "disposable": False, "stored": pool})
            live_value = self._creations.get(spell_id)
            disposable_value = self._disposable_creations.get(spell_id)

            if isinstance(live_value, list):
                live_many = self._creations.pop(spell_id)
                record = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, ManyDisposalBucket)
                    else None
                )
                # One record per key: every row of a disposal-bearing many
                # key carries the same Spell-owned list object.
                methods = None if record is None else record.methods
                for stored_value in live_many:
                    entry = {
                        "scope": "many",
                        "disposable": methods is not None,
                        "stored": stored_value,
                    }
                    if methods is not None:
                        entry["disposal_methods"] = methods
                    extracted.append(entry)
            elif live_value is not None and not isinstance(live_value, dict):
                stored_value = self._creations.pop(spell_id)
                disposable_entry = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, (tuple, HolderDisposalEntry))
                    else None
                )
                entry = {
                    "scope": "unique",
                    "disposable": disposable_entry is not None,
                    "stored": stored_value,
                }
                if isinstance(disposable_entry, HolderDisposalEntry):
                    entry["disposal_methods"] = disposable_entry.methods
                    entry["children"] = [
                        {"stored": child, "disposal_methods": methods}
                        for child, methods in disposable_entry.children
                    ]
                elif disposable_entry is not None:
                    entry["disposal_methods"] = disposable_entry[1]
                extracted.append(entry)

        if pool is not None:
            # A pool in flight between stores is not routable until a restore registers it again.
            self._unregister_managed_quantities([pool])
        return extracted

    def restore_spell_creations(
            self,
            spell_id: str,
            creations: List[Dict[str, Any]],
    ) -> None:
        """
        Restore locally owned creations previously extracted for one spell id.

        Contract:
            - Rebuilds this scoped store from the extracted payload only.
            - Replaces any current local state for the spell id.
            - Restores both live entries and disposal metadata; a many key's
              rows rebuild one `ManyDisposalBucket` over the restored bucket.
            - Raises when the payload does not match the local slot shape, or
              when the rows of one many key disagree on `disposable`.
            - Restores the same raw object references that were extracted; it
              does not clone or rehydrate them.
            - Retains the extracted disposal lists directly, without copying
              their contents or reapplying binding policy.
            - A unique row with `children` rebuilds the holder's
              `HolderDisposalEntry` (0.2.8238); rows without it restore exactly
              as before.
            - A `managed` row installs its pool under the spell id (2026-10-15).
              A different pool already there - the empty one an ownership
              transfer's flip composed at the target's stamp - is replaced and
              cleaned after the lock is released; the store's own pool is kept.
            - After the lock, in this order (S4): the replaced pool is
              unregistered from `ReleaseManagedSpell`, the installed pool is
              registered under this store's root, then the replaced pool is
              cleaned - so the moved pool is routable even when that cleanup
              fails.

        Raises:
            RuntimeError:
                For a row that does not fit the local slot shape.
            ExceptionGroup:
                When cleaning a replaced pool failed; raised after the restore
                completed, with the moved pool in place.

        Returns:
            None.
        """
        if not creations:
            return

        replaced_pools: List[ManagedSpellQuantity] = []
        installed_pools: List[ManagedSpellQuantity] = []
        with self._lock:
            owner_conduit_id = self._owner_conduit_id
            live_value = self._creations.get(spell_id)
            if live_value is not None:
                self._creations.pop(spell_id)
            self._disposable_creations.pop(spell_id, None)

            for entry in creations:
                scope = entry["scope"]
                is_disposable = entry["disposable"]
                stored_value = entry["stored"]
                disposal_methods = entry.get("disposal_methods")

                if scope == "managed":
                    replaced = self._managed_quantities.get(spell_id)
                    if replaced is not None and replaced is not stored_value:
                        replaced_pools.append(replaced)
                    self._managed_quantities[spell_id] = stored_value
                    installed_pools.append(stored_value)
                    continue

                if scope == "unique":
                    existing = self._creations.get(spell_id)
                    if isinstance(existing, dict):
                        raise RuntimeError(
                            f"Cannot restore unique creation for spell '{spell_id}' into non-singleton slot."
                        )
                    self._creations[spell_id] = stored_value
                    children = entry.get("children")
                    if children is not None:
                        self._disposable_creations[spell_id] = HolderDisposalEntry(
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                            [(child["stored"], child["disposal_methods"]) for child in children],
                        )
                    elif is_disposable:
                        self._disposable_creations[spell_id] = (
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                        )
                    continue

                if scope == "many":
                    existing = self._creations.get(spell_id)
                    if existing is None:
                        existing = []
                        self._creations[spell_id] = existing
                    elif not isinstance(existing, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    record = self._disposable_creations.get(spell_id)
                    if is_disposable:
                        if record is None:
                            if existing:
                                raise RuntimeError(
                                    f"Cannot restore a disposable many creation for spell '{spell_id}' "
                                    f"beside entries restored without disposal methods."
                                )
                            self._disposable_creations[spell_id] = ManyDisposalBucket(
                                existing,
                                disposal_methods if disposal_methods is not None else [],
                            )
                        elif not isinstance(record, ManyDisposalBucket):
                            raise RuntimeError(
                                f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                            )
                    elif record is not None:
                        raise RuntimeError(
                            f"Cannot restore a many creation without disposal methods for spell "
                            f"'{spell_id}' beside disposable entries."
                        )
                    existing.append(stored_value)
                    continue

                raise RuntimeError(
                    f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                )

        self._unregister_managed_quantities(replaced_pools)
        for installed in installed_pools:
            ReleaseManagedSpell().register(installed, root_conduit_id=owner_conduit_id)
        if replaced_pools:
            errors = self._cleanup_managed_quantities(replaced_pools)
            if errors:
                raise ExceptionGroup(
                    f"Errors occurred cleaning the managed pool replaced while restoring spell '{spell_id}'",
                    errors,
                )

    def clear_all(self) -> None:
        """
        Dispose and remove all scoped entries without destroying this object.

        Contract:
            - Reusable clear for scope cleanup or pooling flows.
            - Detaches live and disposable registries before disposal work.
            - Raises `ExceptionGroup` after best-effort disposal attempts.
            - Leaves this `Creations` instance reusable after the clear
              completes. Slot guards are kept (they are per spell id, not per
              generation).
            - Leaves the managed pools untouched: only root stores hold pools,
              and the reusable clears run on lesser and spellspace stores only (a
              lesser's pool return, a spellspace's exit), never on a root's.

        Threading:
            The swap runs under the leaf store lock. In-flight builds hold slot
            guards, not the store lock, so this does not wait for them: a build
            that started before the clear and publishes after it lands in the
            fresh registry. Callers that need "nothing survives the clear" must
            quiesce melds on this scope first, as pool return already does.

        Returns:
            None.
        """
        with self._lock:
            if not self._creations and not self._disposable_creations:
                return
            live_creations = self._creations
            disposable_creations = self._disposable_creations
            self._creations = {}
            self._disposable_creations = {}

        errors = self._dispose_disposable_registry(disposable_creations)
        live_creations.clear()
        disposable_creations.clear()

        if errors:
            raise ExceptionGroup("Errors occurred during creations clear", errors)

    def reset_for_pool(self) -> None:
        """
        Clear all live scoped state without destroying this manager.

        Contract:
            - Keeps the same observable result as `clear_all()` for callers.
            - Uses a fast path when no disposable metadata is present:
              clear only the live registry under lock and return.
            - Falls back to the full detachable disposal flow when disposable
              cleanup work is required.

        Returns:
            None.
        """
        with self._lock:
            if not self._creations and not self._disposable_creations:
                return
            if not self._disposable_creations:
                self._creations.clear()
                return
        self.clear_all()

    def reset_for_pool_unlocked(self) -> None:
        """
        Clear all live scoped state without taking the instance lock.

        Purpose:
            Provide the managed spellspace exit lane with a lock-free scope
            clear, removing the last per-cycle lock acquisition from the
            `with conduit.enter_spellspace():` hot path.

        Contract:
            - Same observable result as `reset_for_pool()` for the caller.
            - Caller-guaranteed thread confinement is REQUIRED: this method
              may only be called when the owning scope object is confined to
              the calling thread, as on the managed spellspace exit lane
              (pool deque hand-off in, per-thread stack while live,
              LIFO-validated exit out; the pool deque ops are the cross-thread
              synchronization points). Calling it on a store that other
              threads may be reading or mutating concurrently is a caller
              contract violation.
            - Disposal work stays safe: when disposable metadata is present,
              this method falls back to the fully locked `clear_all()` flow,
              because explicit teardown of user objects is never run
              lock-free.

        Threading:
            - No lock is taken on the fast (no-disposables) path by design;
              see the confinement contract above.

        Returns:
            None.
        """
        if not self._disposable_creations:
            creations = self._creations
            if creations:
                creations.clear()
            return
        self.clear_all()

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this scoped registry.

        Returns:
            str: Conduit id that owns the scope represented by this registry.
        """
        return self._owner_conduit_id

    @property
    def id(self) -> str:
        """
        Return the stable owner scope id for this registry.

        Returns:
            str: Concrete scope id for this registry (for example a conduit id
            or spellspace id).
        """
        return self._id
