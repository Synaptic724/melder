"""
Order probe for the shared real-world gauntlet (melder_0, 2026-09-30).

Purpose:
    Measure whether a library's gauntlet result depends on the libraries that ran
    before it in the same interpreter, and record the process state each library
    inherits. It calls the harness's own `_run_gauntlet_benchmark` unchanged, so
    the measured loop is exactly the benchmark's.

Usage:
    python -X gil=0 order_probe.py --repo-root <tree> --order dishka,melder \
        --run-tag r1 --out results.jsonl [--state-probe]

Contract:
    - One process runs one order. Each entry of --order runs once, in that order,
      exactly as `real_world_gauntlet_gil_runner.main()` runs its fixed tuple. An
      entry may repeat (for example `melder,melder`).
    - Without --state-probe nothing else runs between libraries.
    - With --state-probe, before each library it records the GC-tracked object
      count, how many of those objects carry an owning-thread id (`ob_tid`, the
      first word of a free-threaded object header) other than the main thread's,
      `gc.get_count()`, the interned-string count, and the start+join time of
      no-op threads; after the last library it records the same once more as an
      `(end)` row. The thread probe starts threads of its own, so state-probe runs
      are reported apart.
    - Appends one JSON object per library to --out; prints a one-line summary.
    - Reads the harness configuration from the same environment variables as the
      benchmark (`DI_GAUNTLET_ITERS`, `DI_GAUNTLET_THREADS`, ...).
"""
import argparse
import ctypes
import gc
import json
import os
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List


def _parse_args() -> argparse.Namespace:
    """
    Parse the command line.

    Returns:
        argparse.Namespace: repo_root, order, run_tag, out, state_probe and
            thread_samples.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--order", required=True)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--state-probe", action="store_true")
    parser.add_argument("--thread-samples", type=int, default=200)
    return parser.parse_args()


def _import_harness(repo_root: Path) -> Any:
    """
    Import the gauntlet module from `repo_root` the way the standalone runner does.

    Args:
        repo_root: Tree holding `benchmarks/` and `src/`.

    Returns:
        Any: The `test_real_world_gauntlet` module.
    """
    for path in (repo_root, repo_root / "src"):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)
    import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet
    return gauntlet


def _ob_tid(obj: object) -> int:
    """
    Read the owning-thread id from a free-threaded object header.

    Args:
        obj: Any live object.

    Returns:
        int: The header's first word (`ob_tid`); 0 for merged or static objects.
    """
    return ctypes.c_size_t.from_address(id(obj)).value


def _noop() -> None:
    """Thread body for the start+join probe: does nothing."""
    return None


def _thread_cycle_us(samples: int) -> Dict[str, float]:
    """
    Time `samples` sequential start+join cycles of no-op threads.

    Args:
        samples: Number of threads to start and join, one at a time.

    Returns:
        Dict[str, float]: median and mean microseconds per cycle.
    """
    durations: List[int] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        durations.append(time.perf_counter_ns() - t0)
    return {
        "thread_cycle_median_us": statistics.median(durations) / 1000.0,
        "thread_cycle_mean_us": statistics.fmean(durations) / 1000.0,
    }


def _state_snapshot(main_tid: int, thread_samples: int) -> Dict[str, Any]:
    """
    Record the process state a library is about to inherit.

    Args:
        main_tid: `threading.get_ident()` of the main thread.
        thread_samples: Threads for the start+join probe (run last).

    Returns:
        Dict[str, Any]: gc_objects, foreign_owned, foreign_tids, gc_count, the
            interned-string count and the thread-cycle timings.
    """
    objects = gc.get_objects()
    foreign_owned = 0
    foreign_tids = set()
    for obj in objects:
        tid = _ob_tid(obj)
        if tid != 0 and tid != main_tid:
            foreign_owned += 1
            foreign_tids.add(tid)
    gc_objects = len(objects)
    del objects
    snapshot: Dict[str, Any] = {
        "gc_objects": gc_objects,
        "foreign_owned": foreign_owned,
        "foreign_tids": len(foreign_tids),
        "gc_count": list(gc.get_count()),
        "interned_strings": sys.getunicodeinternedsize(),
    }
    snapshot.update(_thread_cycle_us(thread_samples))
    return snapshot


def _collections_total() -> int:
    """Return the interpreter's cumulative collection count over all generations."""
    return sum(int(stats.get("collections", 0)) for stats in gc.get_stats())


