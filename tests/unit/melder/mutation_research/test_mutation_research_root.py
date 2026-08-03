import threading
import time
from unittest.mock import MagicMock

import pytest

from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_configuration_builder import (
    MutationResearchConfigurationBuilder,
)
from melder.mutation_research.mutation_research import MutationResearch
from melder.mutation_research.research_set.research_set import ResearchSet
from melder.aether.aether import Aether


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each root/config test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def _mock_aether(*, recording: bool = False) -> MagicMock:
    """
    Build one MagicMock Aether host for root unit tests.

    Args:
        recording:
            When True, the mocked crystallizer poses as live-and-recording so
            the emission seam proceeds; otherwise it poses as live but NOT
            recording (inactive), the only reachable custody-unavailable
            state - teardown states are unreachable mid-use by contract.

    Returns:
        MagicMock: Aether double carrying a crystallizer double.
    """
    aether = MagicMock()
    aether.cleaned = False
    aether._crystallizer.cleaned = False
    if recording:
        aether._crystallizer.activated = True
    else:
        aether._crystallizer.activated = False
    return aether


def test_mutation_research_configuration_defaults_validate() -> None:
    """
    Verify the default mutation-research configuration disables unrestricted mode.
    """
    configuration = MutationResearchConfiguration().with_defaults()

    assert configuration.get_property("unrestricted_module_mutations") is False
    assert configuration.validate() is True


def test_mutation_research_configuration_payload_is_value_typed() -> None:
    """
    Verify the shared twin-payload builder coerces non-plain values.
    """
    configuration = MutationResearchConfiguration().with_defaults()
    payload = configuration.describe_configuration_payload()

    assert payload["unrestricted_module_mutations"] is False
    for value in payload.values():
        assert value is None or isinstance(value, (str, int, float, bool))


def test_mutation_research_configuration_builder_activate_hands_off_configuration() -> None:
    """
    Verify the builder activates and hands off a configured object.
    """
    builder = MutationResearchConfigurationBuilder()
    configuration = builder.with_defaults().activate()

    assert configuration.activated is True
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        builder.build()


def test_mutation_research_root_configure_and_activate() -> None:
    """
    Verify the Aether-owned root follows the config/activate pattern.
    """
    root = MutationResearch(aether=_mock_aether())
    configuration = root.create_configuration().with_defaults().activate()

    root.configure(configuration)
    root.activate()

    assert root.is_configured is True
    assert root.is_activated is True
    assert root.configuration is configuration


def test_root_guarantees_default_research_set() -> None:
    """
    Verify the sets registry births with the guaranteed default set.
    """
    root = MutationResearch(aether=_mock_aether())

    assert root.list_research_set_names() == ["default"]
    default_set = root.research_set()
    assert isinstance(default_set, ResearchSet)
    assert default_set.lane_names() == ["default"]


def test_root_create_research_set_registers_unique_names() -> None:
    """
    Verify additional sets register by unique name and resolve back.
    """
    root = MutationResearch(aether=_mock_aether())
    created = root.create_research_set("side-campaign")

    assert root.research_set("side-campaign") is created
    assert root.list_research_set_names() == ["default", "side-campaign"]
    with pytest.raises(ValueError, match="already owns"):
        root.create_research_set("side-campaign")
    with pytest.raises(KeyError, match="Known sets"):
        root.research_set("missing")


def test_root_emits_composition_twin_when_recording() -> None:
    """
    Verify a set mutation re-emits the MutationResearchCrystal composition
    through the crystallizer sink while the root is active and recording.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)
    root.activate()
    aether._crystallizer.emit.reset_mock()

    root.research_set().register_spell("sha-a", author="mutation_0")

    assert aether._crystallizer.emit.call_count == 1
    twin = aether._crystallizer.emit.call_args.args[0]
    assert isinstance(twin, MutationResearchCrystal)
    composition = twin.composition_payload
    organization = composition["default"]["organization"]
    assert organization["residence"]["lane_id_by_spell_id"].keys() == {"sha-a"}


def test_root_emission_skips_while_inactive() -> None:
    """
    Verify set mutations emit nothing before root activation.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    aether._crystallizer.emit.reset_mock()

    root.research_set().register_spell("sha-a")

    assert aether._crystallizer.emit.call_count == 0


