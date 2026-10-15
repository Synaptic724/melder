"""
Spike: a managed shell in the owner store, the three modes, and the one way back (2026-10-14, fable_0).

Shape under test (owner, chat 2026-10-14): the managed object is "managed in creations as a special interface" -
a shell stored under the spell id that hands an idle object out in the mode's way and takes it back;
`ReleaseManagedSpell` is the one way back and hosts a `with`; the root owns the shell; a reset list at bind.
Scratch code: no Melder import, no tree change; the kernel seams it stands in for are named in the task's FACT note.
"""
import threading
import weakref
from collections import deque
from enum import Enum
from typing import Any, Callable, Deque, Dict, Iterator, List, Optional, Tuple
import contextlib


LOCKFREE_WARM = False   # Variant B switch for the spike's measurement (see ManagedShell.acquire)


class ManagedMode(Enum):
    limited_quantity = "limited_quantity"
    elastic = "elastic"
    queue = "queue"


class ManagedQuantity:
    """The bind-time choice: mode plus its numbers (value object; frozen at bind in the real design)."""

    __slots__ = ("mode", "limit", "baseline_idle", "max_idle", "timeout_seconds")

    def __init__(self, mode: ManagedMode, limit: int, baseline_idle: int, max_idle: int,
                 timeout_seconds: float) -> None:
        self.mode = mode
        self.limit = limit
        self.baseline_idle = baseline_idle
        self.max_idle = max_idle
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def limited_quantity(limit: int) -> "ManagedQuantity":
        if limit < 1:
            raise ValueError("limited_quantity needs a limit of at least 1.")
        return ManagedQuantity(ManagedMode.limited_quantity, limit, limit, limit, 0.0)

    @staticmethod
    def elastic(baseline_idle: int = 20, max_idle: int = 256) -> "ManagedQuantity":
        if baseline_idle < 0 or max_idle < baseline_idle:
            raise ValueError("elastic needs 0 <= baseline_idle <= max_idle.")
        return ManagedQuantity(ManagedMode.elastic, 0, baseline_idle, max_idle, 0.0)

    @staticmethod
    def queue(limit: int, timeout_seconds: float) -> "ManagedQuantity":
        if limit < 1 or timeout_seconds <= 0.0:
            raise ValueError("queue needs a limit of at least 1 and a positive timeout.")
        return ManagedQuantity(ManagedMode.queue, limit, limit, limit, timeout_seconds)


class ManagedQuantityExhausted(RuntimeError):
    """A limited or queued pool has every place taken (queued: for the whole timeout)."""


class ManagedReleaseError(RuntimeError):
    """A release of an object that is not out from any managed shell (double release, foreign object)."""


class ManagedEntry:
    """
    One object's record in its shell: strong while idle, weak while out, plus the `many` children built for it.

    `item` is the strong reference while the object sits idle; while it is out, `ref` is the weak reference
    and `item` is None, so a lease nobody returns dies normally and the weakref callback frees its place.
    `children` are `(child, methods)` pairs disposed when the object is destroyed, never on release.
    """

    __slots__ = ("item", "ref", "children", "shell", "__weakref__")

    def __init__(self, shell: "ManagedShell") -> None:
        self.item: Optional[object] = None
        self.ref: Optional[weakref.ref] = None     # created ONCE per object, reused across leases
        self.children: List[Tuple[object, List[str]]] = []
        self.shell = shell

    def on_dead(self, _ref: weakref.ref) -> None:
        """Weakref callback: the leased object died unreturned; bookkeeping only (see ManagedShell._note_dead)."""
        self.shell._note_dead(self)


