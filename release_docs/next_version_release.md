# Melder 0.2.50 — next release

**Draft release notes. Publication date to be assigned; more changes may follow.**

## Added: named lesser conduits

Lesser conduits can now receive a name when created, in automatic or dynamic mode:

```python
job = root.create_lesser_conduit(name="job-42")
cloud = root.get_conduit_cloud()
try:
    assert cloud.get_conduit_by_name("job-42") is job
    # Resolve this job's objects through job.meld(...).
finally:
    job.cleanup()

assert not cloud.has_conduit_name("job-42")
```

Names are exact, nonempty strings and unique among active named roots and lessers in a frame.
They are assigned only through creation, including acquisition of a prewarmed pooled scope.
Cleanup unregisters and clears the name before returning the scope to its pool. Unnamed scope
return keeps its single name check and performs no Cloud, Crystallizer or Nexus publication work.

Naming preserves the scope's lesser status, shared Spellbook and existing instance lifetimes.
Discovery returns the live borrowed object; it does not extend the scope's lifetime. Dynamic
promotion can retain the name or select another available name while preserving the conduit ID
and using the upgraded root's independent Book.

When dynamic structural recording is enabled, Crystallizer captures named lesser names and parent
relationships, including the unnamed ancestry needed for faithful reconstruction. Release and
reuse update later checkpoints without changing sealed history. Both replay drivers reconstruct
fresh structural identities through ordinary creation; previously created application objects
and their mutable data are not restored. Record schema **3.0.0** prevents older root-only readers
from misinterpreting these records; valid older root-only input remains readable. Live restore
requires the caller to quiesce ordinary scope acquisition and cleanup.

Nexus publishes named acquisition, retirement and reuse. A returned named scope retains an unnamed
pooled record so existing projections remain valid; named reuse replaces its current name and
parent information. Capability and codegen named getters resolve the exact authorized identity,
and capability's `create_lesser_conduit(..., name=...)` forwards the creation name. Existing ACLs
and lesser-operation restrictions remain in force. New IDs and permanently removed records use
the existing explicit Rift projection refresh; commands do not refresh while admitted to a Rift.

### Public setup and documentation

Normal conjure now records both the owning Spellbook and settled frame posture when
`configure_aether_frame()` already locked the configuration. Previously that public setup could
omit its Book or frame twin, causing restore to refuse or lose the frame's Nexus visibility policy.
The repair reuses the existing origin-aware freeze/bind machinery; ordinary meld and pool paths
gain no work.

- **Intermediate 41 — Named lesser conduits:** runnable naming, collision, lookup, scoped-state,
  cleanup and anonymous-reuse examples, including prewarmed scopes.
- **Expert 38 — Named scopes in Nexus and restore:** capability creation and authorized lookup,
  explicit projection refresh, named reuse and a successful structural replay with fresh IDs and
  newly created application state, including required unnamed ancestry.
- Scope, agent-room and restore guides now explain the contracts and link the lessons. Source
  downloads and collection ZIPs include both. Canonical architecture/components and the source
  graph now describe all three feature stages.
- Expert 24 now establishes dynamic recording before binding and retires the original root before
  replay, proving successful restoration instead of colliding with its existing runtime.

### Validation and packaging

The Nexus-stage affected selection passed **471 tests**. After the public-setup correction, the final
Book/conjure/naming/Nexus/restore selection passed **392 tests**. These selections overlap and should
not be added together. All **78 intermediate/expert examples** qualify across the main run and the
focused correction; **39 documentation tests**, a strict **300-page HTML build**, local links and
lesson-source/download checks pass. No full-repository coverage claim is made.

The final cleanup audit removed redundant cleaned-state checks from the changed private helpers;
public entry points retain their lifecycle guards. Its affected selection passed **206 tests**.

Packaged Melder and repository LLM assets were regenerated for **0.2.50** after code approval.
The guard, agent documentation, packaged system documents and LLM bundles pass their currentness
checks. **253 asset/document/builder tests** pass across the main run and one isolated test process.
The rebuild changed generated assets only; runtime source is unchanged.

## Added: intermediate and expert bind-hook tutorials

