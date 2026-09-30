"""
Gap probe: where a shared-gauntlet iteration spends its time outside the timed scope cycles (melder_0, 2026-09-30).

Purpose:
    The harness times each scope cycle (outer_total) but not the thread start, the wake-up after the start event,
    the per-cycle bookkeeping between cycles, or the thread exit and join. This probe runs the harness's own ops
    for one library and repeats `_run_gauntlet_once` with extra timestamps, so each of those parts gets a number.

Usage:
    python -X gil=0 gap_probe.py --repo-root <tree> --lib melder --run-tag g1 --out gap.jsonl \
        [--iterations 3000] [--warmup 50] [--thread-samples 200]

Contract:
    - The measured iteration mirrors `test_real_world_gauntlet._run_gauntlet_once` line for line (same lanes,
      reps, seeds, barrier and event); the only additions are perf_counter_ns reads into preallocated slots.
    - Warm-up iterations run through the harness's own `_run_gauntlet_once` and are not recorded.
    - Before and after the measured loop it times `--thread-samples` sequential start+join cycles of a no-op thread.
    - Appends one JSON object to --out and prints a one-line summary. Reads lane sizes from the harness's env.
"""
import argparse
import json
import random
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List


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


def _noop() -> None:
    """Thread body for the start+join probe: does nothing."""
    return None


def _thread_cycle_us(samples: int) -> float:
    """
    Time `samples` sequential start+join cycles of no-op threads.

    Args:
        samples: Number of threads to start and join, one at a time.

    Returns:
        float: Median microseconds per start+join cycle.
    """
    durations: List[int] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        durations.append(time.perf_counter_ns() - t0)
    return statistics.median(durations) / 1000.0


def _instrumented_once(gauntlet: Any, ops: Any, cfg: Any, iteration_ix: int) -> Dict[str, Any]:
    """
    Run one gauntlet iteration exactly like `_run_gauntlet_once`, with timestamps around every part.

    Args:
        gauntlet: The harness module (for its constants and metric helpers).
        ops: The library's `_RuntimeOps`.
        cfg: The harness `_GauntletConfig`.
        iteration_ix: Iteration index (feeds the lane seeds, as in the harness).

    Returns:
        Dict[str, Any]: Per-part nanoseconds for this iteration: bootstrap, thread start (pre-barrier), threaded
            window, and per lane the wake-up, cycle calls, outer_total sum, bookkeeping and end offset.
    """
    t0 = time.perf_counter_ns()
    ops.bootstrap_fanout()
    bootstrap_end = time.perf_counter_ns()
    lane_counts = {"request": 0, "worker_a": 0, "worker_b": 0}
    lane_metrics = {name: gauntlet._new_lane_metric_samples() for name in ("request", "worker_a", "worker_b")}
    lane_variant_counts = {name: [0] * gauntlet._VARIANT_COUNT for name in ("request", "worker_a", "worker_b")}
    errors: List[BaseException] = []
    stop_event = threading.Event()
    active_lanes = [("request", ops.request_scope_cycle, cfg.request_scope_runs, 17)]
    if cfg.threads >= 2:
        active_lanes.append(("worker_a", ops.worker_a_scope_cycle, cfg.worker_a_jobs, 29))
    if cfg.threads >= 3:
        active_lanes.append(("worker_b", ops.worker_b_scope_cycle, cfg.worker_b_jobs, 41))
    ready_barrier = threading.Barrier(len(active_lanes) + 1)
    start_event = threading.Event()
    marks: Dict[str, List[int]] = {name: [0, 0, 0, 0] for name, _, _, _ in active_lanes}

    def make_worker(name: str, call: Any, reps: int, seed_offset: int) -> Any:
        def worker() -> None:
            lane_marks = marks[name]
            calls_ns = 0
            try:
                rng = random.Random(gauntlet._LIB_SEEDS[ops.name] + iteration_ix * 101 + seed_offset)
                ready_barrier.wait()
                start_event.wait()
                lane_marks[0] = time.perf_counter_ns()
                for _ in range(reps):
                    if stop_event.is_set():
                        return
                    variant = rng.randrange(gauntlet._VARIANT_COUNT)
                    c0 = time.perf_counter_ns()
                    metrics = call(variant)
                    calls_ns += time.perf_counter_ns() - c0
                    lane_metrics[name].outer_create_ns.append(metrics.outer_create_ns)
                    lane_metrics[name].outer_cleanup_ns.append(metrics.outer_cleanup_ns)
                    lane_metrics[name].outer_total_ns.append(metrics.outer_total_ns)
                    lane_metrics[name].request_create_ns.append(metrics.request_create_ns)
                    lane_metrics[name].request_cleanup_ns.append(metrics.request_cleanup_ns)
                    lane_metrics[name].request_total_ns.append(metrics.request_total_ns)
                    lane_counts[name] += 1
                    lane_variant_counts[name][variant] += 1
                lane_marks[1] = time.perf_counter_ns()
                lane_marks[2] = calls_ns
            except BaseException as exc:
                errors.append(exc)
                stop_event.set()

        return worker

    threads_list: List[threading.Thread] = []
    for lane_name, lane_call, reps, seed_offset in active_lanes:
        t = threading.Thread(target=make_worker(lane_name, lane_call, reps, seed_offset), daemon=True)
        threads_list.append(t)
        t.start()
    started = time.perf_counter_ns()
    ready_barrier.wait()
    threaded_t0 = time.perf_counter_ns()
    start_event.set()
    for t in threads_list:
        t.join()
    threaded_end = time.perf_counter_ns()
    if errors:
        raise errors[0]
    row: Dict[str, Any] = {
        "bootstrap": bootstrap_end - t0,
        "create_start": started - bootstrap_end,
        "barrier": threaded_t0 - started,
        "threaded": threaded_end - threaded_t0,
        "total": threaded_end - t0,
    }
    last_end = max(marks[name][1] for name in marks)
    for name, lane_marks in marks.items():
        outer_sum = sum(lane_metrics[name].outer_total_ns)
        span = lane_marks[1] - lane_marks[0]
        row[name] = {
            "wake": lane_marks[0] - threaded_t0,
            "calls": lane_marks[2],
            "outer": outer_sum,
            "in_call_outside_outer": lane_marks[2] - outer_sum,
            "bookkeeping": span - lane_marks[2],
            "end_offset": threaded_end - lane_marks[1],
            "is_last": lane_marks[1] == last_end,
        }
    return row


