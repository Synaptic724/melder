"""
TIER: intermediate (33)
GOAL: SpellbookConfiguration hooks, family 2: the CONDUIT LIFECYCLE.
      Five moments of a conduit's life are observable:
        on_conduit_pre_created / on_conduit_post_created /
        on_conduit_activated at conjure, and
        on_conduit_cleanup_start / on_conduit_cleanup_complete at the
        end. Register before conjure; watch the whole life.
SURFACE EXERCISED: conduit lifecycle hooks, firing order
"""
import melder as md


class Anything:
    pass


def main() -> None:
    moments = []

    book = md.Spellbook()
    config = book.get_configuration()
    for name in ("on_conduit_pre_created", "on_conduit_post_created",
                 "on_conduit_activated", "on_conduit_cleanup_start",
                 "on_conduit_cleanup_complete"):
        config.add_hook(book.id, name,
                        (lambda n: lambda *a, **k: moments.append(n))(name))

    book.bind(spell=Anything, existence="unique")
    conduit = book.conjure()
    print("after conjure:", moments)

    conduit.cleanup()
    print("after cleanup:", moments)
    assert moments.index("on_conduit_pre_created") < moments.index(
        "on_conduit_cleanup_start")
    print("a conduit's whole life, observed in order")


if __name__ == "__main__":
    main()
