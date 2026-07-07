"""
Unit tests for the PersistenceAnalyzer strategy passes: link integrity,
contract peers, hydration viability, configuration loss, and the
aggregate verdict semantics.

Runs only on 3.14t (melder package root import chain).
"""
from melder.crystallizer.persistence.analysis.persistence_analyzer import (
    PersistenceAnalyzer,
)


def _custody(spell_id, spellbook_id="book-1", **extra):
    """
    Build one bundle custody payload with overridable fields.
    """
    payload = {
        "id": spell_id,
        "spellbook_id": spellbook_id,
        "rebindability": "hydratable",
        "root_module_kind": "user_source",
        "root_module_name": "tests.mocks.spellbook.core_classes",
        "root_target_kind": "class",
    }
    payload.update(extra)
    return payload


def test_clean_bundle_verdicts_clean():
    """
    Contract: a self-contained bundle with importable custody produces
    zero findings and the "clean" verdict.
    """
    analyzer = PersistenceAnalyzer()
    report = analyzer.analyze({
        "spellbook": {"book-1": {"spellbook_id": "book-1",
                                 "hook_names": []}},
        "conduit": {"cond-1": {"conduit_id": "cond-1",
                               "spellbook_id": "book-1",
                               "link_targets": []}},
        "spell_crystal": {"sha-1": _custody("sha-1")},
    })
    assert report["verdict"] == "clean"
    assert report["findings"] == []
    analyzer.cleanup()


def test_dangling_link_and_absent_contract_peer_warn():
    """
    Contract: link targets and contract endpoints outside the bundle
    produce WARNING rows (the restore shortfalls them) and the
    "warnings" verdict.
    """
    analyzer = PersistenceAnalyzer()
    report = analyzer.analyze({
        "conduit": {"cond-1": {"conduit_id": "cond-1",
                               "spellbook_id": "book-1",
                               "link_targets": ["cond-gone"]}},
        "contract": {"contract-1": {"contract_id": "contract-1",
                                    "conduit_a_id": "cond-1",
                                    "conduit_b_id": "cond-gone"}},
    })
    assert report["verdict"] == "warnings"
    strategies = sorted(row["strategy"] for row in report["findings"])
    assert strategies == ["contract_peer", "link_integrity"]
    analyzer.cleanup()


def test_hydration_blockers_dominate_the_verdict():
    """
    Contract: missing books, pre-M3 synthetic roots, and unimportable
    modules are BLOCKERS; any blocker makes the verdict "blockers".
    """
    analyzer = PersistenceAnalyzer()
    report = analyzer.analyze({
        "spellbook": {"book-1": {"spellbook_id": "book-1",
                                 "hook_names": []}},
        "spell_crystal": {
            "sha-orphan": _custody("sha-orphan", spellbook_id="book-gone"),
            "sha-pre-m3": _custody(
                "sha-pre-m3", root_module_kind="synthetic_module",
                root_module_name="never_recorded_world",
            ),
            "sha-dead-module": _custody(
                "sha-dead-module",
                root_module_name="tests.no_such_module_anywhere",
            ),
        },
    })
    assert report["verdict"] == "blockers"
    assert report["counts"]["blocker"] == 3
    analyzer.cleanup()


def test_configuration_loss_reports_info_without_changing_verdict():
    """
    Contract: hooks and root callable flags are INFO rows (honest
    bootload expectations) and never move the verdict off "clean".
    """
    analyzer = PersistenceAnalyzer()
    report = analyzer.analyze({
        "spellbook": {"book-1": {"spellbook_id": "book-1",
                                 "hook_names": ["conduit:on_link"]}},
        "aether": {"root": {"configuration_payload": {
            "channel_logger_activation_enabled": True,
            "channel_logger_resolver_present": True,
            "default_logger_present": False,
        }}},
    })
    assert report["verdict"] == "clean"
    assert report["counts"]["info"] == 2
    details = " ".join(str(row["detail"]) for row in report["findings"])
    assert "on_link" in details
    assert "channel_logger_resolver_present" in details
    analyzer.cleanup()
