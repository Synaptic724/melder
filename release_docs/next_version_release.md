# Melder 0.2.8215

**Unreleased**

## Melds by name or class take the warm lane

`conduit.meld("Service")` and `conduit.meld(spell=Service)` now reach the compiled builder in one lookup once
the spell has been built once through that call - the warm lane that `meld(spell_id=...)` already had.
`SpellSpace.meld` does the same for scoped melds. The meld door keeps a second success-only registry keyed
by the name string or the class object a caller passes, validated per call by the same guards as the id
entry (door epoch, creation-context identity, live hook and validation flags), so a warm hit returns exactly
what the full lane would.

Nothing changes in what you call or what comes back: the same object for a stored lifetime, a fresh one per
call for `Existence.many`, the same errors, the same override and existing-object behaviour. Melds that pass
`spellframe` or `binding_name`, an instance or a callable as `spell`, dynamic worlds, hooks, and list, tuple
or empty override payloads keep their current path.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded): a warm meld by name of a dependency-free
class 453 -> 269 ns, with one singleton dependency 537 -> 350 ns, at width 4 888 -> 687 ns, a stored singleton
melded directly 333 -> 177 ns; melds by name, by class and by id now cost the same.

## `with` releases a Conduit, and every scope exit finishes its cleanup

**Breaking change:** `with conduit:` no longer holds the conduit's lock for the block. A Conduit is now a
dispose scope, like a .NET `using` block: when the block ends, a lesser conduit disposes the objects it holds
and goes back to its root's pool, and a root conduit is torn down. Code that used `with conduit:` as a lock
needs a lock of its own; code that cleaned the conduit up by hand after the block can drop that call.
`Spellbook`, `Aether`, `AethericFrame`, `ConduitWard` and `SpellIndex` keep `with` as a lock.

`Conduit.enter_lesser_conduit(logger=None, *, name=None)` makes a lesser for such a block; it returns exactly
what `create_lesser_conduit` returns:

```python
with root.enter_lesser_conduit() as request:
    handler = request.meld(Handler)
# the request's objects are disposed and the lesser is back in root's pool
```

**Breaking change:** a failing disposal method no longer stops cleanup half way, and its failure is no longer
only logged. A SpellSpace block exit, a SpellSpace `cleanup()`, a lesser's return to its pool and a root's
teardown now finish every step - the scope still goes back to its pool, or is fully torn down - and then raise
all the disposal failures together as one `ExceptionGroup`. Before, a failure could leave a SpellSpace or a
lesser out of its pool, and a conduit's teardown only logged these failures. If your disposal methods can
fail, catch `ExceptionGroup` (or use `except*`) around cleanup. When the `with` block itself raised, its
exception is kept and the cleanup group rises with it as `__context__`. `using_cleanup()` and
`async_using_cleanup()`, available on every Cleanable, now let a cleanup error propagate instead of
swallowing it.

Also fixed:

- A lesser's return disposes its child lessers first, then its SpellSpaces, then its own objects - the order a
  root's teardown already used.
- Calling `cleanup()` twice on a lesser or a SpellSpace no longer puts it in its pool twice, where two later
  acquisitions could receive the same object.
- A SpellSpace back in its pool refuses `meld` and `purge` with `SpellSpaceScopeError`, so a handle kept after
  its block can no longer build objects into the idle space that the next request would be served.
- A lesser cleaned up inside one of its own `enter_spellspace()` blocks no longer makes that block's exit
  raise "stack corruption".

What stays the same: the disposal order inside a scope (newest first, each object's methods in declared
order), which objects each scope owns, purge, and build locks. Frame teardown still cleans every conduit when
one fails; it now logs that failure instead of dropping it silently.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded), same process, against 0.2.8202: a managed
SpellSpace enter and exit 9-19 ns faster, a lesser create and cleanup 7-20 ns faster, a warm `SpellSpace.meld`
2-5 ns faster; the GIL build measured no slower.

## Fixed: a SpellSpace's live-creation probe missed the `many` objects it holds

The no-create probe on the meld door a SpellSpace uses (`has_live_creation` and
`describe_live_creation_status`) now reads `Existence.many` objects from the space's own store. A `many` with
disposal methods melded through a space is kept there - the space's exit disposes it and the space's `purge`
removes it from there - but the probe looked in the owner conduit's store, so it reported nothing while the
space held such objects and counted the conduit's own instead. It now counts the space's, with
`storage_scope_kind` `"spellspace_many"` and the space's id in `active_spellspace_id`.
`Conduit.has_live_creation`, every other lifetime and the meld path are unchanged; the probe still creates
nothing.

## Fixed: same-named classes can use distinct spell addresses

Two classes named `Repo` can now share a Spellbook when their spellframes or binding names differ.
Previously both registrations succeeded, but `conjure()` rejected them with `DUPLICATE_SPELL_NAME`,
even though its error advised adding those same qualifiers.

