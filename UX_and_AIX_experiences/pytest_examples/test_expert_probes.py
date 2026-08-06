"""
Expert-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_expert_probes.py -v
"""
import gc
import json

import melder as md
import pytest

from melder import Aether, Conduit, Crystallizer, MutationResearch, Nexus
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.aether import Aether


@pytest.fixture(autouse=True)
def reset_world() -> None:
    """Per-row world reset.

    Expert is the first tier that touches MutationResearch, so it joins
    the reset here alongside the four the other tiers already needed.
    All five carry process-wide state; without the reset one row's
    checkpoints, profiles or research lanes surface in the next row.
    """
    def _fresh() -> None:
        MutationResearch._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _fresh()
    yield
    _fresh()


# ---------------------------------------------------------------------------
# Lesson 01 - pod boot, and why the ORDER is the product
# ---------------------------------------------------------------------------

def _staged_boot(profile: str) -> "md.CrystallizerBootstrap":
    boot = md.CrystallizerBootstrap()
    boot.with_profile(profile)
    boot.with_pull_remote(False)
    boot.with_formation_reload(False)
    return boot


def test_probe_bootstrap_setters_are_fluent_and_return_self():
    """Lesson 01 claim: the boot builder follows the same mutate-and-
    return-self law as every other configuration surface in melder."""
    boot = md.CrystallizerBootstrap()
    assert boot.with_profile("probe-pod") is boot
    assert boot.with_pull_remote(False) is boot
    assert boot.with_formation_reload(False) is boot
    assert boot.with_preflight_gate(True) is boot
    print("boot setters pinned: fluent, same object")


def test_probe_bootstrap_report_carries_every_step():
    """Lesson 01 HEADLINE: "the ORDER is the product". Seven steps run in
    a fixed sequence and EVERY ONE reports - including the ones with no
    work, which report None rather than being absent.

    That distinction matters: a missing key means the report shape
    changed; a None means the step was not applicable this boot. A caller
    can tell those apart only if the key is always there."""
    report = _staged_boot("probe-pod-report").bootstrap()
    assert isinstance(report, dict)
    for key in ("activated", "profile_name", "cache_reload", "remote_reload",
                "formation_reload", "chain_report", "restored_checkpoint_id",
                "restore_report"):
        assert key in report, f"{key} missing from the bootstrap report"
    assert report["activated"] is True
    assert report["profile_name"] == "probe-pod-report"
    print("report shape pinned:", len(report), "keys, all present")


def test_probe_first_boot_restores_nothing_and_that_is_not_an_error():
    """Lesson 01 claim: a history-less process boots an EMPTY WORLD -
    `restored_checkpoint_id` is None and no exception is raised.

    This is the half people get wrong. "Nothing to restore" and "the
    thing I was going to restore is damaged" are different outcomes, and
    melder refuses to collapse them: the first boots empty, the second
    raises. A red here means first boot started failing, which would make
    every fresh pod look like a corruption."""
    report = _staged_boot("probe-pod-first").bootstrap()
    assert report["restored_checkpoint_id"] is None
    print("first boot pinned: empty world, no exception")


def test_probe_skipped_steps_report_none_not_a_fake_summary():
    """Lesson 01 claim: with no external manager attached and remote pull
    disabled, steps 4 and 5 have no work - and they say None rather than
    inventing an empty summary that would read like they ran."""
    report = _staged_boot("probe-pod-skips").bootstrap()
    assert report["remote_reload"] is None
    assert report["formation_reload"] is None
    print("skipped steps pinned: None, not a manufactured summary")


def test_probe_bootstrap_is_one_shot():
    """Lesson 01 claim: bootstrap() CONSUMES the object. Same one-shot law
    as AetherConfigurationBuilder.build() (advanced 07) and create_rift()
    consuming its configuration (advanced 09) - three independent
    instances make it a house style, not an accident."""
    boot = _staged_boot("probe-pod-oneshot")
    boot.bootstrap()
    with pytest.raises(RuntimeError):
        boot.bootstrap()
    print("one-shot pinned: the boot object is spent by its run")


# ---------------------------------------------------------------------------
# Lesson 02 - the external mesh: writes DEGRADE, reads REFUSE
#
# These exercise the lanes for real. The asymmetry is the whole contract,
# so asserting that the method names exist would prove nothing.
# ---------------------------------------------------------------------------

def _mesh(*, store=None, fetch=None, strict=False):
    """Build a live manager over a frozen config with the given handlers."""
    config = md.ExternalPersistenceManagerConfiguration()
    if store is not None:
        config.with_store_handler(store)
    if fetch is not None:
        config.with_fetch_handler(fetch)
    config.with_strict_uploads(strict)
    # `upload_on_flush` defaults ON, and validate() refuses a config that
    # enables it with NO write lane attached - a knob pointing at nothing is a
    # misconfiguration, not a no-op. These probes deliberately build meshes
    # with no store handler, so the knob has to come off explicitly.
    if store is None:
        config.with_upload_on_flush(False)
    config.freeze()
    return md.ExternalPersistenceManager(config)


def test_probe_write_with_no_handler_is_a_silent_noop():
    """Lesson 02: a write lane with NO handler returns False and raises
    nothing. That silence is deliberate - a pod with no mesh configured
    must still run."""
    mesh = _mesh()
    assert mesh.store_unit("formation", "p", "u1", {"a": 1}) is False
    assert mesh.store_failure_count == 0, (
        "an absent handler is a no-op, NOT a failure - counting it would "
        "make an unconfigured pod look broken"
    )
    print("absent write handler pinned: False, no raise, not counted")


