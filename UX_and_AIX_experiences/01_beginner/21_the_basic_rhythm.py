"""
TIER: beginner (21)
GOAL: The rhythm of every melder program: bind everything FIRST,
      conjure ONCE, meld everywhere after. Three verbs, one order.
SURFACE EXERCISED: the bind -> conjure -> meld order
"""
import melder as md


class Config:
    pass


class Database:
    pass


class Server:
    pass


def main() -> None:
    book = md.Spellbook()

    # 1. bind everything
    book.bind(spell=Config, existence="unique")
    book.bind(spell=Database, existence="unique")
    book.bind(spell=Server, existence="many")

    # 2. conjure once
    conduit = book.conjure()

    # 3. meld everywhere, as often as you like
    for _ in range(3):
        server = conduit.meld(spell=Server)
        assert isinstance(server, Server)
    assert conduit.meld(spell=Config) is conduit.meld(spell=Config)
    print("bind everything, conjure once, meld everywhere")


if __name__ == "__main__":
    main()
