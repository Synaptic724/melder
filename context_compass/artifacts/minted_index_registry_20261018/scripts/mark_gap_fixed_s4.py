"""S4: mark the collision-check gap fixed where S1 and S2's text, written before S4 landed, still call it open.

src_architecture's identity invariant (its Open list) and the running release note's identity section (Known
limits). Exact anchors, each found once; LF; every changed line within 120 characters; read back.
Usage (repository root): mark_gap_fixed_s4.py --check | --apply
"""
import pathlib
import sys

EDITS = (
    (pathlib.Path("context_compass/system_docs/src_architecture.md"),
     "  definition's slotted object (S3); a record made before 0.2.8257 that holds one object twice fails at its second\n"
     "  replayed bind (S5); and until STORY-2026-10-17-minted_index_missing_from_frame_registry lands, bind's collision\n"
     "  check misses a version alone in an index `remove_from_spell_index` minted.\n",
     "  definition's slotted object (S3); and a record made before 0.2.8257 that holds one object twice fails at its\n"
     "  second replayed bind (S5). Fixed in 0.2.8259: bind's collision check missed a version alone in an index\n"
     "  `remove_from_spell_index` minted (STORY-2026-10-17-minted_index_missing_from_frame_registry).\n"),
    (pathlib.Path("release_docs/next_version_release.md"),
     "order; a bind costs 37-55 us more (conjure and melds are unchanged); a definition rebound under another slotted\n"
     "existence can meet the removed definition's object at its first meld; and a version alone in an index that\n"
     "`remove_from_spell_index` minted is missed by the collision check until that index is registered with its frame.\n",
     "order; a bind costs 37-55 us more (conjure and melds are unchanged); and a definition rebound under another\n"
     "slotted existence can meet the removed definition's object at its first meld.\n"),
)


def main() -> None:
    """Apply each edit to its file; write only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    for path, old, new in EDITS:
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % path)
        text = raw.decode("utf-8")
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times" % (path, text.count(old)))
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("%s: %d chars: %s" % (path, len(line), line))
        text = text.replace(old, new)
        print("%s: %d -> %d lines" % (path, raw.count(b"\n"), text.count("\n")))
        if sys.argv[1] == "--apply":
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path)
    print("applied" if sys.argv[1] == "--apply" else "check OK")


main()
