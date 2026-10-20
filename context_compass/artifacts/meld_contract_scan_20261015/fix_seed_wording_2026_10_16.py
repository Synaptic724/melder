"""Correct the hash-seed wording of the 0.2.8251 entries (melder_1, 2026-10-16): the seeds 3, 4, 6, 8, 9 belong to the
probe; the release note's own example fails for 6 of the seeds 0-9 (runs/release_example_removal_2026_10_16.txt).
usage: python fix_seed_wording_2026_10_16.py <repo root> --check | --apply
"""
import pathlib
import sys

EDITS = {
    "release_docs/next_version_release.md": [(
        "reached the parked version first it removed the active version's copy in its place; it failed for 5 of the hash\n"
        "seeds 0-9. From 0.2.8251 removing a version's copy removes that version's copy - the active one only when it is that\n"
        "version, otherwise the parked one - so the unlink completes in any order:\n",
        "reached the parked version first it removed the active version's copy in its place - in about half of all processes\n"
        "(for the example below, 6 of the hash seeds 0-9). From 0.2.8251 removing a version's copy removes that version's\n"
        "copy - the active one only when it is that version, otherwise the parked one - so the unlink completes in any order:\n",
    )],
    "context_compass/system_docs/src_architecture.md": [(
        "  members in the member set's order, which follows the hash seed, so in about half of all processes (seeds 3, 4, 6,\n"
        "  8 and 9 of 0-9) an unlink after a notch raised RuntimeError \"Spell version <id> not found for conduit ID\n"
        "  <owner>.\" for the active member and left the parked copy behind for good (a retry returned normally and kept\n"
        "  it); removing an old version's grant took the new version's active copy, so its consumers lost their provider.\n",
        "  members in the member set's order, which follows the hash seed, so in about half of all processes (for one\n"
        "  reproducer, the seeds 3, 4, 6, 8 and 9 of 0-9) an unlink after a notch raised RuntimeError \"Spell version <id>\n"
        "  not found for conduit ID <owner>.\" for the active member and left the parked copy behind for good (a retry\n"
        "  returned normally and kept it); removing an old version's grant took the new version's active copy, so its\n"
        "  consumers lost their provider.\n",
    )],
}


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <repo root> --check | --apply")
    root = pathlib.Path(sys.argv[1])
    out = {}
    for rel, edits in EDITS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for old, new in edits:
            if text.count(old) != 1:
                raise SystemExit(f"{rel}: anchor found {text.count(old)} times")
            if any(len(ln) > 120 for ln in new.split("\n")):
                raise SystemExit(f"{rel}: long line in replacement")
            text = text.replace(old, new)
        out[rel] = text
        print(rel, "ok")
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    for rel, text in out.items():
        (root / rel).write_text(text, encoding="utf-8")
        assert (root / rel).read_text(encoding="utf-8") == text
    print("applied and read back")


if __name__ == "__main__":
    main()
