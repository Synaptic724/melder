"""
PGO codegen composition experiment: is the juice worth the squeeze?

WHY THIS EXISTS
    Melder compiles one executor per spell from static knowledge (existence, sockets,
    defaults) and never from what actually happens at run time. Profile-guided
    optimization (PGO) of that codegen would let a warm executor close over the
    singletons it always finds stored, construct its transient children inline and
    positionally, and skip every store lookup and site call the profile says it does
    not need - guarded by one int compare per speculation so a wrong guess deopts to
    the generalized path instead of returning a stale object.

    Before designing any of that, the owner asked one question: for a range of object
    compositions, how many calls and how many nanoseconds per creation could an ideal
    PGO body remove, and is that worth building? This file answers it with numbers.

WHAT IT MEASURES (per composition; the root is always `Existence.many`, so every meld
constructs a fresh root; dependencies are `unique` singletons or `many` transients as
the composition says)
    real_meld     `conduit.meld(spell_id=root_id)`, warm. What a user pays today per
                  creation, door included. The generalized executor is whatever the
                  current codegen emitted for this graph.
    pgo_guarded   Hand-written ideal PGO body: every stored singleton is a closed-over
                  constant guarded by one `epoch` int compare; every transient site is
                  constructed inline with positional arguments; one root door guard.
                  This is what an optimistic-PGO regeneration could emit.
    pgo_store     Same body, but singletons are read with one `dict.get` from a store
                  dict instead of being closed over (a live-PGO body that keeps the
                  store as the source of truth and needs no epoch guard for them).
    pgo_floor     The guarded body without any guard: the theoretical floor.
    noop          An empty function, the timing loop's own floor.

    Metrics per arm: ns per creation (median of REPEATS timed runs of ITERS calls after
    WARMUP calls), Python-level calls and C-level calls per creation (`sys.setprofile`
    over a separate sample of SAMPLE creations), objects constructed per creation
    (class counters). The deltas `real_meld - pgo_*` are the most a PGO body can win on
    that composition; the guard cost is `pgo_guarded - pgo_floor`.

COMPOSITIONS (S = unique singleton, T = many transient)
    solo               Root()                                          - door floor
    wide8_transient    Root(T0..T7)
    wide8_singleton    Root(S0..S7)
    wide16_transient   Root(T0..T15)
    chain8_transient   Root(T1(T2(...T8)))
    chain8_singleton   Root(S1) where S1(S2(...S8)) are all singletons
    diamond            Root(B, C), B(D), C(D); B and C transient, D singleton
    mixed3s4t          Root(S0, S1, S2, T0, T1, T2, T3)
    chain6_alternating Root(T1(S2(T3(S4(T5(S6))))))
    diamond_transient  Root(B, C), B(D), C(D); all transient (D built twice)

ENV KNOBS
    PGO_EXP_ITERS          timed calls per repeat (default 20000)
    PGO_EXP_REPEATS        timed repeats per arm (default 5; the median is reported)
    PGO_EXP_WARMUP         warm calls before timing (default 2000)
    PGO_EXP_SAMPLE         creations profiled for the call counts (default 50)
    PGO_EXP_THREADS        comma list of thread counts for real_meld and pgo_guarded
                           (default "1"; >1 reports aggregate creations per second)
    PGO_EXP_COMPOSITIONS   comma list to restrict (default: all)
    PGO_EXP_MRO_DEPTH      generated classes inherit from a chain of this many bases, each
                           with an `__init__` that sets one slot and calls `super().__init__()`
                           (default 0; Melder's own classes sit at depth 2)

DISTRIBUTION-WEIGHTED SUMMARY
    `pgo_composition_scanner.py` measured Melder's own constructors: 58% take no object
    collaborator, 23% one, 8% two, 9% three or four, 2% five to eight. The report ends
    with the savings weighted by those shares over representative shapes (solo, w1_*,
    w2_mixed, w3_mixed/w4_mixed, mixed3s4t), so the number answers "what would PGO save
    a codebase shaped like Melder".

RUN (on the 3.14t target, from any directory; caching is off so nothing is written)
    python -X gil=0 tests/experimentation/pgo_codegen_composition_experiment.py

HOW TO READ THE RESULT
    The summary table's `saved_ns` and `saved_calls` columns are the juice per creation;
    `saved_per_1000_ms` is what 1000 creations of that composition get back. Compare
    that against the cost of profiling, regenerating and guarding, which this file does
    not model - it measures the ceiling, not the net.
"""

