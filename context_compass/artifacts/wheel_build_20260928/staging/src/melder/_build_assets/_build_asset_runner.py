"""
Discovery-driven runner for every durable build asset melder ships.

WHY THIS EXISTS
---------------
Generated assets rot silently. `bind.py` imports the internal-bind manifest at
module scope and there is no runtime rebuild lane, so whatever is committed IS
the enforced policy - a manifest generated before a class was added will happily
enforce a class list that no longer matches the source. That has already
happened once in this repo. This runner is the single entry point that
regenerates every asset and the single gate CI uses to refuse a stale one.

THE CONVENTION
--------------
One asset per directory beneath this file. A directory participates simply by
containing a `_builder.py`; nothing is registered, imported, or configured::

    _build_assets/
        _build_asset_runner.py      <- this file
        _bind_guard/
            _builder.py             <- discovered automatically
            bind_guard.py           <- loader, hand-written
            manifest/
                bind_guard_manifest.py       <- GENERATED, committed
        _agent_documentation/
            _builder.py             <- same shape, no runner edit needed
            agent_documentation.py
            manifest/
                agent_documentation_manifest.py

Adding a behaviour is therefore "create a folder with a `_builder.py`". Removing
one is "delete the folder". The runner needs no edit either way. Assets are
named for what they DO - `_bind_guard`, `_agent_documentation` - so the folder
says which behaviour it owns rather than which file format it happens to use.

WHAT THE RUNNER DOES *NOT* TOUCH
--------------------------------
The `.melc` caches under `__melder_cache__/__<asset>__/`. Those are derived,
gitignored, interpreter-specific, and rebuilt on demand at import time by
`melder.utilities.caching_system.asset_cache`. This runner's whole surface is
the COMMITTED manifest: the truth the cache is derived FROM. Building a cache
here would bake one interpreter's marshal format into a build step that has no
idea which interpreter will read it.

The split is also why nothing runtime lives in this directory: `_build_assets/`
holds tools that run at BUILD time and never execute in a user's process.

THE BUILDER CONTRACT
--------------------
Every discovered `_builder.py` MUST expose three module-level callables:

    target_path() -> pathlib.Path
        Absolute path of the artifact this builder owns.

    render(version: str) -> str
        The artifact's full text for the given melder version. MUST be pure and
        deterministic: called twice with one version it returns identical text,
        which is what makes `--check` a byte-exact comparison rather than a
        heuristic.

    write(version: str) -> Tuple[pathlib.Path, int]
        Write the artifact and return its path plus an item count for reporting.

A directory whose `_builder.py` is missing any of the three is reported as a
CONTRACT VIOLATION and fails the run, rather than being skipped quietly - a
builder that cannot be checked is worse than no builder at all.

OPTIONAL, EACH BUYING ONE CHECK
-------------------------------
Absent, the runner falls back to the slow byte comparison and still gives a
correct answer - these only make the gate sharper and cheaper:

    source_fingerprint() -> str
        SHA256 over the builder's inputs. Turns staleness into a key compare
        instead of a full re-render.

    manifest_version() -> str
        SCHEMA version of the manifest shape, independent of the melder
        release. Checked separately from content because a manifest in an older
        shape may not hydrate at all, so it must never pass on a key match.

ISOLATION
---------
Builders are loaded BY FILE PATH through `importlib.util.spec_from_file_location`,
never through `import melder...`. Importing the package would execute
`melder/__init__.py` and boot `Aether()`, making the generator depend on the very
runtime it describes - and on the asset it is about to write. Loading by path
keeps generation cycle-free and lets this run against a half-built tree.

USAGE
-----
    python src/melder/_build_assets/_build_asset_runner.py            # regenerate all
    python src/melder/_build_assets/_build_asset_runner.py --check    # CI gate
    python src/melder/_build_assets/_build_asset_runner.py --list     # show discovered
"""
import argparse
import importlib.util
import re
import pathlib
import sys
from types import ModuleType
from typing import List, Optional, Tuple


