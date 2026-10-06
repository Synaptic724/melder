"""
Operation residue probe: which Melder scope operation, run on short-lived worker threads, makes later thread
start+join slower? (melder_0, 2026-09-30)

Purpose:
    After the gauntlet workload runs, a no-op thread's start+join costs about 3x a bare interpreter's in the VM,
    and more after Melder than after dishka. This probe runs one partial Melder scope cycle per variant on three new
    threads per iteration (the gauntlet's thread shape), then times sequential no-op thread start+join cycles.

Variants (each adds to the previous):
    idle      - the three threads do nothing
    lesser    - create_lesser_conduit() then cleanup()
    outer     - lesser plus two melds of the outer (unique_per_conduit) spell
    space     - outer plus `with lesser.enter_spellspace():` doing nothing
    request   - space plus the request marker and root melds (the harness request cycle without its checks)
    harness   - the harness's own request/worker cycles (ops.*_scope_cycle)

Usage:
    python -X gil=0 op_residue_probe.py --repo-root <tree> --variant outer [--iterations 50] [--cycles 20]

Contract:
    - Builds Melder through the harness's `_build_runtime_melder` (identical setup) and reads its conduit and spell
      ids from the ops closures; prints one line with the variant and the median/p90 start+join microseconds.
"""
import argparse
import importlib
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List


def _noop() -> None:
    """Thread body: does nothing."""
    return None


def _cycle(samples: int) -> List[float]:
    """
    Time sequential start+join cycles of a no-op thread.

    Args:
        samples: Number of cycles.

    Returns:
        List[float]: Sorted microseconds per cycle.
    """
    out: List[float] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        out.append((time.perf_counter_ns() - t0) / 1000.0)
    return sorted(out)


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
    Build Melder, run the variant on gauntlet-shaped threads, then time no-op thread cycles.

    Returns:
        int: 0.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--variant", required=True,
                        choices=("idle", "lesser", "outer", "space", "request", "harness"))
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--cycles", type=int, default=20)
    parser.add_argument("--samples", type=int, default=200)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    for path in (root, root / "src"):
        sys.path.insert(0, str(path))
    gauntlet = importlib.import_module("benchmarks.testing_other_di.test_real_world_gauntlet")
    ops = gauntlet._build_ops("melder")
    ops.spawn_singletons()
    get_vars = _closure_vars(_closure_vars(ops.spawn_singletons)["_get"])
    conduit = get_vars["conduit"]
    spell_ids = get_vars["spell_ids"]
    outer_id = spell_ids[gauntlet.RequestSession]
    marker_id = spell_ids[gauntlet.RequestScopeMarker]
    root_id = spell_ids[gauntlet.RequestRoot]
    variant = args.variant

    def one_cycle(lane: int) -> None:
        """Run one partial scope cycle of the chosen variant."""
        if variant == "harness":
            (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle)[lane](lane % 3)
            return
        lesser = conduit.create_lesser_conduit()
        try:
            if variant in ("outer", "space", "request"):
                lesser.meld(spell_id=outer_id)
                lesser.meld(spell_id=outer_id)
            if variant in ("space", "request"):
                with lesser.enter_spellspace() as space:
                    if variant == "request":
                        space.meld(spell_id=marker_id)
                        space.meld(spell_id=marker_id)
                        space.meld(spell_id=outer_id)
                        space.meld(spell_id=root_id)
        finally:
            lesser.cleanup()

    def worker(lane: int) -> None:
        """Gauntlet-shaped worker: `--cycles` cycles, or nothing for `idle`."""
        if variant == "idle":
            return
        for _ in range(args.cycles):
            one_cycle(lane)

    before = _cycle(args.samples)
    for _ in range(args.iterations):
        threads = [threading.Thread(target=worker, args=(lane,)) for lane in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    after = _cycle(args.samples)
    print(f"variant={variant:<8} iterations={args.iterations} cycles={args.cycles} "
          f"before_median={statistics.median(before):7.1f}us after_median={statistics.median(after):7.1f}us "
          f"after_p90={after[int(len(after) * 0.9)]:7.1f}us", flush=True)
    ops.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
