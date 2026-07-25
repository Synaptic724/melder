"""
Internal-bind manifest scanner and durable asset builder.

This module is the SINGLE SOURCE OF TRUTH for how the internal registration manifest is produced.
It lives inside `src/melder/_build_assets/_init_manifest/` as a durable package asset builder.

Consumers:
  * `build_scripts/build_internal_manifest.py` - CLI generation script and CI staleness gate.
  * `melder.aether.spellbook.bind.bind` - imports `INTERNAL_MANIFEST` from
    `internal_manifest.py` and enforces it through `assert_allowed(...)`.

The scan uses pure AST parsing: nothing is imported from `melder`, so it is cycle-safe and free of side effects.
"""
import ast
import pathlib
from typing import Iterable, List, Set, Tuple


class ManifestBuildPolicy:
    """
    Static namespace for the manifest generator's fixed policy values.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime; the generator reads these
        to decide what to scan and where to write.

    Attributes:
        EXCLUDED: Classes that must remain BINDABLE by users, as
            `(module_suffix, qualname)` where module_suffix is the dotted path
            BELOW `melder.` - e.g. `("utilities.helpers.id_builder", "IDBuilder")`.
            Starts EMPTY under the owner's blanket-guard ruling and exists as the
            documented seam for future exceptions.
        BUILD_ASSETS_DIR_NAME: Package directory holding durable build assets.
        INIT_MANIFEST_DIR_NAME: Package directory holding the manifest asset.
        MANIFEST_FILE_NAME: Generated manifest module filename.
        SKIP_DIR_NAMES: Directories excluded from the scan. `__melder_cache__` is
            disposable runtime output, and the asset directories are skipped so
            the generator never records its own scaffolding as bindable internals.
    """

    EXCLUDED: Set[Tuple[str, str]] = set()

    BUILD_ASSETS_DIR_NAME: str = "_build_assets"
    INIT_MANIFEST_DIR_NAME: str = "_init_manifest"
    MANIFEST_FILE_NAME: str = "internal_manifest.py"

    SKIP_DIR_NAMES: Set[str] = {
        "__pycache__",
        "__melder_cache__",
        "_build_assets",
        "_init_manifest",
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
    Return the full path of the durable manifest module.

    Returns:
        pathlib.Path: `<package>/_build_assets/_init_manifest/internal_manifest.py`.
    """
    return (
        package_root()
        / ManifestBuildPolicy.BUILD_ASSETS_DIR_NAME
        / ManifestBuildPolicy.INIT_MANIFEST_DIR_NAME
        / ManifestBuildPolicy.MANIFEST_FILE_NAME
    )


def _iter_source_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Yield every scannable Python source file under the package root.

    Args:
        root: The `melder` package directory.

    Returns:
        Iterable[pathlib.Path]: Source files in stable sorted order.
    """
    for path in sorted(root.rglob("*.py")):
        if any(part in ManifestBuildPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def _module_name_for(path: pathlib.Path, root: pathlib.Path) -> str:
    """
    Derive a file's dotted module name relative to the package root.

    Args:
        path: The source file.
        root: The `melder` package directory.

    Returns:
        str: Dotted module name.
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
            if (suffix, qualname) in ManifestBuildPolicy.EXCLUDED:
                continue
            entries.add((module_name, qualname))
    return sorted(entries)


def render_manifest(entries: List[Tuple[str, str]], version: str) -> str:
    """
    Render the generated manifest module source.

    Args:
        entries: Sorted manifest entries.
        version: The melder version this manifest corresponds to.

    Returns:
        str: Complete module source, newline-terminated.
    """
    lines: List[str] = [
        '"""',
        "GENERATED DURABLE BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "Internal-bind manifest asset. Regenerated automatically when",
        "the melder version changes or via build_scripts:",
        "    python build_scripts/build_internal_manifest.py",
        "",
        "Each entry is a `(module, qualname)` pair naming one melder-internal",
        "class that must never be registered as a spell.",
        "",
        "PAYLOAD SHAPE - emitted as a tuple display. A set display folds to a",
        "frozenset constant in the .pyc instead, but that only MOVES the 577-tuple",
        "hashing cost from the frozenset() call into marshal load. Measured with",
        "typing pre-imported (the real condition inside melder): 267us tuple vs",
        "288us set, i.e. a wash. Do not churn this shape for performance.",
        '"""',
        "from typing import FrozenSet",
        "from typing import Tuple",
        "",
        "",
        f'BUILT_FOR_VERSION: str = "{version}"',
        f"MANIFEST_ENTRY_COUNT: int = {len(entries)}",
        "",
        "INTERNAL_MANIFEST: FrozenSet[Tuple[str, str]] = frozenset((",
    ]
    for module_name, qualname in entries:
        lines.append(f'    ("{module_name}", "{qualname}"),')
    lines.append("))")
    lines.append("")
    return "\n".join(lines)


def write_manifest(version: str) -> Tuple[pathlib.Path, int]:
    """
    Scan the package and write the durable manifest asset to disk.

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
