"""Add the 0.2.8247 entry to the running release note (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
Header to 0.2.8247, one `##` section before `## Packaging and documentation`, one packaging bullet and the rebuild
line. Each edit refuses unless its anchor occurs exactly once; --check edits nothing. The file stays LF.
"""
import pathlib
import sys

CHECK = "--check" in sys.argv[1:]
PATH = pathlib.Path("release_docs/next_version_release.md")

SECTION = '''## A non-resolvable definition no longer sends every meld of its Book through validation

A Spellbook that registers a definition with `resolvable=False` - a `Protocol` (which must be bound that way), an
abstract base, or a class kept so agents can discover, inspect and version it while its consumers receive the value
by override - paid for validation checks on every meld. Such a definition never receives a resolution verdict, so
Melder counted it as validation still owed for the life of the Spellbook: every meld in that Spellbook, of any
spell, went through the meld-time validation gate, and none took the warm fast path. From 0.2.8247 Melder records
the definition as one that owes no verdict and leaves it out of that decision, so melds in such a Spellbook cost
what they cost without it.

```python
class Clock(Protocol):
    def now(self) -> float: ...


class Report:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


book = md.Spellbook()
book.bind(spell=Clock, existence="unique", resolvable=False)   # discoverable, never resolved
book.bind(spell=Report, existence="many")
root = book.conjure()

report = root.meld(spell=Report, override={"clock": time_source})   # 0.4 us warm; 13 us before 0.2.8247
```

Measured on CPython 3.14t with the GIL off: a warm meld in a Spellbook holding one `Protocol` definition went from
15.1 to 0.26 us after `conjure()` and from 16.4 to 0.73 us after `conjure(dynamic=True)`; the example above went
from 12.9 to 0.39 us, and from 13.2 to 0.40 us with the GIL on.

Notching between versions of one spell index follows the version selected each time: while a `resolvable=False`
version is selected the index is left out, and once a resolvable version is selected again it is validated before
its first meld - in the conduit that owns it and in every conduit that borrows it through an index link.

What stays the same: the definition stays in the graph as before - `bind` and `bind_inactive` accept it, Nexus and
the Rift viewers show it, the Crystallizer records its capability - and a meld of the definition itself is still
refused with the same `MeldExecutionError`. A Spellbook without such a definition, `conjure()` and `bind` cost what
they did, and no public signature changes.

'''

PACKAGING = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe the lineage flag `SpellState.non_resolvable`, the registry's published set of flagged lineages and the\n"
    "  validation flag's exclusion of them; the code-map extents of the six changed files are remeasured, and line\n"
    "  citations into `spellbook.py` and `conduit.py` that had drifted point at their code again.\n"
)


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:60], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw, "release note is not LF"
text = raw.decode("utf-8")
text = replace_once(text, "# Melder 0.2.8246\n", "# Melder 0.2.8247\n")
text = replace_once(text, "## Packaging and documentation\n", SECTION + "## Packaging and documentation\n")
text = replace_once(
    text,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8246.\n",
    PACKAGING + "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8247.\n",
)
long_lines = [(n, len(line)) for n, line in enumerate(text.split("\n"), 1) if len(line) > 120]
assert not long_lines, long_lines
if not CHECK:
    PATH.write_bytes(text.encode("utf-8"))
print(("checked " if CHECK else "edited ") + str(PATH) + f" ({len(text.splitlines())} lines)")
