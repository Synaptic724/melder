"""
TIER: advanced (08)
GOAL: TURNING THE NEXUS ON - and discovering that it does NOT climb the
      same ladder Aether does. Lesson 07 taught Aether's rule: freeze,
      then activate, then bring the subsystem up, in that order, or it
      refuses. Nexus reaches the same destination by a different route,
      and knowing which subsystem you are talking to is the whole lesson.

      THE NEXUS PATH
        nexus  = md.Nexus()                        # process-wide, no args
        config = nexus.create_configuration()
        nexus.activate(config)                       # installs AND finalizes
        nexus.is_activated -> True

      THREE ASYMMETRIES WITH AETHER, ALL REAL, NONE ACCIDENTAL:

      1. THE FACTORY PRE-DEFAULTS.
         Aether's create_configuration() hands back a bare config and you
         call with_defaults() yourself. Nexus's create_configuration()
         applies the default property set before returning. Same verb
         shape, different starting state.

      2. ENABLE FINALIZES FOR YOU.
         Aether refuses a merely-frozen config and makes you call
         configuration.activate() first - two bits, your responsibility.
         Nexus.activate() finalizes the installed configuration on its way
         through. You do not pre-seal it, and trying to reason about it
         with Aether's rule in your head will mislead you.

      3. NEITHER FACTORY INSTALLS.
         This one they agree on, and it is worth stating because it is the
         part people assume: create_* is a FACTORY. It builds and hands
         over. Nothing is wired anywhere until you pass it to enable().

      TWO BITS AGAIN, DIFFERENT NAMES
        nexus.is_configured  - a configuration is installed
        nexus.is_activated     - the subsystem is up
      Same shape as frozen/activated in lesson 07. Configuration presence
      and subsystem liveness are always separate questions in melder.
SURFACE EXERCISED: md.Nexus, md.NexusConfiguration,
                   create_configuration, enable, disable
                   (frame mode passed as the string "single")
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    nexus = md.Nexus()
    print("nexus id:", nexus.id)

    # Both bits start down. A constructed Nexus is inert.
    print("start - configured:", nexus.is_configured,
          "enabled:", nexus.is_activated)

    # THE FACTORY. New instance every call, defaults already applied, and
    # nothing installed onto Nexus by the act of creating it.
    config = nexus.create_configuration()
    assert isinstance(config, md.NexusConfiguration)
    second = nexus.create_configuration()
    assert second is not config, "the factory hands back a NEW config each call"
    print("factory: fresh pre-defaulted config, not installed")

    # Still inert - proof that create_* did not wire anything.
    assert nexus.is_activated is False
    print("after create - enabled:", nexus.is_activated)

    # Frame mode is one of three. Pass the NAME - the setter is typed
    # Union[NexusFrameMode, str] and normalizes for you, so a typo is a
    # ValueError at the door rather than a silent default.
    config.with_nexus_frame_mode("single")
    print("frame mode set: single")
    print("available modes:", [mode.name for mode in md.NexusFrameMode])

    # ENABLE. Installs the config and finalizes it on the way through -
    # note that we never called finalize() or freeze() ourselves.
    assert config.frozen is False, "we did not seal it; enable will"
    nexus.activate(config)
    assert nexus.is_configured is True
    assert nexus.is_activated is True
    assert config.frozen is True, "enable finalized the config for us"
    print("after enable - configured:", nexus.is_configured,
          "enabled:", nexus.is_activated, "config frozen:", config.frozen)

    # THE CONTRAST WORTH REMEMBERING. Aether would have refused this exact
    # sequence: it requires configuration.activate() before the subsystem
    # comes up, and says so in its own contract. Nexus does the sealing
    # itself. Two subsystems, two ladders, one codebase.
    print("aether: you seal and activate, THEN aether comes up")
    print("nexus:  you hand it over, enable seals it for you")

    # disable() puts the subsystem back down. The configuration stays
    # installed - liveness went away, configuration did not.
    nexus.deactivate()
    assert nexus.is_activated is False
    assert nexus.is_configured is True
    print("after disable - configured:", nexus.is_configured,
          "enabled:", nexus.is_activated)

    print()
    print("create_* builds and hands over; it never installs")
    print("configured and enabled are separate questions, always")


if __name__ == "__main__":
    main()
