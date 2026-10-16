import threading
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Iterable, List, Optional, Tuple

from melder.aether.conduit.creations.managed_spell_lease import ManagedObjectT, ManagedSpellLease
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity


class ReleaseManagedSpell(Cleanable):
    """
    The one way back for managed objects: a process singleton that routes an object to the pool it came from.

    Purpose:
        Give an object leased from an `Existence.managed_spell_quantity` pool back to that pool - `release(obj)` -
        without a conduit, a spell id or a pool in hand. It keys every live pool by its managed class, so the common
        release is one dict get by `type(obj)` and the pool's `put_back`. A class managed by several pools (two
        binding names, two roots, two versions of one index) is resolved on a cold path: the active version wins,
        and otherwise `spell_id=` or `conduit=` picks the pool.

    Responsibilities:
        - `release(obj, *, spell_id=None, conduit=None)`: give one object back (the pool runs its resets, then the
          object is idle for the next lease).
        - `managed(obj, ...)`: a `ManagedSpellLease` whose `release()` or `with` block gives it back once.
        - `release_all(objects, ...)`: release many; failures are raised together after every attempt.
        - `describe(cls)`: one snapshot per pool of a class - mode, count, idle and out objects, where it lives.
        - `register(pool, ...)` / `unregister(pool)`: kept by the root stores as they take and give up pools, so the
          registry holds exactly the pools live stores hold.

    Contract:
        - A process singleton with Aether's hosted-root shape (owner ruling 2026-10-15): `Aether.__init__` builds it
          (`ReleaseManagedSpell(aether=self)`, last, after Nexus), `Aether.cleanup` cleans it right after the frames,
          and `ReleaseManagedSpell()` returns that instance. A first construction without its host refuses.
        - Releasing never goes through Aether as a verb (owner ruling 2026-10-13) and never needs a conduit.
        - Identity is not tracked (owner, 2026-10-14): an object of a managed class is trusted to come from that
          class's pool; nothing records which objects are out.
        - The registry borrows the pools: it never cleans or disposes one. Each belongs to its root's store.
        - A class key is the exact class object: a subclass is a class of its own, and a redefined class (a new class
          object) is a new key.

    Owned State:
        - `_pools_by_class`: class -> tuple of pools. The release fast path reads it without a lock.
        - `_registrations`: `id(pool)` -> (class, id of the root whose store holds the pool), for the cold paths.
        - `_lock`: a leaf lock held only to publish new maps.
        Both maps are replaced whole (copy-on-write) and never mutated after they are published, so a lock-free reader
        always sees one complete map.

    Threading:
        - `release` on a one-pool class with no filter takes no lock: one attribute read, one dict get, then the
          pool's own lock-free put-back.
        - `register` and `unregister` build new maps under `_lock` and publish `_registrations` then
          `_pools_by_class`. `_lock` is never held with another lock and runs no user code.
        - Singleton construction and reset take the class-level `_singleton_lock`; `Aether.__init__` builds this
          object under `Aether._lock`, so the nesting is one-way Aether -> ReleaseManagedSpell.

    Performance:
        Measured 2026-10-15 (CPython 3.14.7t, both GIL modes): a bound `release` adds about 50 ns over the pool's own
        `put_back`; the singleton call `ReleaseManagedSpell()` costs about 70 ns more, as `Aether()` does. A hot loop
        binds it once - `release = ReleaseManagedSpell().release` - and calls `release(obj)`.

    Lifecycle / Cleanup:
        `cleanup()` is idempotent: it publishes empty maps (tombstones, so lock-free readers racing it see an empty
        registry rather than missing fields), keeps `_lock` (a register or unregister racing it takes the lock and sees
        it cleaned) and resets the singleton bookkeeping. After cleanup `release`, `managed`, `release_all`,
        `describe` and `register` raise the cleaned `RuntimeError`; `unregister` does nothing (it is part of
        teardown). `_reset_singleton_for_tests()` cleans the live instance and clears the bookkeeping.

    Registration:
        MELDER KERNEL - guarded. Created by Aether at boot; users call `ReleaseManagedSpell()` to reach it and never
        bind it as a spell.

    Subsystem Context:
        The managed lifetime (EPIC-2026-10-14-managed_spell_quantity): each managed spell version has a
        `ManagedSpellQuantity` pool in its owning root's `Creations`; a meld or an injection leases from it; this
        registry gives objects back; root teardown disposes what the pool holds. An ownership transfer moves a pool
        between stores, and the stores re-register it under its new root.

    System Context:
        Melder keeps the structure right - pools, this registry, the records that move with a transfer - and leaves
        the objects it hands out to the agents (src_architecture, "Runtime Model: Structure Is the Contract"). An
        object never released stays out and holds its place in a limited or queue pool until the root ends.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Give managed objects back: `ReleaseManagedSpell().release(obj)` returns an object leased from a
        managed_spell_quantity pool (its resets run, it is reused by the next lease); `managed(obj)` gives a lease for
        a `with` block; `release_all(objects)`; `describe(cls)` shows each pool's mode, count and idle objects. Pass
        spell_id= or conduit= only when one class is managed by several pools. In a hot loop bind it once:
        `release = ReleaseManagedSpell().release`.
    """

    _instance: ClassVar[Optional[ReleaseManagedSpell]] = None
    _singleton_lock: ClassVar[threading.RLock] = threading.RLock()
    _initialized: ClassVar[bool] = False

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_pools_by_class",
        "_registrations",
    ]

    def __new__(cls, *args: object, **kwargs: object) -> ReleaseManagedSpell:
        """
        Return the one process-wide registry instance.

        Contract:
            - Double-checked: the fast path reads the published instance without a lock; a miss takes the
              class-level `_singleton_lock` and creates the instance once.
            - Every construction returns the same object until cleanup resets the singleton.

        Returns:
            ReleaseManagedSpell: The process-wide instance.
        """
        instance = cls._instance
        if instance is None:
            with cls._singleton_lock:
                instance = cls._instance
                if instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return instance

    def __init__(self, *, aether: Optional[Aether] = None) -> None:
        """
        Initialize the registry once, for the Aether that hosts it.

        Contract:
            - Once-only: the `_initialized` check and the whole body run under `_singleton_lock`, so concurrent
              first callers build one registry; every later call returns at the unlocked fast path.
            - The first construction requires the hosting `Aether` (`Aether.__init__` passes `aether=self`). Without
              it the construction is refused and the singleton bookkeeping reset, so a later proper one succeeds;
              `import melder` boots Aether, so user code always finds the hosted instance.
            - The registry keeps no reference to its host: Aether owns it, not the other way round.
            - Starts empty: stores register their pools as they take them.

        Args:
            aether:
                The hosting Aether; required on the first construction, ignored afterwards.

        Raises:
            ValueError: On a first construction without the hosting Aether.

        Returns:
            None.
        """
        if ReleaseManagedSpell._initialized:
            return
        with ReleaseManagedSpell._singleton_lock:
            if ReleaseManagedSpell._initialized:
                return
            if aether is None:
                # Already under the singleton lock: drop the half-built instance so a later first construction by
                # Aether starts clean.
                if ReleaseManagedSpell._instance is self:
                    ReleaseManagedSpell._instance = None
                ReleaseManagedSpell._initialized = False
                raise ValueError(
                    "ReleaseManagedSpell is created by Aether at boot; construct Aether() first (import melder "
                    "does), then ReleaseManagedSpell() returns it."
                )
            try:
                super().__init__()
                self._lock: threading.Lock = threading.Lock()
                self._pools_by_class: Dict[type, Tuple[ManagedSpellQuantity, ...]] = {}
                self._registrations: Dict[int, Tuple[type, str]] = {}
                # The initialized object is the singleton, even if a refused bare construction cleared the slot
                # between this object's `__new__` and this lock.
                ReleaseManagedSpell._instance = self
                # The once-only latch flips while the lock is held, so the unlocked fast path only ever sees a
                # fully initialized registry.
                ReleaseManagedSpell._initialized = True
            except Exception:
                if ReleaseManagedSpell._instance is self:
                    ReleaseManagedSpell._instance = None
                ReleaseManagedSpell._initialized = False
                raise

    def cleanup(self) -> None:
        """
        Retire the registry and reset the singleton.

        Contract:
            - Idempotent and one-way.
            - Publishes empty maps as tombstones, so a lock-free reader racing this cleanup sees an empty registry,
              and the release fast path then misses and raises the cleaned error from the cold path.
            - Keeps `_lock` as a tombstone: a register or unregister racing this cleanup takes it and observes
              `_cleaned` instead of a missing field.
            - Never cleans a registered pool: pools belong to their stores, which unregistered them already when
              Aether tears its frames down first.
            - Resets `_instance` and `_initialized` unconditionally, as Aether does: a stale instance cannot unseat a
              live successor, because its cleanup returns at the cleaned check above.

        Threading:
            Takes `_lock` to retire the maps, then `_singleton_lock` to reset the bookkeeping; never both at once.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._registrations = {}
            self._pools_by_class = {}
        with ReleaseManagedSpell._singleton_lock:
            ReleaseManagedSpell._instance = None
            ReleaseManagedSpell._initialized = False

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the registry singleton for test isolation, the way Aether's hosted roots do.

        Contract:
            - Cleans the current instance when one exists; an `AttributeError` from a half-built instance (a
              construction refused before its state existed) is ignored.
            - Clears `_instance` and `_initialized` even when cleanup raises, so the next Aether builds a fresh
              registry. Does not create one.

        Threading:
            Holds `_singleton_lock` for the whole reset.

        Returns:
            None.
        """
        with cls._singleton_lock:
            instance = cls._instance
            if instance is None:
                cls._initialized = False
                return
            try:
                try:
                    instance.cleanup()
                except AttributeError:
                    # A half-built instance has no state to release; clearing the bookkeeping is enough.
                    pass
            finally:
                cls._instance = None
                cls._initialized = False

    @classmethod
    def _live_instance(cls) -> Optional[ReleaseManagedSpell]:
        """
        Internal

        Return the live registry, or None when there is none to reach.

        Purpose:
            The stores' teardown lookup: a store giving up its pools unregisters them from the live registry, and when
            the registry is already gone (reset for a test, or cleaned before a stray store) there is nothing to
            unregister from. Never constructs.

        Returns:
            Optional[ReleaseManagedSpell]: The initialized, uncleaned singleton, or None.
        """
        instance = cls._instance
        if instance is None or not cls._initialized:
            return None
        if instance.cleaned:
            return None
        return instance

    def register(self, pool: ManagedSpellQuantity, *, root_conduit_id: str) -> None:
        """
        Internal

        Make a pool routable: called by a root store when it takes a pool (ensure at an owner stamp, a restore).

        Contract:
            - Keys the pool by its managed class (`pool.managed_class`) and records the root whose store holds it.
            - Idempotent: the same pool, class and root register once. The same pool under a new root (a restore into
              another root) only moves its root; under a new class (a rebind that brought another class object) it
              moves to that class.
            - Publishes new maps; never mutates a published one.

        Args:
            pool:
                A live pool held by the calling store.
            root_conduit_id:
                Id of the root conduit whose store holds the pool now.

        Raises:
            RuntimeError: If the registry or the pool has been cleaned.

        Threading:
            Takes the leaf `_lock` to read and publish; no user code runs under it.

        Returns:
            None.
        """
        self.check_cleaned()
        pool.check_cleaned()
        key = pool.managed_class
        pool_id = id(pool)
        with self._lock:
            self.check_cleaned()
            previous = self._registrations.get(pool_id)
            if previous is not None and previous[0] is key:
                if previous[1] != root_conduit_id:
                    registrations = dict(self._registrations)
                    registrations[pool_id] = (key, root_conduit_id)
                    self._registrations = registrations
                return
            pools_by_class = dict(self._pools_by_class)
            if previous is not None:
                self._drop_pool(pools_by_class, previous[0], pool)
            pools_by_class[key] = pools_by_class.get(key, ()) + (pool,)
            registrations = dict(self._registrations)
            registrations[pool_id] = (key, root_conduit_id)
            self._registrations = registrations
            self._pools_by_class = pools_by_class

    def unregister(self, pool: ManagedSpellQuantity) -> None:
        """
        Internal

        Forget a pool: called by a store when it gives the pool up (extract, a restore replacing it, its cleanup).

        Contract:
            - Idempotent: an unregistered pool, or a second call, does nothing.
            - Does nothing on a cleaned registry: unregistering is part of teardown, and a registry already gone has
              nothing to forget.
            - The pool's class stays routable while it has other pools; a class with none left leaves the registry.

        Args:
            pool:
                The pool the calling store gives up.

        Threading:
            Takes the leaf `_lock` to read and publish; no user code runs under it.

        Returns:
            None.
        """
        if self._cleaned:
            return
        pool_id = id(pool)
        with self._lock:
            if self._cleaned:
                return
            previous = self._registrations.get(pool_id)
            if previous is None:
                return
            pools_by_class = dict(self._pools_by_class)
            self._drop_pool(pools_by_class, previous[0], pool)
            registrations = dict(self._registrations)
            del registrations[pool_id]
            self._registrations = registrations
            self._pools_by_class = pools_by_class

    def release(self, obj: object, *, spell_id: Optional[str] = None, conduit: Optional[Conduit] = None) -> None:
        """
        Give one leased object back to its pool.

        Purpose:
            The common hand-back. With one pool for the object's class and no filter it is one dict get and the
            pool's `put_back`; otherwise the cold resolver picks the pool.

        Contract:
            - The pool runs its reset methods in order, then the object is idle for the next lease; an elastic pool
              above its baseline may trim its oldest idle objects (disposed outside every lock).
            - Several pools for the class: `spell_id` keeps the pool of that version, `conduit` the pools held by its
              root (a root or one of its lessers names that root); when more than one remains, the pools whose version
              is the one its index selects are preferred; exactly one must remain.
            - Trusted, never checked: the object is assumed to be one this pool leased.

        Args:
            obj:
                An object leased from a managed spell's pool.
            spell_id:
                Optional version id picking one pool.
            conduit:
                Optional root conduit, or a lesser of it, picking the pools that root holds.

        Raises:
            ValueError: The class is managed by no live pool, the filters match none, or several remain.
            TypeError: `spell_id` is not a str, or `conduit` is not a Conduit.
            RuntimeError: The registry or the given conduit was cleaned, or the pool was torn down with its root (the
                object is then the caller's to dispose).
            Exception: What a reset raised, after the pool destroyed the object.
            ExceptionGroup: A raising reset whose disposal failed too, or an elastic trim's disposal failures.

        Threading:
            The fast path takes no lock. Safe from any thread.

        Returns:
            None.
        """
        pools = self._pools_by_class.get(type(obj))
        if pools is not None and len(pools) == 1 and spell_id is None and conduit is None:
            pools[0].put_back(obj)
            return
        self._resolve_pool(obj, pools, spell_id, conduit).put_back(obj)

    def managed(
            self,
            obj: ManagedObjectT,
            *,
            spell_id: Optional[str] = None,
            conduit: Optional[Conduit] = None,
    ) -> ManagedSpellLease[ManagedObjectT]:
        """
        Return a lease that gives one leased object back once, by `release()` or at the end of a `with` block.

        Contract:
            - The pool is resolved now, exactly as `release` resolves it; the lease then needs no lookup.
            - `with ReleaseManagedSpell().managed(obj) as o:` releases `o` when the block ends, whether or not it
              raised, and never suppresses the block's exception.

        Args:
            obj:
                An object leased from a managed spell's pool.
            spell_id:
                Optional version id picking one pool.
            conduit:
                Optional root conduit, or a lesser of it, picking the pools that root holds.

        Raises:
            ValueError, TypeError, RuntimeError: As `release` raises them while resolving the pool.

        Returns:
            ManagedSpellLease: The lease over `obj` and its pool.
        """
        pools = self._pools_by_class.get(type(obj))
        if pools is not None and len(pools) == 1 and spell_id is None and conduit is None:
            return ManagedSpellLease(obj, pools[0])
        return ManagedSpellLease(obj, self._resolve_pool(obj, pools, spell_id, conduit))

    def release_all(
            self,
            objects: Iterable[object],
            *,
            spell_id: Optional[str] = None,
            conduit: Optional[Conduit] = None,
    ) -> None:
        """
        Give many leased objects back, attempting every one.

        Contract:
            - Each object is released as `release(obj, spell_id=..., conduit=...)` would; a failure does not stop the
              rest.
            - Every failure is raised together afterwards, in object order, as one `ExceptionGroup`.

        Args:
            objects:
                The leased objects (any iterable, consumed once).
            spell_id:
                Optional version id picking one pool for every object.
            conduit:
                Optional root conduit, or a lesser of it, picking the pools that root holds.

        Raises:
            RuntimeError: If the registry has been cleaned (nothing is released).
            ExceptionGroup: "Errors occurred releasing <n> of <m> managed objects", after every object was attempted.

        Returns:
            None.
        """
        self.check_cleaned()
        errors: List[Exception] = []
        attempted = 0
        for obj in objects:
            attempted += 1
            try:
                self.release(obj, spell_id=spell_id, conduit=conduit)
            except Exception as error:
                # Documented aggregation: every object is attempted, every failure reported.
                errors.append(error)
        if errors:
            raise ExceptionGroup(f"Errors occurred releasing {len(errors)} of {attempted} managed objects", errors)

    def describe(self, cls: type) -> Tuple[Dict[str, Any], ...]:
        """
        Return one snapshot per live pool of a managed class.

        Contract:
            - Each entry is the pool's own `describe()` (mode, limit, timeout, count, idle and out counts, retention,
              spell identity, children recorded) plus `holding_conduit_id` (the root whose store holds the pool now)
              and `active_version` (whether its version is the one its index selects).
            - Entries follow registration order; a class with no pool answers `()`.
            - A read: it creates, registers and changes nothing.

        Args:
            cls:
                The managed class.

        Raises:
            TypeError: If `cls` is not a class.
            RuntimeError: If the registry has been cleaned, or a pool was torn down with its root while it was being
                described.

        Returns:
            Tuple[Dict[str, Any], ...]: The snapshots.
        """
        self.check_cleaned()
        if not isinstance(cls, type):
            raise TypeError(f"describe takes a class; got {type(cls).__name__}.")
        pools = self._pools_by_class.get(cls, ())
        registrations = self._registrations
        snapshots: List[Dict[str, Any]] = []
        for pool in pools:
            snapshot = pool.describe()
            registration = registrations.get(id(pool))
            snapshot["holding_conduit_id"] = registration[1] if registration is not None else None
            snapshot["active_version"] = self._is_selected_version(pool)
            snapshots.append(snapshot)
        return tuple(snapshots)

    def _resolve_pool(
            self,
            obj: object,
            pools: Optional[Tuple[ManagedSpellQuantity, ...]],
            spell_id: Optional[str],
            conduit: Optional[Conduit],
    ) -> ManagedSpellQuantity:
        """
        Pick the pool one object goes back to: the cold path of `release` and `managed`.

        Contract:
            - Raises the cleaned error first, then checks the filters' types.
            - No pool for the class -> ValueError naming the remedy.
            - Keeps the pools matching `spell_id` and the root `conduit` names; when several remain, keeps those whose
              version its index selects; exactly one must remain, else ValueError listing every candidate (spell id,
              binding, frame, holding root, selected) and the keywords that pick one.

        Args:
            obj: The object being released.
            pools: The pools registered for its class, as the caller read them (None when there are none).
            spell_id: The version filter, or None.
            conduit: The root filter, or None.

        Raises:
            RuntimeError, TypeError, ValueError: As `release` documents.

        Returns:
            ManagedSpellQuantity: The pool.
        """
        self.check_cleaned()
        if spell_id is not None and not isinstance(spell_id, str):
            raise TypeError(f"spell_id must be a str or None; got {type(spell_id).__name__}.")
        root_conduit_id = self._root_conduit_id_of(conduit) if conduit is not None else None
        class_name = type(obj).__qualname__
        if not pools:
            raise ValueError(
                f"{class_name} is not a managed spell class in any live root: bind it with "
                f"existence=Existence.managed_spell_quantity, or its root was torn down."
            )
        registrations = self._registrations
        candidates = [
            pool for pool in pools
            if (spell_id is None or pool.spell_id == spell_id)
            and (root_conduit_id is None or self._holding_root(registrations, pool) == root_conduit_id)
        ]
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            selected = [pool for pool in candidates if self._is_selected_version(pool)]
            if len(selected) == 1:
                return selected[0]
            listing = "; ".join(self._describe_candidate(registrations, pool) for pool in candidates)
            raise ValueError(
                f"{class_name} is managed by {len(candidates)} pools: {listing}. "
                f"Pass spell_id=... or conduit=... to pick one."
            )
        filters = []
        if spell_id is not None:
            filters.append(f"spell_id={spell_id}")
        if root_conduit_id is not None:
            filters.append(f"conduit root {root_conduit_id}")
        listing = "; ".join(self._describe_candidate(registrations, pool) for pool in pools)
        raise ValueError(
            f"No pool of managed class {class_name} matches {', '.join(filters)}. Its pools: {listing}. "
            f"Pass the spell_id or conduit of one of them."
        )

    @staticmethod
    def _root_conduit_id_of(conduit: Conduit) -> str:
        """
        Return the id of the root a conduit filter names.

        Contract:
            A root names itself; a lesser names its root (the root whose store holds every pool its world leases from).

        Args:
            conduit: A root conduit or one of its lessers.

        Raises:
            TypeError: If `conduit` is not a Conduit.
            RuntimeError: If the conduit has been cleaned.

        Returns:
            str: The root conduit's id.
        """
        # Imported here: the Conduit module imports the creations package this module belongs to.
        from melder.aether.conduit.conduit import Conduit

        if not isinstance(conduit, Conduit):
            raise TypeError(
                f"conduit must be a Conduit (a root or one of its lessers); got {type(conduit).__name__}."
            )
        conduit.check_cleaned()
        return conduit._root_conduit_id

    @staticmethod
    def _holding_root(registrations: Dict[int, Tuple[type, str]], pool: ManagedSpellQuantity) -> Optional[str]:
        """
        Return the root a pool's registration records, or None when it has none (a racing unregister).

        Args:
            registrations: The registrations map the caller read.
            pool: The pool.

        Returns:
            Optional[str]: The holding root's id.
        """
        registration = registrations.get(id(pool))
        return registration[1] if registration is not None else None

    @staticmethod
    def _is_selected_version(pool: ManagedSpellQuantity) -> bool:
        """
        Return whether a pool's version is the one its index currently selects.

        Contract:
            False for a pool torn down with its root, a Spell cleaned by its Book, or a cleaned index; never raises
            for those, including a teardown racing this read (each read below is cleanup-safe).

        Args:
            pool: The pool.

        Returns:
            bool: True when the pool's spell id is its index's selected id.
        """
        spell = pool._spell_unless_cleaned()
        if spell is None:
            return False
        index = spell._spell_index_unless_cleaned()
        if index is None:
            return False
        return index._is_selected_unless_cleaned(pool.spell_id)

    def _describe_candidate(self, registrations: Dict[int, Tuple[type, str]], pool: ManagedSpellQuantity) -> str:
        """
        Name one pool for an error message.

        Args:
            registrations: The registrations map the caller read.
            pool: The pool.

        Returns:
            str: "spell_id=<id>, binding=<name or default>, frame=<frame>, root=<root>, active=<bool>".
        """
        binding_name = pool.binding_name if pool.binding_name is not None else "default"
        return (
            f"spell_id={pool.spell_id}, binding={binding_name}, frame={pool.frame_name}, "
            f"root={self._holding_root(registrations, pool)}, active={self._is_selected_version(pool)}"
        )

    @staticmethod
    def _drop_pool(
            pools_by_class: Dict[type, Tuple[ManagedSpellQuantity, ...]],
            key: type,
            pool: ManagedSpellQuantity,
    ) -> None:
        """
        Remove one pool from a class's tuple in an unpublished map, dropping the class when none remain.

        Args:
            pools_by_class: The new map being built (not yet published).
            key: The class the pool was registered under.
            pool: The pool to remove.

        Returns:
            None.
        """
        remaining = tuple(registered for registered in pools_by_class.get(key, ()) if registered is not pool)
        if remaining:
            pools_by_class[key] = remaining
        else:
            pools_by_class.pop(key, None)
