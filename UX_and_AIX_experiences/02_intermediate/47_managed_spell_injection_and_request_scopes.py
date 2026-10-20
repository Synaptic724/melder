"""
TIER: intermediate (47)
GOAL: Borrow a pooled object per request, give it back when the request ends.
      A managed spell can be injected like any other: annotate a constructor parameter
      with its class. Every injection is its own lease, so two handlers get two
      objects. The holder gives its object back - here the handler's own disposal
      method releases it, and the handler lives in a request scope (a lesser conduit),
      so leaving the scope disposes the handler and the connection returns to the
      ROOT's pool for the next request.

      The pool belongs to the root and outlives every request scope. Root teardown
      disposes the idle objects only: an object still out is its holder's, and a
      release after teardown is refused because the pool left with its root. So give
      leases back before the root ends - a consumer melded on the root itself that
      releases at its own disposal meets a pool already gone at root teardown.
SURFACE EXERCISED: md.Spellbook.bind, md.Existence.managed_spell_quantity,
                   md.Existence.many (disposal_method_names), constructor injection,
                   md.Conduit.enter_lesser_conduit, md.Conduit.meld,
                   md.ReleaseManagedSpell (release, describe), md.Conduit.cleanup
"""
from typing import Tuple

import melder as md


class PooledConnection:
    """A connection the root keeps pooled across requests; `close` disposes it."""

    def __init__(self) -> None:
        """Open the connection."""
        self.closed: bool = False

    def close(self) -> None:
        """Close the connection; called when the pool destroys it."""
        self.closed = True


class RequestHandler:
    """Handles one request with a pooled connection injected into its constructor.

    `finish` is its disposal method: the request scope runs it when the scope ends,
    and it hands the connection back to the root's pool exactly once.
    """

    def __init__(self, connection: PooledConnection) -> None:
        """Keep the leased connection for the life of the request."""
        self.connection: PooledConnection = connection
        self.finished: bool = False

    def finish(self) -> None:
        """Give the connection back; later calls do nothing."""
        if self.finished:
            return
        self.finished = True
        md.ReleaseManagedSpell().release(self.connection)


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Serve two requests from one pool, then tear the root down.

    Contract:
        Checks that each injection leases its own object, that ending a request
        scope returns its leases, that the next request reuses them, and what root
        teardown does to idle and outstanding objects.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(
            spell=PooledConnection,
            existence=md.Existence.managed_spell_quantity,
            disposal_method_names=["close"],
        )
        book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
        root = book.conjure()
        try:
            with root.enter_lesser_conduit() as request:
                first: RequestHandler = request.meld("RequestHandler")
                second: RequestHandler = request.meld("RequestHandler")
                assert first.connection is not second.connection
                assert pool_counts(PooledConnection) == (2, 0, 2)
                print("two handlers, two leased connections (alive, idle, out):", pool_counts(PooledConnection))
            # Leaving the request scope disposed both handlers; each released its connection.
            assert first.finished and second.finished
            assert pool_counts(PooledConnection) == (2, 2, 0)
            print("the request ended and both connections went back:", pool_counts(PooledConnection))

            with root.enter_lesser_conduit() as request:
                third: RequestHandler = request.meld("RequestHandler")
                assert third.connection in (first.connection, second.connection)
                assert pool_counts(PooledConnection) == (2, 1, 1)
                print("the next request reused a pooled connection:", True)
            assert pool_counts(PooledConnection) == (2, 2, 0)

            # Keep one connection out across root teardown.
            outstanding: PooledConnection = root.meld("PooledConnection")
            assert pool_counts(PooledConnection) == (2, 1, 1)
        finally:
            root.cleanup()

        # Teardown closed the idle connection, left the outstanding one to its holder...
        idle = second.connection if outstanding is first.connection else first.connection
        assert idle.closed and not outstanding.closed
        print("root teardown closed the idle connection, not the one still out:", not outstanding.closed)
        # ...and the pool is gone, so giving it back now is refused.
        try:
            md.ReleaseManagedSpell().release(outstanding)
            raise AssertionError("a connection was released into a torn-down root")
        except ValueError as refused:
            outstanding.close()  # it is ours to dispose now
            print("a release after root teardown is refused:", str(refused)[:70], "...")
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
