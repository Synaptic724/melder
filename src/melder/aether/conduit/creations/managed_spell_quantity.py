import threading
import time
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


class ManagedSpellQuantity(AbstractElasticPool[Any]):
    """
    The pool of one `Existence.managed_spell_quantity` spell version in its owner root's store.

    Purpose:
        Keep the IDLE objects of one managed spell for reuse, account for how many of its objects are alive, and
        apply the spell's mode when a lease misses: `elastic` builds and keeps what demand needed (the kernel pools'
        retention, 0.2.8234), `limited_quantity` refuses past its limit, `queue` waits for a release up to its
        timeout. Objects are leased by the meld's emitted plan (an idle pop, else `reserve()` and a build) and come
        back through `put_back(obj)` (the release behind `ReleaseManagedSpell`), optionally reset on the way.

    Responsibilities:
        - `reserve()`: the cold first step of a miss - account a place for the plan to build into, or refuse, or
          (queue, and limited racing a release) hand back an object that became idle.
        - `put_back(obj)`: run the reset names in order outside every lock, make the object idle, wake one queue
          waiter, and trim above the baseline through the base pool's elastic band.
        - Record the disposal-bearing `many` children built for an object (`adopt`) and dispose them with it
          (`destroy_object`); give a failed build's place back and dispose its children (`abandon`).
        - `cleanup()`: dispose every idle object and every recorded child, wake every waiter, retire the pool.

    Sizes:
        - elastic: `baseline_idle = min(20, limit)`, `max_idle = limit`, every other retention argument the base
          default the kernel pools use (no stretch headroom, settle 1800 s, decay 10% per 600 s). With a limit of
          20 or less it is a fixed-capacity pool: a return above the limit evicts the oldest idle object.
        - limited_quantity and queue: `baseline_idle = max_idle = limit`. Idle objects never outnumber the count,
          which never exceeds the limit, so nothing is ever evicted.

    Contract:
        - Built only by `Creations.ensure_managed_quantity(spell)`: one pool per (root store, managed version).
        - A managed spell's settings are not part of its spell_id (owner ruling 2026-10-17), so a definition bound
          again under the spell_id with another mode, limit, timeout or reset names meets this pool, which takes
          the new settings and keeps every object alive and counted (`_rebind_spell`).
        - The pool never constructs (`create_object` and `acquire` refuse): the plan builds, after `reserve()`.
        - `count` is the number of objects built and alive, idle plus out. Only `reserve()` raises it (under the
          lock, after the mode's check); a destroy or an abandoned build lowers it, never below 0.
        - limited_quantity and queue: `count <= limit` at every moment.
        - No reference to an object that is out is kept (owner: "we don't care about identity"): only `id(obj)`
          keys a children record, so a release is trusted, never checked, and a stray object is simply pooled.
        - Disposal (the Spell's `disposal_method_names`, then the object's recorded children, newest first) runs
          only when the pool destroys an object: an elastic trim, a raising reset, teardown. Never on a release.
        - Failures follow `Creations`: every method of every object runs; each failing method is one
          `RuntimeError` chained from what it raised; a verb that disposes raises them as one `ExceptionGroup`.

    Owned State:
        - The base pool's state: `_idle` (idle objects, oldest left, newest right), `_lock`, the retention fields.
        - `_count`: objects built and alive; written only under `_lock`.
        - `_condition`: a `threading.Condition` over `_lock`, for queue waits and wake-ups.
        - `_children_by_object`: `id(obj)` -> `[(child, child_methods), ...]` in build order, for objects that had
          disposal-bearing `many` children; `_orphaned_children`: records whose object was dropped while out (its
          id was reused by a newer object), kept for teardown. Both written under `_lock`.
        - Fields copied from the Spell at construction: spell id, name, binding name, frame; the policy - mode,
          limit, timeout, reset names - which a rebind under the same spell_id replaces with the new Spell's
          settings (`_rebind_spell`); the Spell's disposal list (borrowed, by reference); the owner root's id.
        - `_spell`: the Spell, borrowed (never cleaned here); `ReleaseManagedSpell`'s cold resolver reads it through
          `_spell_unless_cleaned` (S4).
        - `_managed_class`: the bound class (`spell.spell`), the key `ReleaseManagedSpell` routes releases by;
          re-captured when a rebind re-points the pool, and kept after cleanup.

    Threading:
        - The warm lease (`_idle.pop()` in the plan) and a resetless release below the baseline take no lock:
          `deque.pop` and `deque.append` are atomic per object on 3.14t and the GIL build.
        - `_lock` is a LEAF held only for `count`, the children maps and condition waits. Resets, disposal
          methods and constructors never run under it, and it is never held together with a store lock.
        - A queue wait sleeps on `_condition` (releasing `_lock`) until a place or an idle object appears, the
          deadline passes, or teardown wakes it. Its timeout is required at bind, so a wait under an enclosing
          build guard is bounded.

    Lifecycle / Cleanup:
        Cleaned by the owning store's cleanup (root teardown), by an extract that gives it up for good, or by a
        restore that replaces it. `cleanup()` is idempotent and one-way. Objects out stay their holders'; a release
        after teardown raises. Teardown detaches the idle objects and the children maps (swapping in empty ones)
        and deletes the borrowed Spell under the lock; every other field (the class key included) stays as a
        documented tombstone, because an emitted plan,
        a queue waiter, a release or a trim racing the teardown must reach the torn-down `RuntimeError`, not an
        `AttributeError` (the base pool keeps all of its fields for the same reason).

    Registration:
        MELDER KERNEL - guarded. Constructed only by `Creations`; never user-instantiated and never bindable.

    Subsystem Context:
        A concrete `AbstractElasticPool`, like `SpellSpacePool` and `ConduitPool`, but holding application objects
        of one managed spell instead of Melder's own scopes. It lives in `Creations._managed_quantities` - a map of
        its own beside `_creations` - so no resolution path, live probe or purge can mistake a pool for an object.

    System Context:
        The pooled lifetime (EPIC-2026-10-14-managed_spell_quantity): a meld or an injection leases from the pool,
        `ReleaseManagedSpell` gives objects back, the root's teardown disposes what the pool holds, and an ownership
        transfer moves the pool as a store row. Melder keeps this structure right; the objects it hands out are the
        agents' (src_architecture, "Runtime Model: Structure Is the Contract").

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The pool of one managed spell version in its root's store: idle objects, the count, the
        mode's refusal or wait, resets on release, disposal on destroy. Melder kernel machinery: read it to
        understand the runtime; give objects back through ReleaseManagedSpell, not this class.
    """

    _ELASTIC_BASELINE_IDLE: ClassVar[int] = 20

    __slots__ = AbstractElasticPool.__slots__ + [
        "_spell",
        "_managed_class",
        "_spell_id",
        "_spell_name",
        "_binding_name",
        "_frame_name",
        "_owner_conduit_id",
        "_mode",
        "_limit",
        "_timeout_seconds",
        "_reset_method_names",
        "_disposal_method_names",
        "_notify_on_return",
        "_count",
        "_condition",
        "_children_by_object",
        "_orphaned_children",
    ]

    def __init__(
            self,
            *,
            spell: Spell,
            owner_conduit_id: str,
            time_func: Optional[Callable[[], float]] = None,
    ) -> None:
        """
        Compose the pool of one managed spell version from the Spell's options.

        Contract:
            - Reads the options Bind normalized on the Spell (mode, limit, timeout, reset names) and its disposal
              list; does not re-validate them.
            - Sizes the base pool per mode (see the class docstring) and starts with no object: count 0, idle 0.
            - Keeps the Spell borrowed and its disposal list by reference.

        Args:
            spell:
                A Spell bound with `Existence.managed_spell_quantity`.
            owner_conduit_id:
                Id of the root conduit whose store holds this pool.
            time_func:
                Optional monotonic clock for the elastic retention, for deterministic tests. Queue waits always
                use `time.monotonic`, because they really sleep.

        Raises:
            ValueError:
                If the spell is not `Existence.managed_spell_quantity`.

        Returns:
            None.
        """
        existence = spell.existence
        if existence is not Existence.managed_spell_quantity:
            raise ValueError(
                f"ManagedSpellQuantity needs an Existence.managed_spell_quantity spell; "
                f"'{spell.spell_name}' is {existence.name}."
            )
        mode = spell.managed_spell_mode
        limit = spell.managed_spell_limit
        if mode is ManagedSpellMode.elastic:
            super().__init__(
                baseline_idle=min(self._ELASTIC_BASELINE_IDLE, limit),
                max_idle=limit,
                time_func=time_func,
            )
        else:
            super().__init__(baseline_idle=limit, max_idle=limit, time_func=time_func)
        self._spell: Spell = spell
        # The registry's key: a managed spell binds a class, and type(obj) of every object it builds is that class.
        self._managed_class: type = spell.spell
        self._spell_id: str = spell.spell_id
        self._spell_name: str = spell.spell_name
        self._binding_name: Optional[str] = spell.binding_name
        self._frame_name: str = spell.aetheric_frame
        self._owner_conduit_id: str = owner_conduit_id
        self._mode: ManagedSpellMode = mode
        self._limit: int = limit
        self._timeout_seconds: Optional[float] = spell.managed_spell_timeout_seconds
        self._reset_method_names: Tuple[str, ...] = spell.managed_spell_reset_methods
        self._disposal_method_names: List[str] = spell.disposal_method_names
        # Only queue leases wait, so only a queue release has a waiter to wake.
        self._notify_on_return: bool = mode is ManagedSpellMode.queue
        self._count: int = 0
        self._condition: threading.Condition = threading.Condition(self._lock)
        self._children_by_object: Dict[int, List[Tuple[object, List[str]]]] = {}
        self._orphaned_children: List[List[Tuple[object, List[str]]]] = []

    def cleanup(self) -> None:
        """
        Dispose everything the pool holds and retire it.

        Contract:
            - Idempotent and one-way: a retired pool leases nothing and takes nothing back.
            - Under `_lock`: marks the pool cleaned, drains the idle objects (one atomic `popleft` each, so an
              object is either taken by a racing plan or by this teardown, never both), swaps the children maps for
              empty ones, and wakes every queue waiter (each then raises the torn-down `RuntimeError`).
            - Outside the lock, in order: each idle object, newest first, with its recorded children (newest
              first); then the records of objects still out (newest record first) - the children die with the
              scope, the objects stay their holders'; then the orphaned records.
            - Deletes the borrowed Spell while it holds the lock, so `_spell_unless_cleaned` never meets a half-retired
              pool; the other fields, the class key included, stay as documented tombstones (class docstring).

        Raises:
            ExceptionGroup:
                One chained `RuntimeError` per failing disposal method, after every object was attempted.

        Threading:
            Takes `_lock` once for the detach; no user code runs under it. An object released after the drain
            lands in the retired deque undisposed - releases racing teardown are a caller contract violation, as
            for the kernel pools.

        Returns:
            None.
        """
        if self._cleaned:
            return
        condition = self._condition
        with condition:
            if self._cleaned:
                return
            self._cleaned = True
            idle = self._idle
            idle_objects: List[object] = []
            while True:
                try:
                    idle_objects.append(idle.popleft())
                except IndexError:
                    break
            children_by_object = self._children_by_object
            orphaned_children = self._orphaned_children
            self._children_by_object = {}
            self._orphaned_children = []
            # Under the lock: `_spell_unless_cleaned` reads the cleaned flag and the Spell under it.
            del self._spell
            condition.notify_all()

        failures: List[Exception] = []
        methods = self._disposal_method_names
        for obj in reversed(idle_objects):
            failures.extend(self._run_disposal_methods(obj, methods))
            children = children_by_object.pop(id(obj), None)
            if children:
                failures.extend(self._dispose_children(children))
        for children in reversed(list(children_by_object.values())):
            failures.extend(self._dispose_children(children))
        for children in reversed(orphaned_children):
            failures.extend(self._dispose_children(children))
        if failures:
            raise ExceptionGroup(f"Errors occurred cleaning the pool of managed spell '{self._spell_name}'", failures)

    @property
    def spell(self) -> Spell:
        """
        Return the managed Spell this pool belongs to (borrowed).

        Contract:
            The current Spell object of the spell_id: a rebind that meets this pool under the same id re-points
            it and gives the pool its settings (`Creations.ensure_managed_quantity`). It may be cleaned by its
            Book while the pool lives on.

        Raises:
            RuntimeError: If the pool has been cleaned.

        Returns:
            Spell: The borrowed Spell.
        """
        self.check_cleaned()
        return self._spell

    def _spell_unless_cleaned(self) -> Optional[Spell]:
        """
        Internal

        Return the borrowed Spell, or None once the pool is torn down.

        Purpose:
            The cleanup-safe read `ReleaseManagedSpell` uses while it resolves a release or describes a pool: a
            teardown racing it answers None instead of raising.

        Threading:
            Reads the cleaned flag and the Spell under `_lock`, the lock `cleanup()` marks the pool cleaned and
            deletes the Spell under. Holds no other lock and runs no user code.

        Returns:
            Optional[Spell]: The Spell of the pool's version, or None when the pool was cleaned.
        """
        with self._lock:
            if self._cleaned:
                return None
            return self._spell

    @property
    def managed_class(self) -> type:
        """
        Return the managed class, the key `ReleaseManagedSpell` routes this pool's releases by.

        Contract:
            The class the managed spell binds (`spell.spell`); every object the pool holds is of exactly this class.
            Re-captured when a rebind re-points the pool at another Spell object. Readable after cleanup.

        Returns:
            type: The managed class.
        """
        return self._managed_class

    @property
    def spell_id(self) -> str:
        """
        Return the spell_id the pool is stored under.

        Returns:
            str: The managed spell's spell_id (readable after cleanup).
        """
        return self._spell_id

    @property
    def spell_name(self) -> str:
        """
        Return the managed spell's display name.

        Returns:
            str: The name every pool error uses (readable after cleanup).
        """
        return self._spell_name

    @property
    def binding_name(self) -> Optional[str]:
        """
        Return the managed spell's binding name.

        Returns:
            Optional[str]: The binding name, or None for the default binding.
        """
        return self._binding_name

    @property
    def frame_name(self) -> str:
        """
        Return the aetheric frame the managed spell is bound in.

        Returns:
            str: The frame name.
        """
        return self._frame_name

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the id of the root conduit whose store holds this pool.

        Contract:
            Fixed at construction. An ownership transfer moves the pool object into the target root's store; this
            id names the root that composed it, and the holding store says where it lives now.

        Returns:
            str: The composing root's conduit id.
        """
        return self._owner_conduit_id

    @property
    def mode(self) -> ManagedSpellMode:
        """
        Return the pool's mode.

        Returns:
            ManagedSpellMode: elastic, limited_quantity or queue.
        """
        return self._mode

    @property
    def limit(self) -> int:
        """
        Return the pool's limit.

        Returns:
            int: elastic - the most idle objects kept; limited_quantity and queue - the most objects alive.
        """
        return self._limit

    @property
    def timeout_seconds(self) -> Optional[float]:
        """
        Return how long a queue lease waits.

        Returns:
            Optional[float]: The queue timeout in seconds; None for elastic and limited_quantity.
        """
        return self._timeout_seconds

    @property
    def reset_method_names(self) -> Tuple[str, ...]:
        """
        Return the reset method names a release runs, in order.

        Returns:
            Tuple[str, ...]: The names; empty when the binding named none.
        """
        return self._reset_method_names

    @property
    def disposal_method_names(self) -> Tuple[str, ...]:
        """
        Return the disposal method names run when the pool destroys an object.

        Returns:
            Tuple[str, ...]: A copy of the Spell's ordered disposal names.
        """
        return tuple(self._disposal_method_names)

    @property
    def count(self) -> int:
        """
        Return how many of the pool's objects are alive, idle plus out.

        Contract:
            Read without the lock (one int read); it may move under concurrent leases and releases.

        Returns:
            int: Objects built and not destroyed.
        """
        return self._count

    def reserve(self) -> Optional[object]:
        """
        Take a place for one new object on a lease that found nothing idle.

        Purpose:
            The cold first step of an emitted plan's miss, before any child or the object is built, so a refusal
            or a wait never strands a built object.

        Contract:
            - elastic: `count += 1` and records pressure for the elastic retention (`_note_miss`); returns None.
            - limited_quantity: below the limit `count += 1` and returns None; at the limit returns an object that
              became idle since the plan's pop (served, no build), else raises `ManagedSpellExhaustedError`.
            - queue: waits on the condition until a place frees (`count += 1`, returns None) or an object comes
              back (returned: served, no build), or `managed_spell_timeout_seconds` pass from the call (raises
              `ManagedSpellExhaustedError`). The deadline is taken once, at the call.
            - Returns None when the caller must build into the reserved place; otherwise the object to use as is.

        Raises:
            ManagedSpellExhaustedError:
                limited_quantity at its limit with nothing idle; queue at its deadline. Nothing was built and the
                count is unchanged.
            RuntimeError:
                If the pool was torn down (also for a queue waiter woken by the teardown).

        Threading:
            Takes `_lock` (or waits on `_condition`, which releases it while sleeping); no user code runs under it.

        Returns:
            Optional[object]: None to build, or an idle object served to this lease.
        """
        mode = self._mode
        if mode is ManagedSpellMode.elastic:
            with self._lock:
                if self._cleaned:
                    raise self._torn_down_error("nothing can be leased from it.")
                self._count += 1
            self._note_miss()
            return None
        if mode is ManagedSpellMode.limited_quantity:
            return self._reserve_limited()
        return self._reserve_queue()

    def _reserve_limited(self) -> Optional[object]:
        """
        Reserve a place in a limited_quantity pool, serve a returned object, or refuse.

        Contract:
            - Under `_lock`: a torn-down pool raises; below the limit the count rises; at the limit an idle object
              (a release that raced the plan's empty pop) is handed out.
            - Otherwise raises after releasing the lock, nothing built.

        Raises:
            ManagedSpellExhaustedError: At the limit with nothing idle.
            RuntimeError: If the pool was torn down.

        Returns:
            Optional[object]: None to build, or the idle object.
        """
        with self._lock:
            if self._cleaned:
                raise self._torn_down_error("nothing can be leased from it.")
            if self._count < self._limit:
                self._count += 1
                return None
            try:
                return self._idle.pop()
            except IndexError:
                pass
        raise ManagedSpellExhaustedError.limited(
            spell_id=self._spell_id,
            spell_name=self._spell_name,
            limit=self._limit,
        )

    def _reserve_queue(self) -> Optional[object]:
        """
        Reserve a place in a queue pool, waiting for one or for a returned object until the deadline.

        Contract:
            - The deadline is `time.monotonic() + timeout`, taken once.
            - Each wake-up re-checks, in order: torn down (raise), a free place (count + 1, None), an idle object
              (returned), the deadline (raise), else waits the remaining time.
            - Woken by `put_back` (one waiter), `destroy_object` and `abandon` (one place freed) and `cleanup`
              (all waiters).

        Raises:
            ManagedSpellExhaustedError: At the deadline.
            RuntimeError: If the pool was or is torn down while waiting.

        Returns:
            Optional[object]: None to build, or the idle object.
        """
        condition = self._condition
        deadline = time.monotonic() + self._timeout_seconds
        with condition:
            while True:
                if self._cleaned:
                    raise self._torn_down_error("nothing can be leased from it.")
                if self._count < self._limit:
                    self._count += 1
                    return None
                try:
                    return self._idle.pop()
                except IndexError:
                    pass
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    break
                condition.wait(remaining)
        raise ManagedSpellExhaustedError.queue(
            spell_id=self._spell_id,
            spell_name=self._spell_name,
            limit=self._limit,
            timeout_seconds=self._timeout_seconds,
        )

    def put_back(self, obj: object) -> None:
        """
        Release one object into the pool: optional reset, then idle again for the next lease.

        Purpose:
            The one way back (behind `ReleaseManagedSpell` and the lease's `with`). A release is trusted, never
            checked: identity is not tracked.

        Contract:
            - Raises the torn-down `RuntimeError` when the pool was cleaned; the object is left untouched.
            - Runs each reset name in order (`getattr(obj, name)()`, a dynamic name), outside every lock.
            - A reset that raises: the object is destroyed (`destroy_object`: disposal methods, recorded children,
              its place freed, a waiter woken) and the reset error propagates as raised - or, when the disposal
              failed too, one `ExceptionGroup` of the reset error and the disposal failures. Later resets do not
              run and the object is not pooled.
            - Otherwise appends the object (the newest, leased next), wakes one queue waiter, and when more than
              `baseline_idle` objects are idle runs the base pool's elastic band (`_rebalance_after_return`):
              stretch under pressure, a due decay step, and the trim of the oldest surplus, destroyed outside the
              lock. A destroy that raises there propagates from this release.
            - Never runs disposal methods on the released object itself, except through a raising reset or a trim.

        Args:
            obj:
                An object leased from this pool (trusted).

        Raises:
            RuntimeError: If the pool was torn down with its root.
            Exception: What a reset raised, after the object was destroyed.
            ExceptionGroup: A raising reset whose destroy failed too; or a trim's disposal failures.

        Threading:
            Lock-free for a resetless release at or below the baseline (one append); queue mode takes `_lock` to
            notify; the elastic band takes it only to adjust and detach.

        Returns:
            None.
        """
        if self._cleaned:
            raise self._torn_down_error("the object is yours to dispose.")
        for method_name in self._reset_method_names:
            try:
                getattr(obj, method_name)()
            except Exception as reset_error:
                failures = self._destroy_collecting(obj)
                if failures:
                    raise ExceptionGroup(
                        f"Reset '{method_name}' of managed spell '{self._spell_name}' raised, and disposing the "
                        f"object failed",
                        [reset_error, *failures],
                    ) from None
                raise
        idle = self._idle
        idle.append(obj)
        if self._notify_on_return:
            condition = self._condition
            with condition:
                condition.notify()
        if len(idle) > self._baseline_idle:
            self._rebalance_after_return()

    def release(self, obj: object) -> None:
        """
        Release one object; the base pool's verb, identical to `put_back`.

        Args:
            obj: An object leased from this pool.

        Raises:
            RuntimeError, Exception, ExceptionGroup: As `put_back`.

        Returns:
            None.
        """
        self.put_back(obj)

    def abandon(self, children: List[Tuple[object, List[str]]], error: BaseException) -> None:
        """
        Give a failed build's place back and dispose the children it built.

        Purpose:
            The emitted miss's failure path: the object's construction (or one of its children's) raised after
            `reserve()` took a place.

        Contract:
            - `count -= 1` (never below 0) and one queue waiter woken, under `_condition`.
            - Disposes `children` - `(child, child_methods)` pairs in build order - newest first, outside the lock.
            - A child that fails to dispose adds a note to `error` (the build's exception, which the caller
              re-raises); nothing new is raised here.

        Args:
            children:
                The disposal-bearing `many` children the failed build registered for its object, possibly empty.
            error:
                The exception the build raised; receives one note per disposal failure.

        Returns:
            None.
        """
        condition = self._condition
        with condition:
            if self._count > 0:
                self._count -= 1
            condition.notify()
        for failure in self._dispose_children(children):
            error.add_note(
                f"Disposing a child built for the failed object of managed spell '{self._spell_name}' "
                f"failed: {failure}"
            )

    def adopt(self, obj: object, children: List[Tuple[object, List[str]]]) -> None:
        """
        Record the disposal-bearing `many` children built for one object, so they die with it.

        Contract:
            - No-op for an empty `children` (only objects with such children get a record).
            - Records `children` (the list object itself is kept) under `id(obj)`. A record already under that id
              belonged to an object dropped while out whose id was reused; it moves to the orphaned records and is
              disposed at teardown.
            - Runs no user code on a live pool.
            - On a torn-down pool (a build that finished after its root's teardown): runs the object's disposal
              methods and the children's, then raises the torn-down `RuntimeError` - a retired pool owns nothing,
              as `Creations` refuses a publish into a cleaned store.

        Args:
            obj:
                The object just built for a lease.
            children:
                `(child, child_methods)` pairs in build order.

        Raises:
            RuntimeError:
                If the pool was torn down; chained from an `ExceptionGroup` of disposal failures when any.

        Returns:
            None.
        """
        if not children:
            return
        with self._lock:
            if not self._cleaned:
                key = id(obj)
                previous = self._children_by_object.get(key)
                if previous is not None:
                    self._orphaned_children.append(previous)
                self._children_by_object[key] = children
                return
        failures = self._run_disposal_methods(obj, self._disposal_method_names)
        failures.extend(self._dispose_children(children))
        error = self._torn_down_error("the object built meanwhile and its children were disposed.")
        if failures:
            raise error from ExceptionGroup(
                f"Errors occurred disposing an object of managed spell '{self._spell_name}' built after teardown",
                failures,
            )
        raise error

    def destroy_object(self, obj: object) -> None:
        """
        Permanently destroy one object of this pool and free its place.

        Purpose:
            The base pool's destroy hook, called by its trims (elastic band, fixed-capacity eviction), and by
            `put_back` for a raising reset.

        Contract:
            - Runs the Spell's disposal methods in order, outside every lock; then, under `_condition`, removes the
              object's children record, takes `count` down by one (never below 0) and wakes one queue waiter;
              then disposes those children newest first, outside the lock.
            - Every method of every object runs even after one fails.

        Args:
            obj:
                The object to destroy.

        Raises:
            ExceptionGroup:
                One chained `RuntimeError` per failing disposal method.

        Returns:
            None.
        """
        failures = self._destroy_collecting(obj)
        if failures:
            raise ExceptionGroup(
                f"Errors occurred disposing an object of managed spell '{self._spell_name}'",
                failures,
            )

    def _destroy_collecting(self, obj: object) -> List[Exception]:
        """
        Destroy one object and return its disposal failures instead of raising them.

        Contract:
            As `destroy_object`; the caller decides how to raise the failures.

        Args:
            obj: The object to destroy.

        Returns:
            List[Exception]: One chained `RuntimeError` per failing method, in attempt order.
        """
        failures = self._run_disposal_methods(obj, self._disposal_method_names)
        condition = self._condition
        with condition:
            children = self._children_by_object.pop(id(obj), None)
            if self._count > 0:
                self._count -= 1
            condition.notify()
        if children:
            failures.extend(self._dispose_children(children))
        return failures

    def create_object(self, *args: Any, **kwargs: Any) -> Any:
        """
        Refuse: the pool never builds.

        Contract:
            The meld's emitted plan builds a managed object on a miss, after `reserve()`, so its children, overrides
            and failure path stay in the plan.

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError(
            "ManagedSpellQuantity never builds an object: the meld's plan builds it on a miss after reserve()."
        )

    def acquire(self, *args: Any, **kwargs: Any) -> Any:
        """
        Refuse the base pool's lease verb.

        Contract:
            A managed lease is the plan's inline idle pop, else `reserve()` and a build; there is no pool-side
            factory to call.

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError(
            "ManagedSpellQuantity is leased by the meld's plan (an idle pop, else reserve()), never through acquire()."
        )

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached snapshot of the pool: what is alive, idle and out, and the policy.

        Contract:
            - The base pool's retention keys (baseline, target, max, idle count, stretch, settle, decay) without the
              base's advisory `in_use_count`, which this pool never maintains.
            - Plus: spell identity (`spell_id`, `spell_name`, `binding_name`, `frame_name`, `owner_conduit_id`),
              the policy (`mode` by name, `limit`, `timeout_seconds`, `reset_method_names`,
              `disposal_method_names` as lists), `count`, `out_count` (count minus idle, never below 0) and
              `children_recorded` (children recorded for objects alive or dropped).
            - Values are plain data; the idle count and the count are read a moment apart under concurrent traffic.

        Raises:
            RuntimeError: If the pool has been cleaned.

        Returns:
            Dict[str, Any]: The snapshot.
        """
        self.check_cleaned()
        snapshot = super().describe()
        del snapshot["in_use_count"]
        with self._lock:
            count = self._count
            children_recorded = sum(len(children) for children in self._children_by_object.values())
            children_recorded += sum(len(children) for children in self._orphaned_children)
        snapshot.update(
            {
                "spell_id": self._spell_id,
                "spell_name": self._spell_name,
                "binding_name": self._binding_name,
                "frame_name": self._frame_name,
                "owner_conduit_id": self._owner_conduit_id,
                "mode": self._mode.name,
                "limit": self._limit,
                "timeout_seconds": self._timeout_seconds,
                "reset_method_names": list(self._reset_method_names),
                "disposal_method_names": list(self._disposal_method_names),
                "count": count,
                "out_count": max(0, count - snapshot["idle_count"]),
                "children_recorded": children_recorded,
            }
        )
        return snapshot

    def _rebind_spell(self, spell: Spell) -> None:
        """
        Point the pool at the current Spell object of its spell_id and take that Spell's settings.

        Purpose:
            A definition removed and bound again under the same content-stable id meets its old pool (as a slotted
            replacement meets its old slot, 0.2.8219). Its managed settings are not part of the spell_id (owner
            ruling 2026-10-17: the bind call's settings must not change the SHA256), so the rebind may carry another
            mode, limit, queue timeout or reset names; the pool then describes, resolves releases against and leases
            under the live Spell and its settings rather than the cleaned one's.

        Contract:
            - Called only by `Creations.ensure_managed_quantity`, after it released the store lock, for a Spell
              with this pool's spell_id - hence the same class profile, address, existence and disposal names.
            - Always re-points `_spell`, `_managed_class` and `_disposal_method_names` (the new Spell's list, equal
              in content). The class key is re-captured because a redefined class is a new class object under the
              same content-stable id; the store re-registers the pool under it.
            - Equal settings: nothing else changes - the elastic target, the decay clock and the count stay as they
              were (an ownership transfer's restamp of the same Spell is such a rebind).
            - Other settings: the mode, limit, timeout, reset names and `_notify_on_return` take the Spell's values,
              and the retention sizes follow them exactly as `__init__` sizes them (elastic: baseline
              min(20, limit), ceiling limit; limited_quantity and queue: baseline = ceiling = limit); the target
              restarts at the new baseline and the decay step is recomputed from it. Every queue waiter is woken to
              re-check under the new policy.
            - Destroys nothing: objects alive stay alive and counted, idle ones included. A count above a smaller
              new limit stays until destroys bring it down - limited_quantity and queue build again only below the
              limit, and their fixed capacity evicts the oldest idle object on each release above it; elastic
              trims through its band.
            - A pool torn down meanwhile (its store cleaned after `ensure_managed_quantity` checked it) is left as
              it is.

        Args:
            spell: The current Spell of this spell_id.

        Threading:
            Reads the Spell's settings before taking `_lock` (the caller holds the Spell's lock, as owner stamping
            does), then writes under `_condition`, the pool's leaf lock; no user code runs under it and no store
            lock is held. A lease or a release racing the rebind sees the old or the new policy for that one call:
            `reserve()` reads the mode once before its lock and checks the limit in force under it, `put_back`
            reads the reset names once, and a plan's lock-free idle pop serves an object built for this spell_id
            under either policy.

        Returns:
            None.
        """
        mode = spell.managed_spell_mode
        limit = spell.managed_spell_limit
        timeout_seconds = spell.managed_spell_timeout_seconds
        reset_method_names = spell.managed_spell_reset_methods
        condition = self._condition
        with condition:
            if self._cleaned:
                return
            self._spell = spell
            self._managed_class = spell.spell
            self._disposal_method_names = spell.disposal_method_names
            if (
                    mode is self._mode
                    and limit == self._limit
                    and timeout_seconds == self._timeout_seconds
                    and reset_method_names == self._reset_method_names
            ):
                return
            baseline_idle = min(self._ELASTIC_BASELINE_IDLE, limit) if mode is ManagedSpellMode.elastic else limit
            self._mode = mode
            self._limit = limit
            self._timeout_seconds = timeout_seconds
            self._reset_method_names = reset_method_names
            # Only queue leases wait, so only a queue release has a waiter to wake.
            self._notify_on_return = mode is ManagedSpellMode.queue
            self._baseline_idle = baseline_idle
            self._max_idle = limit
            self._target_idle = baseline_idle
            self._decay_step = max(1, (max(baseline_idle, 1) * self._decay_percent_per_interval) // 100)
            condition.notify_all()

    def _torn_down_error(self, consequence: str) -> RuntimeError:
        """
        Build the error every verb raises on a pool torn down with its root.

        Args:
            consequence: What it means for the caller, ending the message.

        Returns:
            RuntimeError: "The pool of managed spell '<name>' was torn down with its root conduit; <consequence>"
        """
        return RuntimeError(
            f"The pool of managed spell '{self._spell_name}' was torn down with its root conduit; {consequence}"
        )

    def _dispose_children(self, children: List[Tuple[object, List[str]]]) -> List[Exception]:
        """
        Dispose recorded children newest first and collect the failures.

        Args:
            children: `(child, child_methods)` pairs in build order.

        Returns:
            List[Exception]: One chained `RuntimeError` per failing method, in attempt order.
        """
        failures: List[Exception] = []
        for child, methods in reversed(children):
            failures.extend(self._run_disposal_methods(child, methods))
        return failures

    @classmethod
    def _run_disposal_methods(cls, item: object, method_names: List[str]) -> List[Exception]:
        """
        Run every declared disposal method of one object and collect each failure.

        Contract:
            The contract of `Creations._attempt_cleanup`, kept local so this module never imports the store that
            imports it: every method runs once, in declared order, even after one fails; each method that raises
            `Exception` (a missing name included, as `AttributeError`) yields one `RuntimeError` naming the object
            and the method, whose `__cause__` is what the method raised; the text never trusts `__str__`. A
            `BaseException` that is not an `Exception` propagates.

        Args:
            item: The object to dispose.
            method_names: Its ordered disposal method names (borrowed, not mutated).

        Returns:
            List[Exception]: One wrapped error per failing method; empty when all succeeded.
        """
        errors: List[Exception] = []
        for method_name in method_names:
            try:
                item.__getattribute__(method_name)()
            except Exception as ex:
                error = RuntimeError(
                    f"Failed to dispose object {cls._describe_for_disposal_error(item)} "
                    f"using method '{method_name}': {cls._describe_for_disposal_error(ex)}"
                )
                error.__cause__ = ex
                errors.append(error)
        return errors

    @staticmethod
    def _describe_for_disposal_error(value: object) -> str:
        """
        Return text for a disposal error without trusting `value.__str__`.

        Contract:
            `str(value)` when that succeeds, else `<Type object at 0x...; str() raised ErrorType>` (the contract of
            `Creations._describe_for_disposal_error`).

        Args:
            value: The object being disposed, or the exception one of its methods raised.

        Returns:
            str: Text safe to embed in a disposal error message.
        """
        try:
            return str(value)
        except Exception as ex:
            return f"<{type(value).__qualname__} object at {id(value):#x}; str() raised {type(ex).__name__}>"
