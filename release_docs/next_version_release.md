# Melder 0.2.50

**Unreleased**

This release adds named lesser conduits with discovery through ConduitCloud, configurable bind
lifecycle hooks, and scoped creation purge. It also fixes hook isolation when scopes are reused
and gives conduits upgraded from lesser scopes an independent Spellbook.

## Named lesser conduits and ConduitCloud discovery

Give a lesser conduit a name when creating it so other parts of an application can find the same
active scope through its frame's **ConduitCloud**. This works in both automatic and dynamic mode,
including when the scope comes from a prewarmed pool.

Given an existing root conduit:

```python
cloud = root.get_conduit_cloud()
job = root.create_lesser_conduit(name="job-42")

try:
    discovered = cloud.get_conduit_by_name("job-42")
    assert discovered is job
    assert cloud.get_conduit_by_id(job.id) is job
finally:
    job.cleanup()

assert not cloud.has_conduit_name("job-42")
```

ConduitCloud now exposes named normal and lesser conduits through the same discovery APIs:

| API | Result |
| --- | --- |
| `get_conduit_by_name(name)` | The active conduit registered under that name |
| `get_conduit_by_id(conduit_id)` | The named conduit registered under that ID |
| `list_conduit_names()` / `list_conduit_ids()` | Snapshots of registered names or IDs |
| `has_conduit_name(name)` / `has_conduit_id(conduit_id)` | Whether that scope is registered |
| `find_conduit_id_by_name(name)` | Its ID, or `None` when the name is absent |

Names are exact, nonempty strings and must be unique among active named conduits in the same
`AethericFrame`. Duplicate names are rejected. Supply a lesser conduit name at creation; an active
lesser cannot be renamed afterward.

**Cleanup removes the name and ID from discovery before the conduit returns to its pool.** The name
can then be reused. A later acquisition receives its own name or remains unnamed; it never inherits
the previous use's name. Unnamed lesser conduits stay outside ConduitCloud's named directory.

Naming preserves the scope's lesser status, shared Spellbook and existing `Existence` rules.
Discovery returns a reference to the live scope without extending its lifetime. The scope's owner
remains responsible for cleanup; do not continue using a discovered reference after that cleanup.

In dynamic mode, `upgrade_to_normal(name=...)` can keep the lesser conduit's name or select another
available name. Discovery follows the promoted conduit, which keeps its ID and receives its own
empty Spellbook.

### Nexus discovery and structural restore

Named lesser conduits are also available through authorized Nexus capability and codegen lookup.
Capability rooms can pass `name=` to `create_lesser_conduit`. Existing ACLs and lesser-conduit
restrictions still apply. Use the existing Rift projection refresh when scope membership changes.

When dynamic structural recording is enabled, Crystallizer preserves named lesser conduits and
the parent relationships needed to rebuild their hierarchy, including required unnamed ancestors.
Cleanup and name reuse affect subsequent checkpoints while sealed checkpoints retain their history.
Restore creates fresh conduit identities; previously created application objects and their mutable
state are not restored.

The record schema advances to **3.0.0** for named-scope topology. Older readers reject the new schema;
valid older root-only recordings remain readable. During live restore, pause ordinary scope creation,
cleanup and lineage changes until restoration finishes.

## Bind lifecycle hooks

Spellbook now supports callbacks at three points in registration:

| Stage | Callback receives | Use it to |
| --- | --- | --- |
| `pre` | The supplied class, function or existing object | Check a reference before reflection; raise to reject it |
| `activation` | The newly created `Spell` | Inspect or annotate the definition before publication |
| `post` | The registered `Spell` | Observe the completed registration |

```python
book.add_bind_hooks(
    pre=[check_reference],
    activation=[configure_spell],
    post=[observe_registration],
)
```

Callbacks are synchronous and run in registration order. Return values are ignored; raise an
exception to reject an operation. Callback failures raise `HookExecutionError` with the original
cause and the failing stage. A post-hook failure can leave the binding registered because post
runs after registration, before an enclosing transaction necessarily completes.

