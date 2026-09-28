"""
Agent-facing class documentation harvested from docstrings at build time.

WHAT THIS IS
------------
`AGENT_ACCESS:` / `AGENT_PURPOSE:` sections are authored in class docstrings and
harvested into a COMMITTED manifest (`manifest/agent_documentation_manifest.py`)
so the classes themselves stop carrying the facts. The `.melc` under
`__melder_cache__` is only an accelerator - see `_asset_cache` for why the cache
must never be the source.

`-OO` is irrelevant here: it strips docstrings from BYTECODE, never from source,
and the harvest reads source text at build time. Consumers see ordinary string
data.

THE THREE STATES
----------------
    AGENT_METADATA   marked   - access + purpose resolved
    EXEMPT           ruled out deliberately (e.g. the spell_compiler subtree)
    PENDING          not done yet; fill in over time

Keeping `PENDING` distinct is the point of the asset: without it, "deliberately
excluded" and "nobody has got to it" look identical to every tool and every
future agent.

CLASS_BASES IS DIAGNOSTIC ONLY
-----------------------------
It records DIRECT bases, which drops grandparents. Inheritance resolves through
`inspect.getmro` at runtime; this is here for build-time reporting, not lookup.

WHY THIS MODULE IS HAND-WRITTEN
-------------------------------
Only the manifest is generated. This loader is ordinary reviewed code, so it
carries real annotations via PEP 585 builtin generics instead of shipping a
`.pyi` beside a generated typeless module - and with no `typing` import, which
costs 2.88 ms cold.

PAID ONCE, NEVER AGAIN
----------------------
Hydration happens at module import and the result is bound to module globals,
so `sys.modules` makes every later importer free. It does not matter how many
call sites reach for `AGENT_METADATA` - the cost is one hydration per process,
identical in shape and in timing to the sibling `bind_guard` asset.
"""
import os

from melder.utilities.caching_system.asset_cache import hydrate


class AgentDocumentationAsset:
    """
    Static namespace for this asset's fixed identity.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        ASSET_NAME: Bare asset name; drives the cache path
            `__melder_cache__/__agent_documentation__/agent_documentation.melc`.
        MANIFEST_DIR_NAME: Directory holding the committed manifest.
        MANIFEST_MODULE_NAME: Generated manifest module filename.
    """

    ASSET_NAME: str = "agent_documentation"
    MANIFEST_DIR_NAME: str = "manifest"
    MANIFEST_MODULE_NAME: str = "agent_documentation_manifest.py"


def manifest_file() -> str:
    """
    Return the absolute path of the committed manifest module.

    Returns:
        str: Path to `manifest/agent_documentation_manifest.py`.
    """
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        AgentDocumentationAsset.MANIFEST_DIR_NAME,
        AgentDocumentationAsset.MANIFEST_MODULE_NAME,
    )


def _build_payload() -> dict:
    """
    Build the cacheable payload by importing the committed manifest.

    Contract:
        Called ONLY on a cache miss. The import is deliberately inside the
        function: at module scope it would run on every process start and the
        cache would save nothing.

        ONE dict holds every collection, so a cache hit is a single
        `marshal.loads` rather than four separate structure builds.

    Returns:
        dict: `agent_metadata`, `exempt`, `pending`, `class_bases` plus the
            stamped manifest metadata and entry counts.
    """
    from melder._build_assets._agent_documentation.manifest import (
        agent_documentation_manifest as source,
    )

    return {
        "agent_metadata": dict(source.AGENT_METADATA),
        "exempt": frozenset(source.EXEMPT),
        "pending": frozenset(source.PENDING),
        "class_bases": dict(source.CLASS_BASES),
        "manifest_version": source.MANIFEST_VERSION,
        "built_for_version": source.BUILT_FOR_VERSION,
        "marked_count": source.MARKED_COUNT,
        "exempt_count": source.EXEMPT_COUNT,
        "pending_count": source.PENDING_COUNT,
    }


_PAYLOAD: dict = hydrate(
    AgentDocumentationAsset.ASSET_NAME, manifest_file(), _build_payload
)

AGENT_METADATA: dict[tuple[str, str], tuple[str, str]] = _PAYLOAD["agent_metadata"]
EXEMPT: frozenset[tuple[str, str]] = _PAYLOAD["exempt"]
PENDING: frozenset[tuple[str, str]] = _PAYLOAD["pending"]
CLASS_BASES: dict[tuple[str, str], tuple[str, ...]] = _PAYLOAD["class_bases"]
MANIFEST_VERSION: str = _PAYLOAD["manifest_version"]
BUILT_FOR_VERSION: str = _PAYLOAD["built_for_version"]
MARKED_COUNT: int = _PAYLOAD["marked_count"]
EXEMPT_COUNT: int = _PAYLOAD["exempt_count"]
PENDING_COUNT: int = _PAYLOAD["pending_count"]