class ManagedShell:
    """
    The shell stored under a managed spell's id in its root's owner store.

    Threading: `_lock` is a leaf (a Condition over a Lock for the queue mode). Reset and disposal run outside it.
    The weakref callback does bookkeeping only (count, dead list); disposal of a dead lease's children is
    deferred to the next shell verb, outside the lock, never inside the interpreter's deallocation path.
    """

    def __init__(self, spell_id: str, quantity: ManagedQuantity, reset_method_names: List[str],
                 disposal_method_names: List[str]) -> None:
        self.spell_id = spell_id
        self.quantity = quantity
        self.reset_method_names = reset_method_names
        self.disposal_method_names = disposal_method_names
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._idle: Deque[ManagedEntry] = deque()
        self._out: Dict[int, ManagedEntry] = {}
        self._dead: List[ManagedEntry] = []
        self._count = 0
        self._destroyed = False
        self._queued = quantity.mode is ManagedMode.queue
        self._elastic = quantity.mode is ManagedMode.elastic
        self._lockfree_warm = LOCKFREE_WARM

    # ---- dispense ----
    def acquire(self) -> Optional[object]:
        """Hand out an idle object, moving its entry to the out-record; None when nothing is idle."""
        if self._dead:
            self._drain_dead()
        if self._lockfree_warm:
            # Variant B (free-threaded 3.14t): deque.pop and a single dict store are atomic per object, so the
            # warm hand-out needs no shell lock; the count is only touched on cold paths (reserve/cancel/dead).
            try:
                entry = self._idle.pop()
            except IndexError:
                return None
            item = entry.item
            entry.item = None
            self._out[id(item)] = entry
            return item
        lock = self._lock
        lock.acquire()
        try:
            if not self._idle:
                return None
            entry = self._idle.pop()
            item = entry.item
            entry.item = None            # the entry's weakref keeps watching; only the strong ref drops
            self._out[id(item)] = entry
        finally:
            lock.release()
        return item

    def reserve(self) -> ManagedEntry:
        """Take a place for an object about to be built (limited raises, queue waits), before any build."""
        with self._lock:
            mode = self.quantity.mode
            if mode is ManagedMode.limited_quantity:
                if self._count >= self.quantity.limit:
                    raise ManagedQuantityExhausted(
                        f"managed spell '{self.spell_id}': every one of its {self.quantity.limit} places is taken."
                    )
            elif mode is ManagedMode.queue:
                if not self._cond.wait_for(lambda: self._count < self.quantity.limit or self._idle,
                                           timeout=self.quantity.timeout_seconds):
                    raise ManagedQuantityExhausted(
                        f"managed spell '{self.spell_id}': no place freed within {self.quantity.timeout_seconds}s."
                    )
                if self._idle:
                    # A release arrived while we waited: hand that object out instead of building.
                    entry = self._idle.pop()
                    item = entry.item
                    entry.item = None
                    self._out[id(item)] = entry
                    raise _ServedFromIdle(item)
            self._count += 1
            return ManagedEntry(self)

    def cancel(self, entry: ManagedEntry) -> None:
        """A build that reserved failed: free the place (its children, if any, are disposed by the caller)."""
        with self._lock:
            self._count -= 1
            if self._queued:
                self._cond.notify()

    def publish_out(self, entry: ManagedEntry, item: object, children: List[Tuple[object, List[str]]]) -> None:
        """Record a just-built object as out, with the `many` children built for it (the one weakref per object)."""
        entry.children = children
        entry.ref = weakref.ref(item, entry.on_dead)
        with self._lock:
            self._out[id(item)] = entry

    # ---- the way back ----
    def put_back(self, item: object, entry: ManagedEntry) -> None:
        """Reset outside the lock, then idle (or destroy on a failing reset); trims the elastic surplus."""
        lock = self._lock
        if self._lockfree_warm:
            if self._out.pop(id(item), None) is not entry:
                raise ManagedReleaseError(f"managed spell '{self.spell_id}': the object is not out from this shell.")
        else:
            lock.acquire()
            try:
                if self._out.pop(id(item), None) is not entry:
                    raise ManagedReleaseError(f"managed spell '{self.spell_id}': the object is not out from this shell.")
            finally:
                lock.release()
        try:
            for name in self.reset_method_names:
                item.__getattribute__(name)()
        except Exception:
            self._destroy_entry(entry, item)
            with self._lock:
                self._count -= 1
                if self._queued:
                    self._cond.notify()
            raise
        surplus: Optional[Tuple[ManagedEntry, object]] = None
        if self._lockfree_warm and not self._destroyed and not self._queued and not (
                self._elastic and len(self._idle) >= self.quantity.max_idle):
            entry.item = item
            self._idle.append(entry)
            if self._dead:
                self._drain_dead()
            return
        lock.acquire()
        try:
            if self._destroyed:
                surplus = (entry, item)
                self._count -= 1
            elif self._elastic and len(self._idle) >= self.quantity.max_idle:
                # Elastic: keep at most max_idle idle objects (the real design reuses the 0.2.8234 decay).
                surplus = (entry, item)
                self._count -= 1
            else:
                entry.item = item
                self._idle.append(entry)
            if self._queued:
                self._cond.notify()
        finally:
            lock.release()
        if surplus is not None:
            self._destroy_entry(*surplus)
        if self._dead:
            self._drain_dead()

    # ---- destroy paths ----
    def evict_idle(self) -> List[Exception]:
        """Purge with no instance: destroy idle objects now; out objects die at their release."""
        with self._lock:
            idle = list(self._idle)
            self._idle.clear()
            self._count -= len(idle)
            self._cond.notify_all()
        errors: List[Exception] = []
        for entry in idle:
            errors.extend(self._destroy_entry(entry, entry.item))
        return errors

    def destroy_all(self) -> List[Exception]:
        """Root teardown: dispose idle and still-alive out objects (no reset) and forget the index entries."""
        with self._lock:
            self._destroyed = True
            idle = list(self._idle)
            self._idle.clear()
            out = list(self._out.values())
            self._out.clear()
            dead = list(self._dead)
            self._dead.clear()
            self._count = 0
            self._cond.notify_all()
        errors: List[Exception] = []
        for entry in idle:
            errors.extend(self._destroy_entry(entry, entry.item))
        for entry in out:
            item = entry.ref() if entry.ref is not None else None
            errors.extend(self._destroy_entry(entry, item))
        for entry in dead:
            errors.extend(self._destroy_entry(entry, None))
        return errors

    # ---- internals ----
    def _note_dead(self, entry: ManagedEntry) -> None:
        """Weakref callback target: the object is gone, its place is free; its children wait for the next verb."""
        with self._lock:
            for key, candidate in list(self._out.items()):
                if candidate is entry:
                    del self._out[key]
                    break
            else:
                return
            self._count -= 1
            self._dead.append(entry)
            if self._queued:
                self._cond.notify()

    def _drain_dead(self) -> None:
        with self._lock:
            if not self._dead:
                return
            dead = list(self._dead)
            self._dead.clear()
        for entry in dead:
            self._destroy_entry(entry, None)

    def _destroy_entry(self, entry: ManagedEntry, item: Optional[object]) -> List[Exception]:
        """Dispose the object (when still alive) and then its children, newest first; collect failures."""
        errors: List[Exception] = []
        targets: List[Tuple[object, List[str]]] = []
        if item is not None:
            targets.append((item, self.disposal_method_names))
        targets.extend(reversed(entry.children))
        for target, methods in targets:
            for name in methods:
                try:
                    target.__getattribute__(name)()
                except Exception as exc:
                    errors.append(RuntimeError(f"disposal '{name}' failed on {type(target).__name__}: {exc!r}"))
        entry.children = []
        entry.item = None
        entry.ref = None
        return errors

    def describe(self) -> Dict[str, Any]:
        with self._lock:
            return {"mode": self.quantity.mode.value, "count": self._count, "idle": len(self._idle),
                    "out": len(self._out), "dead_pending": len(self._dead)}


