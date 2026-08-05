"""
TIER: expert (06)
GOAL: THE LAST TWO PUBLIC NAMES, and what they say about the whole
      configuration story the curriculum has been tracking since
      advanced 07.

      MutationResearchConfiguration has exactly TWO knobs:
        with_unrestricted_module_mutations(enabled)
        with_lane_type_enforcement(enabled)

      Two. That is the entire configurable surface of a subsystem with 49
      public methods, and the smallness is the point - the research plane
      records what happened; it does not need a policy engine to do it.
      Compare AethericFrameConfiguration's fourteen (advanced 05): a
      frame is a WORLD and needs a law book. A research set is a LEDGER
      and needs almost nothing.

      WHAT THE TWO KNOBS ACTUALLY GOVERN
        unrestricted_module_mutations - whether the plane will record
          mutations that reach outside a spell's own module. Off is the
          conservative posture.
        lane_type_enforcement - whether LaneType (expert 03) is a RULE or
          a LABEL. You met this on the ResearchSet as a live setter; here
          is where the default comes from.
      That second one is worth noticing: the SAME switch exists in two
      places, at two scopes. The configuration sets the default for new
      sets; ResearchSet.set_lane_type_enforcement overrides it per set.
      A knob at both scopes is a deliberate answer to "is this a
      house rule or a per-experiment choice" - melder says both.

      AND THE BUILDER CLOSES THE CONFIGURATION ARC.
      Advanced 17 measured nine public configuration objects carrying
      FIVE different terminator sets. This builder is the most generous
      shape in that table, tied with the crystallizer's:

        build()     hand me the configuration
        finalize()  ...frozen
        activate()  ...and in force

      ONE TERMINATOR PER RUNG. You choose where to get off the ladder,
      instead of always landing on rung one and climbing manually the way
      AetherConfigurationBuilder makes you.

      THE LADDER, ONE LAST TIME (and this is the fourth subsystem):
        Aether            caller activates the config     (advanced 07)
        Crystallizer      caller activates the config     (advanced 17)
        MutationResearch  caller activates the config     (here)
        Nexus             activate() finalizes it FOR you (advanced 08)
      Three to one. Caller-driven activation is the house rule and Nexus
      is the exception - which is worth knowing before you meet a fifth
      subsystem and have to guess.

      AND THE FOURTH ROOT HAS CAUGHT UP. Nexus was once the one root of
      four with NO builder at all - its callers built the configuration
      by hand while every other root handed one over. It now carries the
      same three exits, so the generosity table above is no longer
      lopsided. What has NOT changed is the two-bits rule: the builder's
      `activate()` marks the CONFIGURATION active, and you must still
      pass it to `Nexus.activate(...)`. Two objects, two bits.

      THE EXITS ARE ONE-SHOT, WHICH IS THE POINT OF A BUILDER.
      Each exit TRANSFERS OWNERSHIP and consumes the builder; a second
      exit raises. That is what makes a builder different from a config
      you keep poking - there is exactly one owner at each step, and the
      handoff is the moment ownership moves.

      AND `build()` EARNS ITS PLACE ON THIS ROOT. The builder mirrors
      only the one knob almost everyone sets; the configuration carries a
      far wider `with_*` surface (frame allow/deny lists, tokens, nested
      rift policy). `build()` is the exit that hands you back something
      still MUTABLE so you can reach the rest. A frozen-only builder
      would have made the wide surface unreachable through it.
SURFACE EXERCISED: md.MutationResearchConfiguration,
                   md.MutationResearchConfigurationBuilder,
                   md.NexusConfiguration, md.NexusConfigurationBuilder
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness; the Nexus
        builder section added 2026-08-04 and not yet run.
"""
import melder as md


