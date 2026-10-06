"""
Worker-owned survivor census for the shared gauntlet (melder_0, 2026-09-30).

Purpose:
    After a library has run gauntlet iterations, list the GC-tracked objects that are still alive although a worker
    thread allocated them (object-header owner id `ob_tid` neither the main thread's nor 0). Such survivors keep
    exited threads' allocator pages alive, which is where the thread-lifecycle probes point.

Usage:
    python -X gil=0 worker_owned_census.py --repo-root <tree> --lib melder [--iterations 50] [--top 30]

Contract:
    - Reads object headers through ctypes (diagnostic only); changes nothing on disk.
    - Prints the totals (main-owned, merged, other-owned) and the top types among other-owned survivors.
"""
import argparse
import collections
import ctypes
import gc
import importlib
import sys
import threading
from pathlib import Path


def _ob_tid(obj: object) -> int:
    """
    Read the owning-thread id from a free-threaded object header.

    Args:
        obj: Any live object.

    Returns:
        int: The header's first word.
    """
    return ctypes.c_size_t.from_address(id(obj)).value


def main() -> int:
    """
    Run the library for some iterations, then count survivors by owner and type.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--lib", required=True)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src"):
        sys.path.insert(0, str(path))
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops(args.lib)
    ops.spawn_singletons()
    for ix in range(args.iterations):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    gc.collect()
    main_tid = _ob_tid([0])
    counts = collections.Counter()
    other = collections.Counter()
    tids = set()
    for obj in gc.get_objects():
        tid = _ob_tid(obj)
        if tid == main_tid:
            counts["main"] += 1
        elif tid == 0:
            counts["zero"] += 1
        else:
            counts["other"] += 1
            tids.add(tid)
            kind = type(obj)
            other[f"{kind.__module__}.{kind.__qualname__}"] += 1
    print(f"{args.lib}: iterations={args.iterations} main={counts['main']} zero={counts['zero']} "
          f"other={counts['other']} other_tids={len(tids)} live_threads={threading.active_count()}")
    for name, count in other.most_common(args.top):
        print(f"  {count:6d}  {name}")
    ops.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
