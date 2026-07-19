"""
TIER: beginner (07)
GOAL: The vocabulary enums all accept their string names too - config
      files and CLI flags can drive registration without importing the
      enums. Both spellings resolve to the same lifecycles.
SURFACE EXERCISED: bind(existence="many", permissions="read"), md.Existence
"""
import melder as md


class FromStrings:
    pass


class FromEnums:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=FromStrings, existence="many", permissions="create")
    book.bind(
        spell=FromEnums,
        existence=md.Existence.many,
        permissions=md.Permissions.create,
    )
    conduit = book.conjure()

    s_a, s_b = conduit.meld(spell=FromStrings), conduit.meld(spell=FromStrings)
    e_a, e_b = conduit.meld(spell=FromEnums), conduit.meld(spell=FromEnums)
    assert s_a is not s_b and e_a is not e_b
    print("string and enum registrations behave identically (many)")


if __name__ == "__main__":
    main()
