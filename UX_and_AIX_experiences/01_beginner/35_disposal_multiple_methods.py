"""
TIER: beginner (35)
GOAL: disposal_method_names takes a LIST - complex resources name every
      teardown verb they need, and the printed order documents how the
      runtime walks them.
SURFACE EXERCISED: bind(disposal_method_names=["flush", "close"])
"""
import melder as md

STAGES: list[str] = []


class BufferedWriter:
    """Expose two disposal methods whose requested order is observable."""

    def flush(self) -> None:
        """Record the flush step before the resource is closed."""
        STAGES.append("flushed")

    def close(self) -> None:
        """Record the close step after flushing."""
        STAGES.append("closed")


def main() -> None:
    """Bind ordered disposal names, create the writer, and verify exact cleanup order."""
    book = md.Spellbook()
    book.bind(spell=BufferedWriter, existence="unique",
              disposal_method_names=["flush", "close"])
    conduit = book.conjure()
    writer = conduit.meld("BufferedWriter")
    assert isinstance(writer, BufferedWriter)

    conduit.cleanup()
    book.cleanup()
    print("teardown stages observed:", STAGES or "(documented by the 3.14t run)")
    assert STAGES == ["flushed", "closed"], "disposal methods must run in supplied order"


if __name__ == "__main__":
    main()
