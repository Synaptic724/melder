# Observe registration and runtime lifecycles

Prerequisite: [configuration](configuration.md). Hooks attach observation to a
book or registration so call sites can keep using ordinary `meld` and lifecycle verbs.

## Pick the boundary you need

| Boundary | Registration surface | Saved demonstration |
| --- | --- | --- |
| Spell creation | `SpellBinder.with_pre_hook`, `with_activation_hook`, `with_post_hook` | Record construction events |
| Meld | `configuration.add_hook(book.id, name, callback)` | Observe pre/post resolution |
| Conduit | The same book-keyed hook registration | Observe creation and cleanup |
| Links and contracts | The same book-keyed hook registration | Observe linking, pull, and sever |

The book ID matters when a configuration serves several books. Register the
callbacks before the lifecycle operation you intend to observe. The runnable
examples collect events in memory so you can inspect what actually fired.

## Keep the result separate from the observation

A hook records a moment in a lifecycle. The meld still supplies the resolved
object. Use the meld-hook lesson's repeated resolutions and event counts as a
small working pattern; use the conduit lesson when cleanup observation matters.

For the dynamic arc, read [linking](dynamic-linking.md) before the link-hook lesson.
The latter observes the same owner/borrower operations; it adds no alternative
sharing procedure.
