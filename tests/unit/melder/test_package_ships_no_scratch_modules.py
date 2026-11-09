"""
Unit test: the melder package ships no scratch module.

WHY THIS EXISTS. TASK-2026-10-16-remove_scratch_marker_from_src (GitHub #256): a 35-byte scratch marker,
`generalized_cache_runtime_rows_SCRATCH.py` (`# scratch marker - replaced below`), sat under
`src/melder/.../generalized/compilers/` from 6d0568f2e until 0.2.8284. Nothing imported it, but it shipped in the
wheel and the generated system documents listed it as a module. This test fails if a scratch-named module ever
lands under the package again.
"""
from pathlib import Path
from typing import List

import melder


def test_no_scratch_module_ships_in_the_melder_package() -> None:
    """
    Verify no Python module under the melder package carries "scratch" in its file name.

    Contract:
        - Walks the imported package's directory (what a build ships), every `.py` file at any depth.
        - Fails naming each offending path, relative to the package, so the leftover is easy to find.

    Returns:
        None.
    """
    package_root = Path(melder.__file__).resolve().parent
    offenders: List[str] = sorted(
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*.py")
        if "scratch" in path.name.lower()
    )

    assert offenders == [], f"Scratch modules ship in the melder package: {offenders}"
