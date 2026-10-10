# Melder 0.2.8228

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

## Packaging and documentation

- The README's "Declarative Binding by Module" example passes `permissions="create"`, without which it raised
  `TypeError`, and says that `scan_bind` takes `bind()`'s target options and does not register subclasses or
  instances of a decorated class.
- The packaged system documents (`melder.__components__`, `melder.__architecture__`) describe the scan
  declaration contract, the eligibility change and a scan flow; the scan code-map extent is remeasured.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8228.