def test_root_load_recorded_composition_rebuilds_registry() -> None:
    """
    Verify the hydration seam replaces the registry from a recorded payload
    and keeps the default-set guarantee.
    """
    root = MutationResearch(aether=_mock_aether())
    root.research_set().register_spell("sha-a")
    root.create_research_set("side")
    recorded = root.describe_research_composition()

    root.load_recorded_composition({"side": recorded["side"]})

    assert root.list_research_set_names() == ["default", "side"]
    assert root.research_set().residence_of("sha-a") is None
    with pytest.raises(ValueError, match="dict"):
        root.load_recorded_composition("not-a-dict")


def test_root_record_world_entry_is_idempotent() -> None:
    """
    Verify the seam facade declares once and no-ops on rediscovery.
    """
    root = MutationResearch(aether=_mock_aether())

    assert root.record_world_entry("sha-a") is True
    assert root.record_world_entry("sha-a") is False
    assert root.record_world_entry("sha-b", staged=True) is True
    acts = [
        entry.act.value
        for entry in root.research_set().journal.entries()
    ]
    assert acts.count("registered") == 1
    assert acts.count("staged") == 1


def test_root_record_promotion_catches_up_unknown_targets() -> None:
    """
    Verify promotion of an undeclared identity declares it first (staged
    catch-up), then journals the promoted event.
    """
    root = MutationResearch(aether=_mock_aether())
    root.record_world_entry("sha-old")

    root.record_promotion("sha-old", "sha-new", actor="mutation_0")

    research_set = root.research_set()
    assert research_set.residence_of("sha-new") is not None
    acts = [entry.act.value for entry in research_set.journal.entries()]
    assert acts[-2:] == ["staged", "promoted"]
    last = research_set.journal.entries()[-1]
    assert last.from_spell_id == "sha-old" and last.to_spell_id == "sha-new"


def test_root_activation_hydrates_untouched_registry_from_record() -> None:
    """
    Verify the twin docking loop: an untouched root rebuilds its registry from
    the active profile's recorded composition at activation.
    """
    donor = ResearchSet("default")
    donor.register_spell("sha-recorded", author="past-life")
    recorded_composition = {"default": donor.describe_composition()}
    donor.cleanup()

    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "twin_kind": "mutation_research",
        "activated": True,
        "configuration_payload": {},
        "composition_payload": recorded_composition,
    }
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate()

    hydrated = root.research_set()
    assert hydrated.residence_of("sha-recorded") == (
        hydrated.default_lane.lane_id
    )


def test_root_activation_never_clobbers_live_research() -> None:
    """
    Verify an already-touched registry skips hydration: live research wins and
    re-records itself instead.
    """
    donor = ResearchSet("default")
    donor.register_spell("sha-recorded")
    recorded_composition = {"default": donor.describe_composition()}
    donor.cleanup()

    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "composition_payload": recorded_composition,
    }
    root = MutationResearch(aether=aether)
    root.research_set().register_spell("sha-live")
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate()

    live = root.research_set()
    assert live.residence_of("sha-live") is not None
    assert live.residence_of("sha-recorded") is None


def test_root_activation_hydration_opt_out() -> None:
    """
    Verify hydrate_from_record=False leaves even an untouched registry alone.
    """
    aether = _mock_aether(recording=True)
    aether._crystallizer.describe_mutation_research_record.return_value = {
        "composition_payload": {"default": {}},
    }
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)

    root.activate(hydrate_from_record=False)

    aether._crystallizer.describe_mutation_research_record.assert_not_called()


def test_root_diff_research_resolves_material_from_custody() -> None:
    """
    Verify diff_research pulls custody material through the crystallizer
    (crystal id == spell SHA) and dispatches the source strategy.
    """
    aether = _mock_aether(recording=True)
    aether._crystallizer.get_spell_crystal.return_value.describe.side_effect = [
        {
            "synthetic_module_sources": {"mod.a": {"source_text": "x = 1\n"}},
            "physical_module_fingerprints": {},
        },
        {
            "synthetic_module_sources": {"mod.a": {"source_text": "x = 2\n"}},
            "physical_module_fingerprints": {},
        },
    ]
    root = MutationResearch(aether=aether)

    verdict = root.diff_research("sha-left", "sha-right")

    assert verdict["strategy"] == "source"
    assert verdict["result"]["changed_modules"] == ["mod.a"]
    assert verdict["result"]["identical"] is False


