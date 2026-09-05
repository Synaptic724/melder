"""
TIER: intermediate (30)
GOAL: SpellbookConfiguration, knob by knob - part 1: DISPOSAL.
      Two set-once properties describe teardown policy:
        disposal (bool)               - stored flag; matched names drive calls
        disposal_method_names (list)  - the ordered book-wide vocabulary
      enforce_priority_disposal_methods places the book block first when
      True or last when False (default). The book owns shared names in both modes.
      Both are IDEMPOTENT properties: set once, immutable after - the
      teardown story of a world must not change mid-flight. And the
      whole configuration FREEZES at conjure: any set_property after
      that refuses. Configuration is a pre-flight surface, period.
SURFACE EXERCISED: SpellbookConfiguration.set_property,
                   with_enforce_priority_disposal_methods, bind, meld, cleanup
"""
import melder as md


class PooledThing:
    """Expose observable ordered cleanup methods without a Melder-specific base class."""

    def __init__(self) -> None:
        """Start open with no disposal calls recorded."""
        self.closed = False
        self.calls: list[str] = []

    def close(self) -> None:
        """Mark closed and record the method's actual invocation position."""
        self.closed = True
        self.calls.append("close")

    def flush(self) -> None:
        """Record the configured flush step."""
        self.calls.append("flush")

    def release(self) -> None:
        """Record the spell-only release step."""
        self.calls.append("release")


def demonstrate_priority(priority: bool) -> None:
    """Show that the book owns shared names regardless of front/back placement."""
    config = md.SpellbookConfiguration()
    config.with_disposal_method_names(["flush", "close"])
    config.with_enforce_priority_disposal_methods(priority)
    config.with_defaults().finalize()
    book = md.Spellbook(configuration=config)
    book.bind(
        spell=PooledThing, existence="many",
        disposal_method_names=["close", "release", "flush", "missing"],
    )
    conduit = book.conjure()
    resource = conduit.meld("PooledThing")
    conduit.cleanup()
    expected = ["flush", "close", "release"] if priority else ["release", "flush", "close"]
    assert resource.calls == expected
    print("book block first" if priority else "book block last", resource.calls)
    book.cleanup()


def main() -> None:
    """Verify configuration timing and both ordered disposal arrangements."""
    # CONFIGURE, THEN LOCK - the order is the lesson.
    # The disposal pair is SET-ONCE. A book you construct bare has already
    # taken the standard default set, and that set is COMPLETE - it fills
    # every required property, disposal included. Complete means finished:
    # there is no room left to write disposal into it afterwards.
    # So you pick one path. Take the defaults and live with them, or state
    # your own policy up front and hand it to the book. This lesson states
    # its own.
    config = md.SpellbookConfiguration()
    config.set_property("disposal", True)
    config.set_property("disposal_method_names", ["close"])
    config.set_property("phase_scheduler_workers_per_spellbook", 5)
    config.set_property(
        "phase_scheduler_barrier_timeout_milliseconds", 60000)

    book = md.Spellbook(configuration=config)
    book.bind(spell=PooledThing, existence="unique")

    # IDEMPOTENT LAW: these two are set-once. A second set refuses.
    try:
        config.set_property("disposal", False)
        print("idempotent re-set unexpectedly succeeded")
    except Exception as err:
        print("idempotent re-set refused:", type(err).__name__)

    conduit = book.conjure()
    thing = conduit.meld("PooledThing")
    conduit.cleanup()
    print("disposal vocabulary fired at cleanup:", thing.closed)

    # FREEZE LAW: conjure froze the whole configuration.
    try:
        config.set_property("phase_scheduler_workers_per_spellbook", 2)
        print("post-conjure set unexpectedly succeeded")
    except Exception as err:
        print("post-conjure set refused:", type(err).__name__)
    book.cleanup()
    demonstrate_priority(False)
    demonstrate_priority(True)


if __name__ == "__main__":
    main()