from __future__ import annotations

import os
import statistics
import sys
import threading
import time
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple


class ExperimentSettings:
    """
    Environment-driven settings for one run.

    Contract:
        - Every value is read once at construction from the `PGO_EXP_*` variables.
        - `threads` always starts with 1 so the per-creation tables exist for every
          composition; extra thread counts add aggregate rows.
    """

    __slots__ = ("iters", "repeats", "warmup", "sample", "threads", "compositions", "mro_depth")

    DEFAULT_ITERS: ClassVar[int] = 20000
    DEFAULT_REPEATS: ClassVar[int] = 5
    DEFAULT_WARMUP: ClassVar[int] = 2000
    DEFAULT_SAMPLE: ClassVar[int] = 50

    def __init__(self) -> None:
        self.iters: int = int(os.environ.get("PGO_EXP_ITERS", self.DEFAULT_ITERS))
        self.repeats: int = int(os.environ.get("PGO_EXP_REPEATS", self.DEFAULT_REPEATS))
        self.warmup: int = int(os.environ.get("PGO_EXP_WARMUP", self.DEFAULT_WARMUP))
        self.sample: int = int(os.environ.get("PGO_EXP_SAMPLE", self.DEFAULT_SAMPLE))
        raw_threads = os.environ.get("PGO_EXP_THREADS", "1")
        threads = sorted({int(part) for part in raw_threads.split(",") if part.strip()})
        self.threads: List[int] = [1] + [count for count in threads if count > 1]
        raw = os.environ.get("PGO_EXP_COMPOSITIONS", "")
        self.compositions: Optional[List[str]] = (
            [part.strip() for part in raw.split(",") if part.strip()] if raw else None
        )
        self.mro_depth: int = int(os.environ.get("PGO_EXP_MRO_DEPTH", "0"))


class Node:
    """
    One class in a composition: its name, its existence and its dependencies.

    Contract:
        - `singleton` True binds as `Existence.unique`; False binds as `Existence.many`.
        - `deps` are constructor parameters in signature order.
        - `cls` is filled by `CompositionBuilder.materialize`.
    """

    __slots__ = ("name", "singleton", "deps", "cls")

    def __init__(self, name: str, singleton: bool, deps: List["Node"]) -> None:
        self.name: str = name
        self.singleton: bool = singleton
        self.deps: List[Node] = deps
        self.cls: Optional[type] = None


class Guard:
    """One speculation guard: an int the PGO body compares once per creation."""

    __slots__ = ("epoch",)

    def __init__(self, epoch: int) -> None:
        self.epoch: int = epoch


