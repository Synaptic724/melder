"""
MR composition preflight suite (mr_restore_build_stage_2026_07_11, S3a/b):
shape blockers, residence-agreement warnings, and the world-scope
adjudication that reclassifies MR findings on formation loads.
"""

from melder.crystallizer.crystal_analysis.preflight.mutation_research_composition_strategy import (
    MutationResearchCompositionStrategy,
)
from melder.crystallizer.crystal_analysis.preflight.persistence_analyzer import (
    PersistenceAnalyzer,
)
from melder.crystallizer.crystal_loader_system.load_admission import (
    LoadAdmission,
)


def _bundle(composition):
    return {
        "mutation_research": {
            "root": {
                "activated": True,
                "configuration_payload": {},
                "composition_payload": composition,
            },
        },
    }


def _set_payload(*, lanes, residence):
    # Mirrors ResearchSet.describe_composition(): organization nests the
    # lanes/residence; journal + versioner ride beside it.
    return {
        "organization": {
            "set_id": "01SET",
            "name": "default",
            "created_at": "01J2",
            "lanes": lanes,
            "residence": residence,
        },
        "journal": {"entries": []},
        "network_snapshot_shas": [],
        "network_versioner": {},
    }


def _lane(lane_id, shas):
    return {
        "lane_id": lane_id,
        "name": lane_id,
        "state": "active",
        "nodes": [{"spell_sha": sha} for sha in shas],
    }


def test_agreeing_composition_produces_no_rows():
    """
    Contract: lane-held SHAs resident under their lanes and residences
    pointing at described lanes = clean; absent/empty compositions also
    produce no rows (pre-Phase-B reports through the stage shortfall).
    """
    strategy = MutationResearchCompositionStrategy()
    clean = _bundle({
        "default": _set_payload(
            lanes=[_lane("lane-1", ["sha-a", "sha-b"])],
            residence={"lane_id_by_sha": {
                "sha-a": "lane-1", "sha-b": "lane-1",
            }},
        ),
    })
    assert strategy.analyze(clean) == []
    assert strategy.analyze(_bundle({})) == []
    assert strategy.analyze({"spell_crystal": {}}) == []


def test_unparseable_shapes_block():
    """
    Contract: composition/set/lanes/residence with the wrong shapes are
    blockers - the rebuild seams could not read them mid-stage.
    """
    strategy = MutationResearchCompositionStrategy()
    rows = strategy.analyze(_bundle("not-a-dict"))
    assert [row["severity"] for row in rows] == ["blocker"]

    rows = strategy.analyze(_bundle({"default": "not-a-dict"}))
    assert [row["severity"] for row in rows] == ["blocker"]

    rows = strategy.analyze(_bundle({
        "default": _set_payload(lanes="wrong", residence={}),
    }))
    assert [row["severity"] for row in rows] == ["blocker"]

    rows = strategy.analyze(_bundle({
        "default": {"journal": {}, "network_snapshot_shas": []},
    }))
    assert [row["severity"] for row in rows] == ["blocker"]
    assert "no organization" in str(rows[0]["detail"])


def test_residence_disagreements_warn_with_teach_grade_details():
    """
    Contract: a lane-held SHA missing from residence, a residence lane
    mismatch, and a residence entry pointing at an undescribed lane each
    produce one warning naming the drift.
    """
    strategy = MutationResearchCompositionStrategy()
    rows = strategy.analyze(_bundle({
        "default": _set_payload(
            lanes=[_lane("lane-1", ["sha-held-unresident", "sha-moved"])],
            residence={"lane_id_by_sha": {
                "sha-moved": "lane-2",
                "sha-ghost": "lane-ghost",
            }},
        ),
    }))
    severities = {row["severity"] for row in rows}
    assert severities == {"warning"}
    details = " | ".join(str(row["detail"]) for row in rows)
    assert "not resident" in details
    assert "held by lane lane-1 but resident under lane lane-2" in details
    assert "does not describe" in details
    # Four rows: held-unresident, lane mismatch, and TWO undescribed-lane
    # rows (sha-moved's residence lane-2 AND sha-ghost's lane-ghost are
    # both absent from the organization).
    assert len(rows) == 4


def test_default_set_registers_the_strategy_ninth():
    """
    Contract: the PersistenceAnalyzer default set carries the MR
    composition pass so every restore report covers folded research.
    """
    analyzer = PersistenceAnalyzer()
    try:
        names = [strategy.name for strategy in analyzer._strategies]
        assert "mutation_research_composition" in names
    finally:
        analyzer.cleanup()


def test_scope_adjudication_reclassifies_mr_findings_on_formation_loads():
    """
    Contract (S3b): MR is a WORLD-scope root - conduit/frame loads never
    rebuild it, so mutation_research_composition warnings reclassify to
    expected_for_scope (exactly like frame_posture) and stop driving the
    admission verdict; world scope keeps the raw verdict.
    """
    preflight = {
        "verdict": "warnings",
        "findings": [{
            "strategy": "mutation_research_composition",
            "severity": "warning",
            "kind": "mutation_research",
            "key": "default",
            "detail": "sha drift",
        }],
        "counts": {"warning": 1},
    }
    conduit_view = LoadAdmission._adjudicate_for_scope(
        dict(preflight), "conduit"
    )
    assert conduit_view["verdict"] == "clean"
    assert [
        row["severity"] for row in conduit_view["reclassified"]
    ] == ["expected_for_scope"]

    world_view = LoadAdmission._adjudicate_for_scope(
        dict(preflight), "world"
    )
    assert world_view["verdict"] == "warnings"
    assert world_view["reclassified"] == []
