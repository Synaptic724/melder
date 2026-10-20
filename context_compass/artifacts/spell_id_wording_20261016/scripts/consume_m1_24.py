"""Re-onboarding check-in and consumption of M1-24 (melder_1's ACK of M0-180).

Run from context_compass/:  python3 consume_m1_24.py <NOW> roster    # refresh melder_0's last_checked only
                            python3 consume_m1_24.py <NOW> consume   # delete M1-24, clear its alert, refresh
The M1-24 content is copied into the wording ticket's Notes (note_m1_24_go.txt) before `consume` runs.
"""
import pathlib
import re
import sys

NOW, STEP = sys.argv[1], sys.argv[2]
ROSTER = re.compile(r"^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$", re.M)


def refresh(text: str) -> str:
    """Set melder_0's last_checked to NOW; exactly one roster row must match."""
    assert len(ROSTER.findall(text)) == 1
    return ROSTER.sub(lambda m: m.group(1) + NOW + m.group(2), text, count=1)


def main() -> None:
    """Refresh the roster row, and on `consume` delete M1-24 and clear its alert."""
    mb = pathlib.Path("mailbox_board.md")
    text = mb.read_text(encoding="utf-8")
    assert "\r\n" not in text
    if STEP == "consume":
        head = "- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-17T20:38:54Z\n  TYPE: ACK\n  CLAIM: M1-24, re M0-180."
        assert text.count(head) == 1
        start = text.index(head)
        end = text.index("  ACK_REQUESTED: false\n", start) + len("  ACK_REQUESTED: false\n")
        assert text[start:end].count("- TO:") == 1
        text = text[:start] + text[end:]
        ab = pathlib.Path("attention_board.md")
        board = ab.read_text(encoding="utf-8")
        alert = "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-17T20:38:54Z)\n"
        assert board.count(alert) == 1
        ab.write_text(board.replace(alert, "", 1), encoding="utf-8")
    mb.write_text(refresh(text), encoding="utf-8")
    print(STEP, "done", NOW)


if __name__ == "__main__":
    main()