def test_root_diff_research_refuses_dead_custody() -> None:
    """
    Verify diff material resolution stays loud when the crystallizer is not
    live (no fabricated empty material).
    """
    aether = _mock_aether()
    aether._crystallizer.cleaned = True
    root = MutationResearch(aether=aether)

    with pytest.raises(RuntimeError, match="custody is unavailable"):
        root.diff_research("sha-left", "sha-right")


def test_root_ambient_campaign_stamps_auto_records() -> None:
    """
    Verify the ambient campaign context stamps every root-facade record
    until cleared, and explicit stamps still win.
    """
    root = MutationResearch(aether=_mock_aether())
    root.set_active_campaign("apollo")

    root.record_world_entry("sha-a")
    root.record_promotion("sha-a", "sha-b")
    root.clear_active_campaign()
    root.record_world_entry("sha-c")
    root.record_world_entry("sha-d", campaign="artemis")

    entries = root.research_set().journal.entries()
    stamps = {
        entry.to_spell_id: entry.campaign
        for entry in entries
        if entry.to_spell_id is not None
    }
    assert stamps["sha-a"] == "apollo"
    assert stamps["sha-b"] == "apollo"
    assert stamps["sha-c"] is None
    assert stamps["sha-d"] == "artemis"
    assert root.active_campaign is None
    with pytest.raises(ValueError, match="campaign"):
        root.set_active_campaign("")


def test_root_residency_view_reports_runtime_and_custody_join() -> None:
    """
    Verify the query-time join: active/parked from live index membership,
    stored from custody, declared_only from the record, honest None custody
    when the crystallizer cannot answer.
    """
    aether = _mock_aether(recording=True)
    aether.cleaned = False
    index = MagicMock()
    index.cleaned = False
    index.id = "index-1"
    index.selected_spell_id = "sha-active"
    frame = MagicMock()
    frame.cleaned = False
    frame.find_index_for_spell.side_effect = (
        lambda sha: index if sha in ("sha-active", "sha-parked") else None
    )
    aether._aetheric_frames = {"default": frame}
    root = MutationResearch(aether=aether)
    root.record_world_entry("sha-active")
    root.record_world_entry("sha-parked")
    root.record_world_entry("sha-stored")

    active = root.residency_view("sha-active")
    parked = root.residency_view("sha-parked")
    stored = root.residency_view("sha-stored")
    ghost = root.residency_view("sha-ghost")

    assert active["runtime"] == "active"
    assert active["frame_name"] == "default"
    assert active["index_id"] == "index-1"
    assert parked["runtime"] == "parked"
    assert stored["runtime"] == "stored"
    assert stored["declared"] is True
    assert stored["lane_name"] == "default"
    assert ghost["runtime"] == "stored"
    assert ghost["declared"] is False


def test_root_residency_view_is_honest_without_custody() -> None:
    """
    Verify custody unavailability degrades to None/declared_only instead of
    raising (reads never fabricate).
    """
    aether = _mock_aether()
    aether.cleaned = False
    aether._crystallizer.cleaned = True
    frame = MagicMock()
    frame.cleaned = False
    frame.find_index_for_spell.return_value = None
    aether._aetheric_frames = {"default": frame}
    root = MutationResearch(aether=aether)
    root.record_world_entry("sha-a")

    view = root.residency_view("sha-a")

    assert view["in_custody"] is None
    assert view["runtime"] == "declared_only"
    unknown = root.residency_view("sha-ghost")
    assert unknown["runtime"] == "unknown"
    with pytest.raises(ValueError, match="spell_id"):
        root.residency_view("")


def test_root_cleanup_cascades_into_sets() -> None:
    """
    Verify root cleanup cascades into every owned research set.
    """
    root = MutationResearch(aether=_mock_aether())
    default_set = root.research_set()
    root.cleanup()

    assert root.cleaned is True
    assert default_set.cleaned is True
    with pytest.raises(RuntimeError):
        root.research_set()


