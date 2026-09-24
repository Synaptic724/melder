# Melder 0.2.51

**Unreleased**

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
