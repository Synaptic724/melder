import threading

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
        "child", attach_to="default", attach_at_spell_id="sha-a",
    )
    research_set.register_spell("sha-b", lane="child", parent_spell_ids=["sha-a"])
    research_set.register_spell("sha-c", lane="child", parent_spell_ids=["sha-b"])
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
    node = research_set.register_spell("sha-a", module_source_sha256="mod-1")

    assert node.spell_id == "sha-a"
    assert research_set.residence_of("sha-a") == (
        research_set.default_lane.lane_id
    )
    assert research_set.default_lane.tip_spell_id == "sha-a"
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
        research_set.register_spell("sha-a", parent_spell_ids=["sha-ghost"])
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
            "bad", attach_to="default", attach_at_spell_id="sha-ghost",
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

    assert receiver.node_spell_ids() == ["sha-a", "sha-b", "sha-c"]
    assert receiver.tip_spell_id == "sha-c"
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
        "rival", attach_to="default", attach_at_spell_id="sha-a",
    )
    research_set.register_spell(
        "sha-r1", lane="rival", parent_spell_ids=["sha-a"],
    )
    research_set.join("child", into="default")

    with pytest.raises(RuntimeError, match="Divergent join"):
        research_set.join("rival", into="default")
    research_set.join("rival", into="default", force=True)

    assert research_set.default_lane.tip_spell_id == "sha-r1"
    research_set.cleanup()


def test_collapse_join_moves_tip_only() -> None:
    """
    Verify the collapse dial: the tip moves; earlier records stay readable
    in the joined container with residence intact.
    """
    research_set = _seeded_set()
    research_set.join("child", into="default", collapse=True)

    child = research_set.get_lane("child")
    assert research_set.default_lane.tip_spell_id == "sha-c"
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
    research_set.attach("floater", onto="default", at_spell_id="sha-z")

    floater = research_set.get_lane("floater")
    assert floater.anchor_spell_id == "sha-z"
    assert floater.node_count == 0
    assert research_set.default_lane.has_node("sha-z") is True

    research_set.detach("floater")
    assert floater.anchor_lane_id is None

    with pytest.raises(RuntimeError, match="itself"):
        research_set.attach("floater", onto="floater", at_spell_id="sha-z")
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
    assert [step["spell_id"] for step in walk] == [
        "sha-a", "sha-b", "sha-c",
    ]

    history = research_set.history("sha-b")
    assert history["lane_name"] == "default"
    assert history["node"]["parent_spell_ids"] == ["sha-a"]
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
    assert child.node_spell_ids() == ["sha-b", "sha-c"]
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


def test_record_world_entry_is_idempotent_and_act_aware() -> None:
    """
    Verify the runtime-seam verb: fresh identities register (staged or
    registered act), rediscovery is a quiet None.
    """
    research_set = ResearchSet("default")

    active_node = research_set.record_world_entry("sha-active")
    staged_node = research_set.record_world_entry("sha-parked", staged=True)
    rediscovered = research_set.record_world_entry("sha-active")

    assert active_node is not None and staged_node is not None
    assert rediscovered is None
    acts = [entry.act.value for entry in research_set.journal.entries()]
    assert acts.count("registered") == 1
    assert acts.count("staged") == 1
    assert research_set.residence_of("sha-parked") == (
        research_set.default_lane.lane_id
    )
    research_set.cleanup()


