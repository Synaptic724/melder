"""
TIER: beginner (32)
GOAL: Factory functions compose - a many-bound factory can itself be
      the assembly line for configured objects, keeping construction
      logic in ONE registered place.
SURFACE EXERCISED: function spells as factories, md.Existence.many
"""
import melder as md


class Connection:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn


def connection_factory() -> Connection:
    return Connection(dsn="postgres://replica.example:5432/app")


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=connection_factory, existence="many",
              binding_name="replica-connections")
    conduit = book.conjure()

    conn_a = conduit.meld(binding_name="replica-connections")
    conn_b = conduit.meld(binding_name="replica-connections")
    assert conn_a is not conn_b and conn_a.dsn == conn_b.dsn
    print("factory assembled two connections to", conn_a.dsn)


if __name__ == "__main__":
    main()
