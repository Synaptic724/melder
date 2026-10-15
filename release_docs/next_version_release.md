# Melder 0.2.8240

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

## Lesser conduits and spellspaces past 20 are kept and reused, then let go when quiet

The pools behind `create_lesser_conduit()` and `enter_spellspace()` now keep what a burst needed. Each conduit's
spellspace pool and each root's lesser-conduit pool still always keep 20 idle shells; when more than 20 were out at
once, the extra shells now stay pooled when they come back (up to 256 per pool) instead of being destroyed, so the next
burst reuses them instead of building new lesser conduits and spellspaces. Once no burst has needed a new shell for 30
minutes, the pool lets the extras go a step at a time (10% every 10 minutes) until it is back to 20.

In melder_gauntlet past 20 threads the old pools rebuilt and destroyed up to 11 lesser conduits per iteration on a
2-core machine; they now build each one once. At 1 to 3 threads nothing changes (measured within noise), and returning
a shell while 20 or fewer are idle costs what it did.

`prewarm_lesser_conduits(count)` and `prewarm_spellspaces(count)` now keep up to 256 shells (they were capped at 20);
shells above 20 decay like a burst's.

For subclasses of `AbstractElasticPool`: while a miss happened within `settle_time_seconds`, a return raises the
target to the idle count it sees (up to `max_idle`); after that the target falls by `decay_percent_per_interval` of
its stretched value every `decay_interval_seconds`, with the steps of a quiet period applied at the next return, and
the oldest surplus is destroyed outside the pool lock. `stretch_percent` is now headroom over that count and defaults
to 0 (it was the growth per miss, default 200). A pool built with `max_idle == baseline_idle` behaves as before. No
signature changes, and `describe()` keeps its keys.

What stays the same: the number of live shells is never capped (a miss always builds), a returning shell is cleaned
before it is pooled, and a released spellspace still refuses `meld` and `purge`.

## A `many` dependency is disposed with the object that holds it

A `many` dependency that declares disposal methods and is built for a longer-lived object - a `unique`,
`unique_per_conduit`, `unique_per_spell_space`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster` spell -
now belongs to that object: it is disposed when the object's owner is cleaned up, it is disposed right after the
object when the object is purged, and it moves with the object to another root. Until 0.2.8234 it was recorded with
the scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster - went on handing out the disposed object. Until 0.2.8237 purging
the holder disposed the holder alone, leaving its dependencies registered and open until their scope ended (one more
for every purge-and-meld cycle), and `transfer_spell_ownership(..., move_creations=True)` moved the holder and left
its dependencies with the old root, whose teardown disposed them while the new owner kept serving the holder.

```python
class Connection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Repository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection


book = md.Spellbook()
book.bind(spell=Connection, existence="many", disposal_method_names=["close"])
book.bind(spell=Repository, existence="unique")
root = book.conjure()

with root.enter_lesser_conduit() as request:
    repository = request.meld("Repository")      # first built inside the request scope

assert not repository.connection.closed          # 0.2.8234 closed it when the request scope ended
assert root.meld("Repository") is repository

root.purge("Repository")                          # disposes the repository, then its connection
assert repository.connection.closed               # 0.2.8237 left it open, registered, until root.cleanup()
```

A dependency that belongs to an object is no longer one of its `many` spell's own entries: `purge` and
`has_live_creation` for that spell count only the instances no object holds, so purging the spell never disposes a
dependency a live object still uses. Purging the object raises the dependencies' disposal failures together with its
own, after the object is retired, and the object is disposed before its dependencies, as at teardown.

What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are still
recorded with the scope that melds them (the spellspace, else the conduit), so a lesser conduit or a spellspace still
disposes the transients it built for itself. `purge` still returns the number of the target's own entries it removed.
Warm melds run exactly the code they ran before.

With `generalized_singleton_specialization_enabled` (opt-in, off by default), a root whose graph passes a `many`
dependency to a longer-lived object is no longer specialized: the specialized path built and recorded a new
dependency on every warm meld, which the stored holder never used.

## A root that is torn down leaves its cluster, and leaving a cluster unshares its roots

A root conduit that is torn down - `cleanup()`, the end of a `with` block, or its frame's teardown - now leaves its
conduit cluster first, as `remove_conduit_from_cluster()` would. Until 0.2.8235 it stayed in the cluster as a member,
and as the leader when it led: `unelect_leader()` then failed part-way, `elect_leader()` refused because a leader was
still recorded, adding another conduit raised, and `delete_cluster()` removed the cluster and then raised before
cleaning it up. A torn-down leader now leaves the cluster with no leader, ready to elect another member.

```python
cloud = owner.get_conduit_cloud()
cloud.create_cluster("workers")
for root in (owner, leader, member):
    cloud.add_conduit_to_cluster(root, "workers")
workers = cloud.get_cluster("workers")
workers.elect_leader(leader.id)

