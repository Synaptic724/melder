# Melder 0.2.8265

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
an argument the bind pipeline takes itself (`spell`, `existence`, `profile`, `spell_id` and the rest, 28 in all,
the four `managed_spell_*` options among them) raises `TypeError` naming every such key. Metadata is kept as a
shallow snapshot: later changes to your dict do not reach the declaration, while the values are the objects you
passed. `resolvable` is stored as given, and `bind` checks it when the module is scanned.

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

`Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` on top of it (`find_spell_by_spell_id` and
`get_spell_by_spell_id` since 0.2.8253, next section), used to walk the Book's index map while other threads bound,
removed or parked spells. On the free-threaded build a lookup of a spell nobody was touching could then raise
`RuntimeError: dictionary changed size during iteration`, raise
`AttributeError: 'SpellIndex' object has no attribute '_spells_in_index'`, or return `None` for a spell that was
still registered. The lookup now answers from the Book's id maps: one read for an active version's spell_id, two
for a parked one, the same cost at any Book size, and no lock taken.

What stays the same: a spell_id the Book does not own still returns `None`. Two answers sharpen: a parked version
disposed while a lookup runs no longer makes it raise - the lookup returns the spell it read, or `None` once the
spell_id has left the Book - and a lookup that lands inside a notch or an ownership transfer of that same spell can
return `None` for that instant, as a lookup inside a notch already could. The returned spell is a reference you
borrow, not a lease: a later removal, notch or transfer can retire or move it. What a spell_id answers changed at
0.2.8253 (next section).

The same fix reaches the other places that walked a Book's spells while other threads changed them (0.2.8230).
`Conduit.get_spell_permissions` and the Rift command surface's spell lookup now answer from the id maps too;
`Conduit.validate_resolution`, `Spellbook.inspect_spell` searching the frame's other Books, contract lookups and
the ownership-transfer impact check walk a snapshot; and a `bind` on another thread now waits for a walk that holds
the Book's lock instead of resizing the map under it. None of them can raise
`RuntimeError: dictionary changed size during iteration` any more. `SpellIndex.has_spell` racing the index's
cleanup raises its documented `RuntimeError: SpellIndex has already been cleaned.` instead of `AttributeError`, and
a contract lookup that meets an index its owner has cleaned treats it as holding nothing instead of raising.
Answers on a quiet Book are unchanged.

`Conduit.get_spell_by_spell_id` (`get_spell_by_id` until 0.2.8253) and `Conduit.get_conduit_by_spell_id` keep
raising `ValueError` for an id no conduit in the frame claims, as `get_*` lookups do (a `find_*` lookup returns
`None`); their docstrings said they return `None`, and now document the raise. `get_conduit_by_spell_id` is
annotated as returning a `Conduit`.

## A spell_id lookup answers the spell it names: `find_spell_by_spell_id` and `get_spell_by_spell_id`

**Breaking change:** `Spellbook.find_spell_by_id` and `Conduit.get_spell_by_id` are renamed `find_spell_by_spell_id`
and `get_spell_by_spell_id`, with no alias - the old names raise `AttributeError`; the arguments are the same - and
they answer exactly the spell a spell_id names. A spell_id, the id `bind` and `bind_inactive` return, names one
version, and the lookups return that version, active or parked. Until 0.2.8253 a parked spell_id - a version staged
with `bind_inactive`, or one a notch moved away from - answered with the version its spell index had active in its
place. What an index has active is a lookup by the index:

```python
class ReportService:
    def render(self) -> str:
        return "v1"


class ReportServiceV2:
    def render(self) -> str:
        return "v2"


book = md.Spellbook()
v1 = book.bind(spell=ReportService, existence="unique")
reports = book.conjure(dynamic=True, name="reports")
index = reports.get_spell_by_spell_id(v1).spell_index
v2 = reports.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique")

assert reports.get_spell_by_spell_id(v2).spell_id == v2        # the parked version; the old lookup answered v1
assert book.find_spell_by_spell_id(v2).spell_id == v2
assert reports.get_spell_by_index_id(index.id).spell_id == v1  # the version the index has active

reports.notch_spell(spell_index=index, spell=reports.get_spell_by_spell_id(v2))   # a no-op with the old lookup
assert reports.meld(spell_id=v2).render() == "v2"
```

- Code that passed a parked spell_id to reach the current version asks the index instead:
  `conduit.get_spell_by_index_id(conduit.get_spell_by_spell_id(spell_id).spell_index.id)`.
