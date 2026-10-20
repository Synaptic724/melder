"""Re-wrap prose lines over 120 characters in one file, inside a line range (melder_0, 2026-10-18).

Paths and evidence lines (a list item that is one path) are left alone - unbreakable tokens are allowed over the cap
(configuration_standards.md). A long line is split at spaces into lines of at most 116 characters; continuation
lines keep the line's indent, plus two for a list item. Usage: wrap_long_lines.py <file> <first_line> <last_line>
"""
import pathlib
import re
import sys

PATH_ITEM = re.compile(r"^\s*- (context_compass/|src/|artifacts/|system_docs/|tests/|tickets/|release_docs/)\S*(\s\(.*\))?$")


def wrap(line: str) -> list:
    """Split one long prose line."""
    indent = len(line) - len(line.lstrip(" "))
    body = line.lstrip(" ")
    cont = indent + 2 if body.startswith("- ") else indent
    out, current = [], " " * indent
    for word in body.split(" "):
        candidate = (current + " " + word) if current.strip() else (current + word)
        if len(candidate) > 116 and current.strip():
            out.append(current)
            current = " " * cont + word
        else:
            current = candidate
    out.append(current)
    return out


def main() -> None:
    """Re-wrap the range."""
    path, first, last = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    lines = path.read_text(encoding="utf-8").split("\n")
    result, changed = [], 0
    for number, line in enumerate(lines, 1):
        if first <= number <= last and len(line) > 120 and not PATH_ITEM.match(line):
            result.extend(wrap(line))
            changed += 1
        else:
            result.append(line)
    path.write_text("\n".join(result), encoding="utf-8")
    print(f"re-wrapped {changed} line(s) in {path}")


if __name__ == "__main__":
    main()
