"""
TIER: beginner (23)
GOAL: The three mistakes everyone makes in hour one, and what melder
      says back. Learn the error shapes once and debugging is easy.
SURFACE EXERCISED: the beginner error contracts (all run-proven)
"""
import melder as md


class Thing:
    pass


def main() -> None:
    book = md.Spellbook()

    try:
        book.bind(spell=Thing)  # forgot existence
    except TypeError:
        print("1. forgot existence -> TypeError at bind (fail fast)")

    book.bind(spell=Thing, existence="unique")
    try:
        book.bind(spell=Thing, existence="many")  # bound it twice
    except Exception as err:
        print("2. same class twice ->", type(err).__name__, "at bind")

    conduit = book.conjure()
    try:
        conduit.meld(spellframe="nowhere", binding_name="nothing")
    except KeyError:
        print("3. unknown address -> KeyError at meld (one stable contract)")


if __name__ == "__main__":
    main()