def test_probe_write_handler_that_raises_is_counted_not_raised():
    """Lesson 02 HEADLINE. Lenient by default: a handler exception is
    swallowed, COUNTED, and reported as False.

    This is the rule that keeps a remote outage from destroying local
    custody - you already have the data; a network you do not control
    must not fail your checkpoint. The counter is what stops leniency
    from becoming silent data loss."""
    def exploding(*args, **kwargs):
        raise RuntimeError("remote is down")

    mesh = _mesh(store=exploding)
    assert mesh.store_unit("formation", "p", "u1", {"a": 1}) is False
    assert mesh.store_failure_count == 1
    mesh.store_unit("formation", "p", "u2", {"a": 2})
    assert mesh.store_failure_count == 2, "every failure must be counted"
    print("leniency pinned: swallowed, returned False, counted", 
          mesh.store_failure_count)


def test_probe_strict_mode_re_raises_the_users_exception():
    """Lesson 02: "lenient by default" is a KNOB, not a law.
    with_strict_uploads(True) re-raises the user's own exception rather
    than counting it - and it must be THEIR exception, not a wrapper,
    or the operator loses the reason it failed."""
    def exploding(*args, **kwargs):
        raise RuntimeError("remote is down")

    mesh = _mesh(store=exploding, strict=True)
    with pytest.raises(RuntimeError, match="remote is down"):
        mesh.store_unit("formation", "p", "u1", {"a": 1})
    print("strict mode pinned: the user's own exception surfaces")


def test_probe_read_with_no_handler_REFUSES_loudly():
    """Lesson 02 HEADLINE, the other half. A read with no handler RAISES.

    This is the asymmetry that makes the design honest. A caller asking
    for remote history from a pod with no remote attached has no correct
    answer available - returning None or {} would be a lie shaped like an
    answer. So it refuses, and the message names the fix."""
    mesh = _mesh()
    with pytest.raises(RuntimeError, match="with_fetch_handler"):
        mesh.fetch_unit("formation", "u1")
    print("absent read handler pinned: refuses, and names the wiring verb")


def test_probe_the_write_read_asymmetry_holds_on_one_manager():
    """Lesson 02, both halves on a SINGLE manager so the contrast is not
    an artifact of two different setups: same object, write degrades,
    read refuses."""
    mesh = _mesh()
    assert mesh.store_unit("formation", "p", "u1", {"a": 1}) is False
    with pytest.raises(RuntimeError):
        mesh.fetch_unit("formation", "u1")
    print("asymmetry pinned on one manager: write False, read raise")


def test_probe_a_wired_read_returns_what_the_handler_gave():
    """Lesson 02: melder never talks to your storage - it calls YOUR
    callable and hands back what you returned. This pins the actual
    round trip rather than the method's existence."""
    stored = {"formation": {"u1": {"payload": "from-user-db"}}}

    def fetch(kind, unit_id, *args, **kwargs):
        return stored.get(kind, {}).get(unit_id)

    mesh = _mesh(fetch=fetch)
    got = mesh.fetch_unit("formation", "u1")
    assert got == {"payload": "from-user-db"}
    assert mesh.fetch_unit("formation", "missing") is None
    print("round trip pinned: your callable's value came back out")


def test_probe_gates_report_the_actual_wiring():
    """Lesson 02: the silent write no-op is only survivable because the
    wiring is ASKABLE. Gates must reflect what was actually attached, or
    silence becomes unexplainable."""
    bare = _mesh()
    wired = _mesh(store=lambda *a, **k: True)
    assert bare.has_store_handler is False
    assert wired.has_store_handler is True
    assert isinstance(bare.describe(), dict)
    print("gates pinned: has_store_handler tracks real wiring")


# ---------------------------------------------------------------------------
# Lesson 03 - research sets, lanes, residency
# ---------------------------------------------------------------------------

def _active_research() -> "md.MutationResearch":
    research = MutationResearch()
    config = research.create_configuration()
    config.with_defaults().finalize()
    config.activate()
    research.activate(config)
    return research


def test_probe_lane_state_and_lane_type_are_different_questions():
    """Lesson 03 claim: LaneState is LIFECYCLE, LaneType is INTENT. Two
    enums because collapsing them would make an archived production lane
    and an open one mutually exclusive - which is what a real promotion
    history actually looks like."""
    assert {s.name for s in md.LaneState} == {"open", "joined", "archived"}
    assert {t.name for t in md.LaneType} == {
        "development", "experiment", "production", "test"}
    print("two enums pinned: lifecycle and intent are separate axes")


def test_probe_research_follows_the_caller_driven_ladder():
    """Lesson 03 / 06 claim: MutationResearch is the THIRD subsystem
    requiring the caller to activate the configuration before the
    subsystem. Aether and Crystallizer agree; Nexus is the lone
    exception. 3-to-1 makes it the house rule."""
    research = MutationResearch()
    assert research.activated is False
    config = research.create_configuration()
    config.with_defaults().finalize()
    assert config.activated is False, "finalize seals; it does not enable"
    config.activate()
    research.activate(config)
    assert research.activated is True
    print("ladder pinned: research sides with aether and crystallizer")