class BuildAssetRunnerPolicy:
    """
    Static namespace for the runner's fixed conventions.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        BUILDER_FILE_NAME: Filename that marks a directory as a build asset.
        REQUIRED_CALLABLES: The builder contract. Every discovered builder must
            expose all three or the run fails.
        VERSION_MODULE_NAME: Package-root module carrying the single version truth.
    """

    BUILDER_FILE_NAME: str = "_builder.py"
    REQUIRED_CALLABLES: Tuple[str, ...] = ("target_path", "render", "write")
    FINGERPRINT_CALLABLE: str = "source_fingerprint"
    SCHEMA_CALLABLE: str = "manifest_version"
    VERSION_MODULE_NAME: str = "__version__.py"


def _assets_root() -> pathlib.Path:
    """
    Return the directory this runner lives in, which is the asset root.

    Returns:
        pathlib.Path: `<package>/_build_assets`.
    """
    return pathlib.Path(__file__).resolve().parent


def _package_root() -> pathlib.Path:
    """
    Return the `melder` package directory.

    Returns:
        pathlib.Path: The directory containing `__version__.py`.
    """
    return _assets_root().parent


def _load_by_path(module_name: str, path: pathlib.Path) -> ModuleType:
    """
    Load one module directly from its file, bypassing package import.

    Contract:
        Deliberately does NOT go through `import melder...`. See the ISOLATION
        note in the module docstring: importing the package boots `Aether()` and
        would make asset generation depend on the runtime being generated.

    Args:
        module_name: Name to register the loaded module under.
        path: Absolute path to the `.py` file.

    Returns:
        ModuleType: The executed module.

    Raises:
        ImportError: When the file cannot be turned into a loadable spec.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def melder_version() -> str:
    """
    Read the single version truth without importing the package.

    Returns:
        str: The `__version__` string every asset is stamped with.
    """
    version_module = _load_by_path(
        "_melder_version_for_assets",
        _package_root() / BuildAssetRunnerPolicy.VERSION_MODULE_NAME,
    )
    return version_module.__version__


def discover_builders() -> List[pathlib.Path]:
    """
    Find every asset builder beneath the asset root.

    Contract:
        Scans IMMEDIATE subdirectories only - one asset per directory, no
        nesting - and returns them sorted so runs are reproducible and diffs are
        stable. Directories without a `_builder.py` are not assets and are
        ignored silently; that is how the generated output and any future data
        files coexist beside a builder.

    Returns:
        List[pathlib.Path]: Absolute paths to each discovered `_builder.py`.
    """
    root = _assets_root()
    found: List[pathlib.Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name == "__pycache__":
            continue
        builder = child / BuildAssetRunnerPolicy.BUILDER_FILE_NAME
        if builder.is_file():
            found.append(builder)
    return found


def _load_builder(builder_path: pathlib.Path) -> ModuleType:
    """
    Load one builder and verify it satisfies the builder contract.

    Args:
        builder_path: Path to a discovered `_builder.py`.

    Returns:
        ModuleType: The loaded builder module.

    Raises:
        AttributeError: When the builder is missing a required callable. Failing
            loudly is deliberate: a builder that cannot be rendered cannot be
            checked, so silently skipping it would let an asset rot unnoticed.
    """
    asset_name = builder_path.parent.name
    module = _load_by_path(f"_melder_asset_builder_{asset_name}", builder_path)
    missing = [
        name
        for name in BuildAssetRunnerPolicy.REQUIRED_CALLABLES
        if not callable(getattr(module, name, None))
    ]
    if missing:
        raise AttributeError(
            f"build asset '{asset_name}' violates the builder contract: "
            f"{builder_path} is missing {', '.join(missing)}. "
            f"Every _builder.py must expose "
            f"{', '.join(BuildAssetRunnerPolicy.REQUIRED_CALLABLES)}."
        )
    return module


def build_all(version: str) -> int:
    """
    Regenerate every discovered asset.

    Args:
        version: The melder version to stamp into each artifact.

    Returns:
        int: `0` on success.
    """
    builders = discover_builders()
    if not builders:
        print("No build assets discovered.", file=sys.stderr)
        return 1
    for builder_path in builders:
        asset_name = builder_path.parent.name
        module = _load_builder(builder_path)
        written, count = module.write(version)
        print(f"WROTE  {asset_name:<20} {written.name} ({count} entries, v{version})")
    return 0


def check_all(version: str) -> int:
    """
    Verify every committed asset matches what its builder would produce now.

    Contract:
        Byte-exact text comparison, not a count or a timestamp. That catches a
        version bump with no content change, a content change with no version
        bump, and a hand-edit of a generated file - all three of which have
        produced wrong state in this repo before.

    Args:
        version: The melder version each artifact is expected to carry.

    Returns:
        int: `0` when every asset is current; `1` when any is missing or stale.
    """
    builders = discover_builders()
    if not builders:
        print("No build assets discovered.", file=sys.stderr)
        return 1
    stale: List[str] = []
    for builder_path in builders:
        asset_name = builder_path.parent.name
        module = _load_builder(builder_path)
        target = module.target_path()
        if not target.exists():
            print(f"STALE  {asset_name:<20} not generated: {target}", file=sys.stderr)
            stale.append(asset_name)
            continue
        committed = target.read_text(encoding="utf-8")

        # FAST PATH - compare KEYS, do not rebuild.
        # A builder exposing `source_fingerprint()` lets staleness be decided by
        # one SHA256 over raw source bytes instead of a full AST parse + harvest
        # + render. The slow path below only runs for builders without a key.
        #
        # The patterns match a BARE assignment (`NAME = "..."`), which is what
        # the lean loaders emit. They previously required `NAME: str = "..."`;
        # when annotations moved out to the .pyi stubs, every match silently
        # became `None` and every asset silently took the slow path. Nothing
        # failed - the gate just quietly stopped being fast. `test_fast_path_*`
        # in the runner tests now asserts the render path is never entered.
        fingerprint = getattr(module, BuildAssetRunnerPolicy.FINGERPRINT_CALLABLE, None)
        if callable(fingerprint):
            stamped = re.search(r'^SOURCE_SHA256\s*=\s*"([0-9a-f]{64})"', committed, re.MULTILINE)
            stamped_version = re.search(r'^BUILT_FOR_VERSION\s*=\s*"([^"]+)"', committed, re.MULTILINE)
            stamped_schema = re.search(r'^MANIFEST_VERSION\s*=\s*"([^"]+)"', committed, re.MULTILINE)
            schema_of = getattr(module, BuildAssetRunnerPolicy.SCHEMA_CALLABLE, None)
            expected_schema = schema_of() if callable(schema_of) else None
            if stamped and stamped_version:
                # Schema drift is checked separately from content drift: a
                # payload written in an older SHAPE is not merely out of date,
                # it may not hydrate at all, so it must never pass on a key match.
                if stamped_schema and expected_schema and stamped_schema.group(1) != expected_schema:
                    print(
                        f"STALE  {asset_name:<20} manifest schema moved "
                        f"{stamped_schema.group(1)} -> {expected_schema}",
                        file=sys.stderr,
                    )
                    stale.append(asset_name)
                    continue
                if stamped.group(1) == fingerprint() and stamped_version.group(1) == version:
                    schema = stamped_schema.group(1) if stamped_schema else "?"
                    print(
                        f"OK     {asset_name:<20} current "
                        f"(v{version}, schema {schema}, key match)"
                    )
                    continue
                print(
                    f"STALE  {asset_name:<20} source key or version moved "
                    f"(expected v{version})",
                    file=sys.stderr,
                )
                stale.append(asset_name)
                continue

        # SLOW PATH - only for builders that expose no fingerprint key.
        if committed != module.render(version):
            print(
                f"STALE  {asset_name:<20} out of date or version-mismatched "
                f"(expected v{version})",
                file=sys.stderr,
            )
            stale.append(asset_name)
            continue
        print(f"OK     {asset_name:<20} current (v{version})")
    if stale:
        print(
            f"\n{len(stale)} stale asset(s): {', '.join(stale)}\nRegenerate with:\n"
            f"    python src/melder/_build_assets/_build_asset_runner.py",
            file=sys.stderr,
        )
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """
    Command-line entry point.

    Args:
        argv: Arguments excluding the program name; defaults to `sys.argv[1:]`.

    Returns:
        int: Process exit code.
    """
    parser = argparse.ArgumentParser(
        description="Regenerate or verify melder's durable build assets."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed assets are current; write nothing (CI gate)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list discovered asset builders and exit",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.list:
        for builder_path in discover_builders():
            print(f"{builder_path.parent.name:<20} {builder_path}")
        return 0

    version = melder_version()
    return check_all(version) if args.check else build_all(version)


if __name__ == "__main__":
    raise SystemExit(main())