def main() -> None:
    # TWO KNOBS. That is the whole configurable surface.
    knobs = ("with_unrestricted_module_mutations", "with_lane_type_enforcement")
    for knob in knobs:
        assert hasattr(md.MutationResearchConfiguration, knob), knob
        assert hasattr(md.MutationResearchConfigurationBuilder, knob), knob
    print("configurable surface:", len(knobs), "knobs")
    for knob in knobs:
        print("   ", knob)

    # For contrast - the frame's law book, from advanced 05.
    print()
    print("AethericFrameConfiguration carries 14. A frame is a WORLD.")
    print("A research set is a LEDGER - it needs almost nothing.")

    # THE CONFIG'S OWN LADDER. finalize seals, activate enables, and they
    # are two bits (advanced 07's headline, still true four subsystems on).
    config = md.MutationResearchConfiguration()
    config.with_defaults()
    assert config.activated is False
    config.finalize()
    assert config.activated is False, "finalize seals; it does not enable"
    config.activate()
    assert config.activated is True
    print()
    print("config ladder: with_defaults -> finalize (sealed) -> activate (in force)")

    # THE BUILDER: ONE TERMINATOR PER RUNG. Pick your exit.
    for terminator in ("build", "finalize", "activate"):
        assert hasattr(md.MutationResearchConfigurationBuilder, terminator)
    print()
    print("builder terminators: build / finalize / activate - one per rung")

    built = md.MutationResearchConfigurationBuilder().with_defaults().build()
    assert isinstance(built, md.MutationResearchConfiguration)
    print("  build()    ->", type(built).__name__, "| activated:", built.activated)

    ready = md.MutationResearchConfigurationBuilder().with_defaults().activate()
    assert isinstance(ready, md.MutationResearchConfiguration)
    assert ready.activated is True
    print("  activate() -> already in force, no manual rung 2")

    # THE CONTRAST THAT MAKES THE POINT. Aether's builder offers ONE exit
    # and leaves the rest to you.
    assert not hasattr(md.AetherConfigurationBuilder, "activate")
    print()
    print("AetherConfigurationBuilder offers build() only - rung 2 is yours")
    print("same pattern, different generosity. that divergence is real.")

    # THE FOURTH ROOT CAUGHT UP. Nexus once had no builder at all; it now
    # carries the same three exits as the two most generous shapes above.
    for terminator in ("build", "finalize", "activate"):
        assert hasattr(md.NexusConfigurationBuilder, terminator), terminator
    print()
    print("NexusConfigurationBuilder: build / finalize / activate")
    print("  the root that once had NO builder now matches the table")

    # BUILD() HANDS BACK SOMETHING STILL MUTABLE - and on this root that
    # is the whole reason it exists. The builder mirrors one knob; the
    # configuration carries the wide surface, so you need a mutable exit.
    assert hasattr(md.NexusConfigurationBuilder, "with_rift_creation_enabled")
    assert not hasattr(md.NexusConfigurationBuilder,
                       "with_allowed_target_frame_names")
    assert hasattr(md.NexusConfiguration, "with_allowed_target_frame_names")
    print("  builder mirrors with_rift_creation_enabled, NOT the frame lists")
    print("  -> build() is the exit that keeps the wide surface reachable")

    builder = md.NexusConfigurationBuilder()
    builder.with_defaults().with_rift_creation_enabled(True)
    handed_over = builder.build()
    assert isinstance(handed_over, md.NexusConfiguration)
    assert handed_over.frozen is False, "build() hands back a MUTABLE config"
    handed_over.with_allowed_target_frame_names(["some-frame"])
    print("  build() -> mutable, and the wide surface still applies")

    # ONE-SHOT: the exit TRANSFERS OWNERSHIP and consumes the builder.
    try:
        builder.build()
        raise AssertionError("expected the builder to be consumed")
    except RuntimeError as consumed:
        print("  second build() REFUSED:", str(consumed)[:58])
        print("  one owner at each step - the handoff is ownership moving")

    # THE TWO BITS SURVIVE. A builder that activates the CONFIG has still
    # not turned the Nexus on; that is a separate call on the root.
    ready = md.NexusConfigurationBuilder().with_defaults().activate()
    assert ready.activated is True
    print("  builder.activate() -> config activated, Nexus still OFF")
    print("  two objects, two bits - the rule did not bend for the builder")

    # THE SAME SWITCH AT TWO SCOPES. Configuration sets the default;
    # ResearchSet overrides per set.
    assert hasattr(md.MutationResearchConfiguration, "with_lane_type_enforcement")
    assert hasattr(md.ResearchSet, "set_lane_type_enforcement")
    print()
    print("lane_type_enforcement lives at BOTH scopes:")
    print("   configuration -> the default for new sets")
    print("   ResearchSet   -> the override for one set")
    print("house rule AND per-experiment choice - melder ships both")

    print()
    print("caller-driven activation is the house rule, 3 subsystems to 1")
    print("two knobs is not a gap - a ledger does not need a policy engine")


if __name__ == "__main__":
    main()
