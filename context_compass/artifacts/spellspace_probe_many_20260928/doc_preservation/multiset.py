"""Line-multiset tools for content preservation: `capture <doc> <out>`, `compare <before> <after> <report>`.

A capture counts every non-blank line (trailing whitespace stripped). A comparison lists each line whose count
fell (lost) or rose (added), so every removal in a promotion can be accounted for.
"""
import collections
import pathlib
import sys


def _count(path: pathlib.Path) -> collections.Counter:
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return collections.Counter(line.rstrip() for line in text.split("\n") if line.strip())


def capture(doc: str, out: str) -> None:
    counts = _count(pathlib.Path(doc))
    lines = [f"{n}\t{line}" for line, n in sorted(counts.items())]
    pathlib.Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{doc}: {sum(counts.values())} non-blank lines, {len(counts)} distinct")


def _load(path: str) -> collections.Counter:
    counts: collections.Counter = collections.Counter()
    for row in pathlib.Path(path).read_text(encoding="utf-8").split("\n"):
        if row:
            n, line = row.split("\t", 1)
            counts[line] = int(n)
    return counts


def compare(before: str, after: str, report: str) -> None:
    b, a = _load(before), _load(after)
    lost = sorted((line, b[line] - a[line]) for line in b if b[line] > a[line])
    added = sorted((line, a[line] - b[line]) for line in a if a[line] > b[line])
    out = [f"## lost: {sum(n for _, n in lost)} lines"]
    out += [f"- {n} x `{line}`" for line, n in lost]
    out += ["", f"## added: {sum(n for _, n in added)} lines"]
    out += [f"- {n} x `{line}`" for line, n in added]
    pathlib.Path(report).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"lost {sum(n for _, n in lost)}, added {sum(n for _, n in added)} -> {report}")


if __name__ == "__main__":
    if sys.argv[1] == "capture":
        capture(sys.argv[2], sys.argv[3])
    else:
        compare(sys.argv[2], sys.argv[3], sys.argv[4])
