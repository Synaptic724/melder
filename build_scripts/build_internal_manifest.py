"""
Pre-generate the durable internal-bind manifest asset, and gate against staleness in CI.

Melder's registration guard refuses to bind kernel/control-plane classes. The
authoritative list is a generated `(module, qualname)` manifest living at
`src/melder/_build_assets/_init_manifest/internal_manifest.py`.

Usage
-----
    python build_scripts/build_internal_manifest.py            # write/update manifest
    python build_scripts/build_internal_manifest.py --check    # CI staleness & version gate
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
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_builder = _load_isolated(
    "_melder_manifest_builder",
    _PACKAGE_ROOT / "_build_assets" / "_init_manifest" / "_builder.py",
)
__version__ = _load_isolated(
    "_melder_version", _PACKAGE_ROOT / "__version__.py"
).__version__


def main(argv: List[str]) -> int:
    """
    Generate or verify the durable manifest asset.

    Args:
        argv: Command-line arguments (excluding the program name).

    Returns:
        int: `0` on success; `1` when `--check` finds the manifest missing or stale.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed manifest is current and matches version; write nothing",
    )
    args = parser.parse_args(argv)

    entries = _builder.scan_manifest()
    rendered = _builder.render_manifest(entries, __version__)
    target = _builder.manifest_path()

    if args.check:
        if not target.exists():
            print("STALE: internal manifest asset has not been generated.", file=sys.stderr)
            return 1
        current_text = target.read_text(encoding="utf-8")
        if current_text != rendered:
            print(
                f"STALE: internal manifest asset is out of date or version mismatched (expected v{__version__}).\n"
                "Regenerate with:\n"
                "    python build_scripts/build_internal_manifest.py",
                file=sys.stderr,
            )
            return 1
        print(f"OK: internal manifest asset current ({len(entries)} entries, v{__version__}).")
        return 0

    written, count = _builder.write_manifest(__version__)
    print(f"WROTE {written.relative_to(_REPO_ROOT)} ({count} entries, v{__version__})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