leader.cleanup()                    # leaves "workers"; the cluster has no leader now
workers.elect_leader(member.id)     # 0.2.8235 refused: the torn-down leader was still recorded
cloud.delete_cluster("workers")     # 0.2.8235 removed the cluster, then raised before cleaning it up
```

`remove_conduit_from_cluster()` now also takes the leaving conduit's shared roots back from every remaining member,
and theirs from it. Until 0.2.8235 the leave dropped its record of what the conduit had shared before it unshared it,
so every remaining member kept the leaving conduit's roots in its contracts.

What stays the same: `remove_conduit_from_cluster()` still needs a dynamic frame with clusters enabled, a conduit
belongs to at most one cluster, and `get_clusters_for_conduit()` returns the same list - it now reads the frame's
membership index instead of walking every cluster.

## A cluster's shared object belongs to the cluster, not to its leader

A `unique_per_conduit_cluster` object now lives in the cluster's own store for as long as the cluster exists. Electing
a leader serves it to every member; a leader leaving the cluster or being torn down keeps it; the next leader serves
the same object; and deleting the cluster, or tearing its frame down, disposes it once. Until 0.2.8236 the object
lived in the elected leader conduit's own store: after a leader change the next election built a second object, and
tearing the old leader down disposed the first one while members' objects still used it. Deleting a cluster disposed
nothing.

```python
workers.elect_leader(leader.id)
bus = member.meld("ClusterBus")
cloud.remove_conduit_from_cluster(leader, "workers")
workers.elect_leader(member.id)
assert member.meld("ClusterBus") is bus      # 0.2.8236 built a second bus
leader.cleanup()                              # 0.2.8236 closed the first bus here
cloud.delete_cluster("workers")               # closes the bus, once
```

`delete_cluster()` now raises an `ExceptionGroup` of the cluster objects' disposal failures, after the cluster is
deleted; frame teardown logs them and keeps going.

What stays the same: a cluster still needs an elected leader before its object can be melded, only the elected leader
can purge it, and `describe_live_creation_status()` still reports `"cluster_leader"` as its `storage_scope_kind`.

## An ownership transfer brings the spell's objects with it by default

**Breaking change:** `Conduit.transfer_spell_ownership()` now defaults to `move_creations=True`: the objects the old
owner's creations hold for the transferred spell, for every version of it, move into the new owner's creations. A
`unique` spell therefore stays one object - the new owner serves the instance the old owner's consumers already hold,
and disposes it once, when the new owner is cleaned up. Until 0.2.8238 the default was `False`, which took the old
owner's objects for the spell's active version out of its creations and neither moved nor disposed them: the new
owner built a second instance of a `unique` spell while the old owner's consumers kept the first, and nothing ever ran
the first one's disposal methods.

```python
class Tool:
    def close(self) -> None: ...


class Worker:
    def __init__(self, tool: Tool) -> None:
        self.tool = tool


book = md.Spellbook()
tool_id = book.bind(spell=Tool, existence="unique", disposal_method_names=["close"])
book.bind(spell=Worker, existence="unique_per_conduit")
owner = book.conjure(dynamic=True, name="owner")
target = md.Spellbook().conjure(dynamic=True, name="target")

worker = owner.meld("Worker")
owner.transfer_spell_ownership(spell=tool_id, target_conduit=target)
assert target.meld("Tool") is worker.tool     # 0.2.8238 built a second Tool here
owner.cleanup()                                # leaves the Tool open: the target owns it now
target.cleanup()                               # closes it, once
```

To keep the old behaviour, pass `move_creations=False`; the transfer report's `options` show the value used.

A transfer hands over stewardship, not a working setup, and the docstring and the ownership guide now say so
(0.2.8240). The spells the transferred spell depends on stay with the old owner unless `include_dependencies=True`
moves the direct ones, so the new owner can start out broken: the moved objects keep the dependencies they were
built with, and the old owner's teardown disposes the ones it owns while the moved objects still hold them. That
is expected in a runtime agents iterate in. The new owner purges what it does not want, binds the dependencies it
needs - a meld that must build the spell without them raises `UnresolvedInputError` naming each missing input -
and melds its own version, while the old owner cleans up its own scope.

What stays the same: a transfer disposes nothing. With `move_creations=False` the old owner's objects for the spell's
active version are taken out of its creations, neither moved nor disposed, and the new owner builds its own; objects
of parked versions stay in the old owner's creations. A moved object replaces whatever the new owner's creations
already hold for the same spell - for example a `unique_per_conduit` object it melded while borrowing the spell - and
the replaced object is not disposed. `unique_per_conduit_lineage` objects stay with the lineage that resolved them,
and spellspace and cluster objects are not kept in a conduit's creations, so `move_creations` does not reach them.
Everything else a transfer does is unchanged: stewardship of every version of the spell moves, borrowers are unshared
or repointed, and owned dependencies move only with `include_dependencies=True`.

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
- The packaged system documents describe the elastic retention of the kernel pools: the sizes, the stretch
  under pressure, the timed decay and the prewarm ceiling.
- The packaged system documents describe where a `many` dependency built for a longer-lived object is recorded (with
  the holder's owner), the store selection and live-creation probe that follow, and the specializer's eligibility.
- The ownership guide (`docs/intermediate/ownership.md`) says a transfer moves the spell's objects by default and
  hands over stewardship, not a working setup, and how the new owner rebuilds.
- The packaged system documents (`melder.__architecture__`) open with what Melder is: not a DI container but a
  runtime agents live and build in, where many agents iterate on the same objects through versions, borrowers
  follow a notch, versions coexist (MutationResearch, compositions, one `unique` object per version) and agents
  build the subsystem they are in. Correctness lives in the structure - bindings, indexes and versions, ownership,
  contracts and links, lineage and clusters, verdicts and the Crystallizer's record; the objects Melder builds are
  working material that agents iterate on, leave pending and clean up; Melder disposes what its own creations
  record when they end and does not police the objects it hands out.
- The packaged system documents no longer call a notch's borrower update a known limitation: each linked borrower
  parks its copy of the old version, index-link borrowers move to the new version and build it at their next
  meld, and older versions stay alive.
- The packaged system documents describe a root leaving its cluster at teardown, the team store a cluster owns,
  the record that carries a slotted object's `many` children through purge, transfer and disposal, and the
  transfer default and handover; the code-map extents of the files these changes touched are remeasured.
- The internal-bind guard manifest holds 623 entries at 0.2.8238 (622 at 0.2.8227): `HolderDisposalEntry`, the
  record that keeps a slotted object's `many` children with it, joined.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8240.
