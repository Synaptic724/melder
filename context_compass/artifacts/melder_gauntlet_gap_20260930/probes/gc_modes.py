"""
GC-mode A/B for the shared gauntlet (melder_0, 2026-09-30).

Purpose:
    Size garbage collection's share of each library's gauntlet loop by running the harness's own runner once per
    (library, GC mode) in fresh processes, with the harness's GC probe on. Modes are the harness's own
    GAUNTLET_GC_MODE values: normal, disabled (gc.disable() around the loop) and frozen (gc.collect() then
    gc.freeze() after setup, so the setup heap is left out of collections).

Usage:
    python gc_modes.py --tree <repo> --out <log> --rounds 2 --seed 7 --libs melder,dishka --modes normal,disabled,frozen

Contract:
    - Every run is `python -X gil=0 benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py --lib L` with
      GAUNTLET_GC_PROBE=1 and GAUNTLET_GC_MODE=M added to the inherited environment (DI_GAUNTLET_ITERS etc.).
    - Appends the run's `[lib] gc probe`, `gauntlet config`, `gauntlet total` and `threaded phase` lines, prefixed
      with `round=R mode=M`, to --out; prints one short line per run.
"""
import argparse
import os
import random
import subprocess
import sys
import time
from typing import List, Tuple


def main() -> int:
    """
    Run the shuffled (library, mode) grid.

    Returns:
        int: 0, or the exit code of the first failing run.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--round-offset", type=int, default=0)
    parser.add_argument("--libs", default="melder,dishka")
    parser.add_argument("--modes", default="normal,disabled,frozen")
    args = parser.parse_args()
    grid: List[Tuple[str, str]] = [
        (lib, mode) for lib in args.libs.split(",") for mode in args.modes.split(",")
    ]
    rng = random.Random(args.seed)
    keep = ("gc probe", "gauntlet config", "gauntlet total", "threaded phase")
    for round_ix in range(args.rounds):
        order = list(grid)
        rng.shuffle(order)
        for lib, mode in order:
            env = dict(os.environ, GAUNTLET_GC_PROBE="1", GAUNTLET_GC_MODE=mode)
            command = [sys.executable, "-X", "gil=0",
                       "benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py", "--lib", lib]
            t0 = time.perf_counter()
            done = subprocess.run(command, cwd=args.tree, env=env, capture_output=True, text=True, check=False)
            if done.returncode != 0:
                print(done.stdout[-2000:], done.stderr[-2000:])
                return done.returncode
            lines = [line for line in done.stdout.splitlines() if any(k in line for k in keep)]
            with open(args.out, "a", encoding="utf-8") as handle:
                for line in lines:
                    handle.write(f"round={round_ix + 1 + args.round_offset} mode={mode} {line}\n")
            total = next((line for line in lines if "gauntlet total" in line), "")
            print(f"# {time.perf_counter() - t0:5.1f}s {mode:<8} {total[:70]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
