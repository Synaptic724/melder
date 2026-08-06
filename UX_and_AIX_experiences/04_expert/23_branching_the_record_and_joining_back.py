"""
TIER: expert (23)
GOAL: BRANCHING, AND WHY A JOIN CAN REFUSE. Research lanes are melder's
      branches: parallel lines of versions over one world, anchored to
      each other, finished by joining. It looks like git until three
      places where it deliberately is not.

      A BRANCH STARTS EMPTY
        research_create_lane("try-a", attach_to="default",
                             attach_at_spell_id=v1)
      Anchoring records ANCESTRY ONLY. No node is copied, no node is
      moved, and the anchor lane is untouched - the new lane begins with
      zero versions and a memory of where it came from. That is the
      opposite of a git branch, which starts AT a commit and carries the
      whole history with it.

      ANCHORING IS ALL OR NOTHING
      `attach_to` and `attach_at_spell_id` must be supplied together;
      exactly one of them raises before the lock is even taken. There is
      no "anchor to whatever the tip is" shorthand, because the anchor is
      the one fact the join later reasons about and a shorthand would let
      you record a different anchor than you meant.

      THE DEFAULT LANE TYPE IS `experiment`, NOT `development`
      Omit `lane_type` and you get `experiment` - deliberately NOT the
      default lane's `development`. A freshly cut lane is an experiment
      until someone says otherwise, so the safe classification is the one
      you get by not thinking about it.

      AND A JOIN IS DIVERGENCE-AWARE, WHICH IS THE WHOLE LESSON
        research_join("try-a", into="default")
      The CLEAN path requires two things at once: the source is anchored
      onto the receiver, AND the receiver's tip is STILL AT that anchor.
      Anything else - the receiver moved on, a foreign anchor, no anchor
      at all - is a DIVERGENT join and refuses unless you pass
      `force=True`. The refusal NAMES BOTH TIPS, so you are told exactly
      what drifted apart rather than being handed a conflict to hunt.

      `force=True` IS NOT A MERGE. It is an EXPLICIT SUPERSEDE, and
      melder is blunt about the difference: "Reconciliation-by-content is
      not a join concern: compose in the codegen workshop, register the
      multi-parent result, then join." Merging content is work you do
      with code, in a room, and the record only ever books the outcome.
      A version-control system that merges FOR you is guessing, and this
      one refuses to guess about your source.

      COLLAPSE CHOOSES HOW MUCH LINE COMES WITH IT
        collapse=False (default)  fold the source's FULL line in
        collapse=True             move only the TIP, leaving the rest
                                  readable in the joined source lane
      Residence transfers with whatever moves, and the source is marked
      joined - it accepts no further work afterwards.
SURFACE EXERCISED: research_create_lane (anchored, half-anchored and
                   refused), research_heads, research_join with and
                   without force, Conduit.bind_inactive to move the
                   receiver, and the lane payload create_lane returns
                   (a lane describe() snapshot: lane_type, anchor, nodes)
VERIFY: rides the owner's 3.14t harness; asserts are the contract. The
        SURFACE line was corrected 2026-08-05; executable code unchanged.
"""
import melder as md


FRAME = "branch-world"


class RuleV1:
    def __init__(self) -> None:
        self.tag = "v1"


class RuleV2:
    def __init__(self) -> None:
        self.tag = "v2"


