"""Record melder_0's file-custody note in rule 2's ticket; correct the patch's owner and order lines (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
PATCH = pathlib.Path("system_docs/patches/active/contract_recheck_on_notch_2026_10_16")
NT = "context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"
REL = "2026-10-16T12:33:09Z"
TASK = "TASK-2026-10-16-public_notch_target_for_staged_versions"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: File custody moved (the boards and melder_0's ticket, read after re-onboarding). The owner accepted
    EPIC-2026-10-14-managed_spell_quantity at 12:17:31Z, and melder_0 took its next task,
    {TASK}. Its custody DECISION ({REL}) releases
    spellbook.py and transfer_of_ownership.py to melder_1 now and holds conduit.py until that task lands, because
    it edits `Conduit.notch_spell` too: a `spell_id=` keyword resolved through `Spellbook._get_owned_spell`, and
    target checks before the transaction (exactly one of `spell` and `spell_id`, a version the Book owns, a member
    of the index passed). It leaves the notch window and the fan-out lines as they are and rebinds the resolved
    target to `spell`, so D3's diff applies with at most a context shift. It asked the owner to relay the handoff
    (its Codex bridge does not connect); melder_1 read it in the ticket.
  EVIDENCE:
  - {NT}:252-272
  - {NT}:229-251
  - {NT}:23-38
  - context_compass/attention_board.md:229-229
  IMPACT: D5's spellbook.py condition is met: once the owner approves, every file but conduit.py can be built;
    D3's two conduit.py changes (`_activate_borrowed_spell` and its call in `notch_spell`) follow melder_0's
    landing, and the change set still lands in one notch. The patch's owner column, migration order and D5 lines
    now say so.
  NEXT: Ask the owner to approve the patch and that order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

TICKET_PAIRS = [
    ("- DEPENDENCIES: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done: its findings, probes and rule 1);\n"
     "  melder_0's lanes (spellbook.py and transfer_of_ownership.py are its files: no edit without a handoff).\n",
     "- DEPENDENCIES: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done: its findings, probes and rule 1);\n"
     f"  melder_0's lanes: spellbook.py and transfer_of_ownership.py released to melder_1 at {REL}; conduit.py\n"
     f"  held by {TASK} until it lands (D3's lines wait).\n"),
    ("cannot reach its consumers' state without a new state or a hot-path read; BLOCKER while spellbook.py is not handed\n"
     "  over.\n",
     "cannot reach its consumers' state without a new state or a hot-path read; BLOCKER for D3's conduit.py lines while\n"
     "  melder_0's notch-target task holds conduit.py.\n"),
    ("Design phase (2026-10-16T12:26:59Z): the patch docs carry the owner's decisions D1-D5 and wait for his approval of the\n"
     "whole; no `src/` change before it, and the build waits for melder_0's handoff of spellbook.py (S8 landed as\n"
     "0.2.8248, in review).\n",
     f"Design phase ({NOW}): the patch docs carry the owner's decisions D1-D5 and await his approval\n"
     "of the whole; no `src/` change before it. melder_0 released spellbook.py and transfer_of_ownership.py\n"
     f"({REL}) and holds conduit.py until its {TASK}\n"
     "lands, so D3's conduit.py lines come last.\n"),
    ("(backlog); D5 wait for melder_0.\n"
     "Next: (1) the owner's approval; (2) melder_0's handoff of spellbook.py; (3) the build: red tests, the change, green\n"
     "with the GIL off and on, probes, docs, release note, notch, rebuild.\n",
     f"(backlog); D5 wait for melder_0 (spellbook.py released at {REL}; conduit.py after its notch-target\n"
     "landing).\n"
     "Next: (1) the owner's approval of the patch and its order; (2) the build on every file but conduit.py: red tests,\n"
     "the change, green with the GIL off and on, probes; (3) D3's conduit.py lines after melder_0's landing, then docs,\n"
     "release note, one notch, rebuild.\n"),
]

ARCH_PAIRS = [
    ("  approval of the patch as a whole, and for melder_0's handoff of spellbook.py\n",
     "  approval of the patch as a whole; conduit.py stays with melder_0's notch-target task until it lands (D3's lines)\n", 1),
    ("| melder_0 (handoff) |", f"| melder_1 (released by melder_0, {REL}) |", 2),
    ("| after the notch window, make every linked peer's parked copy of the incoming version active again | melder_1 |",
     "| after the notch window, make every linked peer's parked copy of the incoming version active again | melder_1, "
     f"once melder_0's {TASK} lands (it holds conduit.py) |", 1),
    ("| melder_1 (after melder_0's handoff) |", "| melder_1 |", 1),
    ("This patch -> the owner's approval -> the mapping note in the ticket -> melder_0's handoff of spellbook.py (S8 landed\n"
     "as 0.2.8248 and is in review) -> on a scratch copy of the tree: red tests -> the melder_1 files (spell_system_states.py\n"
     "with the walk; meld.py with the scan's removal and the catch-up; the error and the strategy; conduit.py and the\n"
     "ward's docstring and comment) -> spellbook.py (the five mutators, bind's and the notch's key, the notch's walk) ->\n"
     "green with the GIL off and on -> the probes before and after -> the same diff in the real tree -> the suites again ->\n"
     "system docs, graph descriptors, release note, one notch above the current version -> closure -> rebuild.\n",
     "This patch -> the owner's approval -> the mapping note in the ticket -> on a scratch copy of the tree: red tests ->\n"
     "the melder_1 files (spell_system_states.py with the walk; meld.py with the scan's removal and the catch-up; the\n"
     "error and the strategy; the ward's docstring and comment) -> spellbook.py (released by melder_0 at\n"
     f"{REL}: the five mutators, bind's and the notch's key, the notch's walk) -> green with the GIL off and\n"
     "on -> the probes before and after -> the same diff in the real tree -> the suites again -> conduit.py (D3:\n"
     "`_activate_borrowed_spell` and its call in `notch_spell`) once melder_0's\n"
     f"{TASK} lands and releases it - that task rebinds its resolved target to\n"
     "`spell` and leaves the window and the fan-out lines as they are - with its tests and the suites once more ->\n"
     "system docs, graph descriptors, release note, one notch above the current version -> closure -> rebuild.\n", 1),
    ("  - D5: the landing waits for melder_0 and his handoff of spellbook.py.\n",
     f"  - D5: the landing waits for melder_0: spellbook.py and transfer_of_ownership.py were released at {REL};\n"
     f"    conduit.py stays with melder_0's {TASK} until it lands, so\n"
     "    D3's conduit.py lines come last.\n", 1),
    ("- APPROVAL REQUEST: the patch as a whole - with it the build starts once melder_0 hands spellbook.py over.\n",
     "- APPROVAL REQUEST: the patch as a whole and the migration order above - with it the build starts at once on every\n"
     "  file but conduit.py.\n", 1),
    ("- What remains: the owner's approval, the mapping note, melder_0's handoff, the build.\n",
     "- What remains: the owner's approval, the mapping note, the build (conduit.py after melder_0's notch-target landing).\n", 1),
]

BORROWER_PAIRS = [
    ("- Owner: user; melder_1 (synaptic_python_developer) (patch); the file is melder_0's: its handoff comes first\n",
     "- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of spellbook.py, which melder_0 released at\n"
     f"  {REL})\n", 1),
    ("3. melder_0 owns spellbook.py: the handoff precedes the edit, and the edit follows S8's landing.\n",
     f"3. spellbook.py: melder_0 released it at {REL} (S8 and its epic accepted), so the edit waits only for\n"
     "   the owner's approval.\n", 1),
    ("- Decided: D5 - the landing waits for melder_0 (S8 landed as 0.2.8248 and is in review) and his handoff of\n"
     "  spellbook.py. Open: the owner's approval of the patch as a whole.\n",
     f"- Decided: D5 - the landing waits for melder_0; it released spellbook.py at {REL}. Open: the owner's\n"
     "  approval of the patch as a whole.\n", 1),
]

WALK_PAIRS = [
    ("- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of spell_system_states.py); spellbook.py is\n"
     "  melder_0's: its handoff comes first\n",
     "- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of spell_system_states.py and of spellbook.py,\n"
     f"  which melder_0 released at {REL})\n", 1),
    ("- Spellbook (melder_0's file): `bind`", "- Spellbook (released by melder_0): `bind`", 1),
    ("3. melder_0 owns spellbook.py: its two call sites change after the handoff, with the five mutators.\n",
     f"3. spellbook.py (released by melder_0 at {REL}): its two call sites change with the five mutators.\n", 1),
    ("- Decided: D2 (fold into rule 2). Open: the owner's approval of the patch as a whole; D5 (melder_0's handoff).\n",
     "- Decided: D2 (fold into rule 2). Open: the owner's approval of the patch as a whole.\n", 1),
]

REACT_PAIRS = [
    ("- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of both files)\n",
     "- Owner: user; melder_1 (synaptic_python_developer) (patch; writer of conduit_ward.py, and of conduit.py once\n"
     f"  melder_0's {TASK} lands and releases it)\n", 1),
    ("2. Rule 2's mark must land with it, or a reactivated copy changes nothing a consumer sees until its next unrelated\n"
     "   recheck.\n",
     "2. Rule 2's mark must land with it, or a reactivated copy changes nothing a consumer sees until its next unrelated\n"
     "   recheck.\n"
     f"3. conduit.py is held by melder_0's {TASK} until it lands. That\n"
     "   task adds a `spell_id=` keyword and target checks before the transaction and rebinds the resolved target to\n"
     "   `spell`; it leaves the window and the fan-out lines as they are, so this change applies after it with at most\n"
     "   a context shift, and the migration order puts it last (architecture_patch.md).\n", 1),
]


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("ascii")


def apply_pairs(text, pairs, path):
    for old, new, count in pairs:
        assert text.count(old) == count, (path, old[:70], text.count(old))
        text = text.replace(old, new)
    return text


def bump_updated(text, path):
    lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
    assert len(lines) == 1, (path, lines)
    return text.replace(lines[0], f"- Updated: {NOW}", 1)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


out = {}
text = read(TICKET)
assert "CLAIM: File custody moved" not in text
text = bump_updated(text, TICKET)
text = apply_pairs(text, [(o, n, 1) for o, n in TICKET_PAIRS], TICKET)
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
text = text.replace(anchor, "\n" + NOTE.rstrip("\n") + "\n" + anchor, 1)
check_lengths(text, TICKET)
out[TICKET] = text

for name, pairs in (("architecture_patch.md", ARCH_PAIRS),
                    ("component_patch_borrower_contracted_maps.md", BORROWER_PAIRS),
                    ("component_patch_dependent_walk.md", WALK_PAIRS),
                    ("component_patch_notch_reactivation.md", REACT_PAIRS)):
    path = PATCH / name
    text = bump_updated(apply_pairs(read(path), pairs, path), path)
    check_lengths(text, path)
    out[path] = text

board = pathlib.Path("attention_board.md")
text = read(board)
rows = [l for l in text.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(rows) == 1
row = rows[0]
new_row = apply_pairs(row, [
    ("| the owner's approval of the updated patch docs (D1-D5 decided, D2 added); melder_0's handoff of spellbook.py | "
     "Present the updated patch docs to the owner for approval; on approval, the build after melder_0's handoff. |",
     "| the owner's approval of the patch (D1-D5 decided); conduit.py held by melder_0's notch-target task (D3's lines "
     "only) | Present the patch and its order to the owner for approval; on approval, build every file but conduit.py "
     "first. |", 1),
    ("| 2026-10-16T12:27:32Z | REQUIRED |", f"| {NOW} | REQUIRED |", 1)], board)
out[board] = text.replace(row, new_row, 1)

art = pathlib.Path("artifact_board.md")
text = read(art)
prefix = ("| tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md | "
          "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/")
fixes = {
    "architecture_patch.md": [],
    "component_patch_borrower_contracted_maps.md": [("(melder_0's file: handoff)", "(released by melder_0)", 1)],
    "component_patch_dependent_walk.md": [("(melder_0's file: handoff)", "(released by melder_0)", 1)],
    "component_patch_notch_reactivation.md": [
        ("; the grant docstring corrected. |",
         "; the grant docstring corrected; conduit.py's lines follow melder_0's notch-target landing. |", 1)],
}
for name, pairs in fixes.items():
    rows = [l for l in text.split("\n") if l.startswith(prefix + name + " |")]
    assert len(rows) == 1, name
    new_row = apply_pairs(rows[0], pairs + [("| 2026-10-16T12:27:32Z | REQUIRED |", f"| {NOW} | REQUIRED |", 1)], art)
    text = text.replace(rows[0], new_row, 1)
out[art] = text

for path, text in out.items():
    text.encode("ascii")
    if not CHECK:
        path.write_bytes(text.encode("ascii"))
    print("checked" if CHECK else "written", path, len(text.split("\n")), "lines")
