"""Version-agnostic meld-only lock-order probe. Author: melder_0, 2026-09-25.

Runs against whichever melder is on sys.path. Thread A melds PReq (unique_per_conduit or lineage), holds the
store, and is paused exactly when it requests USvc's Spell lock. Thread C melds USvc (unique). If C then
requests that same store, the request is refused (recorded as would_block) instead of waited on, so a real
cycle is recorded without hanging. Entries are reset by removing them from the store dict (no purge needed).
"""
import json
import sys
from threading import Event, RLock, Thread, current_thread
from typing import Optional

import melder
from melder import Aether, Conduit, Existence, Spellbook


class ProbeWouldBlock(RuntimeError):
    """Raised instead of waiting on the lock that would complete the cycle."""


class Trace:
    """Synchronized event list."""

    def __init__(self) -> None:
        """Start empty."""
        self.rows: list[tuple[str, str, str]] = []
        self.lock = RLock()

    def add(self, label: str, event: str) -> None:
        """Record one event for the current thread."""
        with self.lock:
            self.rows.append((current_thread().name, label, event))


class ObservedLock:
    """Delegate to a real RLock; optionally pause one thread or refuse a contended acquire for another."""

    def __init__(self, raw: object, trace: Trace, label: str) -> None:
        """Wrap the real lock."""
        self.raw, self.trace, self.label = raw, trace, label
        self.paused, self.resume = Event(), Event()
        self.pause_thread: Optional[str] = None
        self.refuse_thread: Optional[str] = None

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Acquire with the probe's scheduling controls."""
        name = current_thread().name
        self.trace.add(self.label, "request")
        if name == self.pause_thread:
            self.paused.set()
            if not self.resume.wait(8):
                raise TimeoutError("coordinator did not resume")
        if name == self.refuse_thread:
            if not self.raw.acquire(False):
                self.trace.add(self.label, "would_block")
                raise ProbeWouldBlock(self.label)
            result = True
        else:
            result = self.raw.acquire(blocking, timeout)
        if result:
            self.trace.add(self.label, "acquired")
        return result

    def release(self) -> None:
        """Release the real lock."""
        self.raw.release()
        self.trace.add(self.label, "released")

    def __enter__(self) -> "ObservedLock":
        """Context-manager acquire."""
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        """Context-manager release."""
        self.release()


class MLeaf:
    """Transient dependency."""

    def __init__(self) -> None:
        """No deps."""

    def close(self) -> None:
        """Optional disposal method."""


class USvc:
    """Frame-wide singleton."""

    def __init__(self, leaf: MLeaf) -> None:
        """Hold a leaf."""
        self.leaf = leaf


class PReq:
    """Per-conduit or lineage consumer of USvc."""

    def __init__(self, svc: USvc) -> None:
        """Hold the service."""
        self.svc = svc


def spells_of(book: Spellbook) -> list:
    """Return live Spell objects across versions."""
    pool = getattr(book, "_spell_id_pool", None)
    return list(pool.values()) if pool is not None else list(book._spells.values())


def run_case(parent: Existence, disposal: bool) -> dict[str, object]:
    """One interleaving; report whether the store/Spell cycle forms."""
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    book = Spellbook(aetheric_frame=f"probe-{parent.name}-{disposal}")
    book.bind(spell=MLeaf, existence=Existence.many, disposal_method_names=["close"] if disposal else None)
    book.bind(spell=USvc, existence=Existence.unique)
    book.bind(spell=PReq, existence=parent)
    conduit = book.conjure(name="probe")
    trace = Trace()
    try:
        conduit.meld(spell=PReq)  # warm compiled contexts and validation
        store = (conduit._meld._root_creations if parent is Existence.unique_per_conduit_lineage
                 else conduit._meld._conduit_creations)
        svc = next(s for s in spells_of(book) if s.spell is USvc)
        req = next(s for s in spells_of(book) if s.spell is PReq)
        for sp in (req, svc):  # return both to the never-built state
            store._creations.pop(sp.spell_id, None)
            store._disposable_creations.pop(sp.spell_id, None)
        same_store = svc._owner_creations is store
        raw_store_lock, raw_svc_lock = store._lock, svc._lock
        store_lock = ObservedLock(raw_store_lock, trace, "store")
        svc_lock = ObservedLock(raw_svc_lock, trace, "svc_spell")
        svc_lock.pause_thread, store_lock.refuse_thread = "meld-A", "meld-C"
        out: dict[str, list[str]] = {"A": [], "C": []}

        def run(tag: str, target: type) -> None:
            """Call public meld; capture the outcome."""
            try:
                out[tag].append(type(conduit.meld(spell=target)).__name__)
            except BaseException as error:  # diagnostic capture
                out[tag].append(f"{type(error).__name__}: {error}")

        store._lock, svc._lock = store_lock, svc_lock
        try:
            a = Thread(target=run, args=("A", PReq), name="meld-A", daemon=True)
            a.start()
            a_paused = svc_lock.paused.wait(6)
            c = Thread(target=run, args=("C", USvc), name="meld-C", daemon=True)
            c.start()
            c.join(5)
            c_stuck_elsewhere = c.is_alive()
        finally:
            svc_lock.resume.set()
            a.join(10)
            c.join(10)
            store._lock, svc._lock = raw_store_lock, raw_svc_lock
        rows = trace.rows
        cycle = (a_paused and ("meld-A", "store", "acquired") in rows
                 and ("meld-C", "svc_spell", "acquired") in rows
                 and ("meld-C", "store", "would_block") in rows)
        return {"parent": parent.name, "leaf_disposal": disposal, "same_store": same_store,
                "cycle_formed": cycle, "C_stuck_elsewhere": c_stuck_elsewhere,
                "A_outcome": out["A"], "C_outcome": out["C"], "trace": rows}
    finally:
        conduit.cleanup()
        book.cleanup()


def main() -> None:
    """Run four cases and print a summary."""
    cases = [run_case(p, d) for p in (Existence.unique_per_conduit, Existence.unique_per_conduit_lineage)
             for d in (True, False)]
    report = {"melder_version": melder.__version__, "melder_path": melder.__file__, "python": sys.version,
              "gil_enabled": sys._is_gil_enabled(), "cases": cases}
    out = f"meld_only_standalone_{melder.__version__}_{'gil' if sys._is_gil_enabled() else 'nogil'}.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("melder", melder.__version__, "| python", sys.version.split()[0], "| gil", sys._is_gil_enabled())
    for case in cases:
        print("  ", {k: v for k, v in case.items() if k != "trace"})


if __name__ == "__main__":
    main()
