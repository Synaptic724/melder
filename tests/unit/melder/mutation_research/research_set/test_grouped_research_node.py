import pytest

from melder.mutation_research.research_set.grouped_research_node import (
    GroupedResearchNode,
)
from melder.mutation_research.research_set.research_lane import (
    ResearchLane,
    node_identity,
)
from melder.mutation_research.research_set.research_node import ResearchNode
from melder.mutation_research.research_set.research_set import ResearchSet


def test_group_identity_is_content_addressed_and_canonical() -> None:
    """
    Verify the identity law: order-independent, dedupe-stable, and equal
    member sets mint equal identities (an identical composition IS the
    same fact).
    """
    a = GroupedResearchNode(["sha-b", "sha-a", "sha-c"])
    b = GroupedResearchNode(["sha-c", "sha-a", "sha-b", "sha-a"])

    assert a.group_id == b.group_id
    assert a.member_spell_ids == ["sha-a", "sha-b", "sha-c"]
    assert a.group_id == GroupedResearchNode.compute_group_id(
        ["sha-a", "sha-b", "sha-c"],
    )
    assert a.group_id != GroupedResearchNode.compute_group_id(["sha-a"])

    with pytest.raises(ValueError, match="non-empty list"):
        GroupedResearchNode([])
    with pytest.raises(ValueError, match="non-empty strings"):
        GroupedResearchNode(["sha-a", ""])


def test_group_node_payload_round_trip_and_integrity() -> None:
    """
    Verify describe()/from_payload() are exact inverses (node_type tag
    carried), an untagged payload refuses, and a tampered group_id
    refuses loudly (the record never trusts a corrupted composition).
    """
    node = GroupedResearchNode(
        ["sha-a", "sha-b"],
        parent_group_ids=["prior-group"],
        author="mutation_0",
        campaign="apollo",
        metadata={"note": "s1"},
    )
    payload = node.describe()
    assert payload["node_type"] == "group"

    rebuilt = GroupedResearchNode.from_payload(payload)
    assert rebuilt.describe() == payload

    with pytest.raises(ValueError, match="node_type"):
        GroupedResearchNode.from_payload(
            {key: value for key, value in payload.items()
             if key != "node_type"},
        )

    tampered = dict(payload)
    tampered["group_id"] = "f" * 64
    with pytest.raises(ValueError, match="corrupted or tampered"):
        GroupedResearchNode.from_payload(tampered)


def test_lane_carries_both_node_families() -> None:
    """
    Verify the carrying-code extension: one lane holds spell nodes and
    composition nodes side by side, identity dedup spans both, the tip
    advances across families, and the lane payload round-trips BOTH
    through the node_type dispatch.
    """
    lane = ResearchLane("subsystem")
    spell = ResearchNode("sha-spell")
    group = GroupedResearchNode(["sha-spell"])

    lane._add_node(spell)
    lane._add_node(group)
    assert lane.tip_spell_id == group.group_id
    assert lane.node_count == 2

    with pytest.raises(ValueError, match="already holds"):
        lane._add_node(GroupedResearchNode(["sha-spell"]))
    with pytest.raises(TypeError, match="ResearchNode or a Grouped"):
        lane._add_node(object())
    assert node_identity(spell) == "sha-spell"
    assert node_identity(group) == group.group_id

    rebuilt = ResearchLane.from_payload(lane.describe())
    rebuilt_group = rebuilt.get_node(group.group_id)
    assert isinstance(rebuilt_group, GroupedResearchNode)
    assert rebuilt_group.member_spell_ids == ["sha-spell"]
    assert isinstance(rebuilt.get_node("sha-spell"), ResearchNode)


