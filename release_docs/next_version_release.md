# Melder 0.2.59

**Unreleased**

## `override` replaces `spell_override` on `SpellMap` and `SpellContract`

The construction payload a `SpellMap` or `SpellContract` carries for its provider is now declared with
`override`, the same keyword `meld` uses:

```python
class Consumer:
    def __init__(
        self,
        service: Service = SpellContract(spell=Service, override={"marker": marker}),
    ) -> None:
        self.service = service
```

- **Breaking change: the old keyword is gone.** `SpellContract(..., spell_override=...)` and
  `SpellMap(..., spell_override=...)` raise `TypeError`; rename the keyword to `override`. The
  attribute is `.override` as well, and there is no alias.
- **`meld(override=...)` is unchanged**, and so is precedence: a value supplied at meld wins over the
  descriptor's payload, which wins over the resolved dependency.

## Override payload values reach the provider as the objects you gave

The values inside a `SpellMap` or `SpellContract` `override` payload may be any Python object - an
instance, a callable, a dict, an enum member. Melder never copies them into a compiled plan or into the
creation cache: the plan records a reference to the descriptor and reads the live value when it builds
the provider, so the provider's constructor receives the very object from the descriptor, on the first
meld and on every later run that loads the creation cache.

- **Before, non-scalar values could arrive transformed.** A dict, list, enum, callable or object in
  the payload could reach the provider as its frozen text or tuple form - on most bindings in-process,
  and always after a creation-cache hit. Only `None`, `bool`, `int`, `float` and `str` values, and
  tuples of them, were reliable. All values are now delivered as they are.
- **`SpellMap` payloads are applied.** A `SpellMap(..., override=...)` payload was accepted but never
  reached the provider. It now does, exactly like a `SpellContract` payload.
- **The creation cache never stores your objects.** Cached plans hold scalar payload values and
  references for everything else, so a plan is valid in any process that binds the same book.
- **Existing creation caches keep working.** Cache entries for books whose payload values are all
  scalars are byte-identical; a book with a non-scalar payload value compiles new plans once.

## Overrides build only what you did not supply

An override meld now runs a plan compiled for its set of override keys the first time that set is used.
The plan builds only what the call still needs, so a dependency you supply, and everything that only it
needed, is never constructed.

- **Supplied dependencies are no longer built and discarded.** Before, an override meld built the root's
  whole graph and then swapped your values in, so a supplied dependency's own dependencies were
  constructed anyway, and a supplied shared dependency was built and stored. A supplied dependency that
  is itself missing an input no longer fails the meld.
- **Positional payloads cover injected parameters.** `meld(spell_id=..., override=(obj,))` supplies the
  root's leading parameters even when they are injected dependencies; it used to raise.
- **A path through a list parameter reaches every member**, not only the last one.
- **Empty payloads are ordinary melds.** `override=()` and `override={}` run at normal meld speed.
- **Descriptor payloads behave the same on override melds.** `SpellMap` and `SpellContract` payload
  values reach their providers as the objects you gave, as they do on plain melds.
- **Unchanged:** the key grammar, the errors for unknown keys and their text, the error for a rule on a
  shared object that is already stored, and supplied objects are passed as given, never registered or
  checked.
- **Faster.** On three benchmark graphs override melds ran 22-44% faster, and 4.6 times faster on a
  deep graph with 511 transient sites. Warm override melds with a dict payload now also take the fast
  lane plain melds use. Cold conjure of that deep graph takes about a quarter less time, because override
  executors are no longer compiled at conjure.
- **Creation caches refresh once.** The cache format advances to generation 14; older caches are rebuilt
  on first use.

## Faster warm melds

- **Id melds on an automatic conduit** - `conduit.meld(spell_id=...)` - are served from the warm fast
  lane directly, about 100 ns less per call (free-threaded 3.14, main thread).
- **A bound existing object** is returned by a warm meld without entering its generated creation code,
  about 10-15% faster on free-threaded and GIL builds.

## Faster conjure on large books

Phase 8 of the compiler hashed the whole book's blueprint rows once per root spell, an
O(spells^2) step on the cold conjure path. It now hashes them once per conjure. On a synthetic book of
300 spells, cold conjure took 34% less time; at 29 spells the difference is within measurement noise.

