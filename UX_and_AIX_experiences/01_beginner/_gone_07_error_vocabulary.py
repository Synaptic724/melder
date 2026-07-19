"""
TIER: beginner (07)
GOAL: Failing well on day one - every exception melder raises at you is
      catchable from the root namespace. No internal paths, ever.
SURFACE EXERCISED: md.SpellbookValidationError, md.MeldExecutionError
"""
import melder as md


class Registered:
    pass


class NeverRegistered:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Registered, existence=md.Existence.unique)
    conduit = book.conjure()

    try:
        outcome = conduit.meld(spell=NeverRegistered)
        print("meld of unregistered spell answered:", outcome)
    except (md.SpellbookValidationError, md.MeldExecutionError) as err:
        print("caught from root:", type(err).__name__)

    # the full catchable family, importable without knowing ANY internal path
    family = [
        md.SpellbookValidationError, md.MeldExecutionError,
        md.SpellSpaceScopeError, md.HookExecutionError,
        md.InternalRegistrationError, md.PhaseSchedulerError,
        md.PhaseExecutionError, md.PhaseTimeoutError, md.DeadReferenceError,
    ]
    assert all(issubclass(e, BaseException) for e in family)
    print("error vocabulary size:", len(family))


if __name__ == "__main__":
    main()
