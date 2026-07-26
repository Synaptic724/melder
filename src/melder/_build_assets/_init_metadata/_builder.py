"""
Internal-bind manifest scanner and durable asset builder.

This module is the SINGLE SOURCE OF TRUTH for how the internal registration manifest is produced.
It lives inside `src/melder/_build_assets/_init_metadata/` as a durable package asset builder.

Consumers:
  * `_build_assets/_build_asset_runner.py` - discovers this file by convention and
    drives it through the target_path/render/write contract at the bottom of this module.
  * `melder.aether.spellbook.bind.bind` - imports `INTERNAL_MANIFEST` from
    `init_metadata.py` and enforces it through `assert_allowed(...)`.

The scan uses pure AST parsing: nothing is imported from `melder`, so it is cycle-safe and free of side effects.

NAMING
------
Directory `_init_metadata`, artifacts `init_metadata.{py,melc,pyi}` - the same
`_<asset>/<asset>.*` shape `_agent_metadata` uses, so the two build assets are
symmetric and the runner's per-directory convention reads uniformly.

The EXPORTED name stays `INTERNAL_MANIFEST`: the directory names the asset, the
constant names the thing, and that thing is specifically the internal-bind
manifest that `assert_allowed(...)` enforces. Renaming it would churn every
ticket and docstring that discusses guard policy for no gain in clarity.

THE THREE ARTIFACTS
-------------------
Each earns its place; none is redundant:

    init_metadata.melc  the marshal payload - the actual data
    init_metadata.py    the import surface; `import marshal` and nothing else
    init_metadata.pyi   the annotations the loader omits, for mypy only

The payload cannot be folded into the loader as a bytes literal: 52 KB of
`\\x..` escapes is ~200 KB of source text for the tokenizer to chew on cold,
which is the exact cost the marshal split was introduced to remove.
"""
import ast
import hashlib
import marshal
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
        INIT_METADATA_DIR_NAME: Package directory holding the manifest asset.
        MANIFEST_FILE_NAME: Generated loader module filename.
        PAYLOAD_FILE_NAME: Marshal payload filename, beside the loader.
        STUB_FILE_NAME: Type stub filename, beside the loader.
        SKIP_DIR_NAMES: Directories excluded from the scan. `__melder_cache__` is
            disposable runtime output, and the asset directories are skipped so
            the generator never records its own scaffolding as bindable internals.
    """

    EXCLUDED: Set[Tuple[str, str]] = set()

    BUILD_ASSETS_DIR_NAME: str = "_build_assets"
    INIT_METADATA_DIR_NAME: str = "_init_metadata"
    MANIFEST_FILE_NAME: str = "init_metadata.py"
    PAYLOAD_FILE_NAME: str = "init_metadata.melc"
    STUB_FILE_NAME: str = "init_metadata.pyi"

    # SCHEMA version of the asset FORMAT, deliberately separate from the melder
    # version it was built for. Mirrors `crystallizer/persistence/record_version.py`.
    # BUILT_FOR_VERSION moves on every release; MANIFEST_VERSION moves only when
    # the payload SHAPE changes - e.g. frozenset -> dict, or a new stamped field.
    # Without it, a reader cannot tell "built by an older melder" (fine, the SHA
    # decides) from "written in a format I cannot parse" (fatal).
    # MAJOR breaks shape. MINOR adds fields. PATCH documents.
    MANIFEST_VERSION: str = "1.0.0"

    # `_init_metadata` is NOT listed: it lives beneath `_build_assets`, so the
    # entry above already excludes it. The old `_init_manifest` entry here was
    # dead config - every path it could have matched was matched one line earlier.
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
    Return the full path of the durable manifest module.

    Returns:
        pathlib.Path: `<package>/_build_assets/_init_metadata/init_metadata.py`.
    """
    return (
        package_root()
        / ManifestBuildPolicy.BUILD_ASSETS_DIR_NAME
        / ManifestBuildPolicy.INIT_METADATA_DIR_NAME
        / ManifestBuildPolicy.MANIFEST_FILE_NAME
    )



