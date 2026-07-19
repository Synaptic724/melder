"""
TIER: beginner (31)
GOAL: existence is not optional - the bind vocabulary is explicit by
      design. Forgetting it fails LOUDLY at bind time, not quietly at
      meld time. The error type is printed for the record.
SURFACE EXERCISED: bind() required kwargs, fail-fast law
"""
import melder as md


class Forgotten:
    pass


def main() -> None:
    book = md.Spellbook()
    try:
        book.bind(spell=Forgotten)  # deliberately missing existence
        print("bind without existence unexpectedly succeeded")
    except TypeError as err:
        print("missing existence fails fast: TypeError -", err)
    except Exception as err:
        print("missing existence fails fast:", type(err).__name__, "-", err)

    try:
        book.bind(spell=Forgotten, existence="not-a-lifecycle")
        print("bogus existence string unexpectedly accepted")
    except Exception as err:
        print("bogus existence string refused:", type(err).__name__)


if __name__ == "__main__":
    main()
