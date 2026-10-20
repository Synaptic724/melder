"""S7 A/B runner: alternate processes between the 0.2.8240 tree (HEAD, exported to /tmp) and the working copy, run the
existing-shapes probe in each, and summarize per arm (median of the per-process medians, and after/before).

Run from the repository root: python s7_bench_ab.py <gil 0|1> <pairs> <cycles> <rounds> <out.txt>
"""
import os
import pathlib
import re
import statistics
import subprocess
import sys

gil, pairs, cycles, rounds, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], pathlib.Path(sys.argv[5])
repo = pathlib.Path.cwd()
probe = repo / "context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s7_existing_shapes.py"
trees = {"before_0_2_8240": pathlib.Path("/tmp/m0_mq/before_0_2_8240"), "after_working_copy": repo}
arm_line = re.compile(r"^ARM (\S+) min (\S+) median (\S+)$")
medians = {name: {} for name in trees}
log = []
for pair in range(pairs):
    for name, tree in trees.items():
        env = dict(os.environ, PYTHONPATH="src:.")
        proc = subprocess.run(
            [sys.executable, "-X", f"gil={gil}", "-W", "ignore", str(probe), cycles, rounds],
            cwd=tree, env=env, capture_output=True, text=True, timeout=160,
        )
        log.append(f"--- pair {pair} {name} rc={proc.returncode}\n{proc.stdout}{proc.stderr}")
        assert proc.returncode == 0, proc.stderr[-2000:]
        for line in proc.stdout.splitlines():
            m = arm_line.match(line)
            if m:
                medians[name].setdefault(m.group(1), []).append(float(m.group(3)))
summary = [f"gil={gil} pairs={pairs} cycles={cycles} rounds={rounds}",
           f"{'arm':16s} {'before ns':>10s} {'after ns':>10s} {'after/before':>12s}   per-process medians (before | after)"]
for arm in medians["before_0_2_8240"]:
    b = medians["before_0_2_8240"][arm]
    a = medians["after_working_copy"][arm]
    summary.append(f"{arm:16s} {statistics.median(b):10.1f} {statistics.median(a):10.1f} {statistics.median(a) / statistics.median(b):12.3f}"
                   f"   {' '.join(f'{v:.0f}' for v in b)} | {' '.join(f'{v:.0f}' for v in a)}")
out.write_text("\n".join(log) + "\n=== SUMMARY\n" + "\n".join(summary) + "\n", encoding="utf-8")
print("\n".join(summary))
