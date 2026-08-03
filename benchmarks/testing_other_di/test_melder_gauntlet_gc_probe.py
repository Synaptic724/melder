"""
GC-isolation wrapper for the Melder gauntlet cache investigation.

Purpose:
    The cache-on gauntlet run shows a systematic ~+100us/iteration wall gap
    while active-cycle throughput and every measured scope segment stay
    EQUAL, and the seam-counter parity probe shows zero warm-leg cache/
    rebuild seam activity. The remaining suspect is automatic GC: on the
    free-threaded build each collection scans the full tracked heap, and a
    warm-cache run keeps the entire marshal-decoded cache bundle (plus the
    per-spell manifests referenced by the lazy-door closures) alive for the
    whole run - thousands of extra tracked objects fattening every pass.

Method:
    Run the UNMODIFIED gauntlet with automatic GC disabled for the duration
    (cycle collection off; refcounting still frees acyclic garbage). Compare
    cache-on vs cache-off pairs of THIS test:
      - If the pair equalizes with GC off, the regression is GC heap-size
        cost from retained cache payloads -> fix is releasing the decoded
        bundle after the conjure load boundary.
      - If the gap survives with GC off, GC is exonerated and the delta
        lives in the runtime path after all.

    A gc.get_stats() delta is printed as corroborating evidence when GC is
    left ON via the env knob.

Usage (same cache toggling as the normal gauntlet):
    pytest benchmarks/testing_other_di/test_melder_gauntlet_gc_probe.py -q -s
    MELDER_GC_PROBE_KEEP_GC=1 pytest ... (leave GC on, print stats delta)

This is a benchmark diagnostic surface, not production runtime code.
"""

import gc
import os
import sys
from pathlib import Path


def _ensure_local_paths() -> None:
    """
    Ensure local source and benchmark helper paths are importable.

    Contract:
        Mirrors the gauntlet module's own path setup so this wrapper can be
        run from the repository root or from this directory.
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import test_melder_gauntlet as _gauntlet


def test_melder_gauntlet_gc_isolated() -> None:
    """
    Run the unmodified gauntlet with cycle GC disabled (or stats-instrumented).

    Contract:
        - Default: gc.collect() once for a clean baseline, then gc.disable()
          for the whole benchmark; gc re-enabled in finally.
        - MELDER_GC_PROBE_KEEP_GC=1: leave GC enabled and print the
          gc.get_stats() collection/collected deltas instead, so a follow-up
          run can show HOW MANY collections ran and how much they scanned.
    """
    keep_gc = os.environ.get("MELDER_GC_PROBE_KEEP_GC") == "1"
    if keep_gc:
        stats_before = gc.get_stats()
        _gauntlet.test_melder_gauntlet()
        stats_after = gc.get_stats()
        for generation, (before, after) in enumerate(
                zip(stats_before, stats_after)
        ):
            collections = after["collections"] - before["collections"]
            collected = after["collected"] - before["collected"]
            print(f"[gc-probe] gen{generation}: collections={collections} "
                  f"collected={collected}")
        return

    gc.collect()
    gc.disable()
    try:
        print("[gc-probe] cycle GC DISABLED for this run")
        _gauntlet.test_melder_gauntlet()
    finally:
        gc.activate()
        gc.collect()


if __name__ == "__main__":
    test_melder_gauntlet_gc_isolated()
