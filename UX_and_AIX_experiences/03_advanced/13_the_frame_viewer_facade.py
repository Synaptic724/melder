"""
TIER: advanced (13)
GOAL: THE FRAME VIEWER - the room's read surface, and the first place in
      melder where the AIX claim stops being a design philosophy and
      becomes methods you can call.

      IT IS A FACADE, AND IT SAYS SO.
      FrameViewer's own docstrings read "FACADE PASS-THROUGH to
      ViewMultiFrame.list_frame_names(...)" and note that it builds "a
      ViewMultiFrame per invocation against a freshly resolved" source.
      That second half matters more than the first: THERE IS NO CACHED
      SNAPSHOT. Every read resolves fresh, so a viewer you held onto for
      an hour cannot hand you an hour-old world. You trade a little work
      per call for never having to ask "is this stale?"

      FOUR SPECIALIZED VIEWS BEHIND IT, IN TWO GROUPS
        get_view_multiframe() HOST-SCOPED - all frames, needs no name
        get_view_frame()      FRAME-SCOPED - targets, visibility, topology
        get_view_conduit()    FRAME-SCOPED - records, roots, relationships
        get_view_spell()      FRAME-SCOPED - identity, source, binding

      AND THERE IS NO DEFAULT FRAME.
      The three frame-scoped accessors REQUIRE a frame name. Omit it and
      you get `ValueError: frame_name is required.`, because "the viewer
      no longer supports default-frame routing for frame-local
      operations". A freshly opened rift is contracted to no frames, so
      until you assign one there is no name to pass - and that is the
      honest state, not a bug in your code.

      DEFECT NOTE (owner's 3.14t run, 2026-08-02): those accessors are
      typed `frame_name: Optional[str] = None` and then reject None
      unconditionally. THE DEFAULT VALUE IS NEVER VALID. A reader who
      trusts the signature writes get_view_frame() and gets a ValueError
      for using the documented default. Either the parameter should be
      `frame_name: str` with no default, or None should route somewhere.
      Pinned in test_advanced_probes.

      AND THEN THE PART WORTH THE WHOLE LESSON.

      The viewer carries a surface built FOR AGENTS, by name:

        describe_agent_onboarding_json()      how to use me
        describe_viewer_agent_purpose_json()  what I am for
        describe_viewer_method_surface()      what I can do
        list_viewer_method_names_ast_json()   my methods, from the AST
        describe_viewer_class_surface_ast_json()

      Most libraries expect a reader to arrive already knowing the API -
      docs live in a website, and the object tells you nothing about
      itself. These methods invert that. The object onboards its own
      caller, in JSON, at runtime.

      For a human that is a curiosity. For an agent it is the difference
      between guessing a surface and reading it - and it is the same idea
      as list_supported_command_methods() in lesson 11. Twice now, melder
      has answered "what may I do here?" with a method instead of a
      manual.
SURFACE EXERCISED: room.frame_viewer, get_view_* accessors,
                   describe_available_views, describe_viewer_method_surface,
                   describe_agent_onboarding_json
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import json

import melder as md


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_system_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.enable(system_config)

    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("capability")
    rift = nexus.create_rift(configuration=rift_config, rift_name="observatory")
    rift.mark_active()

    viewer = rift.space.frame_viewer
    assert isinstance(viewer, md.FrameViewer)
    print("viewer:", viewer.id)

    # THE FACADE'S COMMON READS. A fresh rift has no assigned frames yet,
    # so these are honest zeros rather than errors - the read surface
    # works on an empty world.
    frame_names = viewer.list_frame_names()
    print("frames visible:", viewer.count_frames(), frame_names)
    assert isinstance(frame_names, list)
    assert viewer.count_frames() == len(frame_names)

    # THE VIEWS SPLIT INTO TWO GROUPS, AND THAT SPLIT IS THE LESSON.
    #
    # get_view_multiframe() is HOST-SCOPED - it asks about all frames, so
    # it needs no frame name and works right now.
    multiframe = viewer.get_view_multiframe()
    assert isinstance(multiframe, md.ViewMultiFrame)
    print("view_multiframe:", type(multiframe).__name__, "(host-scoped)")

    # get_view_frame / get_view_conduit / get_view_spell are FRAME-SCOPED.
    # THERE IS NO DEFAULT FRAME. Calling them without a name raises, and
    # the viewer says why: "the viewer no longer supports default-frame
    # routing for frame-local operations."
    for accessor in ("get_view_frame", "get_view_conduit", "get_view_spell"):
        try:
            getattr(viewer, accessor)()
            raise AssertionError(f"{accessor} should require a frame name")
        except ValueError as error:
            print(f"  {accessor:18s} refused: {error}")

    # This rift is contracted to no frames, so there is no name to pass -
    # which is the honest state of a freshly opened rift.
    assert rift.list_assigned_frame_names() == ()
    print("assigned frames:", rift.list_assigned_frame_names(),
          "- nothing to scope a frame-local view to yet")

    # The view TYPES are still inspectable without an instance, which is
    # how the next two lessons map their surfaces.
    for view_type in (md.ViewFrame, md.ViewConduit, md.ViewSpell,
                      md.ViewMultiFrame):
        assert isinstance(view_type, type)
    print("four view types exported:", ", ".join(
        t.__name__ for t in (md.ViewFrame, md.ViewConduit, md.ViewSpell,
                             md.ViewMultiFrame)))

    # NO CACHED SNAPSHOT. The facade resolves per invocation, so two calls
    # hand back two view objects rather than one memoized one.
    assert viewer.get_view_multiframe() is not viewer.get_view_multiframe()
    print("fresh view per invocation - nothing to go stale")

    # WHAT VIEWS EXIST? Ask, do not assume.
    available = viewer.describe_available_views()
    assert isinstance(available, list)
    print("describe_available_views ->", len(available), "entries")

    # THE AIX SURFACE. The viewer describes its own method surface...
    surface = viewer.describe_viewer_method_surface()
    assert isinstance(surface, dict)
    print("describe_viewer_method_surface ->", len(surface), "keys")

    # ...and onboards an agent in JSON, at runtime, from the object itself.
    onboarding = viewer.describe_agent_onboarding_json()
    assert isinstance(onboarding, str)
    parsed = json.loads(onboarding)
    print("describe_agent_onboarding_json -> valid JSON,",
          len(onboarding), "chars")
    print("  top-level keys:", sorted(parsed)[:6])

    purpose = viewer.describe_viewer_agent_purpose_json()
    assert isinstance(purpose, str)
    json.loads(purpose)
    print("describe_viewer_agent_purpose_json -> valid JSON")

    # clone() hands back an independent facade over the same world.
    twin = viewer.clone()
    assert isinstance(twin, md.FrameViewer)
    assert twin is not viewer
    assert twin.count_frames() == viewer.count_frames()
    print("clone: independent object, same reading")

    print()
    print("a facade with no snapshot - every read is a fresh resolve")
    print("and the object onboards its own caller instead of assuming docs")


if __name__ == "__main__":
    main()