def test_record_promotion_is_journal_only_and_validated() -> None:
    """
    Verify promotion journals a forward event without reorganizing lanes
    or minting a new organization snapshot, and refuses undeclared targets.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-old")
    research_set.register_spell("sha-new")
    snapshots_before = len(research_set.network_snapshot_shas())

    entry = research_set.record_promotion(
        "sha-old", "sha-new", actor="mutation_0", reason="notch",
    )

    assert entry.act.value == "promoted"
    assert entry.from_spell_id == "sha-old" and entry.to_spell_id == "sha-new"
    assert len(research_set.network_snapshot_shas()) == snapshots_before
    assert research_set.default_lane.node_count == 2
    with pytest.raises(KeyError, match="not declared"):
        research_set.record_promotion(None, "sha-ghost")
    research_set.cleanup()


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


def test_composition_carries_and_restores_the_undo_ring() -> None:
    """
    Verify the network-versioner ring rides the composition payload so
    restore_network reaches pre-death organization states after hydration.
    """
    research_set = _seeded_set()
    snapshot_before_join = research_set.latest_network_snapshot
    research_set.join("child", into="default")

    rebuilt = ResearchSet.from_payload(research_set.describe_composition())
    rebuilt.restore_network(snapshot_before_join, reason="post-death undo")

    child = rebuilt.get_lane("child")
    assert child.state is LaneState.open
    assert child.node_spell_ids() == ["sha-b", "sha-c"]
    research_set.cleanup()
    rebuilt.cleanup()


def test_campaign_view_gathers_across_lanes() -> None:
    """
    Verify the campaign read collects stamped nodes and events across lanes
    without side effects.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a", campaign="apollo")
    research_set.create_lane(
        "side", attach_to="default", attach_at_spell_id="sha-a",
        campaign="apollo",
    )
    research_set.register_spell(
        "sha-b", lane="side", parent_spell_ids=["sha-a"], campaign="apollo",
    )
    research_set.register_spell("sha-unrelated")

    view = research_set.campaign_view("apollo")

    assert [n["spell_id"] for n in view["nodes"]] == ["sha-a", "sha-b"]
    assert sorted(view["lane_names"]) == ["default", "side"]
    assert all(t["campaign"] == "apollo" for t in view["transitions"])
    assert len(view["transitions"]) == 3
    with pytest.raises(ValueError, match="campaign"):
        research_set.campaign_view("")
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


def test_group_identity_refused_as_spell_parent() -> None:
    """
    Regression (BUG-033): ancestry validation was residency-only, so a
    composition (group) identity was accepted as a spell parent. Corrected
    behavior: spell ancestry refuses group identities, naming the kind.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    group = research_set.register_group(["sha-a"])

    with pytest.raises(ValueError, match="composition"):
        research_set.register_spell(
            "sha-b", parent_spell_ids=[group.group_id],
        )
    research_set.cleanup()


def test_group_identity_refused_as_group_member() -> None:
    """
    Regression (BUG-033): membership validation was residency-only, so a
    composition identity was accepted as a member of another composition
    (G2=[G1]). Corrected behavior: members must be declared spell versions.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    group = research_set.register_group(["sha-a"])

    with pytest.raises(ValueError, match="compositions pin declared"):
        research_set.register_group([group.group_id])
    research_set.cleanup()


def test_spell_identity_refused_as_group_parent() -> None:
    """
    Regression (BUG-033 reverse leak): `parent_group_ids` validation was
    residency-only, so a SPELL identity was accepted as composition
    ancestry. Corrected behavior: composition ancestry must reference
    recorded compositions.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")
    research_set.register_group(["sha-a"])

    with pytest.raises(ValueError, match="spell\\s+identity"):
        research_set.register_group(["sha-b"], parent_group_ids=["sha-a"])
    research_set.cleanup()


def test_group_ancestry_still_accepts_recorded_compositions() -> None:
    """
    Guard against over-rejection: proper composition ancestry (a recorded
    group as `parent_group_ids`) and proper spell ancestry keep recording.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.register_spell("sha-b")
    parent_group = research_set.register_group(["sha-a"])

    child_group = research_set.register_group(
        ["sha-a", "sha-b"], parent_group_ids=[parent_group.group_id],
    )
    child_spell = research_set.register_spell(
        "sha-c", parent_spell_ids=["sha-a", "sha-b"],
    )

    assert child_group.parent_group_ids == [parent_group.group_id]
    assert child_spell.parent_spell_ids == ["sha-a", "sha-b"]
    research_set.cleanup()