```python
book.bind(spell=users.Repo, spellframe="users", existence="many")
book.bind(spell=orders.Repo, spellframe="orders", existence="many")
root = book.conjure()
users_repo = root.meld(spellframe="users")
orders_repo = root.meld(spellframe="orders")
```

Phase 4 now checks the normalized `(frame_key, binding_key)` used by registration and resolution.
This also permits qualified same-named definitions with `resolvable=False` and qualified contracted
bindings. A genuine shared address still produces a collision; its diagnostic retains the
`DUPLICATE_SPELL_NAME` code and names the normalized address. Discoverable definitions retain their
address ownership and direct-meld refusal. Bare-class lookup semantics are unchanged.

## Fixed: concurrent first reads of system documents

Concurrent first access to `__architecture__`, `__components__`, `__graph_network__` or
`__graph_details__` could fail with a `NoneType` error during section lookup. The lazy loader marked
the section table ready before publishing its key map, so another reader could observe only half
the index. It now publishes the complete map before setting that ready marker. A failed map build
also remains retryable. Loading stays deferred and reads remain lock-free.

## Look up frames without creating them

`Aether` can now tell you which frames exist and hand one back without creating anything. Until now every
frame-scoped call on `Aether` - the conduit lookups, `get_conduit_cloud` - resolved "default" through the lazy
creation path, so asking about a missing "default" created it and, on a world with no frames yet, sealed the
Aether configuration. A host that creates frames by constructing Spellbooks and later needs to find them had
to read Aether's private registry.

- `Aether.find_frame(name)` returns the live frame with exactly that name, or `None`.
- `Aether.get_frame(name)` returns it, or raises `ValueError` ("Aetheric frame 'name' does not exist. ...",
  with how to create the frame or probe for it).
- `Aether.list_frame_names()` returns the live frames' names in creation order, as a tuple snapshot.

None of them creates a frame ("default" included), takes the Aether lock or freezes the Aether configuration.
A frame whose cleanup has started reads as absent. The frame you get back is borrowed: Aether still owns it,
and once its owner cleans it the reference must not be used; if a name may have been reused, compare with `is`.
A name that is not a string raises `TypeError`, and a cleaned `Aether` raises `RuntimeError`.

Read-only properties now expose what a host compares against:

- `AethericFrame.shared_spellbook_configuration`: the frame-wide Spellbook configuration that Spellbooks in
  the frame adopt, or `None` when the frame does not share one or no Spellbook has bound it yet.
- `AethericFrameConfiguration.frozen` and `SpellbookConfiguration.frozen`: whether the frame posture or the
  configuration has been frozen. Reading them changes nothing.
- `SpellbookConfiguration.aether_frame`: the frame the configuration was built for; a Spellbook refuses a
  supplied configuration built for another frame.
- `Conduit.spellbook`: the Spellbook a conduit resolves through - the conjuring Spellbook for a root and the
  lessers under it, and the new one after `upgrade_to_normal`.

```python
from melder import Aether, Spellbook

aether = Aether()
assert aether.find_frame("ops") is None          # looking creates nothing
book = Spellbook(aetheric_frame="ops")           # constructing a Spellbook creates the frame
frame = aether.get_frame("ops")
root = book.conjure(name="root")
assert root.spellbook is book
assert frame.shared_spellbook_configuration is None   # this frame does not share one
print(aether.list_frame_names())                 # ('ops',)
```

What stays the same: the existing frame-scoped calls still create "default" when it is missing, frames are
created, owned and cleaned exactly as before, and no meld or conjure path does any extra work.

## Aether refuses a spell-id regime it cannot apply

**Breaking change:** while any frame exists, `Aether.configure(configuration)` and `Aether.activate()` refuse
a configuration whose `process_wide_unique_spell_ids` differs from the regime in force, with a `RuntimeError`
that names both values and the fix. The regime is sealed when the first frame is born (the first Spellbook, or
anything else that creates a frame) and is never re-read while frames exist, because spell ids already
registered were allocated under it. Before, such a configuration was installed anyway: `Aether().configuration`
then reported the new regime while the old one stayed in force - with the process-wide regime in force, the
same class bound into a second frame was still refused as a spell-id collision.

```python
from melder import Aether, AetherConfiguration, Spellbook

per_frame = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
Aether().configure(per_frame)                    # before the first frame: accepted
Spellbook(aetheric_frame="tenant_a")             # the first frame seals the per-frame regime
```

To upgrade: install the configuration before the first Spellbook creates a frame, or keep the regime that is
in force. Replacing the configuration with one that keeps the sealed regime - to change logging, say - is
still accepted, and nothing changes before the first frame.

## A live Nexus keeps its policy

