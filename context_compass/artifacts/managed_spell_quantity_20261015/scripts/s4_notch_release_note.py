"""S4: take the notch 0.2.8243 -> 0.2.8244 and extend the running release note's managed section."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
VERSION = ROOT / "src/melder/__version__.py"
NOTE = ROOT / "release_docs/next_version_release.md"

version = VERSION.read_text(encoding="utf-8")
assert version.count('__version__ = "0.2.8243"') == 1, "version is not 0.2.8243 - another lane landed; re-read"
VERSION.write_text(version.replace('__version__ = "0.2.8243"', '__version__ = "0.2.8244"'), encoding="utf-8")

note = NOTE.read_text(encoding="utf-8")
edits = [
    ("# Melder 0.2.8243\n", "# Melder 0.2.8244\n"),
    (
        """lease reuses it. 0.2.8241 added the member and its place in Melder's lifetime rules, 0.2.8242 its bind options
and 0.2.8243 its pool in the owning root; the release call and leasing through a meld follow, and until they land
a managed binding cannot be melded.
""",
        """lease reuses it. 0.2.8241 added the member and its place in Melder's lifetime rules, 0.2.8242 its bind options,
0.2.8243 its pool in the owning root and 0.2.8244 the way objects go back (`ReleaseManagedSpell`); leasing through
a meld follows, and until it lands a managed binding cannot be melded.
""",
    ),
    (
        """What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values or record changes; a root store without managed spells disposes exactly as before.
""",
        """Objects go back through `ReleaseManagedSpell` (0.2.8244). It, `ManagedSpellLease`, `ManagedSpellMode` and
`ManagedSpellExhaustedError` are importable from `melder`:

```python
from melder import ReleaseManagedSpell

release = ReleaseManagedSpell().release   # bind it once in a hot loop
release(parser)                           # its resets run in order, then it waits for the next lease

with ReleaseManagedSpell().managed(parser) as p:   # given back when the block ends, raised or not
    p.parse(text)
```

- `ReleaseManagedSpell()` is a process singleton like `Aether`: Aether builds it at boot and cleans it with the
  world. A release needs no conduit: the object's class finds its pool with one dict read, then the pool's
  put-back - about 50 ns over the pool call with the method bound once; the `ReleaseManagedSpell()` call itself
  costs about 70 ns more, as `Aether()` does.
- When one class is managed by several pools - two binding names, two roots, two frames, two versions of one
  index - the pool of the version its index selects takes the object. Otherwise pass `spell_id=...` or
  `conduit=...` (a root or one of its lessers); a `ValueError` lists the candidates (spell id, binding, frame,
  root, active) while the choice is still open. A class with no live pool raises "<Class> is not a managed spell
  class in any live root: bind it with existence=Existence.managed_spell_quantity, or its root was torn down."
- `managed(obj)` returns a `ManagedSpellLease`: `release()` gives the object back once and later calls do nothing;
  `object` raises once it was released. `release_all(objects)` attempts every object, then raises one
  `ExceptionGroup` of the failures. `describe(cls)` answers one dict per pool: mode, limit, count, idle and out
  objects, the root holding it (`holding_conduit_id`) and whether it is the active version.
- A reset that raises destroys the object (its disposal methods run) and the error propagates. Once the root ended,
  `release` raises the not-managed `ValueError` (its pools left with it), and a lease made before raises
  `RuntimeError` ("The pool of managed spell 'Parser' was torn down with its root conduit; the object is yours to
  dispose.").
- Releasing trusts the caller: nothing records which objects are out, so give back only what a lease handed you,
  once.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values or record changes; a root store without managed spells disposes exactly as before.
""",
    ),
    (
        """- The internal-bind guard manifest holds 626 entries at 0.2.8243 (622 at 0.2.8227): `HolderDisposalEntry`, the
  record that keeps a slotted object's `many` children with it, joined at 0.2.8238, `ManagedSpellMode` at
  0.2.8242, and the managed pool (`ManagedSpellQuantity`) and `ManagedSpellExhaustedError` at 0.2.8243.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8243.
""",
        """- The internal-bind guard manifest holds 628 entries at 0.2.8244 (622 at 0.2.8227): `HolderDisposalEntry`, the
  record that keeps a slotted object's `many` children with it, joined at 0.2.8238, `ManagedSpellMode` at
  0.2.8242, the managed pool (`ManagedSpellQuantity`) and `ManagedSpellExhaustedError` at 0.2.8243, and
  `ReleaseManagedSpell` and `ManagedSpellLease` at 0.2.8244.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8244.
""",
    ),
]
for old, new in edits:
    assert note.count(old) == 1, old[:70]
    note = note.replace(old, new)
NOTE.write_text(note, encoding="utf-8")
print("notched 0.2.8244; release note extended")
