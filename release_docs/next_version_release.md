# Melder 0.2.54

**Unreleased**

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
  `__graph_details__`) are regenerated and describe unresolved inputs, `UnresolvedInputError` and the
  opt-in conjure warning report.
- `UnresolvedInputError` joins the internal-registration guard. Like every Melder exception it can be
  raised and caught, but it cannot be bound as a spell.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.54.