Use `clear_bind_hooks()` to remove all three stages from future binds, then `add_bind_hooks()` to
register replacements. Both methods are available on Spellbook and normal Conduit instances.
Each Spellbook owns its callback registry; an in-progress bind keeps the callback set it started with.

Configure initial callbacks with `SpellbookConfiguration.with_bind_hooks(...)` before constructing
the Spellbook. Runtime add/clear operations remain available after configuration freezes. These
callbacks concern binding definitions; existing application-object creation hooks still run during
meld. Crystallizer records hook presence, while restoring callback code remains application setup.

## Hook isolation during scope reuse

Reused lesser conduits and SpellSpaces no longer retain temporary Meld callbacks from a previous
use. Cleanup disposes the scope's creations and resets temporary hooks **before returning it to
the pool**. This also covers manual, managed and prewarmed SpellSpaces.

On acquisition, a SpellSpace selects its owner's current Meld hooks. Active SpellSpaces retain
their selected hook source until their next acquisition when the owner switches between local
and shared hook maps.

### Update local or shared runtime hooks

`Conduit.register_conduit_hooks(...)` accepts `create_local_hooks=True` and `overwrite=False`.
It appends locally by default. `Conduit.set_conduit_hooks(...)` provides local replacement by default:

```python
# Add a local callback.
conduit.register_conduit_hooks({"on_meld_pre_resolve": before_meld})

# Replace this conduit's Meld hook family.
conduit.set_conduit_hooks({"on_meld_pre_resolve": replacement})

# Update the shared Meld hooks from the normal root.
root.set_conduit_hooks({"on_meld_pre_resolve": replacement}, create_local_hooks=False)

# Clear the shared Meld hook family.
root.set_conduit_hooks({"on_meld_pre_resolve": []}, create_local_hooks=False)
```

- Setting replaces the supplied hook families: Conduit lifecycle, Meld, or both. Omitted families
  remain unchanged; an empty mapping selects both families.
- Clearing local lifecycle hooks reveals inherited callbacks. Clearing local Meld hooks mutes that
  scope until its hooks change again or it returns to the pool.
- Shared updates are normal-root-only and reach scopes using the shared baseline. Explicit local
  copies remain isolated. Runtime updates do not modify frozen configuration or other normal roots.
- `Meld.register_meld_hooks(...)` provides matching registration controls for Meld hooks.
  `hooks_modified` on Conduit and Meld reports temporary local hook state.
- Invalid callback batches are rejected before either family changes. Use the public methods;
  direct mutation of internal lists or dictionaries is not tracked.

## Independent Spellbooks after lesser-to-normal upgrade

After `Conduit.upgrade_to_normal(...)` succeeds, the same conduit is fully conjured with its own
empty Spellbook, ready for independent binding and resolution. Its object identity, ID and retained
creations are preserved. The upgrade happens in place; the method returns `None`.

```python
lesser = root.create_lesser_conduit(name="job-42")
lesser.upgrade_to_normal("job-42")

lesser.bind(spell=Service, existence="unique_per_conduit", permissions="create")
service = lesser.meld(Service)
```

Previously, an upgraded conduit could continue using its former root's Spellbook, allowing binding,
hook changes or cleanup to affect that root. Each normal conduit now owns its registrations and
cleanup independently.

**The upgraded conduit inherits no spell definitions or contracts.** Bind the definitions it needs
explicitly. Earlier creations remain its disposal responsibility, but their old spell IDs are no
longer resolvable through the new Spellbook.

Pass an optional same-frame `SpellbookConfiguration` to customize the new Spellbook:

```python
configuration = SpellbookConfiguration("application").with_defaults()
configuration.with_bind_hooks(pre=[check_reference])
configuration.with_hooks(on_meld_pre_resolve=before_meld)

# The lesser must already belong to the "application" frame.
lesser.upgrade_to_normal("independent", configuration=configuration)
```

