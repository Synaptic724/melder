# Melder 0.2.8225

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

## Fixed: a definition removed after use can be bound again at the same address and melded

On a dynamic root, a class bound after `conjure()`, melded, then removed with `cleanup_spell` and bound again
at the same address (the same class, spellframe and name) could not be melded afterwards: the second meld
raised `RuntimeError: Cannot build CreationContext before spell_codegen_creation exists.` in every scope that
had resolved the first definition. The two steps that skip the first meld worked. The verdict a conduit
records when it resolves a definition is keyed by the spell id, and the spell id is content-stable, so the
replacement - a new definition with nothing compiled yet - inherited the removed definition's "resolved"
verdict and the meld went to build it without compiling it.

Now removing a definition retires its verdict in every conduit, and registering a definition retires any
verdict already held for its id, so the replacement is resolved again by each conduit on its first meld
there and a new product comes back:

```python
book = Spellbook(aetheric_frame="app")
root = book.conjure(name="definitions", dynamic=True)
scope = root.create_lesser_conduit(name="requests")
spell_id = root.bind(spell=Action, existence="many", spellframe="actions", binding_name="run")
first = scope.meld(spellframe="actions", binding_name="run")
root.cleanup_spell(spell=root.get_spell_by_id(spell_id, "app"))
root.bind(spell=Action, existence="many", spellframe="actions", binding_name="run")
second = scope.meld(spellframe="actions", binding_name="run", override={"value": 2})  # raised before 0.2.8219
```

What stays the same: a product built from the removed definition is untouched by its removal and is disposed
by the scope that built it, alongside the replacement's products; peer scopes that resolved the removed
definition through a contract meld the replacement once it is granted again; consumers of the removed
definition rebuild against whatever is bound at that address next, as before. Removing a definition and
binding again now costs one resolution pass per scope on the replacement's first meld there, the same as a
first late binding; warm melds and conjure do no extra work. A notch back to a member that was active before
is resolved again the same way. One existing behaviour is unchanged and worth knowing: for a lifetime that
stores one object per scope (`unique_per_conduit` and kin) the object built from the removed definition keeps
its slot, so the replacement's first meld in that scope returns it, and an override against it is refused as
against any stored shared instance.

## Fixed: a warm creation cache no longer replays an executor compiled in another world

With system caching on, a conduit's creation-cache bundle was admitted as a full hit whenever every cached spell
was still bound, without checking the rest of the world. An existing object or a non-resolvable definition
carries no cached executor, so a world that only added one - say a provider for a parameter nobody had provided,
bound bare as an existing object - or removed one was still a full hit: the consumer's executor compiled without
the provider was replayed and its first meld raised `TypeError: ... missing 1 required positional argument`, or
a plan naming a spell the world no longer has raised `RuntimeError: generalized manifest references unknown
spell_id`, while a cold cache resolved the same world correctly.

The bundle now records the world its executors were compiled in - the same stamp the structural tier already
uses (the bound spell ids, the frame posture and the borrowed spells) - and a full hit requires it. A changed
world recompiles phases 8-11 once and re-stages the bundle; a repeat world is still a full hit that leaves the
file untouched. A world that only removed a spell is a changed world too and recompiles once (before, surplus
cached ids were ignored). Creation-cache generation 19 retires bundles written without the stamp; they rebuild
on the next conjure.

```python
service = Service()
book.bind(spell=service, existence="unique", permissions="create")   # added since the cached run
book.bind(spell=Worker, existence="many", permissions="create")       # Worker(service: Service)
conduit = book.conjure(name="root")
conduit.meld(spell=Worker).service is service                         # True; TypeError before 0.2.8220
```

What stays the same: caching off, the structural tier and its replay, what is staged per spell, every meld path.

## Transient creations with disposal methods register faster

