"""S4 (STORY-2026-10-17-minted_index_missing_from_frame_registry): the running release note - the header, the new
section before "## Packaging and documentation", the packaging bullet and the rebuild line.

The example is probes/probe_release_note_s4.py, run as written (it raises on a tree without the fix and every assert
holds with it). The header and the rebuild line are matched by pattern, so melder_0's S1/S2 entries can land first.
Usage (repository root): release_note_s4.py --notch 0.2.82NN --check | --apply
"""
import pathlib
import re
import sys

NOTE = pathlib.Path("release_docs/next_version_release.md")

SECTION = '''## A version moved into an index of its own is found by its spell_id

`Conduit.remove_from_spell_index` moves a parked version out of its spell index into a fresh index of its own, where
it stays parked until you notch to it. Until {N} the frame never learned about that index, so the version - parked
there or notched active there - could not be found by its spell_id from a conduit:

```python
class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, existence="many", binding_name="english")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, existence="many", binding_name="french")

world.remove_from_spell_index(spell_id=french, source_index=index)  # French gets an index of its own, parked
own_index = world.get_spell_by_spell_id(french).spell_index  # raised "not found in any conduit" until {N}
world.notch_spell(spell_index=own_index, spell_id=french)
assert world.get_conduit_by_spell_id(french) is world
assert world.meld(spell_id=french).greet() == "bonjour"
assert world.meld(spell_id=english).greet() == "hello"
```

- `get_spell_by_spell_id` and `get_conduit_by_spell_id` answer for such a version, parked or active; they raised
  `ValueError` "Spell version <spell_id> not found in any conduit.".
- A linked conduit's `add_spell_to_contract(spell_id=...)` and `transfer_spell_ownership` by spell_id proceed for
  it; both raised that `ValueError`. The borrower's copy is parked or active as the version is.
- Another Spellbook can no longer bind the same spell_id while the version sits in its own index: the bind raises the
  usual `RuntimeError` "Spell ID collision detected: this object is already registered as spell_id <id>. ...", in
  the same frame and, under process-wide spell ids (the default), in another frame. The bind used to be accepted,
  so two Spellbooks held one spell_id.
- `MutationResearch.residency_view(spell_id)` reads the version `parked` in its own index and `active` there once a
  notch makes it active; it read `declared_only`.

What stays the same: what `remove_from_spell_index` moves and refuses, the version staying parked until a notch,
moving it back with `add_to_spell_index` (its emptied index goes), and every lookup of a version in any other index.
No public signature changes.

## Packaging and documentation
'''

PACKAGING = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the registration of the index `remove_from_spell_index` mints, its removal at the root's teardown and\n"
    "  residency's parked verdict; the code-map extents of `spellbook.py`, `spell.py` and `mutation_research.py` are\n"
    "  remeasured, and their line citations remapped.\n"
)

HEADER = re.compile(r"\A# Melder (0\.2\.82\d\d)\n\n\*\*Unreleased\*\*\n")
REBUILD = re.compile(r"^- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for "
                     r"(0\.2\.82\d\d)\.\n", re.M)


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--notch" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    notch = args[1]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN")
    raw = NOTE.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF")
    text = raw.decode("utf-8")
    header = HEADER.match(text)
    if header is None:
        raise SystemExit("unexpected header")
    text = "# Melder " + notch + text[len("# Melder " + header.group(1)):]
    if text.count("\n## Packaging and documentation\n") != 1:
        raise SystemExit("packaging heading not unique")
    if "## A version moved into an index of its own is found by its spell_id\n" in text:
        raise SystemExit("already applied")
    text = text.replace("## Packaging and documentation\n", SECTION.replace("{N}", notch), 1)
    rebuilds = list(REBUILD.finditer(text))
    if len(rebuilds) != 1:
        raise SystemExit("rebuild line found %d times" % len(rebuilds))
    line = rebuilds[0]
    text = (text[:line.start()] + PACKAGING
            + "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for " + notch + ".\n"
            + text[line.end():])
    long_lines = [entry for entry in text.split("\n") if len(entry) > 120]
    print("header was", header.group(1), "rebuild line was", line.group(1), "lines:", text.count("\n"),
          "over 120:", len(long_lines))
    for entry in long_lines:
        print("  ", len(entry), entry[:100])
    if args[2] == "--apply":
        NOTE.write_bytes(text.encode("utf-8"))
        if NOTE.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
