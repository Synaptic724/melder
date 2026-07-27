"""
TIER: intermediate (31)
GOAL: SpellbookConfiguration DEFINED - the four things you can set,
      what each one means, and the four laws that guard them. This is
      the book's policy object: it decides teardown and how hard the
      conjure pipeline works. Nothing here is exotic - four values,
      four rules.

      THE FOUR ITEMS
      disposal (bool)
          Declares that this book's world performs teardown calls.
      disposal_method_names (list[str])
          The teardown VOCABULARY - the method names that mean "clean
          yourself up" in this system. Cleanup calls whichever of them
          each object actually has (beginner 08 showed it firing).
      phase_scheduler_workers_per_spellbook (int)
          How many worker threads run the conjure pipeline. Conjure
          compiles and validates every spell in phases - more workers
          means more of that in parallel.
      phase_scheduler_barrier_timeout_milliseconds (int)
          How long a phase barrier waits for a straggler before
          refusing loudly. This is the anti-hang knob: a broken spell
          fails your startup with an error, never a frozen process.

      THE FOUR LAWS
      1) CLOSED REGISTRY - an unknown key refuses. No typo silently
         becomes a setting.
      2) IDEMPOTENT PAIR - the two disposal items are set-ONCE. A
         world's teardown story must not change mid-flight.
      3) FREEZE - conjure validates and freezes the whole object.
         Configuration is a pre-flight surface, period.
      4) COMPLETION - hand a book YOUR configuration and you own
         completing it. with_defaults() is easy mode; a bare config
         refuses at conjure-time validation.
SURFACE EXERCISED: the four items, the four refusal laws
"""
import melder as md


class Service:
    pass


def main() -> None:
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["close"])
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property(
        "phase_scheduler_barrier_timeout_milliseconds", 30000)

    # LAW 1 - closed registry: typos refuse.
    try:
        configuration.set_property("phase_sceduler_workers", 4)
    except Exception as err:
        print("unknown key refused:", type(err).__name__)

    # LAW 2 - the disposal pair is set-once.
    try:
        configuration.set_property("disposal", False)
    except Exception as err:
        print("idempotent re-set refused:", type(err).__name__)

    book = md.Spellbook(configuration=configuration)
    book.bind(spell=Service, existence="unique")
    conduit = book.conjure()   # LAW 3 happens here: validate + freeze
    assert isinstance(conduit.meld(spell=Service), Service)

    try:
        configuration.set_property(
            "phase_scheduler_barrier_timeout_milliseconds", 1)
    except Exception as err:
        print("post-freeze set refused:", type(err).__name__)

    # LAW 4 - completion: a bare config you never finished refuses at
    # the conjure gate, naming what is missing.
    bare_book = md.Spellbook(configuration=md.SpellbookConfiguration())
    bare_book.bind(spell=Service, existence="unique", binding_name="bare")
    try:
        bare_book.conjure()
        print("bare configuration unexpectedly conjured")
    except Exception as err:
        print("incomplete configuration refused at conjure:",
              type(err).__name__)


if __name__ == "__main__":
    main()
