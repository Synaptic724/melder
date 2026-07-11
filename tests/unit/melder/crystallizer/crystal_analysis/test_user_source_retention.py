"""
S2 physical custody unit suite: opt-in user-source TEXT retention.

Covers the record-side chain (flag -> harvest -> store -> describe ->
re-fold) and the preflight rows (tamper blocker, drift warning, info
lanes, hydration downgrade). The engine rebuild lane is exercised by the
integration round-trip (seal -> delete tree -> restore).
"""

import hashlib
from pathlib import Path

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy import (
    UserSourceCustodyStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.hydration_strategy import (
    HydrationStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analyzer import (
    PersistenceAnalyzer,
)
from melder.crystallizer.crystal_analysis.preflight.user_source_integrity_strategy import (
    UserSourceIntegrityStrategy,
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_retention_flag_defaults_off_and_rides_the_fluent_lane():
    """
    Contract: retain_user_sources defaults False (with_defaults included)
    and flips through the fluent setter; the schema key exists so the
    reload lane covers it.
    """
    configuration = CrystallizerConfiguration()
    try:
        assert "retain_user_sources" in configuration.available_properties
        configuration.with_defaults()
        assert configuration.retain_user_sources is False
    finally:
        configuration.cleanup()

    flipped = CrystallizerConfiguration()
    try:
        flipped.with_defaults()
        flipped.with_retain_user_sources(True)
        assert flipped.retain_user_sources is True
    finally:
        flipped.cleanup()


def test_user_harvest_payload_reads_text_sha_and_package_flag(tmp_path):
    """
    Contract: harvest returns {source_text, source_sha256, module_path,
    is_package} for a readable .py file; the sha matches the retained
    text; packages are flagged via __init__.py.
    """
    root = tmp_path / "userland"
    root.mkdir()
    module_file = root / "widget.py"
    module_file.write_text("VALUE = 41\n", encoding="utf-8")
    package_init = root / "__init__.py"
    package_init.write_text("", encoding="utf-8")

    strategy = UserSourceCustodyStrategy((root.resolve(),))
    try:
        payload = strategy.harvest_payload(
            module_name="userland.widget", module_path=module_file
        )
        assert payload is not None
        assert payload["source_text"] == "VALUE = 41\n"
        assert payload["source_sha256"] == _sha("VALUE = 41\n")
        assert payload["is_package"] is False

        package_payload = strategy.harvest_payload(
            module_name="userland", module_path=package_init
        )
        assert package_payload is not None
        assert package_payload["is_package"] is True

        assert strategy.harvest_payload(
            module_name="userland.gone", module_path=root / "gone.py"
        ) is None
        assert strategy.harvest_payload(
            module_name="userland.pathless", module_path=None
        ) is None
    finally:
        strategy.cleanup()


def test_result_stores_and_describes_and_refolds_user_sources():
    """
    Contract: record_user_module_source round-trips through the property,
    the describe key, and stays detached (mutating the returned map never
    touches the store).
    """
    result = CrystalAnalysisResult()
    try:
        result.record_user_module_source(
            "userland.widget",
            {
                "source_text": "VALUE = 41\n",
                "source_sha256": _sha("VALUE = 41\n"),
                "module_path": "/gone/userland/widget.py",
                "is_package": False,
            },
        )
        carried = result.user_module_sources
        assert "userland.widget" in carried
        carried["userland.widget"]["source_text"] = "tampered"
        assert result.user_module_sources["userland.widget"][
            "source_text"
        ] == "VALUE = 41\n"
        assert "userland.widget" in result.describe()["user_module_sources"]
    finally:
        result.cleanup()


def test_integrity_strategy_blocks_tamper_and_warns_on_drift(tmp_path):
    """
    Contract: retained text failing its own sha = blocker; a LIVE file
    differing from the bind-time fingerprint = warning
    (user_source_drifted_since_seal); retained module whose file is
    absent produces no integrity row (the rebuild lane owns that case).
    """
    live_file = tmp_path / "drifted.py"
    live_file.write_text("VALUE = 99\n", encoding="utf-8")

    bundle = {
        "spell_crystal": {
            "sha-1": {
                "physical_module_fingerprints": {
                    "userland.drifted": _sha("VALUE = 41\n"),
                },
                "user_module_sources": {
                    "userland.tampered": {
                        "source_text": "VALUE = 1\n",
                        "source_sha256": _sha("something else"),
                        "module_path": "/gone/tampered.py",
                        "is_package": False,
                    },
                    "userland.drifted": {
                        "source_text": "VALUE = 41\n",
                        "source_sha256": _sha("VALUE = 41\n"),
                        "module_path": str(live_file),
                        "is_package": False,
                    },
                    "userland.absent": {
                        "source_text": "VALUE = 2\n",
                        "source_sha256": _sha("VALUE = 2\n"),
                        "module_path": str(tmp_path / "absent.py"),
                        "is_package": False,
                    },
                },
            },
        },
    }
    # Preflight strategies are stateless ABCs (no lifecycle to clean).
    findings = UserSourceIntegrityStrategy().analyze(bundle)
    by_severity = {}
    for row in findings:
        by_severity.setdefault(row["severity"], []).append(row["detail"])
    assert any(
        "userland.tampered" in detail for detail in by_severity["blocker"]
    )
    assert any(
        "user_source_drifted_since_seal" in detail
        for detail in by_severity["warning"]
    )
    assert all(
        "userland.absent" not in detail
        for rows in by_severity.values()
        for detail in rows
    )


def test_hydration_downgrades_absent_module_with_retained_text():
    """
    Contract: an unimportable hydratable root stays a blocker WITHOUT
    retention and downgrades to info WITH retained text for that module.
    """
    def _bundle(with_retention):
        crystal = {
            # The strategy's FIRST gate is owning-book presence - the
            # bundle must carry the spellbook or every crystal blocks
            # before the module checks even run.
            "spellbook_id": "book-1",
            "rebindability": "hydratable",
            "root_target_kind": "class",
            "root_module_kind": "user_source",
            "root_module_name": "userland.definitely_not_importable_s2",
        }
        if with_retention:
            crystal["user_module_sources"] = {
                "userland.definitely_not_importable_s2": {
                    "source_text": "class Thing: pass\n",
                    "source_sha256": _sha("class Thing: pass\n"),
                    "module_path": "/gone/thing.py",
                    "is_package": False,
                },
            }
        return {
            "spellbook": {"book-1": {"spellbook_id": "book-1"}},
            "spell_crystal": {"sha-1": crystal},
        }

    # Preflight strategies are stateless ABCs (no lifecycle to clean).
    strategy = HydrationStrategy()
    blocked = strategy.analyze(_bundle(False))
    assert any(row["severity"] == "blocker" for row in blocked)

    retained = strategy.analyze(_bundle(True))
    assert all(row["severity"] != "blocker" for row in retained)
    assert any(
        row["severity"] == "info" and "RETAINED" in str(row["detail"])
        for row in retained
    )


def test_analyzer_default_set_includes_user_source_integrity():
    """
    Contract: the default preflight set carries the S2 integrity pass
    (8th row) so every restore report covers retained user sources.
    """
    analyzer = PersistenceAnalyzer()
    try:
        names = [strategy.name for strategy in analyzer._strategies]
        assert "user_source_integrity" in names
        assert "synthetic_source_integrity" in names
    finally:
        analyzer.cleanup()