class CompositionBuilder:
    """
    Builds the ten compositions as `Node` trees and materializes them as classes.

    Contract:
        - Every class is generated with `exec` so its constructor carries real type
          annotations that Melder injects by, one `__slots__` field per dependency, and a
          `built` class counter incremented in `__init__` (the same cost in every arm).
        - Node names are unique per composition; classes are fresh per composition so
          every composition binds into its own Spellbook.
    """

    __slots__ = ()

    @staticmethod
    def compositions() -> Dict[str, Node]:
        """Return the named root nodes of every composition."""

        def transient(name: str, deps: Optional[List[Node]] = None) -> Node:
            return Node(name, False, deps or [])

        def singleton(name: str, deps: Optional[List[Node]] = None) -> Node:
            return Node(name, True, deps or [])

        roots: Dict[str, Node] = {}
        roots["solo"] = transient("Root")
        roots["wide8_transient"] = transient("Root", [transient(f"T{i}") for i in range(8)])
        roots["wide8_singleton"] = transient("Root", [singleton(f"S{i}") for i in range(8)])
        roots["wide16_transient"] = transient("Root", [transient(f"T{i}") for i in range(16)])
        chain: Node = transient("T8")
        for level in range(7, 0, -1):
            chain = transient(f"T{level}", [chain])
        roots["chain8_transient"] = transient("Root", [chain])
        schain: Node = singleton("S8")
        for level in range(7, 0, -1):
            schain = singleton(f"S{level}", [schain])
        roots["chain8_singleton"] = transient("Root", [schain])
        shared = singleton("D")
        roots["diamond"] = transient("Root", [transient("B", [shared]), transient("C", [shared])])
        roots["mixed3s4t"] = transient(
            "Root", [singleton(f"S{i}") for i in range(3)] + [transient(f"T{i}") for i in range(4)]
        )
        alternating: Node = singleton("S6")
        for level in range(5, 0, -1):
            alternating = (transient if level % 2 else singleton)(f"{'T' if level % 2 else 'S'}{level}", [alternating])
        roots["chain6_alternating"] = transient("Root", [alternating])
        shared_t = transient("D")
        roots["diamond_transient"] = transient("Root", [transient("B", [shared_t]), transient("C", [shared_t])])
        # Narrow shapes matching the width distribution the scanner found in Melder itself.
        roots["w1_singleton"] = transient("Root", [singleton("S0")])
        roots["w1_transient"] = transient("Root", [transient("T0")])
        roots["w2_mixed"] = transient("Root", [singleton("S0"), transient("T0")])
        roots["w3_mixed"] = transient("Root", [singleton("S0"), singleton("S1"), transient("T0")])
        roots["w4_mixed"] = transient("Root", [singleton("S0"), singleton("S1"), transient("T0"), transient("T1")])
        roots["chain3_mixed"] = transient("Root", [transient("T1", [singleton("S2", [transient("T3")])])])
        return roots

    @staticmethod
    def walk(root: Node) -> List[Node]:
        """Return every distinct node reachable from `root`, dependencies first."""
        seen: Dict[str, Node] = {}

        def visit(node: Node) -> None:
            for dep in node.deps:
                visit(dep)
            seen.setdefault(node.name, node)

        visit(root)
        return list(seen.values())

    @staticmethod
    def base_chain(prefix: str, depth: int) -> Optional[type]:
        """
        Build `depth` chained base classes, each setting one slot and calling
        `super().__init__()`, and return the top one (or None for depth 0).
        """
        top: Optional[type] = None
        for level in range(1, depth + 1):
            name = f"{prefix}_Base{level}"
            parent = "" if top is None else f"({top.__name__})"
            source = (
                f"class {name}{parent}:\n"
                f"    __slots__ = ('_b{level}',)\n"
                f"    def __init__(self) -> None:\n"
                f"        super().__init__()\n"
                f"        self._b{level} = {level}\n"
            )
            namespace: Dict[str, Any] = {} if top is None else {top.__name__: top}
            namespace["__name__"] = __name__
            exec(source, namespace)
            top = namespace[name]
        return top

    @staticmethod
    def materialize(root: Node, prefix: str, mro_depth: int = 0) -> None:
        """
        Generate one class per node (dependencies first) and store it on `node.cls`.

        Raises:
            AssertionError: if a dependency has no class yet (walk order broken).
        """
        base = CompositionBuilder.base_chain(prefix, mro_depth)
        for node in CompositionBuilder.walk(root):
            if node.cls is not None:
                continue
            dep_classes = [dep.cls for dep in node.deps]
            assert all(dep_classes), node.name
            class_name = f"{prefix}_{node.name}"
            params = "".join(f", d{i}: {cls.__name__}" for i, cls in enumerate(dep_classes))
            slots = ", ".join(f"'d{i}'" for i in range(len(dep_classes)))
            assigns = "".join(f"        self.d{i} = d{i}\n" for i in range(len(dep_classes)))
            inherit = "" if base is None else f"({base.__name__})"
            super_call = "" if base is None else "        super().__init__()\n"
            source = (
                f"class {class_name}{inherit}:\n"
                f"    __slots__ = ({slots}{',' if dep_classes else ''})\n"
                f"    built = 0\n"
                f"    def __init__(self{params}) -> None:\n"
                f"{super_call}"
                f"{assigns}"
                f"        {class_name}.built += 1\n"
            )
            namespace: Dict[str, Any] = {cls.__name__: cls for cls in dep_classes}
            if base is not None:
                namespace[base.__name__] = base
            namespace["__name__"] = __name__
            exec(source, namespace)
            node.cls = namespace[class_name]


