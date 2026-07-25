"""
Pre-generate the internal-bind manifest cache, and gate against staleness in CI.

Melder's registration guard refuses to bind kernel/control-plane classes. The
authoritative list is a generated `(module, qualname)` manifest living at
`melder/__melder_cache__/__init_cache__/internal_manifest.py`.

That cache is a build product. It is NOT shipped in the wheel: melder rebuilds
it automatically on first import in any environment (see
`melder.__melder_cache__.__init_cache__`). Running this script pre-builds it so a local checkout
never pays the cold-boot scan.

All scanning logic lives in `melder.__melder_cache__.__init_cache__._builder` - the package owns
it, because `build_scripts/` is not shipped and a cold boot in an installed
environment must work with no external tooling present. This script is a thin
CLI over that module.

Usage
-----
    python build_scripts/build_internal_manifest.py            # write the cache
    python build_scripts/build_internal_manifest.py --check    # CI staleness gate
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys
from typing import List

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SRC_ROOT = _REPO_ROOT / "src"
_PACKAGE_ROOT = _SRC_ROOT / "melder"


def _load_isolated(name: str, path: pathlib.Path):
    """
    Load a single module directly from its file, bypassing package import.

    Contract:
        Deliberately does NOT import `melder`. Importing the package would pull
        in the entire runtime just to run a scanner, and the manifest is a
        bootstrap artifact the guard depends on - it must be buildable without
        a working import of the thing it describes.

    Args:
        name: Module name to register the loaded module under.
        path: Source file to load.

    Returns:
        types.ModuleType: The loaded module.

    Raises:
        ImportError: If the module cannot be loaded from `path`.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_builder = _load_isolated(
    "_melder_manifest_builder", _PACKAGE_ROOT / "__melder_cache__" / "__init_cache__" / "_builder.py"
)
__version__ = _load_isolated(
    "_melder_version", _PACKAGE_ROOT / "__version__.py"
).__version__


def main(argv: List[str]) -> int:
    """
    Generate or verify the manifest cache.

    Args:
        argv: Command-line arguments (excluding the program name).

    Returns:
        int: `0` on success; `1` when `--check` finds the cache missing or stale.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed cache is current; write nothing",
    )
    args = parser.parse_args(argv)

    entries = _builder.scan_manifest()
    rendered = _builder.render_manifest(entries, __version__)
    target = _builder.cache_path()

    if args.check:
        if not target.exists():
            print("STALE: manifest cache has not been generated.", file=sys.stderr)
            return 1
        if target.read_text(encoding="utf-8") != rendered:
            print(
                "STALE: internal manifest cache is out of date. Regenerate with:\n"
                "    python build_scripts/build_internal_manifest.py",
                file=sys.stderr,
            )
            return 1
        print(f"OK: manifest cache current ({len(entries)} entries).")
        return 0

    written, count = _builder.write_cache(__version__)
    print(f"WROTE {written.relative_to(_REPO_ROOT)} ({count} entries, v{__version__})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
