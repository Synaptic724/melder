"""
Paired analysis of door_proto_cycles.py results (melder_0, 2026-09-30).

Purpose:
    Per round, base and proto ran back to back in fresh processes; pairing them removes most of the host drift.
    Prints, per phase and lane, the median and mean proto/base CPU ratio, the inter-quartile range, and in how many
    rounds proto was faster.

Usage:
    python door_proto_cycles_paired.py door_proto_cycles.jsonl [metric]   (metric: cpu_ns, the default, or wall_ns)
"""
import collections
import json
import statistics
import sys
from typing import Any, Dict, List


def main() -> int:
    """
    Print the paired ratios.

    Returns:
        int: 0.
    """
    path = sys.argv[1]
    metric = sys.argv[2] if len(sys.argv) > 2 else "cpu_ns"
    with open(path, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    by_round: Dict[str, Dict[str, Any]] = collections.defaultdict(dict)
    for row in rows:
        by_round[row["run_tag"].split(".")[0]][row["variant"]] = row
    pairs = [value for value in by_round.values() if "base" in value and "proto" in value]
    print(f"paired rounds: {len(pairs)} metric: {metric}")
    everything: List[float] = []
    for phase in ("solo", "concurrent"):
        for lane in ("request", "worker_a", "worker_b"):
            ratios = [pair["proto"][phase][lane][metric] / pair["base"][phase][lane][metric] for pair in pairs]
            everything.extend(ratios)
            quartiles = statistics.quantiles(ratios, n=4)
            faster = sum(1 for ratio in ratios if ratio < 1.0)
            print(f"{phase:<10} {lane:<8} proto/base median={statistics.median(ratios):.4f} "
                  f"mean={statistics.fmean(ratios):.4f} IQR=[{quartiles[0]:.3f},{quartiles[2]:.3f}] "
                  f"proto faster in {faster}/{len(ratios)}")
    faster_all = sum(1 for ratio in everything if ratio < 1.0)
    print(f"all phases and lanes: median={statistics.median(everything):.4f} mean={statistics.fmean(everything):.4f} "
          f"proto faster in {faster_all}/{len(everything)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
