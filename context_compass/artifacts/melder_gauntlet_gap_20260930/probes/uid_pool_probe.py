"""
Unique-id pool probe: does a free-threaded thread's start+join cost grow with the number of live code objects,
heap types and globals dicts in the process? (melder_0, 2026-09-30)

Purpose:
    CPython 3.14t gives heap types, code objects and globals dicts a unique id for per-thread refcounting; each
    thread keeps a refcount array indexed by that id (pycore_object.h `_Py_THREAD_INCREF_OBJECT`) and merges it
    back when it exits. This probe grows the number of id-holding objects in a bare interpreter in steps and
    times sequential start+join cycles of a no-op thread after each step.

Usage:
    python -X gil=0 uid_pool_probe.py [--steps 0,5000,20000,60000,150000] [--kind code|type|dict] [--samples 300]

Contract:
    - Keeps every created object alive until exit; prints one line per step (objects, median and p90 us).
"""
import argparse
import statistics
import threading
import time
from typing import Any, List


def _noop() -> None:
    """Thread body: does nothing."""
    return None


def _cycle_us(samples: int) -> List[float]:
    """
    Time sequential start+join cycles of a no-op thread.

    Args:
        samples: Number of cycles.

    Returns:
        List[float]: Microseconds per cycle.
    """
    out: List[float] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        out.append((time.perf_counter_ns() - t0) / 1000.0)
    return out


def _make(kind: str, index: int, template: Any) -> Any:
    """
    Create one id-holding object of the requested kind.

    Args:
        kind: "code" (a new code object), "type" (a heap type) or "dict" (a function with its own globals dict).
        index: Distinguishes the object.
        template: A code object to copy for kind "code".

    Returns:
        Any: The object to keep alive.
    """
    if kind == "code":
        return template.replace(co_name=f"f{index}")
    if kind == "type":
        return type(f"C{index}", (), {})
    namespace: dict = {}
    exec("def f():\n    return 1\n", namespace)
    return namespace["f"]


def main() -> int:
    """
    Grow the population in steps and time thread cycles after each step.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", default="0,5000,20000,60000,150000")
    parser.add_argument("--kind", default="code", choices=("code", "type", "dict"))
    parser.add_argument("--samples", type=int, default=300)
    args = parser.parse_args()
    template = (lambda: 1).__code__
    keep: List[Any] = []
    _cycle_us(50)
    for target in [int(value) for value in args.steps.split(",")]:
        while len(keep) < target:
            keep.append(_make(args.kind, len(keep), template))
        durations = sorted(_cycle_us(args.samples))
        p90 = durations[int(len(durations) * 0.9)]
        print(f"kind={args.kind} objects={len(keep):>7} median={statistics.median(durations):8.1f}us "
              f"p90={p90:8.1f}us", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
