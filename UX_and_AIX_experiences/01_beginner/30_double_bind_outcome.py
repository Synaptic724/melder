"""
TIER: beginner (30)
GOAL: Binding the SAME class twice is refused - a spell_id is the
      SHA256 of the class's code, and one object registers once, under
      any binding name or lifecycle. When one shape must serve two
      roles, make two shapes: subclass it (see 24).
SURFACE EXERCISED: the one-object law at bind time
"""
import melder as md


class Doubled:
    pass


class DoubledAgain(Doubled):
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Doubled, existence="unique")
    try:
        book.bind(spell=Doubled, existence="many")
        print("second bind unexpectedly accepted")
    except Exception as err:
        print("same object refused:", type(err).__name__)

    # the fix: a subclass IS a new class - a new spell_id (and a new name)
    book.bind(spell=DoubledAgain, existence="many")
    print("subclass bound cleanly - two shapes, two spells")


if __name__ == "__main__":
    main()