def _fake_frame(index_id: str, selected_spell_id: str) -> MagicMock:
    """
    Build one live frame double whose index scan answers a fixed index.

    Args:
        index_id:
            Index id the frame reports for any queried spell.
        selected_spell_id:
            The index's currently selected member.

    Returns:
        MagicMock: Frame double for `_locate_live_membership` scans.
    """
    index = MagicMock()
    index.cleaned = False
    index.id = index_id
    index.selected_spell_id = selected_spell_id
    frame = MagicMock()
    frame.cleaned = False
    frame.find_index_for_spell.return_value = index
    return frame


def test_residency_view_prefers_selected_membership_in_later_frame() -> None:
    """
    Regression (BUG-032): the live-membership scan returned the FIRST frame
    membership found, so a spell parked in an earlier-iterated frame and
    selected in a later one reported a false `parked` posture. Corrected
    behavior: a selected membership anywhere wins (active-if-any).
    """
    spell_id = "s" * 64
    aether = _mock_aether(recording=True)
    aether.cleaned = False
    aether._aetheric_frames = {
        "frame_parked": _fake_frame("idx-parked", selected_spell_id="other"),
        "frame_active": _fake_frame("idx-active", selected_spell_id=spell_id),
    }
    root = MutationResearch(aether=aether)

    view = root.residency_view(spell_id)

    assert view["runtime"] == "active"
    assert view["frame_name"] == "frame_active"
    assert view["index_id"] == "idx-active"


def test_residency_view_still_reports_parked_when_nothing_selects() -> None:
    """
    Guard against over-correction: with live memberships but no selection
    anywhere, the first live membership still reports `parked`.
    """
    spell_id = "s" * 64
    aether = _mock_aether(recording=True)
    aether.cleaned = False
    aether._aetheric_frames = {
        "frame_one": _fake_frame("idx-one", selected_spell_id="other"),
        "frame_two": _fake_frame("idx-two", selected_spell_id="another"),
    }
    root = MutationResearch(aether=aether)

    view = root.residency_view(spell_id)

    assert view["runtime"] == "parked"
    assert view["frame_name"] == "frame_one"
    assert view["index_id"] == "idx-one"


class _GatedRecordingCrystallizer:
    """
    Crystallizer double that can hold ONE emission at the publish boundary.

    Purpose:
        Deterministic stand-in for a free-threaded preemption between the
        emission seam's snapshot build and its record: the first emit after
        arming parks at the boundary until released, while every recorded
        composition's node count is captured in arrival order.
    """

    def __init__(self) -> None:
        self.cleaned = False
        self.activated = True
        self.recorded_node_counts: list = []
        self.hold_next_emit = False
        self.parked_in_emit = threading.Event()
        self.release_gate = threading.Event()
        self._lock = threading.Lock()

    def _composition_node_count(self, crystal) -> int:
        total = 0
        payload = crystal.composition_payload or {}
        for set_payload in payload.values():
            for lane in set_payload["organization"]["lanes"]:
                total += len(lane["nodes"])
        return total

    def emit(self, crystal) -> None:
        hold = False
        with self._lock:
            if self.hold_next_emit:
                self.hold_next_emit = False
                hold = True
        if hold:
            self.parked_in_emit.set()
            assert self.release_gate.wait(timeout=10.0), (
                "emission gate never released"
            )
        with self._lock:
            self.recorded_node_counts.append(
                self._composition_node_count(crystal)
            )

    def emit_mutation_research_state(self, state) -> None:
        pass

    def describe_mutation_research_record(self):
        return None


