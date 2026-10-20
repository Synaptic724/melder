"""S1's notch (0.2.8262 -> 0.2.8263, read at landing), its running release-note section and packaging bullet, and the
attention board's notch notice (melder_1). Anchors found once; LF; new lines within 120 characters; read back.
Usage (repository root): land_s1_notch_note.py --check|--apply
"""
import datetime
import pathlib
import sys

NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = pathlib.Path("src/melder/__version__.py")
NOTE = pathlib.Path("release_docs/next_version_release.md")
BOARD = pathlib.Path("context_compass/attention_board.md")
SECTION = '''## Staging a version keeps the active version's name

Staging a version with `bind_inactive` under the name the active version holds - the usual way to try a new version
before a notch - took that name from the active version until 0.2.8263: Melder released the active version's binding
signature and dropped its address, so a meld by name raised `KeyError`, `find_spell_index` raised, and another
Spellbook of the frame could bind the name while the active version still served. Moving a parked version out of the
index and back, and `cleanup_spell` of a parked version alone in its index, did the same. Now the active version keeps
its name through all three:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                             existence="many")

assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised KeyError until 0.2.8263

world.notch_spell(spell_index=index, spell_id=french)
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "bonjour"
```

- Staging under a name another Spellbook's active spell holds no longer releases that spell's name either; staging
  stays open to any name, and a parked version holds no name until a notch makes it active.
- Restores and grafts stage parked versions the same way, so a restored or grafted world keeps its active versions'
  names too.

What stays the same: what a notch does with names, staging under any name, and every public signature.

'''
PACKAGING = ('- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n'
             '  describe how destroying an index a parked version left empty keeps every other spell\'s name, and the\n'
             '  packaged test documents describe the new tests; the `spellbook.py` code-map extent is remeasured, and its\n'
             '  line citations remapped.\n')
NOTICE = ("### Notch notice (melder_1, 2026-10-19, S1)\n"
          "- melder_1 landed 0.2.8263 (staging, an index move back and a lone parked disposal keep the active spell's\n"
          "  binding signature: `_destroy_spell_index` drops only its own route and releases only the departing member's\n"
          "  claim; STORY-2026-10-17-staged_version_releases_active_signature). Notch above it if you land after.\n")


def swap(text: str, old: str, new: str, name: str) -> str:
    """Replace the one `old` in `text` with `new`."""
    if text.count(old) != 1:
        raise SystemExit("%s: anchor found %d times: %r" % (name, text.count(old), old[:60]))
    for line in new.split("\n"):
        if len(line) > 120:
            raise SystemExit("%s: line over 120: %s" % (name, line))
    return text.replace(old, new)


def load(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path)
    return raw.decode("utf-8")


def main() -> None:
    """Prepare the three edits; write with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    version = swap(load(VERSION), '__version__ = "0.2.8262"', '__version__ = "0.2.8263"', "version")
    note = swap(load(NOTE), "# Melder 0.2.8262\n", "# Melder 0.2.8263\n", "note")
    note = swap(note, "## Packaging and documentation\n", SECTION + "## Packaging and documentation\n", "note")
    note = swap(note, "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8262.",
                PACKAGING + "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for "
                "0.2.8263.", "note")
    board = swap(load(BOARD), "### Device VM git hazard (melder_2, 2026-09-26)\n",
                 NOTICE + "### Device VM git hazard (melder_2, 2026-09-26)\n", "board")
    print("notch: __version__ read 0.2.8262, set 0.2.8263 at", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((VERSION, version), (NOTE, note), (BOARD, board)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path)
        print("applied")


main()