A `many` spell whose instances declare disposal methods (through the Spellbook's disposal configuration or a
bind's own candidates) is registered into its scope's store on every meld, so that the scope's exit can dispose
it. That registration used to allocate a `(instance, methods)` record and append to two lists under the store
lock on every creation; it is now one list append, and the Spell's disposal list is recorded once per spell and
scope, at the first registration. Compiled plans and executors call the store's new positional verb,
`Creations.register_many(spell_id, instance, disposal_methods)`, which takes and releases the store lock
explicitly; `add_many_creations` keeps its signature for other callers.

Nothing changes in what is disposed or when: the same objects, newest first, each method in its declared order,
one chained error per failing method in the same `ExceptionGroup`, and a scope cleaned while an instance was
still being built still disposes that instance and raises. One rule is now enforced that the runtime already
guaranteed: all registrations of one spell id in one scope carry the same disposal declaration, since the spell
id hashes its resolved disposal names; a direct `add_many_creations` call that mixes declarations is refused with
`ValueError` instead of leaving sparse disposal metadata.

Directional numbers on a 2-core VM (Python 3.14t, free-threaded), interleaved before/after medians on the real
compiled plans: the plan of a transient with one singleton dependency 377 -> 249 ns per creation, of a wide
transient over eight singletons 682 -> 527 ns, of an eight-deep transient tree 804 -> 639 ns; the whole meld by
name of those roots 536 -> 414 ns, 962 -> 765 ns and 882 -> 737 ns. Melds of singletons and of transients
without disposal methods are unchanged.

The creation-cache format generation is 16: an existing `__melder_cache__` built by an earlier version is
rebuilt on the next conjure, as before; nothing else changes on disk.

## Dict-mode site plans build no dict on the warm path

A root whose site plan has a generic step - an existing object, a contract payload, a positional override, a
collection parameter - used to allocate `instance_results = {}` at the top of every warm creation and store
every step into it, although only a cold miss ever read it. Each generic construction now receives a dict
literal of exactly the values it reads, built where it runs; the warm path builds nothing. Measured on the
maintainers' VM (3.14t, GIL off): the plan body of a root over existing objects drops 26-32% and the whole meld
22-23%; roots whose plans are all direct calls are byte-identical. Same objects, same errors on a failing
miss; no API change. Creation-cache generation 17 retires executors emitted with the eager dict, so the first
conjure after upgrading regenerates them.

## A consumer's annotation selects by kind: a category never provides, a Protocol frame is a contract

**Breaking change:** a `spellframe` is a string category or a `typing.Protocol` contract, and nothing else.
`bind(spell=Impl, spellframe=SomeClass)` with a concrete class now raises `TypeError` naming the two valid
forms. To upgrade, pass the class's name to keep the grouping (`spellframe="SomeClass"`), or declare the shape
as a `Protocol` to make it a contract the spell is checked against. Before 0.2.8222 the class was accepted and
matched by name, so a same-named single annotation resolved everything grouped under it.

What an annotation selects now follows from what the annotation is:

- a **class** selects the spells of that type - a class bound bare, or an existing object of that class. A
  category that happens to share the class's name does not turn its members into providers: fourteen
  framework classes grouped under `spellframe="spectrum"` no longer raise an ambiguity for a consumer declared
  `spectrum: Spectrum`, which was the MelderOps defect this fixes;
- a **Protocol** selects the spells bound under it as their contract (and the Protocol's own definition when it
  is bound `resolvable=False`, so a descriptive definition still compiles its override socket; an implementer is
  preferred);
- a **`TYPE_CHECKING`-only import**, which leaves a string at runtime, selects a type or a contract by name and
  never a string category;
- `list[...]` gathers the group the annotation's kind names: every spell of the class, every implementer of the
  Protocol, or - for a string - every spell whose frame key is that name.

The binding records what its frame is: `Spell.spellframe_kind` (`none`, `category` or `contract`, which bind
sets from the frame you pass; it is not exported) and `Spell.implemented_protocols` (the Protocol it was checked
against). The crystallizer records them too (record version 4.1.0; 4.0.0 records stay readable), so a restored
or grafted world rebinds a Protocol frame as the Protocol, not as a same-named category; when the Protocol
cannot be imported at restore the spell is bound under the recorded name as a category and the report files a
`spell_crystal` shortfall saying so. Explicit addressing (`SpellMap`, `SpellContract`, `meld(spellframe=...,
binding_name=...)`) is unchanged; ambiguity between two spells of the type still raises in Phase 3 and two
spells at one address are still refused in Phase 4. Creation-cache generation 20 retires bundles captured under
the 0.2.8218 name matcher.

What 0.2.8218 brought and 0.2.8222 keeps: an existing object bound bare satisfies a consumer annotated with
its class, and a binding resolves identically whether the consumer imported the type under `TYPE_CHECKING` or
at runtime.

## Shared singleton sites read their store as a constant

When a compiled site plan reads a dependency of existence `unique` - a singleton its Spellbook owns - it used to
look that spell's owner store up on every creation (`c = spells[i]._owner_creations`) before reading the instance
out of it. In an automatic world that store cannot move after conjure, so the plan now binds it once, when the
plan is emitted at the first meld, and the warm read is the store lookup alone. A dynamic world keeps the
per-creation read, because an ownership transfer repoints a spell's owner store there. Same objects, same
errors, same locks; no API change; nothing changes on disk, since plans are emitted from the cached rows at
hydration and the creation-cache generation stays 19.

Directional numbers on the maintainers' VM (Python 3.14t, free-threaded), interleaved before/after medians of
three runs on the real compiled plans: a transient over one singleton 160 -> 148 ns per creation, a root over
five singletons 316 -> 277 ns, a wide root over eight singletons 447 -> 374 ns, a wide root over eight existing
objects 444 -> 368 ns (-7..-17%), and an eight-deep transient chain with one singleton 432 -> 428 ns. Roots with
no `unique` dependency are byte-identical.

## Cache files are named `.meldercache`

Melder's on-disk cache bundles now end in `.meldercache` instead of `.melc`, so a file under `__melder_cache__`
says what it is: `<cache root>/<frame>/<conduit>.meldercache` for a conduit's creation cache and
`__melder_cache__/__<asset>__/<asset>.meldercache` for the build-asset caches.

Nothing reads or deletes an old `.melc` file. The first conjure and the first import after upgrading compile
cold once and write the new name, as every release change already does; leftover `.melc` files are inert and
safe to delete. Cache contents, locations and admission rules are unchanged, and `.gitignore` ignores both names.

## An ambiguous provider is refused with its candidates and the fix, not a compiler error

When a single typed constructor parameter has two or more registered providers - two classes that happen to
share a name, or one class bound twice - `conjure()` now refuses the consumer through the readable validation
report instead of raising `RuntimeError("SpellCrafter Phase 3: multiple DI candidates ...")` from inside the
compiler:

```text
Spellbook validation failed. Broken spells: MCPScanner.
MCPScanner:
  - Parameter 'profile' on spell 'MCPScanner' expects ScanProfile, but 2 registered spells provide it:
    ScanProfile at (spellframe='agents', binding_name='ScanProfile'); ScanProfile at
    (spellframe='artificial_intelligence_tools', binding_name='ScanProfile'). Select one with a SpellMap
    default on the parameter (SpellMap(spellframe=..., binding_name=...)), supply it at meld with
    override={'profile': ...}, or bind only one provider of this type. [AMBIGUOUS_PROVIDER]
```

Every candidate is named with its address, and the three ways out are spelled out. The refusal keeps its
timing: `conjure()` in an automatic world, the late `bind()` (and any meld) of the consumer in a dynamic one.
Nothing is softened to a warning - ambiguity is a configuration error, not an input Melder picks for you.
Under the hood Phase 3 records the parameter as an `AMBIGUOUS_INPUT` socket and a new Phase-4 strategy
(`AmbiguousProviderStrategy`) reports it; `SpellValidationIssue.details` carries `candidates` for tooling.
Code that matched the old error text (`PhaseExecutionError` / "multiple DI candidates") should expect
`SpellbookValidationError` with code `AMBIGUOUS_PROVIDER`. No cache generation moves.

## Packaging and documentation

- The internal-bind guard manifest holds 620 entries at 0.2.8216 (619 at 0.2.8215): `ManyDisposalBucket`, the
  cleanup record of a `many` key, is Melder-internal and cannot be bound as a spell.
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
- The packaged system documents describe the per-key disposal record behind `register_many`, the store's
  one-declaration rule and the emitted registration line; the Creations entries' line citations are
  remeasured.
- The packaged system documents describe the per-conduit verdict retirement on definition removal and on
  registration, and correct the control-plane entry that named the registry verbs `register_lineage` and
  `unregister_lineage` (they are `register_index` and `unregister_index`).
- The packaged system documents describe the executor-cache world stamp: the envelope field, the full-hit
  rule, the staging write and the retired surplus full hit; the conjure sequence's line citations into
  `spellbook_creation_system.py` are remeasured.
- The packaged system documents describe the owner-store constant of a `unique` site in an automatic world:
  the eligible-site rule, the bound namespace name, the posture that keeps the read and the harness numbers;
  the site-plan lowering's code-map extents are remeasured.
- The internal-bind guard manifest holds 621 entries at 0.2.8222: `SpellframeKind`, the frame-kind enum a
  binding records, is Melder-internal and cannot be bound as a spell.
- The README's spellframe and dependency-injection sections state the kind rule (string or Protocol frames
  only; what a class, a Protocol and a `TYPE_CHECKING` string select; what `list[...]` gathers). The packaged
  system documents describe the frame classification and refusal, the Spell's two new fields, the kind-aware
  predicate and its four index buckets, the crystal's frame-kind keys, the loaders' hydration and shortfall
  and record version 4.1.0; the 0.2.8218 invariant is marked superseded.
- The packaged system documents name the cache bundles `.meldercache`.
- The internal-bind guard manifest holds 622 entries at 0.2.8224: `AmbiguousProviderStrategy` joined.
- The packaged system documents describe the AMBIGUOUS_INPUT socket, the strategy and the message shape; the
  README's `SpellMap` paragraph names the report.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8225.
