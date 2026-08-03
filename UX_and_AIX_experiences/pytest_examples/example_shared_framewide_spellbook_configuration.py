"""
EXAMPLE: shared_framewide_spellbook_configuration

ONE SpellbookConfiguration owned by the FRAME, adopted by every book on
it. No config passed to anybody after the first publish.

WHY THIS FILE LIVED BESIDE THE PROBES: step 2 needed the frame posture,
and no public door reached it - so the file could not obey the tier rule
that lessons import `melder as md` only. That condition is now MET.
configure_aether_frame() accepts shared_framewide_spellbook_configuration
as of 2026-08-03, step 2 below is one public call, and this file is
READY TO MOVE INTO 02_intermediate/ on the owner's numbering call.

WHY THE SWITCH AND THE PUBLISH ARE ONE CALL
configure_aether_frame() is not a pure posture setter: it writes posture,
then FREEZES the rich spellbook configuration and binds it to the frame.
So the policy must be shaped BEFORE the call, and the switch travels IN
it - posture is applied first inside the method, so the bind that follows
in the same call already sees shared=True. Flipping the switch in an
earlier call would freeze the config before step 2 could shape it.

THE FOUR STEPS
  1. build the first book - this mints the frame and its posture
  2. shape the policy on that first book's config - this object is about
     to become the whole frame's policy
  3. ONE PUBLIC CALL: configure_aether_frame(
         shared_framewide_spellbook_configuration=True) sets the switch on
     the frame-owned posture, freezes the policy, and binds it to the
     frame. Must happen BEFORE the frame's first conjure: conjure binds and
     FREEZES the posture (aetheric_frame.py:667-726) and the setter is
     refused once frozen (aetheric_frame_configuration.py:653). conjure()
     is the other publish door (spellbook_creation_system.py:296-300) -
     FIRST ONE WINS
  4. every book built after that ADOPTS the frame-owned object at
     construction and comes back locked
"""
import melder as md


class Alpha:
    pass


class Beta:
    pass


class Gamma:
    pass


FRAME = "one-config-world"


def main() -> None:
    # ---- step 1: first book mints the frame and its posture -----------
    first = md.Spellbook(aetheric_frame=FRAME)

    # A book that exists BEFORE publication. Watch it converge in step 5.
    early = md.Spellbook(aetheric_frame=FRAME)
    assert early.get_configuration() is not first.get_configuration()

    # ---- step 2: shape the policy the whole frame will run under -----
    # Shape it FIRST. The publish call below freezes this object.
    policy = first.get_configuration()
    policy.set_property("phase_scheduler_workers_per_spellbook", 1)

    # ---- step 3: THE SWITCH AND THE PUBLISH, IN ONE PUBLIC CALL ------
    # The posture object is frame-owned; every book on the frame holds
    # this same reference, so the switch set through `first` is set for
    # the frame. configure_aether_frame applies posture BEFORE it freezes
    # and binds, so the bind in this same call already sees shared=True.
    # disposal/disposal_method_names are idempotent set-once keys and
    # load_default_dictionary() already set them on an auto-minted book,
    # so pass None. system_state=None leaves the mode alone.
    first.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        shared_framewide_spellbook_configuration=True,
    )
    assert first.is_configuration_locked() is True
    print("published:", policy is first.get_configuration())

    # ---- step 4: ADOPTION - nothing passed, nothing configured -------
    second = md.Spellbook(aetheric_frame=FRAME)
    assert second.get_configuration() is policy
    assert second.is_configuration_locked() is True
    assert second.get_configuration().get_property(
        "phase_scheduler_workers_per_spellbook"
    ) == 1
    print("second book adopted the frame's config, locked, never asked")

    # Handing a DIFFERENT config to a later book is refused outright.
    try:
        md.Spellbook(
            aetheric_frame=FRAME,
            configuration=md.SpellbookConfiguration(FRAME),
        )
        raise AssertionError("expected the frame to refuse a rival config")
    except RuntimeError as error:
        print("rival config refused:", error)

    # ---- step 5: the pre-existing book CONVERGES at its own conjure ---
    # It still holds its private config right now...
    assert early.get_configuration() is not policy
    early.bind(spell=Gamma, existence="unique")
    early.conjure(name="early")
    # ...and conjure swapped it onto the frame-owned object and cleaned
    # up the local one (spellbook.py:5626-5650).
    assert early.get_configuration() is policy
    assert early.is_configuration_locked() is True
    print("pre-existing book converged onto the shared config at conjure")

    # ---- everything runs under the one policy ------------------------
    first.bind(spell=Alpha, existence="unique")
    second.bind(spell=Beta, existence="unique")
    conduit_one = first.conjure(name="first")
    conduit_two = second.conjure(name="second")
    assert isinstance(conduit_one.meld(spell=Alpha), Alpha)
    assert isinstance(conduit_two.meld(spell=Beta), Beta)
    print("three books, three worlds, ONE configuration object")


if __name__ == "__main__":
    main()
