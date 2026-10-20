"""
Summarize gauntlet_runner.py JSON lines: per thread count, base vs candidate, per round and mean.

Usage: python summarize_runs.py <runs.jsonl> [more.jsonl ...]
Labels are <tree>_t<threads>_<round>. Ratios are candidate / base (below 1.00 = candidate faster for times,
above 1.00 = candidate faster for throughput).
"""
import json
import statistics
import sys
from collections import defaultdict
from typing import Dict, List


def main() -> int:
    """Print one table per thread count and return 0."""
    rows: Dict[int, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                tree = record["label"].split("_")[0]
                rows[record["threads"]][tree].append(record)
    metrics = [
        ("scopes/s", lambda r: r["hot_scopes_per_s"]),
        ("iter median ms", lambda r: r["iteration"]["median_ms"]),
        ("iter p95 ms", lambda r: r["iteration"]["p95_ms"]),
        ("iter p99 ms", lambda r: r["iteration"]["p99_ms"]),
        ("iter avg ms", lambda r: r["iteration"]["avg_ms"]),
        ("outer create med us", lambda r: r["outer_create"]["median_ms"] * 1000),
        ("outer create p99 us", lambda r: r["outer_create"]["p99_ms"] * 1000),
        ("outer cleanup med us", lambda r: r["outer_cleanup"]["median_ms"] * 1000),
        ("outer cleanup p99 us", lambda r: r["outer_cleanup"]["p99_ms"] * 1000),
        ("request total med us", lambda r: r["request_total"]["median_ms"] * 1000),
    ]
    for threads in sorted(rows):
        base, cand = rows[threads]["base"], rows[threads]["cand"]
        iters = sorted({r["iters"] for r in base + cand})
        sys.stdout.write(f"\n== {threads} thread(s), iterations per run {iters}, runs base={len(base)} "
                         f"cand={len(cand)}\n")
        sys.stdout.write(f"{'metric':<22}{'base runs':<30}{'cand runs':<30}{'base mean':>11}{'cand mean':>11}"
                         f"{'cand/base':>10}\n")
        for name, read in metrics:
            b = [read(r) for r in base]
            c = [read(r) for r in cand]
            bm, cm = statistics.fmean(b), statistics.fmean(c)
            sys.stdout.write(f"{name:<22}{' '.join(f'{v:.4g}' for v in b):<30}{' '.join(f'{v:.4g}' for v in c):<30}"
                             f"{bm:>11.4g}{cm:>11.4g}{cm / bm:>10.3f}\n")
        pools = {tree: rows[threads][tree][-1]["pools_at_end"]["conduit_pool"] for tree in ("base", "cand")}
        sys.stdout.write("root ConduitPool at the end: " + ", ".join(
            f"{tree} target {p['target_idle']} idle {p['idle_count']} max {p['max_idle']}" for tree, p in pools.items())
            + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