| Configuration mode | New Spellbook setup |
| --- | --- |
| Local, configuration omitted | Fresh defaults and empty hooks |
| Local, fresh matching configuration supplied | Supplied configuration and its initial hooks |
| Frame-wide sharing enabled | The frame's frozen shared configuration; a different supplied object is rejected |

Frame-wide sharing shares configuration, not Spellbooks or registrations. Configured defaults may
seed the new Spellbook's hooks, while runtime hook changes remain independent. Former Spellbook
hooks and temporary lesser/SpellSpace hook overrides do not carry over.

Configuration `add_hooks` and `with_hooks` now allow an omitted Spellbook ID to provide default
Conduit/Meld events. Explicit Spellbook event lists take precedence. Upgrade's `hooks=` argument
adds local callbacks after activation; configure activation callbacks through the configuration.

Upgrade requires an attached, childless lesser in a dynamic frame. Pause concurrent scope
acquisition and lineage changes, and return managed SpellSpaces held on other threads before
upgrading. Failures before the new Spellbook attaches restore the lesser. After attachment, the
caller remains responsible for cleaning up the normal conduit if later publication fails.

## Scoped creation purge

`Conduit.purge(...)` and `SpellSpace.purge(...)` dispose of retained creations while keeping the
scope, registrations and compiled creation contexts available for later melds.

Use the same selectors as `meld`, or pass an existing object as a shortcut:

```python
conduit.purge("Worker")
conduit.purge(Worker, binding_name="primary")
conduit.purge(spellframe=IWorker, binding_name="primary")
conduit.purge(spell_id=worker_spell_id)
```

`purge_all=True` is the default and removes every retained creation for that binding in the
authorized scope. To remove only one object, pass its instance with `purge_all=False`:

```python
# Worker is bound as Existence.many with configured disposal.
first = conduit.meld(Worker)
second = conduit.meld(Worker)

removed = conduit.purge(first, purge_all=False)  # 1; second remains retained.
removed = conduit.purge(Worker)                 # 1; removes the remaining object.
```

The instance shortcut discovers the binding from the object's class. Use explicit selectors for
bindings that require a spellframe or binding name. Purge returns the number removed, or `0` when
the authorized store has no matching creation. Single-object mode requires an actual instance.

| Existence | Authorized caller |
| --- | --- |
| `many` | The conduit or SpellSpace holding those local creations |
| `unique_per_spell_space` | That SpellSpace |
| `unique_per_conduit` | That conduit |
| `unique_per_conduit_lineage` | The lineage root conduit |
| `unique_per_conduit_cluster` | The elected cluster leader |
| `unique` | The spell's owning conduit |

A SpellSpace purges only its own creations. A Conduit does not redirect purge into an ambient
SpellSpace. Unauthorized scope requests fail before removal.

Purge follows the configured disposal methods. Retained `many` objects are disposed newest first;
single-object purge disposes only the selected object. If disposal fails, other selected objects
are still attempted and errors are reported in an `ExceptionGroup`. Removed objects are not disposed
again by subsequent scope cleanup.

Only retained creations are affected: `many` results without configured disposal are not retained.
Existing application references are not rewritten, and dependent objects are not recursively purged.
An externally supplied object remains referenced by its registration; purge does not unbind it.

## Recording fix and documentation

- Fixed structural recording when `configure_aether_frame()` has already frozen the Spellbook
  configuration. Recordings now include the owning Spellbook and settled frame policy needed for
  faithful restore, including Nexus visibility settings.
- Added runnable intermediate tutorials for bind lifecycle hooks and named lesser-conduit discovery.
- Added expert examples for checking agent-supplied bindings, annotating Spell definitions, and
  discovering and restoring named scope hierarchies through Nexus and Crystallizer.
- Updated scope, upgrade and restore guidance. Tutorials include downloadable Python sources and
  collection ZIPs.