- `Conduit.get_spell_permissions(spell_id)` answers the permissions that version was bound with (for a parked
  spell_id it answered the active version's).
- `find_spell_by_spell_id` also answers a version moved out with `remove_from_spell_index` into an index of its own
  (it returned `None`). `get_spell_by_spell_id` still raises `ValueError` ("Spell version <id> not found in any
  conduit.") for such a version, because the index the move creates is missing from the frame's registry - a
  separate defect, with its own fix pending.
- `add_spell_to_contract(spell_id=...)` and `remove_spell_from_contract(spell_id=...)` take a parked spell_id. They
  raised `RuntimeError` "Provided spell_id '<parked>' does not match inspected ID '<active>'."; a grant now parks
  the copy on the borrower, as a grant of the parked `Spell` does. `get_spells_in_contract_by_conduit` lists each
  version this conduit granted with that version's own `Spell` (a parked grant was listed with the active one's).
- `transfer_spell_ownership(spell_id=...)` still moves the spell index the spell_id belongs to, with the version
  that index has active on this conduit. A spell_id this conduit cannot resolve to an active version of its index -
  another conduit's spell whose index this conduit neither owns nor borrows - is refused up front with
  `RuntimeError` "[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit.", where the
  transfer failed later with "Source conduit does not own the spell.".
- In Rift rooms the command `get_spell_by_id` is now `get_spell_by_spell_id`, listed under that name by
  `list_supported_command_methods`, and both it and `get_spell_by_source_id` answer the spell their argument names:
  a capability or codegen room returns the `Spell`, a static room its live object. Nexus publishes the version each
  index has active, so a room refuses a parked version's spell_id or source id instead of answering another
  version. A static room's refusals name what was asked - "Spell id '<id>' is not live in frame '<frame>'." and
  "Spell '<source_id>' ..." where they said "Spell index '<index id>' ..."; a lookup by index id keeps that wording.

What stays the same: an active version's spell_id answers as before; a spell_id the Book does not own returns `None`
from `find_spell_by_spell_id`, and `get_spell_by_spell_id` raises `ValueError` for one no conduit of the frame
claims; neither takes a lock. `get_spell_by_index_id`, ownership transfers and dependency grants answer as before.
The contract lookups that resolve a granted spell_id through its index - `get_spell_in_contracts` and the versions
a conduit was granted in `get_spells_in_contract_by_conduit` - are unchanged. Nothing recorded, cached or persisted
changes.

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

A transfer now moves each version's owner record both ways (0.2.8246). A spell version records the root that
owns it and the creations it builds into; until 0.2.8246 a transfer moved that record for the active version only,
and a failed transfer left it pointing at the new owner:

- A version parked before the transfer kept building into the old owner's creations: after `notch_spell` to it on
  the new owner, its `unique` object was stored in the old owner's creations, and a managed version raised "has no
  pool to lease from". Every parked version that carries an owner record now names the new owner.
- A transfer that failed after it moved the record left the active version on the new owner's creations, so the old
  owner's next meld built a second `unique` object there instead of returning its own; a managed spell raised "has
  no pool to lease from", or, with `move_creations=False`, leased from an empty pool the failed transfer left in the
  new owner. A failed transfer now puts every owner record back, and the old owner melds as before.
- A version staged with `bind_inactive` before `conjure` has carried an owner record since 0.2.8248 (`conjure`
  gives it one), so a transfer moves that record like any other version's.

What stays the same: a transfer disposes nothing. With `move_creations=False` the old owner's objects for the spell's
active version are taken out of its creations, neither moved nor disposed, and the new owner builds its own; objects
of parked versions stay in the old owner's creations. A moved object replaces whatever the new owner's creations
already hold for the same spell - for example a `unique_per_conduit` object it melded while borrowing the spell - and
the replaced object is not disposed. `unique_per_conduit_lineage` objects stay with the lineage that resolved them,
and spellspace and cluster objects are not kept in a conduit's creations, so `move_creations` does not reach them.
Everything else a transfer does is unchanged: stewardship of every version of the spell moves, borrowers are unshared
or repointed, and owned dependencies move only with `include_dependencies=True`.

## `Existence.managed_spell_quantity`: objects leased from a root-owned pool and released back

A seventh Existence member for objects that are expensive to build and safe to reuse - a logger, a client, a
parser. A meld, or an injection into a constructor, leases an idle object from the spell's pool, kept by the root
conduit that owns the binding, or builds one; the holder gives the object back explicitly and the next lease reuses
it. 0.2.8241 added the member and its place in Melder's lifetime rules, 0.2.8242 its bind options, 0.2.8243 its pool
in the owning root, 0.2.8244 the way objects go back (`ReleaseManagedSpell`), 0.2.8245 leasing through a meld
(`Conduit.managed_spell_meld` included), 0.2.8246 its pools in an ownership transfer, and 0.2.8254 took its four
settings out of its spell_id.

- `Existence.managed_spell_quantity` (`str()` gives `"managed_spell_quantity"`) comes after the six existing members.
- At conjure, a managed spell may depend on `unique` spells, other managed spells and `many` spells; a dependency on
  a `unique_per_conduit_cluster`, `unique_per_conduit_lineage`, `unique_per_conduit` or `unique_per_spell_space`
  spell is refused with the existing scope-ordering message, because the pool outlives those scopes. Any spell may
  depend on a managed one.

A managed binding takes four keyword options on `Spellbook.bind` and `bind_inactive`, `Conduit.bind` and
`bind_inactive`, `scan_bind` and `SpellBinder` (`as_managed_spell_quantity(mode, limit=..., timeout_seconds=...,
reset_methods=...)`), and the Spell keeps them (0.2.8242):

```python
class Parser:
    def reset(self) -> None: ...


book.bind(
    spell=Parser,
    existence="managed_spell_quantity",
    managed_spell_mode="queue",           # a name, or a ManagedSpellMode member
    managed_spell_limit=8,                 # at most 8 parsers alive at once
    managed_spell_timeout_seconds=2.5,     # a lease waits up to 2.5 s for one to come back
    managed_spell_reset_methods=["reset"],  # run on every release, in order
)
```

- `managed_spell_mode`: `elastic` (the default) always builds when no idle object is waiting and keeps up to
  `managed_spell_limit` idle objects (default 256); `limited_quantity` refuses at `managed_spell_limit` objects
  alive; `queue` waits for a release, up to `managed_spell_timeout_seconds`, then refuses. The enum is
  `ManagedSpellMode` (`melder.aether.spellbook.existence.managed_spell_mode`).
- `managed_spell_limit` is required for `limited_quantity` and `queue`; `managed_spell_timeout_seconds` is
  required for `queue` and refused for the other two modes.
- `managed_spell_reset_methods` names zero-argument methods of the class.
- `spell.managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds` and
  `managed_spell_reset_methods` read them back (the default limit filled in); other spells answer None, None,
  None and `()`.
- The four options are settings of the one spell, not part of its spell_id (0.2.8254): one class bound managed at one
  address with one list of disposal methods has one spell_id whatever its mode, limit, timeout or reset methods.
  Staging it again with other settings (`bind_inactive` on its index) is refused as the same spell - `RuntimeError`
  "Spell ID collision detected. ..." - and nothing is registered. A version that differs in more than its settings
  (another class, binding name or disposal methods) is a version of its own, as before.
- To change a managed spell's settings, dispose it and bind it again. The spell_id stays, and the pool the earlier
  binding left takes the new settings with its idle objects and its count, so an object leased before goes back to
  it. The rebind destroys nothing: every object alive stays alive and counted, even above a lower limit, and the
  pool settles to the new limit as objects are released; a lease waiting in a `queue` pool checks the new settings.

```python
sid = book.bind(spell=Parser, existence="managed_spell_quantity",
                managed_spell_mode="limited_quantity", managed_spell_limit=1)
root = book.conjure(dynamic=True, name="parsers")

parser = root.meld(spell_id=sid)
root.cleanup_spell(spell=root.get_spell_by_spell_id(sid))   # the pool stays, with the parser out
assert root.bind(spell=Parser, existence="managed_spell_quantity",
                 managed_spell_mode="limited_quantity", managed_spell_limit=2) == sid   # the same spell
second = root.meld(spell_id=sid)                  # limit 2 now: a second parser
md.ReleaseManagedSpell().release(parser)          # back to the same pool, counted
```

- Builds 0.2.8242-0.2.8253 hashed the four settings into the spell_id, so a managed spell bound by one of them has
  another spell_id from 0.2.8254 on (no other spell's id moves). A Crystallizer record made by one of them restores
  through `bind`, which gives each managed spell its new spell_id. Under process-wide spell ids (the default), one
  managed class bound at one address in two frames now has one spell_id whatever its settings, so the second binding
  is refused as a duplicate, as for any other class: at its `bind` once the first frame's Spellbook is conjured
  ("Spell ID collision detected. ..."), otherwise at its `conjure()` ("Conjure refused: ... already registered").

`bind` refuses, before anything is registered and with a message that says what to change: a `managed_spell_*`
option on another existence (`ValueError`); a managed binding of a function, method, lambda or existing object
(`TypeError`: the pool builds instances of a class); an unknown mode; a limit that is not an int of at least 1, or
is missing where required; a timeout where it does not apply, missing in `queue`, or not a positive finite number;
and reset names that are not a list or tuple of method names of the class.

The Crystallizer records a managed spell's options, and restore and the spell-index graft bind it with them, so
it comes back with its own id. Records are stamped 4.2.0 (they were 4.1.0): only a managed spell's record gains
the four keys, a 4.1 reader ignores them, and 4.1 records restore as before.

Every managed spell version now has a pool in the store of the root conduit that owns it (0.2.8243): conjure
gives each version its pool - the active ones, and since 0.2.8248 the ones staged with `bind_inactive` before
it - and so does a later `bind` or `bind_inactive` on the root. The root's teardown
disposes what its pools hold - the idle objects and every `many` child built for a pooled object - and leaves the
objects that are out to whoever holds them; disposing the spell (`cleanup_spell`) or notching away from it leaves
its pool in place until the root ends. What you can see now:

- `conduit.has_live_creation(...)` and `describe_live_creation_status(...)` answer for a managed spell from the
  owning root's pool, asked through the root or one of its lessers: live while any object the pool built is alive,
  `creation_count` the number alive (idle plus out), `storage_scope_kind` `"managed_pool"`. They raised
  `RuntimeError` ("Unsupported existence ... for live creation probe.") before 0.2.8243.
- `conduit.purge(...)` of a managed spell returns 0 and leaves the pool alone (it raised `RuntimeError`
  "Unsupported purge existence"); a spellspace's `purge` still refuses it. A pool is not purged: you give objects
  back, and the root's teardown disposes the rest.
- Static Rift rooms report a managed spell as an unsupported static existence, as they do `many`: there is no single
  stored object to hand out.
- `ManagedSpellExhaustedError` (`melder.utilities.custom_exceptions.managed_spell_exhausted_error`), a
  `MeldExecutionError` with `mode`, `limit` and `timeout_seconds`, is what a lease will raise when a
  `limited_quantity` pool has every object out ("Managed spell 'Parser' (limited_quantity, limit 8) has all 8
  objects out. Release one with ReleaseManagedSpell().release(obj) before melding another, or bind it with a higher
  managed_spell_limit.") or a `queue` pool had none free within its timeout. Nothing is built when it is raised.

Objects go back through `ReleaseManagedSpell` (0.2.8244). It, `ManagedSpellLease`, `ManagedSpellMode` and
`ManagedSpellExhaustedError` are importable from `melder`:

```python
from melder import ReleaseManagedSpell

release = ReleaseManagedSpell().release   # bind it once in a hot loop
release(parser)                           # its resets run in order, then it waits for the next lease

with ReleaseManagedSpell().managed(parser) as p:   # given back when the block ends, raised or not
    p.parse(text)
```

- `ReleaseManagedSpell()` is a process singleton like `Aether`: Aether builds it at boot and cleans it with the
  world. A release needs no conduit: the object's class finds its pool with one dict read, then the pool's
  put-back - about 50 ns over the pool call with the method bound once; the `ReleaseManagedSpell()` call itself
  costs about 70 ns more, as `Aether()` does.
- When one class is managed by several pools - two binding names, two roots, two frames, two versions of one
  index - the pool of the version its index selects takes the object. Otherwise pass `spell_id=...` or
  `conduit=...` (a root or one of its lessers); a `ValueError` lists the candidates (spell id, binding, frame,
  root, active) while the choice is still open. A class with no live pool raises "<Class> is not a managed spell
  class in any live root: bind it with existence=Existence.managed_spell_quantity, or its root was torn down."
- `managed(obj)` returns a `ManagedSpellLease`: `release()` gives the object back once and later calls do nothing;
  `object` raises once it was released. `release_all(objects)` attempts every object, then raises one
  `ExceptionGroup` of the failures. `describe(cls)` answers one dict per pool: mode, limit, count, idle and out
  objects, the root holding it (`holding_conduit_id`) and whether it is the active version.
- A reset that raises destroys the object (its disposal methods run) and the error propagates. Once the root ended,
  `release` raises the not-managed `ValueError` (its pools left with it), and a lease made before raises
  `RuntimeError` ("The pool of managed spell 'Parser' was torn down with its root conduit; the object is yours to
  dispose.").
- Releasing trusts the caller: nothing records which objects are out, so give back only what a lease handed you,
  once.

Leasing works from 0.2.8245. A meld of a managed spell, and every injection of one into a constructor, takes an idle
object from the pool, or builds one when none is waiting; the plan Melder compiles for the meld does it inline:

```python
parser = conduit.meld(Parser)            # an idle parser, or a new one
release(parser)                          # the next lease gets this object back

handler = conduit.meld(Handler)          # Handler(parser: Parser) is `many`: each meld leases one parser into it
release(handler.parser)

with conduit.managed_spell_meld(Parser) as p:   # meld and lease in one call; given back when the block ends
    p.parse(text)
```

- Each injection is its own lease: two constructors in one meld get two objects, and a holder keeps what it was
  given for its life. A meld through a lesser conduit or a spellspace leases from the owning root's pool.
- A warm cycle - a meld that takes an idle object, plus its release - measured about 0.32 us on an automatic root
  and 0.74 us on a dynamic one (CPython 3.14t, either GIL mode): about one release more than a `many` meld.
- A `limited_quantity` meld raises `ManagedSpellExhaustedError` when every object is out, and a `queue` meld waits
  for a release up to its timeout; nothing is built while it waits or when it raises.
- When a construction fails after it was handed leased objects - its constructor raises, a sibling dependency
  fails, or another meld finished the same shared object first - Melder gives those objects back to their pools
  before the error propagates, and a failure to give one back is added to the error as a note. It is the one case
  Melder returns an object itself.
- Overrides: a value supplied for the holder's parameter takes no lease; values supplied for the managed spell's
  own parameters build a fresh object with them, which the pool neither hands out nor counts.
- The `many` dependencies with disposal methods that a pooled object was built with stay with it, and are disposed
  with it when an elastic pool trims it or the root ends.
- A direct meld of a managed spell runs its activation hooks (the spell's and `on_meld_activation`) on every lease,
  a reused object included.
- `Conduit.managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)`
  resolves its target as `meld` does and returns a `ManagedSpellLease`. It refuses a spell of another existence
  before melding anything ("managed_spell_meld leases a managed spell; 'Config' is unique. Meld it with meld(), or
  bind it with existence=Existence.managed_spell_quantity."), and raises `MeldExecutionError` ("Managed spell
  'Parser' has no pool to lease from: its owner root was torn down, ...") when the version has no pool. A lease on
  an object built fresh by own-parameter overrides gives that object to the pool when it is released.
- Compiled plans cached by earlier builds are retired: the creation cache moves to generation 21 (0.2.8248), which
  retires the bundles written before managed spells existed, and to 22 (0.2.8254), which retires those written while
  the settings were part of the spell_id. Every release change already makes the first `conjure()` after an upgrade
  compile cold, so nothing else changes.

Pools follow an ownership transfer (0.2.8246). A pool is one more record of its spell version, so
`transfer_spell_ownership` treats it as it treats the others:

- With `move_creations=True` (the default) every version's pool moves to the new owner with its idle objects, its
  count and the `many` children recorded with its objects: the new owner leases the same objects, releases reach
  the moved pool, and `ReleaseManagedSpell().describe(cls)` names the new owner as `holding_conduit_id`.
- With `move_creations=False` the new owner leases from a new, empty pool, and the old pool's idle objects are
  neither moved nor disposed. A version parked at the time also gets a new pool in the new owner, while its old pool
  stays with the old owner until that root ends, as a parked version's other objects do; once that version is
  notched in on the new owner, a release by class finds two pools of the selected version and asks for `conduit=`
  (a lease's own `release()` is unaffected).
- A transfer that fails leaves every pool where it was, and the old owner keeps leasing from it.
- A release that runs while its spell is being transferred can find no pool for that moment and raises the
  not-managed `ValueError`; release again once the transfer has returned.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values, record or compiled plan changes; a root store without managed spells disposes exactly as before.

## A non-resolvable definition no longer sends every meld of its Book through validation

A Spellbook that registers a definition with `resolvable=False` - a `Protocol` (which must be bound that way), an
abstract base, or a class kept so agents can discover, inspect and version it while its consumers receive the value
by override - paid for validation checks on every meld. Such a definition never receives a resolution verdict, so
Melder counted it as validation still owed for the life of the Spellbook: every meld in that Spellbook, of any
spell, went through the meld-time validation gate, and none took the warm fast path. From 0.2.8247 Melder records
the definition as one that owes no verdict and leaves it out of that decision, so melds in such a Spellbook cost
what they cost without it.

```python
class Clock(Protocol):
    def now(self) -> float: ...


class Report:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


book = md.Spellbook()
book.bind(spell=Clock, existence="unique", resolvable=False)   # discoverable, never resolved
book.bind(spell=Report, existence="many")
root = book.conjure()

report = root.meld(spell=Report, override={"clock": time_source})   # 0.4 us warm; 13 us before 0.2.8247
```

Measured on CPython 3.14t with the GIL off: a warm meld in a Spellbook holding one `Protocol` definition went from
15.1 to 0.26 us after `conjure()` and from 16.4 to 0.73 us after `conjure(dynamic=True)`; the example above went
from 12.9 to 0.39 us, and from 13.2 to 0.40 us with the GIL on.

Notching between versions of one spell index follows the version selected each time: while a `resolvable=False`
version is selected the index is left out, and once a resolvable version is selected again it is validated before
its first meld - in the conduit that owns it and in every conduit that borrows it through an index link.

What stays the same: the definition stays in the graph as before - `bind` and `bind_inactive` accept it, Nexus and
the Rift viewers show it, the Crystallizer records its capability - and a meld of the definition itself is still
refused with the same `MeldExecutionError`. A Spellbook without such a definition, `conjure()` and `bind` cost what
they did, and no public signature changes.

## A version staged before `conjure` melds after a notch

`bind_inactive` now behaves the same before and after `conjure()`. A version staged with `bind_inactive` on a
Spellbook before its `conjure()` was never wired to the root conduit, so once `notch_spell` made it the active
version, its first meld raised `RuntimeError` ("Spell has no configured CreationContextFactory.") whatever its
existence, and a managed version raised `MeldExecutionError` ("... has no pool to lease from ..."). Staging after
`conjure()` was the only way that worked. From 0.2.8248 `conjure()` wires every version staged before it, exactly as
`bind_inactive` wires one staged after it. Staging before `conjure()` needs a world that is already dynamic - a
Spellbook joining a frame an earlier `conjure(dynamic=True)` settled:

```python
class ReportService:
    def render(self) -> str:
        return "v1"


class ReportServiceV2:
    def render(self) -> str:
        return "v2"


owner = md.Spellbook().conjure(dynamic=True, name="owner")   # settles the world dynamic

book = md.Spellbook()                       # joins the dynamic world
v1 = book.bind(spell=ReportService, existence="unique", binding_name="v1")
index = book.find_spell_by_spell_id(v1).spell_index
v2 = book.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique", binding_name="v2")
reports = book.conjure(name="reports")      # inherits dynamic; wires v2 as well as v1

reports.notch_spell(spell_index=index, spell_id=v2)   # by spell_id since 0.2.8249 (next section)
service = reports.meld(spell_id=v2)         # a ReportServiceV2; RuntimeError before 0.2.8248
assert service.render() == "v2"
```

- Every existence: `unique`, `unique_per_conduit`, `many`, `managed_spell_quantity`, existing objects and
  functions. A managed version staged before `conjure()` has its pool from `conjure()` on, and
  `ReleaseManagedSpell().describe(cls)` lists it.
- Until its notch a staged version stays off resolution, as before: a meld of its id raises `KeyError` ("[MELD] No
  spell found with spell_id: ..."), and a staged existing object is not stored in the root's creations.
- The missing-pool message no longer names that cause or tells you to stage after `conjure()`: "Managed spell
  'Parser' has no pool to lease from: its owner root was torn down, or its owner store holds no pool for this
  version. Meld it through a live root that owns it."

What stays the same: active versions, a `bind_inactive` after `conjure()`, ownership transfers, spell ids and
records. Restore and the spell-index graft stage versions after `conjure()`, so they worked before and behave as
before.

## `notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks its target

`Conduit.notch_spell` makes one version of a spell index the active one - the notch in stage -> notch -> meld. Until
0.2.8249 it took only the version's `Spell`, and no public call returned the `Spell` of a staged version:
`bind_inactive` returns a spell_id, and until 0.2.8253 `get_spell_by_id` / `find_spell_by_id` answered a staged
(parked) spell_id with the index's active version, so a notch to what they returned changed nothing.
`add_to_spell_index` and `remove_from_spell_index` had the same gap, since they move only a parked version. From
0.2.8249 all three take the spell_id `bind` or `bind_inactive` returned:

```python
class ReportService:
    def render(self) -> str:
        return "v1"


class ReportServiceV2:
    def render(self) -> str:
        return "v2"


book = md.Spellbook()
v1 = book.bind(spell=ReportService, existence="unique")
reports = book.conjure(dynamic=True, name="reports")
index = reports.get_spell_by_spell_id(v1).spell_index

v2 = reports.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique")
reports.notch_spell(spell_index=index, spell_id=v2)    # v2 is the active version now
assert reports.meld(spell_id=v2).render() == "v2"

reports.notch_spell(spell_index=index, spell_id=v1)    # and back to v1
assert reports.meld(spell_id=v1).render() == "v1"

reports.remove_from_spell_index(spell_id=v2, source_index=index)   # parked v2 gets an index of its own
reports.add_to_spell_index(spell_id=v2, target_index=index)        # and comes back; its emptied index goes
assert index.spells_in_index() == {v1, v2}
```

- Name the spell by `spell_id=` or by `spell=`, exactly one, on all three: both or neither raise `ValueError`, and a
  `spell_id` that is not a string, or a string passed as `spell`, raises `TypeError`.
- A `spell_id` is resolved inside the call to the exact spell the conduit's Spellbook owns, active or parked.
- A notch checks its target before it starts and again inside its transaction: the spell must be one the conduit's
  Spellbook owns and a member of `spell_index`. Otherwise a `ValueError` names its spell_id and the remedy -
  "notch_spell: spell_id '<id>' is not owned by this conduit's Spellbook. Notch it through the conduit of the
  Spellbook that owns it, or stage the class on this index with bind_inactive(spell_index=...), which returns the
  spell_id to pass." or "notch_spell: spell_id '<id>' belongs to another SpellIndex, not the one passed. Pass its
  own index - conduit.get_spell_by_spell_id('<id>').spell_index - or move it onto this index with
  add_to_spell_index first." A refused notch changes nothing.
- The index moves refuse a `spell_id` the conduit's Spellbook does not own before anything starts, for example
  "add_to_spell_index: spell_id '<id>' is not owned by this conduit's Spellbook. Call add_to_spell_index through the
  conduit of the Spellbook that owns it." Past that, the Spellbook refuses as before (`RuntimeError`): an active
  spell (notch away from it first), a spell it does not own, a target index it does not own, and a spell that is not
  a member of the source index or is its only member (`cleanup_spell` disposes that).
- Until 0.2.8249 nothing checked a notch's target, and three wrong targets damaged the Spellbook. A version staged on
  another index of the same Spellbook was accepted and corrupted both indexes: a meld of this index's old version
  raised `KeyError`, and a meld of the moved version `RuntimeError` ("Cannot build CreationContext before
  spell_codegen_creation exists."). Another index's active version, or another Spellbook's version, raised
  `RuntimeError` ("Owned spell_id not parked for reactivation") after this index's active version had already been
  parked, so the index had no active version until a notch back. Each now raises the `ValueError` above and leaves
  both indexes as they were.
- A notch to the `Spell` that `get_spell_by_id` or `find_spell_by_id` returned for a parked spell_id stayed a
  no-op: it was the active version. Since 0.2.8253 `get_spell_by_spell_id` and `find_spell_by_spell_id` return the
  parked version itself, so a notch to it moves the index ("A spell_id lookup answers the spell it names", above).
- The docstrings of the three verbs say the conduit admits their transaction (the two index moves said the
  Spellbook did), and `remove_from_spell_index`'s no longer says that removing the active version leaves the index
  selecting a non-member: the Spellbook refuses an active version, and always did.

What stays the same: `spell=` on all three (a notch's target is now checked the same way), a notch to the active
version (it changes nothing), what the three verbs return, borrowers following a notch, and what the index moves
do.

## A satisfied `SpellContract` is not checked on every meld; a notch reaches every spell that depends on the notched one

A spell whose constructor takes a `SpellContract` default - its provider lent by another conduit through
`add_index_to_contract` or `add_spell_to_contract` - had that contract checked again at every meld that went through
the meld-time validation gate: Melder read the constructor's signature, looked each contract up in the Spellbook's
contracted spells and rebuilt the spell's plan, about 1.6 ms a meld. From 0.2.8250 a satisfied contract is not
checked again. Whatever changes what a spell resolves marks the spell for revalidation instead, and its next meld
checks its contracts once and rebuilds against the versions active now, or fails with the error its first meld
would give. A notch is the change that matters most, because the notched version's `__init__` may differ: every
spell that depends on the notched one - by annotation or through a `SpellContract`, directly or through other
spells, in its own Spellbook or another - is marked, and builds the new version at its next meld.

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_spell_id(english).spell_index
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
lender.notch_spell(spell_index=index, spell_id=french)
assert borrower.meld(spell=Banner).text == "BONJOUR"   # rebuilt once, at this meld
```

Measured on CPython 3.14t: a warm meld of `Banner` went from 1558 to 2.8 us with the GIL off and from 1682 to 2.8
us with the GIL on. A change of provider costs one structural pass more at the next meld (0.8-1.1 ms), and a
notch's walk 0.2-0.5 ms more with 200 dependent spells.

A spell that depends on the notched one through an annotation follows it too, two hops away included:

```python
class Clock(Protocol):
    def now(self) -> str: ...


class Utc:
    def now(self) -> str:
        return "utc"


class Local:
    def now(self) -> str:
        return "local"


class Stamp:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock


class Report:
    def __init__(self, stamp: Stamp) -> None:
        self.stamp = stamp


book = md.Spellbook()
utc = book.bind(spell=Utc, spellframe=Clock, binding_name="clock", existence="many")
book.bind(spell=Stamp, existence="many")
book.bind(spell=Report, existence="many")
reports = book.conjure(dynamic=True, name="reports")
assert reports.meld(spell=Report).stamp.clock.now() == "utc"

clock_index = reports.get_spell_by_spell_id(utc).spell_index
local = reports.bind_inactive(spell=Local, spell_index=clock_index, spellframe=Clock, binding_name="clock",
                              existence="many")
reports.notch_spell(spell_index=clock_index, spell_id=local)
assert reports.meld(spell=Report).stamp.clock.now() == "local"   # "utc" before 0.2.8250
```

- **Breaking change:** a meld of a contract consumer whose provider's index was destroyed, or whose version grant
  was parked by a notch away, raises `SpellbookValidationError` - the error a first meld raises for a missing
  provider - where it raised `MeldExecutionError` ("SpellContract could not be resolved. Missing contracted
  provider for key (frame_key=..., binding_key=...) on param ..."). Both are `RuntimeError`s; code that caught
  `MeldExecutionError` there catches `SpellbookValidationError`.
- Every lost provider is reported by name - those two, an index unlinked, a link severed, a grant released, and a
  first meld with no provider - where the report said "No validation error was recorded for this spell; its
  validity is invalid, gated or disabled.": "Spell 'Banner' parameter 'greeter' has no provider for its
  SpellContract (frame_key='greeter', binding_key='greeter'): no active spell with that frame and binding name is
  contracted to this Spellbook. Contract one from a linked conduit (add_index_to_contract, or add_spell_to_contract
  for one version) and meld again. [SPELL_CONTRACT_MISSING_PROVIDER]"
- **Breaking change:** a spell that depends on a notched one builds the version now active at its next meld, or
  raises its first meld's error: `UnresolvedInputError` naming the parameter when the new version no longer
  satisfies it, `SpellbookValidationError` naming a dependency whose structure no longer validates. Before, one
  built before the notch went on building the old version, and one never built raised `RuntimeError` on every
  meld (for example "many_only manifest references unknown spell_id '<the old version id>'").
- A version grant (`add_spell_to_contract`) follows its version: a notch away parks the borrower's copy, as before,
  and a notch back makes it active again, so its consumers resolve it at their next meld; a grant of a parked
  version becomes active when that version is notched in. Until 0.2.8250 the copy stayed parked after the notch
  back, and its consumers had no provider until the version was granted again.
- Fixed with the same marks: after `remove_index_from_contract` a consumer kept building the released provider; it
  now fails its next meld as above. After a link or a grant, a spell that depends on a contract consumer kept a plan
  compiled while the provider was missing and built the consumer with its raw `SpellContract` default
  (`AttributeError: 'SpellContract' object has no attribute '...'`); it now rebuilds.
- Not changed yet: a meld of a borrower's contract consumer on another thread while its lender notches the provider
  can, on the free-threaded build with the GIL off, fail with an internal `RuntimeError` or return the consumer
  built with its raw `SpellContract` default, as before 0.2.8250; the next meld is correct. A follow-up orders such
  melds against the notch.

What stays the same: a mark changes state only - nothing is built, disposed or extracted when a provider changes,
and objects already built keep what they were built with (a `unique` consumer keeps its object after a notch and
builds the new version once it is purged). A spell whose providers did not change takes the warm path; first
melds, `conjure()` and `link` check contracts as before, and a dynamic world still accepts a consumer before its
provider is linked. No public signature changes.

## Unlinking an index after a notch removes every version's copy

A borrower that links an index with `add_index_to_contract` holds a copy of every version on it: the active
version's copy is live and the others are parked. After the owner notched the index - to a version staged with
`bind_inactive`, as in the first example above - `remove_index_from_contract` could fail with `RuntimeError`
"Spell version <spell_id> not found for conduit ID <owner id>." and leave the old version's parked copy behind for
good. The unlink removes the versions one at a time, in an order that follows the process's hash seed, and when it
reached the parked version first it removed the active version's copy in its place - in about half of all processes
(for the example below, 6 of the hash seeds 0-9). From 0.2.8251 removing a version's copy removes that version's
copy - the active one only when it is that version, otherwise the parked one - so the unlink completes in any order:

```python
# Continuing the first example above: the lender notched the index from English to French.
borrower.remove_index_from_contract(index_id=index.id, conduit=lender)   # raised in about half of all runs

borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "BONJOUR"
```

The same fix covers version grants: a borrower granted a version, then the new version after a notch, kept the old
version's parked copy and lost the new version's active copy when it released the old grant with
`remove_spell_from_contract`, so its consumers lost their provider. Now only the old version's copy goes.

What stays the same: when a borrower holds one version of an index, an unlink, a grant's release and an index
destroy remove the same copy as before, and a consumer of a removed active copy still fails its next meld with the
missing-provider report. No public signature changes.

## A cleanup of an index's active version is refused while parked versions remain

A spell index can hold parked versions beside its active one - staged with `bind_inactive`, or the version a notch
moved away from. `Conduit.cleanup_spell` has always refused to dispose the active version of such an index. The two
other ways to dispose a spell - its own `cleanup()` and `Spellbook.cleanup_and_remove_spell` - did not: they removed
the version and cleaned the index under its parked versions, which then stayed in the Spellbook uncleaned and out of
reach. A notch to one raised `AttributeError`, `add_to_spell_index` and `cleanup_spell` of one raised "SpellIndex has
already been cleaned.", the Spellbook's teardown left them, and their own `cleanup()` then raised "Spellbook has
already been cleaned.". From 0.2.8256 all three refuse, change nothing, and say how to go on:

```python
class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, existence="many", binding_name="english")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, existence="many", binding_name="french")

try:
    world.get_spell_by_spell_id(english).cleanup()     # until 0.2.8256: cleaned the index under French
except RuntimeError as error:
    print(error)    # Spellbook cannot remove spell <spell_id>: it is the active member of a multi-member index, ...

world.notch_spell(spell_index=index, spell_id=french)            # one remedy: notch first,
world.cleanup_spell(spell=world.get_spell_by_spell_id(english))  # then dispose the old version, now parked
assert world.meld(spell_id=french).greet() == "bonjour"
```

**Breaking change:** `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell(spell)` of the active version of an
index that also holds parked versions raise `RuntimeError` "Spellbook cannot remove spell <spell_id>: it is the
active member of a multi-member index, and disposing it would leave the index's parked versions without an active
one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with remove_from_spell_index
first." Retire such a version in the order you choose - Melder picks no version for you:

- Notch the index to a parked version, then dispose the old version with `cleanup_spell`: it is parked now.
- Dispose the parked versions with `cleanup_spell`; the active version is then the index's only member, and any of
  the three removes it with its index.
- Move the parked versions out with `remove_from_spell_index` - each gets an index of its own and stays parked -
  then remove the active version.

`cleanup_spell`'s refusal keeps its type and its moment and names the same remedies: "cleanup_spell: spell
<spell_id> is the active member of a multi-member index, and disposing it would leave the index's parked versions
without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
remove_from_spell_index first." (it said "...; notch away from it before disposing it.").

What stays the same: removing the only version of an index, which goes with its index; `cleanup_spell` of a parked
version; the teardown of a conduit, Spellbook or frame, which cleans every active version with its index as
before. No public signature changes.

## A spell_id is the SHA256 of the object's code, and one object is one spell

**Breaking change:** every spell_id moves once. A spell_id is now the SHA256 of the registered object's code - its
methods' and constructor's instructions and the constants they load, its class-level values, its base classes
outside the standard library and, for an existing object, its data - and of nothing from the `bind` call: the
spellframe, binding name, existence, disposal methods, `resolvable` and the managed settings are the spell's binding
(next section). Docstrings, comments and line numbers never move it; any change to the code does, a renamed local
variable included. Installed third-party code is named by its distribution and version instead of being read, so
upgrading a library moves the spell_id of a class built over it. The same code is the same spell_id in every
process, hash seed and GIL mode.

One object is one spell. Registering an object a second time is refused - under another binding name, existence or
spellframe, in a second Spellbook of the frame (under process-wide spell ids, the default), or staged again with
`bind_inactive`: `bind` and `bind_inactive` raise RuntimeError "Spell ID collision detected: this object is already
registered as spell_id <id>. ...", whose text names the rule and the remedies, and `conjure` refuses a second
Spellbook's registration of it. To upgrade: share the spell already registered instead of binding it twice (meld it,
or contract it to another conduit); to change how it is bound, `cleanup_spell` it and bind it again; to keep two
versions of a class, edit it - a new spell_id - and stage it with `bind_inactive`, then notch. An edited class
staged that way is now a new version even when only a method body changed (it was refused as a collision). Under
per-frame spell ids a class can still be bound once in each frame.

Also changed: `Bind.spell_id_inspector(spell)` takes the target alone (the binding keywords it took raise
TypeError), and `Spellbook.inspect_spell` finds a registered object by its code. Creation-cache bundles are cold
once. A Crystallizer record made before this release restores through `bind`, which gives each spell its new
spell_id and maps the old ones; a record that holds one object twice fails at its second replayed bind.

Known limits: `-O` changes the spell_id of code that holds an `assert`, including every `typing.NamedTuple` class,
whose base reads a standard-library function that asserts; whether two patch releases of one Python version give one
spell_id is not yet measured; a namespace package that several distributions install is named by the first in sorted
order; a bind costs 37-55 us more (conjure and melds are unchanged); and a definition rebound under another
slotted existence can meet the removed definition's object at its first meld.

## A spell's binding is a manifest with its own hash

`Spell.binding_manifest` and `Spell.binding_hash` (read-only) are how a spell is kept - its spellframe and kind,
address, existence, ordered disposal methods, `resolvable` and managed settings - and the SHA256 of that record;
`BindingManifest.describe()` gives both as plain data. Both creation-cache tiers key on the binding hash beside the
spell_id, so a spell bound another way never replays a plan built for its old binding. The SpellCrystal records the
binding hash (record 4.3.0; 4.x records still read), and a restore reports each binding it rebuilt differently -
under another receiving Spellbook's disposal order, say - in `RestoreReport.describe()["binding_changes"]`, where
the spell_id used to move.

## A version moved into an index of its own is found by its spell_id

`Conduit.remove_from_spell_index` moves a parked version out of its spell index into a fresh index of its own, where
it stays parked until you notch to it. Until 0.2.8259 the frame never learned about that index, so the version - parked
there or notched active there - could not be found by its spell_id from a conduit:

```python
class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, existence="many", binding_name="english")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, existence="many", binding_name="french")

world.remove_from_spell_index(spell_id=french, source_index=index)  # French gets an index of its own, parked
own_index = world.get_spell_by_spell_id(french).spell_index  # raised "not found in any conduit" until 0.2.8259
world.notch_spell(spell_index=own_index, spell_id=french)
assert world.get_conduit_by_spell_id(french) is world
assert world.meld(spell_id=french).greet() == "bonjour"
assert world.meld(spell_id=english).greet() == "hello"
```

- `get_spell_by_spell_id` and `get_conduit_by_spell_id` answer for such a version, parked or active; they raised
  `ValueError` "Spell version <spell_id> not found in any conduit.".
- A linked conduit's `add_spell_to_contract(spell_id=...)` and `transfer_spell_ownership` by spell_id proceed for
  it; both raised that `ValueError`. The borrower's copy is parked or active as the version is.
- Another Spellbook can no longer bind the same spell_id while the version sits in its own index: the bind raises the
  usual `RuntimeError` "Spell ID collision detected: this object is already registered as spell_id <id>. ...", in
  the same frame and, under process-wide spell ids (the default), in another frame. The bind used to be accepted,
  so two Spellbooks held one spell_id.
- `MutationResearch.residency_view(spell_id)` reads the version `parked` in its own index and `active` there once a
  notch makes it active; it read `declared_only`.

What stays the same: what `remove_from_spell_index` moves and refuses, the version staying parked until a notch,
moving it back with `add_to_spell_index` (its emptied index goes), and every lookup of a version in any other index.
No public signature changes.

## A Spellbook's teardown cleans its parked versions too

When a Spellbook is torn down - with its root conduit, or by `Spellbook.cleanup()` - it now cleans every version it
holds, parked ones included, and every spell index that only parked versions hold (one `remove_from_spell_index`
made). Until 0.2.8260 the teardown cleaned only the active versions and their indexes: a parked version stayed
uncleaned, an index of its own with it, and the version's own `cleanup()` raised "Spellbook has already been
cleaned.":

```python
class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, existence="many", binding_name="english")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, existence="many", binding_name="french")
parked = world.get_spell_by_spell_id(french)

world.cleanup()                 # the root's teardown tears the Spellbook down
assert parked.cleaned           # False until 0.2.8260
parked.cleanup()                # returns; raised "Spellbook has already been cleaned." until 0.2.8260
```

What stays the same: the teardown of a Spellbook whose versions are all active, the managed pools a root's teardown
cleans, and every cleanup call on a live Spellbook. No public signature changes.

## Cleaning up a spell takes it out of every contract first

When a lender cleans up a version with `cleanup_spell`, every conduit it shares that version with now lets it go
before it is disposed: a borrower that contracts the version's index with `add_index_to_contract`, and one granted
the version with `add_spell_to_contract`. Until 0.2.8261 the borrower kept its record of the version. An index link
kept a parked version the lender cleaned up, even past the borrower's own `remove_index_from_contract`; a grant kept
the version, parked or active; and a later notch to the same class, staged again, raised `AttributeError` in the
borrower update after the lender had switched, leaving the borrower with no active version:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_spell_id(english).spell_index
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

lender.cleanup_spell(spell=lender.get_spell_by_spell_id(french))  # the borrower lets French go as well
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")  # staged again: the same spell_id
lender.notch_spell(spell_index=index, spell_id=french)  # raised AttributeError until 0.2.8261
assert borrower.meld(spell=Banner).text == "BONJOUR"
```

- A borrower's meld of a granted version the lender cleaned up raises `KeyError` "[MELD] No spell found with
  spell_id: <spell_id>", as for a version it was never granted; it raised `AttributeError` "... object has no
  attribute '_resolvable'".
- `Spellbook.cleanup_spell` on a conjured Spellbook goes through its root conduit, and `cleanup_spell` through a
  lesser conduit releases the root conduit's contracts: until 0.2.8261 neither reached a borrower, and the
  Spellbook's own call did not tell index-link borrowers when the index went with its last version.
- After such a cleanup the borrower's `remove_index_from_contract` leaves nothing of the lender's versions behind.

What stays the same: what `cleanup_spell` refuses - the active version of an index that holds parked versions -
and a refused cleanup touches no contract; `cleanup_spell` disposes no object a version built; and
`Spellbook.cleanup_and_remove_spell` and a spell's own `cleanup()` release no contract. No public signature changes.

## A notch whose new version fails its check is refused, and nothing moves

`notch_spell` checks a version the first time it makes it active - its structure: what its constructor needs and
whether each need resolves to one provider. Until 0.2.8262 the check ran after the switch, and nothing undid the switch
when it failed: `notch_spell` raised `SpellbookValidationError`, yet the index stayed on the broken version, its
borrowers stayed on the old one, and neither the old version (by its spell_id) nor the index (by address) could be
melded until a notch back. Now a failing check puts everything back before the error is raised:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class Clock(Protocol):
    def now(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class UtcClock:
    def now(self) -> str:
        return "12:00 UTC"


class LocalClock:
    def now(self) -> str:
        return "06:00 local"


class TimedGreeter:                    # needs a Clock - and two are registered
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
timed = world.bind_inactive(spell=TimedGreeter, spell_index=index, spellframe=Greeter, binding_name="greeter",
                            existence="many")

try:
    world.notch_spell(spell_index=index, spell_id=timed)
except md.SpellbookValidationError as error:
    print(str(error).splitlines()[0])
    # notch_spell refused: 'TimedGreeter' (spell_id ...) failed its structural check, so the notch did not
    # happen; 'English' (spell_id ...) is still the active version of the index.

assert index.selected_spell_id == english      # it selected TimedGreeter until 0.2.8262
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised until 0.2.8262
```

- The error is still `SpellbookValidationError` with the same validation report; its first line now says the notch
  did not happen and names the version still active (or says the index still has none).
- After the refusal the index selects the version it selected, that version is active and melds by spell_id and by
  address, the refused version is parked again, borrowers never moved, MutationResearch records no promotion for
  it, and Nexus publishes the old version. A retry is checked, and refused, again.
- Any failing check is refused the same way: a constructor that takes its own class (`SELF_DEPENDENCY`) as well as
  an ambiguous provider (`AMBIGUOUS_PROVIDER`, above).
- `SpellbookValidationError` takes an optional keyword `preface`: one line of text put before the report, as the
  refusal does. Anything but a non-empty, single-line `str` raises `TypeError`; without it the message is unchanged.

What stays the same: a notch to a sound version, a notch to the active version (it changes nothing), a notch back to
a version used before, the error's type, and borrowers following a notch that stands.

## Staging a version keeps the active version's name

Staging a version with `bind_inactive` under the name the active version holds - the usual way to try a new version
before a notch - took that name from the active version until 0.2.8263: Melder released the active version's binding
signature and dropped its address, so a meld by name raised `KeyError`, `find_spell_index` raised, and another
Spellbook of the frame could bind the name while the active version still served. Moving a parked version out of the
index and back, and `cleanup_spell` of a parked version alone in its index, did the same. Now the active version keeps
its name through all three:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                             existence="many")

assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised KeyError until 0.2.8263

world.notch_spell(spell_index=index, spell_id=french)
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "bonjour"
```

- Staging under a name another Spellbook's active spell holds no longer releases that spell's name either; staging
  stays open to any name, and a parked version holds no name until a notch makes it active.
- Restores and grafts stage parked versions the same way, so a restored or grafted world keeps its active versions'
  names too.

What stays the same: what a notch does with names, staging under any name, and every public signature.

## Spell constructor reflection works on early Python 3.14 releases

Reading `Spell`'s constructor with `inspect.signature`, or creating a `Mock(spec=Spell)` or
`MagicMock(spec=Spell)` on early Python 3.14 releases, no longer raises
`NameError: name 'ManagedSpellMode' is not defined`. The managed-mode enum is available when Python reads
the annotation, preserving the optional enum type, keyword-only option and None default. Existing bind,
managed-pool and cleanup behavior is unchanged.

## Concurrent cluster adds admit one caller

When threads add the same conduit to a cluster at the same time, exactly one call succeeds and the
others raise the existing `ValueError` ("cluster membership is exclusive (one per conduit)"). This
also holds when the calls target different clusters: the conduit joins only the winning cluster.
Previously several calls could all succeed, and competing clusters could both retain the conduit.
Membership checking and registration now finish together before sharing starts.

## Packaging and documentation

- The README's "Declarative Binding by Module" example passes `permissions="create"`, without which it raised
  `TypeError`, and says that `scan_bind` takes `bind()`'s target options and does not register subclasses or
  instances of a decorated class.
- The packaged system documents (`melder.__components__`, `melder.__architecture__`) describe the scan
  declaration contract, the eligibility change and a scan flow; the scan code-map extent is remeasured.
- The packaged system documents describe how the spell_id lookup (`find_spell_by_spell_id` since 0.2.8253)
  answers from the Book's id maps and why it takes no lock.
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
- The README's lifetimes section is "Seven Lifetimes, Not Three": it lists `managed_spell_quantity` and links to
  its dedicated intermediate section. That section has a complete runnable example of request-scoped injection,
  explicit release, reset, lease-block reuse and root teardown, plus the three pool modes and links to lessons
  43 and 45-47. The docs chapter built from the lifetime table keeps its existing heading selector. The teardown
  section no longer says that a failing disposal method stops that object's remaining methods: every declared
  method runs, and the failures are raised together once the scope has ended (the behaviour since 0.2.80 and
  0.2.8203).
- The scopes guide (`docs/intermediate/scopes.md`) lists `managed_spell_quantity` in its purge table (a conduit's
  purge returns 0, a spell space refuses it), and the glossary defines a managed spell. The documentation site's
  API reference lists the four new root exports - `ManagedSpellMode`, `ReleaseManagedSpell` and `ManagedSpellLease`
  with the lifetime types, `ManagedSpellExhaustedError` with the public errors; since 0.2.8244 the site build had
  refused the root's export list without them.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) describe managed spells: the
  member and its Phase 6 rank, the bind options and their record, the pool in the owning root's creations,
  `ReleaseManagedSpell` and the lease, leasing through compiled melds and `managed_spell_meld`, and pools in an
  ownership transfer. The packaged graph describes the five new modules; the code-map extents of the changed files
  are remeasured, and line citations that had drifted since 0.2.8235 point at their code again.
- The internal-bind guard manifest holds 630 entries at 0.2.8257 (628 at 0.2.8244, 622 at 0.2.8227):
  `SpellCodeDigest` and `BindingManifest` joined at 0.2.8257; `HolderDisposalEntry`, the record that keeps a slotted
  object's `many` children with it, joined at 0.2.8238, `ManagedSpellMode` at 0.2.8242, the managed pool
  (`ManagedSpellQuantity`) and `ManagedSpellExhaustedError` at 0.2.8243, and `ReleaseManagedSpell` and
  `ManagedSpellLease` at 0.2.8244.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the lineage flag `SpellState.non_resolvable`, the registry's published set of flagged lineages and the
  validation flag's exclusion of them; the code-map extents of the six changed files are remeasured, and line
  citations into `spellbook.py` and `conduit.py` that had drifted point at their code again.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe `conjure()` wiring the versions staged before it and the creation cache's generation 21; the code-map
  extents of the five changed files are remeasured, and line citations into `spellbook.py`,
  `spellbook_creation_system.py` and `transfer_of_ownership.py` that had drifted point at their code again.
- The README's swap sketch (stage a version, notch to it, meld it, notch back) names the versions by their spell_id
  and runs as written; the expert guide on governed change (`docs/expert/governed-change.md`) shows promotion as
  `notch_spell(spell_index=..., spell_id=...)`, says a wrong target is refused and that the index moves take
  `spell_id=` too, and the expert walkthrough on notch-swapping a live object (lesson 17) swaps by spell_id.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the notch target - its two forms, the checks before and inside the transaction, the refusals - the
  index moves' `spell_id=`, and the corrected index-mutation sequence: the conduit starts the transaction, and
  the notch claims the Spellbook exclusively. The `conduit.py` code-map extent is remeasured, and line citations
  that had drifted point at their code again.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the contract recheck: the borrower Spellbook's marks, a notch's downstream walk, the meld's refresh of
  stale dependencies, the lost-provider report and a version grant's return on a notch back; the code-map
  extents of the changed files are remeasured, and their line citations remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the removal of one version's copy by its own spell_id; the `spellbook.py` code-map extent is
  remeasured, and its line citations remapped.
- Docstrings and comments that called a spell's id a "version id" now name it the `spell_id` (the id `bind`
  and `bind_inactive` return); the Phase 6 diagnostic `identity_mixing_detected` ends "instead of a
  spell_id." where it said "instead of a version id."
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the exact spell_id lookups: the renames, per-version permissions, the explicit index step of ownership
  transfer and the contract dependency walks, the exact grant check and the Rift rooms' lookups; the code-map
  extents of the changed files are remeasured, and their line citations remapped.
- The expert guide on bind hooks (`docs/expert/bind-hooks.md`) and the agent operations guide
  (`agents/MELDER_AGENT_OPERATIONS.md`) use the new names, and the guide's lookup trap now describes the exact
  lookup; the walkthroughs that call the lookups use the new names, and lessons 17 (notch-swapping a live object)
  and 26 (codegen create, modify, iterate) show a parked spell_id answering its own version. The expert guide on
  governed change (`docs/expert/governed-change.md`) says the same: a lookup by spell_id is exact, and the version
  an index has active is a lookup by the index (it said a parked spell_id answered the active version).
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe a managed spell's settings as settings of the one spell: the fingerprint without them, the pool taking
  new settings on a rebind under its spell_id, and the creation cache's generation 22; `ManagedSpellMode` and the
  bind fingerprint's docstrings say the same, and the code-map extents of the changed files are remeasured.
- Docstrings and comments that called a `SpellIndex` a lineage now call it a SpellIndex; "lineage" stays for the
  conduit scope tree (`unique_per_conduit_lineage`, a root and its lesser conduits). Identifiers, diagnostic codes
  and runtime messages are unchanged.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the refusal on the three cleanup calls and its remedies; the code-map extents of `spellbook.py` and
  `spell.py` are remeasured, and their line citations remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe
  spell identity: the spell_id as the SHA256 of the object's code (what counts, installed code named by version, the
  parity across builds and GIL modes, `-O`), the binding manifest and its hash in both cache tiers and the record,
  and the one-object refusals; the packaged test documents describe the new tests; the code-map extents of the
  changed files are remeasured, and the packaged graph's binding profiles and their builder, the examiner's repr
  helpers and the signature reader no longer describe the retired fingerprint. The managed release's failure is
  corrected there:
  `ReleaseManagedSpell().release(obj)` after the root's teardown raises the not-managed ValueError, and the
  torn-down RuntimeError comes from a lease or a release that raced the teardown.
- The examples teach one object, one spell: the lessons and probes in `UX_and_AIX_experiences/` that bound one class
  twice bind a class of their own or a version of it. The glossary defines a Spell ID and says a frame does not
  namespace it; the troubleshooting row, the inspection walkthrough, the configuration guide and the README's "Frame
  Boundaries" section follow, and the configuration guide's disposal sentence is corrected (every declared method
  runs; the failures are raised together).
- The documentation site's intermediate level gains a chapter on managed spell pools
  (`docs/intermediate/managed-spells.md`): binding a managed spell, the three modes and their refusals,
  leasing by meld, injection and `managed_spell_meld`, giving objects back, reset methods, inspecting a
  pool, request scopes and root teardown, and changing settings or moving a pool. Seven runnable
  intermediate lessons back it, one per mode and lifecycle step (42-48 in
  `UX_and_AIX_experiences/02_intermediate/`), with 34 contract probes in
  `UX_and_AIX_experiences/pytest_examples/test_managed_spell_probes.py`; the scopes guide links the chapter
  from its purge table.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the registration of the index `remove_from_spell_index` mints, its removal at the root's teardown and
  residency's parked verdict; the code-map extents of `spellbook.py`, `spell.py` and `mutation_research.py` are
  remeasured, and their line citations remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the teardown's retirement of parked versions and of the indexes only they hold; the `spellbook.py`
  code-map extent is remeasured, and its line citations remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the release of a version from every contract before `cleanup_spell` disposes it, and the packaged test
  documents describe the new tests; the code-map extents of `conduit.py`, `spellbook.py` and `conduit_ward.py` are
  remeasured, and their line citations remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the refused notch - the check inside the notch window, what the reversal puts back, the refusal line
  and the error's `preface`; the code-map extents of the changed files are remeasured, and their line citations
  remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe how destroying an index a parked version left empty keeps every other spell's name, and the
  packaged test documents describe the new tests; the `spellbook.py` code-map extent is remeasured, and its
  line citations remapped.
- The component map documents Spell constructor reflection; the test map records its four signature/spec
  regressions and the current unit-file inventory.
- The component and test maps describe atomic cluster admission and its forced concurrency regressions.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8265.
