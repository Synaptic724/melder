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
        Aether            caller activates the config   (advanced 07)
        Crystallizer      caller activates the config   (advanced 17)
        MutationResearch  caller activates the config   (here)
        Nexus             enable() does it FOR you      (advanced 08)
      Three to one. Caller-driven activation is the house rule and Nexus
      is the exception - which is worth knowing before you meet a fifth
      subsystem and have to guess.
SURFACE EXERCISED: md.MutationResearchConfiguration,
                   md.MutationResearchConfigurationBuilder
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
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