def main() -> None:
    # Record and custody live BEFORE the world, so binds auto-record.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    # A RECORDED WORLD MUST BE BORN CONFIGURED. With custody active, a
    # dynamic conjure REFUSES if any bind ran before the configuration
    # was finalized - the profile record and default bootstrap would
    # otherwise durably persist binds made against unsettled config.
    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    # THE FRAME POSTURE GOES BEFORE THE BIND. A plain bind auto-declares
    # into research only `if self._is_dynamic_posture()` - a frame-level
    # question answerable before conjure. Bind into a not-yet-dynamic
    # frame and nothing is declared, silently, because research
    # bookkeeping never gates a bind. There would then be no node in the
    # default lane to anchor a branch at.
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    v1 = book.bind(spell=RuleV1, existence="unique", permissions="create",
                   binding_name="branch-v1")
    conduit = book.conjure(name="branch-root")
    print("v1 recorded on the default lane:", v1[:12], "...")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="brancher")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    # ANCHORING IS ALL OR NOTHING - and it refuses before doing anything.
    try:
        commands.research_create_lane("half-anchored", attach_to="default")
        raise AssertionError("expected a refusal: anchor is all-or-nothing")
    except ValueError as error:
        print()
        print("attach_to without attach_at_spell_id refused -")
        print("  ", error)

    # CUT A BRANCH, ANCHORED. It starts EMPTY.
    clean = commands.research_create_lane(
        "clean-branch",
        attach_to="default",
        attach_at_spell_id=v1,
        reason="a branch that will join cleanly",
    )
    print()
    print("created 'clean-branch':")
    print("   lane_type   :", clean["lane_type"], " (default is experiment)")
    print("   anchor_spell:", str(clean["anchor_spell_id"])[:12], "...")
    print("   nodes       :", len(clean["nodes"]),
          " <- EMPTY: ancestry only, nothing copied")
    assert clean["lane_type"] == "experiment"
    assert clean["anchor_spell_id"] == v1
    assert len(clean["nodes"]) == 0

    # A SECOND BRANCH FROM THE SAME POINT. This one will go stale.
    commands.research_create_lane(
        "stale-branch",
        attach_to="default",
        attach_at_spell_id=v1,
        reason="a branch the receiver will move away from",
    )
    heads = commands.research_heads()
    print()
    print("research_heads() ->", len(heads), "open lanes")

    # THE CLEAN JOIN. The receiver's tip is still exactly at the anchor.
    commands.research_join("clean-branch", into="default",
                           reason="nothing diverged")
    print()
    print("join('clean-branch' -> 'default') accepted")
    print("  source anchored onto the receiver AND the receiver still at")
    print("  the anchor: the only arrangement that is not a supersede")

    # NOW MOVE THE RECEIVER. A new version lands on the default lane, so
    # 'stale-branch' is anchored at a point the receiver has left.
    v2 = conduit.bind_inactive(
        spell=RuleV2,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique",
        permissions="create",
    )
    print()
    print("v2 recorded; the default lane moved on:", v2[:12], "...")

    # THE DIVERGENT JOIN REFUSES, AND THE REFUSAL NAMES THE TIPS.
    try:
        commands.research_join("stale-branch", into="default")
        raise AssertionError("expected a refusal: divergent join")
    except RuntimeError as error:
        print()
        print("join('stale-branch' -> 'default') refused -")
        print("  ", str(error)[:150])
        print("  it names BOTH tips, so you are told what drifted rather")
        print("  than handed a conflict to go and find")

    # force=True IS A SUPERSEDE, NOT A MERGE.
    commands.research_join("stale-branch", into="default", force=True,
                           reason="explicit supersede, content already "
                                  "reconciled elsewhere")
    print()
    print("join(..., force=True) accepted - and note what it is NOT:")
    print("  it did not merge any SOURCE. Reconciliation by content is")
    print("  work you do in the codegen workshop; you register the")
    print("  multi-parent result and THEN join. The record books an")
    print("  outcome and never guesses at your code")

    # THE JOINED LANES ARE CLOSED. A join is terminal for the source.
    final_heads = commands.research_heads()
    print()
    print("open lanes now:", len(final_heads), " (joined sources closed)")
    assert len(final_heads) <= len(heads)

    print()
    print("a branch starts EMPTY and remembers where it came from")
    print("a clean join is anchored AND un-drifted; anything else is a")
    print("supersede you have to ask for by name")


if __name__ == "__main__":
    main()
