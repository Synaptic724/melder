"""
TIER: advanced (11)
GOAL: WHAT THE ROOM KIND ACTUALLY CHANGES.

      StaticRiftSpace and CapabilityRiftSpace override exactly TWO
      properties of RiftSpace, and they are the two that matter:

        command_system   StaticCommandSystem / CapabilityCommandSystem
        frame_viewer     StaticFrameViewer   / FrameViewer

      THE DOING ONE AND THE SEEING ONE. workstation, event_system and
      memory_system are inherited unchanged, so the room's storage and
      signalling are constant while its AUTHORITY and its VISIBILITY both
      narrow together.

      That pairing is the design. A room you may not mutate is also a
      room that shows you less - and melder does it the same way twice,
      by handing you a different class rather than guarding a shared one.

      AND HERE IS THE DESIGN DECISION WORTH LEARNING FROM.

      The static room does not REFUSE meld(). It does not raise
      PermissionError, it does not check a flag, it does not consult an
      ACL at call time. IT SIMPLY DOES NOT HAVE THE METHOD.

      melder's own note on StaticCommandSystem says it outright:

        "Does not expose topology mutation or direct meld(...) because
         those methods now live on the capability surface INSTEAD OF
         BEING DENIED AFTER INHERITANCE."

      That is the opposite of the usual pattern, where a subclass inherits
      everything and then overrides the dangerous half to raise. Melder
      builds authority UP by class membership instead of tearing it DOWN
      by guard.

      WHY THAT IS BETTER, CONCRETELY:
        - There is no refusal path, so there is no refusal path to test,
          no error message to get subtly wrong, and no gap between "the
          guard is there" and "the guard is correct".
        - Capability becomes STATICALLY ENUMERABLE. You can answer "what
          may this room do" without executing anything and without
          triggering a single refusal.
        - hasattr becomes an honest question again. In a deny-after-
          inherit design it lies - the attribute is there and calling it
          explodes.

      THE AIX SURFACE
      Both kinds expose list_supported_command_methods(). A room will tell
      you what it can do. For an agent that is the difference between
      probing a surface by trying things and reading it.

      WHAT MOVES BETWEEN THEM
        static  - reads, spell status, and meld_existing_spell (REUSE of
                  something already created; no creation, no topology)
        capability - all of that PLUS direct meld(), link/sever_link,
                  create_lesser_conduit, and the cluster verbs
                  (create/delete/join/leave/list)
SURFACE EXERCISED: StaticCommandSystem vs CapabilityCommandSystem via
                   room.command_system, list_supported_command_methods
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def _room(nexus, space_type, name):
    config = nexus.create_rift_configuration()
    config.with_space_type(space_type)
    rift = nexus.create_rift(configuration=config, rift_name=name)
    rift.mark_active()
    return rift.space


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.activate(system_config)

    static_room = _room(nexus, "static", "ops-static")
    capability_room = _room(nexus, "capability", "ops-capability")

    # The rooms themselves are different classes...
    print("static room:    ", type(static_room).__name__)
    print("capability room:", type(capability_room).__name__)
    assert type(static_room) is not type(capability_room)

    # TWO fixtures differ - and they are the DOING one and the SEEING one.
    static_commands = static_room.command_system
    capability_commands = capability_room.command_system
    print("static commands:    ", type(static_commands).__name__)
    print("capability commands:", type(capability_commands).__name__)
    assert type(static_commands) is not type(capability_commands)

    print("static viewer:      ", type(static_room.frame_viewer).__name__)
    print("capability viewer:  ", type(capability_room.frame_viewer).__name__)
    assert type(static_room.frame_viewer) is not type(
        capability_room.frame_viewer)

    # Everything else is the same class on both - inherited, untouched.
    for fixture in ("workstation", "event_system", "memory_system"):
        static_kind = type(getattr(static_room, fixture)).__name__
        capability_kind = type(getattr(capability_room, fixture)).__name__
        assert static_kind == capability_kind, fixture
        print(f"  {fixture:16s} same on both: {static_kind}")

    # AUTHORITY BY ABSENCE. These are not refusals you catch - they are
    # methods that were never put on the class.
    mutating = ("meld", "link", "sever_link", "create_lesser_conduit",
                "create_cluster", "delete_cluster", "join_cluster",
                "leave_cluster")
    print()
    print("verb                     static  capability")
    for verb in mutating:
        on_static = hasattr(static_commands, verb)
        on_capability = hasattr(capability_commands, verb)
        print(f"  {verb:22s} {str(on_static):6s}  {on_capability}")
        assert on_static is False, f"static must not carry {verb}"
        assert on_capability is True, f"capability must carry {verb}"

    # REUSE IS NOT CREATION. The static room can meld something that
    # already exists - it just cannot bring anything new into being.
    assert hasattr(static_commands, "meld_existing_spell") is True
    assert hasattr(capability_commands, "meld_existing_spell") is True
    print()
    print("meld_existing_spell on both: reuse is not creation")

    # The shared read surface lives on the base and is present either way.
    for shared in ("find_spell_id", "get_spell_permissions", "snapshot_state",
                   "describe_spells_in_conduit", "get_conduit_by_name"):
        assert hasattr(static_commands, shared), shared
        assert hasattr(capability_commands, shared), shared
    print("shared read surface present on both")

    # THE AIX DOOR. Ask the room what it can do rather than probing it.
    static_verbs = static_commands.list_supported_command_methods()
    capability_verbs = capability_commands.list_supported_command_methods()
    print()
    print("static supports    ", len(static_verbs), "command methods")
    print("capability supports", len(capability_verbs), "command methods")
    assert len(capability_verbs) > len(static_verbs), (
        "capability is the broader surface by construction"
    )

    print()
    print("one property differs: command_system. that IS the room kind.")
    print("authority is granted by class membership, never denied by guard")


if __name__ == "__main__":
    main()
