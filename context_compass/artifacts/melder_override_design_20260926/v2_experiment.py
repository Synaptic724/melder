"""Design v2 experiments E2-E4 against today's executors (artifact-only; no source edits).

Usage (repository root, PYTHONPATH=src:.):
    python v2_experiment.py correctness <out.json>            # E3
    python v2_experiment.py timing <graph> <out.json>          # E2; graph in TIMING_GRAPHS
    python v2_experiment.py threads <rounds> <out.json>        # E4

Every world disables disk caching. "current" runs today's executors unchanged; "v2" swaps the root
spell's CreationContext slots to v2_prototype plans (SlotSwitch). Timing numbers are observations.
"""
import gc
import json
import statistics
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment, _path_value
from v2_prototype import SlotSwitch, V2Runtime

COUNTING = """
import threading as _threading
_COUNT_LOCK = _threading.Lock()
def hit(name):
    with _COUNT_LOCK:
        COUNTS[name] = COUNTS.get(name, 0) + 1
"""


class World:
    """One isolated Book/Conduit pair with disk caching disabled."""

    def __init__(self, source: str, bindings: Tuple[Tuple[str, str], ...]) -> None:
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        self.ns: Dict[str, Any] = {"__name__": "v2_models", "COUNTS": {}}
        exec(compile(source, "v2_models", "exec"), self.ns)
        configuration = SpellbookConfiguration().with_defaults()
        configuration.with_phase_scheduler_workers(1)
        posture = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
        posture.with_system_caching_enabled(False)
        self.book = Spellbook(configuration=configuration)
        self.ids: Dict[str, str] = {}
        for name, existence in bindings:
            self.ids[name] = self.book.bind(spell=self.ns[name], existence=existence)
        self.conduit = self.book.conjure()

    def spell(self, name: str) -> Any:
        meld = self.conduit._meld
        spell_id = self.ids[name]
        return meld._spell_id_pool.get(spell_id) or meld._resolve_spell_by_id(spell_id)

    def install_v2(self, root: str) -> SlotSwitch:
        spell = self.spell(root)
        spell._get_or_build_creation_context()
        switch = SlotSwitch(spell, V2Runtime(spell))
        switch.use("v2")
        return switch

    def cleanup(self) -> None:
        try:
            self.conduit.permanent_cleanup()
        finally:
            self.book.cleanup()
            Aether._reset_singleton_for_tests()


# ---- E3: correctness and constructor counts ----------------------------------------------------------

def _classes(spec: str) -> str:
    """Tiny DSL: 'Name(p: Dep, q: Dep)' lines -> counting classes that store their parameters."""
    lines = [COUNTING]
    for line in spec.strip().splitlines():
        name, _, rest = line.strip().partition("(")
        params = [part.strip() for part in rest.rstrip(")").split(",") if part.strip()]
        lines.append(f"class {name}:")
        signature = ", ".join(["self"] + params)
        lines.append(f"    def __init__({signature}):")
        lines.append(f"        hit({name!r})")
        for param in params:
            field = param.split(":")[0].strip()
            lines.append(f"        self.{field} = {field}")
        if not params:
            lines.append("        pass")
    return "\n".join(lines) + "\n"


E3_GRAPHS: Dict[str, Dict[str, Any]] = {
    "many_shallow": {
        "classes": "A()\nB()\nRoot(a: A, b: B)",
        "bindings": (("A", "many"), ("B", "many"), ("Root", "many")),
        "worlds": [[None, {"a": 1}, {"b": 1}, {"a": 1, "b": 1}, (1,), (1, 2), {"*a": 1}, {"**a": 1}, {"nosuch": 1}]],
    },
    "epic_five": {
        "classes": "A()\nB()\nC()\nD()\nE()\nConsumer(a: A, b: B, c: C, d: D, e: E)",
        "bindings": (("A", "many"), ("B", "many"), ("C", "many"), ("D", "many"), ("E", "many"),
                     ("Consumer", "many")),
        "root": "Consumer",
        "worlds": [[None, {"a": 1, "b": 1, "c": 1}]],
    },
    "tree4": {
        "classes": "L()\nN2(left: L, right: L)\nN1(left: N2, right: N2)\nRoot(left: N1, right: N1)",
        "bindings": (("L", "many"), ("N2", "many"), ("N1", "many"), ("Root", "many")),
        "worlds": [[None, {"left": 1}, {"left": 1, "right": 1}, {"left>left": 1}, {"**left": 1}]],
    },
    "gen_mixed": {
        "classes": "X()\nS(x: X)\nA()\nRoot(a: A, s: S)",
        "bindings": (("X", "many"), ("S", "unique_per_conduit"), ("A", "many"), ("Root", "many")),
        "worlds": [[None, None, {"s": 1}, {"a": 1}, {"s>x": 1}], [{"s>x": 1}, None], [{"s": 1}, None]],
    },
    "gen_diamond": {
        "classes": "X()\nS(x: X)\nL(s: S)\nR(s: S)\nRoot(l: L, r: R)",
        "bindings": (("X", "many"), ("S", "unique_per_conduit"), ("L", "many"), ("R", "many"),
                     ("Root", "many")),
        "worlds": [[None, None, {"l": 1}, {"l>s": 1}, {"**s": 1}, {"*s": 1}]],
    },
    "p3_alias": {
        "classes": "X()\nD(x: X)\nP(d: D)\nQ(d: D)\nRoot(p: P, q: Q)",
        "bindings": (("X", "many"), ("D", "unique_per_conduit"), ("P", "unique_per_conduit"), ("Q", "many"),
                     ("Root", "many")),
        "worlds": [[{"p>d>x": 1}, None], [{"q>d>x": 1}], [{"p": 1, "p>d>x": 1}], [None, {"p>d>x": 1}]],
    },
    "unresolved": {
        "classes": "A()\nPackage()\nTask(work: Package)\nRoot(a: A, t: Task)",
        "bindings": (("A", "many"), ("Task", "many"), ("Root", "many")),
        "worlds": [[None, {"t>work": 1}, {"t": 1}]],
    },
}


