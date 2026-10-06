"""Line-ending-preserving helpers for the ContextCompass edits of this lane.

Every board and ticket is read as bytes, normalized to LF for editing, and
written back with the line terminator it had; a new file is written LF (the
package convention) unless told otherwise. Anchored edits assert uniqueness.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
from typing import Optional


def now_utc() -> str:
    """Read the clock immediately before a timestamp is written."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path: str) -> tuple[str, str]:
    """Return (text with LF endings, original newline: '\\r\\n' or '\\n')."""
    with open(path, "rb") as handle:
        raw = handle.read()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    return text, newline


def write_text(path: str, text: str, newline: str = "\n") -> None:
    """Write LF text back with the requested terminator, atomically."""
    data = text.replace("\r\n", "\n").replace("\n", newline).encode("utf-8")
    tmp = path + ".tmp"
    with open(tmp, "wb") as handle:
        handle.write(data)
    os.replace(tmp, path)


def replace_once(text: str, anchor: str, replacement: str, label: str = "") -> str:
    """Replace a unique anchor; refuse when it is absent or repeated."""
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"anchor {label or anchor[:60]!r} found {count} times")
    return text.replace(anchor, replacement)


def insert_after_regex(text: str, pattern: str, block: str, label: str = "") -> str:
    """Insert `block` right after the single match of `pattern` (MULTILINE)."""
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if len(matches) != 1:
        raise SystemExit(f"regex {label or pattern!r} matched {len(matches)} times")
    end = matches[0].end()
    return text[:end] + block + text[end:]


def check_line_lengths(text: str, limit: int = 120, exempt: Optional[str] = None) -> list[str]:
    """Report prose lines over the hard cap (table rows and path lines exempt)."""
    bad = []
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if len(line) <= limit or stripped.startswith("|") or stripped.startswith("- `") \
                or stripped.startswith("- ") and "/" in stripped and " " not in stripped[2:]:
            continue
        if exempt and re.search(exempt, line):
            continue
        bad.append(f"{number}: {len(line)}")
    return bad
