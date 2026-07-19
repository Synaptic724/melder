"""
TIER: beginner (21)
GOAL: Optional dependencies, honestly - an unknown address raises one
      stable KeyError, so "use it if the world has it" is a four-line
      try/except with a fallback. No hasattr poking, no None-guessing.
SURFACE EXERCISED: the KeyError contract as a feature
"""
import melder as md


class Telemetry:
    enabled = True


def main() -> None:
    book = md.Spellbook()
    # note: Telemetry deliberately NOT bound in this world
    book.bind(spell=object, existence="unique", binding_name="anchor",
              spellframe="app")
    conduit = book.conjure()

    try:
        telemetry = conduit.meld(spell=Telemetry)
    except KeyError:
        telemetry = None
    print("optional dependency resolved:", telemetry)
    print("worlds declare what they have; your code adapts in one except")


if __name__ == "__main__":
    main()
