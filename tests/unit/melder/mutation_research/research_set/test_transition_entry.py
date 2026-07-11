import pytest

from melder.mutation_research.research_set.transition_entry import (
    TransitionAct,
    TransitionEntry,
)


def test_entry_carries_all_recorded_fields() -> None:
    """
    Verify one entry preserves every supplied field verbatim.
    """
    entry = TransitionEntry(
        3,
        TransitionAct.registered,
        "lane-1",
        from_spell_id=None,
        to_spell_id="sha-a",
        actor="mutation_0",
        campaign="campaign-x",
        reason="first declaration",
        metadata={"module_source_sha256": "mod-1"},
    )

    assert entry.sequence == 3
    assert entry.act is TransitionAct.registered
    assert entry.lane_id == "lane-1"
    assert entry.to_spell_id == "sha-a"
    assert entry.from_spell_id is None
    assert entry.actor == "mutation_0"
    assert entry.campaign == "campaign-x"
    assert entry.reason == "first declaration"
    assert entry.metadata == {"module_source_sha256": "mod-1"}
    assert entry.created_at


def test_entry_validation_rejects_bad_inputs() -> None:
    """
    Verify sequence, act, and lane_id validation guards.
    """
    with pytest.raises(ValueError, match="sequence"):
        TransitionEntry(0, TransitionAct.registered, "lane-1")
    with pytest.raises(ValueError, match="lane_id"):
        TransitionEntry(1, TransitionAct.registered, "")
    with pytest.raises(ValueError, match="TransitionAct"):
        TransitionEntry(1, "registered", "lane-1")


def test_entry_touches_spell_id_matches_either_end() -> None:
    """
    Verify identity matching covers both endpoints.
    """
    entry = TransitionEntry(
        1,
        TransitionAct.joined,
        "lane-1",
        from_spell_id="sha-old",
        to_spell_id="sha-new",
    )

    assert entry.touches_spell_id("sha-old") is True
    assert entry.touches_spell_id("sha-new") is True
    assert entry.touches_spell_id("sha-other") is False


def test_entry_describe_from_payload_roundtrip() -> None:
    """
    Verify describe() and from_payload() are exact inverses.
    """
    entry = TransitionEntry(
        7,
        TransitionAct.attached,
        "lane-2",
        to_spell_id="sha-anchor",
        actor="agent",
        metadata={"anchor_lane_id": "lane-1"},
    )

    rebuilt = TransitionEntry.from_payload(entry.describe())

    assert rebuilt.describe() == entry.describe()


def test_entry_metadata_is_detached() -> None:
    """
    Verify metadata reads never expose the internal store.
    """
    entry = TransitionEntry(1, TransitionAct.lane_created, "lane-1")
    snapshot = entry.metadata
    snapshot["injected"] = True

    assert entry.metadata == {}


def test_entry_cleanup_is_idempotent_and_guards_reads() -> None:
    """
    Verify cleanup semantics and use-after-clean guards.
    """
    entry = TransitionEntry(1, TransitionAct.archived, "lane-1")
    entry.cleanup()
    entry.cleanup()

    assert entry.cleaned is True
    with pytest.raises(RuntimeError):
        _ = entry.sequence


def test_act_vocabulary_is_world_entry_only() -> None:
    """
    Verify the act vocabulary carries no checkout/rollback acts (the
    grouped acts are forward-only world entries for compositions -
    2026-07-11 GroupedResearchNode ruling - not rewinds).
    """
    values = {act.value for act in TransitionAct}

    assert values == {
        "lane_created",
        "registered",
        "staged",
        "promoted",
        "attached",
        "detached",
        "joined",
        "archived",
        "restored",
        "group_registered",
        "group_recomposed",
    }
