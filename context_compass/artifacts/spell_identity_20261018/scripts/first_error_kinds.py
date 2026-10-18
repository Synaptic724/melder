"""Group failed tests of pytest -v logs by file and first 'E' line (S1+S2 test tranche triage, melder_0)."""
import re
import sys
from collections import defaultdict

HEADER = re.compile(r"^_+ (test\S.*?) _+$")
LOCATION = re.compile(r"^(tests/\S+?\.py):\d+: ")


def main() -> None:
    first = {}
    files = {}
    for path in sys.argv[1:]:
        current = None
        for line in open(path, encoding="utf-8", errors="replace").read().split("\n"):
            match = HEADER.match(line)
            if match:
                current = match.group(1)
                continue
            if current is None:
                continue
            loc = LOCATION.match(line)
            if loc and current not in files:
                files[current] = loc.group(1)
            if line.startswith("E ") and current not in first:
                first[current] = line[1:].strip()[:200]
            if line.startswith("=") and "short test summary" in line:
                current = None
    groups = defaultdict(list)
    for test, error in first.items():
        groups[(files.get(test, "?"), error)].append(test)
    for (path, error), tests in sorted(groups.items()):
        print(f"{len(tests):3d} {path} :: {error}")
        print("      e.g. " + tests[0][:150])


if __name__ == "__main__":
    main()
