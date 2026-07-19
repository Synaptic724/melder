"""
TIER: beginner (03)
GOAL: Spells are not only classes - functions and ready-made objects bind
      with the same verb and the same vocabulary.
SURFACE EXERCISED: md.Spellbook, md.Existence, md.Permissions
"""
import melder as md


def make_settings() -> dict:
    return {"region": "us-east", "retries": 3}


class AlreadyBuilt:
    def __init__(self, label: str) -> None:
        self.label = label


def main() -> None:
    book = md.Spellbook()

    # a factory function: many -> the function RUNS per meld
    book.bind(spell=make_settings, existence=md.Existence.many)

    # an existing object: unique -> melder hands back what you built,
    # read permission because nothing should construct over it
    prebuilt = AlreadyBuilt("built-by-hand")
    book.bind(
        spell=prebuilt,
        existence=md.Existence.unique,
        permissions=md.Permissions.read,
    )

    conduit = book.conjure()

    settings = conduit.meld(spell=make_settings)
    assert settings["region"] == "us-east"
    print("function spell melded:", settings)

    held = conduit.meld(spell=prebuilt)
    assert held is prebuilt and held.label == "built-by-hand"
    print("instance spell melded:", held.label)


if __name__ == "__main__":
    main()
