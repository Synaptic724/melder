"""
TIER: advanced (12)
GOAL: THE ROOM. Every Rift owns exactly one, and the law around it is
      stricter than people expect:

        A RIFT OWNS ONE PRIMARY ROOM, ITS KIND IS CHOSEN ONCE AT CREATION,
        AND IT IS NEVER SWITCHED.

      There is no room registry. There is no "active space". There is no
      swap, promote, or re-type verb. `RiftSpaceType` is the single input
      that fixes a Rift's capability posture FOR LIFE, and `Rift` reads it
      at creation to construct the matching `RiftSpace` subclass.

      That is a design choice worth pausing on. A room you can re-type is
      a room whose permissions are a moving target, and every consumer
      holding a reference has to re-ask what it is allowed to do. Fixing
      the kind at birth makes the answer cacheable and makes an audit of
      "what can this rift do" a question about creation, not about now.

      THE FIXTURES - every room carries the same SET, whatever its kind:
        space_id / space_name / owner_rift_id / space_kind / metadata
        frame_viewer     - the read surface (TYPE VARIES BY KIND)
        workstation      - the binding canvas (lesson 14)
        command_system   - the verb surface (TYPE VARIES BY KIND)
        event_system     - rift-local publish/subscribe
        memory_system    - rift-local command/execution records
        action + category hooks - pre/post interception, unregister by id

      So every room has the same fixtures BY NAME, and two of them differ
      BY TYPE: command_system and frame_viewer - what you may DO and what
      you may SEE. The other three are literally the same classes.

      Lesson 13 takes that pair apart. (An earlier draft of these lessons
      claimed only command_system varied; the owner's 3.14t run proved
      frame_viewer varies too, and the corrected version is the better
      story - authority and visibility narrow TOGETHER.)
SURFACE EXERCISED: md.RiftSpace via rift.space, md.RiftSpaceType,
                   the room fixtures, the one-room law
VERIFY: rides the owner's 3.14t run; asserts are the contract.

FINDING (doc drift, 2026-08-02): RiftSpaceType's docstring documents a
fourth member - "dynamic: Legacy alias for codegen. Retained temporarily
so older AR configuration inputs can still normalize during the room
rename." THERE IS NO SUCH MEMBER. The enum defines static, capability and
codegen only, with no _missing_ handler, so RiftSpaceType("dynamic")
raises ValueError. Either the alias was removed and the docstring was not,
or it was never added. Pinned in test_advanced_probes so the docstring
cannot quietly stay wrong.
"""
import melder as md


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_system_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.enable(system_config)

    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type(md.RiftSpaceType.static)
    rift_config.with_space_name("health")
    rift = nexus.create_rift(configuration=rift_config, rift_name="ops")
    rift.mark_active()
    print("rift active:", rift.is_active)

    # ONE ROOM, AND THE SAME ONE EVERY TIME. `space` is not a lookup or a
    # factory - it is THE room, identical by identity on every read.
    room = rift.space
    assert rift.space is room, "a rift has one room, not a room registry"
    print("room:", type(room).__name__, "| kind:", room.space_kind)

    # The room knows who owns it. Ownership is one-directional and fixed.
    assert room.owner_rift_id == rift.id
    assert room.space_name == "health"
    print("space_id:", room.space_id, "| name:", room.space_name)
    print("owner rift:", room.owner_rift_id == rift.id)

    # THE FIXTURES. Same set on every room regardless of kind - the shape
    # is constant, only the authority differs (lesson 13).
    fixtures = {
        "frame_viewer": room.frame_viewer,
        "workstation": room.workstation,
        "command_system": room.command_system,
        "event_system": room.event_system,
        "memory_system": room.memory_system,
    }
    for name, fixture in fixtures.items():
        assert fixture is not None, f"{name} should be present on every room"
        print(f"  {name:16s} {type(fixture).__name__}")

    # THE TYPE IS NOT RE-SETTABLE. There is no verb for it - not a refusal
    # you catch, an ABSENCE you cannot call. Proving a negative honestly
    # means naming what does not exist rather than try/except-ing.
    for absent in ("set_space_type", "switch_space", "promote_space",
                   "retype", "activate_space"):
        assert not hasattr(room, absent), f"{absent} should not exist"
    print("no re-type verb exists - the kind is fixed at creation")

    # The room kind matches what the configuration asked for, and that is
    # the ONLY place it was ever decided.
    assert room.space_kind == md.RiftSpaceType.static.value
    print("configured kind:", md.RiftSpaceType.static.value,
          "-> room kind:", room.space_kind)

    # THE DOC DRIFT, made visible rather than described. The docstring
    # promises a "dynamic" legacy alias; the enum does not have one.
    members = [kind.value for kind in md.RiftSpaceType]
    print("actual members:", members)
    assert "dynamic" not in members
    try:
        md.RiftSpaceType("dynamic")
        raise AssertionError("docstring would be right - alias exists")
    except ValueError:
        print("'dynamic' is documented but NOT defined - docstring is stale")

    print()
    print("one rift, one room, one kind, decided once and never again")
    print("shape is constant across kinds; authority is not")


if __name__ == "__main__":
    main()