class _ServedFromIdle(Exception):
    """Internal: a queued reserve was satisfied by a release that arrived while it waited."""

    def __init__(self, item: object) -> None:
        super().__init__()
        self.item = item


class ReleaseManagedSpell:
    """
    The one way back. Index: type(object) -> the shells managing that class (one per root per binding), written
    once when a shell is created (copy-on-write under a leaf lock) and read lock-free on every release. A release
    finds its shell by asking each shell of the class whether the object is out from it (one dict get each; one
    shell is the common case). Hosts the `with` and the dispense-or-build the emitted managed door runs.
    """

    _lock = threading.Lock()
    _shells_by_type: Dict[type, Tuple[ManagedShell, ...]] = {}

    @classmethod
    def register(cls, managed_type: type, shell: ManagedShell) -> None:
        with cls._lock:
            cls._shells_by_type[managed_type] = cls._shells_by_type.get(managed_type, ()) + (shell,)

    @classmethod
    def unregister(cls, managed_type: type, shell: ManagedShell) -> None:
        with cls._lock:
            kept = tuple(s for s in cls._shells_by_type.get(managed_type, ()) if s is not shell)
            if kept:
                cls._shells_by_type[managed_type] = kept
            else:
                cls._shells_by_type.pop(managed_type, None)

    @classmethod
    def release(cls, item: object) -> None:
        shells = cls._shells_by_type.get(type(item))
        if shells is not None:
            key = id(item)
            for shell in shells:
                entry = shell._out.get(key)
                if entry is not None and entry.ref is not None and entry.ref() is item:
                    shell.put_back(item, entry)
                    return
        raise ManagedReleaseError("the object is not out from any managed spell (double release or foreign).")

    @classmethod
    @contextlib.contextmanager
    def managed(cls, item: object) -> Iterator[object]:
        try:
            yield item
        finally:
            cls.release(item)

    @staticmethod
    def dispense(shell: ManagedShell, build: Callable[[], Tuple[object, List[Tuple[object, List[str]]]]]) -> object:
        """What the emitted managed door does: acquire, else reserve -> build -> publish_out (cancel on failure)."""
        item = shell.acquire()
        if item is not None:
            return item
        try:
            entry = shell.reserve()
        except _ServedFromIdle as served:
            return served.item
        try:
            item, children = build()
        except BaseException:
            shell.cancel(entry)
            raise
        shell.publish_out(entry, item, children)
        return item

    @classmethod
    def reset_for_tests(cls) -> None:
        with cls._lock:
            cls._shells_by_type.clear()