class MelderWorld:
    """
    One Spellbook and one non-dynamic root conduit holding a materialized composition.

    Contract:
        - Caching is off, so nothing is written to disk.
        - `spell_ids` maps node name to spell id; `root_id` is the root's.
        - `meld()` is the real warm creation of the root.
    """

    __slots__ = ("spellbook", "conduit", "spell_ids", "root_id", "root")

    def __init__(self, root: Node, frame_name: str) -> None:
        from melder.aether.aether import Aether
        from melder.aether.conduit.conduit import Conduit
        from melder.aether.spellbook.existence.existence import Existence
        from melder.aether.spellbook.spellbook import Spellbook
        from melder.nexus.nexus import Nexus

        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        self.spellbook = Spellbook(aetheric_frame=frame_name)
        configuration = self.spellbook.get_configuration()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        self.spellbook.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
        self.spell_ids: Dict[str, str] = {}
        for node in CompositionBuilder.walk(root):
            existence = Existence.unique if node.singleton else Existence.many
            self.spell_ids[node.name] = self.spellbook.bind(
                spell=node.cls, existence=existence, permissions="create"
            )
        self.root = root
        self.root_id: str = self.spell_ids[root.name]
        self.conduit = self.spellbook.conjure(name=f"{frame_name}-root", dynamic=False)

    def meld(self) -> Any:
        """Construct the root through the real meld door."""
        return self.conduit.meld(spell_id=self.root_id)

    def singleton_instances(self) -> Dict[str, Any]:
        """Return the live singleton instance of every singleton node, melded once."""
        instances: Dict[str, Any] = {}
        for node in CompositionBuilder.walk(self.root):
            if node.singleton:
                instances[node.name] = self.conduit.meld(spell_id=self.spell_ids[node.name])
        return instances

    def cleanup(self) -> None:
        """Tear the world down so the next composition starts from a fresh Aether."""
        self.conduit.cleanup()
        self.spellbook.cleanup()


class PgoBodies:
    """
    Generates the hand-written PGO arms for a composition as straight-line source.

    Contract:
        - `guarded`: singletons are closed-over constants, each guarded by one int
          compare on its `Guard.epoch`; one extra root-door guard; transient sites are
          constructed inline, positionally, in dependency order.
        - `store`: singletons come from `store_get(spell_id)` (one `dict.get` each);
          transients inline; no guards.
        - `floor`: the guarded body without guards.
        - A guard miss calls `deopt()`, which is the real meld (never taken while the
          epochs are stable, which the timed loop asserts).
    """

    __slots__ = ()

    @staticmethod
    def expression(node: Node, names: Dict[str, str], store: bool) -> str:
        """Return the construction expression for `node`."""
        if node.singleton:
            return f"store_get({names[node.name]!r})" if store else names[node.name]
        args = ", ".join(PgoBodies.expression(dep, names, store) for dep in node.deps)
        return f"{names[node.name]}({args})"

    @staticmethod
    def build(root: Node, world: MelderWorld, singletons: Dict[str, Any]) -> Dict[str, Callable[[], Any]]:
        """Compile the three PGO arms for `root` and return them by name."""
        names: Dict[str, str] = {}
        namespace: Dict[str, Any] = {}
        guards: List[Tuple[str, str]] = []
        for node in CompositionBuilder.walk(root):
            if node.singleton:
                const = f"S_{node.name}"
                names[node.name] = const
                namespace[const] = singletons[node.name]
                guard_name = f"G_{node.name}"
                namespace[guard_name] = Guard(7)
                guards.append((guard_name, "7"))
            else:
                names[node.name] = f"C_{node.name}"
                namespace[f"C_{node.name}"] = node.cls
        namespace["G_door"] = Guard(11)
        namespace["deopt"] = world.meld
        namespace["store_get"] = {
            world.spell_ids[name]: instance for name, instance in singletons.items()
        }.get
        store_names = {name: world.spell_ids[name] if node.singleton else names[name]
                       for name, node in ((n.name, n) for n in CompositionBuilder.walk(root))}
        guard_lines = "    if G_door.epoch != 11:\n        return deopt()\n" + "".join(
            f"    if {guard}.epoch != {epoch}:\n        return deopt()\n" for guard, epoch in guards
        )
        guarded_src = f"def pgo_guarded():\n{guard_lines}    return {PgoBodies.expression(root, names, False)}\n"
        floor_src = f"def pgo_floor():\n    return {PgoBodies.expression(root, names, False)}\n"
        store_src = f"def pgo_store():\n    return {PgoBodies.expression(root, store_names, True)}\n"
        exec(guarded_src + floor_src + store_src, namespace)
        return {
            "pgo_guarded": namespace["pgo_guarded"],
            "pgo_store": namespace["pgo_store"],
            "pgo_floor": namespace["pgo_floor"],
        }


