"""Apply only this lane's files from apply_fix.py (argv[1] = tree root).

fable_0 landed the Phase-3 half in C-C (F0-16), so compiler_phase_3.py and test_compiler_phase_3.py are skipped:
every replace_block on them is refused here. Everything else in apply_fix.py runs unchanged.
"""
import pathlib
import runpy
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import patch_util

SKIPPED = {"compiler_phase_3.py", "test_compiler_phase_3.py"}
_replace = patch_util.replace_block


def _guarded_replace(path: pathlib.Path, old: str, new: str, count: int = 1) -> None:
    """Skip fable_0's files; delegate every other replacement to patch_util.replace_block."""
    if path.name in SKIPPED:
        print(f"skipped {path.name} (fable_0's C-C file)")
        return
    _replace(path, old, new, count)


patch_util.replace_block = _guarded_replace
runpy.run_path(str(HERE / "apply_fix.py"), run_name="__main__")
