"""
TIER: expert (03)
GOAL: MUTATION RESEARCH - melder's record of how a world CHANGED, not
      what it currently is. Everything up to here described a runtime.
      This describes its history.

      THE SHAPE
        MutationResearch      the subsystem (same ladder as Aether and
                              Crystallizer - you activate the config, then
                              the subsystem; advanced 17 settled that it
                              is 3-to-1 with Nexus the exception)
        ResearchSet           one named body of history
        ResearchLane          a track within it
        ResearchJournal       the ordered record

      TWO ENUMS, AND THEY ANSWER DIFFERENT QUESTIONS
        LaneState   open / joined / archived      - can I still write here?
        LaneType    development / experiment /
                    production / test             - what KIND of work is this?
      A lane has both. State is lifecycle; type is intent. Collapsing
      them would mean you could not have an archived production lane and
      an open one at the same time, which is exactly what a real
      promotion history looks like.

      LANE TYPE ENFORCEMENT IS A KNOB
        set_lane_type_enforcement(enabled)
      Off, the types are labels. On, they are rules. Melder ships the
      choice rather than assuming which one you are doing - a research
      set exploring a hypothesis and a research set tracking a production
      promotion chain want opposite answers.

      RESIDENCY IS THE IDEA WORTH TAKING AWAY.
        residence_of(spell_id) -> lane name or None
      A spell LIVES IN exactly one lane at a time. That is what makes
      "where is this thing now?" a question with one answer, and it is
      why promotion is a MOVE rather than a copy. `heads()` gives you the
      current tip per lane; `walk(lane)` gives the ordered contents;
      `history(spell_id)` follows one spell across lanes.

      CAMPAIGNS group work that belongs together across lanes:
        set_active_campaign / clear_active_campaign / campaign_view
      Set one and subsequent records join it, so you can ask "what did
      this campaign touch" without threading an id through every call.

      ANCESTRY IS STAGED, THEN RECORDED.
        stage_ancestry(parent_spell_ids) -> record_world_entry(...)
      You declare the parents BEFORE the entry that uses them. Staging is
      explicit and clearable, so a half-built lineage is visible as
      staged-but-unrecorded rather than silently attached to the wrong
      thing.
SURFACE EXERCISED: md.MutationResearch, md.ResearchSet, md.LaneState,
                   md.LaneType - lanes, residency, campaigns, ancestry
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


def main() -> None:
    # THE TWO ENUMS. Different questions, so different types.
    states = [state.name for state in md.LaneState]
    types = [kind.name for kind in md.LaneType]
    print("LaneState (lifecycle):", states)
    print("LaneType  (intent):   ", types)
    assert set(states) == {"open", "joined", "archived"}
    assert set(types) == {"development", "experiment", "production", "test"}

    # THE LADDER, third subsystem to use it (aether 07, crystallizer 17).
    # AETHER-HOSTED, and reached the same way as md.Crystallizer() and
    # md.Nexus(): Aether builds all three roots when it boots, so this call
    # is a LOOKUP, not a construction. One process, one Aether, one research
    # root under it - there is no free-standing research world to make.
    research = md.MutationResearch()
    assert research.activated is False
    print()
    print("start - configured:", research.is_configured,
          "activated:", research.activated)

    config = research.create_configuration()
    config.with_defaults().finalize()
    assert config.activated is False, "finalize seals; it does not enable"
    config.activate()
    research.activate(config)
    assert research.activated is True
    print("activated via the caller-driven ladder (not nexus's shortcut)")

    # A RESEARCH SET is one named body of history.
    research_set = research.create_research_set("promotion-history")
    assert isinstance(research_set, md.ResearchSet)
    assert research_set.name == "promotion-history"
    assert "promotion-history" in research.list_research_set_names()
    print()
    print("research set:", research_set.name, "| id:", research_set.set_id)

    # Every set opens with a default lane, so history has somewhere to go
    # before you have made any decisions about structure.
    default_lane = research_set.default_lane
    assert default_lane is not None
    assert research_set.lane_names(), "a set always has at least one lane"
    print("lanes:", research_set.lane_names())

    # LANE TYPE ENFORCEMENT IS A CHOICE, and it is readable.
    enforcement = research_set.lane_type_enforcement
    assert isinstance(enforcement, bool)
    research_set.set_lane_type_enforcement(True)
    assert research_set.lane_type_enforcement is True
    research_set.set_lane_type_enforcement(enforcement)
    print("lane_type_enforcement is a knob, currently:", enforcement)

    # RESIDENCY. One spell, one lane, one answer - and a miss is None
    # rather than an exception, the same honest-absence shape as
    # ConduitCloud.find_conduit_id_by_name (intermediate 37).
    assert research_set.residence_of("no-such-spell") is None
    print()
    print("residence_of() on an unknown spell -> None, not an exception")

    # THE READ SURFACE, ON A SET NOTHING HAS BEEN REGISTERED INTO. An
    # empty record is PRESENT AND EMPTY, not absent - which is the shape
    # you have to be able to tell apart from "no record at all".
    heads = research_set.heads()
    assert isinstance(heads, dict)
    assert "default" in heads, heads
    assert heads["default"] is None, heads
    print()
    print("heads() on a fresh set ->", heads)
    print("  the default lane is THERE with a tip of None. Open-but-empty")
    print("  and absent are different facts, and melder spells them")
    print("  differently: a missing key means `not open`, a None value")
    print("  means `open, nothing in it yet`")

    walked = research_set.walk("default")
    assert isinstance(walked, list) and walked == [], walked
    print("walk('default') ->", len(walked),
          "rows - somewhere for history to go before any has happened")
    print("  (history / campaign_view are driven in expert 29 and 15,")
    print("   where there is something recorded to read)")

    # CAMPAIGNS - group work across lanes without threading an id around.
    assert research.active_campaign is None
    research.set_active_campaign("q3-promotion")
    assert research.active_campaign == "q3-promotion"
    print()
    print("active campaign:", research.active_campaign)
    research.clear_active_campaign()
    assert research.active_campaign is None
    print("cleared - campaigns are explicit at both ends")

    # ANCESTRY IS STAGED FIRST. Declaring parents is a separate, visible
    # step from recording the entry that uses them.
    assert research.staged_ancestry is None
    research.stage_ancestry(["parent-a", "parent-b"])
    assert research.staged_ancestry == ["parent-a", "parent-b"]
    print()
    print("staged ancestry:", research.staged_ancestry)
    research.clear_staged_ancestry()
    assert research.staged_ancestry is None
    print("cleared - a half-built lineage is visible, never auto-attached")

    print()
    print("state is lifecycle, type is intent - a lane carries both")
    print("residency means one spell, one lane, one answer to 'where is it'")


if __name__ == "__main__":
    main()
