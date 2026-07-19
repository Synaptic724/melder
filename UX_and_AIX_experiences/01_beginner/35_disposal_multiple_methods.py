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
    def flush(self) -> None:
        STAGES.append("flushed")

    def close(self) -> None:
        STAGES.append("closed")


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=BufferedWriter, existence="unique",
              disposal_method_names=["flush", "close"])
    conduit = book.conjure()
    writer = conduit.meld(spell=BufferedWriter)
    assert isinstance(writer, BufferedWriter)

    conduit.cleanup()
    book.cleanup()
    print("teardown stages observed:", STAGES or "(documented by the 3.14t run)")
    assert STAGES, "disposal list contract: both verbs must fire on teardown"


if __name__ == "__main__":
    main()