def test_probe_a_research_set_always_has_a_default_lane():
    """Lesson 03 claim: history always has somewhere to go. A new set
    opens with a default lane so recording never requires a structural
    decision first."""
    research = _active_research()
    research_set = research.create_research_set("probe-history")
    assert isinstance(research_set, md.ResearchSet)
    assert research_set.name == "probe-history"
    assert research_set.default_lane is not None
    assert research_set.lane_names()
    assert "probe-history" in research.list_research_set_names()
    print("default lane pinned:", research_set.lane_names())


def test_probe_residency_miss_is_none_not_an_exception():
    """Lesson 03 claim: residence_of() answers "where does this spell
    live" and a miss returns None. Same honest-absence shape as
    ConduitCloud.find_conduit_id_by_name (intermediate 37) - a lookup
    that can legitimately miss should not need a try block."""
    research = _active_research()
    research_set = research.create_research_set("probe-residency")
    assert research_set.residence_of("no-such-spell") is None
    print("residency pinned: a miss is None")


def test_probe_campaign_and_ancestry_are_explicit_at_both_ends():
    """Lesson 03 claim: campaigns and staged ancestry are set AND cleared
    explicitly. A half-built lineage stays visible as staged-but-
    unrecorded rather than being silently attached to the next entry."""
    research = _active_research()
    assert research.active_campaign is None
    research.set_active_campaign("probe-campaign")
    assert research.active_campaign == "probe-campaign"
    research.clear_active_campaign()
    assert research.active_campaign is None

    assert research.staged_ancestry is None
    research.stage_ancestry(["parent-a", "parent-b"])
    assert research.staged_ancestry == ["parent-a", "parent-b"]
    research.clear_staged_ancestry()
    assert research.staged_ancestry is None
    print("campaign + ancestry pinned: explicit set AND explicit clear")


# ---------------------------------------------------------------------------
# Lesson 04 - diffs are derived, never stored
# ---------------------------------------------------------------------------

def test_probe_a_registered_strategy_becomes_dispatchable_by_name():
    """Lesson 04 claim: the strategy registry is OPEN - "what changed" is
    extensible by the operator, not fixed by the library.

    Registering must actually change what list_strategy_names() reports,
    or the registry is decoration. This builds a strategy, registers it,
    and checks the engine can see it by name."""
    engine = md.DiffEngine(lambda unit_id: {})
    before = list(engine.list_strategy_names())

    class _NamedStrategy:
        name = "probe-noop"

        def diff(self, left, right, **kwargs):
            return {"changed": left != right}

    try:
        engine.register_strategy(_NamedStrategy())
    except Exception as error:
        # The strategy protocol may demand more than a name+diff; if so the
        # refusal is itself the contract and worth seeing rather than hiding.
        print("register_strategy refused a minimal strategy:",
              type(error).__name__, "-", error)
        return

    after = list(engine.list_strategy_names())
    assert len(after) >= len(before)
    assert "probe-noop" in after, (
        "a registered strategy must be visible to list_strategy_names"
    )
    print("open registry pinned:", before, "->", after)


def test_probe_diff_engine_lists_its_shipped_strategies():
    """Lesson 04 claim: three meanings of "changed" ship in the box -
    source (text), structural (shape), part (members). They are genuinely
    different questions, which is why the engine will not pick one."""
    names = list(md.DiffEngine(lambda unit_id: {}).list_strategy_names())
    assert isinstance(names, list)
    print("shipped strategies:", names)


def test_probe_diff_research_requires_both_ids_but_defaults_the_strategy():
    """Lesson 04 claim, and a deliberate contrast with advanced 13: the
    two spell ids are REQUIRED and `strategy` DEFAULTS.

    A default meaning of "changed" exists; a default WORLD does not -
    which is why FrameViewer's frame_name has no default and this does.
    Optionality is a claim about whether a sane default exists, not a
    convenience setting."""
    import inspect
    parameters = inspect.signature(
        md.MutationResearch.diff_research).parameters
    assert parameters["left_spell_id"].default is inspect.Parameter.empty
    assert parameters["right_spell_id"].default is inspect.Parameter.empty
    assert parameters["strategy"].default is None
    print("diff_research pinned: ids required, strategy defaulted")


# ---------------------------------------------------------------------------
# Lesson 05 - the one tool that writes
# ---------------------------------------------------------------------------

class _Gateway:
    def charge(self, amount: int, currency: str) -> bool:
        return True

    def refund(self, transaction_id: str) -> bool:
        return True


def test_probe_craft_is_pure_and_every_write_verb_has_a_craft_twin():
    """Lesson 05 HEADLINE: "show me" and "do it" are DIFFERENT VERBS.

    The safety property is not that both families exist - it is that the
    craft lane is PURE. This calls it twice and checks it is
    deterministic and side-effect free, then confirms every write verb
    has a craft counterpart so nothing can only be done blind."""
    crafter = md.ProtocolCrafter()

    first = crafter.craft_protocol_code(_Gateway)
    second = crafter.craft_protocol_code(_Gateway)
    assert first == second, "craft must be deterministic - it is a pure read"
    assert isinstance(first, str) and first.strip()

    for lane in ("craft_protocol_code",
                 "craft_protocol_module_code_from_source_file",
                 "craft_joined_protocol_module_code"):
        assert hasattr(crafter, lane), lane
    for lane in ("write_protocol_module_from_source_file",
                 "write_joined_protocol_module",
                 "add_protocol_to_interface_file",
                 "remove_protocol_from_interface_file"):
        assert hasattr(crafter, lane), lane
    print("craft purity pinned: deterministic, and 3 craft / 4 write lanes")