- **No change in what gets compiled.** The analysis is rebuilt exactly when it was before, and creation
  caches are not invalidated.
- **Phase 3 no longer builds a per-spell graph object.** The local frame of every spell (its resolved
  dependencies, ascending by id, then the spell itself) is computed as id rows; the per-spell
  `DirectedAcyclicWorkGraph` that carried the same information, with its lock, node objects and sort, is
  gone. Phase 3 is about a third faster per conjure on the 29-spell benchmark. `Spell.dependency_graph`
  is now always `None` (kept for shape); `Spell.dependencies`, `Spell.resolution_frame` and the
  registered local topology carry the frame. The Phase-4 warning `MISSING_DEPENDENCY_GRAPH` is retired.

## Creation-cache signatures are the same in every process

The signature that identifies a compiled creation plan in the cache rendered some values with Python's
default `repr`, which prints a memory address for functions and for objects that do not define their own
`repr`. A plan carrying such a value in a contract payload therefore got a different signature every
time the program started and never matched its cache. Signatures are now the same across processes for
every value the cache can hold, and one implementation of the signature code serves the whole compiler.

- **Plans whose signatures were already stable keep their bytes.** Existing caches for those books are
  reused unchanged. Books that carry a function or an object with a default `repr` in a payload compile
  new plans once and then hit the cache on every run.

## Typed parameters without a provider are supplied at meld

A constructor parameter whose type nothing registered provides - a `Package`, a `Conduit`, or a
third-party object you never bind - no longer stops `conjure`. It becomes an unresolved input: the
meld that constructs the object supplies it through `override`, and Melder passes that exact object
to the constructor.

```python
class Task:
    def __init__(self, work: Package) -> None:
        self.work = work

book.bind(spell=Task, existence="many")
conduit = book.conjure()  # succeeds
task = conduit.meld(spell=Task, override={"work": package})
assert task.work is package
```

When a meld builds the object without that value, Melder raises `UnresolvedInputError` instead of
Python's missing-argument error. The message names the object, the parameter, the expected type and
the override keys that would supply it:

```text
Task.work expects Package, but nothing registered provides it and this meld did not supply it.
Supply it with override={'work': ...} when melding Task, a path key ending in '>work' (or '**work')
when Task is built as a dependency, or bind a provider for Package.
```

- **Behavior change: conjure no longer fails for a missing provider.** A single typed parameter with
  no matching registration used to raise "no DI candidate found" at conjure. It now surfaces at the
  first meld that builds the object; `conjure(validation_warnings=True)` lists it beforehand (see the
  next section). Two or more matching providers still fail conjure, as before.
- **Matching rules are unchanged.** A parameter annotated with an interface is still not satisfied
  by a provider bound only under its concrete class or under a different spellframe. Such a
  parameter is now an unresolved input rather than a conjure error: bind the provider under that
  spellframe, or supply the value.
- **How to supply it.** Use the parameter name when melding the object itself, and a path key ending
  in `>work` or a `**work` broadcast key when the object is built as a dependency. The value is
  passed by identity; `None` and other falsey values count as supplied.
- **A provider bound later is picked up.** In a dynamic world, binding a matching provider after
  conjure makes the next meld inject it as an ordinary dependency.
- **Stored objects are unaffected.** An object Melder already holds is returned without running its
  constructor again, so it never asks for the value. After `cleanup_spell` removes a provider, objects
  built before that keep the dependency they hold; new builds need the value or a new provider.
- **`UnresolvedInputError` is a `MeldExecutionError`**, so existing handlers keep catching it. Import
  it from `melder`; `param_name`, `expected_type` and `unresolved_params` name what was missing.
- **`resolvable=False` registrations are unchanged.** They remain a separate, discoverable feature.
- **Successful melds do no extra work.** The check runs only after a constructor call has failed.
- **Creation caches rebuild once.** The creation-cache format advances to generation 11 so executors
  compiled before this change are not reused.