The Read the Docs curriculum now includes two runnable lessons for the new bind lifecycle:

- **Intermediate 40 — Bind lifecycle hooks:** follows the original reference through pre-bind,
  actual-Spell activation and post-registration callbacks. Demonstrates configuration seeds,
  Book registration, and clearing/re-adding hooks through the normal Conduit. Shows that these
  callbacks run during binding, separately from application-object creation during meld.
- **Expert 37 — Review agent bindings:** applies ordered checks to agent-supplied existing objects,
  validates submission metadata, and updates the actual Spell's metadata and tags. Demonstrates
  rejection at each relevant stage and verifies that a post-bind notification failure can leave
  the binding registered and resolvable.

The lessons include assertions and printed outcomes, with linked intermediate/expert guides,
curriculum navigation, individual source downloads and collection ZIPs. The guidance distinguishes
live metadata edits from source/version changes and automatic persistence updates.

The existing graduation lesson also now teaches the new empty Spellbook correctly: former
definitions are no longer visible, new definitions can be bound, and retained creations remain
the upgraded conduit's disposal responsibility.

Both new lessons passed. Across the main run and focused reruns, **76 intermediate/expert examples**
were verified, along with **39 documentation tests**. The strict local HTML build, local-link checks
and byte-for-byte download checks passed. These are repository documentation changes prepared for
the normal publication flow.

## Fixed: pooled hook isolation and runtime hook updates

Reused lesser conduits and SpellSpaces no longer retain temporary Meld callbacks from their
previous use. They are prepared **before returning to the pool**, preserving the existing lifecycle:

1. Dispose the current scope's creations.
2. Clear lesser-conduit local lifecycle hooks and restore temporary Meld hooks to the shared baseline.
3. Reset the hook-modification flag.
4. Return the ready scope to the pool.

This covers lesser conduits and both manual and managed SpellSpace cleanup. Prewarmed SpellSpaces
also restore their hook baseline before entering the idle pool. Permanent SpellSpace cleanup now
cleans its owned Meld runtime and releases callback references; borrowed callbacks are not disposed.

When acquired, a SpellSpace selects its owner's current local Meld hooks when applicable, including
changes made while it was idle. This selects hooks for the new use; disposal and removal of the
previous use's temporary hooks have already completed before pool return.

### Add, replace and clear runtime hooks

`Conduit.register_conduit_hooks(...)` now accepts `create_local_hooks=True` and `overwrite=False`.
The default appends locally. The new `Conduit.set_conduit_hooks(...)` defaults to local replacement:

```python
# Append a callback on this conduit only.
conduit.register_conduit_hooks({"on_meld_pre_resolve": before_meld})

# Replace this conduit's Meld hook family.
conduit.set_conduit_hooks({"on_meld_pre_resolve": replacement})

# Publish a shared replacement from the normal root.
root.set_conduit_hooks({"on_meld_pre_resolve": replacement}, create_local_hooks=False)

# Clear the shared Meld hook family.
root.set_conduit_hooks({"on_meld_pre_resolve": []}, create_local_hooks=False)
```

- Setting replaces the supplied hook families: Conduit lifecycle, Meld, or both. Omitted families
  remain unchanged; an empty mapping selects both families.
- Local lifecycle hooks retain their event-shadowing behavior. Clearing the local lifecycle family
  reveals inherited events. Clearing local Meld hooks mutes that scope until hooks are changed
  again or the scope returns to its pool.
- Shared updates are normal-root-only and reach scopes still using the root's shared baseline,
  including an initially empty baseline. Explicit local copies remain isolated.
- Normal roots own independent runtime hook containers. Runtime changes do not mutate frozen
  configuration or another normal root, even when frame-wide configuration is shared.
- `Meld.register_meld_hooks(...)` provides matching local/shared and append/replace controls for its
  hook family. `hooks_modified` on Conduit and Meld reports temporary local hook state.
- Invalid callback batches are rejected before either hook family changes. Use the mutation methods;
  direct changes to internal lists or dictionaries are not tracked.
- Graduation installs the new root's baselines, so later pool reuse cannot restore the former
  root's callbacks. Active SpellSpaces retain their selected source until their next acquisition
  when an owner switches between local and shared hook maps.

