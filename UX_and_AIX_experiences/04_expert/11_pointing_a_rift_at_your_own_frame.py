"""
TIER: expert (11)
GOAL: AR ONTO YOUR OWN WORLD. Advanced 09 built a Rift and deliberately
      stopped short of targeting - it said so in its own text, because
      until 2026-08-03 the capability was genuinely unreachable from
      `import melder`. This is the lesson that finishes it.

      THE CHAIN, AND EVERY LINK IS A REFUSAL POINT

        1. POSTURE   book.configure_aether_frame(rift_enabled=True)
        2. PUBLISH   book.conjure()            -> descriptor truth exists
        3. ALLOW     config.with_allowed_target_frame_names([...])
        4. ENABLE    nexus.activate(config)    -> the Rift domain is live
        5. CREATE    nexus.create_rift(...)    -> a Rift with one room
        6. ATTACH    rift.create_frame_link(frame_name)

      ATTACHMENT IS TWO-PARTY CONSENT, AND THAT IS THE WHOLE LESSON

      Step 6 runs TWO INDEPENDENT GATES, owned by two different parties,
      in this order (`Rift.create_frame_link`):

        A. THE OBSERVER'S POLICY  Nexus._validate_target_frame_names
             denied_target_frame_names   - deny is checked FIRST and wins
             allowed_target_frame_names  - and it is NOT EMPTY by default

        B. THE WORLD'S POSTURE    _validate_target_frame_runtime_requirements
             rift_enabled=True   on the target frame      - ALWAYS
             ai_native_enabled   on the target frame      - codegen rooms
             system_state == dynamic                      - codegen rooms

      NEITHER SIDE CAN GRANT ALONE. The Nexus says which worlds it may
      ever reach; the frame says whether it consents to being read. A
      perfectly postured frame that is not on the allow-list refuses, and
      an allow-listed frame with no posture refuses. Both refusals appear
      below, because seeing only one of them teaches half the model.

      THE DEFAULT ALLOW-LIST IS `("default",)` - NOT EMPTY
      That is the detail that surprises everyone, including whoever wrote
      the first draft of this lesson. An EMPTY allow-list would mean "no
      restriction" (the check is skipped when it is falsy). Melder ships a
      one-name list instead, so a fresh Nexus can target exactly one
      conventionally-named world and every other world must be named
      deliberately. Default-deny, expressed as data rather than as a flag.

      AND IT ONLY GOVERNS FOREIGN WORLDS. Nexus-managed frames skip gate A
      entirely - a Nexus does not need to put itself on its own allow-list.

      THERE IS ALSO A BUDGET, AND IT IS NEXUS-WIDE
        allow_multiple_target_frames  default False
        max_target_frame_count        default 1
      Target frames are REF-COUNTED ACROSS RIFTS, so two rifts attaching
      two different worlds spend two of the budget, not one each. Attach a
      second world with the defaults in place and you get "Multiple target
      frames are disabled." - which is a budget refusal, not a policy one.

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
                   with_allowed_target_frame_names,
                   with_multiple_target_frames, with_max_target_frame_count,
                   Nexus.create_rift, Rift.create_frame_link, both gates
VERIFY: RUN GREEN on the owner's 3.14t run 2026-08-03.
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

    # ...and three that did. 'unlisted' is postured EXACTLY like
    # 'observable' - the only thing that will differ is the Nexus's own
    # policy, which is how we isolate gate A from gate B.
    _postured_frame("observable")
    _postured_frame("unlisted")
    _postured_frame("workshop", dynamic=True)
    print("four frames: one default, two rift-enabled, one AI-native")

    # The Rift domain has to be live before any of this matters - and the
    # NEXUS has to be told which worlds it may reach. The shipped
    # allow-list is ("default",), so every frame here is foreign to it.
    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names(
        ["observable", "workshop", "closed-world"],
    )
    # Two worlds get attached below, and the budget is NEXUS-WIDE.
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(4)
    nexus.activate(system_configuration)
    assert nexus.is_activated is True
    print("nexus activated; allow-list names 3 of the 4 worlds")

    # A capability room, then ATTACH it to the world that opted in AND is
    # named by the observer's policy. Both parties agreed.
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("capability")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="observer")
    rift.mark_active()
    rift.create_frame_link("observable")
    print()
    print("attached: a capability rift now targets 'observable'")

    # GATE A - THE OBSERVER SAID NO. 'unlisted' is postured identically to
    # 'observable'; the only difference is that the Nexus never named it.
    # The frame's consent is irrelevant here, and note WHICH gate answers:
    # policy is checked BEFORE posture is ever consulted.
    try:
        rift.create_frame_link("unlisted")
        raise AssertionError("expected a refusal: not on the allow-list")
    except ValueError as error:
        assert "not allowed by Nexus policy" in str(error)
        print("refused 'unlisted' -", error)
        print("  same posture as 'observable' - the OBSERVER refused it")

    # GATE B - THE WORLD SAID NO. 'closed-world' IS on the allow-list, so
    # policy passes and the posture gate answers instead. Opposite party,
    # opposite reason, and the message names which.
    try:
        rift.create_frame_link("closed-world")
        raise AssertionError("expected a refusal: rift_enabled is False")
    except ValueError as error:
        assert "rift_enabled" in str(error)
        print("refused 'closed-world' -", error)
        print("  allow-listed, but never opted in - the WORLD refused it")

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

    # THE BUDGET IS NEXUS-WIDE, NOT PER RIFT. Two rifts, two different
    # worlds, and they spent TWO of max_target_frame_count between them -
    # which is why this lesson had to raise the cap from its default of 1
    # even though no single rift targets more than one world.
    print()
    print("two rifts hold two target frames; the cap is shared, not")
    print("per-rift - target frames are ref-counted across the Nexus")

    print()
    print("attachment is the authority boundary - checked once, there")
    print("a frame is observable because IT said so, before it settled")
    print("and reachable because the OBSERVER said so - both, or neither")


if __name__ == "__main__":
    main()
