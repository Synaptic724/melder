"""
TIER: advanced (11)
GOAL: OPENING A RIFT - and meeting melder's most repeated law for the
      third time in three lessons.

      THE PATH (each step needs the one above it)
        nexus = md.Nexus()
        nexus.enable(nexus.create_system_configuration())    # lesson 10
        rift_config = nexus.create_rift_configuration()
        rift_config.with_space_type("static")
        rift = nexus.create_rift(configuration=rift_config, rift_name="ops")

      THE RIFT CONFIGURATION IS CONSUMED.
      create_rift() takes ownership. Hand the same configuration to a
      second create_rift() and it refuses with "RiftConfiguration has
      already been consumed." One configuration, one rift - the same
      one-shot law AetherConfigurationBuilder.build() follows (lesson 09).
      If you want two rifts, you ask the factory twice.

      THE LAW YOU HAVE NOW SEEN THREE TIMES
      Melder never conflates "this exists" with "this is live". Every
      subsystem splits it into two bits, and only the names change:

        lesson 09  config   frozen         / activated
        lesson 10  nexus    is_configured  / is_enabled
        lesson 11  rift     is_registered  / is_active

      Once you have seen it three times it stops being trivia and starts
      being the thing you predict. When you meet a melder object you have
      never used, look for its two bits first - presence and liveness are
      always separate questions, and the answer to one never implies the
      other.

      WHAT THIS LESSON DELIBERATELY DOES NOT DO: AR targeting. That needs
      `rift_enabled` on the target frame's posture, and there is no public
      door that sets it (pinned in test_advanced_probes). Rifts, rooms and
      workstations are reachable; dynamic AR targeting is not, today.
SURFACE EXERCISED: md.Nexus.create_rift_configuration, create_rift,
                   md.RiftConfiguration, md.Rift, md.RiftSpaceType
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    nexus = md.Nexus()

    # A rift needs a live nexus underneath it - lesson 10's ladder.
    system_config = nexus.create_system_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.enable(system_config)
    assert nexus.is_enabled is True
    print("nexus enabled; rift creation permitted")

    # The per-rift configuration is its own object with its own factory.
    # Note the shape is identical to every other config in melder: with_*
    # verbs that mutate and return self, ending in a terminator.
    rift_config = nexus.create_rift_configuration()
    assert isinstance(rift_config, md.RiftConfiguration)
    rift_config.with_space_type("static")
    rift_config.with_space_name("health")
    print("rift configuration staged: static room named 'health'")

    # create_rift finalizes the configuration on the way through - the same
    # courtesy Nexus.enable() extended in lesson 10, and still the opposite
    # of what Aether does.
    rift = nexus.create_rift(configuration=rift_config, rift_name="ops")
    assert isinstance(rift, md.Rift)
    print("rift opened:", rift.rift_name, "| id:", rift.id)

    # ONE CONFIGURATION, ONE RIFT. The object was consumed by the call.
    try:
        nexus.create_rift(configuration=rift_config, rift_name="ops-again")
        raise AssertionError("expected ValueError: configuration consumed")
    except ValueError as error:
        print("second use refused:", error)

    # THE TWO BITS, third appearance. Creation registered it; being
    # registered is not the same as being live.
    assert rift.is_registered is True
    print("after create - registered:", rift.is_registered,
          "active:", rift.is_active)

    rift.mark_active()
    assert rift.is_active is True
    print("after mark_active - registered:", rift.is_registered,
          "active:", rift.is_active)

    rift.mark_inactive()
    assert rift.is_active is False
    assert rift.is_registered is True, "liveness went; registration stayed"
    print("after mark_inactive - registered:", rift.is_registered,
          "active:", rift.is_active)

    # The rift owns a concrete room and a gate. The room's kind came from
    # the configuration; the gate is the entry control (lesson 12 uses it).
    assert rift.space is not None
    assert rift.rift_gate is not None
    print("room:", type(rift.space).__name__,
          "| gate:", type(rift.rift_gate).__name__)

    # Nexus is the registry - the rift can be found by id and by name.
    assert nexus.has_rift(rift.id) is True
    assert rift.id in nexus.list_rift_ids()
    print("registered with nexus; rift ids:", len(nexus.list_rift_ids()))

    print()
    print("one configuration, one rift - create_rift consumes it")
    print("presence and liveness are ALWAYS two bits, whatever they are named")


if __name__ == "__main__":
    main()
