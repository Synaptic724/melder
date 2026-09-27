# Melder 0.2.82

This release makes Aether find any conduit in a frame - a named lesser at any depth by name, any live
conduit by id - and gives the root-only lookups `*_root_*` names, and it makes scope teardown run every
declared disposal method even after one of them raises, reporting each failure with its cause. One rename
is breaking: the root-only Aether lookups, listed below with their new names.

## Aether finds any conduit by name or id; root-only lookups carry root names

`Aether.get_conduit_by_name` now finds every named scope in a frame - a named root, or a lesser created
with `create_lesser_conduit(name=...)` at any depth - and `Aether.get_conduit_by_id` finds any live
conduit, anonymous lessers included:

```python
root = book.conjure(name="app")
request = root.create_lesser_conduit(name="request")
job = request.create_lesser_conduit()

aether = Aether()
assert aether.get_conduit_by_name("request") is request
assert aether.get_conduit_by_id(job.id) is job
```

Before, both answered over root conduits only, so `get_conduit_by_name("request")` raised "not found"
while the frame's `ConduitCloud` returned the scope.

- **Breaking change: the root-only lookups are renamed, with no aliases.** `list_conduit_ids`,
  `list_conduit_names`, `count_conduits`, `has_conduit_id`, `has_conduit_name` and
  `find_conduit_id_by_name` are now `list_root_conduit_ids`, `list_root_conduit_names`,
  `count_root_conduits`, `has_root_conduit_id`, `has_root_conduit_name` and
  `find_root_conduit_id_by_name`; the old names raise `AttributeError`. Root-only lookups by name and
  by id are `get_root_conduit_by_name` and `get_root_conduit_by_id`.
- **`get_conduit_by_name` and `get_conduit_by_id` keep their names and cover more.** Every root still
  resolves to the same object. Code that relied on a lesser's name or id raising "not found" should use
  the root lookups.
- **Lookups stay per frame.** Every lookup takes `aetheric_frame_name`, a string that defaults to
  `"default"`; a scope in another frame is found by naming that frame. A frame given as anything but a
  string, such as `None`, now raises `TypeError` instead of a misleading "does not exist" error.
- **Errors name the frame.** A miss reads `Conduit with name 'request' not found in frame 'default'.`,
  followed by what the lookup covers; the usual cause is a scope that lives in another frame.
- **Returned and cleaned scopes do not resolve.** A lesser returned to its pool leaves both lookups. The
  reference you get is borrowed and does not keep the scope alive.
- **`ConduitCloud.list_conduits()`** returns one frame's named conduits as a tuple:
  `Aether().get_conduit_cloud().list_conduits()`.
- **Id lookups tolerate scopes coming and going.** The walk behind `get_conduit_by_id`, which the room
  commands of the same name also use, reads snapshots, so a lesser returning to its pool on another thread
  can no longer make it fail with `dictionary changed size during iteration` on free-threaded Python.
- **Room commands are unchanged.** The Nexus room commands and viewer methods of the same names keep
  their behaviour and access control.

## Disposal runs every method and reports every failure

When one of an object's disposal methods raises, Melder now still runs the methods declared after it. With
a book whose `disposal_method_names` is `["close", "release"]`, an object whose `close()` raises still has
`release()` called; before, `release()` was skipped and whatever it releases leaked.

- **One error per failing method, with the real cause.** `purge`, leaving a `with conduit.enter_spellspace()`
  block and the other scope teardowns raise the same `ExceptionGroup` as before, and conduit cleanup still
  logs it. The group now holds one `RuntimeError` per failing method instead of one per object, and each
  error's `__cause__` is the exception the method raised, with its type and traceback.
- **One bad object cannot stop the rest.** Reporting a failure no longer relies on the failing object's
  `__str__`; an object whose `__str__` also fails is named by type and id, and the other objects in the
  scope are still disposed.
- **Order is unchanged.** Methods run in the order the book declares them, and objects are disposed newest
  first, as before.

## Packaging and documentation

- The README now includes the roadmap artwork after the product introduction, with quick navigation,
  a full-size image link and a link to the detailed milestones.
- The packaged system documents (`melder.__architecture__`, `__components__`, `__graph_network__` and
  `__graph_details__`) are regenerated and describe what each Aether conduit lookup covers (the root-only
  `*_root_*` family, `get_conduit_by_name` over named scopes and `get_conduit_by_id` over every live
  conduit) and disposal that runs every declared method and reports each failure.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.82.
