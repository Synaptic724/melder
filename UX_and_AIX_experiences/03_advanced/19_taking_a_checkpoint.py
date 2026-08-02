"""
TIER: advanced (19)
GOAL: TAKING A CHECKPOINT - and settling which configuration ladder is
      the house rule.

      YOU HAVE NOW SEEN THREE SUBSYSTEMS COME UP.

        lesson 09  Aether       you finalize, you activate the config,
                                THEN aether.activate() - and handing it a
                                merely-frozen config raises
        lesson 10  Nexus        you hand over a config and enable()
                                finalizes it FOR you
        lesson 19  Crystallizer ...follows AETHER.

      The Crystallizer contract says it in the same capitals Aether used:

        "ORDERING RULE: THE CONFIGURATION MUST BE ACTIVATED FIRST...
         Two distinct failure modes: 'not configured' and 'configuration
         not activated'."

      So it is two against one. Caller-driven activation is the house
      rule; Nexus is the exception. That is worth knowing before you meet
      a fourth subsystem - guess Aether's ladder and you will be right
      more often than not.

      AND THE BUILDER HERE IS THE MOST GENEROUS IN THE LIBRARY.
      CrystallizerConfigurationBuilder offers THREE terminators, one per
      rung, so you choose where to get off:

        build()     hand me the configuration
        finalize()  ...frozen
        activate()  ...and in force

      Compare AetherConfigurationBuilder, which offers only build() and
      leaves rung 2 to you. Same pattern, different generosity - which is
      exactly the kind of divergence the configuration-uniformity program
      exists to catalogue.

      THE CHECKPOINT DOOR
        create_checkpoint(profile_name=None, description=None) -> str
      It hands back an ID. Everything else keys off that ID:
        list_checkpoint_ids()        what exists
        describe_checkpoint(id)      what is in one
        analyze_checkpoint(id)       a deeper read
        verify_checkpoint_chain(...) is the lineage intact
      Lesson 20 does the loading half.

      TWO BITS, FIFTH APPEARANCE: activated / is_activated on the
      Crystallizer, and `activated` on its configuration. By now you
      should expect it.
SURFACE EXERCISED: md.Crystallizer, md.CrystallizerConfiguration,
                   md.CrystallizerConfigurationBuilder, create_checkpoint,
                   list_checkpoint_ids, describe_checkpoint
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    crystallizer = md.Crystallizer()
    print("crystallizer activated at start:", crystallizer.activated)
    assert crystallizer.activated is False

    # THE CONFIG. Bare constructor - unlike the frame posture in lesson 08,
    # this one you build empty and fill in.
    config = md.CrystallizerConfiguration()
    config.with_defaults()

    # AETHER'S LADDER, NOT NEXUS'S. Rung 1: seal it.
    config.finalize()
    assert config.activated is False
    print("config finalized - activated:", config.activated)

    # Rung 2: the caller activates. Nexus would have done this for us;
    # Aether and Crystallizer both make it explicit.
    config.activate()
    assert config.activated is True
    print("config activated - activated:", config.activated)

    # Rung 3: the subsystem comes up.
    crystallizer.activate(config)
    assert crystallizer.activated is True
    # NOTE: `is_activated` is a PROPERTY, not a method - calling it gives
    # "TypeError: 'bool' object is not callable". Two read names for one
    # bit, both properties.
    assert crystallizer.is_activated is True
    print("crystallizer activated:", crystallizer.activated)

    # THE THREE-EXIT BUILDER. Same destination, you pick the rung. This is
    # a SECOND configuration object - the one above is already installed.
    builder = md.CrystallizerConfigurationBuilder()
    for terminator in ("build", "finalize", "activate"):
        assert hasattr(builder, terminator), terminator
    print()
    print("CrystallizerConfigurationBuilder terminators: build/finalize/activate")
    print("AetherConfigurationBuilder offers only build() - rung 2 is yours")

    ready = md.CrystallizerConfigurationBuilder().with_defaults().activate()
    assert isinstance(ready, md.CrystallizerConfiguration)
    assert ready.activated is True
    print("builder.activate() -> a config already in force")

    # ------------------------------------------------------------------
    # THE CHECKPOINT
    # ------------------------------------------------------------------
    before = crystallizer.list_checkpoint_ids()
    assert isinstance(before, list)
    print()
    print("checkpoints before:", len(before))

    checkpoint_id = crystallizer.create_checkpoint(
        description="advanced lesson 19 - first checkpoint",
    )
    assert isinstance(checkpoint_id, str) and checkpoint_id
    print("created checkpoint:", checkpoint_id)

    after = crystallizer.list_checkpoint_ids()
    assert checkpoint_id in after
    assert len(after) == len(before) + 1
    print("checkpoints after: ", len(after))

    # THE ID IS THE HANDLE. Everything else keys off it.
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert isinstance(described, dict)
    print("describe_checkpoint ->", len(described), "keys")
    print("  keys:", sorted(described)[:6])

    # A second checkpoint gets its own id - they are not overwritten.
    second_id = crystallizer.create_checkpoint(description="second")
    assert second_id != checkpoint_id
    assert len(crystallizer.list_checkpoint_ids()) == len(before) + 2
    print("second checkpoint is a distinct id, not an overwrite")

    print()
    print("caller-driven activation is the house rule - nexus is the exception")
    print("create_checkpoint hands back an ID; the ID is the whole handle")


if __name__ == "__main__":
    main()