def _payload(template: Any) -> Tuple[Any, Dict[int, str]]:
    """Replace template values with fresh sentinel objects; remember their labels by id."""
    if template is None:
        return None, {}
    if isinstance(template, tuple):
        values = tuple(object() for _ in template)
        return values, {id(v): f"<args[{i}]>" for i, v in enumerate(values)}
    payload = {key: object() for key in template}
    return payload, {id(v): f"<{k}>" for k, v in payload.items()}


def _describe(value: Any, labels: Dict[int, str], identities: Dict[int, int], depth: int = 0) -> Any:
    """Structure with supplied values labeled and object identity numbered in first-seen order."""
    if id(value) in labels:
        return labels[id(value)]
    if depth > 12 or not hasattr(value, "__dict__"):
        return type(value).__name__
    number = identities.setdefault(id(value), len(identities))
    fields = {k: _describe(v, labels, identities, depth + 1) for k, v in vars(value).items()}
    return {"type": type(value).__name__, "id": number, "fields": fields}


def _run_world(name: str, spec: Dict[str, Any], calls: List[Any], variant: str) -> List[Dict[str, Any]]:
    world = World(_classes(spec["classes"]), spec["bindings"])
    root = spec.get("root", "Root")
    rows: List[Dict[str, Any]] = []
    keep: List[Any] = []
    identities: Dict[int, int] = {}
    try:
        if variant == "v2":
            world.install_v2(root)
        else:
            world.spell(root)._get_or_build_creation_context()
        for template in calls:
            payload, labels = _payload(template)
            world.ns["COUNTS"].clear()
            try:
                if payload is None:
                    result = world.conduit.meld(world.ns[root])
                else:
                    result = world.conduit.meld(world.ns[root], override=payload)
                keep.append(result)
                rows.append({"call": repr(template), "counts": dict(sorted(world.ns["COUNTS"].items())),
                             "result": _describe(result, labels, identities)})
            except Exception as error:
                cause = error.__cause__ or getattr(error, "inner", None)
                rows.append({"call": repr(template), "counts": dict(sorted(world.ns["COUNTS"].items())),
                             "error": f"{type(error).__name__}: {str(error)[:160]}",
                             "cause": None if cause is None else f"{type(cause).__name__}: {str(cause)[:160]}"})
    finally:
        keep.clear()
        world.cleanup()
    return rows


def correctness(out: str) -> None:
    report: Dict[str, Any] = {}
    for name, spec in E3_GRAPHS.items():
        report[name] = []
        for calls in spec["worlds"]:
            current = _run_world(name, spec, calls, "current")
            v2 = _run_world(name, spec, calls, "v2")
            for before, after in zip(current, v2):
                report[name].append({"call": before["call"], "current": before, "v2": after,
                                     "same_result": before.get("result") == after.get("result"),
                                     "same_error_type": before.get("error", "").split(":")[0]
                                     == after.get("error", "").split(":")[0]})
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    for name, rows in report.items():
        for row in rows:
            c, v = row["current"], row["v2"]
            print(f"{name:12} {row['call']:32} cur={c.get('counts')} {('ERR ' + c['error'][:60]) if 'error' in c else ''}")
            print(f"{'':12} {'':32} v2 ={v.get('counts')} {('ERR ' + v['error'][:60]) if 'error' in v else ''}"
                  f" same_result={row['same_result']}")


