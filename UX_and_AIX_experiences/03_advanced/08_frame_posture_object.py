"""
TIER: advanced (08)
GOAL: THE POSTURE OBJECT ITSELF. Lesson 07 mapped the 15 knobs; this one
      picks the object up and handles it. The headline: this config is
      CONSTRUCTOR-FIRST, not fluent-first - alone among melder's configs.

      Four values are REQUIRED keyword-only arguments at construction:
        origin_spellbook_id / system_state / ai_native_enabled / rift_enabled
      There is no bare AethericFrameConfiguration(). You cannot start empty
      and fill it in. The world's identity and mode are declared up front,
      and the with_* chain REFINES that declaration - it never originates it.

      That is the mechanical difference between this config and
      SpellbookConfiguration, which you build empty and populate.

      Three laws this lesson proves:
        1. with_* MUTATES THIS OBJECT and returns self. It is fluent in
           SHAPE, not in semantics - there is no copy, ever. The frame's
           settlement law requires the RETAINED object to be the bound one.
        2. validate() RAISES; it does not return False. The bool return is
           a convention, not a verdict channel. ai_native_enabled requires
           system_state dynamic, and violating it is an exception.
        3. finalize() freezes and returns THE SAME INSTANCE - the fluent
           terminator. After it, every with_* refuses.
SURFACE EXERCISED: md.AethericFrameConfiguration (system_state passed as
                   the string "automatic" / "dynamic")
VERIFY: rides the owner's 3.14t run; asserts are the contract.

FINDING (init surface, for the owner's program): this type is exported from
the public root and CANNOT BE INSTALLED from it. Spellbook.__init__ accepts
(aetheric_frame, configuration, logger) - `configuration` is a
SpellbookConfiguration, not this. Every path that reaches the live frame
posture is private (_initialize_aetheric_frame_configuration,
_bind_aetheric_frame_configuration_to_aether). The one public door,
Spellbook.configure_aether_frame(...), takes four arguments of which only
TWO are frame-posture knobs - system_state and system_caching_enabled. The
remaining 13 knobs have no public door at all.

So today this object is READ-SHAPED: construct one to understand the law
book and to hold a posture you intend to describe. Authoring a world's
posture from the public root is not yet possible beyond those two knobs.
"""
import melder as md


def main() -> None:
    # 1. CONSTRUCTOR-FIRST. All four are keyword-only and REQUIRED.
    #    `origin_spellbook_id=None` is legitimate: an unattached posture has
    #    no owning book yet. It gets attributed at freeze time by the frame.
    posture = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="automatic",
        ai_native_enabled=False,
        rift_enabled=False,
    )
    print("constructed:", posture.system_state)
    assert posture.system_state.name == "automatic"
    assert posture.ai_native_enabled is False
    assert posture.rift_enabled is False

    # 2. with_* MUTATES AND RETURNS SELF. Not a copy. Prove it by identity,
    #    because "fluent" in most libraries means "returns a new one" and
    #    here it does not - and the difference is load-bearing.
    same = posture.with_system_caching_enabled(False)
    assert same is posture, "with_* must return THIS object, not a clone"
    assert posture.system_caching_enabled is False
    print("with_* returned the same instance:", same is posture)

    # 3. validate() RAISES. It does not hand back a False for you to ignore.
    #    ai_native_enabled without dynamic is the semantic rule it enforces.
    posture.with_ai_native(True)
    try:
        posture.validate()
        raise AssertionError("expected ValueError: ai_native needs dynamic")
    except ValueError as error:
        print("validate refused:", error)

    # Satisfy the rule the honest way - move the world to dynamic.
    posture.with_system_state("dynamic")
    assert posture.validate() is True
    print("validate passed once the state matched the capability")

    # 4. PRESETS are methods that set several knobs at once, and they follow
    #    the same mutate-and-return-self law.
    preset = md.AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state="automatic",
        ai_native_enabled=False,
        rift_enabled=False,
    )
    assert preset.dynamic_defaults() is preset
    assert preset.system_state.name == "dynamic"
    print("dynamic_defaults() set the mode and returned self")

    # 5. finalize() - the fluent terminator. Freezes, returns THIS instance.
    #    A cloning finalize would be actively harmful here: the settlement
    #    law requires the RETAINED posture object to be the one that binds.
    finalized = posture.finalize()
    assert finalized is posture, "finalize must not clone the posture"
    print("finalize returned the same instance:", finalized is posture)

    # 6. THE FREEZE LAW. One world, one law book, decided before first use.
    try:
        posture.with_system_state("automatic")
        raise AssertionError("expected RuntimeError on a frozen posture")
    except RuntimeError as error:
        print("frozen posture refused the edit:", error)

    # The values survive the freeze - it seals, it does not clear.
    assert posture.system_state.name == "dynamic"
    assert posture.ai_native_enabled is True

    print()
    print("constructor-first: 4 required values, declared not discovered")
    print("with_* refines the declaration and always returns THIS object")
    print("validate raises; finalize seals; the sealed object is the bound one")


if __name__ == "__main__":
    main()
