"""
TIER: expert (26)
GOAL: THE LOOP TURNED MORE THAN ONCE - AND THE TWO HISTORIES IT WRITES.
      Expert 12 drove the codegen verbs a single time. This iterates
      them, and in doing so runs into the distinction that catches
      everyone: a codegen room and a research record are keeping
      DIFFERENT BOOKS, and only one of them is about your code.

      THE TURN, FOUR VERBS, ONLY TWO OF WHICH CHANGE ANYTHING

        research_preview(code, frame_name=...)   what WOULD this do
        validate_codegen(code, frame_name=...)   am I permitted
        execute_codegen(code, frame_name=...)    do it
        materialize_codegen(code, module_name=, frame_name=)   keep it

      `research_preview` is a read-only candidate mock - AST analysis, a
      would-be diff, blast radius, and (because `frame_name` is supplied)
      the validate verdict folded in. `execute` runs without keeping.
      `materialize` gives the result an ADDRESS. Running is not keeping,
      and an agent that cannot tell those apart cannot iterate safely.

      AND `research_preview` IS CODEGEN-ROOMS-ONLY, which is the tell for
      why the room types differ at all. A codegen room owns the FULL 34
      -command `research_*` family; a capability room owns twenty-one
      READS and none of the organization, synthesis or preview verbs;
      a static room owns none. The split is not capability tiers for
      their own sake - preview TAKES CODE, so it only exists where
      writing code is already the room's business. Both rooms ADVERTISE
      their family through `list_supported_command_methods`, so an agent
      asking "what can you do" learns the surface exists rather than
      having to know.

      NOW THE PART THAT IS EASY TO GET WRONG, AND THIS LESSON GOT IT
      WRONG FIRST. Cutting a research lane per codegen turn records
      NOTHING. A lane cut and never registered into stays empty, and
      `research_walk` on it returns an empty list - correctly.

      THE ROOM'S BOOK          what CODE was written
        room.memory_system, one record per SUCCESSFUL TOP-LEVEL command,
        full source, push-based.
      THE RESEARCH BOOK        what VERSIONS exist
        written by `bind` (active), `bind_inactive` (staged) and a notch
        (promotion) - and by nothing else. Verified in source: the three
        seams are `_record_research_world_entry(..., staged=False/True)`
        and `_record_research_promotion(from, to)`, each a NO-OP unless
        the MutationResearch root already exists AND is activated. It is
        never lazily constructed from a bind path, and rediscovery of an
        identical SHA is a quiet no-op, because research bookkeeping
        never gates a bind.

      So `execute_codegen` writing a module does not mint a version. A
      BIND does. If you want a codegen result on a lane, you bind the
      thing it produced - or you declare it yourself:

        research_set.register_spell(spell_id, lane="my-lane")

      whose own contract says omitting `lane` targets the guaranteed
      default lane, so the common call needs no lane vocabulary at all.
SURFACE EXERCISED: CodegenCommandSystem.research_preview /
                   validate_codegen / execute_codegen /
                   materialize_codegen / research_create_lane /
                   research_walk / research_heads,
                   md.MutationResearch.research_set,
                   ResearchSet.register_spell / walk,
                   Conduit.bind_inactive, SpellIndex.spells_in_index
VERIFY: NOT RUN by the authoring agent - this sandbox is Python 3.10 and
        melder requires >=3.14. Rides the owner's 3.14t harness; the
        asserts are the contract.
"""
import melder as md


FRAME = "iterate-world"


class Rate:
    def __init__(self) -> None:
        self.value = 1


class RateV2:
    def __init__(self) -> None:
        self.value = 2


class RateV3:
    def __init__(self) -> None:
        self.value = 3


TURNS = (
    ("turn-1", "rate_multiplier = 1\nresult = rate_multiplier\n"),
    ("turn-2", "rate_multiplier = 2\nresult = rate_multiplier * 10\n"),
    ("turn-3", "rate_multiplier = 3\nresult = rate_multiplier * 100\n"),
)

UNGRANTED = "import socket\nresult = socket\n"


