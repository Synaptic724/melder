"""Take the racing second cleanup out of the frame-descriptor test (owner, 2026-09-27). melder_0.

Usage: python apply_no_race_test.py <path to tests/unit/melder/aether/test_aetheric_frame_descriptor.py>
The test keeps its record setup and frame-name check byte for byte, then cleans the descriptor once and asserts that
`check_cleaned()` raises. The second cleanup thread, the Barrier and the AttributeError catch go, and so do the
`threading` and `List` imports that only they used. The test is renamed because it no longer tests a recheck.
The file's BOM and CRLF line endings are kept.
"""

import os
import sys

assert sys.version_info >= (3, 14), "run with the 3.14 venv"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eol_lines import replace_lines

OLD_NAME = "def test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock() -> None:"
NEW_NAME = "def test_descriptor_exposes_frame_name_and_reports_cleaned_after_cleanup() -> None:"
SETUP_FIRST = '    descriptor = FrameDescriptor("ops")'
SETUP_LAST = '    assert descriptor.frame_name == "ops"'
OLD_MARKERS = ("start = threading.Barrier(2)", "except AttributeError:", "descriptor.check_cleaned()")
NEW_HEAD = [
    NEW_NAME,
    '    """',
    "    Verify the frame name accessor on a live descriptor, and that cleanup leaves it reporting itself cleaned.",
    "",
    "    Contract:",
    "        - While the descriptor is live and holds records, `frame_name` returns the name it was built with.",
    "        - After `cleanup()` the descriptor must not be used again, so the test only calls `check_cleaned()`,",
    "          which raises to report that the descriptor is cleaned.",
    "",
    "    Returns:",
    "        None.",
    '    """',
]
NEW_TAIL = [
    "",
    "    descriptor.cleanup()",
    "",
    '    with pytest.raises(RuntimeError, match="already been cleaned"):',
    "        descriptor.check_cleaned()",
]


def rewrite_function(path: str) -> str:
    """Replace the racing test with the single-cleanup version; return 'applied' or 'already applied'."""
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    lines = text.splitlines(keepends=True)
    bare = [line.rstrip("\r\n") for line in lines]
    if NEW_NAME in bare:
        return "already applied"
    start = bare.index(OLD_NAME)
    end = next(i for i in range(start + 1, len(bare)) if bare[i].startswith("def "))
    body = "\n".join(bare[start:end])
    missing = [marker for marker in OLD_MARKERS if marker not in body]
    if missing:
        raise SystemExit(f"unexpected version of the test; missing {missing}")
    setup_start = bare.index(SETUP_FIRST, start, end)
    setup_end = bare.index(SETUP_LAST, setup_start, end)
    trailing = end
    while bare[trailing - 1] == "":
        trailing -= 1
    eol = "\r\n" if lines[start].endswith("\r\n") else "\n"
    new_bare = NEW_HEAD + bare[setup_start:setup_end + 1] + NEW_TAIL
    too_long = [line for line in new_bare if len(line) > 120]
    if too_long:
        raise SystemExit(f"line over 120: {too_long[0]!r}")
    new_lines = [line + eol for line in new_bare]
    lines[start:trailing] = new_lines
    with open(path, "wb") as handle:
        handle.write("".join(lines).encode("utf-8"))
    return "applied"


def main() -> int:
    """Rewrite the test, then drop the imports only the old test used."""
    path = sys.argv[1]
    print("test:", rewrite_function(path))
    print("imports:", replace_lines(
        path,
        "import pytest\nimport threading\nfrom typing import List, Optional, Tuple",
        "import pytest\nfrom typing import Optional, Tuple",
    ))
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    assert "threading" not in text, "threading still referenced"
    assert "List[" not in text, "List still referenced"
    assert text.startswith("﻿"), "BOM lost"
    assert "\n" not in text.replace("\r\n", ""), "a bare LF slipped in"
    print("checks: BOM kept, CRLF only, no threading or List left")
    return 0


if __name__ == "__main__":
    sys.exit(main())
