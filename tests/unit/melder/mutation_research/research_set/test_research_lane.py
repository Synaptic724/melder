import pytest

from melder.mutation_research.research_set.research_lane import (
    LaneState,
    ResearchLane,
)
from melder.mutation_research.research_set.research_node import ResearchNode


def _node(spell_id: str) -> ResearchNode:
    """
    Build one minimal version record for lane tests.

    Args:
        spell_id:
            Identity for the record.

    Returns:
        ResearchNode: Minimal node.
    """
    return ResearchNode(spell_id)


def test_lane_starts_open_and_empty_with_ulid_identity() -> None:
    """
    Verify fresh-lane posture: open, empty, identified, unanchored.
    """
    lane = ResearchLane("feature-x")

    assert lane.state is LaneState.open
    assert lane.node_count == 0
    assert lane.tip_spell_id is None
    assert lane.anchor_lane_id is None
    assert lane.lane_id
    assert lane.name == "feature-x"


def test_lane_add_node_orders_and_advances_tip() -> None:
    """
    Verify registration order and tip advancement.
    """
    lane = ResearchLane("feature-x")
    lane.add_node(_node("sha-a"))
    lane.add_node(_node("sha-b"))

    assert lane.node_spell_ids() == ["sha-a", "sha-b"]
    assert lane.tip_spell_id == "sha-b"
    assert lane.has_node("sha-a") is True
    assert lane.get_node("sha-a").spell_id == "sha-a"


def test_lane_rejects_duplicate_identity() -> None:
    """
    Verify full-object records dedup by content SHA within a lane.
    """
    lane = ResearchLane("feature-x")
    lane.add_node(_node("sha-a"))

    with pytest.raises(ValueError, match="already holds"):
        lane.add_node(_node("sha-a"))


def test_lane_detach_nodes_preserves_order_and_recomputes_tip() -> None:
    """
    Verify the join-transfer mechanic detaches in order and fixes the tip.
    """
    lane = ResearchLane("feature-x")
    for sha in ["sha-a", "sha-b", "sha-c"]:
        lane.add_node(_node(sha))

    detached = lane.detach_nodes(["sha-c", "sha-a"])

    assert [node.spell_id for node in detached] == ["sha-a", "sha-c"]
    assert lane.node_spell_ids() == ["sha-b"]
    assert lane.tip_spell_id == "sha-b"
    with pytest.raises(KeyError):
        lane.detach_nodes(["sha-missing"])


def test_lane_anchor_set_and_clear() -> None:
    """
    Verify ancestry anchoring is organization-only state.
    """
    lane = ResearchLane("feature-x")
    lane.set_anchor("lane-parent", "sha-base")

    assert lane.anchor_lane_id == "lane-parent"
    assert lane.anchor_spell_id == "sha-base"

    lane.clear_anchor()
    assert lane.anchor_lane_id is None
    with pytest.raises(RuntimeError, match="no anchor"):
        lane.clear_anchor()


def test_lane_terminal_states_refuse_further_work() -> None:
    """
    Verify joined/archived are terminal for the container.
    """
    joined = ResearchLane("joined-lane")
    joined.mark_joined("lane-target")
    assert joined.state is LaneState.joined
    assert joined.joined_into_lane_id == "lane-target"
    with pytest.raises(RuntimeError, match="joined"):
        joined.add_node(_node("sha-a"))
    with pytest.raises(RuntimeError, match="joined"):
        joined.mark_archived()

    archived = ResearchLane("archived-lane")
    archived.mark_archived()
    assert archived.state is LaneState.archived
    with pytest.raises(RuntimeError, match="archived"):
        archived.set_anchor("lane-x", "sha-x")


def test_lane_describe_from_payload_roundtrip() -> None:
    """
    Verify describe() and from_payload() are exact inverses, including
    state, anchor, order, and nested nodes.
    """
    lane = ResearchLane("feature-x")
    lane.add_node(_node("sha-a"))
    lane.add_node(_node("sha-b"))
    lane.set_anchor("lane-parent", "sha-base")
    lane.mark_joined("lane-target")

    rebuilt = ResearchLane.from_payload(lane.describe())

    assert rebuilt.describe() == lane.describe()
    assert rebuilt.state is LaneState.joined
    assert rebuilt.tip_spell_id == "sha-b"


def test_lane_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup cascades into nodes and guards further use.
    """
    lane = ResearchLane("feature-x")
    node = _node("sha-a")
    lane.add_node(node)
    lane.cleanup()
    lane.cleanup()

    assert lane.cleaned is True
    assert node.cleaned is True
    with pytest.raises(RuntimeError):
        lane.add_node(_node("sha-b"))
