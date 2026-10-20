"""Shared helpers of S6 part A's docs scripts: exact-once substitution, code-map remeasure, line-length checks."""
import pathlib
import re
from typing import Optional


def sub(text: str, old: str, new: str) -> str:
    """Replace `old` with `new`, refusing unless `old` occurs exactly once."""
    count = text.count(old)
    assert count == 1, (old[:100], count)
    return text.replace(old, new)


def insert_before(text: str, anchor: str, block: str) -> str:
    """Insert `block` right before `anchor`, which must occur exactly once."""
    return sub(text, anchor, block + anchor)


def remeasure(text: str, path: str, loc: int, now: str, note_old: Optional[str] = None,
              note_new: Optional[str] = None) -> str:
    """
    Rewrite one code-map record: end_line and loc from disk, verified_at now, and optionally its note.

    The record is `- path: `<path>`` followed by start_line, end_line, loc and verified_at lines; it must occur once.
    """
    pattern = re.compile(
        r"(- path: `" + re.escape(path) + r"`\n  start_line: 1\n)  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n"
    )
    matches = pattern.findall(text)
    assert len(matches) == 1, (path, len(matches))
    text = pattern.sub(lambda m: m.group(1) + f"  end_line: {loc}\n  loc: {loc}\n  verified_at: {now}\n", text)
    if note_old is not None:
        text = sub(text, note_old, note_new)
    return text


def loc_of(repo: pathlib.Path, path: str) -> int:
    """Count a file's lines the way the code maps measure them (splitlines)."""
    return len((repo / path).read_text(encoding="utf-8").splitlines())


def check_lines(old: str, new: str) -> None:
    """Refuse any line the edit adds that is over 120 characters and holds no path."""
    before = set(old.splitlines())
    long = [line for line in new.splitlines() if line not in before and len(line) > 120 and "/" not in line]
    assert not long, long
