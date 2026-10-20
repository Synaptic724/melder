"""Build the fair-matrix outcome table from r4/runs/matrix/*.log (PASS/FAIL per test, tree and GIL mode)."""
import pathlib
import re
import sys

OUT = pathlib.Path(sys.argv[1])
trees = ["head", "cand_r1", "cand_r4", "cand_r4p", "cand_r5", "cand_nc1", "cand_nc2", "cand_nc3"]
labels = {"head": "3d184cac", "cand_r1": "R1", "cand_r4": "R4", "cand_r4p": "R4'", "cand_r5": "R5",
          "cand_nc1": "NC1", "cand_nc2": "NC2", "cand_nc3": "NC3"}
outcome = {}
tests = []
for log in sorted(OUT.glob("*_gil*_rep*.log")):
    m = re.match(r"(.+)_gil(\d)_rep(\d)\.log", log.name)
    tree, gil, rep = m.group(1), m.group(2), m.group(3)
    for line in log.read_text(encoding="utf-8").splitlines():
        r = re.match(r"(PASSED|FAILED|ERROR) diag/test_lookup_fair_matrix\.py::(test_\w+)", line)
        if r:
            status, test = r.group(1), r.group(2)
            if test not in tests:
                tests.append(test)
            outcome.setdefault((test, tree), set()).add((status, gil, rep))
runs = {}
for (test, tree), seen in outcome.items():
    runs[(test, tree)] = len(seen)
order = sorted(tests, key=lambda t: t)
print("Fair matrix, 3d184cac and candidates, CPython 3.14.7t, -X gil=0 and gil=1, 3 repetitions each.")
print("Cell: P = passed in all 6 runs, F = failed in all 6 runs, MIX = differs between runs.\n")
header = "test".ljust(66) + " ".join(labels[t].rjust(8) for t in trees)
print(header)
for test in order:
    cells = []
    for tree in trees:
        seen = outcome.get((test, tree), set())
        statuses = {s for s, _g, _r in seen}
        count = len(seen)
        if statuses == {"PASSED"} and count == 6:
            cells.append("P")
        elif statuses == {"FAILED"} and count == 6:
            cells.append("F")
        else:
            cells.append(f"MIX{count}")
    print(test[5:][:65].ljust(66) + " ".join(c.rjust(8) for c in cells))
