"""
Code-map helpers shared by this lane's document apply scripts: find one measured C1 entry and rewrite it from disk.
"""
import pathlib
import re
from typing import Optional

from apply_support import ApplySession

ENTRY = r"- path: `{0}`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n((?:  note: .*\n)(?:    .*\n)*)?"


def measured(root: str, path: str, now: str, note: Optional[str]) -> str:
    """Return one freshly measured code-map entry (with its note, when given) for a file on disk."""
    loc = len((pathlib.Path(root) / path).read_bytes().decode("utf-8").splitlines())
    block = f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {now}\n"
    return block + (note if note else "")


def remeasure(s: ApplySession, doc: str, root: str, path: str, now: str, new_note: Optional[str] = None) -> None:
    """Rewrite the one code-map entry for `path` in `doc`, keeping its note unless a new one is given."""
    text = s._load(doc)
    matches = list(re.finditer(ENTRY.format(re.escape(path)), text))
    if len(matches) != 1:
        raise AssertionError(f"{doc}: code map entry for {path}: {len(matches)} matches")
    old = matches[0].group(0)
    note = new_note if new_note is not None else (matches[0].group(1) or "")
    s.replace(doc, old, measured(root, path, now, note))
