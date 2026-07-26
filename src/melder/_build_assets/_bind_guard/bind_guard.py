"""
Internal-bind guard manifest: the class list `assert_allowed(...)` enforces.

WHAT THIS IS
------------
`bind.py` imports `INTERNAL_MANIFEST` at module scope and there is no runtime
rebuild lane, so whatever this resolves to IS the enforced registration policy.
That is why the truth lives in a COMMITTED manifest
(`manifest/bind_guard_manifest.py`) and the `.melc` under `__melder_cache__` is
only ever an accelerator - see `_asset_cache` for why the cache must never be
the source.

WHY THIS MODULE IS HAND-WRITTEN
-------------------------------
Only the manifest is generated. This loader is ordinary reviewed code, which
means it can carry real annotations instead of shipping a `.pyi` alongside a
generated typeless module. PEP 585 builtin generics (`frozenset[tuple[str, str]]`)
annotate it fully with NO `typing` import - measured at 2.88 ms on a cold
interpreter, more than the hydration this whole lane exists to make fast.

IMPORT COST
-----------
`os` only, plus the cache helper. The manifest module is imported lazily inside
`_build_payload`, so a warm process never parses it.
"""
import os

from melder.utilities.caching_system.asset_cache import hydrate


class BindGuardAsset:
    """
    Static namespace for this asset's fixed identity.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        ASSET_NAME: Bare asset name; drives the cache path
            `__melder_cache__/__bind_guard__/bind_guard.melc`.
        MANIFEST_DIR_NAME: Directory holding the committed manifest.
        MANIFEST_MODULE_NAME: Generated manifest module filename.
    """

    ASSET_NAME: str = "bind_guard"
    MANIFEST_DIR_NAME: str = "manifest"
    MANIFEST_MODULE_NAME: str = "bind_guard_manifest.py"


def manifest_file() -> str:
    """
    Return the absolute path of the committed manifest module.

    Returns:
        str: Path to `manifest/bind_guard_manifest.py`.
    """
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        BindGuardAsset.MANIFEST_DIR_NAME,
        BindGuardAsset.MANIFEST_MODULE_NAME,
    )


def _build_payload() -> dict:
    """
    Build the cacheable payload by importing the committed manifest.

    Contract:
        Called ONLY on a cache miss. The import is deliberately inside the
        function: at module scope it would run on every process start and the
        cache would save nothing.

        Metadata travels INSIDE the payload rather than being read from the
        manifest module by the loader, so that a cache hit never has to touch
        the manifest for anything.

    Returns:
        dict: `entries`, `manifest_version`, `built_for_version`, `entry_count`.
    """
    from melder._build_assets._bind_guard.manifest import bind_guard_manifest as source

    return {
        "entries": frozenset(source.ENTRIES),
        "manifest_version": source.MANIFEST_VERSION,
        "built_for_version": source.BUILT_FOR_VERSION,
        "entry_count": len(source.ENTRIES),
    }


_PAYLOAD: dict = hydrate(BindGuardAsset.ASSET_NAME, manifest_file(), _build_payload)

INTERNAL_MANIFEST: frozenset[tuple[str, str]] = _PAYLOAD["entries"]
MANIFEST_VERSION: str = _PAYLOAD["manifest_version"]
BUILT_FOR_VERSION: str = _PAYLOAD["built_for_version"]
MANIFEST_ENTRY_COUNT: int = _PAYLOAD["entry_count"]
