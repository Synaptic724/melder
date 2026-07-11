import pytest

from melder.mutation_research.research_set.research_lane import LaneState
from melder.mutation_research.research_set.research_set import ResearchSet


def _seeded_set() -> ResearchSet:
    """
    Build one set with a default-lane version and an anchored child lane.

    Returns:
        ResearchSet: Seeded network (default: sha-a; child: sha-b, sha-c).
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.create_lane(
        "child", attach_to="default", attach_at_sha="sha-a",
    )
    research_set.register_spell("sha-b", lane="child", parent_shas=["sha-a"])
    research_set.register_spell("sha-c", lane="child", parent_shas=["sha-b"])
    return research_set


def test_set_guarantees_default_lane() -> None:
    """
    Verify the default lane exists from birth.
    """
    research_set = ResearchSet("default")

    assert research_set.lane_names() == ["default"]
    assert research_set.default_lane.name == "default"
    research_set.cleanup()


def test_register_spell_defaults_to_default_lane() -> None:
    """
    Verify the auto-default ruling: no orphan binds, no history holes.
    """
    research_set = ResearchSet("default")
    node = research_set.register_spell("sha-a", module_sha="mod-1")

    assert node.spell_sha == "sha-a"
    assert research_set.residence_of("sha-a") == (
        research_set.default_lane.lane_id
    )
    assert research_set.default_lane.tip_sha == "sha-a"
    research_set.cleanup()


def test_register_spell_rediscovery_names_holding_lane() -> None:
    """
    Verify single residence: re-registration raises the rediscovery signal.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")

    with pytest.raises(RuntimeError, match="Rediscovery"):
        research_set.register_spell("sha-a", lane="default")
    research_set.cleanup()


def test_register_spell_requires_known_parents() -> None:
    """
    Verify ancestry must reference formally declared versions.
    """
    research_set = ResearchSet("default")

    with pytest.raises(ValueError, match="not resident"):
        research_set.register_spell("sha-a", parent_shas=["sha-ghost"])
    research_set.cleanup()


