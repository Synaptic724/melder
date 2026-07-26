"""
Internal-bind guard: source scanner and committed-manifest builder.

WHAT IT OWNS
------------
The SINGLE SOURCE OF TRUTH for how the internal registration manifest is
produced. It AST-scans the package for every class melder defines and writes
`manifest/bind_guard_manifest.py`, the committed list `assert_allowed(...)`
enforces through `bind.py`.

Nothing is imported from `melder` during the scan - it is pure AST parsing, so
generation is cycle-free, side-effect free, and runs against a half-built tree.

WHAT IT DOES NOT OWN
--------------------
The `.melc` cache. This builder writes ONE file: the manifest. Hydration and
caching belong to `bind_guard.py` and `_asset_cache`, and the cache is derived
at runtime under `__melder_cache__/__bind_guard__/`. A build step that wrote an
interpreter-specific `marshal` bundle into the source tree would be committing
an artifact only one Python version can read.

LAYOUT
------
    _build_assets/_bind_guard/
        _builder.py                        this file - the tool
        bind_guard.py                      the loader - hand-written
        manifest/
            bind_guard_manifest.py         GENERATED, committed, the truth

    __melder_cache__/__bind_guard__/
        bind_guard.melc                    derived, gitignored, per-interpreter
"""
import ast
import hashlib
import pathlib
from typing import Iterable, List, Set, Tuple


class BindGuardBuildPolicy:
    """
    Static namespace for the manifest generator's fixed policy values.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime; the generator reads
        these to decide what to scan and where to write.

    Attributes:
        EXCLUDED: Classes that must remain BINDABLE by users, as
            `(module_suffix, qualname)` where module_suffix is the dotted path
            BELOW `melder.` - e.g. `("utilities.helpers.id_builder", "IDBuilder")`.
            Starts EMPTY under the owner's blanket-guard ruling and exists as
            the documented seam for future exceptions.
        BUILD_ASSETS_DIR_NAME: Package directory holding durable build assets.
        ASSET_DIR_NAME: This asset's directory.
        MANIFEST_DIR_NAME: Directory holding the committed manifest.
        MANIFEST_FILE_NAME: Generated manifest module filename.
        MANIFEST_VERSION: SCHEMA version of the manifest's shape, deliberately
            separate from the melder release it was built for. BUILT_FOR_VERSION
            moves every release; this moves only when the shape changes - a
            renamed field, a different container. Without the split, a reader
            cannot tell "built by an older melder" (fine, the fingerprint
            decides) from "written in a shape I cannot parse" (fatal).
        SKIP_DIR_NAMES: Directories excluded from the scan. `__melder_cache__`
            is disposable runtime output and `_build_assets` is skipped so the
            generator never records its own scaffolding - including the manifest
            it is about to write - as bindable internals.
    """

    EXCLUDED: Set[Tuple[str, str]] = set()

    BUILD_ASSETS_DIR_NAME: str = "_build_assets"
    ASSET_DIR_NAME: str = "_bind_guard"
    MANIFEST_DIR_NAME: str = "manifest"
    MANIFEST_FILE_NAME: str = "bind_guard_manifest.py"

    # 2.0.0: the manifest is now plain literals consumed by a caching loader.
    # 1.0.0 was a generated loader module beside a COMMITTED `.melc`, which put
    # an interpreter-specific marshal bundle on the import path - not a shape
    # this version can migrate from, hence MAJOR.
    MANIFEST_VERSION: str = "2.0.0"

    SKIP_DIR_NAMES: Set[str] = {
        "__pycache__",
        "__melder_cache__",
        "_build_assets",
    }


def package_root() -> pathlib.Path:
    """
    Return the `melder` package directory.

    Returns:
        pathlib.Path: Directory containing the melder package.
    """
    return pathlib.Path(__file__).resolve().parent.parent.parent


def manifest_path() -> pathlib.Path:
    """
    Return the full path of the committed manifest module.

    Returns:
        pathlib.Path: `<package>/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`.
    """
    return (
        package_root()
        / BindGuardBuildPolicy.BUILD_ASSETS_DIR_NAME
        / BindGuardBuildPolicy.ASSET_DIR_NAME
        / BindGuardBuildPolicy.MANIFEST_DIR_NAME
        / BindGuardBuildPolicy.MANIFEST_FILE_NAME
    )