- **Defaults and collections are unchanged.** A parameter with a default keeps using it, and a
  `list[...]` collection parameter with no providers still receives `[]`. `Optional[T]` without a
  default is an unresolved input; supplying `None` satisfies it.
- **Every missing input is named.** When several unresolved inputs are left out, the message leads
  with the first and lists the rest; `unresolved_params` holds all of them in signature order.

### Upgrading

- **Checks that relied on conjure to catch a forgotten binding** now pass conjure. Meld the affected
  object once in a smoke test, or conjure with `validation_warnings=True` to list unresolved inputs.
- **Tests asserting the old "no DI candidate found" conjure error** should assert that conjure succeeds
  and that the meld raises `UnresolvedInputError`, or supply the value through `override`.

## Opt-in conjure report of validation warnings

`Spellbook.conjure` takes a new `validation_warnings` keyword. With `validation_warnings=True`, conjure
logs the book's validation warnings once, grouped by kind, at WARNING level through the Spellbook's
logger:

```python
conduit = book.conjure(validation_warnings=True)
```

```text
Conjure validation warnings (3):
  UNRESOLVED_INPUT (1): Task.work -> Package
  REQUIRED_HOLE (2): Counter.count; Loader.source
```

- **Off by default.** A plain `conjure()` logs nothing about warnings. Warnings never stop conjure;
  they flag things that may fail later, such as an unresolved input or a parameter Melder can never
  inject and that has no default (`REQUIRED_HOLE`).
- **Every warning kind is included**, not only unresolved inputs. Each entry names the spell and,
  where one applies, the parameter.
- **Only the conjure you call reports.** Frames created through Nexus, crystallizer restores and
  `upgrade_to_normal` never turn it on.

## Dict, set and tuple constructor parameters no longer break conjure

A constructor parameter typed as a `dict`, `set`, `frozenset` or `tuple` of your own classes - or as
`dict[str, Any]` - made `conjure` fail with `SpellbookValidationError`, although Melder never injects such
a parameter: it injects only single objects and `list[T]` collections. One validation check reported the
parameter as an unsupported collection shape and marked the spell broken, while another reported, for the
same parameter, that the caller must supply it.

```python
class Operations:
    def __init__(self, ops: dict[str, Operation]) -> None:
        self.ops = ops

book.bind(spell=Operations, existence="many")
conduit = book.conjure()  # used to raise; now succeeds
operations = conduit.meld(spell=Operations, override={"ops": {"build": build_op}})
```

- **These parameters are caller inputs.** Supply them through `override` when melding, as for any other
  required parameter Melder does not inject. A plain data class registered as a spell works the same way.
- **The hint moved, it did not disappear.** `conjure(validation_warnings=True)` lists such a parameter as
  `REQUIRED_HOLE`; when the container holds one of your classes, as in `dict[str, Operation]`, the message
  says that Melder injects collections only as `list[T]`. Plain data such as `dict[str, Any]` gets no hint.
- **`Any` is never injected.** `list[Any]`, like `list[int]` or `list[str]`, is plain data you supply; it
  draws no list warning.
- **The `UNSUPPORTED_COLLECTION_SHAPE` validation code is no longer emitted.** Code that looked for it in
  validation results can look for `REQUIRED_HOLE`, which reports these parameters when they have no default.

## Spell ids are the same in every process

A spell's id is a fingerprint of how it was bound. For functions, lambdas, methods, `functools.partial`
objects, callable instances and bound objects that use Python's default `repr`, that fingerprint
included the memory address printed in the `repr` (`<function make_engine at 0x...>`), so the same
spell got a different id every time the program started. Classes whose constructor defaults print an
address, such as `object()` or a `SpellContract` carrying an object, were affected the same way. These
spells now keep one id across processes.

- **Creation caches work for these books.** A book holding such a spell never matched its creation
  cache: every conjure recompiled its creation plans, and the cache file gained one stale entry per
  affected spell on every run. Such books now reach a full cache hit.
- **Affected ids change once.** The first run on this release gives these spells their stable ids.
  Ids that were already stable, including those of ordinary classes, do not change.
- **Identity follows the signature, as it does for classes.** Editing a function's body keeps its id.
  Two objects that differ only by memory address now have the same id, so parking the second as
  another version of the same spell with `bind_inactive` is refused as a spell id collision.
