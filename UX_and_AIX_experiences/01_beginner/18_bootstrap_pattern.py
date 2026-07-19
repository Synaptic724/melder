"""
TIER: beginner (18)
GOAL: The composition root - ONE function that binds the whole world
      and hands back the conduit. Configured things are BUILT there and
      bound as instances; everything else in the app just melds.
SURFACE EXERCISED: the build_world() pattern, instance spells
"""
import melder as md


class Settings:
    def __init__(self, env: str) -> None:
        self.env = env


class Api:
    pass


def build_world(env: str) -> tuple[md.Spellbook, md.Conduit]:
    """The one place construction knowledge lives."""
    book = md.Spellbook()
    book.bind(spell=Settings(env), existence="unique", permissions="read",
              binding_name="settings")
    book.bind(spell=Api, existence="many")
    return book, book.conjure()


def main() -> None:
    book, conduit = build_world(env="staging")
    settings = conduit.meld(binding_name="settings")
    assert settings.env == "staging"
    print("world bootstrapped for:", settings.env)
    print("app code melds; only build_world() knows how things are made")
    assert len(book.spells) == 2


if __name__ == "__main__":
    main()