def test_join_refuses_receiver_archived_between_check_and_commit() -> None:
    """
    Regression (BUG-037): join checked the receiver's open state once and
    committed without holding the receiver, so a direct
    lane-surface state flip (lanes were handed out live with public
    mutators pre-BUG-048) could land INSIDE
    the commit window - the audit observed joined nodes inside an archived
    receiver with no exception. Corrected behavior: join holds the
    receiver's lane lock for the whole commit, so a racing archive
    serializes entirely before or entirely after the join - it can never
    interleave mid-commit. (Pre-fix, this test's paused window lets the
    archive win mid-join and the join explodes on the archived receiver;
    post-fix the archive blocks until the join has fully committed.)
    """
    import time

    research_set = _seeded_set()
    receiver = research_set.get_lane(
        research_set.default_lane.lane_id,
    )
    release_archive = threading.Event()
    archive_attempting = threading.Event()
    archive_outcome: list = []

    def racing_archive() -> None:
        release_archive.wait(timeout=10.0)
        archive_attempting.set()
        try:
            receiver._mark_archived()
            archive_outcome.append("archived")
        except RuntimeError:
            archive_outcome.append("refused")

    racer = threading.Thread(target=racing_archive)
    racer.start()

    original_detach = type(receiver)._detach_nodes

    def detach_with_open_window(self, spell_ids):
        # Runs inside join's commit, after the receiver open-check: wake
        # the racing archive and give it the window the bug left open.
        release_archive.set()
        archive_attempting.wait(timeout=10.0)
        time.sleep(0.3)
        return original_detach(self, spell_ids)

    type(receiver)._detach_nodes = detach_with_open_window
    try:
        result = research_set.join("child", into="default")
    finally:
        type(receiver)._detach_nodes = original_detach
    racer.join(timeout=10.0)

    assert not racer.is_alive()
    # The join must have fully committed into a receiver that stayed open
    # through the whole commit: every moved identity resides in the
    # receiver and the receiver holds the folded history.
    assert result is receiver
    assert receiver.node_spell_ids() == ["sha-a", "sha-b", "sha-c"]
    for spell_id in ("sha-a", "sha-b", "sha-c"):
        assert research_set.residence_of(spell_id) == receiver.lane_id
    # The racing archive serialized AFTER the join (archiving the joined
    # receiver afterwards is an ordinary archive).
    assert archive_outcome == ["archived"]
    assert receiver.state.value == "archived"
    research_set.cleanup()