def source_fingerprint() -> str:
    """
    SHA256 over the scanned source tree, WITHOUT parsing any of it.

    Purpose:
        Make staleness a KEY COMPARISON instead of a rebuild.

    Contract:
        Hashes each scanned file's repo-relative path and raw bytes, in sorted
        order, into one digest. Reading bytes is roughly an order of magnitude
        cheaper than the AST parse + render the previous `--check` performed on
        every invocation, and it is exact: any content change, rename, addition
        or deletion moves the digest.

        Deliberately hashes BYTES, not parsed content - a formatting-only edit
        moves the digest and triggers one regeneration, which is the safe
        direction to be wrong in.

        This gates MANIFEST vs SOURCE and is a BUILD-TIME concern only. Cache
        vs manifest is a different question, answered at runtime by
        `_asset_cache` with a `stat()` rather than a hash, because `hashlib` on
        the import path costs more than the hydration it would protect.

    Returns:
        str: Hex digest of the scanned source tree.
    """
    root = package_root()
    digest = hashlib.sha256()
    for path in _iter_source_files(root):
        digest.update(str(path.relative_to(root)).replace("\\", "/").encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _iter_source_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Yield every scannable Python source file under the package root.

    Args:
        root: The `melder` package directory.

    Returns:
        Iterable[pathlib.Path]: Source files in stable sorted order.
    """
    for path in sorted(root.rglob("*.py")):
        if any(part in BindGuardBuildPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def _module_name_for(path: pathlib.Path, root: pathlib.Path) -> str:
    """
    Derive a file's dotted module name relative to the package root.

    Args:
        path: The source file.
        root: The `melder` package directory.

    Returns:
        str: Dotted module name, always rooted at `melder`.
    """
    parts = list(path.relative_to(root).parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][: -len(".py")]
    return ".".join(["melder", *parts]) if parts else "melder"


def _collect_qualnames(tree: ast.Module) -> List[str]:
    """
    Collect dotted qualnames for every class defined in a module.

    Args:
        tree: Parsed module AST.

    Returns:
        List[str]: Qualnames in source order.
    """
    found: List[str] = []

    def walk(body: Iterable[ast.stmt], prefix: str) -> None:
        for node in body:
            if not isinstance(node, ast.ClassDef):
                continue
            qualname = f"{prefix}{node.name}"
            found.append(qualname)
            walk(node.body, f"{qualname}.")

    walk(tree.body, "")
    return found


def scan_manifest() -> List[Tuple[str, str]]:
    """
    Scan the package and return every internal `(module, qualname)` pair.

    Contract:
        Exact-match keys. The manifest does NOT inherit: listing a base class
        does not enrol its subclasses, which is what retired the MRO-walking
        sentinel this asset replaced.

    Returns:
        List[Tuple[str, str]]: Sorted, de-duplicated manifest entries.
    """
    root = package_root()
    entries: Set[Tuple[str, str]] = set()
    for path in _iter_source_files(root):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        module_name = _module_name_for(path, root)
        suffix = module_name[len("melder.") :] if module_name != "melder" else ""
        for qualname in _collect_qualnames(tree):
            if (suffix, qualname) in BindGuardBuildPolicy.EXCLUDED:
                continue
            entries.add((module_name, qualname))
    return sorted(entries)


def render_manifest(entries: List[Tuple[str, str]], version: str) -> str:
    """
    Render the committed manifest module.

    Purpose:
        Plain Python literals - interpreter-independent, reviewable, diffable.
        When a class enters or leaves the guard that shows up as one added or
        removed line in review, rather than as a changed binary blob.

    Contract:
        PURE and DETERMINISTIC: two calls with the same version over the same
        tree return byte-identical text. `--check` depends on it.

        `ENTRIES` is a TUPLE of tuples, not a frozenset literal. The loader
        builds the frozenset once and caches it, so constructing a set here
        would only duplicate work the cache already removes.

    Args:
        entries: Sorted manifest entries.
        version: The melder version this manifest corresponds to.

    Returns:
        str: Complete manifest module source, newline-terminated.
    """
    lines = [
        '"""',
        "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "The committed truth for melder's internal-bind guard: every class the",
        "package defines, as (module, qualname). `bind.py` enforces this list",
        "through `assert_allowed(...)` and there is NO runtime rebuild lane, so",
        "whatever is committed here IS the enforced policy.",
        "",
        "Consumed by `_build_assets/_bind_guard/bind_guard.py`, which hydrates it",
        "into a frozenset and caches that under __melder_cache__/__bind_guard__/.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '"""',
        "",
        f'MANIFEST_VERSION = "{BindGuardBuildPolicy.MANIFEST_VERSION}"',
        f'BUILT_FOR_VERSION = "{version}"',
        f'SOURCE_SHA256 = "{source_fingerprint()}"',
        f"ENTRY_COUNT = {len(entries)}",
        "",
        "ENTRIES = (",
    ]
    lines.extend(f"    ({module!r}, {qualname!r})," for module, qualname in entries)
    lines.extend([")", ""])
    return "\n".join(lines)


def write_manifest(version: str) -> Tuple[pathlib.Path, int]:
    """
    Scan the package and write the committed manifest atomically.

    Contract:
        Writes exactly ONE file. Temp file then `replace`, so an interrupted
        build never leaves a half-written manifest for `bind.py` to enforce.

    Args:
        version: The melder version to stamp into the manifest.

    Returns:
        Tuple[pathlib.Path, int]: The written path and entry count.
    """
    entries = scan_manifest()
    target = manifest_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(render_manifest(entries, version), encoding="utf-8")
    temporary.replace(target)
    return target, len(entries)


# ---------------------------------------------------------------------------
# BUILDER CONTRACT
#
# `_build_asset_runner.py` discovers this file by convention and requires
# target_path/render/write. They are thin aliases over the descriptive
# functions above, kept separate so the asset-specific vocabulary stays
# readable while the runner sees one uniform surface.
# ---------------------------------------------------------------------------


def target_path() -> pathlib.Path:
    """
    Return the artifact path this builder owns.

    Returns:
        pathlib.Path: The committed manifest module's absolute path.
    """
    return manifest_path()


def manifest_version() -> str:
    """
    Return the SCHEMA version of this manifest's shape.

    Contract:
        Part of the runner's optional contract. Exposed as a callable rather
        than a module constant so the policy class stays the single home for
        the value, per the repo's module scope rule.

    Returns:
        str: The manifest shape version, independent of the melder release.
    """
    return BindGuardBuildPolicy.MANIFEST_VERSION


def render(version: str) -> str:
    """
    Render the artifact text for one melder version.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        str: Complete manifest module source, newline-terminated.
    """
    return render_manifest(scan_manifest(), version)


def write(version: str) -> Tuple[pathlib.Path, int]:
    """
    Write the artifact to disk.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        Tuple[pathlib.Path, int]: The written path and the entry count.
    """
    return write_manifest(version)