class Meter:
    """Timing and call-counting helpers shared by every arm."""

    __slots__ = ()

    @staticmethod
    def time_ns(fn: Callable[[], Any], settings: ExperimentSettings) -> float:
        """Median ns per call over `settings.repeats` runs of `settings.iters` calls."""
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

    @staticmethod
    def calls(fn: Callable[[], Any], sample: int) -> Tuple[float, float]:
        """Average (python_calls, c_calls) per call over `sample` profiled calls."""
        counts = {"call": 0, "c_call": 0}

        def profiler(frame: Any, event: str, arg: Any) -> None:
            if event in counts:
                counts[event] += 1

        sys.setprofile(profiler)
        try:
            for _ in range(sample):
                fn()
        finally:
            sys.setprofile(None)
        # The profiled region counts the call of `fn` itself once per sample; subtract it.
        return (counts["call"] - sample) / sample, counts["c_call"] / sample

    @staticmethod
    def objects(fn: Callable[[], Any], classes: List[type], sample: int) -> float:
        """Objects constructed per call, from the generated classes' `built` counters."""
        before = sum(cls.built for cls in classes)
        for _ in range(sample):
            fn()
        return (sum(cls.built for cls in classes) - before) / sample

    @staticmethod
    def threaded_rate(fn: Callable[[], Any], threads: int, settings: ExperimentSettings) -> float:
        """Aggregate creations per second with `threads` threads calling `fn` in parallel."""
        iters = settings.iters
        start_event = threading.Event()

        def worker() -> None:
            start_event.wait()
            for _ in range(iters):
                fn()

        pool = [threading.Thread(target=worker) for _ in range(threads)]
        for thread in pool:
            thread.start()
        started = time.perf_counter_ns()
        start_event.set()
        for thread in pool:
            thread.join()
        elapsed = time.perf_counter_ns() - started
        return threads * iters / (elapsed / 1e9)


def _check_shape(instance: Any, node: Node) -> None:
    """Raise AssertionError unless `instance` matches the composition's tree."""
    assert type(instance) is node.cls, (type(instance), node.cls)
    for index, dep in enumerate(node.deps):
        _check_shape(getattr(instance, f"d{index}"), dep)


def run_composition(name: str, root: Node, settings: ExperimentSettings) -> Dict[str, Any]:
    """Materialize, bind, measure every arm and return one result record."""
    CompositionBuilder.materialize(root, name, settings.mro_depth)
    classes = [node.cls for node in CompositionBuilder.walk(root)]
    world = MelderWorld(root, f"pgo-{name}")
    try:
        singletons = world.singleton_instances()
        arms: Dict[str, Callable[[], Any]] = {"real_meld": world.meld}
        arms.update(PgoBodies.build(root, world, singletons))
        arms["noop"] = lambda: None
        for arm_name, fn in arms.items():
            if arm_name != "noop":
                _check_shape(fn(), root)
        rows: Dict[str, Dict[str, float]] = {}
        for arm_name, fn in arms.items():
            ns = Meter.time_ns(fn, settings)
            py_calls, c_calls = Meter.calls(fn, settings.sample)
            objects = 0.0 if arm_name == "noop" else Meter.objects(fn, classes, settings.sample)
            rows[arm_name] = {"ns": ns, "py_calls": py_calls, "c_calls": c_calls, "objects": objects}
        rates: Dict[str, Dict[int, float]] = {}
        for threads in settings.threads:
            if threads > 1:
                for arm_name in ("real_meld", "pgo_guarded"):
                    rates.setdefault(arm_name, {})[threads] = Meter.threaded_rate(arms[arm_name], threads, settings)
        return {"name": name, "rows": rows, "rates": rates, "classes": len(classes)}
    finally:
        world.cleanup()