def _mean(rows: List[Dict[str, Any]], *path: str) -> float:
    """
    Mean of one numeric field over all rows, in microseconds.

    Args:
        rows: Per-iteration rows from `_instrumented_once`.
        path: Keys leading to the field.

    Returns:
        float: Mean value / 1000.
    """
    values = []
    for row in rows:
        value: Any = row
        for key in path:
            value = value[key]
        values.append(value)
    return statistics.fmean(values) / 1000.0


def main() -> int:
    """
    Build one library, warm it, time the instrumented loop and append one summary line.

    Returns:
        int: 0 on success; harness errors propagate.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--lib", required=True)
    parser.add_argument("--run-tag", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=3000)
    parser.add_argument("--warmup", type=int, default=50)
    parser.add_argument("--thread-samples", type=int, default=200)
    args = parser.parse_args()
    gauntlet = _import_harness(args.repo_root.resolve())
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops(args.lib)
    try:
        ops.spawn_singletons()
        for ix in range(args.warmup):
            gauntlet._run_gauntlet_once(ops, cfg, ix)
        thread_before = _thread_cycle_us(args.thread_samples)
        rows = [_instrumented_once(gauntlet, ops, cfg, args.warmup + ix) for ix in range(args.iterations)]
        thread_after = _thread_cycle_us(args.thread_samples)
    finally:
        ops.cleanup()
    lanes = [name for name in ("request", "worker_a", "worker_b") if name in rows[0]]
    summary: Dict[str, Any] = {
        "run_tag": args.run_tag,
        "lib": args.lib,
        "iterations": args.iterations,
        "thread_cycle_us_before": thread_before,
        "thread_cycle_us_after": thread_after,
        "us": {key: _mean(rows, key) for key in ("bootstrap", "create_start", "barrier", "threaded", "total")},
        "lanes_us": {
            name: {key: _mean(rows, name, key) for key in
                   ("wake", "calls", "outer", "in_call_outside_outer", "bookkeeping", "end_offset")}
            for name in lanes
        },
        "last_lane_share": {name: sum(1 for row in rows if row[name]["is_last"]) / len(rows) for name in lanes},
    }
    with args.out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary) + "\n")
    us = summary["us"]
    print(f"{args.run_tag} {args.lib}: total={us['total']:.1f}us create_start={us['create_start']:.1f} "
          f"barrier={us['barrier']:.1f} threaded={us['threaded']:.1f} thread_cycle={thread_before:.1f}->"
          f"{thread_after:.1f}us", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