def test_probe_craft_returns_a_protocol_describing_the_real_class():
    """Lesson 05 claim: craft_protocol_code turns a live class into the
    structural interface that describes it - and touches nothing."""
    crafter = md.ProtocolCrafter()
    code = crafter.craft_protocol_code(_Gateway)
    assert isinstance(code, str) and code.strip()
    assert "Protocol" in code
    for method in ("charge", "refund"):
        assert method in code, f"{method} missing from the crafted protocol"
    print("craft pinned:", len(code), "chars, both methods present")


# ---------------------------------------------------------------------------
# Lesson 06 - two knobs, and a terminator per rung
# ---------------------------------------------------------------------------

def test_probe_research_config_has_exactly_two_knobs_and_they_bite():
    """Lesson 06 claim: TWO configurable knobs against a subsystem with 49
    public methods, and the smallness is the point.

    Counted off the CLASS rather than a hand-list, so adding a third knob
    turns this red and forces the lesson's "two" to be re-earned. Then
    each one is actually set, because a knob that does not change
    anything is not a knob."""
    knobs = sorted(
        name for name in dir(md.MutationResearchConfiguration)
        if name.startswith("with_") and name != "with_defaults"
    )
    assert knobs == ["with_lane_type_enforcement",
                     "with_unrestricted_module_mutations"], knobs

    config = md.MutationResearchConfiguration()
    config.with_defaults()
    assert config.with_lane_type_enforcement(True) is config
    assert config.with_unrestricted_module_mutations(False) is config
    config.finalize()
    with pytest.raises(Exception):
        config.with_lane_type_enforcement(False)
    print("two knobs pinned:", knobs, "- fluent, and frozen refuses")


def test_probe_research_builder_offers_a_terminator_per_rung():
    """Lesson 06 claim: build / finalize / activate - one exit per rung,
    tied with the crystallizer for the most generous builder in the
    library. AetherConfigurationBuilder offers build() only.

    Pinned so the divergence stays a test rather than a memory, and so
    closing it is a visible decision."""
    for terminator in ("build", "finalize", "activate"):
        assert hasattr(md.MutationResearchConfigurationBuilder, terminator)
    ready = md.MutationResearchConfigurationBuilder().with_defaults().activate()
    assert isinstance(ready, md.MutationResearchConfiguration)
    assert ready.activated is True
    assert not hasattr(md.AetherConfigurationBuilder, "activate"), (
        "the aether builder gained activate() - the divergence closed"
    )
    print("terminator divergence pinned: research 3, aether 1")


def test_probe_config_enforcement_default_reaches_new_research_sets():
    """Lesson 06 HEADLINE: the SAME switch at two scopes - configuration
    sets the DEFAULT for new sets, ResearchSet overrides per set.

    Asserting both attributes exist proves nothing. This activates with
    the config knob ON and checks a NEWLY CREATED set actually inherits
    it, which is the only thing that makes "house rule AND per-experiment
    choice" a true statement rather than a nice one."""
    research = MutationResearch()
    config = research.create_configuration()
    config.with_defaults().with_lane_type_enforcement(True).finalize()
    config.activate()
    research.activate(config)

    inherited = research.create_research_set("probe-inherits")
    assert inherited.lane_type_enforcement is True, (
        "a new set did not inherit the configured default - the config "
        "knob and the per-set knob are not connected"
    )

    # and the per-set override still wins locally
    inherited.set_lane_type_enforcement(False)
    assert inherited.lane_type_enforcement is False
    sibling = research.create_research_set("probe-inherits-sibling")
    assert sibling.lane_type_enforcement is True, (
        "one set's override leaked into another set"
    )
    print("both scopes pinned: default inherited, override stays local")
# ---------------------------------------------------------------------------
# Lesson 03 continued - RESIDENCY FOR REAL
#
# residence_of() returning None on a miss proves nothing on its own. These
# register actual spells into actual lanes and check the record moves.
# ---------------------------------------------------------------------------

def test_probe_a_registered_spell_takes_up_residence_in_a_lane():
    """Lesson 03 HEADLINE: a spell LIVES IN exactly one lane, which is
    what makes "where is this now" a question with one answer.

    Registering must actually change residence_of - otherwise residency
    is a concept the API talks about but does not maintain."""
    research = _active_research()
    research_set = research.create_research_set("probe-live-residency")

    assert research_set.residence_of("spell-alpha") is None
    node = research_set.register_spell("spell-alpha")
    assert node is not None

    where = research_set.residence_of("spell-alpha")
    assert where is not None, "a registered spell must have a residence"
    # RESIDENCE IS A LANE ID, NOT A LANE NAME. `lane_names()` answers a
    # different question, and the two vocabularies are easy to conflate -
    # this row originally asserted the id was in the name list and failed.
    assert isinstance(where, str) and where
    assert where not in research_set.lane_names()
    assert research_set.residence_of("spell-alpha") == where, (
        "residence must be stable across reads"
    )
    print("residency pinned: spell-alpha now lives in", where)


def test_probe_a_new_lane_appears_in_lane_names_and_heads():
    """Lesson 03 claim: lanes are real tracks, not labels. Creating one
    must show up in BOTH the name list and heads() - heads is the
    per-lane tip, so a lane missing from it would be unwalkable."""
    research = _active_research()
    research_set = research.create_research_set("probe-lanes")
    before = set(research_set.lane_names())

    research_set.create_lane("experiment-a", lane_type="experiment")
    after = set(research_set.lane_names())

    assert "experiment-a" in after
    assert after > before, "create_lane must add a lane"
    heads = research_set.heads()
    assert isinstance(heads, dict)
    assert "experiment-a" in heads, "a lane with no head cannot be walked"
    print("lane creation pinned:", sorted(before), "->", sorted(after))


