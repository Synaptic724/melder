"""
TIER: intermediate (45)
GOAL: Hand the next caller a clean object - managed_spell_reset_methods.
      A pooled object is reused, so whatever the last holder left in it would leak to
      the next one. Name its reset methods at bind: zero-argument methods the pool
      calls, in the order given, on EVERY release, before the object is idle again.
      The next lease then gets the same object, reset.

      A reset that raises means the object cannot be trusted: the pool destroys it
      (its disposal methods run, its place is freed) and the reset's error propagates
      from the release. The next meld builds a fresh object.
SURFACE EXERCISED: md.Spellbook.bind (managed_spell_reset_methods,
                   disposal_method_names), md.Existence.managed_spell_quantity,
                   md.Conduit.meld, md.ReleaseManagedSpell (release, describe),
                   md.Conduit.cleanup
"""
from typing import List, Tuple

import melder as md


class ReportBuilder:
    """Accumulates report lines for one request; must start empty for the next one.

    `clear_lines` and `rewind` are its reset methods; `calls` records the order the
    pool ran them, as a lesson diagnostic.
    """

    def __init__(self) -> None:
        """Start with no lines and the cursor at the top."""
        self.lines: List[str] = []
        self.cursor: int = 0
        self.calls: List[str] = []

    def clear_lines(self) -> None:
        """Drop the previous request's lines."""
        self.lines.clear()
        self.calls.append("clear_lines")

    def rewind(self) -> None:
        """Move the cursor back to the top."""
        self.cursor = 0
        self.calls.append("rewind")


class TemplateCache:
    """A pooled cache whose reset refuses once the cache is corrupted.

    `close` is its disposal method; the pool runs it when it destroys the object.
    """

    def __init__(self) -> None:
        """Start valid and open."""
        self.corrupted: bool = False
        self.closed: bool = False

    def reset(self) -> None:
        """Empty the cache for the next holder; a corrupted cache cannot be reset."""
        if self.corrupted:
            raise ValueError("template cache is corrupted and cannot be reset")

    def close(self) -> None:
        """Dispose the cache; called when the pool destroys this object."""
        self.closed = True


def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


def main() -> None:
    """Reset a pooled object on release, then watch a failing reset destroy one.

    Contract:
        Checks the reset order, the reused object's clean state, and that a raising
        reset disposes the object, frees its place and propagates its error.
    Returns:
        None.
    """
    book = md.Spellbook()
    try:
        book.bind(
            spell=ReportBuilder,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_reset_methods=["clear_lines", "rewind"],
        )
        book.bind(
            spell=TemplateCache,
            existence=md.Existence.managed_spell_quantity,
            managed_spell_reset_methods=["reset"],
            disposal_method_names=["close"],
        )
        conduit = book.conjure()
        release = md.ReleaseManagedSpell().release
        try:
            builder: ReportBuilder = conduit.meld("ReportBuilder")
            builder.lines.extend(["header", "totals"])
            builder.cursor = 2
            release(builder)
            # The resets ran in the order named at bind, on the release itself.
            assert builder.calls == ["clear_lines", "rewind"]
            assert builder.lines == [] and builder.cursor == 0
            print("release ran the resets in order:", builder.calls)

            nxt: ReportBuilder = conduit.meld("ReportBuilder")
            assert nxt is builder and nxt.lines == []
            print("the next request got the same builder, clean:", nxt is builder)
            release(nxt)

            cache: TemplateCache = conduit.meld("TemplateCache")
            cache.corrupted = True
            try:
                release(cache)
                raise AssertionError("a corrupted cache went back into the pool")
            except ValueError as error:
                # The pool destroyed the object: disposal ran and its place was freed.
                assert cache.closed
                assert pool_counts(TemplateCache) == (0, 0, 0)
                print("a failing reset destroyed the cache and raised:", error)

            fresh: TemplateCache = conduit.meld("TemplateCache")
            assert fresh is not cache and not fresh.corrupted
            assert pool_counts(TemplateCache) == (1, 0, 1)
            print("the next meld built a fresh cache:", fresh is not cache)
            release(fresh)
        finally:
            conduit.cleanup()
    finally:
        book.cleanup()


if __name__ == "__main__":
    main()
