"""
Big test for the elastic pool retention change (TASK-2026-10-12-make_kernel_pools_elastic).

melder_gauntlet at 20 threads pushed to a large iteration count (20 is the most the 0.2.8233 pools keep, so this is
the no-regression check), then a ladder past the 20 retained shells (24, 32, 48, 64 threads; the retention check).
Every run is a fresh interpreter through gauntlet_runner.py. Run it once before the code change (--phase before) and
once after it (--phase after) on the same machine, then compare.

Usage, from the repository root, on Python 3.14 free-threaded:
    python -X gil=0 context_compass/artifacts/elastic_pool_retention_20261012/big_test.py --phase before --out big_before.jsonl
    (land the change)
    python -X gil=0 context_compass/artifacts/elastic_pool_retention_20261012/big_test.py --phase after --out big_after.jsonl
    python context_compass/artifacts/elastic_pool_retention_20261012/summarize_runs.py big_before.jsonl big_after.jsonl
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List


def gauntlet_cycles_per_iteration(threads: int) -> int:
    """Scope cycles one gauntlet iteration runs at `threads` (request 10, worker A 25, worker B 30 per thread)."""
    if threads <= 3:
        return [10, 35, 65][threads - 1]
    num_req = threads // 3 + (1 if threads % 3 > 0 else 0)
    num_a = threads // 3 + (1 if threads % 3 > 1 else 0)
    num_b = threads // 3
    return num_req * 10 + num_a * 25 + num_b * 30


def main() -> int:
    """Run the matrix and return the first failing exit code, or 0."""
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["before", "after"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--tree", default=str(here.parents[2]), help="repository root (default: this checkout)")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--threads20", type=int, default=20)
    parser.add_argument("--iters20", type=int, default=8000, help="iterations per 20-thread run (raise to push it)")
    parser.add_argument("--ladder", default="24,32,48,64", help="thread counts past retention; empty to skip")
    parser.add_argument("--ladder-cycles", type=int, default=1_300_000, help="scope cycles per ladder run")
    args = parser.parse_args()

    prefix = "base" if args.phase == "before" else "cand"
    plan: List[tuple] = [(args.threads20, args.iters20)]
    for item in [x for x in args.ladder.split(",") if x.strip()]:
        threads = int(item)
        plan.append((threads, max(1, args.ladder_cycles // gauntlet_cycles_per_iteration(threads))))
    runner = here / "gauntlet_runner.py"
    for round_ix in range(1, args.rounds + 1):
        for threads, iters in plan:
            label = f"{prefix}_t{threads}_big{round_ix}"
            t0 = time.perf_counter()
            done = subprocess.run(
                [sys.executable, "-X", "gil=0", "-W", "ignore", str(runner), "--tree", args.tree,
                 "--iters", str(iters), "--threads", str(threads), "--label", label, "--out", args.out],
                stdout=subprocess.DEVNULL,
            )
            sys.stdout.write(f"{label}: {iters} iterations, {time.perf_counter() - t0:.1f} s, exit {done.returncode}\n")
            sys.stdout.flush()
            if done.returncode != 0:
                return done.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
