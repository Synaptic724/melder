"""
Unit tests for the MutationResearch twin emitted from incremental parts (GitHub #331, patch
configure_in_seconds_2026_11_17).

Purpose:
    Pin the owner's decision of 2026-11-17: the root still emits its persistence twin after every mutating verb,
    but from views of append-only parts, so an emission describes no node; the twin, read, equals a fresh
    description of the composition, keeps describing what it was emitted for after a restore or the root's cleanup,
    and a caller mutating a read never reaches the live research.

Runs only on 3.14t (melder package root import chain).
"""
from collections import Counter
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock

import pytest

from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.mutation_research.mutation_research import MutationResearch
from melder.mutation_research.research_set.research_node import ResearchNode


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def _recording_root() -> MutationResearch:
    """
    Build one active root over a MagicMock Aether whose crystallizer poses as live and recording.

    Returns:
        MutationResearch: The configured, activated root; `root._aether._crystallizer.emit` records each twin.
    """
    aether = MagicMock()
    aether.cleaned = False
    aether._crystallizer.cleaned = False
    aether._crystallizer.activated = True
    aether._crystallizer.describe_mutation_research_record.return_value = None
    root = MutationResearch(aether=aether)
    root.configure(root.create_configuration().with_defaults().activate())
    root.activate()
    aether._crystallizer.emit.reset_mock()
    return root


def _emitted_twins(root: MutationResearch) -> List[MutationResearchCrystal]:
    """
    Return every twin the root emitted since `_recording_root`, oldest first.

    Args:
        root: A root built by `_recording_root`.

    Returns:
        List[MutationResearchCrystal]: The emitted twins.
    """
    return [call.args[0] for call in root._aether._crystallizer.emit.call_args_list]


def _build_a_busy_composition(root: MutationResearch) -> None:
    """
    Drive every kind of mutation through the root's default set: appends, lanes, a join, an archive, a promotion
    and compositions.

    Args:
        root: The recording root.

    Returns:
        None.
    """
    research_set = root.research_set()
    root.record_world_entry("sha-a", author="mutation_0")
    research_set.create_lane("child", attach_to="default", attach_at_spell_id="sha-a")
    research_set.register_spell("sha-b", lane="child", parent_spell_ids=["sha-a"], metadata={"k": [1, 2]})
    research_set.register_spell("sha-c", lane="child", parent_spell_ids=["sha-b"])
    research_set.join("child", into="default")
    root.record_world_entry("sha-parked", staged=True)
    research_set.create_lane("dead-end")
    research_set.register_spell("sha-d", lane="dead-end")
    research_set.archive("dead-end")
    root.record_promotion("sha-a", "sha-c", actor="mutation_0")
    group = research_set.register_group(["sha-a", "sha-b"])
    research_set.recompose_group(group.group_id, add=["sha-c"])


def test_the_emitted_twin_equals_a_fresh_description_of_the_composition() -> None:
    """
    Contract: after every kind of mutation, the last emitted twin's composition and rows equal those of a twin
    built from `describe_research_composition()`.
    """
    root = _recording_root()
    _build_a_busy_composition(root)

    twin = _emitted_twins(root)[-1]
    fresh = MutationResearchCrystal(
        activated=True,
        configuration_payload=root.configuration.describe_configuration_payload(),
        composition_payload=root.describe_research_composition(),
    )

    assert twin.describe() == fresh.describe()
    assert twin.research_nodes == fresh.research_nodes
    assert twin.grouped_research_nodes == fresh.grouped_research_nodes
    fresh.cleanup()


def test_an_emission_describes_only_the_appended_node(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Contract: with 50 entries recorded, the 51st world entry - its undo-ring bookkeeping and its twin emission
    included - describes its own node once and no other.
    """
    root = _recording_root()
    for index in range(50):
        root.record_world_entry(f"sha-{index}")
    counts: Counter = Counter()
    original: Callable[..., Any] = ResearchNode.describe

    def counting(self: ResearchNode) -> Any:
        """Record one call, then describe for real."""
        counts["describe"] += 1
        return original(self)

    monkeypatch.setattr(ResearchNode, "describe", counting)
    root.record_world_entry("sha-50")

    assert counts["describe"] == 1
    assert len(_emitted_twins(root)) == 51


def test_a_twin_still_describes_its_composition_after_a_restore_and_after_cleanup() -> None:
    """
    Contract: a twin emitted before a restore keeps describing the composition it was emitted for, and the last
    twin keeps describing the composition after the root is cleaned.
    """
    root = _recording_root()
    research_set = root.research_set()
    research_set.register_spell("sha-a")
    research_set.create_lane("child", attach_to="default", attach_at_spell_id="sha-a")
    research_set.register_spell("sha-b", lane="child", parent_spell_ids=["sha-a"])
    before_restore_twin = _emitted_twins(root)[-1]
    before_restore: Dict[str, object] = root.describe_research_composition()
    research_set.restore_network(research_set.network_snapshot_shas()[0], reason="back to birth")
    last_twin = _emitted_twins(root)[-1]
    last_composition: Dict[str, object] = root.describe_research_composition()

    root.cleanup()

    assert before_restore_twin.describe()["composition_payload"] == before_restore
    assert last_twin.describe()["composition_payload"] == last_composition


def test_mutating_a_twin_read_never_reaches_the_live_research() -> None:
    """
    Contract: a caller editing what a twin returned - a node's fields, its parents, its metadata - changes neither
    the live composition nor the next twin.
    """
    root = _recording_root()
    research_set = root.research_set()
    research_set.register_spell("sha-a", metadata={"tags": ["x"]})
    research_set.register_spell("sha-b", parent_spell_ids=["sha-a"])
    expected = root.describe_research_composition()
    twin = _emitted_twins(root)[-1]

    payload = twin.composition_payload
    nodes = payload["default"]["organization"]["lanes"][0]["nodes"]
    nodes[0]["author"] = "intruder"
    nodes[0]["metadata"]["tags"].append("y")
    nodes[1]["parent_spell_ids"].append("sha-forged")
    research_set.register_spell("sha-c")

    assert root.describe_research_composition()["default"]["organization"]["lanes"][0]["nodes"][:2] == (
        expected["default"]["organization"]["lanes"][0]["nodes"]
    )
    assert _emitted_twins(root)[-1].describe()["composition_payload"] == root.describe_research_composition()


def test_a_refused_add_keeps_the_next_twin_in_step() -> None:
    """
    Contract: a registration refused by an archived lane rolls its residence claim back, and the next emitted twin
    still equals a fresh description.
    """
    root = _recording_root()
    research_set = root.research_set()
    research_set.register_spell("sha-a")
    research_set.create_lane("closed")
    research_set.archive("closed")

    with pytest.raises(RuntimeError):
        research_set.register_spell("sha-x", lane="closed")
    root.record_world_entry("sha-y")

    assert _emitted_twins(root)[-1].describe()["composition_payload"] == root.describe_research_composition()
