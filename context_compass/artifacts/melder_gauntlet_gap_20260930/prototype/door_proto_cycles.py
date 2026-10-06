"""
Per-cycle CPU A/B of the top-level door overlay on warm Melder scope cycles (melder_0, 2026-09-30).

Purpose:
    The gauntlet's totals are too noisy on a 2-vCPU VM to resolve a lever of well under 1 us per scope cycle. This
    measures the scope cycle itself: after the harness's own warm-up, each lane's scope cycle runs on a fresh
    worker thread (solo), then all three lanes run at once on three fresh threads (concurrent); each thread reports
    its own CPU time (time.thread_time_ns) and wall time per cycle. Base and proto run in fresh processes,
    shuffled per round.

Usage (parent):
    python door_proto_cycles.py --repo-root <melder_private> [--rounds 8] [--cycles 3000] [--seed 1]
        [--out door_proto_cycles.jsonl]

Contract:
    - Uses the harness's `_build_ops("melder")`, `spawn_singletons` and 20 `_run_gauntlet_once` iterations as
      warm-up; the measured calls are the harness's own `request/worker_a/worker_b_scope_cycle` with variants
      cycling 0, 1, 2. Variant "proto" installs `door_proto` before anything is built.
    - Appends one JSON line per run; prints medians and proto/base ratios at the end. Changes nothing on disk
      except --out. On Windows thread_time ticks are coarse, so read the wall numbers of the solo phase there.
"""
import argparse
import json
import random
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def _run_lane(call: Callable[[int], Any], cycles: int, result: Dict[str, float], barrier: Any) -> None:
    """
    Thread body: run `cycles` scope cycles and store CPU and wall nanoseconds per cycle.

    Args:
        call: One lane's scope-cycle callable.
        cycles: Number of cycles.
        result: Dict that receives cpu_ns and wall_ns per cycle.
        barrier: Optional barrier to start several lanes together.
    """
    if barrier is not None:
        barrier.wait()
    cpu0 = time.thread_time_ns()
    wall0 = time.perf_counter_ns()
    for ix in range(cycles):
        call(ix % 3)
    result["wall_ns"] = (time.perf_counter_ns() - wall0) / cycles
    result["cpu_ns"] = (time.thread_time_ns() - cpu0) / cycles


def _child(repo_root: Path, variant: str, run_tag: str, cycles: int, out: Path) -> int:
    """
    Build and warm Melder (optionally with the overlay), then time solo and concurrent lanes.

    Args:
        repo_root: Tree holding `benchmarks/` and `src/`.
        variant: "base" or "proto".
        run_tag: Label stored with the row.
        cycles: Cycles per lane per phase.
        out: JSONL file to append to.

    Returns:
        int: 0.
    """
    for path in (repo_root, repo_root / "src", Path(__file__).resolve().parent):
        sys.path.insert(0, str(path))
    if variant == "proto":
        import door_proto
        door_proto.install(door_proto.door_module())
    import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet
    cfg = gauntlet._GauntletConfig.from_env()
    ops = gauntlet._build_ops("melder")
    lanes = {
        "request": ops.request_scope_cycle,
        "worker_a": ops.worker_a_scope_cycle,
        "worker_b": ops.worker_b_scope_cycle,
    }
    row: Dict[str, Any] = {"run_tag": run_tag, "variant": variant, "cycles": cycles, "solo": {}, "concurrent": {}}
    try:
        ops.spawn_singletons()
        for ix in range(20):
            gauntlet._run_gauntlet_once(ops, cfg, ix)
        for name, call in lanes.items():
            result: Dict[str, float] = {}
            thread = threading.Thread(target=_run_lane, args=(call, cycles, result, None))
            thread.start()
            thread.join()
            row["solo"][name] = result
        barrier = threading.Barrier(len(lanes))
        results = {name: {} for name in lanes}
        threads = [threading.Thread(target=_run_lane, args=(call, cycles, results[name], barrier))
                   for name, call in lanes.items()]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        row["concurrent"] = results
    finally:
        ops.cleanup()
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    return 0


def _summary(out: Path, tags: List[str]) -> None:
    """
    Print per-lane medians (CPU and wall ns per cycle) per variant and the proto/base ratios.

    Args:
        out: The JSONL file.
        tags: Run tags written by this invocation.
    """
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [row for row in rows if row["run_tag"] in tags]
    by_variant: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        by_variant.setdefault(row["variant"], []).append(row)
    lanes = ("request", "worker_a", "worker_b")
    medians: Dict[str, Dict[str, float]] = {}
    for variant, vrows in by_variant.items():
        medians[variant] = {}
        for phase in ("solo", "concurrent"):
            for lane in lanes:
                for metric in ("cpu_ns", "wall_ns"):
                    key = f"{phase}.{lane}.{metric}"
                    medians[variant][key] = statistics.median(row[phase][lane][metric] for row in vrows)
    print("\nmedian ns per scope cycle (runs: " + ", ".join(f"{k}={len(v)}" for k, v in by_variant.items()) + ")")
    for key in sorted(next(iter(medians.values())).keys()):
        line = f"  {key:<28}" + "".join(f" {variant}={medians[variant][key]:9.0f}" for variant in medians)
        if "base" in medians and "proto" in medians:
            line += f"  proto/base={medians['proto'][key] / medians['base'][key]:.4f}"
        print(line)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Parent: shuffled rounds of base and proto children, then the summary. Child (--child): one run.

    Args:
        argv: Command line (defaults to sys.argv[1:]).

    Returns:
        int: 0, or the exit code of the first failing child.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path("door_proto_cycles.jsonl"))
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument("--cycles", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--round-offset", type=int, default=0)
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--variant", default="base")
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    if args.child:
        return _child(repo_root, args.variant, args.run_tag, args.cycles, args.out)
    rng = random.Random(args.seed)
    tags: List[str] = []
    for round_ix in range(args.rounds):
        order = ["base", "proto"]
        rng.shuffle(order)
        for variant in order:
            tag = f"c{round_ix + 1 + args.round_offset}.{variant}"
            command = [sys.executable, "-X", "gil=0", str(Path(__file__).resolve()), "--child", "--variant", variant,
                       "--run-tag", tag, "--repo-root", str(repo_root), "--out", str(args.out.resolve()),
                       "--cycles", str(args.cycles)]
            t0 = time.perf_counter()
            done = subprocess.run(command, capture_output=True, text=True, check=False)
            if done.returncode != 0:
                print(done.stdout[-3000:], done.stderr[-3000:])
                return done.returncode
            tags.append(tag)
            row = json.loads(args.out.read_text(encoding="utf-8").splitlines()[-1])
            solo = " ".join(f"{lane}={row['solo'][lane]['cpu_ns']:.0f}" for lane in row["solo"])
            print(f"# {time.perf_counter() - t0:5.1f}s {tag:<10} solo cpu ns/cycle: {solo}", flush=True)
    _summary(args.out.resolve(), tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
