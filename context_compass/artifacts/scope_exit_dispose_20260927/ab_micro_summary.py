"""Summarize bench_scope_ops_micro.py outputs: per operation, median and range per tree and the delta.

melder_0, 2026-09-27. Usage: python ab_micro_summary.py <output file>
"""
import re
import statistics
import sys
from collections import defaultdict

data = defaultdict(lambda: defaultdict(list))
for line in open(sys.argv[1], encoding="utf-8"):
    match = re.match(r"tree=(\S+) gil=\S+ (.*)", line)
    if not match:
        continue
    for key, value in re.findall(r"(\S+)=([\d.]+)", match.group(2)):
        data[key][match.group(1)].append(float(value))
for key, per_tree in data.items():
    base, new = per_tree["wt"], per_tree["wt_new"]
    b, n = statistics.median(base), statistics.median(new)
    print(f"{key:28s} wt={b:7.1f} ({min(base):.1f}-{max(base):.1f})  wt_new={n:7.1f} ({min(new):.1f}-{max(new):.1f})"
          f"  delta={n - b:+6.1f} ({(n - b) / b:+.1%})  runs={len(base)}/{len(new)}")