**Breaking change:** `Nexus.configure(configuration)`, and `Nexus.activate(configuration)` handed a
configuration other than the installed one, now raise `RuntimeError("Cannot reconfigure Nexus while it is
active. Deactivate it first.")` while Nexus is active - the rule `Crystallizer` and `MutationResearch` already
follow. A live Nexus reads its policy at every Rift validation, so a swap changed the rules under Rifts that had
already passed them, and the replacement was installed unfrozen. The check is on identity: a second object with
the same values is still a replacement.

To upgrade, deactivate first:

```python
nexus.deactivate()
nexus.activate(new_configuration)
```

`nexus.activate()` and `nexus.activate(nexus.configuration)` on a live Nexus, and any configuration change on
an inactive Nexus, work as before. Restoring a checkpoint that recorded a Nexus into a process whose Nexus is
active still replaces the live policy with the recorded one: the restore deactivates the live Nexus first, as it
already did for MutationResearch.

## Fixed: a refused dynamic conjure no longer settles its frame dynamic

With an active Crystallizer, `conjure(dynamic=True)` is refused when spells were bound before the Spellbook's
configuration was finalized ("... requires the SpellbookConfiguration to be finalized BEFORE the first bind").
The refusal used to happen after the conjure had settled the frame posture dynamic, so the frame stayed frozen
dynamic and every later conjure in it inherited dynamic and was refused too - even a plain automatic conjure,
which the rule exempts. The refusal now happens before anything is settled: the frame stays as it was, and an
automatic conjure afterwards succeeds. The message, the exception type and the rule itself are unchanged.

## Compare root configurations by value

`AetherConfiguration`, `CrystallizerConfiguration`, `MutationResearchConfiguration` and `NexusConfiguration`
gain `get_configuration_dictionary()`: a new `dict` of the property values the configuration holds, keyed by
property name. A host that embeds Melder next to another Melder user can now compare the policy it was handed
with the one installed on a root without reading private state:

```python
from melder import Crystallizer, CrystallizerConfiguration

wanted = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3)
installed = Crystallizer().configuration
same_policy = wanted.get_configuration_dictionary() == installed.get_configuration_dictionary()
```

Editing the returned dict never changes the configuration; values are the stored objects, not copies (loggers
and resolvers by reference). Only properties that were set appear - start from `with_defaults()` for a
complete picture. Reading it never freezes or validates, works on frozen and activated configurations, and a
cleaned configuration raises `RuntimeError`.

## A restore brings back the spell-id regime it recorded

With an active Crystallizer, the Aether record now carries `process_wide_unique_spell_ids`, and a restore installs
it before it creates any frame, so a world recorded under per-frame spell ids (`process_wide_unique_spell_ids=False`)
comes back under per-frame ids. Before, the record held only the logger policy and every restored world ran
process-wide spell ids: binding the same class into a second tenant frame - which the recorded world allowed - was
refused as a spell-id collision.

When the restoring process has already fixed its regime - the host configured the Aether, or a frame exists - and it
differs from the recorded one, the restore keeps the live regime and says so in its report: a shortfall on
`("aether", "process_wide_unique_spell_ids")` with the reason
`recorded_per_frame_ids_restored_under_process_wide_ids` (or `recorded_process_wide_ids_restored_under_per_frame_ids`).
A record written before this version carries no regime: it restores process-wide as before, and the report lists
the key as missing.

The new read-only `Aether.process_wide_unique_spell_ids` says which regime is in force - the sealed value once a
frame exists, before that the installed configuration's value, otherwise `True`:

```python
from melder import Aether

Aether().process_wide_unique_spell_ids   # True until a per-frame configuration is installed
```

What stays the same: process-wide worlds record and restore exactly as before, and a restore never changes the
regime of a live world.

## Fixed: a class bound in several frames keeps every frame's binding when recorded

Under per-frame spell ids one class can be bound in several frames - the multi-tenant shape - and each frame's
binding has the same spell id. The Crystallizer kept one spell record per spell id, so recording such a world kept
only the last frame's binding, and a restore reported `complete` while the other frames came back without the
class. Records now keep one spell crystal per frame under per-frame ids, and a restore rebuilds each frame's
binding, index selection, parked members and contract grants in that frame's own Spellbook.

Restoring such a record into a process that already runs process-wide ids (a configured Aether or a live frame)
now fails before anything is built - `RuntimeError: restore failed at stage 'aether_configuration'`, chained from
an error that names both regimes and the fix - instead of quietly rebuilding one frame's copy.

**Breaking change:** records are stamped record version 4.0.0 (was 3.0.0), so an older Melder refuses them with its
upgrade message instead of folding several frames' copies into one; records written by older versions still load.
For worlds recorded under per-frame spell ids:

