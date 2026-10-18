"""Print each non-identifier "lineage" occurrence of the given files with its surrounding lines (melder_1, 2026-10-18).

Reads the inventory (one JSON line per occurrence) and, for each requested file, prints the STRING / COMMENT / TEXT
occurrences grouped into windows of context so each docstring or comment can be read whole before a hand edit.
Read-only.

Usage: python show_occurrences.py <inventory.jsonl> <context_lines> <path> [<path> ...]
"""
import json
import pathlib
import sys


def main() -> None:
    """Print the context windows for every requested file."""
    inventory = pathlib.Path(sys.argv[1])
    context = int(sys.argv[2])
    wanted = set(sys.argv[3:])
    hits = {}
    for line in inventory.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["path"] in wanted and row["kind"] != "NAME":
            hits.setdefault(row["path"], set()).add(row["line"])
    for path in sys.argv[3:]:
        lines = pathlib.Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
        numbers = sorted(hits.get(path, ()))
        print(f"===== {path} ({len(numbers)} lines)")
        windows = []
        for number in numbers:
            start, end = max(1, number - context), min(len(lines), number + context)
            if windows and start <= windows[-1][1] + 1:
                windows[-1][1] = max(windows[-1][1], end)
            else:
                windows.append([start, end])
        for start, end in windows:
            for n in range(start, end + 1):
                mark = ">>" if n in numbers else "  "
                print(f"{mark}{n:5d}| {lines[n - 1]}")
            print("  -----")


if __name__ == "__main__":
    main()
