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
        - `methods` is the established ordered disposal list of the Spell
          whose object first registered the key in this store, retained by
          reference (never matched, reordered or copied), and every entry of
          the key is disposed with it. Later registrations append to
          `entries` and leave `methods` as it is; nothing compares lists.
        - One list per key holds by construction: the key is a store key
          (`Spell.store_key`, `<spell_id>:<binding_hash>`), and the binding
          hash covers the existence and the disposal order, so every
          registration of a key comes from one binding and carries its list.
          A class cleaned up (`cleanup_spell`) and bound again under other
          disposal names keeps its spell_id but files under another key, so
          its objects get a record of their own while the removed
          definition's objects stay in theirs, alive in their scope
          (STORY-2026-10-25-creations_store_slots_by_binding; while stores
          were keyed by spell_id the new objects joined the old record).
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


StoredDisposalEntry = Tuple[object, List[str]]
StoredDisposalValue = Union[StoredDisposalEntry, ManyDisposalBucket]


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
        - Entries are keyed by store key (`Spell.store_key`,
          `<spell_id>:<binding_hash>`): one slot per binding of a spell
          (STORY-2026-10-25-creations_store_slots_by_binding; before, by
          spell_id, which two bindings of one class share since 0.2.8257).
        - Unique entries use `key -> object`.
        - Many entries use `key -> list[object]`.
        - Disposal metadata mirrors only entries that declared disposal
          methods:
          - unique: `key -> (object, disposal_methods)`
          - many: `key -> ManyDisposalBucket` whose `entries` IS the
            live many bucket (the same list object, never a copy) and
            whose `methods` is the Spell-owned list recorded once, at the
            key's first registration (2026-10-01; before, a second list of
            `(object, methods)` tuples was appended in step with the live
            bucket, a tuple and a second append per creation). A many key
            therefore carries one disposal declaration: every entry of the
            key is disposal-bearing or none is.
          - A slotted holder's disposal value is its own `(object, methods)`
            tuple, like any unique: nothing records the `many` objects it was
            built with against it. They stay in their spells' buckets in the
            store that recorded them - the meld's innermost scope - and are
            disposed when that store ends (the owner's decision, 2026-10-24;
            from 0.2.8238 to 0.2.8265 a holder record took them in and
            disposed them with the holder).
        - Shelves: `_shelves[spell_id]` lists, in first-filing order, every
          store key this store has filed under that spell_id, and
          `_slot_shapes[key]` records whether the slot is a `many` list.
          Every writer records a key before its first value (`_note_slot`),
          so every live slot is on its shelf; the index lives as long as the
          store, like `_slot_guards`, and readers filter it by what
          `_creations` holds now. A meld reads and writes only its own key;
          operations on a spell - `purge`, `count_spell_creations`,
          `extract_spell_creations` and `restore_spell_creations` - walk the
          shelf and take each slot's shape from the record, never from the
          spell that asks. A key without ':' is its own shelf.
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
        registries (`_creations`, `_disposable_creations`, by store key), the
        per-slot build-guard table (`_slot_guards`, by store key), the shelf
        index (`_shelves`, spell id -> store keys; `_slot_shapes`, store key ->
        is a `many` list) and the managed pools (`_managed_quantities`, spell
        id -> `ManagedSpellQuantity`, 2026-10-15).

    Threading:
        Two lock roles, and keeping them apart is what makes resolution
        deadlock-free.

        - `_lock` (the store lock) is a LEAF lock over the two registries and
          the shelf index. It is held only for dict reads and writes: publish
          of disposal-bearing entries, many append, a key's first filing on
          its shelf, the spell count, purge detach, extract/restore and
          whole-store swap. It is never held while acquiring another lock and
          never around user code. (A publish without disposal methods is one
          atomic dict store under the caller's build lock; see `add_creation`
          and `register_slot`.)
        - `slot_guard(key)` returns one `RLock` per slot - a store key whose
          Existence promises at most one object in this store. Generated
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
        "_slot_shapes",
        "_shelves",
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
        # store's lifetime (bounded by the number of store keys built here).
        self._slot_guards: Dict[str, RLock] = {}
        # The shelf index (STORY-2026-10-25-creations_store_slots_by_binding):
        # every store key filed here, under its spell id, in first-filing order,
        # and whether its slot is a `many` list. Written under the store lock at
        # a key's first filing and kept for this store's lifetime, like the slot
        # guards (bounded by the store keys filed here).
        self._slot_shapes: Dict[str, bool] = {}
        self._shelves: Dict[str, List[str]] = {}
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
              honestly instead of reading stale state, the shelf index included.
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
        del self._slot_shapes
        del self._shelves
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
            - The two-way dispatch is inline, as `_dispose_entry` spells it
              out, so a scope exit pays no extra call per record. A slotted
              holder is an ordinary tuple: its disposal runs only its own
              methods (the owner's decision, 2026-10-24).
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
            already IS the creation-order record. It holds one record per store
            key, so every binding of a spell is disposed with its own methods.

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
            else:
                errors.extend(self._dispose_many_creations(value))
        return errors

    def _dispose_entry(self, value: StoredDisposalValue) -> List[Exception]:
        """
        Dispose one detached disposal-registry value, whatever its shape.

        Purpose:
            One dispatch over the two record shapes `_disposable_creations`
            holds, for retirements of one record such as purge (0.2.8238; two
            shapes again since the holder record was removed, 2026-10-24).
            Whole-store disposal runs the same dispatch inline in its loop.

        Contract:
            - An `(object, methods)` tuple goes to `_attempt_cleanup`: one
              object, a slotted holder included, runs only its own methods.
            - A `ManyDisposalBucket` goes to `_dispose_many_creations` (newest
              object first).
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
        return self._dispose_many_creations(value)

    def slot_guard(self, key: str) -> RLock:
        """
        Return the build guard for one slot in this store.

        Purpose:
            Give "build this slot at most once" its own lock, so the store lock
            only ever protects the registries and can stay a leaf. A slot is a
            store key (`Spell.store_key`) whose Existence promises at most one
            object in this store: `unique_per_conduit`, `unique_per_spell_space`,
            `unique_per_conduit_lineage` and `unique_per_conduit_cluster`.
            (`unique` uses `Spell._lock` instead; `many` has no slot.)

        Contract:
            - Returns the same `RLock` for a key on every call for this
              store's lifetime, including across `clear_all()` and
              `reset_for_pool()`.
            - A hit is one lock-free dict read. The first request for a slot
              publishes a new `RLock` with `dict.setdefault`, which is atomic on
              a builtin dict with `str` keys (GIL and free-threaded builds), so
              concurrent first requests converge on one guard.
            - Returning or holding a guard never implies holding `_lock`.
            - Generated doors and plan steps inline the hit as
              `store._slot_guards.get(key) or store.slot_guard(key)`
              (one method call fewer per cold build). `_slot_guards` is
              therefore part of this class's internal contract: a plain
              `dict` of store key -> `RLock` whose entries are never replaced
              or removed while the store is live.

        Args:
            key:
                Store key of the slot being built or retired.

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
        guard = self._slot_guards.get(key)
        if guard is None:
            guard = self._slot_guards.setdefault(key, RLock())
        return guard

    def _note_slot(self, key: str, is_many: bool) -> None:
        """
        Record one store key on its spell id's shelf, with its slot's shape.

        Purpose:
            Keep the index that lets the operations on a spell - purge, the live
            count, extract and restore - find every slot of every binding of a
            spell id without scanning the store
            (STORY-2026-10-25-creations_store_slots_by_binding).

        Contract:
            - The shelf id is the text before the key's last ':' (a store key is
              `<spell_id>:<binding_hash>`); a key without ':' is its own shelf.
            - A key joins its shelf once, at its first filing in this store, in
              filing order. Its shape (`is_many`: the slot is a `many` list) is
              recorded with it, and updated when a later filing finds the other
              shape - a reused test or legacy key; a store key names one
              existence, so its shape never changes.
            - Writers call this BEFORE they write the slot's first value, so
              every live slot is on its shelf. They test
              `_slot_shapes.get(key) is not is_many` first, so a key already
              recorded costs one dict read and no lock.
            - Does nothing on a cleaned store: the caller's write is then
              refused, dropped or fails exactly as it would without the index.

        Args:
            key:
                The store key being filed.
            is_many:
                True when the slot holds a `many` list.

        Returns:
            None.

        Threading:
            Takes the store lock (re-entrant: a caller may already hold it) and
            nothing under it, so the lock stays a leaf. The index changes only
            here and in `cleanup`, so a reader under the store lock sees it
            whole.
        """
        with self._lock:
            if self._cleaned:
                return
            shapes = self._slot_shapes
            if key not in shapes:
                spell_id, separator, _binding_hash = key.rpartition(":")
                shelf_id = spell_id if separator else key
                shelf = self._shelves.get(shelf_id)
                if shelf is None:
                    self._shelves[shelf_id] = [key]
                else:
                    shelf.append(key)
            shapes[key] = is_many

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
            key: Store key the object would have been published under.
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
            - `key` is the slot's store key (`Spell.store_key`); the key is
              recorded on its spell id's shelf before the object is stored.
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
                if self._slot_shapes.get(key) is not False:
                    self._note_slot(key, False)
                self._creations[key] = item
                return
        else:
            with self._lock:
                if not self._cleaned:
                    if key in self._creations or key in self._disposable_creations:
                        raise ValueError(f"Key {key} already exists in creations.")
                    if self._slot_shapes.get(key) is not False:
                        self._note_slot(key, False)
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

    def register_slot(self, key: str, item: object) -> None:
        """
        Publish one slotted object without disposal methods on the build path.

        Purpose:
            The publication emitted plans run for a slotted site whose Spell
            declares no disposal methods. They stored `_creations[sid] = v`
            inline until the store had to see a key's first filing to put it on
            its spell id's shelf (STORY-2026-10-25-creations_store_slots_by_binding).

        Contract:
            - Precondition, NOT checked here: the caller holds the slot's build
              lock (its slot guard, or `Spell._lock` for `unique`) and has
              rechecked that the slot is empty. The emitters guarantee both;
              callers that cannot promise them use `add_creation`.
            - Records the key on its shelf at its first filing, then writes the
              slot with one dict store: no store lock, no duplicate check and no
              cleaned check, exactly the inline store it replaces. A write
              racing `clear_all()`/`reset_for_pool()` lands in the detached
              generation and is dropped with it; one racing `cleanup()` is
              dropped or fails on the retired store's missing registry, with no
              disposal methods to leak.

        Args:
            key:
                The slot's store key.
            item:
                The just-built object.

        Returns:
            None.

        Raises:
            AttributeError:
                After `cleanup()`, like every other live-surface use of a
                retired store.
        """
        if self._slot_shapes.get(key) is not False:
            self._note_slot(key, False)
        self._creations[key] = item

    def add_many_creations(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one creation into the scoped `many` list of one store key.

        Contract:
            - `key` is the store key (`Spell.store_key`); the key's first
              registration records it on its spell id's shelf as a `many` slot.
            - Appends the live object into `_creations[key]`.
            - For a disposal-bearing key, records the Spell-owned method list
              ONCE, at the key's first registration, in a `ManyDisposalBucket`
              under `_disposable_creations[key]` whose `entries` is the live
              bucket itself; later registrations of the key append only.
            - Rejects collisions with non-list slots, and a registration whose
              disposal declaration disagrees with the key's existing entries -
              a disposal-bearing registration of a key whose entries were
              registered without disposal methods, or the reverse - so every
              entry of a key is disposal-bearing or none is.
            - Does not compare method lists: a disposal-bearing registration
              of a key that already has its record appends under the record's
              list. A store key names one binding, disposal order included, so
              every registration of a key carries an equal list (see
              `ManyDisposalBucket`).
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
                If the key already holds a non-list slot, or if this
                registration is disposal-bearing where the key's existing
                entries are not, or the reverse.
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
            - Precondition, NOT checked here: `key` is the store key of a
              `many` Spell that declares disposal methods, `disposal_methods`
              is that Spell's own ordered list, and the key's live slot in this
              store is a list or absent. The emitters guarantee all three - one
              plan, one list object on every call, one Existence - and the key
              keeps them across a rebind: a store key covers the existence and
              the disposal order, so a class bound again another way files
              under another key (STORY-2026-10-25-creations_store_slots_by_binding;
              while the key was the spell id, a rebind's objects joined the
              removed definition's record, or failed on its slotted object).
              Callers that cannot promise them use `add_many_creations`, which
              checks the slot's shape.
            - The first registration of the key in this store records it on its
              spell id's shelf, then creates the live bucket and its
              `ManyDisposalBucket` record (the bucket itself plus the method
              list) in one critical section; every later one appends.
            - Refuses a cleaned store exactly like `add_many_creations`: the
              object's disposal methods run and `RuntimeError` is raised.

        Args:
            key: The many Spell's store key.
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
                    if self._slot_shapes.get(key) is not True:
                        self._note_slot(key, True)
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
              `ManyDisposalBucket` record in one critical section, after the key
              is recorded on its shelf as a `many` slot. The record IS the live
              bucket, so the live and disposal views cannot diverge (the BUG-073
              invariant, now by construction).

        Raises:
            ValueError:
                If the key already holds a non-list live slot or a non-many
                disposable slot, or if this registration is disposal-bearing
                where the key's existing entries are not, or the reverse.
                Method lists are not compared: a disposal-bearing registration
                of a key with a record appends under the record's list.
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
            if self._slot_shapes.get(key) is not True:
                self._note_slot(key, True)
            bucket = []
            self._creations[key] = bucket
        if has_disposal_methods and record is None:
            self._disposable_creations[key] = ManyDisposalBucket(
                bucket,
                disposal_methods if disposal_methods is not None else [],
            )
        bucket.append(item)

    def get_creation(self, key: str) -> Optional[Any]:
        """
        Return one scoped live object, or a `many` list, by store key.

        Contract:
            - Reads one slot of `_creations`: the binding's that `key` names
              (`Spell.store_key`). A spell's other bindings are other keys;
              `count_spell_creations` reads all of them.
            - Never consults `_disposable_creations`.
            - Returns the stored value directly; None for an empty slot.
        """
        return self._creations.get(key)

    def count_spell_creations(self, spell_id: str) -> int:
        """
        Return how many objects this store holds under every binding of one spell id.

        Purpose:
            The count the live probes report (`describe_live_creation_status`,
            `has_live_creation`): a spell's objects in this store, whichever of
            its bindings filed them (STORY-2026-10-25-creations_store_slots_by_binding;
            before, a probe read one slot by spell id and took its shape from
            the asking spell).

        Contract:
            - Walks the spell id's shelf; each slot it holds now adds its
              length when it is a `many` slot, one otherwise, and nothing when
              it holds None (a None object reads as absent, as the probes always
              read it).
            - Reads only; never creates, registers or disposes.

        Args:
            spell_id:
                The spell whose objects are counted.

        Returns:
            int: The number of objects; 0 when nothing is filed under the spell id.

        Raises:
            AttributeError:
                After `cleanup()`, like every other live-surface read of a
                retired store.

        Threading:
            Runs under the store lock - a leaf: no other lock, no user code - so
            the count is one consistent reading of the shelf.
        """
        with self._lock:
            keys = self._shelves.get(spell_id)
            if not keys:
                return 0
            creations = self._creations
            shapes = self._slot_shapes
            count = 0
            for key in keys:
                value = creations.get(key)
                if value is None:
                    continue
                count += len(value) if shapes[key] else 1
            return count

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
              the same pool. Pools stay keyed by spell id, not by store key: a
              rebind under the same content-stable id meets the pool its earlier
              definition left, under any binding, which takes the new Spell object and its
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
            - The target is the spell's whole shelf: every slot filed here under
              its spell id, by any binding - a class bound again under another
              existence or other disposal names leaves its removed definition's
              objects in a slot of their own
              (STORY-2026-10-25-creations_store_slots_by_binding).
            - True removes every slot of the shelf from both live and disposal
              registries. Each slot is counted by its recorded shape, never by
              the asking spell's existence: a `many` slot counts its bucket's
              length; any other slot one stored value, even when that value is
              falsey or a container.
            - False removes only the supplied creation and its disposal record,
              from whichever slot of the shelf holds it (by identity). Other many
              entries remain in their original order. Empty buckets are removed;
              an absent reference leaves the store unchanged.
            - Disposal uses each slot's recorded methods without rematching or
              copying the Spell-owned method-name list. Slots run newest-filed
              first and many entries newest-first; each object's methods run in
              their established order.
            - Purging a holder disposes only the holder, with its own methods:
              the `many` objects it was built with stay in their spells' buckets
              in the store that recorded them, and a `many` purge of their spell
              counts and disposes every one of them, a live holder's included
              (the owner's decision, 2026-10-24; from 0.2.8238 to 0.2.8265 a
              holder's purge disposed its children and a `many` purge skipped
              them).
            - Every declared method runs even after one fails; each failure is
              collected and other selected objects are still attempted, matching
              cleanup.
            - Unrelated keys, the registration and this reusable store survive.
            - A managed spell (`Existence.managed_spell_quantity`) returns 0 and
              touches nothing: purge is not part of the managed design (owner,
              2026-10-15), and its objects live in a pool, never in `_creations`.

        Args:
            spell:
                Existing definition discovered by Meld. Its spell id selects the
                shelf; its Existence and store key select the writer lock its
                builds take (the slot shapes come from the store).
            purge_all:
                True retires every retained entry for the discovered target.
                False retires one entry for the supplied object reference.
            creation:
                Original application instance, required when purge_all is False.
                Ignored for whole-target removal; never used to discover a spell.

        Returns:
            int:
                Number of removed creations, or zero when the shelf holds no
                live slot or the supplied instance is not retained. An untracked
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
            Retirement takes the asking definition's build lock first, then this
            store's leaf lock, so it waits for an in-flight build of its own slot
            and never removes a half-built entry: `unique` takes Spell._lock;
            `unique_per_conduit`, `unique_per_spell_space`, lineage and cluster
            take `slot_guard(spell.store_key)` of this store (the lineage/cluster
            store selected by their Meld door); `many` has no slot and takes only
            the store lock. Slots of the shelf's other bindings - definitions
            already removed - are detached under the store lock alone; a build
            of one still in flight publishes after the purge and stays, like any
            later registration. Every slot detaches in one critical section. All
            removal locks are released before any user disposal method runs.

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
        spell_id = spell.spell_id
        if existence is Existence.unique:
            with spell._lock:
                count, retired, disposals = self._detach_purge_entries(
                    spell_id, purge_all=purge_all, creation=creation,
                )
        elif existence is Existence.many:
            count, retired, disposals = self._detach_purge_entries(
                spell_id, purge_all=purge_all, creation=creation,
            )
        else:
            with self.slot_guard(spell.store_key):
                count, retired, disposals = self._detach_purge_entries(
                    spell_id, purge_all=purge_all, creation=creation,
                )
        errors: List[Exception] = []
        for disposal in disposals:
            errors.extend(self._dispose_entry(disposal))
        # Keep non-disposable objects alive until the removal locks are released.
        del retired
        if errors:
            raise ExceptionGroup("Errors occurred during creations purge", errors)
        return count

    def _detach_purge_entries(
            self,
            spell_id: str,
            *,
            purge_all: bool,
            creation: Optional[object],
    ) -> Tuple[int, List[object], List[StoredDisposalValue]]:
        """
        Detach one spell's paired entries from every slot of its shelf while holding this store's writer lock.

        Purpose:
            Separate atomic registry removal from user disposal callbacks while
            preserving a strong reference to every removed live value.

        Contract:
            - The caller already holds the asking definition's build lock:
              Spell._lock for unique, this store's `slot_guard(store_key)` for the
              other slotted existences, none for many.
            - Rechecks cleaned state after acquiring the store lock.
            - Walks the spell id's shelf newest-filed key first; a slot's
              presence is key membership, and its recorded shape decides whether
              it is one object or an owned many bucket.
            - Whole retirement pops every live slot of the shelf, with its
              record; the count adds each `many` slot's length and one per other
              slot.
            - Single retirement touches only the supplied creation, in the first
              slot that holds it by identity, preserving all other entries and
              their disposal metadata in a many bucket.
            - Removes no key of another spell id and does not inspect
              caller/scope identity.
            - Performs no disposal and never builds extraction/restore payloads.

        Args:
            spell_id: The spell id whose shelf is retired.
            purge_all: Whether to detach every slot or one supplied instance.
            creation: Original instance for single retirement; otherwise ignored.

        Returns:
            Tuple[int, List[object], List[StoredDisposalValue]]:
                Removal count, the detached live values and the detached
                disposal records, in detach order. The caller retains these
                references beyond lock release. A shelf with no live slot
                returns (0, [], []).

        Raises:
            RuntimeError: If the store was permanently cleaned before removal.

        Threading / Lifecycle:
            The store lock covers the shelf walk, the counts and every pop. No
            callback runs here; the caller owns disposal and release of the
            returned values.
        """
        with self._lock:
            self.check_cleaned()
            keys = self._shelves.get(spell_id)
            if not keys:
                return 0, [], []
            creations = self._creations
            shapes = self._slot_shapes
            if not purge_all:
                for key in reversed(keys):
                    if key not in creations:
                        continue
                    if shapes[key]:
                        found, retired, entry = self._detach_single_many_creation(key, creation)
                        if found:
                            return found, [retired], [] if entry is None else [entry]
                    elif creations[key] is creation:
                        retired = creations.pop(key)
                        record = self._disposable_creations.pop(key, None)
                        return 1, [retired], [] if record is None else [record]
                return 0, [], []
            count = 0
            retired_values: List[object] = []
            disposals: List[StoredDisposalValue] = []
            for key in reversed(keys):
                if key not in creations:
                    continue
                live = creations.pop(key)
                count += len(live) if shapes[key] else 1
                retired_values.append(live)
                record = self._disposable_creations.pop(key, None)
                if record is not None:
                    disposals.append(record)
            return count, retired_values, disposals

    def _detach_single_many_creation(
            self,
            key: str,
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
            key: A live `many` slot of the spell's shelf.
            creation: Original application instance requested for retirement.

        Returns:
            Tuple[int, object, Optional[StoredDisposalEntry]]:
                Count, detached live object and its optional disposal record.
                The caller retains both references until removal locks release.

        Threading / Lifecycle:
            Called only inside `_detach_purge_entries`' locked critical section.
            This helper owns no scope policy, additional lock or disposal action.
        """
        bucket = self._creations[key]
        for index, retired in enumerate(bucket):
            if retired is creation:
                break
        else:
            return 0, None, None

        bucket.pop(index)
        record = self._disposable_creations.get(key)
        if not bucket:
            del self._creations[key]
            if record is not None:
                del self._disposable_creations[key]
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
            - Extracts the spell's whole shelf: every slot filed here under the
              spell id, by any binding, in first-filing order
              (STORY-2026-10-25-creations_store_slots_by_binding). Each object row
              carries its slot's store key as `"key"`, so a restore files it
              where it was.
            - Preserves enough metadata for later restore.
            - Supports both singleton and `many` storage shapes, read from each
              slot's recorded shape. A singleton slot holding a dict is left in
              place, as before.
            - Does not reach into external owners or adjacent scopes.
            - Returns raw stored objects plus disposal metadata, not a richer
              wrapper object.
            - Retains each established method-list reference in the returned
              rows; this in-memory handoff is not a serialization boundary.
            - A holder's row is an ordinary unique row: the `many` objects it
              was built with are not in it and stay where they were recorded
              when the holder moves (the owner's decision, 2026-10-24; from
              0.2.8238 to 0.2.8265 a holder's row carried its adopted children).
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
            creations = self._creations
            disposables = self._disposable_creations
            shapes = self._slot_shapes
            for key in self._shelves.get(spell_id, ()):
                live_value = creations.get(key)
                if live_value is None:
                    continue
                disposable_value = disposables.get(key)
                if shapes[key]:
                    live_many = creations.pop(key)
                    record = (
                        disposables.pop(key)
                        if isinstance(disposable_value, ManyDisposalBucket)
                        else None
                    )
                    # One record per key: every row of a disposal-bearing many
                    # key carries the same Spell-owned list object.
                    methods = None if record is None else record.methods
                    for stored_value in live_many:
                        entry = {
                            "key": key,
                            "scope": "many",
                            "disposable": methods is not None,
                            "stored": stored_value,
                        }
                        if methods is not None:
                            entry["disposal_methods"] = methods
                        extracted.append(entry)
                elif not isinstance(live_value, dict):
                    stored_value = creations.pop(key)
                    disposable_entry = (
                        disposables.pop(key)
                        if isinstance(disposable_value, tuple)
                        else None
                    )
                    entry = {
                        "key": key,
                        "scope": "unique",
                        "disposable": disposable_entry is not None,
                        "stored": stored_value,
                    }
                    if disposable_entry is not None:
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
            - Replaces any current local state for the spell id: every slot on
              its shelf here, and the bare spell id key, is dropped undisposed
              before the rows are installed.
            - Files each object row under its `"key"` - the store key it was
              extracted from - and a row without one under the spell id, which
              is its own shelf; each key is recorded on its shelf first
              (STORY-2026-10-25-creations_store_slots_by_binding).
            - Restores both live entries and disposal metadata; a many key's
              rows rebuild one `ManyDisposalBucket` over the restored bucket.
            - Raises when the payload does not match the local slot shape, or
              when the rows of one many key disagree on `disposable`.
            - Restores the same raw object references that were extracted; it
              does not clone or rehydrate them.
            - Retains the extracted disposal lists directly, without copying
              their contents or reapplying binding policy.
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
            live = self._creations
            disposables = self._disposable_creations
            for key in self._shelves.get(spell_id, ()):
                live.pop(key, None)
                disposables.pop(key, None)
            live.pop(spell_id, None)
            disposables.pop(spell_id, None)

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

                key = entry.get("key", spell_id)
                if scope == "unique":
                    existing = live.get(key)
                    if isinstance(existing, dict):
                        raise RuntimeError(
                            f"Cannot restore unique creation for spell '{spell_id}' into non-singleton slot."
                        )
                    if self._slot_shapes.get(key) is not False:
                        self._note_slot(key, False)
                    live[key] = stored_value
                    if is_disposable:
                        disposables[key] = (
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                        )
                    continue

                if scope == "many":
                    existing = live.get(key)
                    if existing is None:
                        if self._slot_shapes.get(key) is not True:
                            self._note_slot(key, True)
                        existing = []
                        live[key] = existing
                    elif not isinstance(existing, list):
                        raise RuntimeError(
                            f"Cannot restore many creations for spell '{spell_id}' into non-list slot."
                        )
                    record = disposables.get(key)
                    if is_disposable:
                        if record is None:
                            if existing:
                                raise RuntimeError(
                                    f"Cannot restore a disposable many creation for spell '{spell_id}' "
                                    f"beside entries restored without disposal methods."
                                )
                            disposables[key] = ManyDisposalBucket(
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
              completes. Slot guards and the shelf index are kept (they are per
              store key, not per generation); every slot is disposed with its
              own record.
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
