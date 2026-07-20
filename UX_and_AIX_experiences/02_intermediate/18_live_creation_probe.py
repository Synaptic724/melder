"""
TIER: intermediate (18)
GOAL: "Is it already alive?" without creating it - has_live_creation
      mirrors meld's exact lookup but stops before construction.
      Doc-canon: the no-create probe for agents and diagnostics.
SURFACE EXERCISED: Conduit.has_live_creation / describe_live_creation_status
"""
import melder as md


class ExpensiveEngine:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=ExpensiveEngine, existence="unique")
    conduit = book.conjure()

    before = conduit.has_live_creation(spell=ExpensiveEngine)
    conduit.meld(spell=ExpensiveEngine)
    after = conduit.has_live_creation(spell=ExpensiveEngine)
    print("live before meld?", before, "| after?", after)
    assert after is True and before is False
    print("status:", conduit.describe_live_creation_status(spell=ExpensiveEngine))


if __name__ == "__main__":
    main()