def test_emission_never_publishes_stale_composition_over_newer_one() -> None:
    """
    Regression (BUG-031): the emission seam built its snapshot and published
    with no serialization, so an emitter paused before its record let a
    second thread commit AND publish a newer composition first - the paused
    thread then replaced it with the stale snapshot, silently dropping the
    newest research record from persistence. Corrected behavior: snapshot
    build + publication are atomic under the emission lock, so recorded
    compositions never move backwards.
    """
    crystallizer = _GatedRecordingCrystallizer()
    aether = MagicMock()
    aether.cleaned = False
    aether._aetheric_frames = {}
    aether._crystallizer = crystallizer
    root = MutationResearch(aether=aether)
    root.configure(root.create_configuration().with_defaults().activate())
    root.activate()
    crystallizer.recorded_node_counts.clear()
    crystallizer.hold_next_emit = True

    def register_first() -> None:
        root.research_set().register_spell("a" * 64)

    def register_second() -> None:
        root.research_set().register_spell("b" * 64)

    first = threading.Thread(target=register_first)
    first.start()
    assert crystallizer.parked_in_emit.wait(timeout=10.0)
    second = threading.Thread(target=register_second)
    second.start()
    time.sleep(0.5)  # window where unserialized emission would publish
    published_during_hold = bool(crystallizer.recorded_node_counts)
    crystallizer.release_gate.set()
    first.join(timeout=10.0)
    second.join(timeout=10.0)

    assert not first.is_alive() and not second.is_alive()
    # Serialization: nothing may publish while the first emission is parked.
    assert published_during_hold is False
    # Monotone replace-on-emit: durable composition never moves backwards.
    counts = crystallizer.recorded_node_counts
    assert counts == sorted(counts)
    # The final record carries the full live composition (both spells).
    assert counts[-1] == 2


def test_activation_completes_hydration_before_reporting_active() -> None:
    """
    Regression (BUG-035): `activate()` flipped `_activated` (opening the
    public ingress) BEFORE the untouched-check/hydration sequence, so a live
    entry recorded through the already-open ingress could be clobbered by
    the registry swap. Corrected behavior: hydration completes before the
    root ever reports active, so the documented seam (ingress opens at
    activation) cannot race the swap.
    """
    observed_active_during_hydration: list = []
    root_box: list = []

    crystallizer = MagicMock()
    crystallizer.cleaned = False
    crystallizer.activated = True

    def record_probe():
        observed_active_during_hydration.append(root_box[0].is_activated)
        return {
            "composition_payload": {
                "default": ResearchSet("default").describe_composition(),
            },
        }

    crystallizer.describe_mutation_research_record.side_effect = record_probe
    aether = MagicMock()
    aether.cleaned = False
    aether._crystallizer = crystallizer
    root = MutationResearch(aether=aether)
    root_box.append(root)
    root.configure(root.create_configuration().with_defaults().activate())

    root.activate()

    assert observed_active_during_hydration == [False]
    assert root.is_activated is True
    # Post-activation ingress works normally on the hydrated registry.
    assert root.record_world_entry("c" * 64) is True


def test_cleanup_completes_cascade_when_state_sink_raises() -> None:
    """
    Regression (BUG-036): root cleanup marked `_cleaned=True`, then called
    the state-emission sink unguarded - a raising sink aborted child
    cleanup and singleton reset, and every retry early-returned on the
    cleaned flag, leaving the cascade permanently half-complete. Corrected
    behavior: the sink is best-effort; a raising observer never stops the
    cascade or the singleton reset.
    """
    crystallizer = MagicMock()
    crystallizer.cleaned = False
    crystallizer.activated = True
    crystallizer.emit_mutation_research_state.side_effect = RuntimeError(
        "sink down"
    )
    aether = MagicMock()
    aether.cleaned = False
    aether._crystallizer = crystallizer
    root = MutationResearch(aether=aether)
    default_set = root.research_set()

    root.cleanup()

    assert root.cleaned is True
    assert default_set.cleaned is True
    assert MutationResearch._instance is None
    assert MutationResearch._initialized is False


def test_promotion_catchup_consumes_staged_ancestry_for_its_candidate() -> None:
    """
    Regression (BUG-049): promotion's world-entry catch-up declared the
    candidate directly through the set, bypassing the root's one-shot
    staged-ancestry consumption - the promoted candidate landed parentless
    while the stamp stayed armed and leaked onto the next unrelated world
    entry. Corrected behavior: catch-up routes through the root world-entry
    verb, so staged ancestry rides the candidate it was staged to describe.
    """
    aether = _mock_aether(recording=True)
    aether.cleaned = False
    root = MutationResearch(aether=aether)
    base = "a" * 64
    donor = "b" * 64
    candidate = "c" * 64
    unrelated = "d" * 64
    root.record_world_entry(base)
    root.record_world_entry(donor)
    root.stage_ancestry([base, donor])

    root.record_promotion(None, candidate)
    root.record_world_entry(unrelated)

    research_set = root.research_set()
    candidate_node = research_set.default_lane.get_node(candidate)
    unrelated_node = research_set.default_lane.get_node(unrelated)
    assert candidate_node.parent_spell_ids == [base, donor]
    assert unrelated_node.parent_spell_ids == []


