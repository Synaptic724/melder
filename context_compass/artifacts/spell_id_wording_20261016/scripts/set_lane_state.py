"""Move the spell_id wording lane between "audit" (in_progress) and "hold" (blocked) on its ticket and board row.

Run from context_compass/:  python artifacts/spell_id_wording_20261016/scripts/set_lane_state.py <NOW> audit|hold

Rewrites the ticket's Status and State Transition Event (in place; the history is in the Notes) and the lane's
attention-board row (status, mode, blocker, next, updated_at); the detail entry's SWITCH_TRIGGER is unchanged.
"""
import pathlib
import re
import sys

NOW, STATE = sys.argv[1], sys.argv[2]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md")
HELD = ("melder_1 holds the 25 files of the held scope (its rule-2 src and tests, the system docs, graph, release "
        "note and __version__.py) until its closure and rebuild (M1-22)")
PRESETS = {
    "audit": {
        "status": "in_progress", "mode": "implementation", "blocker": "none for the audit; " + HELD,
        "next": "Apply the 10 free lines the audit found (V331-V340), compile and run their tests, GIL off and on.",
        "transition": ("- from_state: blocked\n- to_state: in_progress\n- transition_reason: the owner asked for a "
                       "double check that no real version id for something else is\n  being renamed (chat "
                       "2026-10-16); the audit found 12 missed lines, 10 in free files\n  (FACT and DECISION, "
                       + NOW + ").\n"),
    },
    "hold": {
        "status": "blocked", "mode": "implementation", "blocker": HELD,
        "next": "On melder_1's release NOTICE, recheck the 127 held decisions against the files, then apply them.",
        "transition": ("- from_state: in_progress\n- to_state: blocked\n- transition_reason: the audit's free lines "
                       "are applied and green (MEASURE, " + NOW + "); the 127 held\n  decisions wait for melder_1's "
                       "release NOTICE (BLOCKER, 2026-10-16T19:11:31Z).\n"),
    },
}


def main() -> None:
    """Rewrite the ticket's state lines and the board row for the preset."""
    preset = PRESETS[STATE]
    raw = TICKET.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace(nl, "\n")
    text, n = re.subn(r"^- Status: \w+$", "- Status: " + preset["status"], text, count=1, flags=re.M)
    assert n == 1
    text, n = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    assert n == 1
    start = text.index("## State Transition Event\n") + len("## State Transition Event\n")
    end = text.index("\n## Steps / Checklist", start)
    text = text[:start] + preset["transition"] + text[end:]
    assert all(len(line) <= 120 for line in preset["transition"].splitlines())
    TICKET.write_bytes(text.replace("\n", nl).encode("utf-8"))
    board = pathlib.Path("attention_board.md")
    btext = board.read_text(encoding="utf-8")
    rx = re.compile(r"^\| spell_id_wording \| .*\| tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task"
                    r"\.md \| [0-9TZ:-]+ \| REQUIRED \|$", re.M)
    assert len(rx.findall(btext)) == 1
    row = ("| spell_id_wording | " + preset["status"] + " | " + preset["mode"] + " | claude | melder_0 | "
           + preset["blocker"] + " | " + preset["next"] + " | Every 'version id' that relates to a spell index names "
           "spell_id or the spell index id, by hand; the rest listed with reasons. | The wording lands with its notch, "
           "release note and rebuild, or the owner redirects. | "
           "tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md | " + NOW + " | REQUIRED |")
    board.write_text(rx.sub(lambda m: row, btext, count=1), encoding="utf-8")
    print("lane state:", STATE, preset["status"], NOW)


if __name__ == "__main__":
    main()
