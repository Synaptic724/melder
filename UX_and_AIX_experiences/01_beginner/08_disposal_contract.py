"""
TIER: beginner (08)
GOAL: Teardown is part of registration - disposal_method_names tells
      melder which methods to call on YOUR instances when their owner
      cleans up. No base class, no protocol: name the method, done.
      The printed stages document exactly when disposal fires.
SURFACE EXERCISED: bind(disposal_method_names=[...]), cleanup cascade
"""
import melder as md

CLOSED: list[str] = []


class PooledConnection:
    def close(self) -> None:
        CLOSED.append("connection closed")


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=PooledConnection,
        existence=md.Existence.unique,
        disposal_method_names=["close"],
    )
    conduit = book.conjure()
    conn = conduit.meld(spell=PooledConnection)
    assert isinstance(conn, PooledConnection) and not CLOSED

    conduit.cleanup()
    print("after conduit.cleanup():", CLOSED or "not yet disposed")
    book.cleanup()
    print("after book.cleanup():", CLOSED or "not disposed")
    assert CLOSED, "disposal_method_names contract: close() must fire on teardown"
    print("disposal contract held:", CLOSED[0])


if __name__ == "__main__":
    main()
