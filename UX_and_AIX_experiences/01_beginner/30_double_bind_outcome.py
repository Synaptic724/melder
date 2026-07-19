"""
TIER: beginner (30)
GOAL: Binding the SAME class twice is refused - spells are
      content-fingerprinted and one fingerprint registers once. When one
      shape must serve two roles, make two shapes: subclass it (see 24).
SURFACE EXERCISED: the one-fingerprint law at bind time
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
        print("same fingerprint refused:", type(err).__name__)

    # the fix: a subclass IS a different fingerprint (and a different name)
    book.bind(spell=DoubledAgain, existence="many")
    print("subclass bound cleanly - two shapes, two spells")


if __name__ == "__main__":
    main()
