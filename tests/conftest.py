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
