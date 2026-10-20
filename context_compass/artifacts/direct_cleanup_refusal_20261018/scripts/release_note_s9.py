"""S9 (0.2.8256): the running release note - header, the new section, the packaging lines.

Usage (repository root): release_note_s9.py --check | --apply
"""
import pathlib
import sys

NOTE = pathlib.Path("release_docs/next_version_release.md")

SECTION = '''## A cleanup of an index's active version is refused while parked versions remain

A spell index can hold parked versions beside its active one - staged with `bind_inactive`, or the version a notch
moved away from. `Conduit.cleanup_spell` has always refused to dispose the active version of such an index. The two
other ways to dispose a spell - its own `cleanup()` and `Spellbook.cleanup_and_remove_spell` - did not: they removed
the version and cleaned the index under its parked versions, which then stayed in the Spellbook uncleaned and out of
reach. A notch to one raised `AttributeError`, `add_to_spell_index` and `cleanup_spell` of one raised "SpellIndex has
already been cleaned.", the Spellbook's teardown left them, and their own `cleanup()` then raised "Spellbook has
already been cleaned.". From 0.2.8256 all three refuse, change nothing, and say how to go on:

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

try:
    world.get_spell_by_spell_id(english).cleanup()     # until 0.2.8256: cleaned the index under French
except RuntimeError as error:
    print(error)    # Spellbook cannot remove spell <spell_id>: it is the active member of a multi-member index, ...

world.notch_spell(spell_index=index, spell_id=french)            # one remedy: notch first,
world.cleanup_spell(spell=world.get_spell_by_spell_id(english))  # then dispose the old version, now parked
assert world.meld(spell_id=french).greet() == "bonjour"
```

**Breaking change:** `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell(spell)` of the active version of an
index that also holds parked versions raise `RuntimeError` "Spellbook cannot remove spell <spell_id>: it is the
active member of a multi-member index, and disposing it would leave the index's parked versions without an active
one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with remove_from_spell_index
first." Retire such a version in the order you choose - Melder picks no version for you:

- Notch the index to a parked version, then dispose the old version with `cleanup_spell`: it is parked now.
- Dispose the parked versions with `cleanup_spell`; the active version is then the index's only member, and any of
  the three removes it with its index.
- Move the parked versions out with `remove_from_spell_index` - each gets an index of its own and stays parked -
  then remove the active version.

`cleanup_spell`'s refusal keeps its type and its moment and names the same remedies: "cleanup_spell: spell
<spell_id> is the active member of a multi-member index, and disposing it would leave the index's parked versions
without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
remove_from_spell_index first." (it said "...; notch away from it before disposing it.").

What stays the same: removing the only version of an index, which goes with its index; `cleanup_spell` of a parked
version; the teardown of a conduit, Spellbook or frame, which cleans every active version with its index as
before. No public signature changes.

## Packaging and documentation
'''

PACKAGING_OLD = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8255.\n"
PACKAGING_NEW = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the refusal on the three cleanup calls and its remedies; the code-map extents of `spellbook.py` and\n"
    "  `spell.py` are remeasured, and their line citations remapped.\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8256.\n"
)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    raw = NOTE.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF")
    text = raw.decode("utf-8")
    if not text.startswith("# Melder 0.2.8255\n\n**Unreleased**\n"):
        raise SystemExit("unexpected header")
    text = "# Melder 0.2.8256\n" + text[len("# Melder 0.2.8255\n"):]
    if text.count("\n## Packaging and documentation\n") != 1:
        raise SystemExit("packaging heading not unique")
    text = text.replace("## Packaging and documentation\n", SECTION, 1)
    if text.count(PACKAGING_OLD) != 1:
        raise SystemExit("packaging rebuild line not found once")
    text = text.replace(PACKAGING_OLD, PACKAGING_NEW, 1)
    long_lines = [line for line in text.split("\n") if len(line) > 120]
    print("lines:", text.count("\n"), "over 120:", len(long_lines))
    for line in long_lines:
        print("  ", len(line), line[:100])
    if mode == "--apply":
        NOTE.write_bytes(text.encode("utf-8"))
        if NOTE.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
