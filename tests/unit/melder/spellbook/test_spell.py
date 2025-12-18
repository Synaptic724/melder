"""Auto-generated placeholder test to mirror src structure.
Tests will be replaced with real coverage when available.
"""
from __future__ import annotations

import importlib
import sys
from collections import namedtuple

import pytest

MODULE_PATH = "melder.spellbook.spell"


def test_import_module(monkeypatch) -> None:
    """Ensure the spell module and its dependencies are importable."""
    pytest.importorskip("ulid")
    VersionInfo = namedtuple(
        "VersionInfo", [
            "major",
            "minor",
            "micro",
            "releaselevel",
            "serial",
        ],
    )
    fake_version_info = VersionInfo(3, 13, 0, "final", 0)
    monkeypatch.setattr(sys, "version_info", fake_version_info)
    importlib.import_module(MODULE_PATH)
