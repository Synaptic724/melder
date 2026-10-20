"""S7's release-note entry (melder_1): the header to 0.2.8260, the section before "## Packaging and documentation",
one packaging bullet and the rebuild line. Each anchor must occur once; new lines stay within 120 characters; LF.
The section's example is probes/probe_release_note_s7.py, run as written with the GIL off and on.
Usage (repository root): release_note_s7.py --check | --apply
"""
import pathlib
import sys

NOTE = pathlib.Path("release_docs/next_version_release.md")
SECTION = '''## A Spellbook's teardown cleans its parked versions too

When a Spellbook is torn down - with its root conduit, or by `Spellbook.cleanup()` - it now cleans every version it
holds, parked ones included, and every spell index that only parked versions hold (one `remove_from_spell_index`
made). Until 0.2.8260 the teardown cleaned only the active versions and their indexes: a parked version stayed
uncleaned, an index of its own with it, and the version's own `cleanup()` raised "Spellbook has already been
cleaned.":

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
parked = world.get_spell_by_spell_id(french)

world.cleanup()                 # the root's teardown tears the Spellbook down
assert parked.cleaned           # False until 0.2.8260
parked.cleanup()                # returns; raised "Spellbook has already been cleaned." until 0.2.8260
```

What stays the same: the teardown of a Spellbook whose versions are all active, the managed pools a root's teardown
cleans, and every cleanup call on a live Spellbook. No public signature changes.

'''
EDITS = [
    ("# Melder 0.2.8259\n", "# Melder 0.2.8260\n"),
    ("## Packaging and documentation\n", SECTION + "## Packaging and documentation\n"),
    ("- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8259.\n",
     "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
     "  describe the teardown's retirement of parked versions and of the indexes only they hold; the `spellbook.py`\n"
     "  code-map extent is remeasured, and its line citations remapped.\n"
     "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8260.\n"),
]


def main() -> None:
    """Apply the edits in memory; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    raw = NOTE.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the release note")
    text = raw.decode("utf-8")
    before = text.count("\n")
    for old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("anchor found %d times: %r" % (text.count(old), old[:60]))
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("line over 120 chars: " + line)
        text = text.replace(old, new)
    print("release note: %d -> %d lines" % (before, text.count("\n")))
    if sys.argv[1] == "--apply":
        NOTE.write_bytes(text.encode("utf-8"))
        if NOTE.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