def test_register_group_laws_and_journal() -> None:
    """
    Verify the grouped world-entry: members must be declared (loud),
    the journal carries the group_registered act with roster metadata,
    and an identical roster re-registration surfaces rediscovery.
    """
    research_set = ResearchSet("groups")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")
    research_set.create_lane("subsystem", lane_type="production")

    with pytest.raises(ValueError, match="not resident"):
        research_set.register_group(["sha-a", "sha-ghost"])

    node = research_set.register_group(
        ["sha-a", "sha-b"],
        lane="subsystem",
        author="mutation_0",
    )
    assert research_set.residence_of(node.group_id) is not None

    events = [
        entry for entry in research_set.journal.describe()["entries"]
        if entry["act"] == "group_registered"
    ]
    assert events[-1]["to_spell_id"] == node.group_id
    assert events[-1]["metadata"]["member_spell_ids"] == [
        "sha-a", "sha-b",
    ]

    with pytest.raises(RuntimeError, match="Rediscovery"):
        research_set.register_group(["sha-b", "sha-a"], lane="subsystem")
    research_set.cleanup()


def test_recompose_group_iterate_and_add_flow() -> None:
    """
    Verify the owner's agent loop: recompose reads the previous roster,
    applies adds/removes, mints the new composition into the SAME lane
    with parents=[previous], journals group_recomposed - and refuses
    no-op rosters, unknown removals, spell targets, and empty results.
    """
    research_set = ResearchSet("groups")
    for sha in ("sha-a", "sha-b", "sha-c"):
        research_set.register_spell(sha)
    research_set.create_lane("subsystem")
    first = research_set.register_group(["sha-a"], lane="subsystem")

    second = research_set.recompose_group(
        first.group_id, add=["sha-b", "sha-c"],
    )
    assert second.member_spell_ids == ["sha-a", "sha-b", "sha-c"]
    assert second.parent_group_ids == [first.group_id]
    assert research_set.residence_of(second.group_id) == \
        research_set.residence_of(first.group_id)

    recomposed_events = [
        entry for entry in research_set.journal.describe()["entries"]
        if entry["act"] == "group_recomposed"
    ]
    assert recomposed_events[-1]["from_spell_id"] == first.group_id
    assert recomposed_events[-1]["to_spell_id"] == second.group_id

    third = research_set.recompose_group(
        second.group_id, remove=["sha-c"],
    )
    assert third.member_spell_ids == ["sha-a", "sha-b"]

    with pytest.raises(RuntimeError, match="identical member"):
        research_set.recompose_group(third.group_id, add=["sha-a"])
    with pytest.raises(ValueError, match="not in the previous"):
        research_set.recompose_group(third.group_id, remove=["sha-ghost"])
    with pytest.raises(RuntimeError, match="spell version"):
        research_set.recompose_group("sha-a", add=["sha-b"])
    with pytest.raises(ValueError, match="would be empty"):
        research_set.recompose_group(
            third.group_id, remove=["sha-a", "sha-b"],
        )
    research_set.cleanup()


def test_compositions_ride_twin_and_restore_loops() -> None:
    """
    Verify the persistence promise EARLY (S3 proves the full loop): a
    composition survives describe_composition -> from_payload hydration,
    and the organization snapshot/restore loop rebuilds it - members,
    ancestry, and type intact.
    """
    research_set = ResearchSet("groups")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")
    research_set.create_lane("subsystem")
    first = research_set.register_group(["sha-a"], lane="subsystem")
    second = research_set.recompose_group(first.group_id, add=["sha-b"])
    # Capture identities BEFORE restore: restore rebuilds the organization
    # wholesale and CLEANS the old containers' nodes (existing law), so
    # in-hand node references die with their containers - identities are
    # the durable handles.
    first_id = first.group_id
    second_id = second.group_id

    hydrated = ResearchSet.from_payload(research_set.describe_composition())
    lane_id = hydrated.residence_of(second_id)
    node = hydrated.get_lane(lane_id).get_node(second_id)
    assert isinstance(node, GroupedResearchNode)
    assert node.member_spell_ids == ["sha-a", "sha-b"]
    assert node.parent_group_ids == [first_id]

    snapshot = research_set.snapshot_network()
    research_set.archive("subsystem", reason="mistake")
    research_set.restore_network(snapshot)
    restored_lane_id = research_set.residence_of(second_id)
    restored = research_set.get_lane(restored_lane_id).get_node(second_id)
    assert isinstance(restored, GroupedResearchNode)
    assert restored.member_spell_ids == ["sha-a", "sha-b"]
    hydrated.cleanup()
    research_set.cleanup()