# ---- E2: throughput ---------------------------------------------------------------------------------

TIMING_GRAPHS = ("shallow", "wide", "diamond", "deep", "shared_mixed")


def _average_ns(call: Callable[[], Any], iterations: int) -> float:
    gc.collect()
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        started = time.perf_counter_ns()
        for _ in range(iterations):
            call()
        return (time.perf_counter_ns() - started) / iterations
    finally:
        if was_enabled:
            gc.enable()


def _benchmark_cases(graph: str) -> Tuple[Any, Dict[str, Tuple[Callable[[], Any], Dict[str, Any]]], SlotSwitch, Any]:
    world = MelderExperiment()
    world.setup(graph, "automatic")
    cases = {label: (call, expected) for label, (call, expected, _note) in world.cases.items()}
    for label, (call, _expected) in list(cases.items()):
        try:
            call()
            call()
        except Exception:
            pass  # root_args_tuple raises today; kept for the v2 variant only
    meld = world.conduit._meld
    spell = meld._spell_id_pool.get(world.root_id) or meld._resolve_spell_by_id(world.root_id)
    switch = SlotSwitch(spell, V2Runtime(spell))
    return world, cases, switch, world.root_type


def _shared_cases() -> Tuple[Any, Dict[str, Tuple[Callable[[], Any], Dict[str, Any]]], SlotSwitch, Any]:
    world = World(_classes("X()\nS(x: X)\nA()\nB()\nRoot(a: A, b: B, s: S)"),
                  (("X", "many"), ("S", "unique_per_conduit"), ("A", "many"), ("B", "many"), ("Root", "many")))
    meld = world.conduit.meld
    root = world.ns["Root"]
    first = meld(root)
    supplied_s, supplied_a = first.s, object()
    one_a = {"a": supplied_a}
    one_s = {"s": supplied_s}
    cases = {
        "normal": (lambda: meld(root), {}),
        "empty_tuple": (lambda: meld(root, override=()), {}),
        "root_one_reused": (lambda: meld(root, override=one_a), {"a": supplied_a}),
        "shared_supplied": (lambda: meld(root, override=one_s), {"s": supplied_s}),
        "python_root_only": (lambda: root(supplied_a, supplied_a, supplied_s), {}),
    }
    for call, _ in cases.values():
        call()
        call()
    spell = world.spell("Root")
    switch = SlotSwitch(spell, V2Runtime(spell))
    return world, cases, switch, root


def timing(graph: str, out: str, repeats: int = 7, sample_ms: float = 30.0, warmup: int = 128) -> None:
    world, cases, switch, root_type = _shared_cases() if graph == "shared_mixed" else _benchmark_cases(graph)
    try:
        measured: List[Tuple[str, str]] = []
        verified: Dict[str, str] = {}
        for label, (call, expected) in cases.items():
            for variant in (("lower_bound",) if label == "python_root_only" else ("current", "v2")):
                switch.use("current" if variant != "v2" else "v2")
                try:
                    first, second = call(), call()
                    assert first is not second, "transient root reused"
                    for path, supplied in expected.items():
                        assert _path_value(first, path) is supplied, f"missed {path}"
                        assert _path_value(second, path) is supplied, f"missed {path}"
                    verified[f"{label}/{variant}"] = "ok"
                    measured.append((label, variant))
                except Exception as error:
                    verified[f"{label}/{variant}"] = f"{type(error).__name__}: {str(error)[:120]}"
        counts: Dict[Tuple[str, str], int] = {}
        samples: Dict[Tuple[str, str], List[float]] = {entry: [] for entry in measured}
        for label, variant in measured:
            switch.use("v2" if variant == "v2" else "current")
            call = cases[label][0]
            for _ in range(warmup):
                call()
            probe = _average_ns(call, 64)
            counts[(label, variant)] = max(64, min(100_000, int(sample_ms * 1e6 / probe)))
        for repeat in range(repeats):
            order = measured[repeat % len(measured):] + measured[:repeat % len(measured)]
            for label, variant in order:
                switch.use("v2" if variant == "v2" else "current")
                samples[(label, variant)].append(_average_ns(cases[label][0], counts[(label, variant)]))
        switch.use("current")
        baseline = statistics.median(samples[("normal", "current")])
        rows = []
        for (label, variant), values in samples.items():
            median = statistics.median(values)
            rows.append({"graph": graph, "case": label, "variant": variant, "median_ns": median,
                         "min_ns": min(values), "max_ns": max(values), "samples_ns": values,
                         "iterations": counts[(label, variant)],
                         "percent_of_current_normal": 100 * baseline / median})
        report = {"python": sys.version, "gil_enabled": sys._is_gil_enabled(), "graph": graph,
                  "verified": verified, "rows": rows}
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=1)
        for key, status in verified.items():
            if status != "ok":
                print("NOT MEASURED", key, status)
        for row in sorted(rows, key=lambda r: (r["case"], r["variant"])):
            print(f"{graph:12} {row['case']:18} {row['variant']:11} {row['median_ns'] / 1000:9.3f} us"
                  f"  {row['percent_of_current_normal']:7.1f}% of current normal")
    finally:
        try:
            switch.use("current")
        finally:
            world.cleanup()


