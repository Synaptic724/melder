"""
TIER: beginner (04)
GOAL: Two implementations of one shape, told apart by binding_name -
      the beginner door into disambiguation (spellframes come later).
SURFACE EXERCISED: md.Spellbook, md.Existence, binding_name= on bind/meld
"""
import melder as md


class PostgresStore:
    kind = "postgres"


class SqliteStore:
    kind = "sqlite"


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=PostgresStore,
        existence="unique",
        binding_name="primary",
    )
    book.bind(
        spell=SqliteStore,
        existence="unique",
        binding_name="local",
    )
    conduit = book.conjure()

    primary = conduit.meld(spell=PostgresStore, binding_name="primary")
    local = conduit.meld(spell=SqliteStore, binding_name="local")
    assert primary.kind == "postgres" and local.kind == "sqlite"
    print("named bindings resolved:", primary.kind, "+", local.kind)


if __name__ == "__main__":
    main()
