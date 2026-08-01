"""
TIER: intermediate (35)
GOAL: ONE SPELLBOOK CONFIGURATION SHARED BY EVERY BOOK. When several
      books make up one subsystem, per-book configs drift - one book's
      teardown vocabulary says "close", another forgot it. The fix is
      ONE SpellbookConfiguration for the whole subsystem.

      KNOW WHICH OBJECT YOU ARE TALKING ABOUT. A frame has two:

        * the FRAME POSTURE (AethericFrameConfiguration) - narrow: system
          state, ai-native, rift, the devops brakes. It is SHARED WITH
          EVERY BOOK ON THE FRAME ALREADY, by default, with no opt-in.
          The frame mints exactly one and every Spellbook only borrows
          that reference. Set posture through any one book and every
          book on that frame reads it.

        * the RICH CONFIG (SpellbookConfiguration) - wide: disposal,
          disposal method names, scheduler workers, barrier timeout,
          singleton specialization. THIS one is PER-BOOK by default.
          Two books on the same frame mint two separate ones.

      This lesson is about making the RICH one shared. Two shapes:

      SHAPE 1 - MANUAL SHARE (fully public, works today, shown below):
        1. build ONE SpellbookConfiguration for the frame
        2. set the policy on it once
        3. hand THE SAME OBJECT to every Spellbook you construct
        Every book now reads one policy, by reference. The first conjure
        freezes that object; every later book's conjure re-enters the
        freeze and locks against the same object.

      SHAPE 2 - FRAME-OWNED SHARE (the frame holds the config and later
      books ADOPT it with nothing passed). The machinery is complete and
      it takes exactly two things, in this order:
        1. THE SWITCH - the frame posture must carry
           shared_framewide_spellbook_configuration=True. Every sharing
           path early-outs while it is False. It must be flipped BEFORE
           the frame's first conjure, because the posture freezes on
           that first bind and the switch is refused once frozen.
        2. PUBLICATION - one book binds its rich config to the frame.
           Two doors do this, whichever runs first: configure_aether_
           frame(), and conjure() itself (conjure freezes and binds
           whenever the book is not already locked). FIRST ONE WINS.
        Then every book constructed AFTER that adopts the frame-owned
        object at construction and reports is_configuration_locked()
        True; a book that already existed converges at its own conjure,
        swapping to the shared object and cleaning up its local one.
        Handing a DIFFERENT config to a later book on that frame is
        refused. Adoption is total - no per-book override - and a book's
        cleanup() leaves the shared object alone.

      HONEST GAP: shape 2 has NO public switch today. Nothing in the
      public API sets shared_framewide_spellbook_configuration - every
      construction site in the runtime passes False or omits it, and no
      Spellbook door exposes the retained posture. So shape 1 is the
      answer to "one config for every book" until a door exists. The
      probes pin shape 2's machinery through the private seam so it
      cannot rot while it waits.
SURFACE EXERCISED: one configuration object across multiple books
"""
import melder as md


class ServiceA:
    pass


class ServiceB:
    pass


def main() -> None:
    # THE DEFAULT for the rich config: two books, two configurations.
    solo_a = md.Spellbook(aetheric_frame="drifting-world")
    solo_b = md.Spellbook(aetheric_frame="drifting-world")
    assert solo_a.get_configuration() is not solo_b.get_configuration()
    print("default: same frame, two separate rich configurations")

    # ...while the frame POSTURE was already one object for both books.
    print("posture was shared the whole time - that one needs no opt-in")

    # SHAPE 1, step 1+2: ONE policy object for the whole subsystem.
    shared = md.SpellbookConfiguration()
    shared.with_defaults()
    shared.set_property("phase_scheduler_workers_per_spellbook", 1)

    # SHAPE 1, step 3: hand THE SAME OBJECT to every book.
    book_a = md.Spellbook(configuration=shared)
    book_b = md.Spellbook(configuration=shared)

    # Both books read THE SAME object - one teardown story, one
    # scheduler policy, no drift possible.
    assert book_a.get_configuration() is book_b.get_configuration()
    assert book_a.get_configuration() is shared
    print("two books, one configuration object")

    book_a.bind(spell=ServiceA, existence="unique")
    book_b.bind(spell=ServiceB, existence="unique")
    # Root conduit names are unique PER FRAME, and an unnamed conjure takes
    # the name "default". Two books in one frame therefore need two names -
    # the shared configuration is what they have in common, not their identity.
    conduit_a = book_a.conjure(name="shared-policy-a")
    conduit_b = book_b.conjure(name="shared-policy-b")
    assert isinstance(conduit_a.meld(spell=ServiceA), ServiceA)
    assert isinstance(conduit_b.meld(spell=ServiceB), ServiceB)
    print("both worlds conjured under the one shared policy")


if __name__ == "__main__":
    main()
