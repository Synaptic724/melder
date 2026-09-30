"""
Thread-lifecycle state probe: at which setup stage does a library's process make thread start+join slower?
(melder_0, 2026-09-30)

Purpose:
    The shared gauntlet starts three threads per iteration, and in Melder's process a no-op thread start+join
    costs about three times what it costs in a bare interpreter (VM). This probe times sequential start+join
    cycles of a no-op thread after each setup stage of one library, in one process, to find the stage that
    raises it.

Usage:
    python -X gil=0 thread_state_probe.py --repo-root <tree> --lib melder --out stages.jsonl [--samples 200]
        [--loop 1000]

Stages (in order): bare, harness_import, library_import, build_ops (bind + conjure or container build),
warm_50 (singletons + 50 harness iterations), loop_N (N more harness iterations), after_gc (gc.collect()).

Contract:
    - One JSON line per stage with the median and p90 microseconds and the GC-tracked object count.
    - Uses the harness's own `_build_ops` and `_run_gauntlet_once`; changes nothing on disk except --out.
"""
import argparse
import gc
import importlib
import json
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List


def _noop() -> None:
    """Thread body: does nothing."""
    return None


def _cycle(samples: int) -> Dict[str, float]:
    """
    Time sequential start+join cycles of a no-op thread.

    Args:
        samples: Number of cycles.

    Returns:
        Dict[str, float]: median_us and p90_us.
    """
    out: List[float] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        out.append((time.perf_counter_ns() - t0) / 1000.0)
    out.sort()
    return {"median_us": statistics.median(out), "p90_us": out[int(len(out) * 0.9)]}


def main() -> int:
    """
    Walk the stages and append one JSON line per stage.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--lib", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--loop", type=int, default=1000)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    rows: List[Dict[str, Any]] = []

    def stage(name: str) -> None:
        """Record one stage."""
        row = {"tag": args.tag, "lib": args.lib, "stage": name, "gc_objects": len(gc.get_objects())}
        row.update(_cycle(args.samples))
        rows.append(row)
        print(f"{args.lib:<7} {name:<15} median={row['median_us']:7.1f}us p90={row['p90_us']:7.1f}us "
              f"gc_objects={row['gc_objects']}", flush=True)

    _cycle(30)
    stage("bare")
    root = args.repo_root.resolve()
    for path in (root, root / "src"):
        sys.path.insert(0, str(path))
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    stage("harness_import")
    importlib.import_module("melder" if args.lib == "melder" else args.lib.replace("-", "_"))
    stage("library_import")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops(args.lib)
    stage("build_ops")
    ops.spawn_singletons()
    for ix in range(50):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    stage("warm_50")
    for ix in range(args.loop):
        gauntlet._run_gauntlet_once(ops, cfg, 50 + ix)
    stage(f"loop_{args.loop}")
    gc.collect()
    stage("after_gc")
    ops.cleanup()
    with args.out.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