The common pool path uses simple flag checks; only modified state takes the existing reset lock.
Ordinary meld execution gains no additional checks or locks. Clearing hooks restores the existing
warm fast path without recompilation or cache reset.

### Pool-hook validation

The affected selection passed **2,102 tests**, with two existing owner-deferred skips. **73 new
parameterized cases** cover pool reuse, prewarming, local/shared controls, graduation, callback
release, disposal order, concurrent updates and warm-path recovery. Scoped lint passed. These
results do not claim full-repository coverage.

## Fixed: lesser-to-normal graduation owns its new Spellbook

`Conduit.upgrade_to_normal(...)` now completes normal Spellbook setup against the existing conduit.
When it returns successfully, the conduit is already conjured and ready to bind and meld through
its own new, empty Spellbook. Its object identity, conduit ID and retained creations are preserved.

```python
lesser = root.create_lesser_conduit()
lesser.upgrade_to_normal("independent")

service_id = lesser.bind(spell=Service, existence=Existence.unique_per_conduit)
service = lesser.meld(spell_id=service_id)
```

The upgraded conduit has no parent and inherits no spell definitions, contracts or resolution
verdicts. Earlier creations remain retained for disposal, but their old spell IDs are no longer
resolvable through the new Book. Register the definitions needed by the new root explicitly.

Previously, graduation discarded the new Book and continued using the former root's Book. Binding,
Bind-hook changes and cleanup could consequently affect the former root. Graduation now attaches
the correct Book, removes both parent relationship links, and gives the new root independent pool
and cluster resources. Each root cleans up its own Book and bindings.

### Configuration and hook initialization

Pass an optional same-frame `SpellbookConfiguration` to configure the new Book:

```python
configuration = SpellbookConfiguration("application").with_defaults()
configuration.with_bind_hooks(
    pre=[check_reference],
    activation=[inspect_bound_spell],
    post=[record_binding],
)
configuration.with_hooks(on_meld_pre_resolve=before_meld)

# The lesser must already belong to the "application" frame.
lesser.upgrade_to_normal("configured", configuration=configuration)
```

| Configuration mode | New Book setup |
| --- | --- |
| Local, configuration omitted | Fresh defaults and empty hooks |
| Local, fresh matching configuration supplied | Uses the supplied configuration and its initial hooks |
| Frame-wide sharing enabled | Uses the frame's existing frozen configuration; a different supplied object is rejected |

Frame-wide sharing shares configuration, not the Book or its registrations. It applies within that
AethericFrame, not across all frames. Individual Books leave the canonical shared configuration
alive; its frame owns cleanup.

Successful graduation discards the former Book's runtime Bind-hook changes, old Book-specific
Conduit/Meld hooks, and lesser/SpellSpace runtime hook overrides. The selected configuration's
deliberate defaults may apply again. Callback objects can therefore be reused by shared policy;
their state is not cloned.

- Configuration now supports `add_bind_hooks`, `clear_bind_hooks`, `get_bind_hooks` and fluent
  `with_bind_hooks`. These stage initial pre/activation/post callbacks before freeze.
- Each Book captures its own Bind hook set during construction. Later runtime add/clear operations
  affect that Book only; changes to configuration seeds apply to subsequently constructed Books.
- Configuration `add_hooks` and `with_hooks` accept an omitted Book ID for default Conduit/Meld
  events. Existing explicit Book IDs remain supported; their event lists take precedence.
- The upgrade's existing `hooks=` mapping supplies local runtime additions after conjure activation.
  Configure creation/activation callbacks through the selected configuration itself.
- Recording preserves effective hook-presence markers, without serializing callback code.

### Lifecycle and failure behavior

Graduation remains limited to an attached, childless lesser in a dynamic frame. It drains the
existing creation gate before changing ownership and restores its original admission state.
Retained manual, idle pooled and current-thread managed SpellSpaces receive the new Book lookup
references and hooks; stale lookup caches cannot resolve the former Book's definitions.

