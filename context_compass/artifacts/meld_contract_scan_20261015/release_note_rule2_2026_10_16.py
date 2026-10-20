"""Add the 0.2.8250 entry to the running release note (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
Header to 0.2.8250, one `##` section after the 0.2.8249 section (before `## Packaging and documentation`), one
packaging bullet and the rebuild line. Each edit refuses unless its anchor occurs exactly once; --check edits
nothing. The file stays LF and no line passes 120 characters. The two examples are verified as written by
release_example_rule2_2026_10_16.py; the before-0.2.8250 figures come from release_example_rule2_before_2026_10_16.py.
"""
import pathlib
import sys

CHECK = "--check" in sys.argv[1:]
PATH = pathlib.Path("release_docs/next_version_release.md")

SECTION = '''## A satisfied `SpellContract` is not checked on every meld; a notch reaches every spell that depends on the notched one

A spell whose constructor takes a `SpellContract` default - its provider lent by another conduit through
`add_index_to_contract` or `add_spell_to_contract` - had that contract checked again at every meld that went through
the meld-time validation gate: Melder read the constructor's signature, looked each contract up in the Spellbook's
contracted spells and rebuilt the spell's plan, about 1.6 ms a meld. From 0.2.8250 a satisfied contract is not
checked again. Whatever changes what a spell resolves marks the spell for revalidation instead, and its next meld
checks its contracts once and rebuilds against the versions active now, or fails with the error its first meld
would give. A notch is the change that matters most, because the notched version's `__init__` may differ: every
spell that depends on the notched one - by annotation or through a `SpellContract`, directly or through other
spells, in its own Spellbook or another - is marked, and builds the new version at its next meld.

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_id(english).spell_index
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
lender.notch_spell(spell_index=index, spell_id=french)
assert borrower.meld(spell=Banner).text == "BONJOUR"   # rebuilt once, at this meld
```

Measured on CPython 3.14t: a warm meld of `Banner` went from 1558 to 2.8 us with the GIL off and from 1682 to 2.8
us with the GIL on. A change of provider costs one structural pass more at the next meld (0.8-1.1 ms), and a
notch's walk 0.2-0.5 ms more with 200 dependent spells.

A spell that depends on the notched one through an annotation follows it too, two hops away included:

```python
class Clock(Protocol):
    def now(self) -> str: ...


class Utc:
    def now(self) -> str:
        return "utc"


class Local:
    def now(self) -> str:
        return "local"


class Stamp:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


class Report:
    def __init__(self, stamp: Stamp) -> None:
        self.stamp = stamp


book = md.Spellbook()
utc = book.bind(spell=Utc, spellframe=Clock, binding_name="clock", existence="many")
book.bind(spell=Stamp, existence="many")
book.bind(spell=Report, existence="many")
reports = book.conjure(dynamic=True, name="reports")
assert reports.meld(spell=Report).stamp.clock.now() == "utc"

clock_index = reports.get_spell_by_id(utc).spell_index
local = reports.bind_inactive(spell=Local, spell_index=clock_index, spellframe=Clock, binding_name="clock",
                              existence="many")
reports.notch_spell(spell_index=clock_index, spell_id=local)
assert reports.meld(spell=Report).stamp.clock.now() == "local"   # "utc" before 0.2.8250
```

- **Breaking change:** a meld of a contract consumer whose provider's index was destroyed, or whose version grant
  was parked by a notch away, raises `SpellbookValidationError` - the error a first meld raises for a missing
  provider - where it raised `MeldExecutionError` ("SpellContract could not be resolved. Missing contracted
  provider for key (frame_key=..., binding_key=...) on param ..."). Both are `RuntimeError`s; code that caught
  `MeldExecutionError` there catches `SpellbookValidationError`.
- Every lost provider is reported by name - those two, an index unlinked, a link severed, a grant released, and a
  first meld with no provider - where the report said "No validation error was recorded for this spell; its
  validity is invalid, gated or disabled.": "Spell 'Banner' parameter 'greeter' has no provider for its
  SpellContract (frame_key='greeter', binding_key='greeter'): no active spell with that frame and binding name is
  contracted to this Spellbook. Contract one from a linked conduit (add_index_to_contract, or add_spell_to_contract
  for one version) and meld again. [SPELL_CONTRACT_MISSING_PROVIDER]"
- **Breaking change:** a spell that depends on a notched one builds the version now active at its next meld, or
  raises its first meld's error: `UnresolvedInputError` naming the parameter when the new version no longer
  satisfies it, `SpellbookValidationError` naming a dependency whose structure no longer validates. Before, one
  built before the notch went on building the old version, and one never built raised `RuntimeError` on every
  meld (for example "many_only manifest references unknown spell_id '<the old version id>'").
- A version grant (`add_spell_to_contract`) follows its version: a notch away parks the borrower's copy, as before,
  and a notch back makes it active again, so its consumers resolve it at their next meld; a grant of a parked
  version becomes active when that version is notched in. Until 0.2.8250 the copy stayed parked after the notch
  back, and its consumers had no provider until the version was granted again.
- Fixed with the same marks: after `remove_index_from_contract` a consumer kept building the released provider; it
  now fails its next meld as above. After a link or a grant, a spell that depends on a contract consumer kept a plan
  compiled while the provider was missing and built the consumer with its raw `SpellContract` default
  (`AttributeError: 'SpellContract' object has no attribute '...'`); it now rebuilds.
- Not changed yet: a meld of a borrower's contract consumer on another thread while its lender notches the provider
  can, on the free-threaded build with the GIL off, fail with an internal `RuntimeError` or return the consumer
  built with its raw `SpellContract` default, as before 0.2.8250; the next meld is correct. A follow-up orders such
  melds against the notch.

What stays the same: a mark changes state only - nothing is built, disposed or extracted when a provider changes,
and objects already built keep what they were built with (a `unique` consumer keeps its object after a notch and
builds the new version once it is purged). A spell whose providers did not change takes the warm path; first
melds, `conjure()` and `link` check contracts as before, and a dynamic world still accepts a consumer before its
provider is linked. No public signature changes.

'''

PACKAGING = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the contract recheck: the borrower Spellbook's marks, a notch's downstream walk, the meld's refresh of\n"
    "  stale dependencies, the lost-provider report and a version grant's return on a notch back; the code-map\n"
    "  extents of the changed files are remeasured, and their line citations remapped.\n"
)


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:60], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw, "release note is not LF"
text = raw.decode("utf-8")
assert "0.2.8250" not in text
text = replace_once(text, "# Melder 0.2.8249\n", "# Melder 0.2.8250\n")
text = replace_once(text, "## Packaging and documentation\n", SECTION + "## Packaging and documentation\n")
text = replace_once(
    text,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8249.\n",
    PACKAGING + "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8250.\n",
)
long_lines = [(n, len(line)) for n, line in enumerate(text.split("\n"), 1) if len(line) > 120]
assert not long_lines, long_lines
if not CHECK:
    PATH.write_bytes(text.encode("utf-8"))
print(("checked " if CHECK else "edited ") + str(PATH) + f" ({len(text.splitlines())} lines)")
