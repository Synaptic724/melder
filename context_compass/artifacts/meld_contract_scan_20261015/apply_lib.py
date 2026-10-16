"""Exact-text edit helpers shared by the lane's apply scripts (melder_1, TASK-2026-10-15-make_meld_state_checks...)."""
import pathlib
from typing import List, Tuple


def one(text: str, old: str, new: str, where: str) -> str:
    """Replace exactly one occurrence of `old`; refuse when it occurs zero or several times."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{where}: expected one occurrence, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def between(text: str, start: str, end: str, new: str, where: str) -> str:
    """Replace the text from `start` (inclusive) to `end` (exclusive); both markers must be unique."""
    for marker in (start, end):
        count = text.count(marker)
        if count != 1:
            raise SystemExit(f"{where}: marker found {count} times: {marker[:80]!r}")
    i = text.index(start)
    j = text.index(end)
    if j <= i:
        raise SystemExit(f"{where}: end marker precedes start marker")
    return text[:i] + new + text[j:]


def apply(root: pathlib.Path, rel: str, steps: List[Tuple[str, str, str, str]], check_only: bool) -> None:
    """Apply ('one'|'between', a, b, c) steps to one file under `root`; with check_only, verify and write nothing.

    Anchors match LF text. A file whose every line ends CRLF is written back CRLF, new lines included, so its git
    diff shows only the edits (three of the lane's test files are stored CRLF in the index); any other file - LF or
    mixed - is written LF, the form git stores it in.
    """
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for kind, a, b, c in steps:
        added = b if kind == "one" else c
        for line in added.splitlines():
            if len(line) > 120:
                raise SystemExit(f"{rel}: new line longer than 120 characters ({len(line)}): {line!r}")
        if kind == "one":
            text = one(text, a, b, rel)
        else:
            text = between(text, a, b, c, rel)
    if not check_only:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(("checked " if check_only else "applied ") + rel + (" (CRLF kept)" if crlf else ""))
