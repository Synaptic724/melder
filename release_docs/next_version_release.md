# Melder 0.2.53

**Unreleased**

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
