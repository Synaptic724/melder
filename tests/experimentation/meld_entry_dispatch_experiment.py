"""
Meld entry dispatch experiment: is a one-lookup entry faster than today's `conduit.meld`?

WHY THIS EXISTS
    The PGO composition experiment found that most of what a user pays per warm creation is
    dispatch, not construction: `conduit.meld("Service")` and `conduit.meld(spell=Service)`
    spend two method frames, two `isinstance` checks, one lookup that turns the name or class
    into a spell id, a second lookup that finds the compiled entry, and a forwarding closure
    before the compiled builder runs - about 330 ns around a ~110 ns object on the VM.

    The proposal: key the fast table by the name and the class as well as by the spell id,
    all pointing at the same entry, and let `meld` go entry -> guards -> builder in one step.
    Users keep calling exactly what they call today. This file measures that proposal with a
    faithful prototype over the REAL runtime objects (the real fast-door entries, the real
    compiled builders, the real epoch and context guards), so the number is the dispatch
    saving and nothing else.

ARMS (per shape; every arm returns the same object type and is shape-checked first)
    today_by_name      `conduit.meld("<registered name>")` - what users call
    today_by_class     `conduit.meld(spell=Cls)` - what users call
    today_by_id        `conduit.meld(spell_id=...)` - the machine path (reference)
    proposed_by_name   one lookup on the name in a table that holds the real entry, the two
                       (since 2026-09-27 `today_by_name` IS this lane: `Conduit.meld` reads the
                       door's `_fast_input_doors`; the prototype arms remain the reference)
                       structural guards (`_door_epoch`, `_creation_context` identity), then
                       the same callable `Conduit.meld` calls today (the lane)
    proposed_by_class  the same table keyed by the class
    proposed_inner     as proposed_by_name, but the entry holds the compiled builder itself
                       instead of the forwarding lane (one frame less; `many` roots only)

    The prototype keeps an `override` check and a precomputed `fast_ok` flag that stands for
    the checks `Conduit.meld` makes on state that only changes at configuration time
    (cleaned, dynamic environment, hooks, validation-required); a guard miss or a miss in the
    table falls back to the real `conduit.meld`, and the file proves that fallback fires by
    bumping the epoch once.

ENV KNOBS
    MELD_ENTRY_ITERS (default 200000), MELD_ENTRY_REPEATS (5), MELD_ENTRY_WARMUP (20000)

RUN (on the 3.14t target; caching is off so nothing is written)
    python -X gil=0 tests/experimentation/meld_entry_dispatch_experiment.py
"""

import os
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pgo_codegen_composition_experiment import CompositionBuilder, MelderWorld, Node  # noqa: E402


class EntrySettings:
    """Environment-driven loop sizes."""

    __slots__ = ("iters", "repeats", "warmup")

    def __init__(self) -> None:
        self.iters: int = int(os.environ.get("MELD_ENTRY_ITERS", "200000"))
        self.repeats: int = int(os.environ.get("MELD_ENTRY_REPEATS", "5"))
        self.warmup: int = int(os.environ.get("MELD_ENTRY_WARMUP", "20000"))


class ProposedEntry:
    """
    Prototype of the proposed `Conduit.meld` fast path over the real runtime objects.

    Contract:
        - `table` maps every key a user may pass (registered name, class, spell id) to the
          real fast-door entry `(door_spell, captured_context, captured_epoch, callable)`.
        - `meld(key)` does: override check, `fast_ok` flag, one `dict.get`, the two structural
          guards, call. Anything else falls back to the real `conduit.meld`, which is what the
          production slow path would be.
        - `fast_ok` stands for the configuration-time checks folded into one flag.
    """

    __slots__ = ("_table", "_meld_component", "_fast_ok", "_slow")

    def __init__(self, table: Dict[Any, Tuple[Any, Any, int, Callable[..., Any]]], meld_component: Any,
                 slow: Callable[..., Any]) -> None:
        self._table = table
        self._meld_component = meld_component
        self._fast_ok: bool = True
        self._slow = slow

    def meld(self, key: Any, override: Optional[Any] = None) -> Any:
        """The proposed entry: one lookup, two guards, one call."""
        if override is not None or not self._fast_ok:
            return self._slow(key, override)
        entry = self._table.get(key)
        if entry is None:
            return self._slow(key, override)
        door_spell, captured_context, captured_epoch, target = entry
        if door_spell._door_epoch != captured_epoch or door_spell._creation_context is not captured_context:
            return self._slow(key, override)
        return target(self._meld_component)


def _slow_path(conduit: Any) -> Callable[..., Any]:
    """The fallback: today's `conduit.meld`, called the way the key was given."""

    def slow(key: Any, override: Optional[Any]) -> Any:
        if isinstance(key, str) and len(key) == 64:
            return conduit.meld(spell_id=key, override=override)
        if isinstance(key, str):
            return conduit.meld(key, override=override)
        return conduit.meld(spell=key, override=override)

    return slow


