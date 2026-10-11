# Melder 0.2.8233

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

## Index links, contract reads and binds across frames hold up under concurrent changes

On the free-threaded build, a few operations that touch more than one object could fail - or leave linked conduits
out of step - when another thread changed one of those objects at the same moment (0.2.8231-0.2.8233):

- `Conduit.cleanup_spell`, `notch_spell`, `add_to_spell_index`, `remove_from_spell_index` and `bind_inactive` tell
  index-link borrowers about the change after the change has committed. A `link` or `sever_link` of the same conduit
  at that moment made them raise `RuntimeError: dictionary changed size during iteration` with the change already
  made, and could leave a borrower subscribed to an index that no longer exists, or holding no active copy of the
  lineage after a notch. The notification now holds the conduit's ward lock, so the link or sever waits for it.
- `Conduit.get_spell_in_contracts` and `get_spells_in_contract_by_conduit` (and its by-name variant) could raise the
  same error, `RuntimeError: Detail has already been cleaned.` or an `AttributeError` while the lending conduit added
  or removed index members. They now read each contract under its own lock, by key where they can.
- `get_spells_in_contract_by_conduit` could hang for good when the same conduit ran `sever_link` or `link` at the
  same time: the two took the same two locks in opposite orders. It now resolves spells through the conduit's
  Spellbook and never takes the conduit's lock.
- With two or more frames under process-wide spell ids (the default), `bind` checks every other frame for the new
  spell id. A frame born (a tenant's first Spellbook) or torn down at that moment made the bind fail with
  `dictionary changed size during iteration`, `AethericFrame has already been cleaned.` or an `AttributeError`. The
  check now reads a list of frames that Aether replaces whenever a frame is born or removed, so a bind copies nothing.
- `conjure` could fail its duplicate-id check with `RuntimeError: Set changed size during iteration` while another
  Spellbook of the same frame bound spells. The frame now copies each Spellbook's ids in one step, which is also
  faster.
- `Conduit.find_contracted_spell` could raise `RuntimeError: dictionary changed size during iteration` while another
  conduit linked to or severed from the one it was asked on. It now copies the list of linked conduits in one step
  and takes no lock (0.2.8232).
- `Spellbook.inspect_spell` and `Conduit.inspect_spell` could return `None` for a registered object while a
  Spellbook was conjured or torn down in the same frame, and could hang against a frame being torn down at the same
  moment, because they held the Spellbook's (and the conduit's) lock while asking the frames. They now walk a copy of
  the frame's conduits and hold no lock while the frames answer (0.2.8232).
- Two `cleanup_spell` calls for the same spell at the same moment both ran the disposal, and one of them then
  failed part-way through. The second now raises
  `RuntimeError: cleanup_spell: spell <id> is already being disposed by another call.` before it changes anything,
  and borrowers hear of a destroyed index once (0.2.8232).
- Calling `cleanup()` directly on a live `Spell` could hang for good when its Spellbook was torn down (`cleanup()` on
  the root conduit, the Spellbook or its frame) or conjured at the same moment: the call held the spell's lock while
  it waited for the Spellbook's, and the teardown or conjure held the Spellbook's lock while it waited for the
  spell's. The call now lets go of the spell's lock before it asks the Spellbook to remove the spell, and a second
  direct `cleanup()` of the same spell still waits for the first and returns. A direct call racing its Spellbook's
  teardown returns once the teardown has cleaned the spell, or raises `RuntimeError: Spellbook has already been
  cleaned.` (0.2.8233).

Three errors change type: a second `cleanup_spell` of a spell already disposed raises
`RuntimeError: cleanup_spell: spell <id> has already been disposed.` instead of
`AttributeError: 'Spell' object has no attribute 'spell_index'`; `AethericFrame.has_spell` or `spells_in_index`
racing the frame's cleanup raises the documented `RuntimeError: AethericFrame has already been cleaned.` instead of an
`AttributeError`; and `Spellbook.cleanup_and_remove_spell` waiting on a Spellbook that is torn down meanwhile raises
`RuntimeError: Spellbook has already been cleaned.` (or returns, when the teardown has cleaned the spell it was given)
instead of `AttributeError: ... object has no attribute '_spells_by_id'` (0.2.8233). Everything a quiet system returns
is unchanged, and the only new lock is one per spell that a direct `Spell.cleanup()` takes and nothing else does.

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
- The packaged system documents describe the ward-lock rule for index-link notifications, the contract-lock
  rule for contract reads, the frame list bind's cross-frame check reads, and how `cleanup_spell` reports the
  index it destroyed.
- The packaged system documents describe the lock-free contracted lookup and inspection and the in-flight disposal
  mark of `cleanup_spell`.
- The packaged system documents describe how a direct `Spell.cleanup()` removes the spell outside the spell lock and
  how `cleanup_and_remove_spell` treats a Spellbook torn down while it waits.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8233.
