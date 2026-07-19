"""
TIER: beginner (03)
GOAL: Spells are not only classes - functions and ready-made objects
      bind with the same verb. RUNTIME LAW (proven by the harness):
      callable and pre-built spells are always "unique" - the factory
      runs once and its product is shared; instances are already built.
SURFACE EXERCISED: function spells, instance spells, string vocabulary
"""
import melder as md


def make_settings() -> dict:
    return {"region": "us-east", "retries": 3}


class AlreadyBuilt:
    def __init__(self, label: str) -> None:
        self.label = label


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=make_settings, existence="unique")

    prebuilt = AlreadyBuilt("built-by-hand")
    book.bind(spell=prebuilt, existence="unique", permissions="read")

    conduit = book.conjure()

    settings = conduit.meld(spell=make_settings)
    print("function spell melded ->", settings)
    again = conduit.meld(spell=make_settings)
    print("unique law: same product back?", settings is again)

    held = conduit.meld(spell=prebuilt)
    assert held is prebuilt and held.label == "built-by-hand"
    print("instance spell melded:", held.label)


if __name__ == "__main__":
    main()
