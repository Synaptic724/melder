"""Point the board row and the epic's resume view at tranche 2 (sweep A6 first).

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/sync_tranche2.py <NOW>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")


def board() -> None:
    """Rewrite the correctness_defects row's next field and updated_at."""
    path = pathlib.Path("attention_board.md")
    text = path.read_text(encoding="utf-8")
    row = re.compile(r"^(\| correctness_defects \| in_progress \| discovery \| claude \| melder_0 \| none \| )"
                     r"[^|]+( \| [^|]+ \| [^|]+ \| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )"
                     r"[0-9TZ:-]+( \| REQUIRED \|)$", re.M)
    assert len(row.findall(text)) == 1
    nxt = ("Sweep A6: read ReleaseManagedSpell, the managed pool and the Creations pool paths whole, then probe a "
           "managed version across notch, disposal and release.")
    text = row.sub(lambda m: m.group(1) + nxt + m.group(2) + NOW + m.group(3), text, count=1)
    path.write_text(text, encoding="utf-8")


def epic() -> None:
    """Replace the resume view's Next item; set Updated."""
    text = EPIC.read_text(encoding="utf-8")
    old = ("- Next: (1) tell the owner what was filed and the two open questions; (2) NOTICE melder_1 of the fourth\n"
           "  story; (3) the next sweep areas on the owner's word.\n")
    new = ("- Done since: the owner told what was filed and the two open questions (chat); melder_1 told of the four\n"
           "  stories whose fixes sit in its files (M0-181, M0-182; it carries them to the owner with its fix #1).\n"
           "- Next: tranche 2 (PLAN 20:37:46Z): (1) A6 managed pools across a version's life; (2) A7 Book teardown\n"
           "  with parked versions; (3) A8 the views of moved and separated versions.\n")
    assert text.count(old) == 1
    text = text.replace(old, new, 1)
    text, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, text, count=1)
    assert count == 1
    assert all(len(line) <= 120 for line in new.splitlines())
    EPIC.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    board()
    epic()
    print("synced", NOW)
