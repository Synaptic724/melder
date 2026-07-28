"""
EXAMPLE: shared_framewide_spellbook_configuration

ONE SpellbookConfiguration owned by the FRAME, adopted by every book on
it. No config passed to anybody after the first publish.

WHY THIS FILE IS NOT IN 02_intermediate/: step 2 below needs the frame
posture, and there is no public door to it today. Lessons import
`melder as md` only, so this example lives beside the probes until a
door exists. The moment configure_aether_frame() (or anything else)
accepts shared_framewide_spellbook_configuration, step 2 becomes one
public call and this file moves into the tier.

THE FIVE STEPS
  1. build the first book - this mints the frame and its posture
  2. THE SWITCH: shared_framewide_spellbook_configuration = True on the
     frame posture. Must happen BEFORE the frame's first conjure: conjure
     binds and FREEZES the posture (aetheric_frame.py:667-726) and the
     setter is refused once frozen (aetheric_frame_configuration.py:653)
  3. shape the policy on that first book's config - this object is about
     to become the whole frame's policy
  4. PUBLISH: bind it to the frame. Two doors, whichever runs first -
     configure_aether_frame() (spellbook.py:5910) or conjure() itself
     (spellbook_creation_system.py:296-300). FIRST ONE WINS
  5. every book built after that ADOPTS the frame-owned object at
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

    # A book that exists BEFORE publication. Watch it converge in step 6.
    early = md.Spellbook(aetheric_frame=FRAME)
    assert early.get_configuration() is not first.get_configuration()

    # ---- step 2: THE SWITCH ------------------------------------------
    # The posture object is frame-owned; every book on the frame holds
    # this same reference, so flipping it through `first` flips it for
    # the frame. (Private seam - no public door yet.)
    first._aetheric_frame_configuration.\
        with_shared_framewide_spellbook_configuration(True)
    assert (
        early._aetheric_frame_configuration
        .shared_framewide_spellbook_configuration is True
    )

    # ---- step 3: shape the policy the whole frame will run under -----
    policy = first.get_configuration()
    policy.set_property("phase_scheduler_workers_per_spellbook", 1)

    # ---- step 4: PUBLISH ---------------------------------------------
    # disposal/disposal_method_names are idempotent set-once keys and
    # load_default_dictionary() already set them on an auto-minted book,
    # so pass None here. system_state=None leaves posture alone.
    first.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
    )
    assert first.is_configuration_locked() is True
    print("published:", policy is first.get_configuration())

    # ---- step 5: ADOPTION - nothing passed, nothing configured -------
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

    # ---- step 6: the pre-existing book CONVERGES at its own conjure ---
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
