"""
TIER: intermediate (35)
GOAL: ONE CONFIGURATION FOR EVERY BOOK. When several books make up one
      subsystem, per-book configs drift - one book's teardown
      vocabulary says "close", another forgot it. The fix is ONE
      SpellbookConfiguration for the whole subsystem.

      FIRST, THE DEFAULT: configuration is PER-BOOK. Every Spellbook
      mints its own SpellbookConfiguration at construction (with
      defaults loaded), even when two books sit on the SAME frame.
      Nothing is shared until you say so.

      Two ways to say so:

      1) MANUAL SHARE (this lesson, fully public): build one config and
         hand THE SAME OBJECT to every book. One policy, by reference.

      2) FRAME-OWNED SHARE (the aetheric_frame_configuration knob
         shared_framewide_spellbook_configuration): the FRAME owns one
         config and later books ADOPT it - no passing required. This
         takes TWO steps, and the flag alone does nothing:

           step 1 - THE SWITCH: the frame's posture must carry
                    shared_framewide_spellbook_configuration=True.
                    While it is False every sharing path early-outs.
           step 2 - PUBLICATION: one book must call
                    configure_aether_frame(), which freezes that book's
                    config and binds it to the frame. FIRST ONE WINS.
                    conjure() does NOT publish - only that door does.

         After both steps, every book built on that frame adopts the
         frame-owned object at construction and reports
         is_configuration_locked() == True; handing a DIFFERENT config
         to a later book on that frame is refused. Adoption is total -
         there is no per-book override once the frame owns the policy -
         and a book's cleanup() leaves the shared object alone.

         NOTE: the switch has NO public door today (recorded finding,
         same family as the devops brakes). The probes pin both the
         per-book default and the switch+publish machinery through the
         retained frame posture until a door exists.
SURFACE EXERCISED: one configuration object across multiple books
"""
import melder as md


class ServiceA:
    pass


class ServiceB:
    pass


def main() -> None:
    # THE DEFAULT: two books, two configurations. Nothing shared.
    solo_a = md.Spellbook(aetheric_frame="drifting-world")
    solo_b = md.Spellbook(aetheric_frame="drifting-world")
    assert solo_a.get_configuration() is not solo_b.get_configuration()
    print("default: same frame, two separate configurations")

    # ONE policy object for the whole subsystem.
    shared = md.SpellbookConfiguration()
    shared.with_defaults()
    shared.set_property("phase_scheduler_workers_per_spellbook", 1)

    book_a = md.Spellbook(configuration=shared)
    book_b = md.Spellbook(configuration=shared)

    # Both books read THE SAME object - one teardown story, one
    # scheduler policy, no drift possible.
    assert book_a.get_configuration() is book_b.get_configuration()
    print("two books, one configuration object:",
          book_a.get_configuration() is shared)

    book_a.bind(spell=ServiceA, existence="unique")
    book_b.bind(spell=ServiceB, existence="unique")
    conduit_a = book_a.conjure()
    conduit_b = book_b.conjure()
    assert isinstance(conduit_a.meld(spell=ServiceA), ServiceA)
    assert isinstance(conduit_b.meld(spell=ServiceB), ServiceB)
    print("both worlds conjured under the one shared policy")


if __name__ == "__main__":
    main()
