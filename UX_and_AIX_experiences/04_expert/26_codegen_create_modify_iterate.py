"""
TIER: expert (26)
GOAL: THE LOOP TURNED MORE THAN ONCE - AND THE TWO BOOKS IT WRITES.
      Expert 12 drove the codegen verbs once. This iterates them, and in
      doing so hits the distinction that catches everyone: a codegen room
      and a research record keep DIFFERENT BOOKS, and only one is about
      your code.

      THE TURN - four verbs, only two of which change anything:
        research_preview(code, frame_name=)  what WOULD this do
        validate_codegen(code, frame_name=)  am I permitted
        execute_codegen(code, frame_name=)   do it
        materialize_codegen(code, module_name=, frame_name=)   keep it
      Running is not keeping. `materialize` takes a module_name because
      durability needs an ADDRESS, and that is a separate decision from
      having run the code.

      `research_preview` is CODEGEN-ROOMS-ONLY, and that is the tell for
      why room types differ at all: it TAKES CODE, so it only exists
      where writing code is already the room's business. A codegen room
      owns the full 34-command research family; a capability room owns
      twenty-one reads; a static room none.

      THE TWO BOOKS
        THE ROOM'S      what CODE was written. One record per SUCCESSFUL
                        TOP-LEVEL public command - every command, not
                        just codegen ones - with a call-depth counter
                        suppressing the tree underneath each call.
        THE RESEARCH    what VERSIONS exist. Written by `bind` (active),
                        `bind_inactive` (staged) and a notch (promotion),
                        and by NOTHING else.
      So `execute_codegen` writing a module does not mint a version. A
      BIND does. Cutting a lane and running three codegen turns leaves
      that lane EMPTY, and this lesson asserts it.

      AND SINGLE RESIDENCE IS WHY YOU CANNOT JUST FILE IT ELSEWHERE.
      One binding-signature SHA256 lives in exactly ONE lane, network
      wide, permanently - there is no release verb. `bind_inactive`
      already declared the staged version onto `default`, so
      `register_spell(..., lane=...)` for that id raises the REDISCOVERY
      signal naming the holding lane. That raise is a signal, not a
      failure: identical content rebinds to the same SHA, and this is the
      system saying "you built this before, here".
      The way to file it under a name is a different SET - a set is its
      own residence partition, so a version resident in one is simply
      unknown to another.
SURFACE EXERCISED: CodegenCommandSystem.research_preview /
                   validate_codegen / execute_codegen /
                   materialize_codegen / research_create_lane /
                   research_walk / research_heads,
                   MutationResearch.research_set / create_research_set,
                   ResearchSet.register_spell / create_lane / walk,
                   Conduit.bind_inactive
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "iterate-world"


class Rate:
    def __init__(self) -> None:
        self.value = 1


class RateV2:
    def __init__(self) -> None:
        self.value = 2


TURNS = (
    ("turn-1", "rate_multiplier = 1\nresult = rate_multiplier\n"),
    ("turn-2", "rate_multiplier = 2\nresult = rate_multiplier * 10\n"),
    ("turn-3", "rate_multiplier = 3\nresult = rate_multiplier * 100\n"),
)

UNGRANTED = "import socket\nresult = socket\n"


def main() -> None:
    # Custody and record FIRST: the research seams no-op unless the root
    # already exists and is active, and they never construct one.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    # A recorded world must be born configured, and POSTURE GOES BEFORE
    # BIND - a bind into a not-yet-dynamic frame declares nothing.
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

    # Subscribe before acting: `memory_enabled` is literally "is anyone
    # listening", so a room with no subscriber keeps nothing.
    written = []
    assert room.memory_system.memory_enabled is False
    subscription = room.memory_system.register_memory_callback(written.append)
    assert room.memory_system.memory_enabled is True

    # A lane cut BEFORE the loop, so we can prove what the loop does not
    # write to it. Anchoring records ancestry only - it copies nothing.
    cut = commands.research_create_lane(
        "codegen-turns", attach_to="default", attach_at_spell_id=v1,
        reason="does a codegen turn mint a version? (it does not)",
    )
    assert cut["anchor_spell_id"] == v1
    assert len(cut["nodes"]) == 0

    print()
    for label, code in TURNS:
        preview = commands.research_preview(code, frame_name=FRAME)
        verdict = commands.validate_codegen(code, frame_name=FRAME)
        outcome = commands.execute_codegen(code, frame_name=FRAME)
        kept = commands.materialize_codegen(
            code,
            module_name="iterate_policy_%s" % label.replace("-", "_"),
            frame_name=FRAME,
        )
        print("%s: preview(%s) -> validate(%s) -> execute(%s) -> keep(%s)" % (
            label, type(preview).__name__, type(verdict).__name__,
            type(outcome).__name__, type(kept).__name__))

    # A refusal mid-loop changes the verdict, not the structure. Nothing
    # compiled, nothing ran, and the loop reads it rather than breaking.
    denied = commands.validate_codegen(UNGRANTED, frame_name=FRAME)
    refused = commands.execute_codegen(UNGRANTED, frame_name=FRAME)
    print("ungranted import: validate ->", type(denied).__name__,
          "| execute ->", type(refused).__name__)

    room.memory_system.unregister_memory_callback(subscription)
    assert room.memory_system.memory_enabled is False
    print()
    print("room memory:", len(written), "records - the unit is the COMMAND,")
    print("  not the turn:", len(TURNS), "turns x 4 verbs plus the lane cut")

    # THE RESEARCH BOOK IS UNTOUCHED BY ALL OF IT.
    walked_turns = commands.research_walk("codegen-turns")
    assert len(walked_turns) == 0, (
        "a codegen turn is not a version - executing and materializing "
        "code writes the ROOM's book, never the research record"
    )
    print("research_walk('codegen-turns') ->", len(walked_turns),
          "nodes, and correctly so")

    # Now mint versions the only way that works: bind / bind_inactive.
    index = conduit.get_spell_by_id(v1).spell_index
    assert index.spells_in_index() == {v1}
    assert conduit.meld(spell=Rate, binding_name="iterate-rate").value == 1

    staged = conduit.bind_inactive(
        spell=RateV2, spell_index=index,
        existence="unique", permissions="create",
    )
    assert index.spells_in_index() == {v1, staged}
    assert index.selected_spell_id == v1, "staging must NOT move selection"
    assert conduit.meld(spell=Rate, binding_name="iterate-rate").value == 1
    print("v2 STAGED: 2 members, selection unchanged, candidate inert")

    walked_default = commands.research_walk("default")
    assert len(walked_default) >= 1, (
        "bind and bind_inactive declare world entries once the MR root is "
        "active - if this is empty the root was activated too late"
    )
    print("research_walk('default') ->", len(walked_default),
          "nodes - the binds recorded; the codegen calls did not")

    # SINGLE RESIDENCE. The staged id already lives on `default`.
    try:
        research.research_set().register_spell(staged, lane="codegen-turns")
        raise AssertionError("expected the rediscovery signal")
    except RuntimeError as rediscovery:
        print()
        print("register_spell(staged, lane='codegen-turns') REFUSED:")
        print("  ", str(rediscovery)[:110])

    # A different SET is its own residence partition, so the same id
    # files cleanly there.
    audit = research.create_research_set("codegen-audit")
    audit.create_lane("turns", lane_type="experiment")
    audit.register_spell(staged, lane="turns", reason="independent audit")
    assert len(audit.walk("turns")) == 1
    print("the SAME id accepted in a second set - residence is per-set")

    # The loop stops where the public surface stops (expert 17): the
    # promoting verb takes the parked OBJECT, and no public door hands
    # one out - both id->object doors resolve to the ACTIVE member.
    assert conduit.get_spell_by_id(staged).spell_id == v1
    assert hasattr(conduit, "notch_spell")

    print()
    print("preview, permit, run, keep - four questions, four verbs")
    print("two books: the room keeps CODE, research keeps VERSIONS")
    print("a lane you never register into is empty, and that is not a bug")


if __name__ == "__main__":
    main()