- **Recorded history follows the change.** Crystallizer restore maps each old id to the new one, and
  MutationResearch records the new id as one more version of the spell.
- **Displayed text is unchanged.** Profiles and Nexus descriptions still show the object's `repr`,
  address included; only the fingerprint leaves it out.

## Creation caches stay consistent when a provider changes

Changing a provider's constructor signature changes its spell id. The next conjure rebuilt its plans
in memory but kept the cached plans of the objects that depend on that provider, which still named the
old id. The run after that took the cached path, and the first meld of a dependent object failed with
`RuntimeError: generalized manifest references unknown spell_id '...'` - on every later run, until the
cache file was deleted. Creation caching is on by default, so any book could hit this.

- **A conjure that is not a full cache hit now rewrites the whole cache file** from the plans it just
  compiled, and drops ids that are no longer bound. The file no longer accumulates stale entries.
- **Full cache hits are unchanged.** A conjure that finds every plan cached loads them and leaves the
  file as it is.
- **Creation caches rebuild once.** The creation-cache format advances to generation 12, so caches
  that already hold a stale dependent plan are discarded.

## `TYPE_CHECKING`-only annotations no longer break Melder

Python 3.14 evaluates annotations when something reads them. A class or function whose annotations
name a type imported only under `if TYPE_CHECKING:` - the style Melder's own code uses - made several
Melder features raise `NameError`:

- binding a spell after `conjure` in a dynamic world when it depends on a class annotated this way
  (its first meld failed with a phase error wrapping the `NameError`);
- `Package.describe()` and `Package.signature()`;
- `ProtocolCrafter` on such a class, including Melder's own `Conduit` and `Spellbook`;
- the `"detailed"` `SpellExaminer` profile of a bound spell.

Melder now reads these annotations without evaluating the unavailable names and renders them as
written in the source. A class annotated this way also gets the same spell id in every process;
before, its fingerprint carried a memory address.

- **No change for annotations that resolve.** Rendered signatures match Python's own text whenever
  every name in them can be resolved.
- **Class fields annotated this way now count in the spell id.** A class whose class-level annotations
  named such a type was bound with no annotations at all, so adding or removing one of its annotated
  fields kept the same spell id, and Nexus showed no fields for it. The annotations are now kept, each
  unavailable name as written. These classes get a new spell id once and their creation plans rebuild on
  the next conjure; classes whose annotations all resolve keep their ids.
- **Your own introspection of Melder's API is unchanged.** Calling `inspect.signature` or
  `typing.get_type_hints` with default settings on a Melder class or function that names such a type
  still raises `NameError`. Pass `annotation_format=annotationlib.Format.FORWARDREF` to
  `inspect.signature`; `help()` works as before.

## Concurrent first-time melds no longer deadlock

Two threads that resolved related objects for the first time at the same moment could hang
forever. The typical shape: one thread melds a `unique_per_conduit`, lineage, cluster or
SpellSpace-scoped object that depends on a `unique` service, while another thread melds that
service directly (or purges it). This affected ordinary request-scoped lesser conduits and
constructors that call `meld` themselves, on GIL and free-threaded builds, and it has existed
since at least 0.2.3.

Each object that may exist only once per scope now has its own build lock. Threads that need the
same object still wait for it and receive the one instance; threads building different objects
no longer block each other, and no thread holds a scope's store lock while waiting on another lock.

- **No API change.** Existence semantics, hooks and override behavior are unchanged.
- **Warm melds are unaffected.** Resolving an object that already exists takes no lock, as before.
- **First-time builds of shared objects cost slightly more** (a few percent in micro-benchmarks
  with empty constructors). Multi-threaded workloads can see less contention.