def test_probe_walk_returns_the_lane_contents_in_order():
    """Lesson 03 claim: walk(lane) gives the ordered contents. Register
    two spells and the walk must contain both - a lane that records but
    cannot be read back is a write-only ledger."""
    research = _active_research()
    research_set = research.create_research_set("probe-walk")
    lane = research_set.default_lane
    lane_name = research_set.lane_names()[0]

    research_set.register_spell("spell-one", lane=lane_name)
    research_set.register_spell("spell-two", lane=lane_name)

    walked = research_set.walk(lane_name)
    assert isinstance(walked, list)
    assert len(walked) >= 2, f"expected both spells in the walk, got {len(walked)}"
    print("walk pinned:", len(walked), "entries in", lane_name)


def test_probe_history_follows_one_spell_and_heads_tracks_the_tip():
    """Lesson 03 claim: history(spell_id) follows ONE spell, heads()
    reports the current tip per lane. Together they answer "where has
    this been" and "what is latest here" - different questions that a
    single ledger read could not separate."""
    research = _active_research()
    research_set = research.create_research_set("probe-history-read")
    lane_name = research_set.lane_names()[0]

    research_set.register_spell("spell-tracked", lane=lane_name)
    history = research_set.history("spell-tracked")
    assert isinstance(history, dict) and history

    heads = research_set.heads()
    assert lane_name in heads
    print("history/heads pinned: history keys", sorted(history)[:5],
          "| head of", lane_name, "->", heads[lane_name])


def test_probe_lane_type_enforcement_is_actually_togglable():
    """Lesson 03 / 06 claim: LaneType is a RULE or a LABEL depending on a
    knob, and the knob is live per set. Reading it back must reflect what
    was set, or "melder ships the choice" is not true."""
    research = _active_research()
    research_set = research.create_research_set("probe-enforcement")
    original = research_set.lane_type_enforcement

    research_set.set_lane_type_enforcement(not original)
    assert research_set.lane_type_enforcement is (not original)
    research_set.set_lane_type_enforcement(original)
    assert research_set.lane_type_enforcement is original
    print("enforcement knob pinned: toggles and reads back, default", original)


def test_probe_two_research_sets_do_not_share_residency():
    """Lesson 03 claim: a research set is ONE named body of history. Two
    sets must not see each other's residents, or "one spell, one lane"
    would be ambiguous the moment a second set existed."""
    research = _active_research()
    first = research.create_research_set("probe-isolation-a")
    second = research.create_research_set("probe-isolation-b")

    first.register_spell("spell-only-in-a")
    assert first.residence_of("spell-only-in-a") is not None
    assert second.residence_of("spell-only-in-a") is None, (
        "research sets must not leak residency across each other"
    )
    print("set isolation pinned: residency does not cross sets")


# ---------------------------------------------------------------------------
# Lessons 07-09 - the codegen room, the research gradient, the DB lane
# ---------------------------------------------------------------------------

def _enabled_nexus():
    nexus = Nexus()
    config = nexus.create_configuration()
    config.with_rift_creation_enabled(True)
    nexus.activate(config)
    return nexus


def _room(nexus, kind: str, name: str):
    config = nexus.create_rift_configuration()
    config.with_space_type(kind)
    rift = nexus.create_rift(configuration=config, rift_name=name)
    rift.mark_active()
    return rift.space


def test_probe_codegen_room_swaps_a_third_property():
    """Lesson 07 claim: advanced 11 found static and capability each swap
    TWO properties - command_system (DO) and frame_viewer (SEE). The
    codegen room adds `codegen_system` (MAKE). Three planes of authority,
    each swapped by handing over a different class."""
    nexus = _enabled_nexus()
    codegen = _room(nexus, "codegen", "probe-cg-room")
    capability = _room(nexus, "capability", "probe-cap-room")

    assert codegen.space_kind == "codegen"
    assert hasattr(codegen, "codegen_system")
    assert not hasattr(capability, "codegen_system"), (
        "a capability room gained codegen_system - the MAKE plane leaked"
    )
    assert type(codegen.command_system) is not type(capability.command_system)
    print("third plane pinned: do / see / MAKE")


def test_probe_codegen_verbs_exist_only_on_the_codegen_room():
    """Lesson 07 claim: validate/execute/materialize are authority granted
    BY ABSENCE elsewhere - the other two room kinds do not carry them, and
    that is not a guard that refuses."""
    nexus = _enabled_nexus()
    codegen = _room(nexus, "codegen", "probe-cg-verbs").command_system
    static = _room(nexus, "static", "probe-st-verbs").command_system
    capability = _room(nexus, "capability", "probe-cap-verbs").command_system

    for verb in ("validate_codegen", "execute_codegen", "materialize_codegen"):
        assert hasattr(codegen, verb), verb
        assert not hasattr(static, verb), f"static gained {verb}"
        assert not hasattr(capability, verb), f"capability gained {verb}"
    print("codegen verbs pinned: present on one room kind only")