def _print_report(results: List[Dict[str, Any]], settings: ExperimentSettings) -> None:
    """Print the per-composition tables and the summary as Markdown."""
    import melder

    gil = "disabled" if not sys._is_gil_enabled() else "enabled"
    print(f"# PGO codegen composition experiment\n")
    print(f"melder {melder.__version__}; Python {sys.version.split()[0]}; GIL {gil}; "
          f"iters={settings.iters} repeats={settings.repeats} warmup={settings.warmup} sample={settings.sample} "
          f"mro_depth={settings.mro_depth}\n")
    for result in results:
        rows = result["rows"]
        real = rows["real_meld"]
        print(f"## {result['name']} ({result['classes']} classes)\n")
        print("| arm | ns/creation | py calls | C calls | objects | vs real_meld |")
        print("| --- | ---: | ---: | ---: | ---: | --- |")
        for arm, row in rows.items():
            delta = "" if arm == "real_meld" else (
                f"-{real['ns'] - row['ns']:.0f} ns, -{real['py_calls'] - row['py_calls']:.1f} py, "
                f"-{real['c_calls'] - row['c_calls']:.1f} C")
            print(f"| {arm} | {row['ns']:.0f} | {row['py_calls']:.1f} | {row['c_calls']:.1f} | {row['objects']:.1f} | {delta} |")
        for arm, by_threads in result["rates"].items():
            for threads, rate in by_threads.items():
                print(f"| {arm} @ {threads} threads | {1e9 * threads / rate:.0f} ns/creation/thread | | | | {rate:,.0f} creations/s |")
        print()
    print("## Summary: the most an ideal PGO body wins per creation\n")
    print("| composition | real ns | guarded ns | saved ns | saved % | saved py calls | saved C calls | saved per 1000 (ms) |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for result in results:
        real = result["rows"]["real_meld"]
        best = result["rows"]["pgo_guarded"]
        saved = real["ns"] - best["ns"]
        print(f"| {result['name']} | {real['ns']:.0f} | {best['ns']:.0f} | {saved:.0f} | {100 * saved / real['ns']:.0f}% | "
              f"{real['py_calls'] - best['py_calls']:.1f} | {real['c_calls'] - best['c_calls']:.1f} | {saved / 1e6 * 1000:.2f} |")
    by_name = {result["name"]: result["rows"] for result in results}
    buckets: List[Tuple[str, float, List[str]]] = [
        ("width 0", 0.58, ["solo"]), ("width 1", 0.23, ["w1_singleton", "w1_transient"]),
        ("width 2", 0.08, ["w2_mixed"]), ("width 3-4", 0.09, ["w3_mixed", "w4_mixed"]),
        ("width 5-8", 0.02, ["mixed3s4t"]),
    ]
    if all(name in by_name for _label, _w, names in buckets for name in names):
        print("\n## Weighted by Melder's own constructor-width distribution (scanner, 2026-09-27)\n")
        print("| bucket | share | shapes | real ns | guarded ns | saved ns | saved % |")
        print("| --- | ---: | --- | ---: | ---: | ---: | ---: |")
        weighted_real = weighted_saved = 0.0
        for label, weight, names in buckets:
            real_ns = statistics.mean(by_name[n]["real_meld"]["ns"] for n in names)
            best_ns = statistics.mean(by_name[n]["pgo_guarded"]["ns"] for n in names)
            weighted_real += weight * real_ns
            weighted_saved += weight * (real_ns - best_ns)
            print(f"| {label} | {100 * weight:.0f}% | {', '.join(names)} | {real_ns:.0f} | {best_ns:.0f} | "
                  f"{real_ns - best_ns:.0f} | {100 * (real_ns - best_ns) / real_ns:.0f}% |")
        print(f"| **weighted** | 100% | | {weighted_real:.0f} | {weighted_real - weighted_saved:.0f} | "
              f"{weighted_saved:.0f} | {100 * weighted_saved / weighted_real:.0f}% |")
        print(f"\nWeighted: an ideal PGO body saves {weighted_saved:.0f} ns per creation on a codebase shaped like "
              f"Melder ({weighted_saved / 1e3:.2f} ms per 1000 creations, {weighted_saved / 1e3:.1f} s per million).")


def main() -> int:
    """Run every selected composition and print the report."""
    settings = ExperimentSettings()
    compositions = CompositionBuilder.compositions()
    selected = settings.compositions or list(compositions)
    results = [run_composition(name, compositions[name], settings) for name in selected]
    _print_report(results, settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
