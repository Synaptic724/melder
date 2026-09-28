"""Summarize bench_scope_cycle_steps.py outputs: per tree and step, the median of the per-run medians.

melder_0, 2026-09-27. Usage: python ab_summary.py <output file> [<output file> ...]
"""
import re
import statistics
import sys
from collections import defaultdict

runs = defaultdict(lambda: defaultdict(list))
totals = defaultdict(list)
tree = None
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8"):
        head = re.match(r"tree=(\S+) mode=(\S+) .* sum_of_step_medians=([\d,]+) ns", line)
        if head:
            tree = f"{head.group(1)}:{head.group(2)}"
            totals[tree].append(int(head.group(3).replace(",", "")))
            continue
        step = re.match(r"\s+(\S+)\s+median=\s*([\d,]+) ns", line)
        if step and tree:
            runs[tree][step.group(1)].append(int(step.group(2).replace(",", "")))
trees = list(runs)
print("step".ljust(24) + "".join(t.rjust(26) for t in trees))
for name in runs[trees[0]]:
    cells = []
    for t in trees:
        values = runs[t][name]
        cells.append(f"{statistics.median(values):>8,.0f} ({min(values):,}-{max(values):,})".rjust(26))
    print(name.ljust(24) + "".join(cells))
print("sum_of_step_medians".ljust(24) + "".join(
    f"{statistics.median(totals[t]):>8,.0f} ({min(totals[t]):,}-{max(totals[t]):,})".rjust(26) for t in trees))
print("runs per tree: " + ", ".join(f"{t}={len(totals[t])}" for t in trees))
