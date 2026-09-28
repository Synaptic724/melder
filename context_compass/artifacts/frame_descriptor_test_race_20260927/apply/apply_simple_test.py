"""Replace the stand-in version of the cleanup race test with the owner's simple form. melder_0, 2026-09-27.

Usage: python apply_simple_test.py <repository root>
Runs on a tree where apply_hardened_test.py was applied. Edits only
tests/unit/melder/aether/test_aetheric_frame_descriptor.py; keeps its BOM and CRLF line endings.
"""

import importlib.util
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eol_lines

assert sys.version_info >= (3, 14), "run with the 3.14 venv"

_spec = importlib.util.spec_from_file_location(
    "apply_hardened_test", pathlib.Path(__file__).resolve().parent / "apply_hardened_test.py"
)
hardened = importlib.util.module_from_spec(_spec)
sys.argv = [sys.argv[0], sys.argv[1]]
_spec.loader.exec_module(hardened)

TARGET = hardened.TARGET

SIMPLE_HEAD = '''def test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify the frame name accessor, and that two cleanups racing on one descriptor leave it cleaned.

    Contract:
        - Two threads call `cleanup()` at the same moment. One tears the descriptor down; the other returns at
          a `_cleaned` check, or raises AttributeError if it reaches the lock after the winner deleted it. A
          cleaned descriptor must not be used any more, so that AttributeError is expected and ignored.
        - Any other exception, or a thread that does not finish, fails the test.
        - Afterwards `check_cleaned()` raises: the descriptor reports itself cleaned.

    Returns:
        None.
    """
'''

SIMPLE_THREADS = '''    descriptor = FrameDescriptor("ops")
    start = threading.Barrier(2)
    unexpected_errors: List[BaseException] = []

    def run_cleanup() -> None:
        """Start together with the other thread, clean up, and keep any error but the use-after-clean one."""
        try:
            start.wait(timeout=10.0)
            descriptor.cleanup()
        except AttributeError:
            # The other cleanup finished first and deleted the lock; this descriptor is no longer usable.
            return
        except BaseException as error:
            unexpected_errors.append(error)

    threads = [threading.Thread(target=run_cleanup, daemon=True) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15.0)

    assert not any(thread.is_alive() for thread in threads)
    assert unexpected_errors == []
    with pytest.raises(RuntimeError, match="already been cleaned"):
        descriptor.check_cleaned()
'''


DOCSTRING_GAP_OLD = '''        - Afterwards `check_cleaned()` raises: the descriptor reports itself cleaned.

    Returns:
        None.
    """

    descriptor = FrameDescriptor("ops")
'''

DOCSTRING_GAP_NEW = '''        - Afterwards `check_cleaned()` raises: the descriptor reports itself cleaned.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
'''

def main() -> int:
    """Swap the stand-in version for the simple one and restore the original imports plus List."""
    for old, new in (
        (hardened.IMPORT_TYPES_NEW, hardened.IMPORT_TYPES_OLD),
        (hardened.IMPORT_TYPING_NEW, "from typing import List, Optional, Tuple\n"),
        (hardened.HELPER_NEW, SIMPLE_HEAD),
        (hardened.THREADS_NEW, SIMPLE_THREADS),
        (DOCSTRING_GAP_OLD, DOCSTRING_GAP_NEW),
    ):
        print(eol_lines.replace_lines(TARGET, old, new))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
