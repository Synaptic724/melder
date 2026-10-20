"""S5: take the notch 0.2.8244 -> 0.2.8245 and extend the running release note's managed section."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
VERSION = ROOT / "src/melder/__version__.py"
NOTE = ROOT / "release_docs/next_version_release.md"

version = VERSION.read_text(encoding="utf-8")
assert version.count('__version__ = "0.2.8244"') == 1, "version is not 0.2.8244 - another lane landed; re-read"
VERSION.write_text(version.replace('__version__ = "0.2.8244"', '__version__ = "0.2.8245"'), encoding="utf-8")

note = NOTE.read_text(encoding="utf-8")
edits = [
    ("# Melder 0.2.8244\n", "# Melder 0.2.8245\n"),
    (
        """A seventh Existence member is on its way for objects that are expensive to build and safe to reuse - a logger, a
client, a parser. A meld, or an injection into a constructor, will lease an idle object from the spell's pool, kept
by the root conduit that owns the binding, or build one; the holder gives the object back explicitly and the next
lease reuses it. 0.2.8241 added the member and its place in Melder's lifetime rules, 0.2.8242 its bind options,
0.2.8243 its pool in the owning root and 0.2.8244 the way objects go back (`ReleaseManagedSpell`); leasing through
a meld follows, and until it lands a managed binding cannot be melded.
""",
        """A seventh Existence member for objects that are expensive to build and safe to reuse - a logger, a client, a
parser. A meld, or an injection into a constructor, leases an idle object from the spell's pool, kept by the root
conduit that owns the binding, or builds one; the holder gives the object back explicitly and the next lease reuses
it. 0.2.8241 added the member and its place in Melder's lifetime rules, 0.2.8242 its bind options, 0.2.8243 its pool
in the owning root, 0.2.8244 the way objects go back (`ReleaseManagedSpell`) and 0.2.8245 leasing through a meld
(`Conduit.managed_spell_meld` included); the rules for pools in an ownership transfer come next.
""",
    ),
    (
        """- Releasing trusts the caller: nothing records which objects are out, so give back only what a lease handed you,
  once.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values or record changes; a root store without managed spells disposes exactly as before.
""",
        """- Releasing trusts the caller: nothing records which objects are out, so give back only what a lease handed you,
  once.

Leasing works from 0.2.8245. A meld of a managed spell, and every injection of one into a constructor, takes an idle
object from the pool, or builds one when none is waiting; the plan Melder compiles for the meld does it inline:

```python
parser = conduit.meld(Parser)            # an idle parser, or a new one
release(parser)                          # the next lease gets this object back

handler = conduit.meld(Handler)          # Handler(parser: Parser) is `many`: each meld leases one parser into it
release(handler.parser)

with conduit.managed_spell_meld(Parser) as p:   # meld and lease in one call; given back when the block ends
    p.parse(text)
```

- Each injection is its own lease: two constructors in one meld get two objects, and a holder keeps what it was
  given for its life. A meld through a lesser conduit or a spellspace leases from the owning root's pool.
- A warm cycle - a meld that takes an idle object, plus its release - measured about 0.32 us on an automatic root
  and 0.74 us on a dynamic one (CPython 3.14t, either GIL mode): about one release more than a `many` meld.
- A `limited_quantity` meld raises `ManagedSpellExhaustedError` when every object is out, and a `queue` meld waits
  for a release up to its timeout; nothing is built while it waits or when it raises.
- When a construction fails after it was handed leased objects - its constructor raises, a sibling dependency
  fails, or another meld finished the same shared object first - Melder gives those objects back to their pools
  before the error propagates, and a failure to give one back is added to the error as a note. It is the one case
  Melder returns an object itself.
- Overrides: a value supplied for the holder's parameter takes no lease; values supplied for the managed spell's
  own parameters build a fresh object with them, which the pool neither hands out nor counts.
- The `many` dependencies with disposal methods that a pooled object was built with stay with it, and are disposed
  with it when an elastic pool trims it or the root ends.
- A direct meld of a managed spell runs its activation hooks (the spell's and `on_meld_activation`) on every lease,
  a reused object included.
- `Conduit.managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)`
  resolves its target as `meld` does and returns a `ManagedSpellLease`. It refuses a spell of another existence
  before melding anything ("managed_spell_meld leases a managed spell; 'Config' is unique. Meld it with meld(), or
  bind it with existence=Existence.managed_spell_quantity."), and raises `MeldExecutionError` ("Managed spell
  'Parser' has no pool to lease from: its owner root was torn down, ...") when the version has no pool. A lease on
  an object built fresh by own-parameter overrides gives that object to the pool when it is released.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values, record or compiled plan changes; a root store without managed spells disposes exactly as before.
""",
    ),
    (
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8244.\n",
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8245.\n",
    ),
]
for old, new in edits:
    assert note.count(old) == 1, old[:70]
    note = note.replace(old, new)
long = [line for line in note.splitlines() if len(line) > 120]
assert not long, long
NOTE.write_text(note, encoding="utf-8")
print("notched 0.2.8245; release note extended")
