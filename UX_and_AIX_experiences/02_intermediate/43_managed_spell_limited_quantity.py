"""
TIER: intermediate (43)
GOAL: Cap how many objects exist at once - managed_spell_mode="limited_quantity".
      managed_spell_limit (required here) is the most objects ALIVE at once: idle plus
      out. Below the limit a meld builds; at the limit, with nothing idle, the meld is
      refused with ManagedSpellExhaustedError before anything is built. The error is a
      MeldExecutionError that names the mode and the limit, and says how to get out:
      release an object, or bind a higher limit.

      Releasing frees a place: the next meld is served the released object, so the
      pool never grows past its limit. release_all(objects) gives many back at once.
SURFACE EXERCISED: md.Spellbook.bind (managed_spell_mode, managed_spell_limit),
                   md.ManagedSpellMode.limited_quantity, md.Conduit.meld,
                   md.ManagedSpellExhaustedError (mode, limit, timeout_seconds),
                   md.MeldExecutionError, md.ReleaseManagedSpell (release,
                   release_all, describe), md.Conduit.cleanup
"""
from typing import Tuple

import melder as md


class LicenseSeat:
    """One seat of a licence that allows a fixed number of concurrent users.

    `close` is its disposal method, run when the pool destroys the seat (root
    teardown here). `closed` is a lesson diagnostic.
    """

    def __init__(self) -> None:
        """Claim the seat; the lesson only records that it is open."""
        self.closed: bool = False

    def close(self) -> None:
        """Give the seat up for good; called by the pool when it destroys this object."""
        self.closed = True


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Fill a limited pool, read its refusal, then release and lease again.

    Contract:
        The refusal is caught and its fields checked; the counts prove the refusal
        built nothing and that releases never let the pool grow past its limit.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(
            spell=LicenseSeat,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_mode="limited_quantity",
            managed_spell_limit=2,
            disposal_method_names=["close"],
        )
        conduit = book.conjure()
        try:
            first: LicenseSeat = conduit.meld("LicenseSeat")
            second: LicenseSeat = conduit.meld("LicenseSeat")
            assert pool_counts(LicenseSeat) == (2, 0, 2)
            print("both seats taken (alive, idle, out):", pool_counts(LicenseSeat))

            # At the limit with nothing idle: refused before anything is built.
            try:
                conduit.meld("LicenseSeat")
                raise AssertionError("a third seat was leased past the limit")
            except md.ManagedSpellExhaustedError as refused:
                assert isinstance(refused, md.MeldExecutionError)
                assert refused.mode == "limited_quantity" and refused.limit == 2
                assert refused.timeout_seconds is None
                assert "Release one with ReleaseManagedSpell().release(obj)" in str(refused)
                print("third seat refused:", type(refused).__name__, "- mode", refused.mode, "limit", refused.limit)
            assert pool_counts(LicenseSeat) == (2, 0, 2)

            # A release frees a place, and the next meld is served the released seat.
            md.ReleaseManagedSpell().release(first)
            again: LicenseSeat = conduit.meld("LicenseSeat")
            assert again is first
            assert pool_counts(LicenseSeat) == (2, 0, 2)
            print("after a release the next user got the freed seat:", again is first)

            # release_all gives every seat back; the pool still holds exactly two.
            md.ReleaseManagedSpell().release_all([second, again])
            assert pool_counts(LicenseSeat) == (2, 2, 0)
            reused = {id(conduit.meld("LicenseSeat")), id(conduit.meld("LicenseSeat"))}
            assert reused == {id(first), id(second)}
            assert pool_counts(LicenseSeat) == (2, 0, 2)
            print("two more leases reused the same two seats; alive stays at the limit:", pool_counts(LicenseSeat))
        finally:
            conduit.cleanup()

        # Teardown disposes only what is idle; both seats were still out.
        assert not first.closed and not second.closed
        print("seats still out at teardown stay their holder's:", not first.closed)
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
