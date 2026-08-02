"""
TIER: advanced (07)
GOAL: TWO DOORS TO ONE CONFIG, AND THE LADDER BEHIND THEM.

      Aether hands you two ways to build its root configuration:
        aether.create_configuration()         -> AetherConfiguration
        aether.create_configuration_builder() -> AetherConfigurationBuilder

      They are NOT redundant, and they do NOT end in the same place by
      accident - they end in the same place ON PURPOSE:

        config.with_*(...).finalize()   ->  FROZEN
        builder.with_*(...).build()     ->  FROZEN

      finalize() freezes and returns THE SAME OBJECT. build() freezes and
      HANDS OVER OWNERSHIP - it is one-shot and consuming, so the builder
      is spent afterwards. Reach for the builder when construction happens
      somewhere that should not keep a handle on the result.

      THE PART EVERYONE GETS WRONG: FROZEN IS NOT READY.

      Freezing and activating are TWO SEPARATE STATE BITS, and this is the
      single most confusing thing about melder's configuration model until
      you see it written down:

        frozen     - "no more edits"     (finalize / build / freeze)
        activated  - "in force"          (activate)

      A config can sit frozen for a long time before anything turns it on.
      So the ladder is three rungs, in this order, and the order is a RULE
      rather than a convention:

        1. finalize() or build()    -> frozen
        2. configuration.activate() -> activated
        3. aether.activate(config)  -> Aether itself comes up

      Skipping rung 2 raises. Aether's own contract says so in capitals:
      "THE CONFIGURATION MUST BE ACTIVATED BEFORE AETHER CAN BE." The two
      failure modes stay distinct on purpose - "not configured" and
      "configuration not activated" are different sentences because they
      are different bugs.

      RUNG 3 IS NOT PERFORMED HERE, DELIBERATELY. Aether is a process-wide
      singleton, and `aether.activate(cfg)` installs the config BEFORE it
      checks the activated bit - so even the refusing call mutates the
      world. A lesson that shares an interpreter with every other lesson
      must not do that. The refusal is pinned in
      pytest_examples/test_advanced_probes.py, where the reset fixture
      owns a clean singleton.
SURFACE EXERCISED: md.Aether().create_configuration,
                   create_configuration_builder, md.AetherConfiguration,
                   md.AetherConfigurationBuilder, the freeze/activate split
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    aether = md.Aether()

    # DOOR 1 - the configuration object, driven fluently.
    # create_configuration() is a FACTORY: it hands back a fresh, UNATTACHED
    # config. Making one does not install it anywhere, which is exactly why
    # this lesson can build several without disturbing the running world.
    config = aether.create_configuration()
    assert isinstance(config, md.AetherConfiguration)
    assert config.frozen is False
    assert config.activated is False
    print("door 1: fresh config - frozen:", config.frozen,
          "activated:", config.activated)

    # finalize() is the fluent terminator: freeze, return THIS object.
    sealed = config.with_defaults().finalize()
    assert sealed is config, "finalize must not clone the configuration"
    assert config.frozen is True
    print("after finalize  - frozen:", config.frozen,
          "activated:", config.activated)

    # THE POINT OF THE LESSON. Two bits, and freezing set only one of them.
    assert config.frozen is True and config.activated is False
    print("frozen is NOT ready - activated is still False")

    # Rung 2. Now it is in force.
    config.activate()
    assert config.activated is True
    print("after activate  - frozen:", config.frozen,
          "activated:", config.activated)

    # DOOR 2 - the builder. Same destination, different ownership story.
    builder = aether.create_configuration_builder()
    assert isinstance(builder, md.AetherConfigurationBuilder)
    built = builder.with_defaults().build()
    assert isinstance(built, md.AetherConfiguration)

    # build() lands on EXACTLY the rung finalize() did: frozen, not
    # activated. The builder is spent; the config belongs to the caller now.
    assert built.frozen is True
    assert built.activated is False
    print("door 2: built config - frozen:", built.frozen,
          "activated:", built.activated)
    print("both doors land on the same rung: frozen, not yet in force")

    # The two configs are separate objects with separate bits - proof that
    # neither door reaches into shared state to do its work.
    assert built is not config
    assert config.activated is True and built.activated is False
    print("independent objects, independent bits")

    print()
    print("finalize/build = frozen. activate = in force. two bits, not one.")
    print("the config activates BEFORE aether does - that ordering is a rule")


if __name__ == "__main__":
    main()