def source_fingerprint() -> str:
    """
    SHA256 over the scanned source tree, WITHOUT parsing any of it.

    Purpose:
        Make staleness a KEY COMPARISON instead of a rebuild.

    Contract:
        Hashes each scanned file's repo-relative path and raw bytes, in sorted
        order, into one digest. Reading bytes is roughly an order of magnitude
        cheaper than the AST parse + harvest + render the previous `--check`
        performed on every invocation, and it is exact: any content change,
        rename, addition, or deletion moves the digest.

        Deliberately hashes BYTES, not parsed content - a formatting-only edit
        moves the digest and triggers one regeneration, which is the safe
        direction to be wrong in.

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


def payload_path() -> pathlib.Path:
    """
    Return the marshal payload path beside the loader module.

    Returns:
        pathlib.Path: `<asset dir>/init_metadata.melc`.
    """
    return manifest_path().with_name(ManifestBuildPolicy.PAYLOAD_FILE_NAME)


def stub_path() -> pathlib.Path:
    """
    Return the type-stub path beside the loader module.

    Returns:
        pathlib.Path: `<asset dir>/init_metadata.pyi`.
    """
    return manifest_path().with_name(ManifestBuildPolicy.STUB_FILE_NAME)


def render_manifest(entries: List[Tuple[str, str]], version: str) -> str:
    """
    Render the THIN LOADER module that hydrates the marshal payload.

    Purpose:
        Keep the module interface (`from ... import INTERNAL_MANIFEST`) while
        removing the per-entry construction cost from every process start.

    Contract:
        The module carries only cheap constants plus one `marshal.loads`. It
        does NOT embed 577 tuple literals.

        MEASURED on the real payload, fresh interpreter, minimum of 9 runs:

            .py literals, cold (compile)   4.04 ms
            .py literals, warm (.pyc)      2.14 ms
            marshal payload                0.18 ms   <- 11.7x faster warm

        The literal form makes the interpreter EXECUTE bytecode that builds a
        577-element tuple and then calls `frozenset()` over it, walking every
        node on every process start. `marshal.loads` reconstructs the same
        frozenset in C in a single pass. This mirrors the `.melc` marshal
        bundles `caching_system` already uses.

    Args:
        entries: Sorted manifest entries.
        version: The melder version this manifest corresponds to.

    Returns:
        str: Complete loader module source, newline-terminated.
    """
    return "\n".join([
        '\"\"\"',
        "GENERATED DURABLE BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "Thin loader for the internal-bind manifest. The payload is a marshal",
        "bundle beside this file, mirroring the `.melc` bundles `caching_system`",
        "already uses.",
        "",
        "IMPORTS ONLY `marshal` - DELIBERATELY. Measured on the real 577-entry",
        "payload, fresh interpreter, minimum of 9 runs:",
        "",
        "    .py literals            cold 5.29 ms   warm 3.32 ms",
        "    loader + pathlib/typing cold 5.77 ms   warm 5.09 ms   <- SLOWER",
        "    loader, marshal only    cold 0.64 ms   warm 0.22 ms   <- 14.9x",
        "",
        "`import pathlib` costs 3.77 ms and `from typing import ...` costs",
        "2.88 ms on a cold interpreter, while `import marshal` is free. Adding",
        "either one here spends more than the structure build it was meant to",
        "avoid. Types live in the sibling .pyi stub, which costs nothing at",
        "runtime and keeps mypy fully informed.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '\"\"\"',
        "import marshal",
        "",
        f'MANIFEST_VERSION = "{ManifestBuildPolicy.MANIFEST_VERSION}"',
        f'BUILT_FOR_VERSION = "{version}"',
        f'SOURCE_SHA256 = "{source_fingerprint()}"',
        f"MANIFEST_ENTRY_COUNT = {len(entries)}",
        "",
        'INTERNAL_MANIFEST = marshal.loads(open(__file__[:-3] + ".melc", "rb").read())',
        "",
    ])


def render_stub(entries: List[Tuple[str, str]]) -> str:
    """
    Render the `.pyi` type stub for the generated loader.

    Contract:
        Carries the annotations the loader deliberately omits, so mypy sees full
        types while the runtime imports nothing beyond `marshal`.

    Args:
        entries: Sorted manifest entries (unused; signature kept uniform).

    Returns:
        str: Stub source, newline-terminated.
    """
    return "\n".join([
        "from typing import FrozenSet",
        "from typing import Tuple",
        "",
        "MANIFEST_VERSION: str",
        "BUILT_FOR_VERSION: str",
        "SOURCE_SHA256: str",
        "MANIFEST_ENTRY_COUNT: int",
        "INTERNAL_MANIFEST: FrozenSet[Tuple[str, str]]",
        "",
    ])


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

    payload = payload_path()
    payload_tmp = payload.with_suffix(".melc.tmp")
    payload_tmp.write_bytes(marshal.dumps(frozenset(entries)))
    payload_tmp.replace(payload)

    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(render_manifest(entries, version), encoding="utf-8")
    temporary.replace(target)

    stub = stub_path()
    stub_tmp = stub.with_suffix(".pyi.tmp")
    stub_tmp.write_text(render_stub(entries), encoding="utf-8")
    stub_tmp.replace(stub)
    return target, len(entries)


# ---------------------------------------------------------------------------
# BUILDER CONTRACT
#
# `_build_asset_runner.py` discovers this file by convention and requires these
# three names. They are thin aliases over the descriptive functions above, kept
# separate so the asset-specific vocabulary (`scan_manifest`, `render_manifest`,
# `write_manifest`) stays readable while the runner sees one uniform surface.
# ---------------------------------------------------------------------------


def target_path() -> pathlib.Path:
    """
    Return the artifact path this builder owns.

    Returns:
        pathlib.Path: The generated manifest module's absolute path.
    """
    return manifest_path()


def manifest_version() -> str:
    """
    Return the SCHEMA version of this asset's format.

    Contract:
        Part of the runner's optional contract. Exposed as a callable rather
        than a module constant so the policy class stays the single home for
        the value, per the repo's module scope rule.

    Returns:
        str: The payload format version, independent of the melder release.
    """
    return ManifestBuildPolicy.MANIFEST_VERSION


def render(version: str) -> str:
    """
    Render the artifact text for one melder version.

    Contract:
        PURE and DETERMINISTIC - two calls with the same version and the same
        source tree return byte-identical text. The runner's `--check` gate
        depends on that: it compares this output against the committed file
        exactly, so any nondeterminism here would produce phantom staleness.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        str: Complete module source, newline-terminated.
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