def test_create_lane_anchoring_requires_full_arguments() -> None:
    """
    Verify anchor arguments travel together and target a real node.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")

    with pytest.raises(ValueError, match="together"):
        research_set.create_lane("half", attach_to="default")
    with pytest.raises(KeyError, match="sha-ghost"):
        research_set.create_lane(
            "bad", attach_to="default", attach_at_sha="sha-ghost",
        )
    with pytest.raises(ValueError, match="already has a lane"):
        research_set.create_lane("default")
    research_set.cleanup()


def test_clean_join_folds_history_and_archives_source() -> None:
    """
    Verify the fast-forward-analog join: full line folds into the receiver,
    residence transfers, the source becomes terminal.
    """
    research_set = _seeded_set()
    receiver = research_set.join("child", into="default")

    assert receiver.node_shas() == ["sha-a", "sha-b", "sha-c"]
    assert receiver.tip_sha == "sha-c"
    child = research_set.get_lane("child")
    assert child.state is LaneState.joined
    assert research_set.residence_of("sha-b") == receiver.lane_id
    with pytest.raises(RuntimeError, match="joined"):
        research_set.register_spell("sha-d", lane="child")
    research_set.cleanup()


def test_divergent_join_requires_force() -> None:
    """
    Verify divergence-awareness: a moved receiver tip refuses the join until
    force=True supersedes.
    """
    research_set = _seeded_set()
    research_set.create_lane(
        "rival", attach_to="default", attach_at_sha="sha-a",
    )
    research_set.register_spell(
        "sha-r1", lane="rival", parent_shas=["sha-a"],
    )
    research_set.join("child", into="default")

    with pytest.raises(RuntimeError, match="Divergent join"):
        research_set.join("rival", into="default")
    research_set.join("rival", into="default", force=True)

    assert research_set.default_lane.tip_sha == "sha-r1"
    research_set.cleanup()


def test_collapse_join_moves_tip_only() -> None:
    """
    Verify the collapse dial: the tip moves; earlier records stay readable
    in the joined container with residence intact.
    """
    research_set = _seeded_set()
    research_set.join("child", into="default", collapse=True)

    child = research_set.get_lane("child")
    assert research_set.default_lane.tip_sha == "sha-c"
    assert child.has_node("sha-b") is True
    assert research_set.residence_of("sha-b") == child.lane_id
    assert research_set.residence_of("sha-c") == (
        research_set.default_lane.lane_id
    )
    research_set.cleanup()


def test_attach_detach_organize_ancestry_only() -> None:
    """
    Verify attach/detach move the anchor and never the content.
    """
    research_set = _seeded_set()
    research_set.register_spell("sha-z")
    research_set.create_lane("floater")
    research_set.attach("floater", onto="default", at_sha="sha-z")

    floater = research_set.get_lane("floater")
    assert floater.anchor_sha == "sha-z"
    assert floater.node_count == 0
    assert research_set.default_lane.has_node("sha-z") is True

    research_set.detach("floater")
    assert floater.anchor_lane_id is None

    with pytest.raises(RuntimeError, match="itself"):
        research_set.attach("floater", onto="floater", at_sha="sha-z")
    research_set.cleanup()


def test_archive_retires_dead_ends_but_never_default() -> None:
    """
    Verify archive semantics and the default-lane guarantee.
    """
    research_set = ResearchSet("default")
    research_set.create_lane("dead-end")
    research_set.archive("dead-end", reason="abandoned")

    assert research_set.get_lane("dead-end").state is LaneState.archived
    with pytest.raises(RuntimeError, match="never archives"):
        research_set.archive("default")
    research_set.cleanup()


def test_walk_history_heads_read_surfaces() -> None:
    """
    Verify the read verbs report ordered lines, per-identity history, and
    open-lane tips only.
    """
    research_set = _seeded_set()
    research_set.join("child", into="default")

    walk = research_set.walk("default")
    assert [step["spell_sha"] for step in walk] == [
        "sha-a", "sha-b", "sha-c",
    ]

    history = research_set.history("sha-b")
    assert history["lane_name"] == "default"
    assert history["node"]["parent_shas"] == ["sha-a"]
    assert len(history["transitions"]) >= 1
    with pytest.raises(KeyError, match="not resident"):
        research_set.history("sha-ghost")

    heads = research_set.heads()
    assert heads == {"default": "sha-c"}
    research_set.cleanup()


def test_restore_network_recovers_organization_and_keeps_history() -> None:
    """
    Verify the recovery mechanic: organization rewinds to the addressed
    snapshot while the journal only ever grows.
    """
    research_set = _seeded_set()
    snapshot_before_join = research_set.latest_network_snapshot
    research_set.join("child", into="default")
    entries_before_restore = research_set.journal.entry_count

    research_set.restore_network(snapshot_before_join, reason="undo join")

    child = research_set.get_lane("child")
    assert child.state is LaneState.open
    assert child.node_shas() == ["sha-b", "sha-c"]
    assert research_set.residence_of("sha-b") == child.lane_id
    assert research_set.journal.entry_count == entries_before_restore + 1
    assert research_set.journal.entries()[-1].act.value == "restored"
    with pytest.raises(KeyError):
        research_set.restore_network("no-such-snapshot")
    research_set.cleanup()


def test_composition_roundtrip_hydrates_equivalent_set() -> None:
    """
    Verify the twin-payload seam: describe_composition() rebuilds an
    equivalent set whose journal continues minting without reuse.
    """
    research_set = _seeded_set()
    payload = research_set.describe_composition()

    rebuilt = ResearchSet.from_payload(payload)

    assert rebuilt.lane_names() == research_set.lane_names()
    assert rebuilt.set_id == research_set.set_id
    assert rebuilt.journal.latest_sequence == (
        research_set.journal.latest_sequence
    )
    rebuilt.create_lane("post-hydration")
    assert rebuilt.journal.entries()[-1].sequence == (
        research_set.journal.latest_sequence + 1
    )
    research_set.cleanup()
    rebuilt.cleanup()


def test_on_mutation_fires_per_mutating_verb_only() -> None:
    """
    Verify the persistence emission hook cadence: one call per successful
    mutating verb, none for reads.
    """
    calls = []
    research_set = ResearchSet("default", on_mutation=lambda: calls.append(1))
    baseline = len(calls)

    research_set.register_spell("sha-a")
    research_set.create_lane("child")
    research_set.walk("default")
    research_set.heads()

    assert len(calls) == baseline + 2
    research_set.cleanup()


def test_set_cleanup_cascades_and_guards() -> None:
    """
    Verify cleanup cascades into every owned structure.
    """
    research_set = _seeded_set()
    journal = research_set.journal
    lane = research_set.get_lane("child")
    research_set.cleanup()
    research_set.cleanup()

    assert research_set.cleaned is True
    assert journal.cleaned is True
    assert lane.cleaned is True
    with pytest.raises(RuntimeError):
        research_set.register_spell("sha-x")
