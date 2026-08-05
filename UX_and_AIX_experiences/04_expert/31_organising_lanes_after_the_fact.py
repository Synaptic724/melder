"""
TIER: expert (31)
GOAL: LANES ARE ORGANISED AFTER THE FACT, NOT PLANNED IN ADVANCE. Expert
      23 cut branches and joined them. This is the other three verbs -
      the ones for when you got the shape wrong the first time.

        research_attach(lane, onto=, at_spell_id=)   re-anchor ancestry
        research_detach(lane)                        forget the anchor
        research_archive(lane)                       retire a dead end

      ANCESTRY IS ORGANISATION, NOT CONTENT. Every one of these moves
      where a lane SAYS it came from. None of them copies, moves or
      deletes a version. That separation is why re-organising is cheap
      and safe: the nodes never move, so a wrong anchor is a wrong label
      rather than lost work.

      ATTACH IS ALL-OR-NOTHING, and it refuses before taking a lock:
      `onto` and `at_spell_id` must both be supplied. There is no
      "anchor to whatever the tip is" shorthand, because the anchor is
      the one fact a later join reasons about - a shorthand would let you
      record a different anchor than you meant.

      DETACH IS NOT A DELETE. It removes the anchor, leaving a lane that
      remembers nothing about where it came from. A detached lane can
      still be joined, but the join is DIVERGENT by definition - no
      anchor means nothing for the receiver's tip to agree with - so it
      needs the same explicit `force=True` supersede.

      ARCHIVE RETIRES A LANE WITHOUT LOSING IT. Residence is permanent:
      the versions stay resident in the archived container, rediscovery
      still points at it, and a network snapshot can restore a view that
      contained it. Archiving hides a dead end from the ACTIVE view; it
      does not unmake it.

      AND THE DEFAULT LANE NEVER ARCHIVES. It is the guaranteed
      world-entry record - `register_spell` without a lane records there,
      and `default_lane` resolves by well-known name - so a set that
      archived it could not serve its own default. The refusal is checked
      at the door rather than discovered later.
SURFACE EXERCISED: research_create_lane / research_attach /
                   research_detach / research_archive / research_join /
                   research_heads,
                   ResearchSet.lane_names, Conduit.bind_inactive
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "organise-world"


class Rule:
    def __init__(self) -> None:
        self.tag = "v1"


class RuleV2:
    def __init__(self) -> None:
        self.tag = "v2"


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    v1 = book.bind(spell=Rule, existence="unique", permissions="create",
                   binding_name="organise-rule")
    conduit = book.conjure(name="organise-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="organiser")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system
    research_set = research.research_set()
    print("v1 on the default lane:", v1[:12], "...")

    # A lane cut with NO anchor - a perfectly legal shape, and the one
    # `attach` exists to repair.
    unanchored = commands.research_create_lane(
        "unanchored", reason="cut without an anchor on purpose",
    )
    assert unanchored["anchor_spell_id"] is None
    assert len(unanchored["nodes"]) == 0
    print("cut 'unanchored' -> anchor is None, nodes 0")

    # ATTACH IS ALL-OR-NOTHING and refuses before doing anything.
    try:
        commands.research_attach("unanchored", onto="default")
        raise AssertionError("expected a refusal: anchor is all-or-nothing")
    except TypeError:
        print("attach(onto=) without at_spell_id -> TypeError (both or none)")

    # Now anchor it properly, after the fact.
    commands.research_attach("unanchored", onto="default", at_spell_id=v1,
                             reason="organising after the fact")
    print("attach(onto='default', at_spell_id=v1) accepted")
    print("  ancestry only - no node was copied, moved or created")

    # A clean join is now possible, because the receiver is still at v1.
    commands.research_join("unanchored", into="default",
                           reason="anchored, and the receiver has not moved")
    print("join('unanchored') accepted - re-anchoring made it joinable")

    # DETACH: a second lane, anchored, then deliberately un-anchored.
    commands.research_create_lane(
        "forgetful", attach_to="default", attach_at_spell_id=v1,
        reason="this one will forget where it came from",
    )
    commands.research_detach("forgetful", reason="dropping the anchor")
    print()
    print("detach('forgetful') - the lane now remembers no origin")

    # Move the receiver so the contrast is honest, then show that a
    # detached lane joins only as an explicit supersede.
    v2 = conduit.bind_inactive(
        spell=RuleV2,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique", permissions="create",
    )
    print("default moved on:", v2[:12], "...")

    try:
        commands.research_join("forgetful", into="default")
        raise AssertionError("expected a refusal: no anchor means divergent")
    except RuntimeError as error:
        print("join('forgetful') refused -", str(error)[:100])
        print("  no anchor means nothing for the tip to agree with, so the")
        print("  join is divergent BY DEFINITION - not by drift")

    commands.research_join("forgetful", into="default", force=True,
                           reason="explicit supersede of an unanchored line")
    print("join(force=True) accepted")

    # ARCHIVE: retire a dead end. It is hidden, not unmade.
    commands.research_create_lane(
        "dead-end", attach_to="default", attach_at_spell_id=v1,
        reason="an experiment that went nowhere",
    )
    # OPEN BUT EMPTY IS A REAL STATE. heads() carries the lane with a tip
    # of None - "absent" and "None" mean different things here.
    assert commands.research_heads()["dead-end"] is None
    print()
    print("'dead-end' is open with tip None - empty, not absent")

    commands.research_archive("dead-end", reason="went nowhere")

    # HIDDEN, NOT UNMADE - and the two reads disagree ON PURPOSE.
    assert "dead-end" not in commands.research_heads(), "left the active view"
    assert "dead-end" in research_set.lane_names(), "still exists - no delete"
    print("archive('dead-end'):")
    print("  heads()      -> dropped   (OPEN lanes only)")
    print("  lane_names() -> still there (ALL lanes, any state)")
    print("  the two reads disagree deliberately, and that gap IS the")
    print("  difference between hidden and unmade. Residence stays")
    print("  PERMANENT: the versions remain resident in the archived")
    print("  container and a network snapshot can restore a view that")
    print("  contained it")

    # THE DEFAULT LANE NEVER ARCHIVES.
    try:
        commands.research_archive("default")
        raise AssertionError("expected a refusal: the default lane is guaranteed")
    except RuntimeError as refusal:
        print()
        print("archive('default') refused -", str(refusal)[:100])
        print("  it is the guaranteed world-entry record: register_spell")
        print("  with no lane records THERE, so a set that archived it")
        print("  could not serve its own default")

    # A JOIN FINISHES THE SOURCE: both joined lanes are terminal, and the
    # archived one is retired, so `default` is the only lane left open.
    open_lanes = commands.research_heads()
    assert set(open_lanes) == {"default"}, sorted(open_lanes)
    print()
    print("open lanes now:", sorted(open_lanes), "- a join finishes its source")
    print()
    print("attach, detach, archive - all organisation, none content")
    print("nodes never move, so a wrong shape is a wrong label, not lost work")


if __name__ == "__main__":
    main()
