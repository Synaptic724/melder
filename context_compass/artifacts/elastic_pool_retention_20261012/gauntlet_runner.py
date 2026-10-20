"""
Gauntlet runner for the elastic pool retention task (TASK-2026-10-12-make_kernel_pools_elastic).

Runs the melder_gauntlet workload of `benchmarks/testing_other_di/test_melder_gauntlet.py` against a chosen source
tree with any thread count. The test file caps MELDER_GAUNTLET_THREADS at 3; `melder_gauntlet_support` itself spreads
more threads over the request / worker A / worker B lanes, so this runner builds the same runtime and config and calls
the support harness directly. Each scope cycle takes a lesser from the root's ConduitPool and one spellspace from that
lesser's SpellSpacePool, so the root pool sees one lesser per running thread.

Appends one JSON line per run to --out; prints the harness's normal report too. With --instrument the pool classes
are wrapped to count shell builds and destructions (do not mix instrumented runs into timing comparisons).

Usage:
    python -X gil=0 gauntlet_runner.py --tree <tree root> --iters N --threads T --label L --out <file.jsonl>
        [--instrument]
"""
import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict


def _install_counters(counters: Dict[str, int]) -> None:
    """
    Wrap the two kernel pools so shell builds, destructions and the peak of lessers out at once are counted.

    The counters take one lock (free-threaded `+=` on a dict loses updates), so instrumented runs are slower and
    never mixed into timing comparisons.
    """
    import threading
    from melder.aether.conduit.conduit_pool import ConduitPool
    from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool

    lock = threading.Lock()
    original_take = ConduitPool.create_object
    original_return = ConduitPool.return_lesser_conduit
    original_conduit_destroy = ConduitPool.destroy_object
    original_space_create = SpellSpacePool.create_object
    original_space_destroy = SpellSpacePool.destroy_object

    def bump(key: str, delta: int = 1) -> None:
        with lock:
            counters[key] += delta
            if key == "lessers_out" and counters["lessers_out"] > counters["lessers_out_peak"]:
                counters["lessers_out_peak"] = counters["lessers_out"]

    def take(self: Any, *args: Any, **kwargs: Any) -> Any:
        shell = original_take(self, *args, **kwargs)
        bump("lesser_reused" if shell is not None else "lesser_built")
        bump("lessers_out")
        return shell

    def give_back(self: Any, conduit: Any) -> None:
        bump("lessers_out", -1)
        original_return(self, conduit)

    def conduit_destroy(self: Any, obj: Any) -> None:
        bump("lesser_destroyed")
        original_conduit_destroy(self, obj)

    def space_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        bump("spellspace_built")
        return original_space_create(self, *args, **kwargs)

    def space_destroy(self: Any, obj: Any) -> None:
        bump("spellspace_destroyed")
        original_space_destroy(self, obj)

    ConduitPool.create_object = take
    ConduitPool.return_lesser_conduit = give_back
    ConduitPool.destroy_object = conduit_destroy
    SpellSpacePool.create_object = space_create
    SpellSpacePool.destroy_object = space_destroy


def main() -> int:
    """Run one gauntlet configuration and append its JSON record."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True)
    parser.add_argument("--iters", type=int, required=True)
    parser.add_argument("--threads", type=int, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--instrument", action="store_true")
    parser.add_argument("--request-scopes", type=int, default=10)
    parser.add_argument("--worker-a-jobs", type=int, default=25)
    parser.add_argument("--worker-b-jobs", type=int, default=30)
    args = parser.parse_args()

    tree = Path(args.tree).resolve()
    sys.path.insert(0, str(tree / "benchmarks" / "testing_other_di"))
    sys.path.insert(0, str(tree / "src"))
    import melder
    import melder_gauntlet_support as support
    import test_melder_gauntlet as gauntlet

    counters = {
        "lesser_built": 0, "lesser_reused": 0, "lesser_destroyed": 0,
        "spellspace_built": 0, "spellspace_destroyed": 0, "lessers_out": 0, "lessers_out_peak": 0,
    }
    if args.instrument:
        _install_counters(counters)

    cfg = support.GauntletConfig(
        iterations=args.iters,
        threads=args.threads,
        request_scope_runs=args.request_scopes,
        worker_a_jobs=args.worker_a_jobs,
        worker_b_jobs=args.worker_b_jobs,
    )
    ops = gauntlet._build_runtime_melder()
    pools: Dict[str, Any] = {}
    original_cleanup = ops.cleanup

    def cleanup_with_snapshot() -> None:
        from melder.aether.aether import Aether
        root = Aether().get_root_conduit_by_name("real-world-gauntlet", aetheric_frame_name="real-world-gauntlet")
        pools["conduit_pool"] = root._conduit_pool.describe()
        pools["root_spellspace_pool"] = root._spellspace_pool.describe()
        original_cleanup()

    ops = dataclasses.replace(ops, cleanup=cleanup_with_snapshot)
    wall_t0 = time.perf_counter()
    result = support.run_gauntlet_benchmark(ops, cfg)
    wall_s = time.perf_counter() - wall_t0
    support.print_benchmark_result(result)

    def summary(s: Any) -> Dict[str, float]:
        return {"median_ms": s.median_ns / 1e6, "p95_ms": s.p95_ns / 1e6, "p99_ms": s.p99_ns / 1e6,
                "avg_ms": s.avg_ns / 1e6, "max_ms": s.max_ns / 1e6}

    record = {
        "label": args.label,
        "melder": melder.__version__,
        "python": sys.version.split()[0],
        "gil": result.gil_status_label,
        "threads": args.threads,
        "iters": args.iters,
        "wall_s": round(wall_s, 3),
        "hot_scopes": result.total_hot_scopes,
        "hot_scopes_per_s": round(result.hot_scope_cycles_per_s, 1),
        "iteration": summary(result.iteration_summary),
        "threaded": summary(result.threaded_summary),
        "outer_create": summary(result.outer_scope_create_summary),
        "outer_cleanup": summary(result.outer_scope_cleanup_summary),
        "outer_total": summary(result.outer_scope_total_summary),
        "request_create": summary(result.request_scope_create_summary),
        "request_cleanup": summary(result.request_scope_cleanup_summary),
        "request_total": summary(result.request_scope_total_summary),
        "pools_at_end": pools,
        "counters": counters if args.instrument else None,
    }
    with open(args.out, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
