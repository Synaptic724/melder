import pytest

from melder.mutation_research.research_set.research_lane import (
    LaneType,
    ResearchLane,
)
from melder.mutation_research.research_set.research_set import ResearchSet


def test_lane_type_defaults_and_vocabulary() -> None:
    """
    Verify freeform lanes default to experiment, the guaranteed default
    lane is development, explicit types stick, and unknown words refuse
    teach-grade naming the vocabulary.
    """
    research_set = ResearchSet("types")

    assert research_set.default_lane.lane_type is LaneType.development
    assert research_set.create_lane("free").lane_type is LaneType.experiment
    assert research_set.create_lane(
        "prod", lane_type="production",
    ).lane_type is LaneType.production

    with pytest.raises(ValueError, match="Known types"):
        research_set.create_lane("bad", lane_type="mainline")
    research_set.cleanup()


def test_lane_type_rides_describe_and_journal() -> None:
    """
    Verify the type rides the lane payload and the lane_created journal
    metadata.
    """
    research_set = ResearchSet("types")
    lane = research_set.create_lane("exp", lane_type="test")

    assert lane.describe()["lane_type"] == "test"
    created_events = [
        entry for entry in research_set.journal.describe()["entries"]
        if entry["act"] == "lane_created"
        and entry["lane_id"] == lane.lane_id
    ]
    assert created_events[-1]["metadata"]["lane_type"] == "test"
    research_set.cleanup()


def test_lane_type_hydration_round_trip_and_back_compat() -> None:
    """
    Verify from_payload restores an explicit type exactly, and a payload
    sealed BEFORE the vocabulary (no lane_type key) hydrates as
    development for the default lane and experiment otherwise.
    """
    explicit = ResearchLane("prod", lane_type="production")
    assert ResearchLane.from_payload(
        explicit.describe()
    ).lane_type is LaneType.production

    legacy_default = ResearchLane("default").describe()
    legacy_other = ResearchLane("side").describe()
    del legacy_default["lane_type"]
    del legacy_other["lane_type"]
    assert ResearchLane.from_payload(
        legacy_default
    ).lane_type is LaneType.development
    assert ResearchLane.from_payload(
        legacy_other
    ).lane_type is LaneType.experiment


def test_join_type_gate_only_when_enforcement_armed() -> None:
    """
    Verify the join policy matrix: enforcement OFF lets type-mixing joins
    ride the normal divergence law; enforcement ON refuses a type-mixing
    join without force (teach-grade, naming both types), allows it WITH
    force, and never gates same-type joins.
    """
    research_set = ResearchSet("types")
    research_set.register_spell("sha-base")
    research_set.create_lane(
        "exp-a",
        lane_type="experiment",
        attach_to="default",
        attach_at_spell_id="sha-base",
    )

    # OFF (default posture): clean anchored join proceeds despite the
    # experiment -> development type mix.
    assert research_set.lane_type_enforcement is False
    research_set.join("exp-a", into="default")

    # ON: the same arrangement now refuses without force.
    research_set.set_lane_type_enforcement(True)
    research_set.create_lane(
        "exp-b",
        lane_type="experiment",
        attach_to="default",
        attach_at_spell_id="sha-base",
    )
    with pytest.raises(RuntimeError, match="Type-mixing join"):
        research_set.join("exp-b", into="default")
    research_set.join("exp-b", into="default", force=True)

    # ON, same types: no gate.
    research_set.create_lane(
        "exp-c",
        lane_type="development",
        attach_to="default",
        attach_at_spell_id="sha-base",
    )
    research_set.join("exp-c", into="default")
    research_set.cleanup()


def test_record_world_entry_mints_declared_ancestry() -> None:
    """
    Verify the runtime seam mints multi-parent nodes when parents are
    supplied, refuses undeclared parents loudly, and journals the
    ancestry.
    """
    research_set = ResearchSet("mint")
    research_set.register_spell("sha-left")
    research_set.register_spell("sha-right")

    with pytest.raises(ValueError, match="not resident"):
        research_set.record_world_entry(
            "sha-child",
            parent_spell_ids=["sha-left", "sha-ghost"],
        )

    node = research_set.record_world_entry(
        "sha-child",
        parent_spell_ids=["sha-left", "sha-right"],
    )
    assert node.parent_spell_ids == ["sha-left", "sha-right"]
    registered = [
        entry for entry in research_set.journal.describe()["entries"]
        if entry["act"] == "registered"
        and entry["to_spell_id"] == "sha-child"
    ]
    assert registered[-1]["metadata"]["parent_spell_ids"] == [
        "sha-left", "sha-right",
    ]
    research_set.cleanup()
