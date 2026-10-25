# Melder 0.2.8270

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

## `purge` and the live-creation probes reach a parked version by its spell_id

A notch changes which version of a SpellIndex is active; the version it parks keeps the objects it built, under its
own spell_id. `purge(spell_id=...)`, `has_live_creation(spell=<spell_id>)` and
`describe_live_creation_status(spell=<spell_id>)` found only the active version: for a parked one they raised
`KeyError: '[MELD] No spell found with spell_id: <id>'`, so checking or retiring an old version's objects meant
notching back to it first.

They now answer for the exact version a spell_id names - active or parked, your Spellbook's own or a copy borrowed
from a linked conduit - and purge that version's objects from the same store, under the same rules, as an active
version's:

```python
class Report:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


book = md.Spellbook()
v1 = book.bind(spell=Report, existence="unique", disposal_method_names=["close"])
root = book.conjure(dynamic=True)
first = root.meld(spell_id=v1)


class Report:                                     # version 2: the same name, new code
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def render(self) -> str:
        return "v2"


index = root.get_spell_by_spell_id(v1).spell_index
v2 = root.bind_inactive(spell=Report, spell_index=index, existence="unique", disposal_method_names=["close"])
root.notch_spell(spell_index=index, spell_id=v2)  # version 1 is parked; its object is kept
second = root.meld(spell_id=v2)

assert root.has_live_creation(spell=v1)           # raised KeyError before
assert root.purge(spell_id=v1) == 1               # raised KeyError before
assert first.closed and not second.closed         # only version 1's object was disposed
root.meld(spell_id=v1)                            # still KeyError: meld builds the active version only
```

Every other selector is unchanged: a name, a class, a spellframe and binding name, or an object passed to `purge`
names the version the index has active, as `meld` does - to retire a parked version's objects, pass its spell_id
(with the default `purge_all=True`). Who may purge which store is unchanged too: a `unique` version from its owner
root, a `unique_per_conduit_lineage` version from the lineage root, a `unique_per_conduit_cluster` version from the
elected leader, a `many` or `unique_per_conduit` version from the conduit that holds it, a `unique_per_spell_space`
version only through its spell space; a managed spell's purge still returns 0, and its probe reads that version's
own pool.

**Breaking change:** code that caught this `KeyError` to tell a parked version from the active one now gets an
answer. To ask whether a spell_id is the active version, compare it with the index's:
`conduit.get_spell_by_index_id(conduit.get_spell_by_spell_id(spell_id).spell_index.id).spell_id == spell_id`. A
spell_id no version of the conduit carries - unknown, disposed, or another Spellbook's and not borrowed - still
raises the same `KeyError`, and `meld(spell_id=...)` still raises it for a parked version.

Also fixed: purging a `unique` version whose owner stamp failed when its Spellbook was conjured (the conjure logs that
failure) raised `AttributeError: 'NoneType' object has no attribute 'owner_conduit_id'`. It now raises a
`RuntimeError` that names the version and the remedy: dispose it with `cleanup_spell` and bind it again.

What stays the same: every signature; `meld`, `meld_existing_spell`, `managed_spell_meld` and `SpellSpace.meld` build
or return only the active version; a probe or purge of an active version reads what it read before; cache files and
saved records are unchanged.

## Codegen rooms under the safe, hybrid and precision profiles refuse `open`

Code an agent runs in a codegen room is checked against the codegen profile of the frame it names before it runs.
Through 0.2.8269 no profile stopped the `open` builtin, so room code under every profile read and wrote any file the
process could reach - under `safe` too, whose posture says it denies writes - and `hybrid` also admitted
`import pathlib`, whose `Path.write_text` writes files.

**Breaking change:** under the `safe`, `hybrid` and `precision` profiles - `precision` on its own or as the overlay
on another profile - room code that calls `open` is refused at validation, and nothing runs:

```python
# command_system: the command surface of a codegen room (rift.space.command_system) whose Rift is linked to the
# frame "ops", and the codegen profile of "ops" is safe.
result = command_system.execute_codegen("handle = open('notes.txt', 'w')\nhandle.write('x')", frame_name="ops")
result["accepted"]              # False: nothing is written
result["validation_issues"][0]  # "Builtin 'open' is not allowed in this codegen mode."
```

Code that only names it (`reader = open`) is refused with "Name 'open' is not available in the codegen namespace.",
and `open` is no longer among the room's runtime builtins. A request naming a frame the room holds no codegen
projection for runs under the safe posture, which denies `open` as well. Under `hybrid`, `import pathlib` is refused
with "Import root 'pathlib' is not allowed in this codegen mode.": `pathlib`, like `io` and `os`, is now on the
`permissive` import list only. Room code that must read or write files runs under the `permissive` or `full_access`
profile, whose file posture stays open by design.

What stays the same: `permissive` and `full_access` keep `open`, `io`, `os` and `pathlib`; every other builtin and
import root of each profile is unchanged; a `builtin_names` allow rule in a frame's codegen capability override still
allows `open` for that frame; and nothing cached or recorded changes. These checks run in the room's own process:
they are policy and defence in depth, not isolation.

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
- The internal `Creations` store's docstrings (`ManyDisposalBucket`, `add_many_creations`, `register_many`) no
  longer say that a spell_id covers a `many` spell's disposal names - it has not since 0.2.8257, when the spell_id
  became the SHA256 of the object's code - and say what the store does after `cleanup_spell` and a new `bind` of the
  same class while a scope still holds the objects of the removed binding: bound again as a `many` with other
  disposal names, the new objects join the removed binding's disposal record and are disposed with its names; bound
  again as a `many` after a `unique` or `unique_per_conduit` binding, the next meld in that scope raises
  `AttributeError` and returns nothing. Both are known and not fixed here; behaviour is unchanged. The packaged
  system documents (`melder.__components__`, `melder.__architecture__`) and the packaged graph say the same, and
  the code-map extent and line citations of `creations.py` are remeasured.
- Releases on PyPI, and release candidates on TestPyPI, are published by Trusted Publishing: each upload
  authenticates with its workflow's own short-lived identity, with no stored API token, and uploads a PEP 740
  attestation for each file. After each upload the workflow checks every uploaded file's provenance on its
  index - its publisher, its Sigstore signature, the repository, workflow, commit and run that signed it, and
  the file's sha256 - and the release candidate does so before its installation tests use the files. The
  installation guide (`docs/beginner/install.md`) shows how to check a downloaded file with
  `pypi-attestations`, and the README links to it; the guide no longer says Melder has no runtime dependencies
  (it declares pip).
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph say what
  a spell_id reaches through `purge` and the live-creation probes - a parked version or a borrowed copy - and that
  purge refuses a `unique` version with no owner store; the scopes guide (`docs/intermediate/scopes.md`), the
  live-probe section of `docs/intermediate/overrides.md` and the governed-change guide
  (`docs/expert/governed-change.md`) say the same, and the packaged test documents describe the new tests. The
  code-map extents of the six changed files are remeasured, and line citations into `spellbook.py`, `meld.py` and
  `conduit.py` remapped.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe
  each codegen profile's file posture - `open` on the deny list `safe`, `hybrid` and `precision` share, `io`, `os` and
  `pathlib` on the `permissive` import list only, and the safe posture of a request naming a frame with no codegen
  projection - and the packaged test documents describe the new tests; each profile's docstring states its file
  posture. The code-map extent of `codegen_system.py` is remeasured, and line citations into it remapped.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8270.
