"""Exact-once, ending-preserving text replacement helper for the slotted_lifetime_fixes landing scripts.

Usage (from a landing script): `apply(path, [(old, new), ...])`.
- `old` and `new` are written with LF line endings and must be whole lines (both end with a newline).
- Matching ignores line endings (the file may mix CRLF and LF, as conduit_cloud.py does); every `old` must occur
  exactly once (else nothing is written).
- Line endings are preserved: lines the edit keeps unchanged keep their own ending; inserted or changed lines take
  the ending of the nearest kept or replaced line before them in the block (the block's first line for a leading
  insertion), so a file's mix of CRLF and LF lines is never normalized.
Returns the number of edits applied.
"""
import difflib
import pathlib
from typing import List, Tuple


def _split(raw: str) -> Tuple[List[str], List[str]]:
    bodies: List[str] = []
    endings: List[str] = []
    for line in raw.splitlines(keepends=True):
        if line.endswith("\r\n"):
            bodies.append(line[:-2]); endings.append("\r\n")
        elif line.endswith("\n"):
            bodies.append(line[:-1]); endings.append("\n")
        else:
            bodies.append(line); endings.append("")
    return bodies, endings


def apply(path: str, edits: List[Tuple[str, str]]) -> int:
    file_path = pathlib.Path(path)
    bodies, endings = _split(file_path.read_bytes().decode("utf-8"))
    for index, (old, new) in enumerate(edits):
        if not old.endswith("\n") or not new.endswith("\n"):
            raise SystemExit(f"{path}: edit {index} must be whole lines")
        old_lines = old[:-1].split("\n")
        new_lines = new[:-1].split("\n")
        width = len(old_lines)
        hits = [s for s in range(len(bodies) - width + 1) if bodies[s:s + width] == old_lines]
        if len(hits) != 1:
            raise SystemExit(f"{path}: edit {index} anchor found {len(hits)} times:\n{old[:300]}")
        start = hits[0]
        old_endings = endings[start:start + width]
        new_endings: List[str] = []
        matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
        last = old_endings[0]
        for tag, a0, a1, b0, b1 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(a1 - a0):
                    new_endings.append(old_endings[a0 + k]); last = old_endings[a0 + k]
            else:
                if a1 > a0:
                    last = old_endings[a0]
                for _ in range(b1 - b0):
                    new_endings.append(last)
        bodies[start:start + width] = new_lines
        endings[start:start + width] = new_endings
    file_path.write_bytes("".join(b + e for b, e in zip(bodies, endings)).encode("utf-8"))
    return len(edits)
