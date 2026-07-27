"""
TIER: intermediate (30)
GOAL: SpellbookConfiguration, knob by knob - part 1: DISPOSAL.
      Two properties own teardown behavior:
        disposal (bool)               - master switch for disposal calls
        disposal_method_names (list)  - the book-wide teardown vocabulary
      Both are IDEMPOTENT properties: set once, immutable after - the
      teardown story of a world must not change mid-flight. And the
      whole configuration FREEZES at conjure: any set_property after
      that refuses. Configuration is a pre-flight surface, period.
SURFACE EXERCISED: get_configuration().set_property, the idempotent
                   law, the freeze-at-conjure law
"""
import melder as md


class PooledThing:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def main() -> None:
    book = md.Spellbook()
    config = book.get_configuration()

    # The disposal pair - the config-side alternative to passing
    # disposal_method_names at bind (beginner 08).
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
    book.bind(spell=PooledThing, existence="unique")

    # IDEMPOTENT LAW: these two are set-once. A second set refuses.
    try:
        config.set_property("disposal", False)
        print("idempotent re-set unexpectedly succeeded")
    except Exception as err:
        print("idempotent re-set refused:", type(err).__name__)

    conduit = book.conjure()
    thing = conduit.meld(spell=PooledThing)
    conduit.cleanup()
    print("disposal vocabulary fired at cleanup:", thing.closed)

    # FREEZE LAW: conjure froze the whole configuration.
    try:
        config.set_property("phase_scheduler_workers_per_spellbook", 2)
        print("post-conjure set unexpectedly succeeded")
    except Exception as err:
        print("post-conjure set refused:", type(err).__name__)


if __name__ == "__main__":
    main()