The caller must stop concurrent lineage changes and scope acquisition, and return managed
SpellSpaces held on other threads before upgrading. Failures before Book attachment restore the
lesser and clean newly allocated state. Failures after attachment retain ordinary conjure's
caller-owned cleanup responsibility. Existing hook exception behavior is unchanged.

### Graduation validation

The affected source selection passed **4,118 tests**, with two existing owner-deferred skips.
The final **157-test** graduation/configuration selection includes **12 additional regression
cases** for hook isolation, retained SpellSpaces, shared defaults, separate frames and failure/retry.
Scoped lint passed. These results do not claim full-repository coverage.

## Added: scoped creation purge

`Conduit.purge(...)` and `SpellSpace.purge(...)` retire retained creations without ending their
scope or removing the registered spell. This gives applications an explicit way to dispose of
objects while keeping their bindings and compiled creation machinery available for later melds.

### Choose an object reference or explicit selectors

Pass an existing object as a shortcut. Purge inspects its class and uses the existing spell lookup:

```python
worker = conduit.meld(Worker)
removed = conduit.purge(worker)
```

The normal meld-style selectors are also available. These are alternative call forms:

```python
conduit.purge(Worker)                           # Class reference
conduit.purge("Worker")                         # Registered name
conduit.purge(Worker, binding_name="primary")    # Named binding
conduit.purge(spellframe=IWorker, binding_name="primary")
conduit.purge(spell_id=worker_spell_id)           # Explicit machine identity
```

Both input paths use the same scope checks and creation-disposal machinery. Discovery itself
does not call a constructor or invoke meld execution.

### Remove all retained creations or one object

`purge_all=True` is the default. It removes all retained creations for the selected spell within
the authorized scope. For `many`, that means the spell's entire local retained bucket.

Use `purge_all=False` with an actual object instance to remove only that object:

```python
# Worker is bound as Existence.many with configured disposal.
first = conduit.meld(Worker)
second = conduit.meld(Worker)

removed = conduit.purge(first, purge_all=False)  # 1; second remains retained
removed = conduit.purge(Worker)                 # 1; removes second
```

The same options are available on a spell space:

```python
with conduit.enter_spellspace() as space:
    session = space.meld(RequestSession)
    removed = space.purge(session, purge_all=False)
```

Purge returns the number of removed creations. It returns `0` when the selected store has no
matching entry, including when a requested single object is no longer retained. Single-object
mode requires an instance; it does not choose an arbitrary object from a name or class selector.

### Scope authority follows the creation lifetime

| Existence | Authorized caller and target |
| --- | --- |
| `many` | The calling conduit or spell space removes its own local creations |
| `unique_per_spell_space` | That spell space removes its own creation |
| `unique_per_conduit` | That conduit removes its own creation |
| `unique_per_conduit_lineage` | Only the lineage root conduit removes the shared creation |
| `unique_per_conduit_cluster` | Only the elected cluster leader removes the shared creation |
| `unique` | Only the spell's owning conduit removes the creation |

A spell space can purge only its own `many` and `unique_per_spell_space` creations. A conduit
does not redirect purge into an ambient spell space. Unauthorized scope requests fail before removal.

### Disposal and subsequent melds

- Purge uses the configured disposal methods and their existing order. Retained `many` entries
  are disposed newest first; single-object mode invokes disposal only for the selected object.
- Live and disposal records are removed together under the existing creation locks. Disposal
  callbacks run after those locks are released.
- If disposal fails, other selected objects are still attempted and failures are reported as an
  `ExceptionGroup`. Removed entries remain removed and are not disposed again during later cleanup.
- Registrations, compiled contexts and scope objects remain available. A later meld can create a
  fresh factory-backed instance according to its normal lifetime.
- Only retained creations can be purged. `many` results without configured disposal are not retained.
- Existing Python references held by application code are not rewritten, and dependent objects are
  not recursively purged. An externally supplied object remains referenced by its registration;
  purge does not unbind it or turn it into a factory.

## Validation recorded for this change

The focused source selection passed **270 tests**, covering both selector paths, single/all removal,
scope authority, creation locks, disposal ordering/failures, concurrent purge and existing
Creations/Meld/lineage/cluster behavior. Scoped lint checks passed. This is not a full-suite or
coverage claim.