def main() -> None:
    # 1. CUSTODY AND RECORD FIRST - and this ordering is load-bearing for
    #    the whole lesson. The research seams are NO-OPs unless the root
    #    already exists and is activated; they never construct one from a
    #    bind path. Activate after binding and those binds recorded
    #    nothing, silently.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    print("custody recording:", crystallizer.activated)

    # 2. A RECORDED WORLD MUST BE BORN CONFIGURED, and THE POSTURE GOES
    #    BEFORE THE BIND: a plain bind declares into research only on a
    #    dynamic posture, so binding into a not-yet-dynamic frame records
    #    nothing.
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
    v1 = book.bind(spell=Rate, existence="unique", permissions="create",
                   binding_name="iterate-rate")
    conduit = book.conjure(name="iterate-root")
    print("v1 bound - an ACTIVE world entry:", v1[:12], "...")

    # 3. THE ROOM.
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="iterator")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    room = rift.space
    commands = room.command_system
    print("codegen room up:", type(room).__name__, "-> targets", FRAME)

    # 4. SUBSCRIBE BEFORE YOU ACT. `memory_enabled` is literally "is
    #    anyone listening", so a room with no subscriber keeps nothing.
    written = []
    assert room.memory_system.memory_enabled is False
    subscription = room.memory_system.register_memory_callback(written.append)
    assert room.memory_system.memory_enabled is True

    # 5. AN EMPTY LANE, CUT BEFORE THE LOOP so we can prove what the loop
    #    does NOT write to it.
    cut = commands.research_create_lane(
        "codegen-turns", attach_to="default", attach_at_spell_id=v1,
        reason="does a codegen turn mint a version? (it does not)",
    )
    assert cut["anchor_spell_id"] == v1
    assert len(cut["nodes"]) == 0
    print("lane 'codegen-turns' cut, anchored at v1, EMPTY by construction")

    # 6. THE LOOP.
    print()
    for label, code in TURNS:
        preview = commands.research_preview(code, frame_name=FRAME)
        verdict = commands.validate_codegen(code, frame_name=FRAME)
        outcome = commands.execute_codegen(code, frame_name=FRAME)
        kept = commands.materialize_codegen(
            code,
            module_name=f"iterate_policy_{label.replace('-', '_')}",
            frame_name=FRAME,
        )
        print(f"{label}: preview({type(preview).__name__}) ->"
              f" validate({type(verdict).__name__}) ->"
              f" execute({type(outcome).__name__}) ->"
              f" materialize({type(kept).__name__})")

    # 7. A REFUSAL MID-LOOP. The structure does not change; the verdict
    #    does. Nothing compiled, nothing ran.
    denied = commands.validate_codegen(UNGRANTED, frame_name=FRAME)
    refused = commands.execute_codegen(UNGRANTED, frame_name=FRAME)
    print()
    print("ungranted import mid-loop: validate ->", type(denied).__name__,
          "| execute ->", type(refused).__name__)
    print("  the loop READS a verdict; it does not break on one")

    # 8. THE ROOM'S BOOK, AND WHAT IT ACTUALLY COUNTS. The rule is ONE
    #    RECORD PER SUCCESSFUL TOP-LEVEL PUBLIC COMMAND - not one per
    #    turn, and not only for codegen verbs. Every public command on
    #    this room emits, so the lane cut counts too, and each turn spent
    #    FOUR commands. A nested call-depth counter suppresses the tree
    #    underneath each call, so you get the calls you made and not the
    #    ones they made internally.
    print()
    print("room memory:", len(written), "records")
    print("  the unit is the COMMAND, not the turn:", len(TURNS),
          "turns x 4 verbs, plus the lane cut, all top-level")
    print("  a refused command does not emit - memory is a log of what")
    print("  HAPPENED, not of what was attempted")
    room.memory_system.unregister_memory_callback(subscription)
    assert room.memory_system.memory_enabled is False

    # 9. AND THE RESEARCH BOOK IS UNTOUCHED BY ALL OF IT.
    walked_turns = commands.research_walk("codegen-turns")
    print()
    print("research_walk('codegen-turns') ->", len(walked_turns), "nodes")
    assert len(walked_turns) == 0, (
        "a codegen turn is not a version - executing and materializing code "
        "writes the ROOM's book, never the research record"
    )
    print("  EMPTY, and correctly so. Three turns of codegen wrote three")
    print("  room records and ZERO research nodes. The books are different:")
    print("  the room keeps what CODE was written, research keeps what")
    print("  VERSIONS exist, and only bind / bind_inactive / notch mint one")

    # 10. SO MINT SOME VERSIONS. Staging is the loop's object half, and
    #     each staged entry IS a world entry - recorded as `staged`.
    active = conduit.get_spell_by_id(v1)
    assert active is not None
    index = active.spell_index
    assert index.selected_spell_id == v1
    assert index.spells_in_index() == {v1}

    live = conduit.meld(spell=Rate, binding_name="iterate-rate")
    assert live.value == 1

    staged_ids = []
    for candidate in (RateV2, RateV3):
        staged_ids.append(conduit.bind_inactive(
            spell=candidate,
            spell_index=index,
            existence="unique",
            permissions="create",
        ))
    assert index.spells_in_index() == {v1, *staged_ids}
    assert index.selected_spell_id == v1, (
        "staging must NOT move the selection - preparing a swap and taking "
        "it are two different acts"
    )
    print()
    print("two candidates STAGED: index now has", len(index.spells_in_index()),
          "members, selection UNCHANGED")

    still = conduit.meld(spell=Rate, binding_name="iterate-rate")
    assert still.value == 1
    print("meld -> value", still.value, "(the parked candidates are inert)")

    # 11. NOW THE RESEARCH BOOK HAS SOMETHING, on the DEFAULT lane -
    #     because that is where world entries land when nobody names one.
    walked_default = commands.research_walk("default")
    print()
    print("research_walk('default') ->", len(walked_default), "nodes")
    assert len(walked_default) >= 1, (
        "bind and bind_inactive declare world entries once the MR root is "
        "active - if this is empty the root was activated too late"
    )
    print("  the binds recorded; the codegen calls did not")

    # 12. NOW TRY TO PUT ONE OF THOSE VERSIONS ON THE LANE WE CUT - and
    #     watch it REFUSE. This is the rule that catches everyone, and it
    #     is the reason step 11 mattered.
    research_set = research.research_set()
    try:
        research_set.register_spell(
            staged_ids[-1],
            lane="codegen-turns",
            reason="trying to file an already-recorded version elsewhere",
        )
        raise AssertionError("expected the rediscovery signal")
    except RuntimeError as rediscovery:
        print()
        print("register_spell(staged_id, lane='codegen-turns') REFUSED:")
        print("  ", str(rediscovery)[:120])

    print("  SINGLE RESIDENCE: one binding-signature SHA256 lives in")
    print("  exactly ONE lane, network-wide, PERMANENTLY. `bind_inactive`")
    print("  already declared this version onto `default` in step 10, so")
    print("  the id is spoken for. There is no release verb - residence is")
    print("  not a label you move, it is where the version LIVES")
    print("  AND THE RAISE IS A SIGNAL, NOT A FAILURE: identical content")
    print("  rebinds to the same SHA, so this is the system saying `you")
    print("  built this before, here` and naming the holding lane")

    # 13. SO HOW DO YOU EVER FILL A NAMED LANE? Either declare a version
    #     that is NOT yet resident, or work in a DIFFERENT SET. A set is
    #     its own residence partition - two sets are two independent
    #     investigations of the same runtime, and a version resident in
    #     one is simply UNKNOWN to the other.
    audit = research.create_research_set("codegen-audit")
    audit.create_lane("turns", lane_type="experiment")
    declared = audit.register_spell(
        staged_ids[-1],
        lane="turns",
        reason="the same version, filed in an independent investigation",
    )
    print()
    print("create_research_set('codegen-audit') + register_spell ->",
          type(declared).__name__)
    walked_audit = audit.walk("turns")
    assert len(walked_audit) == 1
    print("  the SAME spell id, accepted here:", len(walked_audit), "node")
    print("  a set is its own residence partition, so the collision above")
    print("  is scoped to a set rather than to the process")
    print("  DECLARES, never creates: the version already existed - this")
    print("  writes a research record for it and mints no runtime state")

    heads = commands.research_heads()
    print("research_heads() ->", len(heads), "open lane(s) in the default set")

    # 13. THE BOUNDARY, DEMONSTRATED. Promotion is the runtime's rung.
    resolved_from_parked = conduit.get_spell_by_id(staged_ids[0])
    assert resolved_from_parked is not None
    assert resolved_from_parked.spell_id == v1
    assert hasattr(conduit, "notch_spell")
    print()
    print("looking up a PARKED id returned the ACTIVE spell")
    print("  `notch_spell(spell_index=, spell=)` takes the parked OBJECT;")
    print("  SpellIndex exposes ids only and both id->object doors resolve")
    print("  to the live member. Staging is yours; promotion is the")
    print("  runtime's - the loop stops here on purpose (expert 17)")

    print()
    print("preview, permit, run, keep - four questions, four verbs")
    print("two books: the room keeps CODE, research keeps VERSIONS")
    print("a lane you never register into is empty, and that is not a bug")


if __name__ == "__main__":
    main()
