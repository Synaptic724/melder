"""
TIER: beginner (18)
GOAL: The composition root - ONE function that binds the whole world
      and hands back the conduit. Configured things are BUILT there and
      bound as instances; everything else in the app just melds. Note:
      melder worlds do not "switch environments" - the same objects
      cannot register twice (spells are content-fingerprinted), so your
      MODULE decides what to build, once, at the root.
SURFACE EXERCISED: the build_world() pattern, instance spells
"""
import melder as md


class Settings:
    def __init__(self, database_url: str, retries: int) -> None:
        self.database_url = database_url
        self.retries = retries


class Api:
    pass


def build_world() -> tuple[md.Spellbook, md.Conduit]:
    """The one place construction knowledge lives."""
    book = md.Spellbook()
    book.bind(spell=Settings("postgres://db.example:5432/app", 3),
              existence="unique",
              spellframe="app", binding_name="settings")
    book.bind(spell=Api, existence="many")
    return book, book.conjure()


def main() -> None:
    book, conduit = build_world()
    settings = conduit.meld(spellframe="app", binding_name="settings")
    assert settings.retries == 3
    print("world bootstrapped:", settings.database_url)
    print("app code melds; only build_world() knows how things are made")
    assert len(book.spells) == 2


if __name__ == "__main__":
    main()
