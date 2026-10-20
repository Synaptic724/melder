"""Record the owner's approval of Option A (SpellState.non_resolvable) (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
TASK = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15): "well do the recommended, it makes sense to add a new spellstate just map
    that out to ensure we don't break anything please fully understand the implications of the state system but I
    agree with A sounds reasonable", then "make regression tests for this please so we can properly ensure it
    works". Option A is approved: a new `SpellState.non_resolvable` flag (the recommended name) for a lineage whose
    selected version is a resolvable=False definition, produced where that version is registered and read by
    RiskManager, with the validity axis left truthful. Before any `src/` edit: map every reader and writer of the
    state model from source, write the patch docs, and settle the producer's call sites (spellbook.py and
    transfer_of_ownership.py are melder_0's). Regression tests are part of the deliverable. Items (2)-(3) of the
    design request (the contract check) are not answered and stay out of this change.
  EVIDENCE: {TASK}:323-350
  IMPACT: Rule 1 moves to implementation after the map and the patch docs; rule 2 waits for the owner.
  NEXT: Map the state system's readers and writers from source and record the map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). The owner approved Option A for rule 1: a new `SpellState.non_resolvable` flag for a\n"
    "lineage whose selected version is resolvable=False, read by RiskManager; map the state system first and add\n"
    "regression tests. Items (2)-(3), the contract check, still await his answer. Nothing in `src/` has changed.\n"
    "Next: the implication map (Notes), the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/,\n"
    "and the producer's call sites (spellbook.py and transfer_of_ownership.py are melder_0's).\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append the note, refresh the handoff and the Updated stamp, and the board's next."""
    for line in NOTES.splitlines() + HANDOFF.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/", "EVIDENCE:")), (
            len(line), line)
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + NOTES + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Owner picks the spell-state option for resolvable=False (last Note) and answers the contract-check "
               "items. |",
            "| Map the state system for SpellState.non_resolvable (Option A, owner-approved), then write the patch "
            "docs. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