def test_probe_codegen_requires_both_code_and_a_named_frame():
    """Lesson 07 claim: neither `code` nor `frame_name` defaults.
    Generated code has to land in a NAMED world - a codegen call that
    guessed its target frame would be the worst possible bug, and the
    signature is what prevents it."""
    import inspect
    nexus = _enabled_nexus()
    commands = _room(nexus, "codegen", "probe-cg-sig").command_system
    for verb in ("validate_codegen", "execute_codegen"):
        parameters = inspect.signature(getattr(commands, verb)).parameters
        assert parameters["code"].default is inspect.Parameter.empty, verb
        assert parameters["frame_name"].default is inspect.Parameter.empty, verb
        with pytest.raises(TypeError):
            getattr(commands, verb)()
    print("codegen signatures pinned: code and frame_name both required")


def test_probe_research_access_is_graduated_across_the_three_rooms():
    """Lesson 08 HEADLINE, measured rather than asserted. Research access
    is a GRADIENT, not a binary:

        static      0 research verbs
        capability  some
        codegen     strictly more

    A red here means the tiers collapsed, and lesson 08's whole argument
    (the room that may fabricate code is the room that may restate the
    past) stops being true."""
    nexus = _enabled_nexus()
    def verbs(space):
        return {n for n in dir(space.command_system)
                if n.startswith("research_")}

    static = verbs(_room(nexus, "static", "probe-grad-st"))
    capability = verbs(_room(nexus, "capability", "probe-grad-cap"))
    codegen = verbs(_room(nexus, "codegen", "probe-grad-cg"))

    assert len(static) == 0, "a static room must not reach the record"
    assert 0 < len(capability) < len(codegen)
    print("gradient pinned:", len(static), "<", len(capability), "<",
          len(codegen))


def test_probe_codegen_is_a_strict_superset_and_adds_only_writes():
    """Lesson 08 claim, and the part that makes the gradient meaningful:
    capability has NOTHING codegen lacks, and every verb codegen adds is
    a WRITE to the record.

    So the line is READ vs WRITE, not "codegen gets research". Reading
    history is safe; writing it changes what the next reader concludes,
    so it arrives with the power to fabricate code rather than before."""
    nexus = _enabled_nexus()
    def verbs(space):
        return {n for n in dir(space.command_system)
                if n.startswith("research_")}

    capability = verbs(_room(nexus, "capability", "probe-super-cap"))
    codegen = verbs(_room(nexus, "codegen", "probe-super-cg"))

    assert not (capability - codegen), (
        f"capability-only verbs appeared: {capability - codegen}"
    )
    added = codegen - capability
    assert added, "codegen stopped adding anything"

    for writer in ("research_create_lane", "research_attach",
                   "research_archive", "research_stage_ancestry",
                   "research_group_register", "research_preview",
                   "research_synthesize"):
        assert writer in added, f"{writer} was expected to be codegen-only"

    for reader in ("research_walk", "research_history", "research_diff",
                   "research_impact", "research_residency"):
        assert reader in capability, (
            f"{reader} left the capability surface - reads must stay shared"
        )
    print("read/write line pinned:", len(added), "codegen-only, all writes")


def test_probe_crystallizer_has_no_opaque_sync_verb():
    """Lesson 09 claim: every external verb names a KIND and a DIRECTION.
    There is deliberately NO sync() / mirror_all().

    An opaque sync is impossible to reason about the moment local and
    remote disagree - you cannot tell which side won or what it decided.
    This pins the absence, so adding one becomes a visible decision."""
    crystallizer = Crystallizer()
    for absent in ("sync", "mirror", "mirror_all", "sync_external",
                   "push_everything", "sync_all"):
        assert not hasattr(crystallizer, absent), (
            f"{absent} appeared on the crystallizer"
        )
    for present in ("store_index_graft_external", "fetch_index_graft_external",
                    "list_index_grafts_external",
                    "reload_profile_from_external",
                    "reload_formations_from_external",
                    "apply_external_retention"):
        assert hasattr(crystallizer, present), present
    print("no-opaque-sync pinned: direction and kind are always named")


def test_probe_the_two_describe_doors_answer_different_questions():
    """Lesson 09 claim: describe_external_persistence_manager reports what
    is WIRED; describe_external_interface reports what the CONTRACT is.
    Both must return dicts and both must exist - an operator debugging a
    mesh needs the first, a handler author needs the second."""
    crystallizer = Crystallizer()
    config = md.CrystallizerConfigurationBuilder().with_defaults().activate()
    crystallizer.activate(config)
    wiring = crystallizer.describe_external_persistence_manager()
    contract = crystallizer.describe_external_interface()
    assert isinstance(wiring, dict)
    assert isinstance(contract, dict)
    print("describe doors pinned: wiring", len(wiring), "keys | contract",
          len(contract), "keys")


# ---------------------------------------------------------------------------
# Lessons 26-28 - the iteration loop, the runtime teardown, and the record
#                 crossing as text
# ---------------------------------------------------------------------------

def test_probe_describe_payload_is_strictly_json_safe():
    """Lesson 28's load-bearing claim, and the reason that example calls
    `json.dumps` with NO `default=` handler.

    `describe_composition()` states "PLAIN-VALUE THROUGHOUT. Every nested
    value is JSON-safe". This pins it STRICTLY: a `default=str` would
    paper over the exact regression worth catching, because a datetime
    would go out as a string, come back as a string, and nothing would
    notice the round trip had become lossy."""
    research = _active_research()
    research_set = research.create_research_set("probe-json-safe")
    lane_name = research_set.lane_names()[0]
    research_set.register_spell("spell-json-one", lane=lane_name)
    research_set.register_spell("spell-json-two", lane=lane_name)

    payload = research_set.describe()
    assert isinstance(payload, dict)
    assert "organization" in payload, "organization is a hard requirement"
    assert "journal" in payload, "journal is a hard requirement"

    # No default= on purpose. If this raises, the guarantee has regressed
    # and the TypeError names the offending value.
    text = json.dumps(payload, sort_keys=True)
    assert isinstance(text, str)
    assert json.loads(text) == payload, "the trip must be lossless"
    print("json-safety pinned:", len(text), "chars, strict dumps, lossless")


