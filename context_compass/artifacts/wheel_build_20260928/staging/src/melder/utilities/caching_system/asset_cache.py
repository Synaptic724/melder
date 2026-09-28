"""
Shared hydration lane for durable build assets: committed manifest -> hot cache.

WHY IT LIVES HERE AND NOT IN `_build_assets/`
---------------------------------------------
This is RUNTIME code. It runs on every `import melder`, and it has nothing to
do with building anything - it only ever READS a manifest and manages a cache
beside it. `_build_assets/` holds the generators (`_builder.py`, the runner):
tools that run at build time, on a developer's machine or in CI, and that never
execute in a user's process. Putting a hot-path loader in that folder made the
directory mean two unrelated things.

It sits beside `caching_system.py` because that is where melder's cache
machinery lives, and the two are deliberately different scopes of the same
idea: `CachingSystem` is a per-conduit instance cache with a lock, a logger and
a lifecycle; this is a process-lifetime, read-mostly bundle for build assets.
Both write `.melc` under `__melder_cache__`, both stamp
`sys.implementation.cache_tag`, and both treat a bad bundle as a cold cache.

Importing this module does NOT pull in `caching_system.py` - there is no
`__init__.py` in this directory (PEP 420 namespace package), so the sibling
stays unloaded and the boot path stays clean.

THE TWO-ARTIFACT MODEL
----------------------
Every build asset has exactly two on-disk forms, and confusing them is the
mistake this module exists to prevent:

    MANIFEST   `_build_assets/<asset>/manifest/<asset>_manifest.py`
               COMMITTED. Plain Python literals. Interpreter-independent,
               diffable in review, and the thing `--check` gates on. This is
               the TRUTH.

    CACHE      `__melder_cache__/__<asset>__/<asset>.melc`
               DERIVED and GITIGNORED. One marshal bundle, rebuilt on demand.
               This is SPEED, and nothing else.

WHY THE CACHE CANNOT BE THE TRUTH
---------------------------------
`marshal` is explicitly interpreter-specific - the format carries no
compatibility guarantee across Python versions, which is why `CachingSystem`
stamps `sys.implementation.cache_tag` into every bundle it writes. This repo
runs 3.10 today and targets 3.14t free-threaded, so a committed `.melc` would
be a blob written by one interpreter and handed to another. Committing one puts
an interpreter-specific artifact on the critical import path of a package that
deliberately supports two interpreters.

Keeping the manifest as source and the `.melc` as cache also means a clone,
a wheel, and a read-only install all work identically: worst case they miss the
cache and pay the manifest import once.

INTEGRITY IS REGENERATION-BASED
-------------------------------
Copied deliberately from `CachingSystem`: a bundle that is corrupt, written by
another interpreter, or built from a different manifest is treated as a COLD
CACHE, never as an error and never repaired in place. There is no failure mode
here that should reach a caller - the manifest can always answer.

STALENESS IS (size, mtime_ns), NOT A HASH
-----------------------------------------
The cache stamps the manifest file's size and mtime and compares both on load.
This is exactly CPython's own default `.pyc` invalidation strategy, and it is
chosen over SHA256 for a specific reason: hashing means `import hashlib` on the
boot path, which costs more than the structure build the cache exists to avoid.
Two `stat()` fields cost microseconds.

The failure direction is safe. A fresh checkout rewrites mtime, so the cache
invalidates and rebuilds - a wasted rebuild, never a stale read. The inverse
(same size AND same nanosecond mtime with different content) is not reachable
by any real edit, and CI gates manifest-vs-source separately through
`_build_asset_runner.py --check`.

IMPORT COST
-----------
`marshal`, `os` and `sys` only. All three are already resident before any
melder code runs, so this module adds nothing measurable to boot. `pathlib`
(3.77 ms) and `typing` (2.88 ms) are deliberately absent - both were measured
costing more than the hydration they were meant to describe.
"""
import marshal
import os
import sys


