"""
TIER: beginner (32)
GOAL: Two factory shapes, one law each - a FUNCTION spell is unique
      (one shared product); when you want a fresh object per meld, the
      factory must be a CLASS bound "many".
SURFACE EXERCISED: function-unique law vs class-many freshness
"""
import melder as md


class Connection:
    def __init__(self, dsn: str = "postgres://replica.example:5432/app") -> None:
        self.dsn = dsn


def shared_connection() -> Connection:
    return Connection()


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=shared_connection, existence="unique",
              spellframe="db", binding_name="shared-conn")
    book.bind(spell=Connection, existence="many",
              spellframe="db", binding_name="fresh-conn")
    conduit = book.conjure()

    a = conduit.meld(spellframe="db", binding_name="shared-conn")
    b = conduit.meld(spellframe="db", binding_name="shared-conn")
    print("function factory (unique): shared?", a is b)

    c = conduit.meld(spellframe="db", binding_name="fresh-conn")
    d = conduit.meld(spellframe="db", binding_name="fresh-conn")
    assert c is not d
    print("class factory (many): fresh per meld -", c is not d)


if __name__ == "__main__":
    main()
