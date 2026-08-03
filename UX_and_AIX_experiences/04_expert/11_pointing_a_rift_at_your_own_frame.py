"""
TIER: expert (11)
GOAL: AR ONTO YOUR OWN WORLD. Advanced 09 built a Rift and deliberately
      stopped short of targeting - it said so in its own text, because
      until 2026-08-03 the capability was genuinely unreachable from
      `import melder`. This is the lesson that finishes it.

      THE CHAIN, AND EVERY LINK IS A REFUSAL POINT

        1. POSTURE   book.configure_aether_frame(rift_enabled=True)
        2. PUBLISH   book.conjure()            -> descriptor truth exists
        3. ENABLE    nexus.activate(config)    -> the Rift domain is live
        4. CREATE    nexus.create_rift(...)    -> a Rift with one room
        5. ATTACH    rift.create_frame_link(frame_name)

      Step 5 is the one that matters, and it is where three separate
      gates fire. `Nexus._validate_target_frame_runtime_requirements`
      demands, IN ORDER:

        rift_enabled=True  on the target frame           - ALWAYS
        ai_native_enabled  on the target frame           - codegen rooms
        system_state == dynamic                          - codegen rooms

      WHY rift_enabled DEFAULTS FALSE, AND SHOULD
      It is the frame's OPT-IN TO BEING OBSERVED. A world does not become
      inspectable because something else decided to look at it. You say
      so, once, before the frame settles - and after conjure the posture
      is frozen, so a world's observability is fixed for its whole life.

      THE PART WORTH SITTING WITH
      Melder does not check permissions when the AR asks a question. It
      checks them when the AR ATTACHES, and then never again. Attachment
      is the authority boundary; everything after it is reading a world
      that already agreed to be read.

      AND THE ORDER IS NOT NEGOTIABLE. Posture must precede conjure,
      because conjure freezes it. Conjure must precede attach, because
      attach requires descriptor truth. Get it wrong and you get a
      refusal that names which link broke, not a mysterious empty view.
SURFACE EXERCISED: configure_aether_frame(rift_enabled=..., ai_native=...),
                   Nexus.create_rift, Rift.create_frame_link, and the
                   runtime-posture gate behind it
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


class Ledger:
    pass


def _postured_frame(frame_name: str, *, dynamic: bool = False) -> None:
    """Build one frame with the posture AR needs, then settle it."""
    book = md.Spellbook(aetheric_frame=frame_name)
    # binding_name keeps the spell_id distinct per frame - identity is
    # process-wide and the frame is not in the fingerprint (advanced 02).
    book.bind(spell=Ledger, existence="unique", binding_name=frame_name)
    if dynamic:
        book.configure_aether_frame(
            system_state="dynamic",
            disposal=None,
            disposal_method_names=None,
            rift_enabled=True,
            ai_native=True,
        )
    else:
        book.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            rift_enabled=True,
        )
    # Conjure PUBLISHES the descriptor and FREEZES the posture. Both are
    # preconditions for attachment, and both happen here.
    book.conjure(name=f"{frame_name}-root")


def main() -> None:
    # A frame that never opted in. This is the default, on purpose.
    closed = md.Spellbook(aetheric_frame="closed-world")
    closed.bind(spell=Ledger, existence="unique", binding_name="closed-world")
    closed.conjure(name="closed-root")

    # ...and two that did.
    _postured_frame("observable")
    _postured_frame("workshop", dynamic=True)
    print("three frames: one default, one rift-enabled, one AI-native")

    # The Rift domain has to be live before any of this matters.
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    nexus.activate(system_configuration)
    assert nexus.is_activated is True
    print("nexus activated")

    # A capability room, then ATTACH it to the world that opted in.
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("capability")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="observer")
    rift.mark_active()
    rift.create_frame_link("observable")
    print()
    print("attached: a capability rift now targets 'observable'")

    # THE GATE, PROVEN. The same call against the default frame refuses,
    # and the message names the reason rather than the symptom.
    try:
        rift.create_frame_link("closed-world")
        raise AssertionError("expected a refusal: rift_enabled is False")
    except ValueError as error:
        assert "rift_enabled" in str(error)
        print("refused 'closed-world' -", error)

    # A CODEGEN room raises the bar twice more: ai_native AND dynamic.
    codegen_configuration = nexus.create_rift_configuration()
    codegen_configuration.with_space_type("codegen")
    codegen_rift = nexus.create_rift(configuration=codegen_configuration,
                                     rift_name="maker")
    codegen_rift.mark_active()

    # 'observable' is rift-enabled but NOT ai-native, so codegen refuses it
    # while capability accepted it. Same frame, different room, different
    # answer - the posture is read against what the room can DO.
    try:
        codegen_rift.create_frame_link("observable")
        raise AssertionError("expected a refusal: codegen needs ai_native")
    except ValueError as error:
        print()
        print("codegen refused 'observable' -", error)

    codegen_rift.create_frame_link("workshop")
    print("codegen attached to 'workshop', which is dynamic AND ai-native")

    print()
    print("attachment is the authority boundary - checked once, there")
    print("a frame is observable because IT said so, before it settled")


if __name__ == "__main__":
    main()
