"""
Register the managed spell pool chapter in the documentation inputs (S3 of
EPIC-2026-10-18-managed_spell_examples_and_docs).

Run from the repository root (any Python 3.10+):

    python context_compass/artifacts/managed_spell_examples_20261018/scripts/apply_s3_docs.py

Edits four existing files in place, each change anchored on exact text that must occur
once, each new line written with the line ending of the line next to it:

- docs/curriculum.toml: the `intermediate/managed-spells` chapter, placed right before
  the `intermediate/connected-subsystems` chapter (so right after `intermediate/ownership`:
  the page's last section uses the dynamic posture and the ownership transfer the chapters
  before it teach)
- docs/intermediate/index.md: one "What you will learn" bullet
- docs/intermediate/scopes.md: a cross-link after the managed-pool purge paragraph
- docs/seo.toml: the page in `required_descriptions`

The page itself (docs/intermediate/managed-spells.md) and the catalog registration of
lessons 42-48 (docs/catalog.toml) are written separately. A second run refuses before it
changes anything, because the chapter id must be absent.
"""
import sys
from pathlib import Path


def line_ending_of(raw: bytes, position: int) -> bytes:
    """Return the line ending that terminates the line holding `position` (CRLF or LF)."""
    end = raw.index(b"\n", position)
    return b"\r\n" if raw[end - 1:end] == b"\r" else b"\n"


def checked_index(path: Path, raw: bytes, anchor: bytes) -> int:
    """Return the anchor's offset, refusing unless it occurs exactly once."""
    if raw.count(anchor) != 1:
        raise SystemExit(f"{path}: anchor must occur once, found {raw.count(anchor)}: {anchor!r}")
    return raw.index(anchor)


def insert_after_line(path: Path, anchor: bytes, lines: list) -> None:
    """Insert `lines` after the line containing `anchor`, matching that line's ending."""
    raw = path.read_bytes()
    position = checked_index(path, raw, anchor)
    eol = line_ending_of(raw, position)
    end = raw.index(b"\n", position) + 1
    block = b"".join(line.encode("utf-8") + eol for line in lines)
    path.write_bytes(raw[:end] + block + raw[end:])


def insert_before_previous_line(path: Path, anchor: bytes, lines: list) -> None:
    """Insert `lines` before the line that precedes the line containing `anchor`."""
    raw = path.read_bytes()
    position = checked_index(path, raw, anchor)
    eol = line_ending_of(raw, position)
    anchor_line_start = raw.rindex(b"\n", 0, position) + 1
    previous_line_start = raw.rindex(b"\n", 0, anchor_line_start - 1) + 1
    block = b"".join(line.encode("utf-8") + eol for line in lines)
    path.write_bytes(raw[:previous_line_start] + block + raw[previous_line_start:])


def main() -> None:
    """Apply the four registrations; refuse a second run."""
    root = Path.cwd()
    curriculum = root / "docs" / "curriculum.toml"
    if b'id = "intermediate/managed-spells"' in curriculum.read_bytes():
        raise SystemExit("docs/curriculum.toml already holds intermediate/managed-spells; nothing applied.")
    # The line before `id = "intermediate/connected-subsystems"` is that chapter's `[[chapter]]` header.
    insert_before_previous_line(curriculum, b'id = "intermediate/connected-subsystems"',
                                ["[[chapter]]",
                                 'id = "intermediate/managed-spells"',
                                 'title = "Managed spell pools"',
                                 'level = "intermediate"',
                                 'source = "intermediate/managed-spells.md"',
                                 'lessons = ["intermediate:42", "intermediate:43", "intermediate:44", '
                                 '"intermediate:45", "intermediate:46", "intermediate:47", "intermediate:48"]',
                                 "show_steps = true",
                                 ""])
    insert_after_line(root / "docs" / "intermediate" / "index.md",
                      b"- Early object disposal with `purge`, scoped cleanup, transfer, and severing relationships.",
                      ["- Managed spell pools: lease, release and reset pooled objects in elastic, limited and "
                       "queue modes."])
    insert_after_line(root / "docs" / "intermediate" / "scopes.md",
                      b"trims them and when the root that owns it is torn down.",
                      ["[Managed spell pools](managed-spells.md) walks through the whole lifecycle."])
    insert_after_line(root / "docs" / "seo.toml",
                      b'  "examples/intermediate/15-constructor-di-by-annotation.html",',
                      ['  "intermediate/managed-spells.html",'])
    sys.stdout.write("applied: curriculum.toml, intermediate/index.md, intermediate/scopes.md, seo.toml\n")


if __name__ == "__main__":
    main()