def test_composition_diff_refuses_unknown_strategy() -> None:
    """
    Regression (BUG-044): diff_research on two compositions dropped the
    caller's strategy and silently routed to the `members` default, so
    `strategy='definitely-missing'` returned a normal members diff.
    Corrected behavior: the documented unknown-strategy KeyError applies
    to the composition branch too, and the per-kind defaults survive.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    base = "a" * 64
    donor = "b" * 64
    root.record_world_entry(base)
    root.record_world_entry(donor)
    research_set = root.research_set()
    left = research_set.register_group([base])
    right = research_set.register_group([base, donor])

    with pytest.raises(KeyError, match="definitely-missing"):
        root.diff_research(
            left.group_id, right.group_id, strategy="definitely-missing",
        )
    # Default routing still works for compositions.
    verdict = root.diff_research(left.group_id, right.group_id)
    assert verdict["strategy"] == "members"
    assert verdict["result"]["added_members"] == [donor]


def test_group_diff_never_fabricates_moves_for_unrelated_identities() -> None:
    """
    Regression (BUG-046): same-lane pairing treated two UNRELATED
    auto-recorded identities sharing the catch-all default lane as one
    object at two versions (`version_moved=[A -> B]`). Corrected behavior:
    a move requires a real ancestry relation; unrelated identities report
    as honest removals/additions.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    unrelated_a = "a" * 64
    unrelated_b = "b" * 64
    root.record_world_entry(unrelated_a)
    root.record_world_entry(unrelated_b)
    research_set = root.research_set()
    left = research_set.register_group([unrelated_a])
    right = research_set.register_group([unrelated_b])

    verdict = root.group_diff_research(left.group_id, right.group_id)

    assert verdict["result"]["version_moved"] == []
    assert verdict["result"]["removed_members"] == [unrelated_a]
    assert verdict["result"]["added_members"] == [unrelated_b]


def test_group_diff_pairs_true_version_moves() -> None:
    """
    Guard against over-correction: a member replaced by its recorded
    descendant on the same lane still pairs as a version move.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    base = "a" * 64
    descendant = "b" * 64
    root.record_world_entry(base)
    research_set = root.research_set()
    research_set.register_spell(descendant, parent_spell_ids=[base])
    left = research_set.register_group([base])
    right = research_set.register_group([descendant])

    verdict = root.group_diff_research(left.group_id, right.group_id)

    moves = verdict["result"]["version_moved"]
    assert len(moves) == 1
    assert moves[0]["from_spell_id"] == base
    assert moves[0]["to_spell_id"] == descendant
    assert verdict["result"]["added_members"] == []
    assert verdict["result"]["removed_members"] == []


def test_group_ancestry_relation_walks_transitive_parents() -> None:
    """
    Regression (BUG-045): `ancestry_related` checked only DIRECT parents,
    so G1 -> G2 -> G3 reported `group_diff_research(G1, G3)` unrelated.
    Corrected behavior: the documented parent-chain relationship includes
    transitive ancestry.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    first = "a" * 64
    second = "b" * 64
    third = "c" * 64
    for sha in (first, second, third):
        root.record_world_entry(sha)
    research_set = root.research_set()
    g1 = research_set.register_group([first])
    g2 = research_set.register_group(
        [first, second], parent_group_ids=[g1.group_id],
    )
    g3 = research_set.register_group(
        [first, second, third], parent_group_ids=[g2.group_id],
    )

    verdict = root.group_diff_research(g1.group_id, g3.group_id)

    assert verdict["result"]["ancestry_related"] is True


