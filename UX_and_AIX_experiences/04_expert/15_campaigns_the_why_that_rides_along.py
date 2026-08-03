"""
TIER: expert (15)
GOAL: CAMPAIGNS - the WHY, carried without anyone remembering to carry
      it. Expert 14 built a subsystem and left one argument dangling:
      `research_group_history(group_id, campaign=...)`. This is what goes
      in that slot, and why the slot is worth having.

      A campaign is a stamp that crosses lanes. Lanes are WHERE work
      lives; a campaign is WHICH EFFORT it belonged to, and one effort
      routinely touches several lanes, several subsystems, and several
      agents. Nothing else in the record can express that, because
      everything else is organized by place.

      THE SURFACE, AND IT SPLITS THE SAME WAY

        SET (codegen rooms only - these WRITE)
          research_set_campaign(campaign)
          research_clear_campaign()

        READ (capability rooms get this too)
          research_campaign_view(campaign)

      THE ONE THING TO ACTUALLY LEARN HERE

        campaign=None DOES NOT MEAN "no campaign". IT MEANS INHERIT.

      Pass nothing and the record takes the AMBIENT stamp. To record
      something with no campaign at all you must CLEAR the ambient one
      first. That reads like a trap until you see what it buys: campaign
      membership never depends on an agent remembering to pass an
      argument on every call, across a session that might be thousands of
      them. Attribution defaults to true rather than to blank.

      An EXPLICIT campaign still wins over the ambient one, so the
      default is a default and not a cage.

      AND IT RIDES EXACTLY FOUR SEAMS, NOT EVERYTHING
      The ambient stamp is applied by the ROOT FACADE:
      `record_world_entry`, `record_promotion`, `register_group`,
      `recompose_group` - every dynamic bind, staged bind, notch, and
      composition write. The room's ORGANIZATIONAL verbs
      (`research_create_lane`, `research_attach`, `research_archive`)
      delegate straight to the research set and are UNSTAMPED. Moving
      furniture is not part of an effort's story unless you say so.

      WRITE/READ AGREEMENT, AND IT IS A LAW (BUG-047)
      An empty campaign is refused on the WRITE side for one stated
      reason: `campaign_view` refuses it on the READ side. A public write
      may never create a record the public query API cannot reach. That
      is the never-substitute law wearing a different hat - melder would
      rather refuse your write than let you produce a fact nobody can
      ever ask about.

      WHAT THE VIEW ANSWERS
        {campaign, nodes, transitions, lane_names}
      TRANSITIONS AND NODES ARE NOT THE SAME SET, deliberately. Every
      stamped journal entry is a transition; only four acts contribute a
      NODE (registered, staged, group_registered, group_recomposed). A
      campaign of pure organizational moves yields transitions and an
      empty node list - that is correct, not a gap.

      And the sequence is the JOURNAL's order, not a lane walk. Lane
      iteration would tie-break same-millisecond ULIDs on their random
      component, so the story would reorder itself between runs. A
      history that is not reproducible is not a history.
SURFACE EXERCISED: research_set_campaign / research_clear_campaign /
                   research_campaign_view, ambient inheritance through
                   research_group_register and research_group_recompose,
                   and research_group_history(campaign=...)
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def _room(nexus, kind, name):
    """Open one rift of the given kind and hand back its command surface."""
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type(kind)
    rift = nexus.create_rift(configuration=configuration, rift_name=name)
    rift.mark_active()
    return rift.space.command_system


def main() -> None:
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.activate(system_configuration)

    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)

    codegen = _room(nexus, "codegen", "worker")
    capability = _room(nexus, "capability", "auditor")

    # THE SPLIT AGAIN. Setting the WHY is a write; reading it is not.
    assert hasattr(codegen, "research_set_campaign")
    assert hasattr(codegen, "research_clear_campaign")
    assert not hasattr(capability, "research_set_campaign")
    assert not hasattr(capability, "research_clear_campaign")
    assert hasattr(codegen, "research_campaign_view")
    assert hasattr(capability, "research_campaign_view")
    print("set/clear: codegen only   view: both rooms")

    # Some declared versions to compose over.
    research_set = research.research_set()
    alpha, beta, gamma = "a" * 64, "b" * 64, "c" * 64
    for spell_id in (alpha, beta, gamma):
        research_set.register_spell(spell_id)
    research_set.create_lane("payments", lane_type="production")

    # 1. NAME THE EFFORT ONCE.
    codegen.research_set_campaign("q3-payments-split")
    assert research.active_campaign == "q3-payments-split"
    print()
    print("ambient campaign set ->", research.active_campaign)

    # 2. WRITE WITHOUT MENTIONING IT. This is the whole point: no
    #    `campaign=` argument anywhere, and the record is attributed.
    first = codegen.research_group_register(
        [alpha, beta], lane="payments", reason="the payments core",
    )
    assert first["campaign"] == "q3-payments-split", (
        "campaign=None means INHERIT, not none"
    )
    print("registered a composition with NO campaign argument ->",
          first["campaign"])

    second = codegen.research_group_recompose(
        first["group_id"], add=[gamma], reason="settlement joined",
    )
    assert second["campaign"] == "q3-payments-split"
    print("recompose inherited the same stamp - so the whole arc is one")
    print("effort, without one call naming it")

    # 3. ORGANIZATIONAL MOVES DO NOT RIDE ALONG. The room's lane verbs go
    #    straight to the research set, not through the stamping facade.
    before = len(codegen.research_campaign_view("q3-payments-split")
                 ["transitions"])
    codegen.research_create_lane("scratch", lane_type="experiment")
    after = len(codegen.research_campaign_view("q3-payments-split")
                ["transitions"])
    assert after == before, (
        "an organizational move must not be attributed to an effort "
        "nobody said it belonged to"
    )
    print()
    print("created a lane under a live campaign; transitions unchanged:",
          before, "->", after)
    print("   the stamp rides declarations, not furniture moves")

    # 4. TO RECORD WITH NO CAMPAIGN, CLEAR THE AMBIENT ONE. There is no
    #    "campaign=None means none" escape hatch, because None is taken.
    codegen.research_clear_campaign()
    assert research.active_campaign is None
    delta = "d" * 64
    research_set.register_spell(delta)
    unattributed = codegen.research_group_register(
        [alpha, delta], lane="payments", reason="side quest",
    )
    assert unattributed["campaign"] is None
    print()
    print("cleared the ambient stamp -> the next write is unattributed")
    print("   clearing is the ONLY way to opt out, which is why the")
    print("   default direction is 'attributed'")

    # 5. AN EXPLICIT CAMPAIGN BEATS THE AMBIENT ONE. A default, not a cage.
    codegen.research_set_campaign("q3-payments-split")
    epsilon = "e" * 64
    research_set.register_spell(epsilon)
    override = codegen.research_group_register(
        [beta, epsilon],
        lane="payments",
        reason="borrowed for a different effort",
    )
    # The room verb takes no campaign argument, so the override is made at
    # the root facade - the same seam that applies the ambient default.
    explicit = research.register_group(
        [gamma, epsilon],
        lane="payments",
        campaign="hotfix-2026-08",
        reason="explicitly someone else's effort",
    )
    assert override["campaign"] == "q3-payments-split"
    assert explicit.campaign == "hotfix-2026-08"
    print()
    print("ambient ->", override["campaign"])
    print("explicit ->", explicit.campaign, " (wins)")

    # 6. THE WRITE/READ AGREEMENT. An empty stamp is refused on BOTH sides
    #    for one reason: the read side cannot address it.
    for attempt in (
            lambda: codegen.research_set_campaign(""),
            lambda: codegen.research_campaign_view(""),
    ):
        try:
            attempt()
            raise AssertionError("expected ValueError on an empty campaign")
        except ValueError:
            pass
    print()
    print("empty campaign refused by the WRITE and by the READ -")
    print("   a public write may never create a record the public query")
    print("   API cannot reach")

    # 7. THE VIEW. Transitions are every stamped event; nodes are only the
    #    four acts that declare something.
    view = codegen.research_campaign_view("q3-payments-split")
    for key in ("campaign", "nodes", "transitions", "lane_names"):
        assert key in view, key
    assert len(view["nodes"]) <= len(view["transitions"]), (
        "only registered/staged/group_registered/group_recomposed "
        "contribute a node - transitions is the wider set"
    )
    print()
    print("campaign view:", len(view["nodes"]), "nodes /",
          len(view["transitions"]), "transitions across lanes",
          sorted(view["lane_names"]))
    print("   sequenced by JOURNAL order, so two runs tell the same story")

    # 8. AND THE JOIN EXPERT 14 LEFT OPEN: one subsystem, one effort.
    story = capability.research_group_history(
        second["group_id"], campaign="q3-payments-split",
    )
    print()
    print("group_history(subsystem, campaign) ->", type(story).__name__)
    print("   WHERE by WHEN - 'how did this subsystem change during that")
    print("   effort' is a question you can only ask if both were named")

    print()
    print("a lane says where work lives; a campaign says what it was for")
    print("None means INHERIT, so attribution defaults to true")
    print("and nothing is written that nobody could later ask about")


if __name__ == "__main__":
    main()