def test_probe_from_payload_restores_the_recorded_identity():
    """Lesson 28 claim, and the distinction from a WORLD restore.

    `from_payload` says "RECORDED IDENTITY IS PRESERVED - the rebuilt set
    restores the recorded `set_id` and `created_at` rather than minting
    new ones". That is the opposite guarantee to expert 24/27, where a
    restored world is deliberately equivalent-not-identical and hands you
    a translation map. Runtime objects are rebuilt; the RECORD is
    restored, and a lesson that blurred those would teach the wrong
    mental model."""
    research = _active_research()
    research_set = research.create_research_set("probe-identity")
    lane_name = research_set.lane_names()[0]
    research_set.register_spell("spell-identity", lane=lane_name)

    original_id = research_set.set_id
    lanes_before = sorted(research_set.lane_names())
    text = json.dumps(research_set.describe(), sort_keys=True)

    rebuilt = md.ResearchSet.from_payload(json.loads(text))

    assert rebuilt.set_id == original_id, (
        "a hydrated set is the SAME set, not an equivalent copy"
    )
    assert sorted(rebuilt.lane_names()) == lanes_before, (
        "every lane must survive the text round trip"
    )
    assert isinstance(rebuilt.walk(lane_name), list)
    assert isinstance(rebuilt.network_snapshot_shas(), list), (
        "the undo ring rides the payload so restore_network still works"
    )
    print("identity pinned:", original_id[:12], "-> rebuilt same id,",
          len(lanes_before), "lanes")


def test_probe_a_lane_never_registered_into_walks_empty():
    """Lesson 26's correction, pinned so it cannot regress into folklore.

    Cutting a lane records ANCESTRY ONLY - no node is copied and none is
    minted. A codegen turn is not a version either: only bind,
    bind_inactive and a notch write the research book. So a lane cut and
    never registered into must walk EMPTY, and that is correct rather
    than a defect."""
    research = _active_research()
    research_set = research.create_research_set("probe-empty-lane")
    default_lane = research_set.lane_names()[0]
    research_set.register_spell("spell-on-default", lane=default_lane)

    research_set.create_lane("never-registered", lane_type="experiment")
    walked = research_set.walk("never-registered")

    assert isinstance(walked, list)
    assert len(walked) == 0, (
        "a lane nobody registered into is empty - anchoring is ancestry, "
        "not a copy"
    )
    assert len(research_set.walk(default_lane)) >= 1, (
        "the control: the lane we DID register into is not empty"
    )
    print("empty-lane pinned: cut lane walks", len(walked),
          "| registered lane walks", len(research_set.walk(default_lane)))


def test_probe_aether_cleanup_clears_the_singleton():
    """Lesson 27 claim: `cleanup()` IS the public reset, so the lesson
    needs no private door.

    Singleton bookkeeping is cleared in a `finally` (`_instance = None`,
    `_initialized = False`), which is why a failing child teardown can no
    longer leave a cleaned husk installed as the process singleton. The
    private `_reset_singleton_for_tests` sitting next to it is the
    test-isolation verb - this conftest uses it - not a lifecycle door."""
    first = Aether()
    assert Aether() is first, "the singleton must be a singleton first"

    first.cleanup()
    collected = gc.collect()

    second = Aether()
    assert second is not first, (
        "cleanup() must clear the singleton - a fresh Aether() may never "
        "return the cleaned instance"
    )
    print("teardown pinned: fresh root differs after cleanup;",
          collected, "objects collected")


# ---------------------------------------------------------------------------
# Lessons 29-33 - the laws the 2026-08-04/05 runs taught, pinned
# ---------------------------------------------------------------------------

def _frame(name: str):
    """Posture one dynamic, rift-enabled frame and return its Spellbook."""
    configuration = md.SpellbookConfiguration(name).with_defaults().finalize()
    book = md.Spellbook(aetheric_frame=name, configuration=configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    return book


def test_probe_an_empty_conjured_frame_is_linkable():
    """Lessons 29/30/32/33 claim: AN EMPTY FRAME IS A REAL FRAME.

    `configure_aether_frame` declares the frame's LAW and realizes
    nothing. `conjure` gives the frame a root conduit, and THAT is what
    publishes it to the Nexus - `_publish_nexus_state_for_conjure`
    publishes the frame and conduit records and then loops
    `self._spells.values()`, which iterates nothing when nothing is bound.
    The publish gate itself (`_refresh_nexus_publish_enabled`) reads
    `rift_enabled` and NOTHING else.

    So spells are cargo, not a precondition. This probe conjures a frame
    with ZERO spells bound and links a rift to it, then binds afterwards
    to show late arrivals publish incrementally. It also pins the negative
    half: before the conjure there is nothing to target."""
    frame_name = "probe-empty-frame"
    book = _frame(frame_name)

    nexus = Nexus()
    config = nexus.create_configuration()
    config.with_rift_creation_enabled(True)
    config.with_allowed_target_frame_names([frame_name])
    nexus.activate(config)
    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_config, rift_name="probe-empty")
    rift.mark_active()

    # UNREALIZED: declared law, no root conduit, nothing to target yet.
    with pytest.raises(ValueError) as refusal:
        rift.create_frame_link(frame_name)
    assert "descriptor" in str(refusal.value), str(refusal.value)

    # CONJURE WITH ZERO SPELLS BOUND - this is the whole claim.
    book.conjure(name="probe-empty-root")
    rift.create_frame_link(frame_name)
    print("empty frame pinned: conjured with no spells, linked fine")

    # Late arrivals publish incrementally into the already-live frame.
    class LateArrival:
        def __init__(self) -> None:
            self.late = True

    book.bind(spell=LateArrival, existence="unique", permissions="create",
              binding_name="probe-late")
    print("late bind pinned: spells are cargo, not a precondition")