def _summary_ms(summary: Any) -> Dict[str, float]:
    """
    Flatten one harness `_Summary` into milliseconds.

    Args:
        summary: A `_Summary` from the harness.

    Returns:
        Dict[str, float]: total, avg, median, p95, p99, max in ms and cv.
    """
    return {
        "total": summary.total_ns / 1e6,
        "avg": summary.avg_ns / 1e6,
        "median": summary.median_ns / 1e6,
        "p95": summary.p95_ns / 1e6,
        "p99": summary.p99_ns / 1e6,
        "max": summary.max_ns / 1e6,
        "cv": summary.cv,
    }


def _record(result: Any) -> Dict[str, Any]:
    """
    Extract the numbers this probe compares from one `_BenchmarkResult`.

    Args:
        result: The harness result for one library.

    Returns:
        Dict[str, Any]: setup, cleanup, iteration/threaded/bootstrap summaries,
            throughput and per-lane active rates.
    """
    lanes: Dict[str, Dict[str, float]] = {}
    for name, lane in result.lane_summaries.items():
        lanes[name] = {
            "active_cycles_per_s": lane.active_cycles_per_s,
            "outer_total_avg_ms": lane.outer_total_summary.avg_ns / 1e6,
            "request_total_avg_ms": lane.request_total_summary.avg_ns / 1e6,
        }
    return {
        "setup_ms": result.setup_ns / 1e6,
        "cleanup_ms": result.cleanup_ns / 1e6,
        "iteration": _summary_ms(result.iteration_summary),
        "threaded": _summary_ms(result.threaded_summary),
        "bootstrap": _summary_ms(result.bootstrap_summary),
        "hot_scopes_per_s": result.hot_scope_cycles_per_s,
        "lanes": lanes,
    }


def main() -> int:
    """
    Run one order in this process and append one JSON line per library.

    Returns:
        int: 0 on success; harness errors propagate.
    """
    args = _parse_args()
    gauntlet = _import_harness(args.repo_root.resolve())
    cfg = gauntlet._GauntletConfig.from_env()
    order = [name.strip() for name in args.order.split(",") if name.strip()]
    main_tid = threading.get_ident()
    tid_check = [0]
    header_matches = _ob_tid(tid_check) == main_tid
    for position, lib in enumerate(order, start=1):
        before: Dict[str, Any] = {}
        if args.state_probe:
            before = _state_snapshot(main_tid, args.thread_samples)
        collections_before = _collections_total()
        wall_t0 = time.perf_counter_ns()
        result = gauntlet._run_gauntlet_benchmark(lib, cfg)
        wall_ms = (time.perf_counter_ns() - wall_t0) / 1e6
        row: Dict[str, Any] = {
            "run_tag": args.run_tag,
            "order": ",".join(order),
            "position": position,
            "lib": lib,
            "iterations": cfg.iterations,
            "threads": cfg.threads,
            "pid": os.getpid(),
            "gil_enabled": sys._is_gil_enabled(),
            "ob_tid_matches_main": header_matches,
            "state_probe": args.state_probe,
            "before": before,
            "collections_during_call": _collections_total() - collections_before,
            "wall_ms": wall_ms,
        }
        row.update(_record(result))
        with args.out.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")
        print(
            f"{args.run_tag} {row['order']} pos={position} {lib}: "
            f"total={row['iteration']['total']:.1f}ms "
            f"thr_avg={row['threaded']['avg']:.3f}ms setup={row['setup_ms']:.1f}ms "
            f"coll={row['collections_during_call']} before={before}",
            flush=True,
        )
    if args.state_probe:
        final = _state_snapshot(main_tid, args.thread_samples)
        with args.out.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"run_tag": args.run_tag, "order": ",".join(order), "position": len(order) + 1,
                                     "lib": "(end)", "before": final}) + "\n")
        print(f"{args.run_tag} {','.join(order)} end: {final}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