def test_unrelated_default_lane_spell_cannot_revoke_composition() -> None:
    """
    Regression (BUG-150): current-composition discovery probed the raw lane
    tip, so an unrelated ordinary spell registered later on the shared
    default lane displaced a still-resident composition out of
    `compositions_of` (the reverse lift went empty). Corrected behavior:
    each lane's LATEST composition record stays current regardless of later
    ordinary entries.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    member = "a" * 64
    unrelated = "b" * 64
    root.record_world_entry(member)
    group = root.research_set().register_group([member])
    assert [
        entry["group_id"] for entry in root.compositions_of(member)
    ] == [group.group_id]

    root.record_world_entry(unrelated)  # later unrelated default-lane spell

    assert [
        entry["group_id"] for entry in root.compositions_of(member)
    ] == [group.group_id]


def test_rejected_world_entry_restores_staged_ancestry() -> None:
    """
    Regression (BUG-151): record_world_entry cleared the one-shot ancestry
    stamp BEFORE set validation and restored it only for rediscovery, so a
    pre-commit refusal (unresident parent) destroyed the synthesized
    lineage - the corrected retry minted the candidate parentless.
    Corrected behavior: any pre-commit failure re-arms the stamp; the first
    SUCCESSFUL declaration consumes it.
    """
    aether = _mock_aether(recording=True)
    root = MutationResearch(aether=aether)
    parent = "a" * 64
    candidate = "b" * 64
    root.stage_ancestry([parent])  # parent not resident yet

    with pytest.raises(ValueError, match="not resident"):
        root.record_world_entry(candidate)

    # The stamp survived the refusal: declare the parent through the SET
    # surface (root consumption is one-shot-any-declaration by design),
    # then the retried candidate mints the intended lineage.
    root.research_set().register_spell(parent)
    assert root.record_world_entry(candidate) is True
    node = root.research_set().default_lane.get_node(candidate)
    assert node.parent_spell_ids == [parent]


# ---------------------------------------------------------------------------
# Single access: MutationResearch now behaves exactly like its two siblings
# ---------------------------------------------------------------------------

def test_a_hostless_first_construction_is_refused() -> None:
    """
    The host is REQUIRED, and the refusal is a `ValueError` raised by the
    BODY - not a `TypeError` from the signature.

    That distinction is the whole point. A signature error fires before
    `__init__` runs, so the rollback below could never execute and the bare
    lookup in the next row could never work either. Crystallizer and Nexus
    have always been shaped this way; MutationResearch joined them
    2026-08-03.
    """
    MutationResearch._reset_singleton_for_tests()

    with pytest.raises(ValueError, match="Aether must be provided"):
        MutationResearch()


def test_a_refused_construction_leaves_no_husk() -> None:
    """
    Regression (2026-08-03): `__new__` publishes `cls._instance` before
    `__init__` runs, so a refused construction used to leave the singleton
    pointing at an object whose `_cleaned` slot was never assigned. Every
    later `_reset_singleton_for_tests()` then raised AttributeError - one bad
    call took out 38 unrelated rows in the UX/AIX expert suite.
    """
    MutationResearch._reset_singleton_for_tests()

    with pytest.raises(ValueError):
        MutationResearch()

    assert MutationResearch._instance is None
    assert MutationResearch._initialized is False
    MutationResearch._reset_singleton_for_tests()  # must not raise


def test_a_bare_call_is_the_single_access_door() -> None:
    """
    THE POINT OF THE WHOLE CHANGE. Once Aether has built the root, a bare
    `MutationResearch()` returns it - no host argument, no accessor hop -
    exactly like `Crystallizer()` and `Nexus()`.

    In a real process this is always the case: `Aether()` runs at package
    import and constructs all three hosted roots eagerly.
    """
    root = MutationResearch(aether=_mock_aether())

    assert MutationResearch() is root


def test_a_second_construction_is_a_lookup_that_ignores_its_host() -> None:
    """
    Documented contract: later constructions return early, so arguments are
    SILENTLY IGNORED. Passing a different Aether does not rebind the root.
    """
    first_host = _mock_aether()
    root = MutationResearch(aether=first_host)

    same_root = MutationResearch(aether=_mock_aether())

    assert same_root is root
    assert root._aether is first_host


def test_the_host_is_keyword_only() -> None:
    """
    `aether` is keyword-only on all three roots. Pinning the shape keeps
    them interchangeable to a reader.
    """
    MutationResearch._reset_singleton_for_tests()

    with pytest.raises(TypeError):
        MutationResearch(_mock_aether())

    # A signature TypeError fires before `__init__` runs, so the body's
    # rollback never executes and `__new__`'s published instance is left
    # installed. The class's own reset door is what clears it - never a
    # direct poke at `_instance` / `_initialized`.
    MutationResearch._reset_singleton_for_tests()
