"""
Unit tests for MutationResearch appends at constant cost (GitHub #331, patch configure_in_seconds_2026_11_17).

Purpose:
    Pin the owner's decisions of 2026-11-17: an append (`record_world_entry`, `register_spell`, `register_group`,
    `recompose_group`) marks the undo ring stale instead of minting a snapshot; organizing verbs, `snapshot_network`
    and the ring reads mint the pending snapshot first, so the organization an organizing verb started from stays
    restorable; `describe_composition` mints nothing; an append describes only its own node.

Runs only on 3.14t (melder package root import chain).
"""
from collections import Counter
from typing import Any, Callable

import pytest

from melder.mutation_research.research_set.research_lane import LaneState
from melder.mutation_research.research_set.research_node import ResearchNode
from melder.mutation_research.research_set.research_set import ResearchSet


def _ring_as_described(research_set: ResearchSet) -> list:
    """
    Read the ring addresses the composition payload carries, which reads without minting.

    Args:
        research_set: The set to describe.

    Returns:
        list: The `network_snapshot_shas` of `describe_composition()`.
    """
    return list(research_set.describe_composition()["network_snapshot_shas"])


def _count_node_describes(monkeypatch: pytest.MonkeyPatch) -> Counter:
    """
    Count every `ResearchNode.describe` call from now on, delegating to the real method.

    Args:
        monkeypatch: The test's monkeypatch, which restores the method.

    Returns:
        Counter: `counts["describe"]` is the number of calls since this returned.
    """
    counts: Counter = Counter()
    original: Callable[..., Any] = ResearchNode.describe

    def counting(self: ResearchNode) -> Any:
        """Record one call, then describe for real."""
        counts["describe"] += 1
        return original(self)

    monkeypatch.setattr(ResearchNode, "describe", counting)
    return counts


def test_appends_mint_no_snapshot_until_the_ring_is_read() -> None:
    """
    Contract: world entries and explicit declarations leave the ring as it was; the first ring read mints one
    snapshot for all of them, and a second read mints nothing more.
    """
    research_set = ResearchSet("default")
    ring_at_birth = _ring_as_described(research_set)

    research_set.record_world_entry("sha-a")
    research_set.register_spell("sha-b")
    research_set.record_world_entry("sha-c", staged=True)

    assert _ring_as_described(research_set) == ring_at_birth
    read_once = research_set.network_snapshot_shas()
    assert len(read_once) == len(ring_at_birth) + 1
    assert research_set.network_snapshot_shas() == read_once
    assert research_set.latest_network_snapshot == read_once[-1]
    research_set.cleanup()


def test_the_latest_snapshot_property_mints_the_pending_organization() -> None:
    """
    Contract: `latest_network_snapshot` read after appends names the organization holding them, which a restore
    rebuilds.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")

    latest = research_set.latest_network_snapshot
    research_set.create_lane("later")
    research_set.restore_network(latest)

    assert research_set.lane_names() == ["default"]
    assert research_set.default_lane.node_spell_ids() == ["sha-a", "sha-b"]
    research_set.cleanup()


def test_group_appends_mark_the_ring_stale_too() -> None:
    """
    Contract: `register_group` and `recompose_group` append a composition and mint nothing; the next ring read mints
    one snapshot holding both compositions.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")
    ring_before = _ring_as_described(research_set)

    first = research_set.register_group(["sha-a"])
    research_set.recompose_group(first.group_id, add=["sha-b"])

    assert _ring_as_described(research_set) == ring_before
    assert len(research_set.network_snapshot_shas()) == len(ring_before) + 1
    research_set.cleanup()


@pytest.mark.parametrize("organizing_verb", ["join", "archive"])
def test_an_organizing_verb_mints_the_organization_it_starts_from(organizing_verb: str) -> None:
    """
    Contract: with appends pending and no ring read, `join` and `archive` first mint the organization they start
    from, so restoring that snapshot (the one before the verb's own) brings the lane and its nodes back.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.create_lane("child", attach_to="default", attach_at_spell_id="sha-a")
    research_set.register_spell("sha-b", lane="child", parent_spell_ids=["sha-a"])
    research_set.register_spell("sha-c", lane="child", parent_spell_ids=["sha-b"])

    if organizing_verb == "join":
        research_set.join("child", into="default")
    else:
        research_set.archive("child")
    shas = research_set.network_snapshot_shas()
    research_set.restore_network(shas[-2], reason="undo the organizing verb")

    child = research_set.get_lane("child")
    assert child.state is LaneState.open
    assert child.node_spell_ids() == ["sha-b", "sha-c"]
    assert research_set.residence_of("sha-c") == child.lane_id
    research_set.cleanup()


def test_describing_and_reading_the_set_mint_nothing() -> None:
    """
    Contract: `describe_composition`, `walk`, `heads` and `history` stay read-only: with appends pending, the ring the
    composition carries is unchanged by them.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    ring_before = _ring_as_described(research_set)

    research_set.describe_composition()
    research_set.walk("default")
    research_set.heads()
    research_set.history("sha-a")

    assert _ring_as_described(research_set) == ring_before
    research_set.cleanup()


def test_an_append_describes_only_its_own_node(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Contract: the 51st world entry builds its own node's payload once and describes no other node, however many
    the set already holds.
    """
    research_set = ResearchSet("default")
    for index in range(50):
        research_set.record_world_entry(f"sha-{index}")
    counts = _count_node_describes(monkeypatch)

    research_set.record_world_entry("sha-50")

    assert counts["describe"] == 1
    research_set.cleanup()


def test_a_refused_add_leaves_the_residence_and_a_later_append_as_before() -> None:
    """
    Contract: a registration into an archived lane claims residence, is refused by the lane and rolls the claim
    back; the residence the composition carries is unchanged, and the next append lands normally.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.create_lane("closed")
    research_set.archive("closed")
    residence_before = research_set.describe_composition()["organization"]["residence"]

    with pytest.raises(RuntimeError):
        research_set.register_spell("sha-x", lane="closed")

    assert research_set.describe_composition()["organization"]["residence"] == residence_before
    research_set.record_world_entry("sha-y")
    assert research_set.residence_of("sha-y") == research_set.default_lane.lane_id
    assert research_set.residence_of("sha-x") is None
    research_set.cleanup()
