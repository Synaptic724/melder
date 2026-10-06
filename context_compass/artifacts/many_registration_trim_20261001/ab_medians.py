"""Interleave N harness runs of two trees and print per-shape medians of the plain plan and the whole meld."""
import os, re, statistics, subprocess, sys
PY = os.path.expanduser("~/work/melder_cc/.venv/bin/python")
TREES = {"before": os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/work/melder_before"), "after": os.path.expanduser(sys.argv[3] if len(sys.argv) > 3 else "~/work/melder_cc")}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
rows = {}
for i in range(N):
    for side, root in TREES.items():
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=f"{root}/src:{root}:{root}/tests/experimentation")
        out = subprocess.run([PY, "-X", "gil=0", f"{root}/tests/experimentation/codegen_strategy_certification.py"],
                             cwd=os.path.expanduser("~/work/pgo_run"), env=env, capture_output=True, text=True, timeout=60).stdout
        for line in out.splitlines():
            m = re.match(r"\| (\w+) \| (plain|reference: [^|]+) \| (\d+) \|", line)
            if m:
                key = (m.group(1), "plan" if m.group(2) == "plain" else "meld")
                rows.setdefault(key, {}).setdefault(side, []).append(int(m.group(3)))
print(f"| shape | measure | before median (min-max) | after median (min-max) | delta |")
print("| --- | --- | ---: | ---: | ---: |")
for (shape, measure), sides in sorted(rows.items()):
    b, a = sides["before"], sides["after"]
    mb, ma = statistics.median(b), statistics.median(a)
    print(f"| {shape} | {measure} | {mb:.0f} ({min(b)}-{max(b)}) | {ma:.0f} ({min(a)}-{max(a)}) | {100*(ma-mb)/mb:+.0f}% |")
