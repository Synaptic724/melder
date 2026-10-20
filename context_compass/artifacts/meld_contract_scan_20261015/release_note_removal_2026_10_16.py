"""Release-note entry for the contracted-copy removal fix (0.2.8251), melder_1 (synaptic_python_developer), 2026-10-16.

Adds one `##` section after the 0.2.8250 contract-recheck section and one packaging bullet before the rebuild line of
release_docs/next_version_release.md. The header and the rebuild line's version move with the notch script.
usage: python release_note_removal_2026_10_16.py <repo root> --check | --apply. Anchors must match exactly once.
"""
import pathlib
import sys

NOTE = "release_docs/next_version_release.md"

SECTION = '''## Unlinking an index after a notch removes every version's copy

A borrower that links an index with `add_index_to_contract` holds a copy of every version on it: the active
version's copy is live and the others are parked. After the owner notched the index - to a version staged with
`bind_inactive`, as in the first example above - `remove_index_from_contract` could fail with `RuntimeError`
"Spell version <spell_id> not found for conduit ID <owner id>." and leave the old version's parked copy behind for
good. The unlink removes the versions one at a time, in an order that follows the process's hash seed, and when it
reached the parked version first it removed the active version's copy in its place; it failed for 5 of the hash
seeds 0-9. From 0.2.8251 removing a version's copy removes that version's copy - the active one only when it is that
version, otherwise the parked one - so the unlink completes in any order:

```python
# Continuing the first example above: the lender notched the index from English to French.
borrower.remove_index_from_contract(index_id=index.id, conduit=lender)   # raised in about half of all runs

borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "BONJOUR"
```

The same fix covers version grants: a borrower granted a version, then the new version after a notch, kept the old
version's parked copy and lost the new version's active copy when it released the old grant with
`remove_spell_from_contract`, so its consumers lost their provider. Now only the old version's copy goes.

What stays the same: when a borrower holds one version of an index, an unlink, a grant's release and an index
destroy remove the same copy as before, and a consumer of a removed active copy still fails its next meld with the
missing-provider report. No public signature changes.

'''

PACKAGING_BULLET = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the removal of one version's copy by its own spell_id; the `spellbook.py` code-map extent is\n"
    "  remeasured, and its line citations remapped.\n"
)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <repo root> --check | --apply")
    path = pathlib.Path(sys.argv[1]) / NOTE
    text = path.read_text(encoding="utf-8")
    if b"\r" in path.read_bytes():
        raise SystemExit("the note has CR bytes - refusing (would change line endings)")
    anchor = "## Packaging and documentation\n"
    if text.count(anchor) != 1:
        raise SystemExit("packaging heading not found exactly once")
    text = text.replace(anchor, SECTION + anchor)
    rebuild = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8250.\n"
    if text.count(rebuild) != 1:
        raise SystemExit("rebuild line not found exactly once")
    text = text.replace(rebuild, PACKAGING_BULLET + rebuild)
    long = [ln for ln in (SECTION + PACKAGING_BULLET).split("\n") if len(ln) > 120]
    if long:
        raise SystemExit(f"long lines {long}")
    print(NOTE, "lines", path.read_text(encoding="utf-8").count("\n"), "->", text.count("\n"))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    path.write_text(text, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == text
    print("applied and read back")


if __name__ == "__main__":
    main()
