"""Print, per failed test in pytest -v logs, the test name and its first 'E' lines (blast-radius triage)."""
import re
import sys

HEADER = re.compile(r"^_+ (test\S.*?) _+$")


def main() -> None:
    for path in sys.argv[1:]:
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        current = None
        shown = 0
        for line in lines:
            match = HEADER.match(line)
            if match:
                current = match.group(1)
                shown = 0
                print(f"\n## {current}")
                continue
            if current and line.startswith("E ") and shown < 3:
                print("   " + line[:230])
                shown += 1
            if line.startswith("=") and "short test summary" in line:
                current = None


if __name__ == "__main__":
    main()