# ---- E4: threads ------------------------------------------------------------------------------------

THREAD_CLASSES = """
import time as _time
class X:
    def __init__(self):
        hit('X')
class Q:
    def __init__(self, x: X):
        hit('Q'); _time.sleep(0.0002); self.x = x
class P:
    def __init__(self, q: Q):
        hit('P'); _time.sleep(0.0002); self.q = q
class Root:
    def __init__(self, p: P):
        hit('Root'); self.p = p
class Root2:
    def __init__(self, q: Q):
        hit('Root2'); self.q = q
"""


def threads(rounds: int, out: str, workers: int = 8) -> None:
    world = World(COUNTING + THREAD_CLASSES,
                  (("X", "many"), ("Q", "unique_per_conduit"), ("P", "unique_per_conduit"),
                   ("Root", "many"), ("Root2", "many")))
    report: Dict[str, Any] = {"python": sys.version, "gil_enabled": sys._is_gil_enabled(), "variants": {}}
    try:
        switches = []
        for root in ("Root", "Root2"):
            spell = world.spell(root)
            spell._get_or_build_creation_context()
        warm = world.conduit.create_lesser_conduit()
        warm.meld(world.ns["Root"])
        warm.meld(world.ns["Root2"])
        warm.meld(world.ns["Root"], override={"p": object()})
        warm.cleanup()
        for root in ("Root", "Root2"):
            spell = world.spell(root)
            switches.append(SlotSwitch(spell, V2Runtime(spell)))
        for variant in ("current", "v2"):
            for switch in switches:
                switch.use(variant)
            failures: List[str] = []
            durations: List[float] = []
            for round_index in range(rounds):
                lesser = world.conduit.create_lesser_conduit()
                world.ns["COUNTS"].clear()
                barrier = threading.Barrier(workers)
                results: List[Optional[Tuple[str, Any]]] = [None] * workers
                errors: List[str] = []
                supplied_p = object()

                def work(index: int) -> None:
                    try:
                        barrier.wait(timeout=10)
                        if index < 4:
                            results[index] = ("root", lesser.meld(world.ns["Root"]))
                        elif index < 6:
                            results[index] = ("root2", lesser.meld(world.ns["Root2"]))
                        else:
                            results[index] = ("cut", lesser.meld(world.ns["Root"], override={"p": supplied_p}))
                    except Exception as error:
                        errors.append(f"{type(error).__name__}: {error}")

                pool = [threading.Thread(target=work, args=(i,)) for i in range(workers)]
                started = time.perf_counter()
                for thread in pool:
                    thread.start()
                for thread in pool:
                    thread.join(timeout=20)
                durations.append(time.perf_counter() - started)
                if any(thread.is_alive() for thread in pool):
                    failures.append(f"round {round_index}: DEADLOCK (threads alive after 20 s)")
                    break
                counts = dict(world.ns["COUNTS"])
                ps = {id(r[1].p) for r in results if r and r[0] == "root"}
                qs = {id(r[1].p.q) for r in results if r and r[0] == "root"} | {id(r[1].q) for r in results if r and r[0] == "root2"}
                cut_ok = all(r[1].p is supplied_p for r in results if r and r[0] == "cut")
                if errors or counts.get("P", 0) != 1 or counts.get("Q", 0) != 1 or len(ps) != 1 or len(qs) != 1 or not cut_ok:
                    failures.append(f"round {round_index}: counts={counts} ps={len(ps)} qs={len(qs)} cut_ok={cut_ok} errors={errors[:2]}")
                lesser.cleanup()
            report["variants"][variant] = {"rounds": rounds, "workers": workers, "failures": failures[:20],
                                           "failure_count": len(failures),
                                           "median_round_ms": 1000 * statistics.median(durations),
                                           "max_round_ms": 1000 * max(durations)}
            print(variant, json.dumps(report["variants"][variant]))
        for switch in switches:
            switch.use("current")
    finally:
        world.cleanup()
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "correctness":
        correctness(sys.argv[2])
    elif command == "timing":
        timing(sys.argv[2], sys.argv[3])
    elif command == "threads":
        threads(int(sys.argv[2]), sys.argv[3])
    else:
        raise SystemExit(f"unknown command {command}")
