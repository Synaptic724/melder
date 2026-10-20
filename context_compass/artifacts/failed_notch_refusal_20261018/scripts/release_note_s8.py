"""S8's release-note entry (melder_1): the header to the notch landed (`__version__`), the section before "## Packaging
and documentation", one packaging bullet and the rebuild line for that version. Run after the notch, from the
repository root; each anchor must occur once; new lines stay within 120 characters; LF. The section's example is
probes/probe_release_note_s8.py, run as written with the GIL off and on.
Usage: release_note_s8.py --check | --apply
"""
import pathlib
import re
import sys

NOTE = pathlib.Path("release_docs/next_version_release.md")
VERSION_FILE = pathlib.Path("src/melder/__version__.py")
SECTION = '''## A notch whose new version fails its check is refused, and nothing moves

`notch_spell` checks a version the first time it makes it active - its structure: what its constructor needs and
whether each need resolves to one provider. Until {V} the check ran after the switch, and nothing undid the switch
when it failed: `notch_spell` raised `SpellbookValidationError`, yet the index stayed on the broken version, its
borrowers stayed on the old one, and neither the old version (by its spell_id) nor the index (by address) could be
melded until a notch back. Now a failing check puts everything back before the error is raised:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class Clock(Protocol):
    def now(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class UtcClock:
    def now(self) -> str:
        return "12:00 UTC"


class LocalClock:
    def now(self) -> str:
        return "06:00 local"


class TimedGreeter:                    # needs a Clock - and two are registered
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
timed = world.bind_inactive(spell=TimedGreeter, spell_index=index, spellframe=Greeter, binding_name="greeter",
                            existence="many")

try:
    world.notch_spell(spell_index=index, spell_id=timed)
except md.SpellbookValidationError as error:
    print(str(error).splitlines()[0])
    # notch_spell refused: 'TimedGreeter' (spell_id ...) failed its structural check, so the notch did not
    # happen; 'English' (spell_id ...) is still the active version of the index.

assert index.selected_spell_id == english      # it selected TimedGreeter until {V}
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised until {V}
```

- The error is still `SpellbookValidationError` with the same validation report; its first line now says the notch
  did not happen and names the version still active (or says the index still has none).
- After the refusal the index selects the version it selected, that version is active and melds by spell_id and by
  address, the refused version is parked again, borrowers never moved, MutationResearch records no promotion for
  it, and Nexus publishes the old version. A retry is checked, and refused, again.
- Any failing check is refused the same way: a constructor that takes its own class (`SELF_DEPENDENCY`) as well as
  an ambiguous provider (`AMBIGUOUS_PROVIDER`, above).
- `SpellbookValidationError` takes an optional keyword `preface`: one line of text put before the report, as the
  refusal does. Anything but a non-empty, single-line `str` raises `TypeError`; without it the message is unchanged.

What stays the same: a notch to a sound version, a notch to the active version (it changes nothing), a notch back to
a version used before, the error's type, and borrowers following a notch that stands.

'''
PACKAGING = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the refused notch - the check inside the notch window, what the reversal puts back, the refusal line\n"
    "  and the error's `preface`; the code-map extents of the changed files are remeasured, and their line citations\n"
    "  remapped.\n"
)
REBUILD = re.compile(r"^- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for \S+\.\n", re.M)


def main() -> None:
    """Apply the edits in memory with the landed version; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    version = re.search(r'^__version__ = "([0-9.]+)"$', VERSION_FILE.read_text(encoding="utf-8"), re.M).group(1)
    raw = NOTE.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the release note")
    text = raw.decode("utf-8")
    before = text.count("\n")
    header = re.match(r"# Melder (\S+)\n", text)
    if header is None:
        raise SystemExit("no header line")
    if header.group(1) == version:
        raise SystemExit("the header already names %s: notch first, then run this once" % version)
    text = "# Melder %s\n" % version + text[header.end():]
    anchor = "## Packaging and documentation\n"
    if text.count(anchor) != 1:
        raise SystemExit("packaging anchor found %d times" % text.count(anchor))
    section = SECTION.replace("{V}", version)
    text = text.replace(anchor, section + anchor)
    found = REBUILD.findall(text)
    if len(found) != 1:
        raise SystemExit("rebuild line found %d times" % len(found))
    rebuild = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for %s.\n" % version
    text = REBUILD.sub(lambda _match: PACKAGING + rebuild, text, count=1)
    for line in (section + PACKAGING + rebuild).split("\n"):
        if len(line) > 120:
            raise SystemExit("line over 120 chars: " + line)
    print("release note: %d -> %d lines; header %s -> %s" % (before, text.count("\n"), header.group(1), version))
    if sys.argv[1] == "--apply":
        NOTE.write_bytes(text.encode("utf-8"))
        if NOTE.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
