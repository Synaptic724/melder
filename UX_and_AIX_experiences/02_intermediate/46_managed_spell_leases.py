"""
TIER: intermediate (46)
GOAL: Let a `with` block give the object back - ManagedSpellLease.
      conduit.managed_spell_meld(Spell) melds a managed spell and returns a lease: the
      `with` target is the leased object, and leaving the block releases it, even when
      the block raised (the block's exception is never swallowed). A lease releases
      exactly once: release() a second time does nothing, and lease.object raises once
      the object went back, because the pool may already have leased it again.

      ReleaseManagedSpell().managed(obj) wraps an object you already hold - one meld
      returned, or one injected into your constructor - in the same kind of lease.
      managed_spell_meld refuses a spell that is not managed, before melding anything.
SURFACE EXERCISED: md.Conduit.managed_spell_meld, md.ManagedSpellLease (object,
                   release, released, with), md.ReleaseManagedSpell (managed,
                   describe), md.Existence.managed_spell_quantity, md.Existence.many,
                   md.Conduit.meld, md.Conduit.cleanup
"""
from typing import Tuple

import melder as md


class HttpSession:
    """A pooled HTTP session; `requests` counts the requests made with it."""

    def __init__(self) -> None:
        """Open the session."""
        self.requests: int = 0


class RequestLog:
    """A plain `many` spell, to show managed_spell_meld's refusal."""

    def __init__(self) -> None:
        """Start an empty log."""
        self.entries: int = 0


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Use leases from managed_spell_meld and from ReleaseManagedSpell().managed.

    Contract:
        Checks that a `with` block releases on exit (also when it raises), that a
        lease releases once, that a released lease refuses its object, and that a
        non-managed spell is refused.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(spell=HttpSession, existence=md.Existence.managed_spell_quantity)
        book.bind(spell=RequestLog, existence=md.Existence.many)
        conduit = book.conjure()
        try:
            with conduit.managed_spell_meld(HttpSession) as session:
                session.requests += 1
                assert pool_counts(HttpSession) == (1, 0, 1)
                print("inside the block the session is out (alive, idle, out):", pool_counts(HttpSession))
            assert pool_counts(HttpSession) == (1, 1, 0)
            print("leaving the block gave it back:", pool_counts(HttpSession))

            # A lease held by hand: the same idle session comes back.
            lease = conduit.managed_spell_meld("HttpSession")
            assert isinstance(lease, md.ManagedSpellLease)
            assert lease.object is session and not lease.released
            lease.release()
            lease.release()  # a second release does nothing
            assert lease.released and pool_counts(HttpSession) == (1, 1, 0)
            try:
                lease.object
                raise AssertionError("a released lease still handed out its object")
            except RuntimeError as refused:
                print("a released lease refuses its object:", refused)

            # The block raises: the session still goes back, and the error is not swallowed.
            try:
                with conduit.managed_spell_meld(HttpSession) as session:
                    session.requests += 1
                    raise ConnectionError("upstream timed out")
            except ConnectionError as error:
                assert pool_counts(HttpSession) == (1, 1, 0)
                print("the block raised", repr(error), "and the session went back anyway")

            # Wrap an object you already hold - here, one a plain meld returned.
            held: HttpSession = conduit.meld("HttpSession")
            with md.ReleaseManagedSpell().managed(held) as same:
                assert same is held and pool_counts(HttpSession) == (1, 0, 1)
            assert pool_counts(HttpSession) == (1, 1, 0)
            print("managed(obj) leased a melded session and gave it back:", same is held)

            try:
                conduit.managed_spell_meld("RequestLog")
                raise AssertionError("managed_spell_meld leased a many spell")
            except ValueError as refused:
                print("managed_spell_meld refuses a spell that is not managed:", str(refused)[:60], "...")
        finally:
            conduit.cleanup()
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
