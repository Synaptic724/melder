"""
DEPRECATED single-asset entry point. Delegates to the build asset runner.

SUPERSEDED 2026-07-25 by `src/melder/_build_assets/_build_asset_runner.py`, which
discovers every `_builder.py` beneath `_build_assets/` by convention instead of
naming one asset. Prefer the runner:

    python src/melder/_build_assets/_build_asset_runner.py            # regenerate all
    python src/melder/_build_assets/_build_asset_runner.py --check    # CI gate

This shim survives only because the path is referenced by existing docs, tickets,
and generated-file headers. It forwards its arguments unchanged so both spellings
share ONE code path - there is no second implementation to drift.
"""
import importlib.util
import pathlib
import sys
from types import ModuleType
from typing import List, Optional


def _load_runner() -> ModuleType:
    """
    Load the build asset runner by file path.

    Contract:
        Loads by path rather than `import melder._build_assets...` for the same
        reason the runner loads builders by path: importing the package would
        boot `Aether()` and make asset generation depend on the runtime it
        describes.

    Returns:
        ModuleType: The executed runner module.

    Raises:
        ImportError: When the runner cannot be located or loaded.
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    runner_path = repo_root / "src" / "melder" / "_build_assets" / "_build_asset_runner.py"
    spec = importlib.util.spec_from_file_location("_melder_build_asset_runner", runner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load build asset runner from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_melder_build_asset_runner"] = module
    spec.loader.exec_module(module)
    return module


def main(argv: Optional[List[str]] = None) -> int:
    """
    Forward to the runner.

    Args:
        argv: Arguments excluding the program name; defaults to `sys.argv[1:]`.

    Returns:
        int: The runner's exit code.
    """
    arguments = sys.argv[1:] if argv is None else argv
    print(
        "NOTE: build_scripts/build_internal_manifest.py is superseded by\n"
        "      python src/melder/_build_assets/_build_asset_runner.py\n",
        file=sys.stderr,
    )
    return _load_runner().main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
