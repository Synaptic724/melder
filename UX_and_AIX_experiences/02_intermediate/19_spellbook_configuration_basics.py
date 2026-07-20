"""
TIER: intermediate (19)
GOAL: SpellbookConfiguration - the book's policy object. with_defaults()
      is easy mode; set_property tunes the knobs; conjure VALIDATES AND
      FREEZES it (frozen config refuses mutation - fail fast, not drift).
SURFACE EXERCISED: md.SpellbookConfiguration, set_property, the freeze law
"""
import melder as md


class Service:
    pass


def main() -> None:
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    book = md.Spellbook(configuration=configuration)
    book.bind(spell=Service, existence="unique")
    conduit = book.conjure()  # validates + freezes the configuration here
    assert isinstance(conduit.meld(spell=Service), Service)
    print("configured, conjured, melded")

    try:
        configuration.set_property("phase_scheduler_workers_per_spellbook", 8)
        print("post-freeze mutation unexpectedly succeeded")
    except Exception as err:
        print("frozen configuration guards itself:", type(err).__name__)


if __name__ == "__main__":
    main()
