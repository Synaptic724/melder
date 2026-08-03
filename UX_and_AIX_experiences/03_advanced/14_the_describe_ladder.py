"""
TIER: advanced (14)
GOAL: THE DESCRIBE LADDER - why the read surface is not one fat
      describe() per thing, and why that shape is aimed at agents.

      Look at what ViewSpell offers for a single spell:

        describe_spell_brief(...)      the smallest useful answer
        describe_spell(...)            the normal record
        describe_spell_detail(...)     the long form
        describe_spell_payload(...)    the raw payload

      ...and then NINE per-facet verbs that hand you exactly one slice:

        describe_spell_identity      describe_spell_source
        describe_spell_origin        describe_spell_binding
        describe_spell_index         describe_spell_resolution
        describe_spell_metadata      describe_spell_research
        describe_spell_class_profile

      ViewConduit is built the same way - brief / describe / topology /
      inventory / relationships / crosswalk, plus root and policy filters.

      THIS IS A CONTEXT BUDGET CONTROL.

      A human reading one spell does not care whether the payload is
      400 bytes or 40,000. An agent with a finite context window cares
      enormously. The ladder lets a caller enumerate 400 spells at BRIEF,
      decide which three matter, and pay full price for only those three.

      A single fat describe() forces the opposite trade: either it is
      thin and you cannot answer detailed questions, or it is fat and
      surveying anything is unaffordable. The ladder refuses that choice.

      THE CHEAP RUNG IS ALWAYS list_*
        list_spells / list_conduits / list_root_conduits
      Names and ids first. Descriptions only for what survives the filter.

      A NOTE ON THIS LESSON'S WORLD
      ViewSpell and ViewConduit are FRAME-SCOPED (lesson 13), and a
      freshly opened rift is contracted to no frames - so this lesson
      maps the ladder off the EXPORTED TYPES rather than off instances.
      That is not a workaround: THE LADDER IS A PROPERTY OF THE CLASS.
      You do not need a populated world to see the shape of the surface
      you will be paying for, which is exactly the point of surveying
      before you commit.

      The HOST-SCOPED view (get_view_multiframe) needs no frame, so the
      cheapest rung of all really is callable before you have assigned
      anything - and this lesson proves that too.
SURFACE EXERCISED: md.ViewSpell, md.ViewConduit - the describe ladder,
                   list_* enumeration, empty-world coherence
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


SPELL_LADDER = (
    "describe_spell_brief",
    "describe_spell",
    "describe_spell_detail",
    "describe_spell_payload",
)

SPELL_FACETS = (
    "describe_spell_identity",
    "describe_spell_source",
    "describe_spell_origin",
    "describe_spell_binding",
    "describe_spell_index",
    "describe_spell_resolution",
    "describe_spell_metadata",
    "describe_spell_research",
    "describe_spell_class_profile",
)

CONDUIT_LADDER = (
    "describe_conduit_brief",
    "describe_conduit",
    "describe_conduit_topology",
    "describe_conduit_inventory",
    "describe_conduit_relationships",
    "describe_conduit_crosswalk",
)


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.activate(system_config)

    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("capability")
    rift = nexus.create_rift(configuration=rift_config, rift_name="survey")
    rift.mark_active()

    viewer = rift.space.frame_viewer

    # THE VIEWS ARE FRAME-SCOPED (lesson 13) and this rift is contracted
    # to none, so we map the surface off the EXPORTED TYPES rather than
    # off instances. The ladder is a property of the class - you do not
    # need a populated world to see its shape.
    assert rift.list_assigned_frame_names() == ()
    print("no assigned frames - mapping the ladder from the types")

    # THE CHEAP RUNG. Enumeration first - names and ids, nothing more.
    for cheap in ("list_spells",):
        assert hasattr(md.ViewSpell, cheap), cheap
    for cheap in ("list_conduits", "list_root_conduits"):
        assert hasattr(md.ViewConduit, cheap), cheap
    print("cheap rung: list_spells / list_conduits / list_root_conduits")

    # But the HOST-SCOPED view needs no frame, so the cheap rung really
    # is callable right now - proof the survey entry point is reachable
    # before you have committed to anything.
    multiframe = viewer.get_view_multiframe()
    frames = multiframe.list_frame_names()
    assert isinstance(frames, list)
    print("host-scoped survey works with no frame bound:", frames)

    # THE LADDER EXISTS, RUNG BY RUNG. Four resolutions for one spell.
    print()
    print("ViewSpell resolution ladder:")
    for rung, verb in enumerate(SPELL_LADDER, start=1):
        assert hasattr(md.ViewSpell, verb), verb
        print(f"  {rung}. {verb}")

    # NINE FACETS. Ask for one slice instead of the whole record.
    print()
    print("ViewSpell per-facet verbs:", len(SPELL_FACETS))
    for verb in SPELL_FACETS:
        assert hasattr(md.ViewSpell, verb), verb
        print("   ", verb.replace("describe_spell_", ""))

    # ViewConduit is built to the same plan.
    print()
    print("ViewConduit resolution ladder:")
    for rung, verb in enumerate(CONDUIT_LADDER, start=1):
        assert hasattr(md.ViewConduit, verb), verb
        print(f"  {rung}. {verb}")

    # Filters belong on the cheap rung too - narrow BEFORE you describe.
    for narrowing in ("list_conduits_by_root_id", "list_conduits_by_policy",
                      "is_root_conduit", "get_root_conduit_id"):
        assert hasattr(md.ViewConduit, narrowing), narrowing
    print()
    print("filters live on the cheap rung: narrow first, describe after")

    # The shape is deliberate: strictly more facets than ladder rungs,
    # because most questions want one slice rather than one more size.
    assert len(SPELL_FACETS) > len(SPELL_LADDER)
    print("facets:", len(SPELL_FACETS), "> ladder rungs:", len(SPELL_LADDER))

    print()
    print("survey at brief, commit at detail - the ladder is a budget")
    print("a read surface that throws on an empty world cannot survey")


if __name__ == "__main__":
    main()
