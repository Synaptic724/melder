# Melder 0.2.8230

**Unreleased**

## `scan_bind` takes every option `bind` takes, and registers only what a module declares

`@scan_bind(...)` now accepts the three target options it was missing - `resolvable`, per-target
`disposal_method_names` and keyword application metadata - with the defaults `Spellbook.bind` uses, and a scan
passes them through `bind`. A scanned registration therefore matches a direct `bind` of the same target with
the same options: a `Protocol` can be declared as a non-resolvable definition, a target can name its own
disposal methods (combined with the Book's configured names and priority exactly as in `bind`), and metadata
lands in `Spell.metadata`.

```python
@md.scan_bind(existence="unique", permissions="create", disposal_method_names=["close"], owner="billing")
class Ledger:
    def close(self) -> None: ...
```

The declaration is checked when the decorator runs: `disposal_method_names` must be a list or tuple of method
names (a bare string is refused - `bind` would read it one character at a time), and a metadata key that names
an argument the bind pipeline takes itself (`spell`, `existence`, `profile`, `spell_id` and the rest, 24 in all)
raises `TypeError` naming every such key. Metadata is kept as a shallow snapshot: later changes to your dict do
not reach the declaration, while the values are the objects you passed. `resolvable` is stored as given, and
`bind` checks it when the module is scanned.

**Breaking change:** only an object that carries its own declaration is registered. An undecorated subclass of
a decorated class used to be bound with its parent's declaration; it is now skipped - decorate the subclass to
register it. A module-level instance of a decorated class, a class whose metaclass was decorated and an object
that answers every attribute are skipped too (the instance and that object used to make the scan fail). A second
module name for the same object (`Alias = Thing`) no longer fails the scan with "Spell ID collision": the object
is bound once, under the first name in module order.

What stays the same: `existence` and `permissions` are still required on `scan_bind`, and hooks are still
validated at decoration; only the module you pass is scanned and re-exports are still refused; two different
objects that share a binding key, and scanning the same module twice, still raise. A scan is still not atomic:
if one target's bind fails, the targets bound before it stay registered. The `Spellbook.scan` docstring said the
scan rolled back with its transaction window; it never did, and the docstring now says so.

## Spell lookups and validation no longer fail while other spells change

`Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` on top of it, used to walk the Book's index map while
other threads bound, removed or parked spells. On the free-threaded build a lookup of a spell nobody was touching
could then raise `RuntimeError: dictionary changed size during iteration`, raise
`AttributeError: 'SpellIndex' object has no attribute '_spells_in_index'`, or return `None` for a spell that was
still registered. The lookup now answers from the Book's id maps: one read for a current version id, three for a
superseded or parked one, the same cost at any Book size, and no lock taken.

What stays the same: any id in a spell's version lineage resolves to the live spell that represents it now -
after a notch, an index move or an ownership transfer too - and an id the Book does not own still returns `None`,
as does a parked version moved out into an index of its own. Two answers sharpen: a parked version disposed while
a lookup runs returns `None` instead of raising, and a lookup that lands inside a notch or an ownership transfer
of that same lineage can return `None` for that instant, as a lookup inside a notch already could. The returned
spell is a reference you borrow, not a lease: a later removal, notch or transfer can retire or move it.

The same fix reaches the other places that walked a Book's spells while other threads changed them (0.2.8230).
`Conduit.get_spell_permissions` and the Rift command surface's spell lookup now answer from the id maps too;
`Conduit.validate_resolution`, `Spellbook.inspect_spell` searching the frame's other Books, contract lookups and
the ownership-transfer impact check walk a snapshot; and a `bind` on another thread now waits for a walk that holds
the Book's lock instead of resizing the map under it. None of them can raise
`RuntimeError: dictionary changed size during iteration` any more. `SpellIndex.has_spell` racing the index's
cleanup raises its documented `RuntimeError: SpellIndex has already been cleaned.` instead of `AttributeError`, and
a contract lookup that meets an index its owner has cleaned treats it as holding nothing instead of raising.
Answers on a quiet Book are unchanged.

`Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` keep raising `ValueError` for an id no conduit in
the frame claims, as `get_*` lookups do (a `find_*` lookup returns `None`); their docstrings said they return
`None`, and now document the raise. `get_conduit_by_spell_id` is annotated as returning a `Conduit`.

## Packaging and documentation

- The README's "Declarative Binding by Module" example passes `permissions="create"`, without which it raised
  `TypeError`, and says that `scan_bind` takes `bind()`'s target options and does not register subclasses or
  instances of a decorated class.
- The packaged system documents (`melder.__components__`, `melder.__architecture__`) describe the scan
  declaration contract, the eligibility change and a scan flow; the scan code-map extent is remeasured.
- The packaged system documents describe how `find_spell_by_id` resolves version ids from the Book's id maps
  and why it takes no lock.
- The packaged system documents describe the Book-lock rule for the spell maps' writers, the snapshot rule for
  walks that cannot hold that lock, the cleanup-safe membership probe and the documented ValueError of the
  Conduit spell lookups.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8230.