- **Purge waits for an in-flight build** of the same object instead of racing it.
- **Cleaning a scope while another thread is still building into it** now raises `RuntimeError`
  for that build (after running the new object's disposal methods) instead of handing back an
  object the cleanup already disposed. Reusing a SpellSpace or pooled scope while a build is in
  flight lets that build land in the fresh scope.
- **Creation caches rebuild once.** The creation-cache format advances to generation 10 so plans
  compiled with the previous locking are not reused.

## Melding a shared spell while another conduit revalidates it no longer fails

In dynamic worlds a spell shared between conduits (through links, contracts or clusters) has one
compiled plan and one creation context. The first time a conduit melds such a spell, Melder
revalidates it for that conduit and rebuilds the plan. A thread melding the same spell at that
moment could fail with `RuntimeError: Cannot build CreationContext before spell_codegen_creation
exists`, or with an `AttributeError` because the context was cleaned while it was in use. The
failure was intermittent and depended on thread timing.

A rebuild now pauses new melds of that spell, waits for the melds already running to finish,
rebuilds, and then lets them continue with the new plan. Melds of other spells are not affected.

- **No API change.** Revalidation runs exactly as before; only its interaction with running melds
  changes.
- **Warm melds are unaffected.** Measured within noise; automatic worlds take no new path.
- **A meld can wait briefly** while another conduit rebuilds the same spell, typically the first
  meld through a new link, contract or cluster.
- **A failed context build is reported, not waited on.** Threads that were waiting for it raise
  with the original cause instead of waiting forever.
- **No creation-cache rebuild.** Compiled plans are unchanged, so existing caches stay valid.
- **Limitation:** a constructor that melds its own spell through a conduit that must first rebuild
  that spell waits on itself and fails after 30 seconds.

## Clearer errors when conjure refuses spells

When `conjure` refused spells, `SpellbookValidationError` printed every check that had run on them -
warnings included, each followed by a dump of its details - with 64-character spell ids, internal phase
names, and cycles written as ids. Some refusals printed no reason at all. The message now says which spells
failed, why, and what to change, by name:

```text
Spellbook validation failed. Broken spells: Holder.
Holder:
  - Spell 'Holder' (unique) depends on 'Leaf' (unique_per_spell_space), which lives for a shorter scope,
    so 'Holder' would keep a stale 'Leaf' after that scope ends. Give 'Holder' the same or a shorter
    existence (or many), or give 'Leaf' a longer one. [scope_ordering_violation]
```

A cycle between two spells used to take 15 lines: each spell's 64-character id twice, the cycle reported
twice for each spell (once as spell ids, once as binding keys) and a dump of each check's details. It now
reads:

```text
Spellbook validation failed. Broken spells: CycleA, CycleB.
CycleA:
  - Spell 'CycleA' is part of a dependency cycle: 'CycleA' -> 'CycleB' -> 'CycleA'. Melder cannot build
    any spell in the cycle; remove one of these constructor dependencies or give that parameter a default.
    [CIRCULAR_DEPENDENCY]
CycleB:
  - Spell 'CycleB' is part of a dependency cycle: 'CycleB' -> 'CycleA' -> 'CycleB'. Melder cannot build
    any spell in the cycle; remove one of these constructor dependencies or give that parameter a default.
    [CIRCULAR_DEPENDENCY]
```

- **Errors only.** Each broken spell gets one block listing its errors, each with what to change and its
  code in brackets. Warnings never block conjure, so they are only counted, in a closing line such as
  `2 warnings not shown (warnings never block conjure); conjure(validation_warnings=True) logs them.`
- **No more reasonless refusals.** A refusal found while resolving the conduit (scope ordering, a dependency
  the book cannot see, a cycle) used to print "(none recorded)"; its reason is now in the message. Errors
  that belong to no single spell are listed under "Whole-graph errors".
- **Names, not ids.** Cycles read `'CycleA' -> 'CycleB' -> 'CycleA'`, reported once per spell; a
  spell id appears, shortened, only where Melder has no name for it.
- **Internal errors are marked.** Checks of Melder's own bookkeeping are shown as `[internal]`, with a note
  to report them: they are Melder bugs, not problems in your code.
- **Follow-on errors are left out.** `root_not_viable` and `broken_spell_in_dag`, which only say that a
  spell cannot be built because something it depends on is broken, appear only when nothing else explains
  the refusal. A cycle found by two checks is reported by one.
- **Only spells with an error are named.** A refusal that belongs to the whole graph opens with
  `Spellbook validation failed. The dependency graph has errors.` and lists its errors under "Whole-graph
  errors", instead of naming every spell in the book as broken. `broken_spells` is unchanged.
- **Frames are named only when set.** A spell bound under a spellframe is labelled with it, for example
  `Holder (frame 'cache')`; a spell in the default frame shows only its name, where the old text printed
  `frame=None`.
- **Meld reports the same way.** When `meld` refuses a spell, the message has the same layout and carries
  the reason when one was recorded; otherwise it says that the spell's validity is invalid, gated or
  disabled.
- **`*args: Any` and `**kwargs: Any` no longer break a spell.** A constructor accepting anything through
  variadic parameters annotated `Any` was refused as "variadic DI"; `Any` is never injected, so it now
  conjures.
- **Same exception, same data.** `SpellbookValidationError` and its `broken_spells` are unchanged, and it
  gains an optional keyword, `system_diagnostics`. The first line still starts with
  `Spellbook validation failed.` and contains `Broken spells:` whenever it names a spell. Validation codes
  are unchanged; their messages are reworded.
- **Limitation, not changed here:** a constructor that takes its own class fails earlier, in the compiler,
  with `PhaseExecutionError` ("DagNode cannot depend on itself"), so this report cannot explain it yet.

### Upgrading

- **Tests or log filters that matched the old text** - `one or more spells are broken`, `Phase 4 issues`,
  `Phase 6 diagnostics`, `(id=`, `[error] CODE (source=...)` - need updating. Match the code in brackets
  that ends every error line, such as `[scope_ordering_violation]`.

## Automatic creation-cache refresh after a Melder update

Persisted creation caches now record the Melder version that produced them. When a different
release opens an existing cache, Melder treats it as a cache miss and rebuilds the creation plans
through the normal compilation process. This applies to upgrades, downgrades and prerelease changes.

Previously, a package update could reuse an older plan when its binding IDs and cache-format version
still matched. The new release check prevents that reuse automatically.

- **No manual cache deletion is required.** Affected caches rebuild when next used; refreshed caches
  can be reused by subsequent runs of the same Melder release.
- **The first use after an update may take longer** because the creation plans are rebuilt.
- **Legacy caches refresh automatically.** The creation-cache format advances to generation 9;
  caches without the required release stamp are treated as cold. Older generation-8 readers also
  reject the new format when downgrading.
- **Existing compatibility checks remain.** Cache-format and Python interpreter compatibility are
  checked separately from the Melder release.
- **The check runs when loading the cache.** It adds no version polling to ordinary meld calls.

This change affects derived creation-plan caches only. It does not delete Crystallizer checkpoints,
formations or research history, and it does not change their record format. Applications with
creation caching disabled retain their existing behavior.

## Inherited cleanup methods are honored

Class bindings now recognize requested disposal methods inherited from a base class. For example,
`disposal_method_names=["cleanup"]` retains an eligible inherited `cleanup()` method without
requiring the subclass to repeat it. This applies to both per-binding and configured disposal names.

Previously, binding inspected only methods declared directly on the class, so inherited cleanup
could be silently omitted from the disposal list and never run during scope teardown.

- **Python inheritance rules are respected.** Subclass overrides take precedence, and a
  non-callable declaration hides a base method instead of allowing it to be selected.
- **Disposal ordering is preserved.** Book priority, shared-name ordering and deduplication
  retain their existing behavior.
- **Unrelated binding IDs remain stable.** The class profile is unchanged. Bindings whose resolved
  disposal list now includes an inherited method receive an updated fingerprint when rebound.

## Packaging and documentation

- The packaged system documents (`melder.__architecture__`, `__components__`, `__graph_network__` and
  `__graph_details__`) are regenerated and describe unresolved inputs, `UnresolvedInputError`, the
  opt-in conjure warning report, process-stable spell ids, cache generation 12, caller-supplied container
  parameters, the `override` descriptor keyword with live payload values, the single
  codegen-signature implementation, melding a shared spell while another conduit revalidates it, and the
  conjure validation report.
- `UnresolvedInputError` joins the internal-registration guard. Like every Melder exception it can be
  raised and caught, but it cannot be bound as a spell.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.59.
