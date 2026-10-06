"""
Run one interleaved round of the order matrix, one fresh process per configuration.

Purpose:
    Drive `order_probe.py` over every permutation of the three libraries plus each
    library alone, in a shuffled order per round, so drift over the session spreads
    across configurations instead of landing on one position.

Usage:
    python run_matrix.py --repo-root <tree> --python <interpreter> --round r1 \
        --seed 1 --out results.jsonl [--state-probe] [--configs a,b,c;d]

Contract:
    - Each configuration runs in its own `-X gil=0` subprocess; this launcher does
      no measuring itself.
    - The harness configuration comes from the inherited environment
      (`DI_GAUNTLET_ITERS`, ...).
    - Stops at the first failing configuration and returns its exit code.
"""
import argparse
import itertools
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import List


def _configs(explicit: str) -> List[str]:
    """
    Return the configurations to run: explicit ones, or all orders plus singles.

    Args:
        explicit: Semicolon-separated orders, or "" for the default matrix.

    Returns:
        List[str]: Comma-joined library orders.
    """
    if explicit:
        return [item for item in explicit.split(";") if item]
    libs = ("dependency-injector", "dishka", "melder")
    orders = [",".join(perm) for perm in itertools.permutations(libs)]
    return orders + list(libs)


def main() -> int:
    """
    Run one shuffled round.

    Returns:
        int: 0, or the exit code of the first failing configuration.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--python", required=True)
    parser.add_argument("--round", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--state-probe", action="store_true")
    parser.add_argument("--configs", default="")
    args = parser.parse_args()
    configs = _configs(args.configs)
    random.Random(args.seed).shuffle(configs)
    probe = Path(__file__).resolve().with_name("order_probe.py")
    for index, order in enumerate(configs, start=1):
        command = [
            args.python, "-X", "gil=0", str(probe),
            "--repo-root", str(args.repo_root),
            "--order", order,
            "--run-tag", f"{args.round}.{index}",
            "--out", str(args.out),
        ]
        if args.state_probe:
            command.append("--state-probe")
        t0 = time.perf_counter()
        completed = subprocess.run(command, check=False)
        print(f"# {args.round}.{index} {order} rc={completed.returncode} {time.perf_counter() - t0:.1f}s", flush=True)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
