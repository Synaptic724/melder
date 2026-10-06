"""
Diagnostic A/B: does it matter which thread first built Melder's pooled scope shells? (melder_0, 2026-09-30)

Purpose:
    The operation-residue probe showed later thread start+join costing more when pooled lesser shells were first
    built by short-lived worker threads (the gauntlet's own warm-up) than when the main thread built them. This
    probe measures that on the real harness loop: with `--prebuild N`, the main thread builds N lesser shells
    (each entering one SpellSpace, so its SpellSpace pool gets a shell) and returns them before the loop; without it
    the pools fill from the gauntlet's worker threads as they do in the benchmark. DIAGNOSTIC ONLY: prebuilding is
    not a proposed change (the owner ruled out prewarming); it locates where the cost comes from.

Usage:
    python -X gil=0 prewarm_ab_probe.py --repo-root <tree> --tag p1 --out ab.jsonl [--prebuild 6] [--warmup 50]
        [--iterations 2000] [--samples 200]

Contract:
    - Uses the harness's `_build_ops("melder")` and `_run_gauntlet_once`; the measured loop is the benchmark's.
    - Appends one JSON line: prebuild count, loop totals (ms), mean threaded window (us), no-op thread start+join
      medians (us) after warm-up and after the loop.
"""
import argparse
import importlib
import json
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List


def _noop() -> None:
    """Thread body: does nothing."""
    return None


def _cycle_median(samples: int) -> float:
    """
    Median microseconds of sequential no-op thread start+join cycles.

    Args:
        samples: Number of cycles.

    Returns:
        float: Median microseconds.
    """
    out: List[float] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        out.append((time.perf_counter_ns() - t0) / 1000.0)
    return statistics.median(out)


def _closure_vars(function: Callable[..., Any]) -> Dict[str, Any]:
    """
    Map a closure's free-variable names to their cell contents.

    Args:
        function: A nested function.

    Returns:
        Dict[str, Any]: name -> value.
    """
    names = function.__code__.co_freevars
    return {name: cell.cell_contents for name, cell in zip(names, function.__closure__ or ())}


def main() -> int:
    """
    Build Melder, optionally prebuild shells on the main thread, run the harness loop and record the numbers.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prebuild", type=int, default=0)
    parser.add_argument("--warmup", type=int, default=50)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--samples", type=int, default=200)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src"):
        sys.path.insert(0, str(path))
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops("melder")
    ops.spawn_singletons()
    conduit = _closure_vars(_closure_vars(ops.spawn_singletons)["_get"])["conduit"]
    if args.prebuild:
        shells = [conduit.create_lesser_conduit() for _ in range(args.prebuild)]
        for shell in shells:
            with shell.enter_spellspace():
                pass
        for shell in shells:
            shell.cleanup()
    for ix in range(args.warmup):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    thread_after_warmup = _cycle_median(args.samples)
    totals: List[int] = []
    threaded: List[int] = []
    for ix in range(args.iterations):
        result = gauntlet._run_gauntlet_once(ops, cfg, args.warmup + ix)
        totals.append(result.total_ns)
        threaded.append(result.threaded_ns)
    thread_after_loop = _cycle_median(args.samples)
    ops.cleanup()
    row = {
        "tag": args.tag,
        "prebuild": args.prebuild,
        "iterations": args.iterations,
        "loop_total_ms": sum(totals) / 1e6,
        "iteration_mean_us": statistics.fmean(totals) / 1000.0,
        "threaded_mean_us": statistics.fmean(threaded) / 1000.0,
        "thread_cycle_after_warmup_us": thread_after_warmup,
        "thread_cycle_after_loop_us": thread_after_loop,
    }
    with args.out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    print(f"{args.tag} prebuild={args.prebuild}: loop={row['loop_total_ms']:.1f}ms iter={row['iteration_mean_us']:.1f}us "
          f"threaded={row['threaded_mean_us']:.1f}us thread_cycle={thread_after_warmup:.1f}->{thread_after_loop:.1f}us",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
