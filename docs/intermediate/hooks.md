# Observe registration and runtime lifecycles

Prerequisite: [configuration](configuration.md). Hooks attach observation to a
book or registration so call sites can keep using ordinary `meld` and lifecycle verbs.

## Pick the boundary you need

| Boundary | Registration surface | Saved demonstration |
| --- | --- | --- |
| Bind registration | `book.add_bind_hooks(pre=..., activation=..., post=...)` | Check the reference, annotate its Spell, observe registration |
| Spell creation | `SpellBinder.with_pre_hook`, `with_activation_hook`, `with_post_hook` | Record construction events |
| Meld | `configuration.add_hook(book.id, name, callback)` | Observe pre/post resolution |
| Conduit | The same book-keyed hook registration | Observe creation and cleanup |
| Links and contracts | The same book-keyed hook registration | Observe linking, pull, and sever |

Register callbacks before the lifecycle operation you intend to observe. For
configuration-based Conduit/Meld hooks, a Book ID selects Book-specific events;
omitting it supplies defaults. Bind hooks belong to the Book itself and use the
three named stages below.

## Follow a binding through its three stages

Intermediate 40 is the runnable bind-hook example. Its callbacks receive these subjects:

| Stage | Callback argument | Timing and purpose |
| --- | --- | --- |
| `pre` | The exact class, function or existing object passed to bind | Before reflection; check the reference and raise to reject it |
| `activation` | The actual new `Spell` | Before publication; inspect it and add application metadata or tags |
| `post` | That `Spell` after registration | Inspect the registered result or record an application audit |

```python
book.add_bind_hooks(
    pre=[check_reference],
    activation=[configure_spell],
    post=[observe_registration],
)
```

Pass sequences of synchronous callbacks. Calls append in order; returning `False`
does not reject a reference, and returning another object does not replace it.
Raise an exception to reject. Melder wraps callback failures in `HookExecutionError`
and preserves their `phase`, `hook_name`, and `original_exception`.

Bind activation constructs/configures the **Spell definition**. It does not create
the application object. The older fluent creation-hook lesson runs callbacks during
Meld instead. Intermediate 40 proves this distinction: binding records pre → activation
→ post, and a later `meld("Report")` leaves that bind-event list unchanged.

## Configure once or adjust future bindings

For initial callbacks, call `configuration.with_bind_hooks(...)` before constructing
the Book. Each Book captures those seeds during construction. Runtime
`book.add_bind_hooks(...)` then appends to that Book's own registry.

`book.clear_bind_hooks()` removes all three stages from future bindings. Register
them again with `add_bind_hooks`; an empty sequence does not clear a stage.
The normal Conduit exposes the same `add_bind_hooks` and `clear_bind_hooks` methods.
These methods remain usable after configuration freezes, subject to the existing
rules for actually binding new definitions. Lessers cannot change their borrowed
Book's bind hooks through the Conduit facade.

An in-flight bind keeps one captured callback set; updates affect subsequent binds.
Clearing does not erase metadata from earlier Spells or remove their creation hooks.
Shared configuration does not turn runtime Bind-hook edits into cross-Book updates.

Post-bind runs after registration, before any enclosing transaction's final completion.
A post-hook failure can leave the binding registered. The
[expert bind-hook lesson](../expert/bind-hooks.md) demonstrates that case alongside
agent-supplied reference checks and changes to the actual Spell.

## Keep the result separate from the observation

A hook records a moment in a lifecycle. The meld still supplies the resolved
object. Use the meld-hook lesson's repeated resolutions and event counts as a
small working pattern; use the conduit lesson when cleanup observation matters.

For the dynamic arc, read [linking](dynamic-linking.md) before the link-hook lesson.
The latter observes the same owner/borrower operations; it adds no alternative
sharing procedure.
