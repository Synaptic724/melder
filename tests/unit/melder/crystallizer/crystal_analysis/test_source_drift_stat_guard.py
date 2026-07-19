"""
Unit tests for the SourceDriftStrategy stat-guard lane (IO-economy,
2026-07-19): unchanged worlds preflight without reads; tamper and honesty
channels survive the cache.

Runs only on 3.14t (melder package root import chain).
"""
import hashlib
from pathlib import Path

import pytest

from melder.crystallizer.crystal_analysis.physical_source_cache import (
    PhysicalSourceCache,
)
from melder.crystallizer.crystal_analysis.preflight.source_drift_strategy import (
    SourceDriftStrategy,
)


@pytest.fixture(autouse=True)
def clear_physical_source_cache():
    """
    Purpose:
        Isolate every drift row behind an empty shared cache.
    Contract:
        - Clears cache entries and counters before and after each test.
    Returns:
        None.
    """
    PhysicalSourceCache._clear_for_tests()
    yield
    PhysicalSourceCache._clear_for_tests()


def _bundle(module_name, sealed_text, path):
    """
    Build one spell_crystal payload bundle in the preflight shape.
    """
    return {
        "spell_crystal": {
            "sha-1": {
                "module_to_path": {module_name: str(path)},
                "physical_module_fingerprints": {
                    module_name: hashlib.sha256(
                        sealed_text.encode("utf-8")
                    ).hexdigest(),
                },
            },
        },
    }


def test_unchanged_world_preflights_silently_without_second_reads(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The load-time half of the IO storm: an unchanged sealed world
        must preflight silently, and a SECOND pass must not re-read.
    Contract:
        No findings both passes; pass two runs with read_text poisoned.
    """
    module_file = tmp_path / "steady.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    bundle = _bundle("steady", "VALUE = 1\n", module_file)
    strategy = SourceDriftStrategy()
    assert strategy.analyze(bundle) == []

    def _explode(*args, **kwargs):
        raise AssertionError("unchanged drift pass must not read files")

    monkeypatch.setattr(Path, "read_text", _explode)
    assert strategy.analyze(bundle) == []


def test_drift_after_a_primed_pass_still_warns(tmp_path):
    """
    Purpose:
        Truth law through the cache: an edit AFTER a silent pass warns on
        the next pass (stat guard misses, fresh hash compares).
    Contract:
        One "user_source_drifted_since_seal" warning row appears.
    """
    module_file = tmp_path / "mutable.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    bundle = _bundle("mutable", "VALUE = 1\n", module_file)
    strategy = SourceDriftStrategy()
    assert strategy.analyze(bundle) == []
    module_file.write_text(
        "VALUE = 1\nTAMPERED = True\n", encoding="utf-8"
    )
    findings = strategy.analyze(bundle)
    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert "user_source_drifted_since_seal" in str(findings[0])


def test_unreadable_file_keeps_the_info_honesty_row(
        tmp_path, monkeypatch,
):
    """
    Purpose:
        The honesty channel survives the cache rewrite: a file that
        exists but cannot be read reports INFO, never raises and never
        fabricates a verdict.
    Contract:
        One info row naming the module.
    """
    module_file = tmp_path / "locked.py"
    module_file.write_text("VALUE = 1\n", encoding="utf-8")
    bundle = _bundle("locked", "VALUE = 1\n", module_file)

    def _explode(self, *args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(Path, "read_text", _explode)
    strategy = SourceDriftStrategy()
    findings = strategy.analyze(bundle)
    assert len(findings) == 1
    assert findings[0]["severity"] == "info"
    assert "locked" in str(findings[0])
