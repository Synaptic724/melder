"""
TIER: beginner (06)
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
        conduit.meld(spell=NeverRegistered)
    except KeyError as err:
        # the documented "not found anywhere" contract is one stable KeyError
        print("unregistered spell -> KeyError:", err)

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
