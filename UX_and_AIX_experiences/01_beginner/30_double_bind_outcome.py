"""
TIER: beginner (30)
GOAL: What happens when you bind the same class twice with no
      disambiguating name? The printed outcome IS the documentation -
      beginners hit this in their first hour, so the example makes the
      contract visible instead of leaving it to folklore.
SURFACE EXERCISED: repeated bind(), the error vocabulary
"""
import melder as md


class Doubled:
    pass


def main() -> None:
    book = md.Spellbook()
    first_id = book.bind(spell=Doubled, existence="unique")
    print("first bind:", first_id[:8])
    try:
        second_id = book.bind(spell=Doubled, existence="many")
        print("second bind accepted:", second_id[:8],
              "- distinct registration" if second_id != first_id else "- same id")
    except Exception as err:
        print("second bind refused:", type(err).__name__, "-", err)
    print("lesson: spells are SHA256 content-matched - same-name spells with")
    print("        different internals coexist; SAME-fingerprint rebinds need frames")


if __name__ == "__main__":
    main()
