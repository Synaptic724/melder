"""S8: add melder_0's 0.2.8248 notch notice to the attention board's notes (before the git-hazard note).

Run from the repository root: python s8_board_notch_notice.py
"""
import pathlib

BOARD = pathlib.Path("context_compass/attention_board.md")
ANCHOR = "### Device VM git hazard (melder_2, 2026-09-26)"
NOTICE = (
    "### Notch notice (melder_0, 2026-10-16)\n"
    "- melder_0 landed 0.2.8248 (conjure wires the versions staged with `bind_inactive` before it, so they meld after a\n"
    "  notch; creation cache generation 21; S8 of EPIC-2026-10-14-managed_spell_quantity). Notch above it if you land\n"
    "  after.\n"
)


def main() -> None:
    """Insert the notice once, keeping the board's line endings."""
    text = BOARD.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    assert text.count(ANCHOR) == 1, text.count(ANCHOR)
    assert "melder_0 landed 0.2.8248" not in text, "already added"
    text = text.replace(ANCHOR, NOTICE.replace("\n", newline) + ANCHOR, 1)
    BOARD.write_bytes(text.encode("utf-8"))
    print("notice added;", "CRLF" if newline == "\r\n" else "LF")


if __name__ == "__main__":
    main()