class AssetCachePolicy:
    """
    Static namespace for the asset cache's fixed values.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        CACHE_VERSION_HISTORY: Every bundle layout this loader has written,
            newest last. Mirrors `CachingSystem.CACHE_VERSION_HISTORY`: the
            history is kept rather than a bare number so that when a bundle is
            rejected, WHY it was rejected is documented next to the version
            that caused it.
        CURRENT_VERSION: The layout written today; anything else is cold.
        BUNDLE_SUFFIX: Cache bundle extension, matching `CachingSystem`.
        CACHE_ROOT_DIR_NAME: Package-level cache root shared with the conjure
            and crystallizer caches.
        PACKAGE_ROOT: Absolute path of the `melder` package. Resolved once at
            import from this file's own location - this module sits at
            `melder/utilities/caching_system/asset_cache.py`, so the package
            root is three directories up. Computed here rather than at each
            call so the walk happens once per process.
    """

    # Version 1: `{version, python, manifest_size, manifest_mtime_ns, payload}`
    # where `payload` is whatever the owning asset marshalled. No earlier
    # layouts exist; the pre-history form was a COMMITTED `.melc` beside the
    # loader with no interpreter tag at all, which is precisely the arrangement
    # this module replaces rather than a version it can migrate from.
    CACHE_VERSION_HISTORY = {1: "manifest_stat_gated_payload"}
    CURRENT_VERSION = max(CACHE_VERSION_HISTORY)

    BUNDLE_SUFFIX = ".melc"
    CACHE_ROOT_DIR_NAME = "__melder_cache__"

    # melder/utilities/caching_system/asset_cache.py -> melder/
    PACKAGE_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def cache_path_for(asset_name):
    """
    Return the cache bundle path for one asset.

    Contract:
        `<package>/__melder_cache__/__<asset>__/<asset>.melc` - the same
        `<root>/<scope>/<name>.melc` shape `CachingSystem` uses for conduits,
        so every cache in the tree is discoverable by one mental model.

    Args:
        asset_name: Bare asset name, e.g. `bind_guard`.

    Returns:
        str: Absolute path to the cache bundle.
    """
    return os.path.join(
        AssetCachePolicy.PACKAGE_ROOT,
        AssetCachePolicy.CACHE_ROOT_DIR_NAME,
        f"__{asset_name}__",
        f"{asset_name}{AssetCachePolicy.BUNDLE_SUFFIX}",
    )


def hydrate(asset_name, manifest_file, build_payload):
    """
    Return an asset's payload from cache, rebuilding from the manifest on a miss.

    Purpose:
        The single entry point every generated loader calls. Callers get a
        payload and never learn whether it came from the cache.

    Contract:
        - Reads the cache and returns its payload when the bundle is intact, was
          written by THIS interpreter, matches `CURRENT_VERSION`, and was built
          from a manifest with the same `(size, mtime_ns)`.
        - Otherwise calls `build_payload()` and writes a fresh bundle.
        - NEVER raises for cache reasons. Every failure - missing, truncated,
          foreign interpreter, unreadable directory - degrades to the manifest,
          because the manifest can always answer and an import-time raise here
          would take the whole package down for a performance optimisation.
        - The write is best-effort and atomic (temp file then `os.replace`). A
          read-only install (site-packages, container layer, multi-user box)
          silently keeps the in-memory payload; correctness never depends on
          the filesystem being writable.

    Args:
        asset_name: Bare asset name, e.g. `bind_guard`.
        manifest_file: Absolute path to the committed manifest module.
        build_payload: Zero-arg callable returning the marshal-safe payload.
            Called ONLY on a cache miss, so the manifest import it performs
            stays off the warm path.

    Returns:
        object: The asset payload.
    """
    bundle_path = cache_path_for(asset_name)
    try:
        stamp = os.stat(manifest_file)
    except OSError:
        # No manifest on disk: nothing can validate a cache against it, so the
        # only honest move is to let the caller's builder speak.
        return build_payload()

    try:
        bundle = marshal.loads(open(bundle_path, "rb").read())
        if (
            bundle["version"] == AssetCachePolicy.CURRENT_VERSION
            and bundle["python"] == sys.implementation.cache_tag
            and bundle["manifest_size"] == stamp.st_size
            and bundle["manifest_mtime_ns"] == stamp.st_mtime_ns
        ):
            return bundle["payload"]
    except Exception:
        # Regeneration-based integrity, as CachingSystem does: a bad bundle is
        # a cold cache. Nothing is logged - this runs before melder's logging
        # exists, and a cache miss is not an event worth reporting.
        pass

    payload = build_payload()
    _write_bundle(bundle_path, stamp, payload)
    return payload


def _write_bundle(bundle_path, stamp, payload):
    """
    Persist one cache bundle atomically, best-effort.

    Contract:
        Temp file then `os.replace`, so a crash or a concurrent interpreter
        mid-write never leaves a torn bundle for the next process to read. The
        temp name carries the pid, so two processes racing a cold cache write
        to distinct temp files and the last `replace` wins - both wrote
        identical bytes, so the race has no observable outcome.

        Every `OSError` is swallowed. Failing to cache is not failing.

    Args:
        bundle_path: Absolute destination path.
        stamp: `os.stat_result` for the manifest this payload was built from.
        payload: The marshal-safe payload to store.

    Returns:
        None
    """
    temporary = f"{bundle_path}.{os.getpid()}.tmp"
    try:
        os.makedirs(os.path.dirname(bundle_path), exist_ok=True)
        with open(temporary, "wb") as handle:
            handle.write(marshal.dumps({
                "version": AssetCachePolicy.CURRENT_VERSION,
                "python": sys.implementation.cache_tag,
                "manifest_size": stamp.st_size,
                "manifest_mtime_ns": stamp.st_mtime_ns,
                "payload": payload,
            }))
        os.replace(temporary, bundle_path)
    except OSError:
        try:
            os.unlink(temporary)
        except OSError:
            pass