- spell custody is keyed `"<spell_id>@<frame>"` instead of the bare spell id - in `checkpoint_replay_data(...)`
  journals and payloads, formation records and the spells `analyze_impact(...)` lists; `spell_activity` and
  `spell_removed` payloads carry both "spell_id" and "custody_key", and `describe_profile()` counts one spell
  crystal per frame's copy;
- `Crystallizer.emit_spell_removed(...)` and `emit_spell_activity(...)` take `frame_name`, required while recording
  (`ValueError` without it); Melder's own call sites pass it;
- `Crystallizer.get_spell_crystal(spell_id, frame_name=None)` answers the named frame's copy, and without a frame
  the copy with the lowest key.

To upgrade: code that reads per-frame records by spell id should match on a payload's "id" (or split a key at its
first "@", which `SpellCrystal.spell_id_of_custody_key(...)` does), and pass `frame_name` when it calls the two emit
verbs directly. Process-wide worlds keep bare spell-id keys and need no change. `SpellCrystal.frame_name` and
`SpellCrystal.custody_key` are new.

## Fixed: a class bound after conjure melds directly after it was injected

On a dynamic root, a class bound after `conjure()` and first built as another class's dependency could not be
melded directly afterwards. The consumer's meld worked and received the dependency, but a direct meld of the
dependency from the same scope raised `RuntimeError: Cannot build CreationContext before spell_codegen_creation
exists.` The consumer's meld had compiled the dependency only inside the consumer's own plan and left it marked
valid, so nothing compiled it for a meld of its own. Now the consumer's meld marks such a dependency as still
owing its own resolution, and its first direct meld runs that resolution itself - no validation call, second
conjure or dependency-first warm-up - and returns the instance its scope already holds (`unique_per_conduit`,
`unique`) or a new one (`many`):

```python
book = Spellbook(aetheric_frame="app")
root = book.conjure(name="app-root", dynamic=True)
root.bind(spell=Service, existence="unique_per_conduit")   # bound after conjure
root.bind(spell=Consumer, existence="many")
scope = root.create_lesser_conduit()
consumer = scope.meld(spell=Consumer)          # Service is built as Consumer's dependency
assert scope.meld(spell=Service) is consumer.service   # raised RuntimeError before 0.2.8215
```

The same holds on the root, in named or unnamed and sibling lessers, through `SpellSpace.meld`, and with the
conjure cache on. What stays the same: melding the dependency first, or binding both before `conjure()`, works
as before; warm melds, validation verdicts and conjure do no extra work. A dependency marked this way pays one
resolution pass on its first direct meld.

## Packaging and documentation

- The packaged system documents (`melder.__components__`, `melder.__architecture__`) are regenerated: the Meld
  Resolution Runtime entry describes the name/class registry, its mint rule, its readers and its invalidation,
  and the meld sequence names both door registries.
- The packaged system documents also describe `with` as a dispose scope, `enter_lesser_conduit`, the finished
  scope exits and the SpellSpace lease; their stale SpellSpace claims (an active-scope check, `reset()`, a
  version) are corrected.
- The packaged system documents also describe which store each meld door's live-creation probe reads, and
  the Meld runtime's store-selection text now matches the code for `unique`, lineage and cluster lifetimes.
- The packaged system documents no longer paste the documentation tooling's commands or cite its files,
  which a reader of the packaged copy could not resolve, and the conduit meld door's docstrings now name
  the store each lifetime uses and no longer promise an active-spellspace check.
- The source and test system documents describe canonical address validation and the qualified-name
  regressions, including discoverable definitions, contracted bindings and genuine address collisions.
- The system-document contracts describe readiness-last index publication and the deterministic
  concurrency/retry regressions that protect it.
- The packaged system documents describe the root configuration guards: the sealed spell-id regime, the
  active-Nexus refusal and the restore's deactivate-first, the conjure refusal before settlement, and
  `get_configuration_dictionary()`; line citations that moved, and four that were already stale, are
  remeasured. `docs/advanced/nexus.md` says how to replace the policy of an active Nexus.
- The packaged system documents describe the recorded spell-id regime, per-frame custody keys and the restore's
  per-Book replay, and correct two stale claims in the restore detail: spell SHAs do translate when a receiving
  policy changes them, and the record version is no longer 2.0.0.
- The packaged system documents describe how a dependency compiled only inside a consumer's plan is marked and
  resolved on its first direct meld, and the meld runtime's deferred lane; their line citations into
  `spellbook.py`, `spellbook_creation_system.py` and `meld.py` are remeasured (several were already stale).
- The packaged system documents describe the frame lookups and read accessors of "Look up frames without
  creating them" (the Aether, frame registry, frame, posture, Spellbook configuration and conduit entries, a
  frame-lookup flow and diagram), and `docs/intermediate/scopes.md` shows them. Line citations those additions
  moved, and the stale ones into `aether.py`, are remeasured; the Aether singleton invariant now says that
  teardown resets unconditionally and only a failed construction checks identity.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8215.
