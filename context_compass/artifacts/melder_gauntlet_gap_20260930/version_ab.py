"""
Interleaved A/B of one library across source trees on the current gauntlet harness (melder_0, 2026-09-30).

Purpose:
    Measure whether Melder's gauntlet loop got slower or faster between versions, with one harness, one machine
    state and the order of runs shuffled per round so drift spreads across trees. A control library that does not
    depend on the tree (dishka) runs in every round to show machine drift.

Usage:
    python version_ab.py --probe <order_probe.py> --python <interpreter> --out results.jsonl --rounds 2 \
        --seed 1 --config v0274=<tree>:melder --config ctrl=<tree>:dishka

Contract:
    - Every run is a fresh `-X gil=0` process of order_probe.py with one library; the tag goes in the run tag.
    - The iteration count and other harness settings come from the inherited environment.
    - Stops at the first failing run and returns its exit code.
"""
import argparse
import random
import subprocess
import sys
import time
from typing import List, Tuple


def _parse_config(text: str) -> Tuple[str, str, str]:
    """
    Split `tag=tree:lib` into its parts.

    Args:
        text: One --config value.

    Returns:
        Tuple[str, str, str]: tag, tree path and library name.
    """
    tag, rest = text.split("=", 1)
    tree, lib = rest.rsplit(":", 1)
    return tag, tree, lib


def main() -> int:
    """
    Run the shuffled rounds.

    Returns:
        int: 0, or the exit code of the first failing run.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--round-prefix", default="r")
    parser.add_argument("--config", action="append", required=True)
    args = parser.parse_args()
    configs: List[Tuple[str, str, str]] = [_parse_config(item) for item in args.config]
    rng = random.Random(args.seed)
    for round_ix in range(args.rounds):
        order = list(configs)
        rng.shuffle(order)
        for tag, tree, lib in order:
            command = [
                args.python, "-X", "gil=0", args.probe,
                "--repo-root", tree, "--order", lib,
                "--run-tag", f"{args.round_prefix}{round_ix + 1}.{tag}", "--out", args.out,
            ]
            t0 = time.perf_counter()
            completed = subprocess.run(command, check=False, capture_output=True, text=True)
            line = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else completed.stderr[-300:]
            print(f"# {time.perf_counter() - t0:5.1f}s rc={completed.returncode} {line[:110]}", flush=True)
            if completed.returncode != 0:
                return completed.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
