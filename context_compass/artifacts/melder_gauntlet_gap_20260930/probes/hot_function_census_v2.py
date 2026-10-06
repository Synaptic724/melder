"""
Hot-function census: which functions run in one warm Melder scope cycle, and do they get CPython 3.14t's
automatic deferred reference counting? (melder_0, 2026-09-30; v2 adds --proto: install the top-level door overlay first)

Purpose:
    On free-threaded CPython a function object without deferred refcounting is incref'd and decref'd atomically by
    every thread that calls it; top-level functions (code without CO_NESTED) are deferred automatically, closures
    are not. This probe records every Python code object executed during warm scope cycles of the shared gauntlet
    (Melder lane) and reports, per code object, the calls per cycle, whether its function object is deferred, and
    whether its code is nested.

Usage:
    python -X gil=0 hot_function_census.py --repo-root <tree> [--cycles 50] [--proto --proto-dir <dir>]

Contract:
    - Diagnostic only: reads object headers through ctypes (ob_gc_bits at offset 11, bit 64 = deferred) and uses
      sys.setprofile on the main thread; changes nothing on disk.
"""
import argparse
import collections
import ctypes
import gc
import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict


def _deferred(obj: object) -> bool:
    """
    Report whether a free-threaded object has deferred reference counting.

    Args:
        obj: Any live object.

    Returns:
        bool: True when `_PyGC_BITS_DEFERRED` is set in `ob_gc_bits`.
    """
    return bool(ctypes.c_uint8.from_address(id(obj) + 11).value & 64)


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
    Warm the Melder lane, profile warm cycles, and print the census.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--cycles", type=int, default=50)
    parser.add_argument("--proto", action="store_true")
    parser.add_argument("--proto-dir", type=Path, default=Path(__file__).resolve().parent / "proto")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src"):
        sys.path.insert(0, str(path))
    if args.proto:
        sys.path.insert(0, str(args.proto_dir.resolve()))
        import door_proto
        door_proto.install(door_proto.door_module())
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops("melder")
    ops.spawn_singletons()
    for ix in range(20):
        gauntlet._run_gauntlet_once(ops, cfg, ix)
    calls: collections.Counter = collections.Counter()
    harness_file = gauntlet.__file__

    def profiler(frame: Any, event: str, arg: Any) -> None:
        """Count Python-level calls by code object."""
        if event == "call":
            calls[frame.f_code] += 1

    lanes = (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle)
    sys.setprofile(profiler)
    try:
        for ix in range(args.cycles):
            for lane in lanes:
                lane(ix % 3)
    finally:
        sys.setprofile(None)
    cycles = args.cycles * len(lanes)
    rows = []
    for code, count in calls.items():
        if code.co_filename == harness_file:
            continue
        functions = [ref for ref in gc.get_referrers(code) if inspect.isfunction(ref)]
        deferred = [_deferred(fn) for fn in functions]
        nested = bool(code.co_flags & inspect.CO_NESTED)
        rows.append((count / cycles, code.co_qualname, Path(code.co_filename).name, nested,
                     len(functions), sum(deferred), bool(code.co_freevars)))
    rows.sort(reverse=True)
    total = sum(row[0] for row in rows)
    not_deferred = sum(row[0] for row in rows if row[4] and row[5] < row[4])
    print(f"python-level calls per scope cycle (non-harness): {total:.1f}; to non-deferred functions: {not_deferred:.1f}")
    print(f"{'per_cycle':>9} {'nested':>6} {'fns':>3} {'defer':>5} {'cells':>5}  qualname (file)")
    for per_cycle, qualname, filename, nested, fns, deferred_count, cells in rows[:45]:
        print(f"{per_cycle:9.2f} {str(nested):>6} {fns:3d} {deferred_count:5d} {str(cells):>5}  {qualname} ({filename})")
    ops.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
