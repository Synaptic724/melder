"""
TIER: beginner (11)
GOAL: Registration is just Python - bind a whole list of classes with a
      plain loop. No special batch API needed, ever.
SURFACE EXERCISED: bind() in a loop
"""
import melder as md


class Users:
    pass


class Orders:
    pass


class Invoices:
    pass


def main() -> None:
    book = md.Spellbook()
    for cls in (Users, Orders, Invoices):
        book.bind(spell=cls, existence="unique")
    conduit = book.conjure()

    assert all(isinstance(conduit.meld(spell=c), c)
               for c in (Users, Orders, Invoices))
    print("three spells bound with one plain loop")


if __name__ == "__main__":
    main()
