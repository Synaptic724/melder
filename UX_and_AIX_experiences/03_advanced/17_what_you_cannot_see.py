"""
TIER: advanced (17)
GOAL: THE READ SURFACE REPORTS ITS OWN BLIND SPOTS. Arc C closes on the
      most unusual thing in the viewer family, and the most useful one if
      you are an agent.

      START FROM THE PROBLEM. You call describe_spell(...) and a field is
      not there. What does that mean?

        (a) the field does not exist for this spell, or
        (b) it exists and this rift is not allowed to see it.

      melder states outright that you cannot tell from the outside:

        "VISIBILITY-FILTERED PROJECTION: absence means 'not visible to
         this rift' OR 'not present', INDISTINGUISHABLE FROM OUTSIDE."

      Almost every API in existence stops there and leaves you to guess.
      For a human that produces a confused afternoon. For an agent it
      produces a CONFIDENT WRONG ANSWER - "this spell has no source
      binding" instead of "I was not shown the source binding" - and the
      agent has no way to know which it said.

      SO MELDER SHIPS THE DISAMBIGUATOR.

        describe_spell_missing_sections(...)     ViewSpell
        describe_conduit_missing_sections(...)   ViewConduit
        describe_missing_surface(...)            ViewFrame / FrameViewer

      The spell one describes itself as "THE WITHHELD-SECTION PROBE: it
      computes every payload field name and subtracts the visible ones, so
      it reports the NAMES of sections you cannot read. THIS IS HOW YOU
      TELL 'HIDDEN' FROM 'EMPTY' WITHOUT THE CONTENTS."

      READ THAT LAST CLAUSE AGAIN - IT IS THE WHOLE DESIGN.
      You learn the SHAPE of your blindness without breaching it. The
      contract says "does not expose hidden payload bodies". So the probe
      is safe to ship to a low-authority room: it can honestly say "there
      are three sections here you may not read" without reading them.

      That is what makes this different from an error message. A refusal
      tells you that you were stopped. This tells you WHAT you were
      stopped from, by name, without stopping being enforced any less.

      VISIBLE AND MISSING ARE COMPLEMENTS
        describe_visible_surface()  what I can see right now
        describe_missing_surface()  what I cannot
      Together they partition the world. Either alone is half an answer.

      AND ONE ANTI-FOOTGUN WORTH STEALING
      Every one of these takes frame_name, and it is NOT a selector:

        "`frame_name` is an ASSERTION, not a selector - when supplied it
         must match the bound frame or the call raises."

      A parameter shaped like a filter that is really a guard. You cannot
      accidentally read a different frame than the one you think you are
      holding; saying the wrong name is an error, not a surprise result.
SURFACE EXERCISED: describe_visible_surface / describe_missing_surface,
                   describe_spell_missing_sections,
                   describe_conduit_missing_sections
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_system_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.enable(system_config)

    # A STATIC room on purpose - the lower-authority kind (lesson 13).
    # Blind spots are the point of this lesson, so pick the room that has
    # more of them.
    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type(md.RiftSpaceType.static)
    rift = nexus.create_rift(configuration=rift_config, rift_name="restricted")
    rift.mark_active()

    viewer = rift.space.frame_viewer

    # THE FAMILY EXISTS AT EVERY LEVEL. That consistency is the point -
    # you never have to wonder whether this particular view can tell you
    # what it is hiding. Checked on the TYPES, because the frame-scoped
    # views cannot be built without an assigned frame (lesson 15).
    print("the withheld-section probes:")
    probes = {
        "ViewSpell.describe_spell_missing_sections":
            (md.ViewSpell, "describe_spell_missing_sections"),
        "ViewConduit.describe_conduit_missing_sections":
            (md.ViewConduit, "describe_conduit_missing_sections"),
        "ViewFrame.describe_missing_surface":
            (md.ViewFrame, "describe_missing_surface"),
        "FrameViewer.describe_missing_surface":
            (md.FrameViewer, "describe_missing_surface"),
    }
    for label, (owner_type, verb) in probes.items():
        assert hasattr(owner_type, verb), label
        print("   ", label)

    # AND THEIR COMPLEMENTS. Visible + missing is the whole world.
    print()
    print("and the visible half:")
    for owner_type in (md.ViewFrame, md.FrameViewer):
        assert hasattr(owner_type, "describe_visible_surface")
        print("   ", owner_type.__name__ + ".describe_visible_surface")

    # NOW THE PART THAT SURPRISED ME, AND IT BELONGS IN THIS LESSON MORE
    # THAN ANYWHERE ELSE.
    #
    # These reads are FRAME-SCOPED and this rift is contracted to no
    # frames - so asking "what am I not seeing?" REFUSES rather than
    # answering "everything". Which is the correct call: with no frame
    # bound there is no surface to compare against, and a cheerful empty
    # dict would be a lie shaped like an answer.
    assert rift.list_assigned_frame_names() == ()
    print()
    print("assigned frames:", rift.list_assigned_frame_names())

    for verb in ("describe_visible_surface", "describe_missing_surface"):
        try:
            getattr(viewer, verb)()
            raise AssertionError(f"{verb} should require a frame name")
        except ValueError as error:
            print(f"  {verb:26s} refused: {error}")

    print()
    print("no frame bound, no blind-spot report - and refusing is right:")
    print("an empty answer here would be a lie shaped like an answer")

    # NAMES, NOT BODIES. The probe is safe precisely because it withholds
    # the contents it is telling you about - so it can ship to a room that
    # is not allowed to read them.
    print()
    print("the probe names what it withholds; it never hands over bodies")

    print()
    print("absence is ambiguous - 'hidden' and 'empty' look identical")
    print("so melder ships the disambiguator, and keeps the ACL intact")


if __name__ == "__main__":
    main()
