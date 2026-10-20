"""
TIER: intermediate (42)
GOAL: Lease pooled objects and give them back by hand - Existence.managed_spell_quantity.
      A managed spell's objects live in a pool its root conduit owns. A meld takes an
      idle object, or builds one when none is waiting; ReleaseManagedSpell().release(obj)
      gives it back, and the next meld reuses it (the newest released object first).
      Nothing returns an object automatically: you decide when it goes back.

      Elastic is the default mode: a meld never refuses, and managed_spell_limit (256
      by default) is how many IDLE objects the pool keeps. With a small limit, a release
      that would keep more idle objects than the limit destroys the oldest idle one -
      its disposal methods run. Root teardown disposes the idle objects; describe(cls)
      shows what is alive, idle and out at any moment.
SURFACE EXERCISED: md.Spellbook.bind (managed_spell_mode, managed_spell_limit,
                   disposal_method_names), md.Existence.managed_spell_quantity,
                   md.ManagedSpellMode.elastic, md.Conduit.meld,
                   md.Conduit.has_live_creation, md.ReleaseManagedSpell (release, describe),
                   md.Conduit.cleanup
"""
from typing import Tuple

import melder as md


class DatabaseConnection:
    """A connection that is expensive to open and cheap to hand to the next caller.

    `close` is its disposal method: the pool calls it when it destroys the object
    (a trim, or root teardown), never on an ordinary release. `closed` is a lesson
    diagnostic, so the example can observe disposal from the outside.
    """

    def __init__(self) -> None:
        """Open the connection; the lesson only records that it is open."""
        self.closed: bool = False
        self.queries: int = 0

    def close(self) -> None:
        """Close the connection; called by the pool when it destroys this object."""
        self.closed = True


class ScratchBuffer:
    """A pooled buffer bound with a small idle limit, to show the elastic trim."""

    def __init__(self) -> None:
        """Allocate the buffer; `closed` records disposal."""
        self.closed: bool = False

    def close(self) -> None:
        """Release the buffer; called by the pool when it trims this object."""
        self.closed = True


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class.

    `ReleaseManagedSpell().describe(cls)` answers one snapshot per pool; this lesson
    binds each class once, so there is exactly one.
    """
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Lease, release, reuse and trim pooled objects, then tear the root down.

    Contract:
        Every assertion checks an observable outcome: object identity, the pool's
        counts from describe(), or the disposal flag. The conduit and the book are
        cleaned in finally blocks.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(
            spell=DatabaseConnection,
            existence=md.Existence.managed_spell_quantity,
            disposal_method_names=["close"],
        )
        book.bind(
            spell=ScratchBuffer,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_mode=md.ManagedSpellMode.elastic,
            managed_spell_limit=2,
            disposal_method_names=["close"],
        )
        conduit = book.conjure()
        # Bind the release once: it is the one way back for every managed object.
        release = md.ReleaseManagedSpell().release
        try:
            # The pool exists from conjure on, empty, with the default elastic policy.
            (snapshot,) = md.ReleaseManagedSpell().describe(DatabaseConnection)
            assert snapshot["mode"] == "elastic" and snapshot["limit"] == 256
            assert pool_counts(DatabaseConnection) == (0, 0, 0)
            assert not conduit.has_live_creation("DatabaseConnection")
            print("pool ready at conjure:", snapshot["mode"], "limit", snapshot["limit"])

            # Nothing is idle yet, so each meld builds a connection and leases it out.
            first: DatabaseConnection = conduit.meld("DatabaseConnection")
            second: DatabaseConnection = conduit.meld("DatabaseConnection")
            assert first is not second
            assert pool_counts(DatabaseConnection) == (2, 0, 2)
            assert conduit.has_live_creation("DatabaseConnection")
            print("two connections leased (alive, idle, out):", pool_counts(DatabaseConnection))

            # Give one back: it becomes idle, still open, and the next meld reuses it.
            first.queries += 1
            release(first)
            assert pool_counts(DatabaseConnection) == (2, 1, 1) and not first.closed
            reused: DatabaseConnection = conduit.meld("DatabaseConnection")
            assert reused is first and reused.queries == 1
            print("the released connection came back on the next meld:", reused is first)

            # The newest released object is leased first.
            release(second)
            release(reused)
            newest: DatabaseConnection = conduit.meld("DatabaseConnection")
            assert newest is reused
            release(newest)
            assert pool_counts(DatabaseConnection) == (2, 2, 0)
            print("newest released leased first; all back (alive, idle, out):", pool_counts(DatabaseConnection))

            # Elastic never refuses: with limit 2 a third buffer is still built...
            buffers = [conduit.meld("ScratchBuffer") for _ in range(3)]
            assert pool_counts(ScratchBuffer) == (3, 0, 3)
            # ...but only 2 stay idle: the third release destroys the oldest idle buffer.
            for buffer in buffers:
                release(buffer)
            assert [buffer.closed for buffer in buffers] == [True, False, False]
            assert pool_counts(ScratchBuffer) == (2, 2, 0)
            print("limit 2 keeps 2 idle buffers; the oldest was closed:", buffers[0].closed)
        finally:
            conduit.cleanup()

        # Root teardown disposes what the pools hold and unregisters them.
        assert first.closed and second.closed
        assert md.ReleaseManagedSpell().describe(DatabaseConnection) == ()
        print("root teardown closed the idle connections:", first.closed and second.closed)
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