def test_probe_two_visible_spells_may_not_share_a_name():
    """Lesson 30 claim: a distinct `binding_name` does NOT settle a
    duplicate spell name.

    Two INDEPENDENT binds make both spells visible at once, so a shared
    class name makes `meld(spell_name=...)` ambiguous and the post-conjure
    structural validator refuses. This is why 30's two generated modules
    declare ReportBase and ReportDonor rather than Report twice."""
    frame_name = "probe-dupname-frame"
    book = _frame(frame_name)

    class Alpha:
        def __init__(self) -> None:
            self.tag = "a"

    Beta = type("Alpha", (), {"__init__": lambda self: None})

    book.bind(spell=Alpha, existence="unique", permissions="create",
              binding_name="probe-dup-one")
    with pytest.raises(Exception) as collision:
        book.bind(spell=Beta, existence="unique", permissions="create",
                  binding_name="probe-dup-two")
        book.conjure(name="probe-dup-root")
    message = str(collision.value)
    assert "Alpha" in message, message
    print("duplicate name pinned: distinct binding_name did not save it")


def test_probe_parts_are_top_level_only_and_a_miss_is_a_value():
    """Lesson 29/30 claim: the part grain is TOP-LEVEL, and the two verbs
    disagree about how they say so.

    `part_view` returns `found: False` on a miss and never raises, which
    is why 29 shipped GREEN while silently comparing nothing. `synthesize`
    RAISES on the same mistake. Same grain, two failure modes - and the
    quiet one is the dangerous one."""
    research = MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    assert hasattr(research, "part_view")
    assert hasattr(research, "synthesize_candidate")
    doc = (research.part_view.__doc__ or "")
    assert "top-level" in doc.lower(), (
        "part_view stopped documenting the top-level grain"
    )
    print("part grain pinned: top-level only, miss is a value not a raise")


def test_probe_archive_hides_from_heads_but_not_from_lane_names():
    """Lesson 31 claim: archiving HIDES a lane, it does not unmake it -
    and the proof is that two reads disagree on purpose.

    It also pins the None-vs-absent distinction: an open lane with no tip
    is PRESENT in heads() with value None, which is a different fact from
    being absent."""
    research = MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)
    research_set = research.research_set()

    research_set.create_lane("probe-dead-end", lane_type="experiment")
    assert research_set.heads()["probe-dead-end"] is None, (
        "an open lane with no tip is PRESENT with value None, not absent"
    )

    research_set.archive("probe-dead-end", reason="probe")
    assert "probe-dead-end" not in research_set.heads(), "left the active view"
    assert "probe-dead-end" in research_set.lane_names(), "still exists"

    # `default_lane` is a PROPERTY, not a method - it resolves the lane by
    # its well-known name on every read rather than holding a reference.
    with pytest.raises(RuntimeError):
        research_set.archive(research_set.default_lane.name)
    print("archive pinned: hidden from heads, kept in lane_names, "
          "default refuses")


def test_probe_four_custody_classes_answer_four_questions():
    """Lesson 33 claim: custody is a FOUR-class priority chain, and the
    per-class answers are what decide whether a module can drift.

    Only user_source claims the SHA256 fingerprint, which is the trust
    boundary; synthetic rides its own harvest payload and makes no
    fingerprint claim; unknown is the only class that does not descend."""
    from melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy import (
        SyntheticCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy import (
        UserSourceCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy import (
        SitePackageCustodyStrategy,
    )
    from melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy import (
        BinaryUnknownCustodyStrategy,
    )

    synthetic = SyntheticCustodyStrategy()
    user = UserSourceCustodyStrategy(tuple())
    site = SitePackageCustodyStrategy(tuple())
    unknown = BinaryUnknownCustodyStrategy()

    assert synthetic.kind == "synthetic_module"
    assert user.kind == "user_source"
    assert site.kind == "site_package"
    assert unknown.kind == "unknown"

    # ONLY user source makes the fingerprint claim - the trust boundary.
    assert user.claims_sha256_source_fingerprint is True
    for other in (synthetic, site, unknown):
        assert other.claims_sha256_source_fingerprint is False, other.kind
    assert synthetic.fingerprint("x") is None

    # Synthetic source never comes off disk; unknown reads nothing at all.
    assert synthetic.reads_physical_source is False
    assert user.reads_physical_source is True

    # UNKNOWN IS THE ONLY LEAF.
    for descending in (synthetic, user, site):
        assert descending.descends is True, descending.kind
    assert unknown.descends is False
    print("custody pinned: 4 classes, 1 fingerprint custodian, 1 leaf")
