"""Pytest configuration for Melder tests."""
from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if SRC_PATH.exists():
    src_as_str = str(SRC_PATH)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)

# The tests tree is a NAMESPACE package (no __init__.py anywhere), so
# `import tests.mocks...` and the tests/_*_support modules resolve only
# when the project root is importable. `python -m pytest` gets this for
# free via the cwd; a bare `pytest` invocation does not - insert the root
# explicitly so both invocations behave identically.
PROJECT_ROOT_AS_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_AS_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_AS_STR)
