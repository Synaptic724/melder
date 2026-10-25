# Melder 0.2.8267

**Unreleased**

## A cache file that cannot be saved no longer fails a meld

Melder keeps each root conduit's compiled creation plans in a cache file (`<conduit>.meldercache`, in the package's
`__melder_cache__` folder) so a later conjure can skip compilation. A meld that staged new plans - the first meld of
a spell compiled at that meld, such as one bound after `conjure` - saved the file before it returned, and a save the
operating system refused was raised from the meld after its object had been built: on Windows `PermissionError:
[WinError 5] Access is denied` while another program held the file open (a real-time virus scanner or an indexer,
for example), on any platform for a read-only cache folder or a full disk. A `unique` built that way came back from
the next meld, but a `many` was lost to its caller, a managed lease never went back to its pool, and while the
refusal lasted every meld of the Spellbook raised.

The cache file is now best-effort, as a missing or unreadable one already was (it only makes the cache cold):

- A save the operating system refuses raises nothing. The meld returns its object, the cache stays in memory for
  the next save, and the refusal is logged once per cache file at WARNING - later refusals of that file at DEBUG:

```text
Could not save the creation-cache bundle '.../__melder_cache__/__conjure_cache__/<frame>/<conduit>.meldercache':
[WinError 5] Access is denied: ... Melds are not affected and the cache stays in memory for the next save. To
persist it, make the cache folder writable (on Windows, also exclude it from real-time scanning), or turn caching
off for the frame with with_system_caching_enabled(False). Later refused saves of this bundle log at DEBUG.
```

- On Windows a refused rename of the file is retried for about 100 ms before the save counts as refused.
- Each process and thread writes a temp file of its own (`<conduit>.meldercache.<pid>.<thread id>.tmp`) and a
  failed save removes it, so no `<conduit>.meldercache.tmp` is left behind, and two processes that share a frame
  and conduit name never write into one temp file.

**Breaking change:** `Spell.emit_cache_file()` returns `False` when the operating system refuses the save (the
refusal is logged), where it raised the `OSError`. `True` still means the file was written, and `False` also means
caching is off for the spell or nothing was staged since the last save; code that caught `OSError` around the call
can check the result instead.

What stays the same: the cache file's format and generation (23), when and where Melder saves it, and every other
public signature. A save that fails for any reason other than an operating-system error still raises.

## A `many` dependency belongs to the scope that built it, not to the object that holds it

**Breaking change:** a `many` dependency with disposal methods is now always recorded and disposed by the scope that
built it - the spell space, else the conduit that melded - also when it is built for a longer-lived object (a
`unique`, `unique_per_conduit`, `unique_per_spell_space`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster`
spell). Cleaning up that object - purging it, or the end of the creations that hold it - runs only the object's own
disposal methods; what it does with the objects it holds is up to those methods. From 0.2.8235 to 0.2.8265 such a
dependency belonged to the object that held it: it was recorded with the object's owner, disposed right after the
object when the object was purged, and moved with the object to another root. That is removed on the owner's
decision, so Melder behaves like Autofac: an object is disposed by the scope that built it, and cleaning up one
object never cleans up the objects it was given.

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

assert repository.connection.closed              # the request scope closed the connection it built
assert root.meld("Repository") is repository     # the root still serves the same repository
```

The calls are the same as in 0.2.8235-0.2.8265; only Melder's answer differs: those releases left the connection
open here and closed it when the root ended. The repository now holds a closed connection because the scope that
built the connection has ended - what Autofac does when a singleton keeps a dependency from a shorter scope. To keep
the connection as long as the repository, meld the repository first where it lives (`root.meld("Repository")`), so
the root builds the connection and closes it when the root ends; or bind `Connection` without disposal methods and
close it in the repository's own disposal method.

Purge, the live-creation probes and transfers follow the same rule:

- Purging the object disposes the object alone. Its `many` dependencies are disposed when their scope ends, and
  their disposal failures are raised there (0.2.8238-0.2.8265 disposed them right after the object and raised their
  failures with its own).
- `purge` and `has_live_creation` for the dependency's `many` spell count every instance its scope recorded, also
  one a live object still holds (they skipped those).
- `transfer_spell_ownership(..., move_creations=True)` moves the object, not its `many` dependencies, which stay
  with the scope that built them (0.2.8238-0.2.8265 moved them with it); with `include_dependencies=True` the
  dependency's spell moves too, and its objects with it.

What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are recorded
with the scope that melds them, as before; a `many` dependency without disposal methods is not recorded at all;
managed pools (`Existence.managed_spell_quantity`) keep the `many` dependencies of their objects with each object;
warm melds run exactly the code they ran before, and cache files and saved records are unchanged.

With `generalized_singleton_specialization_enabled` (opt-in, off by default), a root whose graph passes a `many`
dependency to a longer-lived object is still not specialized: the specialized path would build a new dependency on
every warm meld, which the stored object never uses.

## Packaging and documentation

- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe
  the best-effort cache save - the result of a refused save, the per-writer temp file, the Windows rename retry and
  the one WARNING per cache file - and `Spell.emit_cache_file()`'s `False`; the code-map extents of
  `caching_system.py`, `spellbook.py` and `spell.py` are remeasured, and their line citations remapped.
- Melder declares one runtime dependency, `pip==26.2.2`, so installing Melder installs that pip release; the
  package description and the README say so (both said "Zero dependencies"). The documentation build pins it in
  `docs/requirements.lock`, and CI's installed-package checks - the wheel check after every build and the release
  candidate's install from TestPyPI on every supported Python release - install the wheel beside it and confirm
  with `pip check` that the installed set satisfies the wheel's requirements.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe a
  `many` dependency belonging to the scope that built it: one registration rule in the compiled plans, a holder's
  cleanup running only its own disposal, what purge, the live-creation probe and a transfer do with the dependency,
  and the specializer's decline kept; the removed holder record is marked as removed. The scopes guide
  (`docs/intermediate/scopes.md`) and the ownership guide (`docs/intermediate/ownership.md`) say a `many` dependency
  belongs to the conduit or spell space that built it and stays there through a transfer, and the packaged test
  documents describe the new tests; the code-map extents of the changed files are remeasured, and line citations
  into `conduit.py` and `creations.py` remapped.
- The internal-bind guard manifest holds 629 entries at 0.2.8267 (630 at 0.2.8257): `HolderDisposalEntry`, the record
  that kept a slotted object's `many` children with it (0.2.8238), left.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8267.