def test_restore_network_refuses_snapshot_without_default_lane() -> None:
    """
    Regression (BUG-038): restore installed decoded lanes/residence without
    validating core invariants, so a payload with no default lane replaced
    live state and `default_lane` then raised KeyError. Corrected behavior:
    restore validates the guaranteed-default-lane invariant BEFORE touching
    live state and refuses loudly, leaving the current organization intact.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    # Forge a retained snapshot whose organization carries no lanes at all.
    versioner = research_set._versioner
    forged_address = versioner.snapshot({"lanes": [], "residence": {}})

    with pytest.raises(ValueError, match="default lane"):
        research_set.restore_network(forged_address)

    # Live organization untouched: the default lane and residence survive.
    assert research_set.lane_names() == ["default"]
    assert research_set.residence_of("sha-a") == (
        research_set.default_lane.lane_id
    )
    research_set.cleanup()


def test_forced_cross_type_join_is_journaled_as_forced() -> None:
    """
    Regression (BUG-040): a clean experiment->development join that REQUIRED
    force=True (armed lane-type gate) journaled `forced: False` because the
    metadata recorded divergence only. Corrected behavior: the audit trail
    records that type policy was overridden.
    """
    research_set = ResearchSet("default")
    research_set.set_lane_type_enforcement(True)
    research_set.register_spell("sha-a")
    research_set.create_lane(
        "exp",
        attach_to="default",
        attach_at_spell_id="sha-a",
        lane_type="experiment",
    )
    research_set.register_spell(
        "sha-b", lane="exp", parent_spell_ids=["sha-a"],
    )

    with pytest.raises(RuntimeError, match="Type-mixing"):
        research_set.join("exp", into="default")
    research_set.join("exp", into="default", force=True)

    joined = [
        entry
        for entry in research_set.describe_composition()["journal"]["entries"]
        if entry["act"] == "joined"
    ]
    assert joined[-1]["metadata"]["forced"] is True
    research_set.cleanup()


def test_empty_campaign_stamp_refused_at_the_write_seam() -> None:
    """
    Regression (BUG-047): write paths accepted campaign="" while
    campaign_view("") rejects the same identifier - public writes created
    records the public query API could not address. Corrected behavior:
    every campaign-accepting verb refuses empty stamps up front.
    """
    research_set = ResearchSet("default")

    with pytest.raises(ValueError, match="non-empty"):
        research_set.register_spell("sha-a", campaign="")
    with pytest.raises(ValueError, match="non-empty"):
        research_set.record_world_entry("sha-b", campaign="")

    # Valid stamps still record and stay queryable.
    research_set.register_spell("sha-a", campaign="alpha")
    view = research_set.campaign_view("alpha")
    assert view["campaign"] == "alpha"
    assert [n["spell_id"] for n in view["nodes"]] == ["sha-a"]
    research_set.cleanup()


def test_public_lane_surface_cannot_bypass_set_invariants() -> None:
    """
    Regression (BUG-048): publicly returned lane objects exposed mutators
    (add_node, detach_nodes, set_anchor, mark_joined, mark_archived) that
    bypassed the set's residence claim, journal, snapshot callback, and
    persistence emission - the same identity could be added to multiple
    lanes with residence=None. Corrected behavior (owner ruling 2026-07-18,
    option a): lanes are read surfaces; every mutator is set-internal, so
    the public surface physically cannot construct a state the
    single-residence model forbids.
    """
    research_set = ResearchSet("default")
    research_set.register_spell("sha-a")
    research_set.create_lane(
        "side", attach_to="default", attach_at_spell_id="sha-a",
    )
    default_lane = research_set.default_lane
    node = default_lane.get_node("sha-a")

    for public_mutator in (
        "add_node", "detach_nodes", "set_anchor",
        "mark_joined", "mark_archived",
    ):
        with pytest.raises(AttributeError):
            getattr(default_lane, public_mutator)

    # The governed path still enforces single residence end to end.
    with pytest.raises(RuntimeError, match="Rediscovery"):
        research_set.register_spell("sha-a", lane="side")
    assert research_set.residence_of("sha-a") == default_lane.lane_id
    assert node.spell_id == "sha-a"
    research_set.cleanup()


def test_nested_metadata_mutation_cannot_bypass_publication_control() -> None:
    """
    Regression (BUG-039): metadata carriers copied only the OUTER dict, so
    mutating a nested object obtained from public metadata changed live
    describe() state with no lock, journal record, snapshot, or emission.
    Corrected behavior: metadata is deep-copied at intake and exposure -
    published state changes only through governed mutation.
    """
    research_set = ResearchSet("default")
    supplied = {"tags": ["alpha"], "grades": {"initial": 1}}
    node = research_set.register_spell("sha-a", metadata=supplied)

    # Caller-side mutation after intake never reaches the record.
    supplied["tags"].append("smuggled-in")
    exposed = node.metadata
    exposed["grades"]["initial"] = 999
    exposed["tags"].append("smuggled-out")

    fresh = node.metadata
    assert fresh["tags"] == ["alpha"]
    assert fresh["grades"] == {"initial": 1}
    described = node.describe()["metadata"]
    assert described["tags"] == ["alpha"]
    assert described["grades"] == {"initial": 1}
    research_set.cleanup()