def _time(fn: Callable[[], Any], settings: EntrySettings) -> float:
    """Median ns per call."""
    for _ in range(settings.warmup):
        fn()
    samples: List[float] = []
    counter = time.perf_counter_ns
    for _ in range(settings.repeats):
        start = counter()
        for _ in range(settings.iters):
            fn()
        samples.append((counter() - start) / settings.iters)
    return statistics.median(samples)


def _calls(fn: Callable[[], Any]) -> Tuple[int, int]:
    """(python_calls, c_calls) of one call of `fn`, excluding `fn` itself."""
    counts = {"call": 0, "c_call": 0}

    def profiler(frame: Any, event: str, arg: Any) -> None:
        if event in counts:
            counts[event] += 1

    sys.setprofile(profiler)
    try:
        fn()
    finally:
        sys.setprofile(None)
    return counts["call"] - 1, counts["c_call"] - 1  # minus fn itself and minus setprofile(None)


def run_shape(name: str, root: Node, settings: EntrySettings) -> Dict[str, Any]:
    """Measure every arm for one shape and return the rows."""
    CompositionBuilder.materialize(root, f"entry_{name}")
    world = MelderWorld(root, f"entry-{name}")
    try:
        world.singleton_instances()
        conduit, cls, sid = world.conduit, root.cls, world.root_id
        registered_name = cls.__name__
        for _ in range(50):
            conduit.meld(registered_name)
        meld_component = conduit._meld
        # Finding worth keeping: does a meld by name mint a fast entry? Before 2026-09-27 only a
        # meld by id minted (`_fast_meld_doors`, keyed by id); since then a meld by name or class
        # mints `_fast_input_doors`, keyed by the name or class the caller passed.
        minted_by_name = (
            sid in meld_component._fast_meld_doors
            or registered_name in getattr(meld_component, "_fast_input_doors", {})
        )
        if not minted_by_name:
            conduit.meld(spell_id=sid)
        entry = meld_component._fast_meld_doors[sid]
        door_spell, captured_context, captured_epoch, _existing = entry
        lane = captured_context._no_overrides_instance_executor
        table: Dict[Any, Tuple[Any, Any, int, Callable[..., Any]]] = {}
        for key in (registered_name, cls, sid):
            table[key] = (door_spell, captured_context, captured_epoch, lane)
        proposed = ProposedEntry(table, meld_component, _slow_path(conduit))
        arms: Dict[str, Callable[[], Any]] = {
            "today_by_name": lambda: conduit.meld(registered_name),
            "today_by_class": lambda: conduit.meld(spell=cls),
            "today_by_id": lambda: conduit.meld(spell_id=sid),
            "proposed_by_name": lambda: proposed.meld(registered_name),
            "proposed_by_class": lambda: proposed.meld(cls),
        }
        if not root.singleton and "_no_overrides_executor" in lane.__code__.co_freevars:
            inner = lane.__closure__[lane.__code__.co_freevars.index("_no_overrides_executor")].cell_contents
            inner_table = {k: (door_spell, captured_context, captured_epoch, inner) for k in table}
            proposed_inner = ProposedEntry(inner_table, meld_component, _slow_path(conduit))
            arms["proposed_inner"] = lambda: proposed_inner.meld(registered_name)
        for label, fn in arms.items():
            assert type(fn()) is cls, label
        # Prove the guard falls back: a bumped epoch must route to the real meld and still work.
        saved = door_spell._door_epoch
        door_spell._door_epoch = saved + 1
        try:
            assert type(proposed.meld(registered_name)) is cls
        finally:
            door_spell._door_epoch = saved
        rows: Dict[str, Dict[str, float]] = {}
        for label, fn in arms.items():
            ns = _time(fn, settings)
            py_calls, c_calls = _calls(fn)
            rows[label] = {"ns": ns, "py": py_calls, "c": c_calls}
        return {"name": name, "rows": rows, "minted_by_name": minted_by_name}
    finally:
        world.cleanup()


def main() -> int:
    """Run the shapes and print the Markdown report."""
    import melder

    settings = EntrySettings()
    shapes = CompositionBuilder.compositions()
    selected = ["solo", "w1_singleton", "w2_mixed", "w4_mixed", "wide8_singleton"]
    shapes["singleton_direct"] = Node("Root", True, [])  # a stored unique melded directly
    selected.append("singleton_direct")
    results = [run_shape(n, shapes[n], settings) for n in selected]
    gil = "disabled" if not sys._is_gil_enabled() else "enabled"
    print("# Meld entry dispatch experiment\n")
    print(f"melder {melder.__version__}; Python {sys.version.split()[0]}; GIL {gil}; "
          f"iters={settings.iters} repeats={settings.repeats} warmup={settings.warmup}\n")
    print("| shape | arm | ns/call | py calls | C calls | vs today_by_name |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for result in results:
        base = result["rows"]["today_by_name"]["ns"]
        print(f"| {result['name']} | fast entry minted by 50 melds by name: {'yes' if result['minted_by_name'] else 'NO - minted by one meld by id'} | | | | |")
        for label, row in result["rows"].items():
            delta = "" if label == "today_by_name" else f"{100 * (row['ns'] - base) / base:+.0f}%"
            print(f"| {result['name']} | {label} | {row['ns']:.0f} | {row['py']} | {row['c']} | {delta} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
